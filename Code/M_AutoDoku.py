#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:13:44 2019

@author: apluta
"""

import Code.M_Visuell       as M_Visuell
import shutil
import matplotlib.pyplot    as plt
import os



def summary2File(data_sources,  CompNames = ['LNGs', 'Compressors', 'Storages', 'PipeSegments', 'Nodes'], sourceList = ['InterNet', 'EntsoG', 'LKD', 'GB', 'GIE', 'GSE', 'IGU', 'GasLib_135', 'GasLib_582', 'GasLib_4197']):
    """Function of writing meta data to a markdown document.

		\n.. comments: 
		Input:
        data_sources    dict of all data sources
			CompNames: 		List of component to creat a table for
							(default = ['LNGs', 'Compressors', 'Storages', 'PipeSegments', 'Nodes'])
			sourceList: 	List of sources that shall be incorporated
							(default = ['InterNet', 'EntsoG', 'LKD', 'GB', 'GIE', 'GSE', 'IGU', 'GasLib_135', 'GasLib_582', 'GasLib_4197'])
		Output:
			1 	
    """		
    baseDirName 	= os.getcwd()
    fileNameIn      = str(baseDirName / 'Dokumentation/Source/03_DataSources/02_NonOSM/99_Summary/SciGrid_DatenUebersicht.md')
    fileNameOut     = str(baseDirName / 'Dokumentation/Source/03_DataSources/02_NonOSM/99_Summary/99_Summary.md')
    
    
    
    #####################################################################
    # 3. Writing of tables
    #####################################################################
    print('summary2File: 3. Writing of tables')
    # Copying source file into new location 
    shutil.copyfile(fileNameIn, fileNameOut)
    
    with open(fileNameOut, 'a') as writer:
        for compName in CompNames:
            print('summary2File: 3.X Writing of component: ' + compName)
            
            ############################################
            ### Header and total number
            ############################################
            data_vals = []

            # cal of values and put into list
            for key in sourceList:
                data_vals.append(str(len(getattr(data_sources[key], compName))))

            # writing the new stuff            
            writer.write('\n  ')
            writer.write('\n   ')
            writer.write('\n<!---  ---------------------------------------------------- --->  ')
            writer.write('\n### {c}<a name=''id-SS-DU-{c}''></a>    '.format(c=compName))
            writer.write('\n<!---  ---------------------------------------------------- --->    ')
            writer.write('\n  ')
            writer.write('Below is a table, indicating for the component of {} which data set which data source has how many elements available.\n  '.format(compName))
            writer.write('Component | ' + ' | '.join(sourceList) + '|\n')
            writer.write('--- | ' + ' | '.join(['---' for source in sourceList]) + '|\n')
            writer.write('**Total number** | ' + ' | '.join(data_vals) + '|\n')
            
            
            ############################################
            ### Generation of list of attributes
            ############################################

            allKeys     = []
            data_vals   = []
            
            for sourceName in sourceList:
                if len(data_sources[sourceName].__dict__[compName]) > 0:
                    for key in (data_sources[sourceName].__dict__[compName][0].__dict__['param'].keys()):
                        allKeys.append(str(key))
                    
            # making unique list
            allKeys = sorted(list(set(allKeys)))
            # removing those attrib lables that contain no gas info
            for key in ['uncer', 'method', 'source', 'status', 'name_short', 'comment', 'tpMapX', 'tpMapY', 'license', 'comp_id']:
                try: allKeys.remove()
                except: pass
            
            # Populating the table for each attribute                
            for key in allKeys:
                data_vals = []
                for sourceName in sourceList:
                    data_vals.append(str(data_sources[sourceName].get_AttribDensity(compName, key)[key] ))
                writer.write(key + ' | ' + ' | '.join(data_vals) + '|\n')

    return 1





def source_summary2File(Netz, netzName, fileNameIn, fileNameOut, picNameOut = ''):
    """Method of generating of a markdown html document for documentation.

		\n.. comments: 
		Input:
		    netzName: 		String of network name
        fileNameIn: 	Location and name of input mark up file name
        fileNameOut: 	Location and name of output mark up file name
        picNameOut: 	Name and location of picture jpg file.
							(default = '')
    """		
    
    attribIgnore = ['id', 'name', 'source_id', 'node_id', 'comp_id', 'lat', 
                    'country_code', 'exact', 'source', 'license', 'comment', 
                    'tpMapX', 'tpMapY', 'pointKey', 'pointLabel', 'dataSet', 
                    'uncertainty', 'method', 'name_short', 'long', 'meta_id',
                    'tags']
    AttribDesc = Netz.AttribDesc()
    
    # Copying source file into new location 
    shutil.copyfile(fileNameIn, fileNameOut)
    
    with open(fileNameOut, 'a') as writer:
        # writing the new stuff            
#        writer.write('\n  ')
#        writer.write('\nThis is a summary of the data set **{}-data**.  '.format(netzName))
#        writer.write('\n   ')
#        writer.write('\n   ')
#        writer.write('\n<!---  ---------------------------------------------------- --->  ')
#        writer.write('\n### Components<a name=''id-SS-NS-Components''></a>    ')
#        writer.write('\n<!---  ---------------------------------------------------- --->    ')
#        writer.write('\n  ')
#        writer.write('\nThis network contains the following components with the following number of elements:  ')
#        writer.write('\nComponent name | num of elements|    ')
#        writer.write('\n---------------|----------------|    ')
#        for key in Netz.CompLabels():
#            if len(Netz.__dict__[key]) > 0:
#                writer.write('\n{}|{}|   '.format(key, str(len(Netz.__dict__[key]))))
        writer.write('\n   ')
        writer.write('\n   ')

        writer.write('\n<!---  ---------------------------------------------------- --->  ')
        writer.write('\n### Data summary for each component<a name=''id-SS-NS-Attributes''></a>    ')
        writer.write('\n<!---  ---------------------------------------------------- --->    ')
        writer.write('\n   ')
        writer.write('\nThis section will list for each component, and will specify how many elements have some available data.    ')
        writer.write('\n   ')
        writer.write('\n   ')
        
        for compName in Netz.CompLabels():
            if len(Netz.__dict__[compName]) > 0:
#                if compName != 'Nodes':
                compLength      = len(Netz.__dict__[compName])
                compLengthStr   = str(compLength)
                AttribsNumbers  = Netz.get_AttribDensity(compName)
                
                writer.write('\n<!---  ---------------------------------------------------- --->  ')
                writer.write('\n#### **{}**<a name=''id-SS-NS-Attributes-{}''></a>    '.format(compName, compName))
                writer.write('\n<!---  ---------------------------------------------------- --->    ')
                writer.write('\n   ')
                writer.write('\nThis network contains {} elements of component type **{}**.    '.format(compLengthStr, compName))
                writer.write('\nThe component **{}** contains the following attribues,'.format(compName))
                writer.write('\nsummaried in the table below, with number of elements,')
                writer.write('\nthat contain information for this attribute ')
                writer.write('\n(elements, that do NOT have NONE as an entry).    ')
                writer.write('\n   ')
                writer.write('\nAttribute name | Brief description | num of elements|  ')
                writer.write('\n---------------|-------------------|----------------|  ')
                writer.write('\n{}|{}|{}|  '.format('id', AttribDesc['id'], compLengthStr))
                for subKey, keyVal in AttribsNumbers.items():
                    if subKey not in attribIgnore:
                        if subKey in AttribDesc:
                            writer.write('\n{}|{}|{}|  '.format(subKey, AttribDesc[subKey], str(keyVal)))
                        else:
                            writer.write('\n{}|{}|{}|  '.format(subKey, ' ', str(keyVal)))
                    
    # plotting new map of the network        
    if len(picNameOut) > 0:
        if netzName == 'GB':
            M_Visuell.quickplot(Netz, figureNum = 9999, savefile = picNameOut, countrycode = 'GB', LegendStyle = 'Str(Num)',PlotList =["Nodes"])
        elif (netzName == 'LKD') or ('GasLib' in netzName):
            M_Visuell.quickplot(Netz, figureNum = 9999, savefile = picNameOut, countrycode = 'DE', PlotList =["Nodes"])
        else:        
            M_Visuell.quickplot(Netz, figureNum = 9999, savefile = picNameOut, countrycode = 'EU', PlotList =["Nodes"])
        plt.close(9999)
        
        