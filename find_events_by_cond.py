import numpy as np
import mne
import os
import os.path as op




subjects = ['W001','W002','W003','W004','W005','W006','W007', 'W008','W009','W010','W011','W012','W013', 'W014','W015'] 

data = ['230628','230704','230710','230711','230714','230718','230722','230724','230712','230719','230717','230721','230728','230731','230724','230804','230811',
        '230807','230814','230809','230816','230821','230816','230823','230821']

rounds = [1, 2, 3, 4, 5, 6]
#rounds_name = ['passive', 'active1', 'active2', 'active3', 'active4', 'active5', 'active6']


marks = [2,3,130,8,9,136,4,5,132,10,11,138, 6, 7, 134, 12, 13, 140]

group=['a_1','b_1','c_1','d_1']

#group=['a_1','b_1','c_1','d_1','a_2','b_2','c_2','d_2']
stim_type= ['comb','comb_CS','sound','sound_CS','pict','pict_CS'] 

data_path = '/net/server/data/Archive/piansrann/pultsinak/meg/raw_without_ica'




def process_events(events_clean):
    sound_CS = []
    sound = []
    pict_CS = []
    pict = []
    comb_CS = []
    comb = []
    i = 0
    while i <= (len(events_clean)-6):
        print(i)
        # Process Sound
        if events_clean[i][2] == 2 and events_clean[i + 2][2] == 2:
            sound.append(list(events_clean[i]))
            i += 3
            print("Sound")
        elif events_clean[i][2] == 2 and events_clean[i + 2][2] not in [2]:
            i += 1
            
        elif events_clean[i][2] == 3 and events_clean[i + 2][2] == 130:
            sound_CS.append(list(events_clean[i]))
            i += 3
            print("Sound CS")
        elif events_clean[i][2] == 3 and events_clean[i + 2][2] not in  [130]:
            i += 1
         
        elif events_clean[i][2] == 8 and events_clean[i + 2][2] == 8:
            sound.append(list(events_clean[i]))
            i += 3
            print("Sound")
        elif events_clean[i][2] == 8 and events_clean[i + 2][2] not in [8]:
            i = i+1
       
            
        elif events_clean[i][2] == 9 and events_clean[i + 2][2] == 136:
            sound_CS.append(list(events_clean[i]))
            i += 3
            print("Sound CS")
        elif events_clean[i][2] == 9 and events_clean[i + 2][2] not in  [136]:
            i += 1
        
        # Process Picture
        
        elif events_clean[i][2] == 4 and events_clean[i + 2][2] == 4:
            pict.append(list(events_clean[i]))
            i += 3
            print("Pict")
        
        elif events_clean[i][2] == 4 and events_clean[i + 2][2] not in [4,132]:
            i += 1
            
        elif events_clean[i][2] == 4 and events_clean[i + 2][2] == [132]:
            pict_CS.append(list(events_clean[i]))
            i += 3
            print("Pict CS")
          
        elif events_clean[i][2] == 5 and events_clean[i + 2][2] == 132:
            pict_CS.append(list(events_clean[i]))
            i += 3
            print("Pict CS")
        elif events_clean[i][2] == 5 and events_clean[i + 2][2] not in [132]:
            i += 1
            print("Pict")
            
        elif events_clean[i][2] == 10 and events_clean[i + 2][2] == 10:
            pict.append(list(events_clean[i]))
            i += 3
            print("Pict")
        elif events_clean[i][2] == 10 and events_clean[i + 2][2] not in  [10]:
            i += 1
            print("Pict")
            
        elif events_clean[i][2] == 11 and events_clean[i + 2][2] == 138:
            pict_CS.append(list(events_clean[i]))
            i += 3
            print("Pict CS")
      
        elif events_clean[i][2] == 11 and events_clean[i + 3][2] == 138:
            #pict_CS.append(list(events_clean[i]))
            i += 4
            print("Pict CS")
         
        elif events_clean[i][2] == 11 and events_clean[i + 2][2] not in  [138]:
            i += 1
            print("Pict")
        
        
        
        # Process Complex
        elif events_clean[i][2] == 6 and events_clean[i + 2][2] == 6:
            comb.append(list(events_clean[i]))
            i += 3
        
        elif events_clean[i][2] == 6 and events_clean[i + 2][2] not in  [6]:
            i += 1
            
        elif events_clean[i][2] == 7 and events_clean[i + 2][2] == 134:
            comb_CS.append(list(events_clean[i]))
            i += 3
        elif events_clean[i][2] == 7 and events_clean[i + 3][2] == 134:
            #comb_CS.append(list(events_clean[i]))
            i += 4   
        elif events_clean[i][2] == 7 and events_clean[i + 2][2] not in [134]:
            i += 1
            
        elif events_clean[i][2] == 12 and events_clean[i + 2][2] == 12:
            comb.append(list(events_clean[i]))
            i += 3
        elif events_clean[i][2] == 12 and events_clean[i + 2][2] == 140:
            comb_CS.append(list(events_clean[i]))
            i += 3
        elif events_clean[i][2] == 12 and events_clean[i + 2][2] not in [12,140]:
            i += 1
           
        elif events_clean[i][2] == 13 and events_clean[i + 2][2] == 140:
            comb_CS.append(list(events_clean[i]))
            i += 3
            
        elif events_clean[i][2] == 13 and events_clean[i + 3][2] == 140:
             
            i += 4  
            
        #elif events_clean[i][2] == [138,140]:
            #i += 1
       
        elif events_clean[i][2] == 13 and events_clean[i+2][2] not in [140]:
            #print(f'pict {r} has missing mark')
            i= i+1

    return np.array(sound_CS), np.array(sound), np.array(pict_CS), np.array(pict), np.array(comb), np.array(comb_CS)


