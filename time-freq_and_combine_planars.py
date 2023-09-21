import mne
import os
import os.path as op
import numpy as np
import pandas as pd

os.environ['SUBJECTS_DIR'] = '/net/server/data/Archive/piansrann/freesurfer'
subjects_dir = '/net/server/data/Archive/piansrann/freesurfer'



subjects = ['W001','W002','W003','W004','W005','W006','W007', 'W008','W009','W010','W011','W012',
            'W013','W014','W015']                                             
L_freq = 4
H_freq = 7
f_step = 1

time_bandwidth = 4 #(by default = 4)
# if delta (1 - 4 Hz) 
#n_cycles = np.array([1, 1, 1, 2]) # уточнить

freqs = np.arange(L_freq, H_freq, f_step)
n_cycles = freqs//2

period_start = -2.0
period_end = 4.0

baseline = (-1, -0.4)

freq_range = 'beta_16_30'


rounds = [1, 2, 3, 4, 5, 6]

group=['a_1','b_1','c_1','d_1']

stim_type=['pict','comb','sound','pict_CS','comb_CS','sound_CS']

data_path = '/net/server/data/Archive/piansrann/pultsinak/meg/raw_without_ica'




for subj in subjects:

    #for date in data:
        for g in group:
            for r in rounds:
                for stim in stim_type:

                    try:
                        
                        freqs = np.arange(L_freq, H_freq, f_step)
                        
                    
                        events_bl = np.loadtxt("/net/server/data/Archive/piansrann/data_processing/main_experiment/events_for_bl_without_ica/{0}_round_{1}_{2}.txt".format(subj, r,g), dtype='int') 
                            # если только одна метка, т.е. одна эпоха, то выдается ошибка, поэтому приводим shape к виду (N,3)
                        if events_bl.shape == (3,):
                            events_bl = events_bl.reshape(1,3)
                        events_bl = np.sort(events_bl, axis = 0)  
                        
                        #events, which we need
                        events_response = np.loadtxt('/net/server/data/Archive/piansrann/pultsinak/meg/events_by_cond/{0}/run{1}_{0}_{2}_{3}.txt'.format(subj,r,g,stim), dtype='int')
                        # если только одна метка, т.е. одна эпоха, то выдается ошибка, поэтому приводи shape к виду (N,3)
                        if events_response.shape == (3,):
                            events_response = events_response.reshape(1,3)
                        
                    	           
                        raw_fname = op.join(data_path, '{0}_{1}_run{2}_raw_tsss_mc.fif'.format(subj,g,r))

                        raw_data = mne.io.Raw(raw_fname, preload=True)
                        raw_data.notch_filter(np.arange(50, 201, 50), filter_length='auto', phase='zero')    
                        raw_data.filter(1., 50., fir_design='firwin')   
                        
                        picks = mne.pick_types(raw_data.info, meg = True, eog = True,exclude="bads")
                    		    
                    	   	    
                        #epochs for baseline
                        # baseline = None, чтобы не вычитался дефолтный бейзлайн
                        epochs_bl = mne.Epochs(raw_data, events_bl, event_id = None, tmin = -2.0, tmax = 1.0, baseline = None, picks = picks,reject = dict(mag=9e-12, grad=4e-10),preload = True)
                        events_bl_after_reject=epochs_bl.events 
                        if events_bl_after_reject.shape[0]==0:
                            print('NO BL')
                        
                        else:
                        
                            epochs_bl.resample(300)
                        
                            
                            freq_show_baseline = mne.time_frequency.tfr_multitaper(epochs_bl, freqs = freqs, n_cycles = n_cycles, time_bandwidth = time_bandwidth, use_fft = False, return_itc = False, average=False).crop(tmin=baseline[0], tmax=baseline[1], include_tmax=True) #frequency of baseline
                    	    
                        #add up all values according to the frequency axis
                            b_line = freq_show_baseline.data.sum(axis=-2)
                        
                        # логарифмируем данные для бейзлайн и получаем бейзлайн в дБ
                            b_line = 10*np.log10(b_line)
                    	    
                    	# Для бейзлайна меняем оси местами, на первом месте число каналов
                            b_line = np.swapaxes(b_line, 0, 1)
                            
                        # выстраиваем в ряд бейзлайны для каждого из эвентов, как будто они происходили один за другим
                            a, b, c = b_line.shape
                        
                            b_line_ave = b_line.reshape(a, b * c)

                        # Усредняем бейзлайн по всем точкам, получаем одно число (которое будем вычитать из data для каждого канала) (то же самое если вместо смены осей усреднить сначала по времени, а потом по эпохам)
                    	                        
                            b = b_line_ave.mean(axis=-1)
                    	                        
                            b_line_new_shape = b[:, np.newaxis, np.newaxis]  
                        

                    	####### ДЛЯ ДАННЫХ ##############
                        # baseline = None, чтобы не вычитался дефолтный бейзлайн
                            epochs = mne.Epochs(raw_data, events_response, event_id = None, tmin = period_start, 
                    		                tmax = period_end, baseline = None, picks = picks,reject = dict(mag=9e-12, grad=4e-10) , preload = True)
                    		       
                            epochs.resample(300) 

                            freq_show = mne.time_frequency.tfr_multitaper(epochs, freqs = freqs, n_cycles = n_cycles, time_bandwidth = time_bandwidth, use_fft = False, return_itc = False, average=False)

                            temp = freq_show.data.sum(axis=2)
                        
                        # логарифмируем данные и получаем данные в дБ
                            temp = 10*np.log10(temp)
                    	    
                    	####### Для данных так же меняем оси местами
                            data = np.swapaxes(temp, 0, 1)
                            data = np.swapaxes(data, 1, 2)
                    	
                    	
                        #Вычитаем из данных в дБ бейзлайн в дБ
                            data_dB = data - b_line_new_shape 
                        
                        # меняем оси обратно   
                            data_dB = np.swapaxes(data_dB, 1, 2)
                            data_dB = np.swapaxes(data_dB, 0, 1)
                        
                                
                            freq_show.data = data_dB[:, :, np.newaxis, :]
                            
                        #freq_show.data = freq_show.data[:, :, np.newaxis, :]
                            
                        #33 is an arbitrary number. We have to set some frequency if we want to save the file
                            freq_show.freqs = np.array([33])
                            
                        #getting rid of the frequency axis	
                            freq_show.data = freq_show.data.mean(axis=2) 
                            events_after_reject=epochs.events 
                            if events_after_reject.shape[0]!=0:
                                epochs_tfr = mne.EpochsArray(freq_show.data, freq_show.info, tmin = period_start, events = events_after_reject)
                         
                        #epochs_tfr = make_beta_signal(subj,date,g,stim, r, data_path, L_freq, H_freq, f_step, period_start, period_end, baseline, n_cycles, time_bandwidth = time_bandwidth)
                                epochs_tfr.save('/net/server/data/Archive/piansrann/pultsinak/meg/theta_epo_4_7_no_ica_3cycle/{0}_run{1}_{2}_{3}_epo.fif'.format(subj, r, stim, g), overwrite=True)
                            else:
                                print("EPO BADS")
                    except (OSError):
                        print('This file not exist')
                        
                        
                        
