library(reshape2)
library(data.table)
library(ggplot2)
library(ggpubr)
library(lme4)
library(ggpubr)
library(emmeans)
library(lmerTest)
library(plotrix)
library(stringi)
library(gridExtra)
library(ggprism)
library(dplyr)
library(ggsignif)
options(scipen = 999)
library(ggpattern)
library(cowplot)


path<- "/Users/kristina/Documents/associative/theta/sensors/df_lmem_3cycle"


read_plus <- function(flnm) {
  read_csv(flnm) %>% 
    mutate(filename = flnm)
}
df <-list.files(path,pattern = "*.csv", full.names = T) %>% 
  map_df(~read_plus(.))

sensors_all<- fread('/Users/kristina/Documents/associative/theta/sensors/us_1000_1400.csv') ##### load sensors of intrest
sensor_info <- fread('/Users/kristina/Documents/stc/sensors.csv', header = TRUE)
names(sensor_info)[1] <- 'sensor'

files <- data.table(full_filename=list.files(path, pattern = '*.csv', full.names = T))
files$short_filename <- list.files(path, pattern = '*.csv', full.names = F)

# files$short_filename <- gsub('planar2','',files$short_filename)

files[, sensor:=stri_extract_first_regex(short_filename,"[0-9]+")]
# files[, interval:=str_extract(short_filename,'[0-9]+_[0-9]+.csv')]
# files[,interval:=gsub('.csv','',interval)]
files$sensor <- as.integer(files$sensor)
files <- merge.data.table(files,sensor_info,by = c('sensor'))
names(files)[4] <- 'sensor_name'
files$effect <- NULL
subj_list<- as.data.frame(unique(df1$subject))

##### filter files and leave needed sensors only ######

files <- files[sensor_name %in% sensors_all$sensor_name] 

temp <- fread(files[sensor==1]$full_filename) #donor of colnames for empty datatable "beta"
temp$V1 <- NULL
beta <- setNames(data.table(matrix(nrow = 0, ncol = length(colnames(temp))+2)), c(colnames(temp),'sensor','sensor_name'))

for (i in files$sensor){
  temp <- fread(files[sensor==i]$full_filename)
  temp$V1 <- NULL
  temp <- as.data.table(temp)
  temp <- temp[subject %in% subj_list$`unique(df$subject)`]
  
  temp$sensor <- i
  temp$sensor_name <- files[sensor==i]$sensor_name
  
  beta <- rbind(beta,temp)
}
beta[,`mean beta power [1.  1.4]`:=rowMeans(beta[,.SD,.SDcol=c("beta power [1.  1.4]")])] # mean of intervals 

beta[, index := 1:.N, by=c('subject','sensor')] #set indexes of all trials of each subject, same for all sensors 

means <- beta[, mean(`mean beta power beta power [1.  1.4]`),by=c('subject','index')] # compute means of sensors

means$US_type <- ifelse(grepl("_", means$stim_type), sapply(strsplit(means$stim_type, "_"), `[`, 2), "CS_minus")
means$CS_type <- sub("_.*", "", means$stim_type)
means$CS_type<- as.factor(means$CS_type)
means$US_type<- as.factor(means$US_type)
means$subject<- as.factor(means$subject)
means[is.na(means) | means=="Inf"] = NA


df1 <- means[means$round!= "run1", ]
df1 <- df1 [df1 $round!= "run2", ]



m <- lmer(V1 ~ CS_type*US_type + (1|subject), data =df1) # main part, fit model!
summary(m)
s <- step(m)
m2 <- get_model(s)
### Take the marginal means from the model ########
emm_options(pbkrtest.limit = 5000)
marginal_em <- emmeans(m, ~ as.factor(US_type|CS_type), level = 0.99)
marginal_em<- as.data.frame(marginal_em)

an <- NULL
an <- anova(m2)
an <- data.table(an,keep.rownames = TRUE)
#an[, eta2:=F_to_eta2(`F value`, NumDF, DenDF)$Eta2_partial]
an[`Pr(>F)`<0.001, stars:='***']
an[`Pr(>F)`<0.01 & `Pr(>F)`>0.001 , stars:='**']
an[`Pr(>F)`<0.05 & `Pr(>F)`>0.01 , stars:='*']
an[`Pr(>F)`>0.05 & `Pr(>F)`<0.1 , stars:='#']