for idx, subj in enumerate(subjects):
    for d in data:
        for ir, r in enumerate(rounds):
            os.makedirs(f'/net/server/data/Archive/piansrann/pultsinak/meg/events_by_cond/{subj}', exist_ok=True)
            for g in group:
                try:
                    raw = mne.io.Raw(op.join(data_path, f'{subj}_{g}_run{r}_raw_tsss_mc.fif'), preload=True)
                    events_clean = mne.find_events(raw, stim_channel='STI101', shortest_event=1)
                    events_clean = [e for e in events_clean if e[2] in marks]

                    sound_CS, sound, pict_CS, pict, comb, comb_CS = process_events(events_clean)

                    events_list = [sound_CS, sound, pict_CS, pict, comb, comb_CS]
                    events_name = ['sound_CS', 'sound', 'pict_CS', 'pict', 'comb', 'comb_CS']
                    for ind, el in enumerate(events_list):
                        np.savetxt(f"/net/server/data/Archive/piansrann/pultsinak/meg/events_by_cond/{subj}/run{r}_{subj}_{g}_{events_name[ind]}.txt", el, fmt="%s")
                except (OSError):
                    print('This file not exist')
                    
                   
                    
############## remove files without events #############

remove_files = []
for subj in subjects:
    for r in rounds:
        for  stim in stim_type:
            
            for g in group:
                
                try:
                    
                    # загружаем массив эвентов, разбитые по условиям
                    events_by_cond = np.loadtxt('/net/server/data/Archive/piansrann/pultsinak/meg/events_by_cond/{0}/run{1}_{0}_{2}_{3}.txt'.format(subj,r,g,stim), dtype='int')
                    
                    if events_by_cond.size == 0:
                        os.remove('/net/server/data/Archive/piansrann/pultsinak/meg/events_by_cond/{0}/run{1}_{0}_{2}_{3}.txt'.format(subj,r,g,stim))
                        #print('File removed successfully')
                        name_remove = f'{subj} run{r} {stim} {g}'
                        remove_files.append(name_remove)
                except OSError:
                    
                    print(f'{subj} run{r} {stim} {g} not exist')
print(remove_files)   
                    