########### create FIF planars (sum of grad) ######                       
tmin=-1.0
def combine_planar_Epoches_TFR(EpochsTFR, tmin):
	ep_TFR_planar1 = EpochsTFR.copy(); 
	ep_TFR_planar2 = EpochsTFR.copy()
	ep_TFR_planar1.pick_types(meg='planar1')
	ep_TFR_planar2.pick_types(meg='planar2')

	#grad_RMS = np.power((np.power(evk_planar1.data, 2) + np.power(evk_planar2.data, 2)), 1/2)
	combine = ep_TFR_planar1.get_data() + ep_TFR_planar2.get_data()
	ep_TFR_combined = mne.EpochsArray(combine, ep_TFR_planar1.info, tmin = tmin, events = EpochsTFR.events)

	return ep_TFR_combined #возвращает эпохи, которые можно сохранить .fif в файл
                        
                        
for subj in subjects:

    for g in group:
        for r in rounds:
            for stim in stim_type:

                try:
                        
                    epochs = mne.read_epochs('/net/server/data/Archive/piansrann/pultsinak/meg/theta_epo_4_7_no_ica_3cycle/{0}_run{1}_{2}_{3}_epo.fif'.format(subj, r, stim, g), preload=True)
                    combined_planar = combine_planar_Epoches_TFR(epochs, tmin)
                    combined_planar.save('/net/server/data/Archive/piansrann/pultsinak/meg/theta_epo_3cycle_comb_planar/{0}_run{1}_{2}_{3}_epo_comb_planar.fif'.format(subj, r, stim, g), overwrite=True)
                    
                    
                except (OSError, FileNotFoundError):
                    print('This file not exist')      
