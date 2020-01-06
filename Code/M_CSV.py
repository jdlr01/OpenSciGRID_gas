# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:12:17 2018

@author: apluta
"""
import os
import pandas as pd
import Code.K_Netze          as K_Netze
import Code.K_Component      as K_Component
import numpy as np
import Code.C_colors         as CC
import Code.M_FindPos        as M_FindPos
from   pathlib           import Path
import math
import pandas                as pd



def CSV_Write(file, subkeys, subvalues):
    """Description:
    -------------
        Schreibt die Eigenschaften(subkeys) eines Netzattribute in ein File
        zusammen mit seinen werten (subvalues)
        file = filepath+name.csv (des Netzattributes)
    Input:
    ------
        file        String containing absolute path and name to file
        subkeys     
        subvalues
    Called by:
    ----------
        WriteCSVfiles()
    
    Needs: 
    ------
        Panda, Numpy
    """
    
#    units1      = subkeys # hier sollen eigentlich die erste reihe einheiten hin
#    units2      = subkeys # hier sollen die zweite Reihe einheiten hin
#    subkeys     = [subkeys, units1, units2]
    # Nutze numpy für spätere Matrixtransposition T um aus den eingabe Arrays
    # ein DatenFrame zu konstruieren
    tsubvalues  = np.matrix(subvalues)
    tsubvalues  = np.transpose(tsubvalues)
    df          = pd.DataFrame(tsubvalues, subkeys)
    df.T.to_csv(file,sep=';', index = False, na_rep = 'None')




def write(RelDirName = 'Eingabe/CSV/', Grid = []):
    """Writes Instance of Netz-Class (**Grid**) into CSV tables, located in relative folder **RelDirName**.

