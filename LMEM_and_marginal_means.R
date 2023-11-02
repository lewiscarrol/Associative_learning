library(reshape2)
library(data.table)
library(ggplot2)
library(lme4)
# library("ggpubr")
library(emmeans)
library(lmerTest)
library(stringi)
library(stringr)
library(dplyr)
library(purrr)
library(tidyverse)
library(LMERConvenienceFunctions)


path<- "/Users/kristina/Documents/associative/theta/sensors/df_lmem_3cycle"


read_plus <- function(flnm) {
  read_csv(flnm) %>% 
    mutate(filename = flnm)
}
df <-list.files(path,pattern = "*.csv", full.names = T) %>% 
  map_df(~read_plus(.))

sensor_info <- fread('/Users/kristina/Documents/stc/theta_sensors/sensors.csv', header = TRUE)

names(sensor_info)[1]<- "sensor"
files <- data.table(full_filename=list.files(path, pattern = '*.csv', full.names = T))
files$short_filename <- list.files(path, pattern = '*.csv', full.names = F)

files[, sensor:=stri_extract_first_regex(short_filename,"[0-9]+")]
files[, interval:=str_extract(short_filename,'[0-9]+_[0-9]+.csv')]
# files[,interval:=gsub('.csv','',interval)]
files$sensor <- as.integer(files$sensor)
files <- merge.data.table(files,sensor_info,by = c('sensor'))
files$interval<-NULL
files$Name<-NULL
df$...1<- NULL
names(df)[18]<- "full_filename"
new_df<- merge.data.table(files,df,by = c('full_filename'))
new_df$US_type <- ifelse(grepl("_", new_df$stim_type), sapply(strsplit(new_df$stim_type, "_"), `[`, 2), "CS_minus")
new_df$CS_type <- sub("_.*", "", new_df$stim_type)
new_df$CS_type<- as.factor(new_df$CS_type)
new_df$US_type<- as.factor(new_df$US_type)
new_df$subject<- as.factor(new_df$subject)

#new_df[is.na(new_df) | new_df=="Inf"] = NA

cols <- colnames(new_df)[grep('[0-9]',colnames(new_df))]
sensors<- unique(new_df$sensor)

###### !!! remove runs for 1 day ######
df1 <- new_df[new_df$round!= "run1", ]
df1 <- df1 [df1 $round!= "run2", ]
###### !!! remove runs for 2 day ######
df1 <- new_df[new_df$round!= "run4", ]
df1 <- df1 [df1 $round!= "run5", ]
df1 <- df1 [df1 $round!= "run6", ]
###### create table if you want to merge stims pict and sound at one type - element
elem<- filter(df1, CS_type=='pict'|CS_type=='sound')
elem$type<- 'element'
complex<- filter(df1, CS_type=='comb')
complex$type<- 'complex'
new_df1<- rbind(complex, elem)


emm_options(lmerTest.limit = 10000)
emm_options(pbkrtest.limit = 9000)

p_vals <- data.table()
############### for green heads (main_effects) ##############
for (i in 1:length(sensors)) {
  temp <-subset(df1, sensor == sensors[i])
  #print(temp)
  for (j in cols){
    
    m1 <- lmer(temp[[j]] ~ CS_type*US_type + (1|subject), data = temp)
    d<-romr.fnc(m1, temp, trim = 2.5) ##### remove outliers
    data<- d$data 
    m <- lmer(data[[j]] ~ CS_type*US_type + (1|subject), data = data)
    an <- anova(m)
    an <- data.table(an,keep.rownames = TRUE)
    an_cols <- c('rn','Pr(>F)') 
    an <- an[, ..an_cols]
    an$`Pr(>F)` <- format(an$`Pr(>F)`, digits = 3)
    an$interval <- j
    an$interval <- gsub('beta power','',an$interval)
    an <- dcast(an,formula = interval~rn,value.var = 'Pr(>F)')
    an$sensor <- sensors[i] 
    #an$sensor_name <- files[sensor==i]$Name
    p_vals <- rbind(p_vals,an)
  }
}
setwd('/Users/kristina/Documents/associative/theta/sensors')
write.csv(p_vals, "lmem_cs_us_type.csv")


########## marginal means for toopomaps #######
marginal <- data.table()
for (i in 1:length(sensors)){
  temp <-subset(df1, sensor == sensors[i])
  for (j in cols){
    m1 <- lmer(temp[[j]] ~ CS_type*US_type + (1|subject), data = temp)
    summary(m)
    d<-romr.fnc(m1, temp, trim = 2.5) ##### remove outliers
    data<- d$data 
    m <- lmer(data[[j]] ~ CS_type*US_type + (1|subject), data = data,REML=FALSE)
    marginal_em <- emmeans(m, ~ as.factor(CS_type|US_type),level = 0.95,lmer.df = "satterthwaite")
    
    marginal_em<- as.data.frame(marginal_em)
    marginal_em$interval <- j
    print(marginal_em)
  
    marginal_em$sensor <- unique(temp$sensor)
 
    marginal <- rbind(marginal,marginal_em)
  }
}

pict_cs_plus<- filter(marginal,CS_type=="pict" & US_type=='CS')
pict_cs_minus<- filter(marginal,CS_type=="pict" & US_type=='CS_minus')
sound_cs_plus<- filter(marginal,CS_type=="sound" & US_type=='CS')
sound_cs_minus<-filter(marginal,CS_type=="sound" & US_type=='CS_minus')
comb_cs_plus<- filter(marginal,CS_type=="comb" & US_type=='CS')
comb_cs_minus<- filter(marginal,CS_type=="comb" & US_type=='CS_minus')

pict<- pict_cs_plus$emmean - pict_cs_minus$emmean
sound<- sound_cs_plus$emmean - sound_cs_minus$emmean
comb<- comb_cs_plus$emmean - comb_cs_minus$emmean

pict_vs_comb_plus<- pict_cs_plus$emmean - comb_cs_plus$emmean
sound_vs_comb_plus<- sound_cs_plus$emmean - comb_cs_plus$emmean

pict_vs_comb_minus<- pict_cs_minus$emmean - comb_cs_minus$emmean
sound_vs_comb_minus<- sound_cs_minus$emmean - comb_cs_minus$emmean




marg<- data.table()
marg$pict_cs_plus<-pict_cs_plus$emmean
marg$pict_cs_minus<-pict_cs_minus$emmean
marg$sound_cs_plus<-sound_cs_plus$emmean
marg$sound_cs_minus<-sound_cs_minus$emmean
marg$comb_cs_plus<- comb_cs_plus$emmean
marg$comb_cs_minus<- comb_cs_minus$emmean
marg$pict<- pict
marg$sound<- sound
marg$comb<- comb
marg$pict_vs_comb_plus<- pict_vs_comb_plus
marg$sound_vs_comb_plus<- sound_vs_comb_plus
marg$pict_vs_comb_minus<-pict_vs_comb_minus
marg$sound_vs_comb_minus<-sound_vs_comb_minus
marg$interval<- pict_cs_plus$interval
marg$sensor<- pict_cs_plus$sensor



setwd("/Users/kristina/Documents/associative/theta/sensors")
write.csv(as.data.frame(marg), "marginal_theta.csv")











