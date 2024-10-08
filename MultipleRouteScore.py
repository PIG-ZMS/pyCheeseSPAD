#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:08:15 2024

@author: zhumingshuai
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:03:57 2024

@author: zhumingshuai
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import Reward_Latency as RL

class input_file:
    def __init__ (self,folder,filename):
        self.folder = folder
        self.filename = filename
        self.ID = filename.split('_')[0]
        self.path = os.path.join(folder,filename)
        self.df = pd.read_csv(self.path)
        self.day_avg = GetDayAvg(self.df)
        self.ContainSB = False
        self.lag = False
        if 'Average' in self.filename:
            self.avg = True
            for i in range (len(self.df.columns.tolist())):
                if 'SB' in self.df.columns[i]:
                    self.ContainSB = True
        elif 'Route_Score' in self.filename:
            self.avg = False
            if 'Less' in self.filename:
                self.pfw = False
            else:
                self.pfw = True
        elif 'Lag' in self.filename:
            self.lag = True
            self.avg = False
        else:
            print('ERROR! Please remove irrelevent csv files in '+folder)
        return 
        

def ReadFiles (input_folder):
    csv_files = []
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith('.csv'):
                csv_file = input_file(root,filename) 
                csv_files.append(csv_file)
    return csv_files

def IntegrateData (csv_files):
    csv_files_norm_pfw = None
    csv_files_norm_lpfw = None
    csv_files_day_avg = None
    for i in range (len(csv_files)):
        file = csv_files[i]
        if (file.avg and file.ContainSB):
            csv_files_day_avg = pd.concat([csv_files_day_avg,file.day_avg], ignore_index=True)
        elif (not file.avg) and (not file.lag):
            if(file.pfw):
                csv_files_norm_pfw = pd.concat([csv_files_norm_pfw,GetDayAvg(file.df)], ignore_index=True)
            else:
                csv_files_norm_lpfw = pd.concat([csv_files_norm_lpfw,GetDayAvg(file.df)], ignore_index=True)
            
    return csv_files_norm_pfw,csv_files_norm_lpfw,csv_files_day_avg

def GetDayAvg (csv_files):
    avg_csv = csv_files.groupby('day').mean().reset_index()
    return avg_csv     
        
def PlotDoubleY (csv_files,y1_column,y2_column,xlab = 'x',ylab1 = 'y1',ylab2 = 'y2',day_column = 'day'):
    mean_df = csv_files.groupby(day_column).mean()
    # Calculate the standard error of the mean (SEM)
    std_df = csv_files.groupby(day_column).std()
    count_df = csv_files.groupby(day_column).size()
    # std_df = mean_df.groupby(day_column).std()
    # count_df = mean_df.groupby(day_column).size()
    count_df = pd.DataFrame({col: count_df for col in std_df.columns})
    sem_df = std_df / np.sqrt(count_df)
    t_value = stats.t.ppf(1-0.025, df=count_df-1)
    ci_df = sem_df * t_value
    days = mean_df.index
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Days')
    ax1.set_ylabel(y1_column, color='black')
    ax1.errorbar(days, mean_df[y1_column], yerr=sem_df[y1_column], fmt='-o', color='black', capsize=5)
    ax1.tick_params(axis='y', labelcolor='black')

    ax2 = ax1.twinx()
    ax2.set_ylabel(y2_column, color='green')
    ax2.errorbar(days, mean_df[y2_column], yerr=sem_df[y2_column], fmt='-o', color='green', capsize=5)
    ax2.tick_params(axis='y', labelcolor='green')
    fig.tight_layout()
    return fig

def PlotTwoDif (data_frame_pfw, data_frame_lpfw, data_frame_SB,output_folder,tot_SB):
    imp_folder = output_folder+'learning_curve/'
    if not os.path.exists(imp_folder):
        os.makedirs(imp_folder)
    if tot_SB:
        fig_dif2,imp_ax2 = plt.subplots(figsize=(7, 5))
        RL.PlotRSDif(data_frame_SB,'day','SB_peak_frequency',imp_ax2,color='black', xlab = 'Day',ylab = 'SB_peak_frequency')
        fig_dif2.savefig(imp_folder+'SB_peak_frequency')
        
        fig_dif3,imp_ax3 = plt.subplots(figsize=(7, 5))
        RL.PlotRSDif(data_frame_SB,'day','SB_zdff_max',imp_ax3,color='black', xlab = 'Day',ylab = 'SB_zdff_max')
        fig_dif3.savefig(imp_folder+'SB_zdff_max')
        
        fig_dif4,imp_ax4 = plt.subplots(figsize=(7, 5))
        RL.PlotRSDif(data_frame_SB,'day','SB_average_peak_value',imp_ax4,color='black', xlab = 'Day',ylab = 'SB_average_peak_value')
        fig_dif4.savefig(imp_folder+'SB_zdff_maxSB_average_peak_value')
    
    fig_dif1,imp_ax1 = plt.subplots(figsize=(7, 5))
    RL.PlotRSDif(data_frame_pfw,'day','route_score',imp_ax1,color='black', label = 'preferred well', xlab = 'Day',ylab = 'Route Score')
    RL.PlotRSDif(data_frame_lpfw,'day','route_score',imp_ax1,color='green', label = 'less preferred well',xlab = 'Day',ylab = 'Route Score')
    fig_dif1.savefig(imp_folder+'RouteScore')
    
    fig_dif5,imp_ax5 = plt.subplots(figsize=(7, 5))
    RL.PlotRSDif(data_frame_pfw,'day','z_dif',imp_ax5,color='black', label = 'preferred well', xlab = 'Day',ylab = 'z_dif')
    RL.PlotRSDif(data_frame_lpfw,'day','z_dif',imp_ax5,color='green', label = 'less preferred well',xlab = 'Day',ylab = 'z_dif')
    fig_dif5.savefig(imp_folder+'z_dif')
    
    plt.close()
    return
    

