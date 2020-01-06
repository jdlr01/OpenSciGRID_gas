#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import math
import Code.M_Helfer       as M_Helfer
from matplotlib        import dates
import matplotlib.pyplot   as plt
import os

def plotHist(plt = [], dataList = [], binNum = 10, newPlot = True, lengendStr = ''):
    '''Creation Hist Plot in figure
    
    '''

    if dataList != []:
        bins = np.linspace(math.ceil(min(dataList)), 
                       math.floor(max(dataList)),
                       binNum) 
    
        if plt == []:
            plt.figure(0, figsize = (5,5))
    
        if newPlot:
            plt.clf()
            
            
        plt.hist(dataList, bins=bins, alpha=0.5, legend = lengendStr)
    
    return plt




def plot_FDC(Data, DirNamePlot = 'Ausgabe/Temp/', figureNum = 0, Speicher_Graphen = True):
    """
Function to create a FDC from time series and plot. Inputs are **Data** (of type K_Netze.EntsoG_GasFlow) string for ouput directory **DirNamePlot**, figure number **figureNum**, and boolean to save plot to file via **Speicher_Graphen**.

.. comments: 
    Input:
        Data        		Element of K_Netze.EntsoG_GasFlow
		DirNamePlot: 		string containing path name for optional 
        figureNum:    		Integer of plot number, default = 0
		Speicher_Graphen: 	boolean to save plot to file.
    Return:
        []
    
    """
    # Initialization
    formatter           = dates.DateFormatter('%b %y')
    values_Entry_sorted = []


    values_Exit_sorted  = []
    FileName            = os.path.basename(Data.fileName)
    FileName            = FileName[0:-4]
    FileName            = DirNamePlot + FileName + '.jpg'
    fileName            = os.path.basename(Data.fileName)
    fileName            = fileName[0:-4]
    #print('Plot: ' + fileName)
    # Kreieren des ersten Graphen s
    plt.figure(figureNum, figsize = (5,5))
    plt.clf()

    # plotting the FDC
    values_Entry          = Data.values_Entry
    intervalStart_Entry   = Data.intervalStart_Entry
    values_Exit           = Data.values_Exit
    intervalStart_Exit    = Data.intervalStart_Exit
    
    # Plotting time series
    if 'both' in Data.directionKey:
        plt.subplot(411)
        plt.plot(intervalStart_Entry, values_Entry, 'g-')

        plt.ylabel('[' + Data.unit + ']')
        ax      = plt.gcf().axes[0] 
        ax.xaxis.set_major_formatter(formatter)
        plt.gcf().autofmt_xdate(rotation=25)
    



        plt.title(fileName)

        plt.subplot(412)
        plt.plot(intervalStart_Exit,  values_Exit,  'r-')
        plt.ylabel('[' + Data.unit + ']')
        ax      = plt.gcf().axes[0] 
        ax.xaxis.set_major_formatter(formatter)
        plt.gcf().autofmt_xdate(rotation=25)
    elif 'entry' in Data.directionKey:
        plt.subplot(211)
        if len(values_Entry) > 0:
            plt.plot(intervalStart_Entry, values_Entry, 'g-')
            plt.title(fileName)
            plt.ylabel('[' + Data.unit + ']')
            ax      = plt.gcf().axes[0] 
            ax.xaxis.set_major_formatter(formatter)
            plt.gcf().autofmt_xdate(rotation=25)
    elif 'exit' in Data.directionKey:
        plt.subplot(211)
        if len(values_Exit) > 0:
            plt.plot(intervalStart_Exit, values_Exit, 'g-')
            plt.title(fileName)
            plt.ylabel('[' + Data.unit + ']')
            ax      = plt.gcf().axes[0] 
            ax.xaxis.set_major_formatter(formatter)
            plt.gcf().autofmt_xdate(rotation=25)
    
    
    #N   = len(values)
    for vv in values_Entry:
        values_Entry_sorted.append(vv)
    for vv in values_Exit:
        values_Exit_sorted.append(vv)
    
    # Removing zeros or nanas
    for ii in range(len(values_Entry_sorted)):
        if values_Entry_sorted[ii] == 0:
            values_Entry_sorted[ii] = float(0.01)
    for ii in range(len(values_Exit_sorted)):
        if values_Exit_sorted[ii] == 0:
            values_Exit_sorted[ii] = float(0.01)
            
            
    values_Entry_sorted = sorted([x for x in values_Entry_sorted if not math.isnan(x)])
    values_Exit_sorted  = sorted([x for x in values_Exit_sorted  if not math.isnan(x)])
    
    
    
    # Plotting FDC
    plt.subplot(212)
    [X_Entry, Y_Entry] = M_Helfer.shrink_Data(range(len(values_Entry_sorted)), values_Entry_sorted, 200)
    [X_Exit, Y_Exit]   = M_Helfer.shrink_Data(range(len(values_Exit_sorted)),  values_Exit_sorted,  200)
    




    # scaling Data
    for ii in range(len(Y_Entry)):
        Y_Entry[ii] = Y_Entry[ii]/max(Y_Entry)
    for ii in range(len(Y_Exit)):
        Y_Exit[ii]  = Y_Exit[ii]/max(Y_Exit)
    
    
    plt.plot(X_Entry, Y_Entry, 'k-')
    plt.plot(X_Entry, Y_Entry, 'g.')
    plt.plot(X_Exit, Y_Exit, 'k-')
    plt.plot(X_Exit, Y_Exit, 'r.')

    plt.xlabel('percentile [%]')
    plt.ylabel('[a.u.]')
    plt.ylim(0, 1)
    plt.xlim(0, 100)
    
    try:
        plt.tight_layout()
    except:
        print('error')
            
    plt.show()
    
    # Speichern des Graphens
    if Speicher_Graphen == True:
        plt.savefig(FileName)


    plt.close()
    return []

def Wrapper_PlotLines(coord, type = 'line', Symbol = 'k-'):
    plt.figure(0)
    count = 0
    if type == 'line':
        for ii in range(int(len(coord) - 1)):
            x       = [coord[count][0], coord[count+1][0]]
            y       = [coord[count][1], coord[count+1][1]]
            count   = count + 1
            plt.plot(x, y, Symbol)
            
    elif type == 'point':
        plt.plot(coord[0], coord[1],'r.')
        




