# -*- coding: utf-8 -*-
"""
M_Filter
---------

Collection of functions, that are being called from other modules, for 
filtering data/meta-data based on user specified values.  
"""

import math



def filter_Daten(InfoFilter, MetaData):
    """ Filtering of meta data, in respect of start_year,  end_year and license.  
    Input are **InfoFilter**, and **MetaData**.
    
    \n.. comments:
    Input:
        InfoFilter      Dictionary of filter settings,
                            thisFilter =	{"year": ['2000',], 
                                              "license": ['Wikipedia',], 
                                              "Is_H_gas": [1,]}
        MetaData        Data of the  class K_Netze.(component)
    Return:
        MetaData        List of  points """
    count = 0
    # Filter : DateYear
    try:
        if len(InfoFilter['year']) > 0:
            MetaDataNeu = []
            for line in MetaData:
                Pass1 = 0
                Pass2 = 0
                for FilterYearStr in InfoFilter['year']:
                    if len(FilterYearStr) == 0:
                        Pass1 = 1
                        Pass2 = 1
                    else:
                        FilterYear  = int(FilterYearStr)
                        if line.start_year == None:
                            Pass1 = 1
                        elif math.isnan(line.start_year):
                            Pass1 = 1
                        elif line.start_year <= FilterYear:
                            Pass1 = 1
                            
                        if line.end_year == None:
                            Pass2 = 1
                        elif math.isnan(line.end_year):
                            Pass2 = 1
                        elif line.end_year >= FilterYear:
                            Pass2 = 1
                        
                    if Pass1 and Pass2:
                        MetaDataNeu.append(line)
                    
            # Return what shall be kept
            MetaData = MetaDataNeu
            
    except:
        count = count + 1
        
        
        
    # Filter : Lizenz
    try:
        if len(InfoFilter['license'])>0:
            MetaDataNeu  = []
            
            if "license" in dir(MetaData[0]):
                for line in MetaData:
                    Pass1 = 0
                    for Lizenz in InfoFilter['license']:
                        if type(line.license) == str:
                            if len(Lizenz) == 0:
                                if len(line.license) == 0:
                                    Pass1 = 1
                            else:
                                if line.license.find(Lizenz)>-1:
                                    Pass1 = 1
                    if Pass1 == 1:
                        MetaDataNeu.append(line)
                        count = count + 1
                            
                    
                # Return what shall be kept
                MetaData = MetaDataNeu
            
    except:
        count = count + 1


    # Filter : GasType
    try:
        if len(InfoFilter['Is_H_gas'])>0:
            MetaDataNeu  = []
            
            if "is_H_gas" in dir(MetaData[0]):
                for line in MetaData:
                    Pass1 = 0
                    for GasType in InfoFilter['Is_H_gas']:
                        if len(GasType) == 0:
                            if len(line.is_H_gas) == 0:
                                Pass1 = 1
                        elif line.is_H_gas.find(GasType)>-1:
                            Pass1 = 1
                    if Pass1 == 1:
                        MetaDataNeu.append(line)
                        
                # Return what shall be kept
                MetaData = MetaDataNeu
                
            
    except:
        count = count + 1
    
    return MetaData 