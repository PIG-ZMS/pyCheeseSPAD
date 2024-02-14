# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 16:13:41 2022
@author: Yifang
"""
import numpy as np
import matplotlib.pyplot as plt
import photometry_functions as fp
import scipy
import traceAnalysis as Analysis
import os
# Folder with your files
#folder = 'C:/SPAD/pyPhotometry_v0.3.1/data/' # Modify it depending on where your file is located
folder ='E:/SPAD/SPADData/20240105_pyPhotometry_SNR/timedivision/'
# File name
file_name = 'SNR_cont1mA-2024-01-04-180856.csv'
sampling_rate=130
#%%`
raw_signal,raw_reference,Cam_Sync=fp.read_photometry_data (folder, file_name, readCamSync=True,plot=True)
#raw_signal,raw_reference=read_photometry_data (folder, file_name, readCamSync='False')
#CamSyncfname = os.path.join(folder, "CamSync_photometry.csv")
#np.savetxt(CamSyncfname, Cam_Sync, fmt='%d',delimiter=",")
#%%
#raw_signal,raw_reference=fp.read_photometry_data (folder, file_name, readCamSync=False,plot=True)
import glob
def calculate_SNR_for_photometry_folder (parent_folder):
    # Iterate over all folders in the parent folder
    SNR_savename='pyPhotometry_SNR_timedivision.csv'        
    SNR_array = np.array([])
    all_files = os.listdir(parent_folder)
    csv_files = [file for file in all_files if file.endswith('.csv')]
    print(csv_files)
    for csv_file in csv_files:
        print('111',csv_file)
        raw_signal,raw_reference=fp.read_photometry_data (parent_folder, csv_file, readCamSync=False,plot=True)
        SNR=Analysis.calculate_SNR(raw_signal)
        SNR_array = np.append(SNR_array, SNR)
    csv_savename = os.path.join(parent_folder, SNR_savename)
    np.savetxt(csv_savename, SNR_array, delimiter=',')
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.plot(SNR_array, marker='o', linestyle='-', color='b')
    plt.xlabel('Light Power (uW)')
    plt.ylabel('SNR')
    return -1

calculate_SNR_for_photometry_folder (folder)
%
# snr_py=Analysis.calculate_SNR (raw_signal)
'''Define the segments you want to zoom in, in seconds'''
def get_part_trace(data,start_time,end_time,fs):
    start_time=start_time
    end_time=end_time
    sliced_data=data[fs*start_time:fs*end_time]
    return sliced_data

'''!!!Skip this part or comment these four lines if you dont want to cut your data'''
# start_time=40
# end_time=60
# raw_signal=get_part_trace(raw_signal,start_time=start_time,end_time=end_time,fs=sampling_rate)
# raw_reference=get_part_trace(raw_reference,start_time=start_time,end_time=end_time,fs=sampling_rate)
# fig = plt.figure(figsize=(16, 10))
# ax1 = fig.add_subplot(211)
# ax1 = fp.plotSingleTrace (ax1, raw_signal, SamplingRate=sampling_rate,color='blue',Label='Signal')
# ax2 = fig.add_subplot(212)
# ax2 = fp.plotSingleTrace (ax2, raw_reference, SamplingRate=sampling_rate,color='purple',Label='Reference')
#%%
'''
You can get zdFF directly by calling the function fp.get_zdFF(),at the end of this file
TO CHECK THE SIGNAL STEP BY STEP:
YOU CAN USE THE FOLLOWING CODES TO GET MORE PLOTS
These will give you plots for 
smoothed signal, corrected signal, normalised signal and the final zsocre
'''
'''Step 1, plot smoothed traces'''
smooth_win = 1
smooth_reference,smooth_signal,r_base,s_base = fp.photometry_smooth_plot (
    raw_reference,raw_signal,sampling_rate=sampling_rate, smooth_win = smooth_win)
#%%
'''Step 2, plot corrected traces, removing the baseline (detrend)'''
remove=0
reference = (smooth_reference[remove:] - r_base[remove:])
signal = (smooth_signal[remove:] - s_base[remove:])  

fig = plt.figure(figsize=(16, 10))
ax1 = fig.add_subplot(211)
ax1 = fp.plotSingleTrace (ax1, signal, SamplingRate=sampling_rate,color='blue',Label='corrected_signal')
ax2 = fig.add_subplot(212)
ax2 = fp.plotSingleTrace (ax2, reference, SamplingRate=sampling_rate,color='purple',Label='corrected_reference')

#%%
'''Step 3, plot normalised traces'''
z_reference = (reference - np.median(reference)) / np.std(reference)
z_signal = (signal - np.median(signal)) / np.std(signal)

fig = plt.figure(figsize=(16, 10))
ax1 = fig.add_subplot(211)
ax1 = fp.plotSingleTrace (ax1, z_signal, SamplingRate=sampling_rate,color='blue',Label='normalised_signal')
ax2 = fig.add_subplot(212)
ax2 = fp.plotSingleTrace (ax2, z_reference, SamplingRate=sampling_rate,color='purple',Label='normalised_reference')

#%%
'''Step 4, plot fitted reference trace and signal'''
from sklearn.linear_model import Lasso
lin = Lasso(alpha=0.001,precompute=True,max_iter=1000,
            positive=True, random_state=9999, selection='random')
n = len(z_reference)
'''Need to change to numpy if previous smooth window is 1'''
z_signal=z_signal.to_numpy()
z_reference=z_reference.to_numpy()
''
lin.fit(z_reference.reshape(n,1), z_signal.reshape(n,1))

z_reference_fitted = lin.predict(z_reference.reshape(n,1)).reshape(n,)

fig = plt.figure(figsize=(16, 5))
ax1 = fig.add_subplot(111)
ax1 = fp.plotSingleTrace (ax1, z_signal, SamplingRate=sampling_rate,color='blue',Label='normalised_signal')
ax1 = fp.plotSingleTrace (ax1, z_reference_fitted, SamplingRate=sampling_rate,color='purple',Label='fitted_reference')
#%%
'''Step 5, plot zscore'''
zdFF = (z_signal - z_reference_fitted)
fig = plt.figure(figsize=(16, 5))
ax1 = fig.add_subplot(111)
ax1 = fp.plotSingleTrace (ax1, zdFF, SamplingRate=sampling_rate,color='black',Label='zscore_signal')

'''Save signal'''
greenfname = os.path.join(folder, "Green_traceAll.csv")
np.savetxt(greenfname, raw_signal, delimiter=",")
redfname = os.path.join(folder, "Red_traceAll.csv")
np.savetxt(redfname, raw_reference, delimiter=",")
zscorefname = os.path.join(folder, "Zscore_traceAll.csv")
np.savetxt(zscorefname, zdFF, delimiter=",")
#%%

#%%
'''Optional, for spectrogram'''
# f, t, Sxx = scipy.signal.spectrogram(raw_signal, fs=130)
# plt.pcolormesh(t, f, Sxx, shading='gouraud')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.ylim(0, 50)
# plt.show()
#%%
'''Get zdFF directly'''
zdFF = fp.get_zdFF(raw_reference,raw_signal,smooth_win=5,remove=0,lambd=5e4,porder=1,itermax=50)
fig = plt.figure(figsize=(16, 5))
ax1 = fig.add_subplot(111)
ax1 = fp.plotSingleTrace (ax1, zdFF, SamplingRate=sampling_rate,color='black',Label='zscore_signal')