def PlotRSForMultipleMouse(input_folder,output_folder,y1_column='route_score',y2_column='z_dif'):
    csv_files = ReadFiles(input_folder)
    tot_SB = True
    for i in range (len(csv_files)):
        if (csv_files[i].lag):
            continue
        op = output_folder+csv_files[i].ID
        if not os.path.exists(op):
            os.makedirs(op)
        if (not csv_files[i].avg):
            fig_zdif,ax = plt.subplots(figsize=(7, 5))
            RL.PlotLagDif(csv_files[i].df,'day','pct_high',ax,color='blue', label = 'max signal before collecting the reward', xlab = 'Day',ylab = 'z-score of the signal')
            RL.PlotLagDif(csv_files[i].df,'day','pct_low',ax,color='green', label = 'min signal after collecting the reward',xlab = 'Day',ylab = 'z-score of the signal')
            
            
        if (not csv_files[i].avg) and csv_files[i].pfw:
            RL.PlotLagDif(csv_files[i].df,'day','z_dif',ax,color='black', label = 'z_dif',xlab = 'Day',ylab = 'z-score of the signal',title='z_dif for preferred well',axh=True)
            fig_zdif.savefig(op+'/Preferred_Well_zdif.png')
            fig = PlotDoubleY(csv_files[i].df,y1_column,y2_column)
            fig.savefig(op+'/Preferred_Well_RS.png')
            
        if (not csv_files[i].avg) and (not csv_files[i].pfw):
            RL.PlotLagDif(csv_files[i].df,'day','z_dif',ax,color='black', label = 'z_dif',xlab = 'Day',ylab = 'z-score of the signal',title='z_dif for less preferred well',axh=True)
            fig_zdif.savefig(op+'/Less_Preferred_Well_zdif.png')
            fig = PlotDoubleY(csv_files[i].df,y1_column,y2_column)
            fig.savefig(op+'/Less_Preferred_Well_RS.png')
        if (csv_files[i].avg) and (csv_files[i].ContainSB):
            sbop = output_folder+csv_files[i].ID+'/SB/'
            if not os.path.exists(sbop):
                os.makedirs(sbop)
            fig_SBPK,ax1 = plt.subplots(figsize=(7, 5))
            RL.PlotLagDif(csv_files[i].df,'day','SB_peak_frequency',ax1,color='green', xlab = 'Day',ylab = 'Transient frequency')
            fig_SBPK.savefig(sbop+'SB_peak_frequency.png')
            fig_SB_zdff,ax2 = plt.subplots(figsize=(7, 5))
            RL.PlotLagDif(csv_files[i].df,'day','SB_zdff_max',ax2,color='green', xlab = 'Day',ylab = 'SB_zdff_max')
            fig_SB_zdff.savefig(sbop+'SB_zdff_max.png')
            fig_SB_APK,ax3 = plt.subplots(figsize=(7, 5))
            RL.PlotLagDif(csv_files[i].df,'day','SB_average_peak_value',ax3,color='green', xlab = 'Day',ylab = 'SB_average_peak_value')
            fig_SB_APK.savefig(sbop+'SB_average_peak_value.png')
        if (csv_files[i].avg) and not (csv_files[i].ContainSB):
            tot_SB = False
            
    csv_files_norm_pfw,csv_files_norm_lpfw,csv_files_day_avg = IntegrateData(csv_files)

    fig = PlotDoubleY(csv_files_norm_pfw, y1_column,y2_column)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    fig.savefig(output_folder+'Preferred_well_Tot.png')
    
    fig = PlotDoubleY(csv_files_norm_lpfw, y1_column,y2_column)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    fig.savefig(output_folder+'Less_Preferred_well_Tot.png')
    PlotTwoDif(csv_files_norm_pfw, csv_files_norm_lpfw, csv_files_day_avg,output_folder, tot_SB)

    return
                
                
#%%
# input_folder = '/Users/zhumingshuai/Desktop/Programming/Photometry/output/'
# output_folder = '/Users/zhumingshuai/Desktop/Programming/Photometry/output/'
# PlotRSForMultipleMouse(input_folder,output_folder,'route_score', 'z_dif')


