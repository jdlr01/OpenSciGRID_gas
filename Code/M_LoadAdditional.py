# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 11:13:05 2019

@author: diet_jn
"""
import Code.M_Internet    as M_Internet
import Code.M_GB    as M_GB
import Code.M_EntsoG    as M_EntsoG
import Code.M_LKD    as M_LKD
import Code.M_GIE    as M_GIE
import Code.M_GSE    as M_GSE
import Code.M_IGU    as M_IGU
import Code.M_GasLib    as M_GasLib
import Code.M_CSV       as M_CSV
import os

def loadData(DataLocationType = 'Data_Raw_CSV', sourceList = ['InterNet', 'EntsoG', 'LKD', 'GB', 'GIE', 'GSE', 'IGU', 'GasLib_135', 
                                                     'GasLib_582', 'GasLib_4197']):
    """Method of generating of a combined network instance from different sources, and 
    generation of a markdown html document for documentation.

        \n.. comments: 
        Input:
            DataLocationType: string indicating from where the read the data in from. Options are:
                            **source**: tools will go to source to get data.
                            **Data_Raw_CSV**: Data was read in from source before and 
                                                stored into CSV files.
                            **Data_Modified_CSV**: Data was read in from source and 
                                                modifications have been carried out before 
                                                saved into CSV files.
                            [default = 'Data_Raw_CSV']
            sourceList:     List of data source names
                            [default = ['InterNet', 'EntsoG', 'LKD', 'GB', 'GIE', 'GSE', 'IGU', 'GasLib_135', 'GasLib_582', 'GasLib_4197']]
        Output:
            Netz_DasNetz    Dictionary of Instance of the network classes
    """

#    compNames       = ['LNGs', 'Compressors', 'Storages', 'PipeSegments', 'Nodes']
#    Netz_DasNetz    = []
#    fileNameIn      = str(baseDirName + 'Dokumentation/Source/SciGrid_DatenUebersicht.md')
#    fileNameOut     = str(baseDirName + 'Dokumentation/Build/SciGrid_DatenUebersicht.md')
    #####################################################################
    # 1. Loading of data
    #####################################################################
    data_sources = {}
    if DataLocationType == 'source':
        if 'GB' in sourceList:
            data_sources['GB']              = M_GB.read()
        if 'InterNet' in sourceList:
            data_sources['InterNet']        = M_Internet.read()
        if 'EntsoG' in sourceList:
            data_sources['EntsoG']          = M_EntsoG.read()
        if 'LKD' in sourceList:
            data_sources['LKD']             = M_LKD.read()
        if 'GIE' in sourceList:
            data_sources['GIE']             = M_GIE.read(requeYear = list(range(1999, 2020)))
        if 'GSE' in sourceList:
            data_sources['GSE']             = M_GSE.read()
        if 'IGU' in sourceList:
            data_sources['IGU']             = M_IGU.read()
        if 'GasLib_135' in sourceList:
            data_sources['GasLib_135']      = M_GasLib.read(sourceName = 'GasLib-135')
        if 'GasLib_582' in sourceList:
            data_sources['GasLib_582']      = M_GasLib.read(sourceName = 'GasLib-582')
        if 'GasLib_4197' in sourceList:
            data_sources['GasLib_4197']     = M_GasLib.read(sourceName = 'GasLib-4197')
        
    elif DataLocationType == 'Data_Raw_CSV' or DataLocationType == 'Data_Modified_CSV':
        if DataLocationType == 'Data_Raw_CSV': 
            DataLocationType = 'Data_Raw'
        else:
            DataLocationType = 'Data_Modified'
            
            
        if 'GB' in sourceList:
            data_sources['GB']              = M_CSV.read(os.path.join(('Ausgabe/GB/' + DataLocationType + '/')))
        if 'InterNet' in sourceList:
            data_sources['InterNet']        = M_CSV.read(os.path.join(('Ausgabe/InternetDaten/' + DataLocationType + '/')))
        if 'EntsoG' in sourceList:      
            data_sources['EntsoG']          = M_CSV.read(os.path.join(('Ausgabe/EntsoG/' + DataLocationType + '/')))
        if 'LKD' in sourceList:
            data_sources['LKD']             = M_CSV.read(os.path.join(('Ausgabe/LKD/' + DataLocationType + '/')))
        if 'GIE' in sourceList:
            data_sources['GIE']             = M_CSV.read(os.path.join(('Ausgabe/GIE/' + DataLocationType + '/')))
        if 'GSE' in sourceList:
            data_sources['GSE']             = M_CSV.read(os.path.join(('Ausgabe/GSE/' + DataLocationType + '/')))
        if 'IGU' in sourceList:
            data_sources['IGU']             = M_CSV.read(os.path.join(('Ausgabe/IGU/' + DataLocationType + '/')))
        if 'GasLib_135' in sourceList:
            data_sources['GasLib_135']      = M_CSV.read(os.path.join(('Ausgabe/GasLib_135/' + DataLocationType + '/')))
        if 'GasLib_582' in sourceList:
            data_sources['GasLib_582']      = M_CSV.read(os.path.join(('Ausgabe/GasLib_582/' + DataLocationType + '/')))
        if 'GasLib_4197' in sourceList:
            data_sources['GasLib_4197']     = M_CSV.read(os.path.join(('Ausgabe/GasLib_4197/' + DataLocationType + '/')))


    return data_sources