Tuk<-data.table(summary(emmeans(m, pairwise ~ US_type|CS_type, adjust = 'tukey',lmer.df = "satterthwaite"))$contrasts)
Tuk <- Tuk[, group1:=gsub(' -.*', '', contrast)][, group2:=gsub('.*- ', '', contrast)]
Tuk <- Tuk[p.value<0.1, p_significant:=format(p.value, digits = 3)]

n <- Tuk[!is.na(p_significant), .N]

Tuk[p.value<0.001, stars:='***']
Tuk[p.value<0.01 & p.value>0.001 , stars:='**']
Tuk[p.value<0.05 & p.value>0.01 , stars:='*']
Tuk[p.value>0.05 & p.value<0.1 , stars:='#']

p1 <- ggplot(marginal_em, aes(x = factor(CS_type,level = c("pict","sound","comb")),
                              y = emmean,  ymin=emmean-SE, ymax = emmean+SE, color = US_type,group = US_type))+
  scale_x_discrete(labels = c("pict","sound","complex"))+ geom_line(size=1.5)+
  geom_point(position=position_dodge(0.1)) + geom_errorbar(width = 0.1,  position=position_dodge(0.1), size=1.5)+labs(y = "Theta power change,dB", x = "Stimul type")+
  theme_classic()+ theme(text = element_text(size=20))+scale_color_discrete(name = "US_type", labels = c("CS+", "CS-"))+theme(legend.position="bottom")+
  ylim(-2.5,0.5) +
  geom_hline(yintercept=-0.0, linetype='dashed', col = 'black', size = 1.0)+
  theme(axis.text.x = element_text(colour="black"), axis.text.y = element_text(colour="black"))

p1 <- p1+geom_signif(y_position=c(y_values$y_max +0.05),
                     xmin=c(y_values$number-0.075), xmax=c(y_values$number+0.075),
                     annotation=c(y_values$stars),col='black',
                     tip_length=0.003,textsize = 12,vjust = 0.4,size = 1.2)

p1<- ggpar(p1,
           ylim = c(-2.5,0.5),
           font.ytickslab = 30,
           font.xtickslab = 27,
           font.main = 25,
           font.submain = 25,
           font.x = 27,
           font.y = 27)

p1


Tuk<-data.table(summary(emmeans(m, pairwise ~ CS_type|US_type, adjust = 'tukey',lmer.df = "satterthwaite"))$contrasts)
Tuk <- Tuk[, group1:=gsub(' -.*', '', contrast)][, group2:=gsub('.*- ', '', contrast)]
Tuk <- Tuk[p.value<0.1, p_significant:=format(p.value, digits = 3)]

n <- Tuk[!is.na(p_significant), .N]

Tuk[p.value<0.001, stars:='***']
Tuk[p.value<0.01 & p.value>0.001 , stars:='**']
Tuk[p.value<0.05 & p.value>0.01 , stars:='*']
Tuk[p.value>0.05 & p.value<0.1 , stars:='#']
tuk_cs_minus<- filter(Tuk, US_type=="CS_minus")
tuk_cs_plus<- filter(Tuk, US_type=="CS")
cs_minus<- filter(marginal_em, US_type=="CS_minus")
cs_plus<- filter(marginal_em, US_type=="CS")

plot_emmean<-ggplot(data = cs_plus, aes(x = factor(CS_type,level = c("pict","sound","comb")), 
                                            y = emmean,  ymin=emmean-SE, ymax = emmean+SE, group = 1))+
  scale_x_discrete(labels = c("pict","sound","complex"))+
  geom_point() + geom_errorbar(width = 0.1, size=1.5)+geom_line(size=1.5)+labs(y = "Theta power change,dB", x = "Choice type")+
  theme_classic()+theme(text = element_text(size=20))+ ylim (-2.5,0.5) +
  theme(axis.text.x = element_text(colour="black"), axis.text.y = element_text(colour="black"))+
  geom_hline(yintercept= 0.0, linetype='dashed', col = 'black', size = 1.0)+
  stat_pvalue_manual(tuk_cs_plus, label = 'stars', size = 12, bracket.size = 1.5, tip.length = 0.01,y.position =c(-0.1,-0.3,-0.5),inherit.aes = FALSE)

plot_emmean <- ggpar(plot_emmean,
                     ylim = c(-2.5,0.5),
                     font.ytickslab = 30,
                     font.xtickslab = 27,
                     font.main = 25,
                     font.submain = 25,
                     font.x = 27,
                     font.y = 30)

plot_emmean

