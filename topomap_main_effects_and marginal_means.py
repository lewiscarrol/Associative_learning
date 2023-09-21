

import mne
import os.path as op
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import copy
import statsmodels.stats.multitest as mul

df = pd.read_csv('/Users/kristina/Documents/associative/theta/sensors/lmem_cs_us_type.csv')

t=np.linspace(0, 3.9, num = 20)
# задаем время для построения топомапов (используется в функции MNE plot_topomap)
time_to_plot = np.linspace(0.1, 3.9, num = 20)
# загружаем донора (любой Evoked с комбинированными планарами или одним планаром - чтобы было 102 сеносора). 
temp = mne.Evoked('/Users/kristina/Documents/stc/theta_sensors/P001_norisk_evoked_resp_comb_planar.fif',verbose=True).crop(tmin=0, tmax=0.036, include_tmax=True)


n = 20 # количество говов в ряду

# задаем временные точнки, в которых будем строить головы, затем мы присвоим их для донора (template)
times_array = np.array([0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3, 2.5,
       2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.9])


##############  empty topomaps line (without color) ##################
def nocolor_topomaps_line (n, temp, times_array ):
    df = np.zeros((102, 20))
    temp.data = df
    #temp.times = times_array

    return temp  


      
def space_fdr(p_val_n):
    #print(p_val_n.shape)
    temp = copy.deepcopy(p_val_n)
    for i in range(temp.shape[1]):
        _, temp[:,i] = mul.fdrcorrection(p_val_n[:,i])
    return temp


################## Full FDR -the correction is made once for the intire data array ############
def full_fdr(p_val_n):
    s = p_val_n.shape
    #print(p_val_n.shape)
    temp = copy.deepcopy(p_val_n)
    pval = np.ravel(temp)
    _, pval_fdr = mul.fdrcorrection(pval)
    pval_fdr_shape = pval_fdr.reshape(s)
    return pval_fdr_shape

################ make binary dataframe from pvalue (0 or 1) #########################
def p_val_binary(p_val_n, treshold):
	p_val =  copy.deepcopy(p_val_n)
	for raw in range(p_val.shape[0]):
		for collumn in range(p_val.shape[1]):
			if p_val[raw, collumn] < treshold:
				p_val[raw, collumn] = 1
			else:
				p_val[raw, collumn] = 0
	return p_val

time=temp.times

temp = nocolor_topomaps_line(n, temp, times_array)

pval_in_intevals = []
# number of heads in line and the number og intervals into which we divided (see amount od tables with p_value in intervals)
for i in range(102):

    pval_s = df[df['sensor'] == i]
    pval = pval_s['US_type'].tolist()

    pval_in_intevals.append(pval)
    
pval_in_intevals = np.array(pval_in_intevals)
pval_space_fdr = space_fdr(pval_in_intevals)
pval_full_fdr =  full_fdr(pval_in_intevals)


binary = p_val_binary(pval_in_intevals, treshold = 0.05)

fig = temp.plot_topomap(times=time,ch_type='planar1', scalings = 1, units = 'dB', show = False,  time_unit='s',  colorbar = False, extrapolate = "local", mask = np.bool_(binary), mask_params = dict(marker='o', markerfacecolor='green', markeredgecolor='g', linewidth=0, markersize=10, markeredgewidth=2))

binary_space = p_val_binary(pval_space_fdr, treshold = 0.05)

fig2 = temp.plot_topomap(times = time, ch_type='planar1', scalings = 1, units = 'dB', show = False,  time_unit='s', colorbar = False, extrapolate = "local", mask = np.bool_(binary_space), mask_params = dict(marker='o', markerfacecolor='green', markeredgecolor='g', linewidth=0, markersize=10, markeredgewidth=2))

# full fdr
binary_full = p_val_binary(pval_full_fdr, treshold = 0.05)

fig3 = temp.plot_topomap(times = time, ch_type='planar1', scalings = 1, units = 'dB', show = False, time_unit='s',  colorbar = False,extrapolate = "local", mask = np.bool_(binary_full), mask_params = dict(marker='o', markerfacecolor='green', markeredgecolor='g', linewidth=0, markersize=10, markeredgewidth=2))


########## Plot topomaps with marginal means #########
df = pd.read_csv('/Users/kristina/Documents/associative/theta/sensors/marginal_theta.csv')

theta_in_intevals = []
# number of heads in line and the number og intervals into which we divided (see amount od tables with p_value in intervals)
for i in range(102):

    pval_s = df[df['sensor'] == i]
    pval = pval_s['sound_vs_comb_minus'].tolist()

    theta_in_intevals.append(pval)
    
theta_in_intevals  = np.array(theta_in_intevals )
temp = mne.Evoked('/Users/kristina/Documents/stc/theta_sensors/P001_norisk_evoked_resp_comb_planar.fif',verbose=True).crop(tmin=0, tmax=0.062, include_tmax=True)

temp.data=theta_in_intevals 

fig = temp.plot_topomap(times=time,ch_type='planar1', scalings = 1, units = 'dB', show = False,  time_unit='s',vlim=(-2,2),  colorbar = True, extrapolate = "local")






