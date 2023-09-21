import mne
import os
import os.path as op
import numpy as np
import pandas as pd
from scipy import stats
import copy


rounds = [1, 2, 3, 4, 5, 6]

data_path = '/net/server/data/Archive/piansrann/pultsinak/meg/raw_without_ica'

def events_for_bc(raw):
    events = mne.find_events(raw,min_duration=0, shortest_event=1)
    exclude=[1, 16, 32, 64, 128] #exclusion of event we do not need for further analysis ###############
    events = mne.pick_events(events, include=None, exclude=exclude, step=False)
    events_clean =[]
    tok = [130, 132, 134, 136, 138, 140]
    for i in range(0, len(events[:, 2])-3):
        if events[:, 2][i] == events[:, 2][i+2] or events[:, 2][i+2] in tok:
            events_clean.append(events[i])
    events_clean.append(events[len(events[:, 2])-3])
    events_clean = np.array(events_clean)
    #this works!!!
    events_test =[]
    events_test.append(events_clean[0])
    #events_test[0][2] = 0

    tok = [3, 5, 7, 9, 11, 13]
    picture = [4, 5, 10, 11]
    sound = [2, 3, 8, 9]
    compl = [6, 7, 12, 13]
    for i in range(1, len(events_clean[:, 2])):
        if events_clean[:, 2][i-1] in tok:
            events_test.append(events_clean[i])
            if events_clean[:, 2][i-1] in picture:
                x = 10
            if events_clean[:, 2][i-1] in sound:
                x = 20
            if events_clean[:, 2][i-1] in compl:
                x = 30
            events_test[i][1] = x+1
        else:
            events_test.append(events_clean[i])
            if events_clean[:, 2][i-1] in picture:
                x = 10
            if events_clean[:, 2][i-1] in sound:
                x = 20
            if events_clean[:, 2][i-1] in compl:
                x = 30
            events_test[i][1] = x
    events_test = np.array(events_test)



    for i in range(0, len(events_test[:, 2])):
        events_test[:, 2][i] = events_test[:, 1][i]
        events_test[:, 1][i] = 0
    return events_test

subjects = ['W001','W002','W003','W004','W005','W006','W007', 'W008','W009','W010','W011','W012',
            'W013','W014','W015'] 
group=['a_1','b_1','c_1','d_1','a_2','b_2','c_2','d_2']


for idx, subj in enumerate(subjects):
      for ir, r in enumerate(rounds):
            #os.makedirs(f'/net/server/data/Archive/piansrann/pultsinak/meg/events/{subj}', exist_ok=True)
          for g in group:
              try:
                  raw = mne.io.Raw(op.join(data_path, f'{subj}_{g}_run{r}_raw_tsss_mc.fif'), preload=True)
                  event_bl = events_for_bc(raw)
                  np.savetxt('/net/server/data/Archive/piansrann/data_processing/main_experiment/events_for_bl_without_ica/{0}_round_{1}_{2}.txt'.format(subj,r,g),event_bl)
              except (OSError):
                  print('This file not exist')
                       
