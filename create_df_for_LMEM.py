import mne
import os
import os.path as op
import numpy as np
import pandas as pd

os.environ['SUBJECTS_DIR'] = '/net/server/data/Archive/piansrann/freesurfer'
subjects_dir = '/net/server/data/Archive/piansrann/freesurfer'


subjects = ['W001', 'W002','W003','W004','W005','W006','W007', 'W008','W009','W010','W011','W012',
            'W013','W014','W015'] 
rounds = [1, 2, 3, 4, 5, 6]

group=['a_1','b_1','c_1','d_1']

stim_type=['pict','comb','sound','pict_CS','comb_CS','sound_CS']
tmin = -1.0
tmax = 4.
step = 0.4

def make_subjects_df(combined_planar, s, subj, r, stim,tmin, tmax, step, g):

    time_intervals = np.arange(tmin, tmax, step)
    list_of_time_intervals = []
    i = 0
    while i < (len(time_intervals) - 1):
        interval = time_intervals[i:i+2]
        list_of_time_intervals.append(interval)
        #print(interval)
        i = i+1
    
    list_of_beta_power = []    
    for i in list_of_time_intervals:
        combined_planar_in_interval = combined_planar.copy()
        combined_planar_in_interval = combined_planar_in_interval.crop(tmin=i[0], tmax=i[1], include_tmax=True)

        mean_combined_planar = combined_planar_in_interval.get_data().mean(axis=-1)
    
        beta_power = []

        for j in range(len(mean_combined_planar)):
            a = mean_combined_planar[j][s]
            beta_power.append(a)
        list_of_beta_power.append(beta_power)
    
    trial_number = range(len(mean_combined_planar))
    
    subject = [subj]*len(mean_combined_planar)
    run = ['run{0}'.format(r)]*len(mean_combined_planar)
    stim_type = [stim]*len(mean_combined_planar)
    group = [g]*len(mean_combined_planar)
    
    df = pd.DataFrame()
    

    df['epo'] = trial_number
    
    # beta на интервалах
    for idx, beta in enumerate(list_of_beta_power):
        df['beta power %s'%list_of_time_intervals[idx]] = beta
    
    #df['beta_power'] = beta_power
    df['subject'] = subject
    df['round'] = run
    df['stim_type'] = stim_type
    #df['feedback_cur'] = feedback_cur
    df['group'] = group
    return (df)                        
                      
for s in range(102):
    df = pd.DataFrame()
	
    for subj in subjects:
        for r in rounds:
            for stim in stim_type:
                for g in group:
                    try:
                        combined_planar = mne.read_epochs('/net/server/data/Archive/piansrann/pultsinak/meg/theta_epo_3cycle_comb_planar/{0}_run{1}_{2}_{3}_epo_comb_planar.fif'.format(subj, r, stim, g), preload=True)
                        
                        df_subj = make_subjects_df(combined_planar, s, subj, r, stim,tmin, tmax, step, g)
       
                        df = pd.concat([df,df_subj], axis=0 )  
                    except (OSError, FileNotFoundError):
                        print('This file not exist')
    df.to_csv('/net/server/data/Archive/piansrann/pultsinak/meg/df_lmem_3cycle/df_LMEM_{0}.csv'.format(s))
                    