..comments: 
    Input:
        CSV_Path_write:  Output Directory
        Grid:          Instance of Netz Class
    Return:
        []
    """
    # dir name
    dataFolder = os.getcwd()
    DirName = os.path.join(dataFolder, RelDirName)
    
    FileList = Grid.CompLabels()

    if os.path.isdir(DirName) is not True:
        os.makedirs(DirName)

    list(map(os.unlink, (os.path.join( DirName,f) for f in os.listdir(DirName)) ) )
    
    for key in FileList:
        # Resetting values
        subkeys             = []
        dictSubKeysParam    = []
        dictSubKeysMethod   = []
        subvalues           = []
        tempsubvalues       = []
        i                   = 0
        dictSubKeysUncertainty = []
        # groing through each component, as long as length larger than 0
        if len(Grid.__dict__[key]) > 0:
            for subkey in Grid.__dict__[key][0].__dict__.keys():
                if 'param' in subkey:
                    for subKey2 in Grid.__dict__[key][0].param.keys():
                        subkeys.append(subKey2)
                        dictSubKeysParam.append(subKey2)
                elif 'uncertainty' in subkey:
                    for subKey2 in Grid.__dict__[key][0].uncertainty.keys():
                        subkeys.append(subKey2)
                        dictSubKeysUncertainty.append(subKey2)
                elif 'method' in subkey:
                    for subKey2 in Grid.__dict__[key][0].method.keys():
                        subkeys.append(subKey2)
                        dictSubKeysMethod.append(subKey2)
                elif 'tags' in subkey:
                    for subKey2 in Grid.__dict__[key][0].tags.keys():
                        subkeys.append(subKey2)
                        dictSubKeysMethod.append(subKey2)
                else:
                    subkeys.append(subkey)
                    
            # Loop for number of Components
            fileSubKeys = []
            if len(Grid.__dict__[key]) > 0:
                subkeys         = Grid.__dict__[key][i].__dict__.keys()
                for ss in subkeys:
                    fileSubKeys.append(ss)

            for i in range(len(Grid.__dict__[key])):
                subvalue        = Grid.__dict__[key][i].__dict__.values()
                tempsubvalues   = []
                for val, subkey in zip(subvalue, subkeys):
                    tempsubvalues.append(val)
                        
                subvalues.append(tempsubvalues)
                
            if 'Meta_' in key:
                # Writing the compopnent meta data
                CSV_Write(os.path.join((DirName), key + '.csv'), fileSubKeys, subvalues)    
            else:
                # Writing the component position data
                CSV_Write(os.path.join((DirName),'Gas_' + key + '.csv'), fileSubKeys, subvalues)    
        else: 
            pass



def read(RelDirName = 'Eingabe/CSV/', NumDataSets = 1e+100, skiprows = []):
    """Description:
    ------------
        Reads Data from folder CSV_Path into Grid 
        Grid = Instance of Netz Class
        
    Input Parameter:
    ----------------
        CSV_Path        string containing path name of data location
        
    Return Parameters:
    ------------------
        Grid            instance of class K_Netze.Netz, populated with 
                         data from CSV files  """
    # Dir name stuff
    DirName     = Path.cwd() /  RelDirName

    Grid        = K_Netze.NetComp()
    FileList    = K_Netze.NetComp().CompLabels()
    for key in FileList:
        count       = 0
        filename    = 'Gas_' + key + '.csv'
        CSV_File    = str(DirName / filename)

        # Z set to zero if file does not exist
        Z           = CSV_2_list(CSV_File, skiprows = skiprows)
        if len(Z) > 0:
            for entry in Z:
                Keys    = list(entry.keys())
                Vals    = list(entry.values())
                for ii in range(len(Vals)):
                    if Vals[ii] == 'None':
                        Vals[ii] = None
                    elif type(Vals[ii]) is float:
                        if math.isnan(Vals[ii]):
                            Vals[ii] = None
                    else:
                        try:
                            Vals[ii] = float(Vals[ii])
                        except:
                            pass
                        
                pos_Id   = M_FindPos.find_pos_StringInList('id', Keys)
                pos_Name = M_FindPos.find_pos_StringInList('name', Keys)
                pos_SId  = M_FindPos.find_pos_StringInList('source_id', Keys)
                pos_Node = M_FindPos.find_pos_StringInList('node_id', Keys)
                pos_CC   = M_FindPos.find_pos_StringInList('country_code', Keys)
                pos_lat  = M_FindPos.find_pos_StringInList('lat', Keys)
                pos_long = M_FindPos.find_pos_StringInList('long', Keys)
                pos_comm = M_FindPos.find_pos_StringInList('comment', Keys)
                pos_para = M_FindPos.find_pos_StringInList('param', Keys)
                pos_meth = M_FindPos.find_pos_StringInList('method', Keys)
                pos_unce = M_FindPos.find_pos_StringInList('uncertainty', Keys)
                pos_tags = M_FindPos.find_pos_StringInList('tags', Keys)
                
                del entry['id']
                del entry['name']
                del entry['source_id']
                del entry['node_id']
                del entry['country_code']

                del entry['lat']
                del entry['long']
                del entry['comment']
                del entry['param']
                del entry['method']
                del entry['uncertainty']
                del entry['tags']

                
                id          = Vals[pos_Id[0]]
                name        = Vals[pos_Name[0]]
                source_id   = makeList(Vals[pos_SId[0]])
                node_id     = makeList(Vals[pos_Node[0]])
                country_code = makeList(Vals[pos_CC[0]])

                lat         = Vals[pos_lat[0]]
                if isinstance(lat, str):
                    lat         = eval(lat)
                    
                long        = Vals[pos_long[0]]
                if isinstance(long, str):
                    long        = eval(long)
                    
                comment     = Vals[pos_comm[0]]
                param       = eval(Vals[pos_para[0]].replace(': nan,', ': float(\'nan\'),'))
                method      = eval(Vals[pos_meth[0]].replace(': nan,', ': float(\'nan\'),'))
                uncertainty = eval(Vals[pos_unce[0]].replace(': nan,', ': float(\'nan\'),'))
                tags        = eval(Vals[pos_tags[0]].replace(': nan,', ': float(\'nan\'),'))
                
                Grid.__dict__[key].append(K_Component.__dict__[key](id = id, 
                             name       = name,
                             source_id  = source_id, 
                             node_id    = node_id,
                             country_code = country_code, 
                             param      = param,
                             lat        = lat,
                             long       = long,
                             method     = method,
                             uncertainty = uncertainty,
                             tags       = tags,
                             comment    = comment))
                count = count + 1
                if count >= NumDataSets:
                    break
        else:
            Grid.__dict__[key]      = []
            
    return Grid




def makeList(stringVal):
    """Function to convert a string values into a list"""
	
    listVal = []
    if stringVal != None:
        if isinstance(stringVal, str):
            if '[\'' in stringVal and '\']' in stringVal:
                stringVal = stringVal[1:-2]
                stringVal   = stringVal
                stringVal   = stringVal.replace('\', \'', '\',\'')
                for val in stringVal.split(','):
                    if val[0] == '\'':
                        val = val[1:]
                    if val[-1] == '\'':
                        val = val[:-1]
                    listVal.append(val)
            else:
                listVal = stringVal
        else:
            listVal = stringVal
            
    else:
        listVal = stringVal
            
    return listVal



def read_CSV_raw(CSV_Path):
    """Reading a CSV file where first line is column labels
    """

    df          = pd.read_csv(CSV_Path, sep = ";")
    DictList    = []
    dictVal     = {}
    colNames    = df.columns
    
    for idx in range(df.shape[0]):
        dictVal    = {}
        for colName in colNames:
            dictVal.update({colName:df[colName][idx]})
        DictList.append(dictVal)
    
    
    
    return     DictList





def read_CSV(CSV_Path):
    """Description:
    ------------
        Reads Data from folder CSV_Path into Grid 
        Grid = Instance of Netz Class
        
    Input Parameter:
    ----------------
        CSV_Path        string containing path name of data location
        
    Return Parameters:
    ------------------
        Grid            instance of class K_Netze.Netz, populated with 
                         data from CSV files"""
						 
    FileList = ['BorderPoints', 'PipePoints', 'Compressors', 'Nodes', 'EntryPoints', 
                'InterConnectionPoints', 'LNGs', 'Meta_BorderPoints', 'Meta_Compressors', 
                'Meta_EntryPoints', 'Meta_InterConnectionPoints', 'Meta_LNGs', 
                'Meta_PipePoints', 'Meta_Storages', 'Storages']
    
    print('')
    print(CC.Caption+'Load CSV-Data into Grid'+CC.End)
    print('--------------------------------------')      
	
    Grid = K_Netze.NetComp()
    Grid.Processes.append(K_Netze.Processes('M_CSV.read_CSV'))
    
    for filename in os.listdir(CSV_Path):
        # check if Filename is used for Import
        for key in FileList:
            if 'Meta_' in key:
                filename = key + '.csv'
            else:
                filename = 'Gas_' + key + '.csv'
            CSV_File                = os.path.join((CSV_Path),(filename))
            Z                       = CSV_2_list(CSV_File)
            if len(Z) > 0:
                for entry in Z:
                    Keys = list(entry.keys())
                    Vals = list(entry.values())
                    posId   = M_FindPos.find_pos_StringInList('id', Keys)
                    posName = M_FindPos.find_pos_StringInList('name', Keys)
                    del entry['id']
                    del entry['name']
                    Grid.__dict__[key].append(K_Netze.__dict__[key](id = Vals[posId[0]], 
                                 name       = Vals[posName[0]], 
                                 param      = entry))
            else:
                Grid.__dict__[key]      = []
            
    return Grid




def CSV_2_list(file, skiprows = []):
    """Description:
    ------------
        Liest ein Netzattribute aus einer CSV-datei (file) als Dataframe ein 
        und liefert eine Liste zurück
    Parameter:
    -----------
        file = filepath+name.csv (des Netzattributes)
    Needs: 
    -------
        Panda Library
    called by: 
    -----------
        read_CSV()
    """ 
    if os.path.isfile(file):
        with open(file,'rt', encoding = 'iso-8859-15', errors = 'ignore') as csvfile:
            df = pd.read_csv(csvfile, sep =';', skiprows = skiprows)
            liste = []
            liste = df.T.to_dict().values()
        
            return liste
    else:
        return []
