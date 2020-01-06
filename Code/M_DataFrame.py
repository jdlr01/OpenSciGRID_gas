# -*- coding: utf-8 -*-
"""
M_DataFrame
-----------
Functions that help in dealing with Panda Data Frames

@author: diet_jn
"""
import numpy                   as np
import pandas                  as pd
import Code.M_CSV              as M_CSV
import Code.K_Component        as K_Component
import sys
import os


def drop_nan(df, df_actionMeta):
    """Removes nan from data frame, based on df_actionMeta.AttribNames. 
    **df**, **df_actionMeta**
    """
    N = df.shape[0]
    
    #RegType       = []
    This_Convert2Float      = []
    AttribNames   = []
    Simulate      = []
    
    for idx, attribName in enumerate(df_actionMeta.AttribNames):
        if df[attribName ].isnull().sum() == N:
            df.drop(attribName, axis = 1)
        else:
            #RegType.append(df_actionMeta.RegType[idx])
            This_Convert2Float.append(df_actionMeta.Convert2Float[idx])
            AttribNames.append(df_actionMeta.AttribNames[idx])
            Simulate.append(df_actionMeta.Simulate[idx])
    
    #df_actionMeta.RegType       = RegType
    df_actionMeta.Convert2Float = This_Convert2Float
    df_actionMeta.AttribNames   = AttribNames
    df_actionMeta.Simulate      = Simulate

    df.dropna()
    return df, df_actionMeta




def make_DataFrame(Netz, StatsInputDirName, This_AttribNames, thisCompName, ApplyLoad = False):
    '''Loading data from CSV and converting into data frame
    '''    
    
    # =======================================
    # 1. Data mport
    # =======================================
    df_actionMeta   = K_Component.DF_Action_Meta()
    
    # getting more meta data for Stats processes
    This_Convert2Float  = []
    This_RegType        = []
    This_Simulate       = []
    This_Load           = []
    DirName             = os.path.join(StatsInputDirName, 'StatsAttribSettings.csv')
    
    StatsCompName, AttribName, Load, Simualte, Convert2Float, RegressionType = get_AttribInfo(DirName)
    
    if len(This_AttribNames) == 0:
        for ida, compName in enumerate(StatsCompName):
            if  compName  == thisCompName:
                This_AttribNames.append(AttribName[ida])
                This_Convert2Float.append(Convert2Float[ida])
                This_RegType.append(RegressionType[ida])
                This_Simulate.append(float(Simualte[ida]))
                
                # Default setting to Load to 1 if simulation is required
                if float(Simualte[ida]) == 1:
                    This_Load.append(1)
                # Othewise get  load value from CSV file
                else:
                    This_Load.append(Load[ida])
                    
                   

    df_actionMeta.RegType       = This_RegType
    df_actionMeta.Convert2Float = This_Convert2Float
    df_actionMeta.AttribNames   = This_AttribNames
    df_actionMeta.Simulate      = This_Simulate
    
    # =======================================
    # 2. Data 2 DataFrame
    # =======================================
    df = pd.DataFrame()
    if ApplyLoad == False:
        # converting Netzdata into data frame
        for attribName in df_actionMeta.AttribNames:
            #print('attribName', attribName)
            wert = Netz.get_Attrib(thisCompName, attribName )
            N       = len(wert)
            NumNaN  = 0
            if len(wert) == 0:
                for ii in range(df.shape[0]):
                    wert.append(np.nan)
                    NumNaN  = NumNaN + 1
            else:
                for idy, ww in enumerate(wert):
                    if ww == None:
                        wert[idy] = np.nan
                        NumNaN  = NumNaN + 1
            if N > NumNaN:
                df[attribName] = np.array(wert)

    else:
        # converting Netzdata into data frame
        Th_Convert2Float  = []
        Th_RegType    = []
        Th_Simulate   = []
        Th_AttribNames= []
        
        for idx, attribName in enumerate(df_actionMeta.AttribNames):
            #print('    attribName ', attribName )
            if This_Load[idx] == 1:
                wert = Netz.get_Attrib(thisCompName, attribName )
                N       = len(wert)
                NumNaN  = 0
                if len(wert) == 0:
                    for ii in range(df.shape[0]):
                        wert.append(np.nan)
                        NumNaN = NumNaN + 1
                else:
                    for idy, ww in enumerate(wert):
                        if ww == None:
                            wert[idy] = np.nan
                            NumNaN = NumNaN + 1
                            
                # Add only if there is data
                if N > NumNaN:
                    df[attribName] = np.array(wert)
                    df[attribName] = np.array(wert)
                    
                    Th_AttribNames.append(df_actionMeta.AttribNames[idx])
                    Th_Convert2Float.append(df_actionMeta.Convert2Float[idx])
                    Th_RegType.append(df_actionMeta.RegType[idx])
                    Th_Simulate.append(df_actionMeta.Simulate[idx])
                

        df_actionMeta.AttribNames   = Th_AttribNames
        df_actionMeta.Convert2Float = Th_Convert2Float
        df_actionMeta.RegType       = Th_RegType
        df_actionMeta.Simulate      = Th_Simulate
               
        
    # now adjusting the "df_actionMeta" so that "AttribNames" only contains those ones that shall be simulated
    Th_AttribNames  = []
    Th_RegType      = []
    Th_Convert2Float       = []
    Th_Simulate     = []
    for idx, sim in enumerate(df_actionMeta.Simulate):
        if sim == 1:
            Th_AttribNames.append(df_actionMeta.AttribNames[idx])
            Th_Convert2Float.append(df_actionMeta.Convert2Float[idx])
            Th_RegType.append(df_actionMeta.RegType[idx])
            Th_Simulate.append(df_actionMeta.Simulate[idx])
            
    df_actionMeta.AttribNames   = Th_AttribNames
    df_actionMeta.Convert2Float = Th_Convert2Float
    df_actionMeta.RegType       = Th_RegType
    df_actionMeta.Simulate      = Th_Simulate


    return df, df_actionMeta




def rem_LowDensData(df, df_actionMeta):
    '''Removal of data from data framebased on densitz threshold
    
    '''
    # removing the ones requested from user through setup file
    NumRows     = df.shape[0]
    NoData      = []
    for idx, colName in enumerate(df_actionMeta.AttribNames): 
        if df_actionMeta.Simulate == 0:
            # removing the ones that have no data at all
            if NumRows - df[colName].isnull().sum() == 0:
                NoData.append(idx)
        elif (NumRows - df[colName].isnull().sum())/ NumRows > df_actionMeta.DataDensity[idx]:
            pass        
        else:
            df_actionMeta.Simulate[idx] = 0 
            if NumRows - df[colName].isnull().sum() == 0:
                print('raus',colName)
                NoData.append(idx)
    
    # removing the ones that have no data at all
    colNames = df.columns
    for idx in range(len(NoData)-1, -1, -1):
        #del df_actionMeta.RegType[NoData[idx]]
        del df_actionMeta.isFloats[NoData[idx]]
        del df_actionMeta.AttribNames[NoData[idx]]
        del df_actionMeta.DataDensity[NoData[idx]]
        del df_actionMeta.Simulate[NoData[idx]]
        df = df.drop(colNames[NoData[idx]], axis = 1)

    
    return df, df_actionMeta




def Str2Uint(df, df_actionMeta):
    '''Converting Strings to numbers, where N-unique minus 1 new columns will be added
    '''
    
    Convert2Float         = []
    New_List_RegType        = []
    New_List_AttribName     = []
    New_List_Simulate       = []
    for idx, attribName in enumerate(df_actionMeta.AttribNames):
        if df_actionMeta.Convert2Float[idx] == 0:
            # same data will be copied
            Convert2Float.append(df_actionMeta.Convert2Float[idx])
            New_List_RegType.append(df_actionMeta.RegType[idx])
            New_List_AttribName.append(df_actionMeta.AttribNames[idx])
            New_List_Simulate.append(df_actionMeta.Simulate[idx])
        else:
            # string data will be dropped nd replace with integer numbers
            # and removes one of the newly created columns
            oldShape    = df.shape[1]
            data        = list(set(df[attribName].tolist()))
            data        = [x for x in data if str(x) != 'nan']
            
            df          = pd.get_dummies(df, columns = [attribName])
            
            if type(data[-1]) == str:
                df          = df.drop([attribName + '_' + data[-1]], axis = 1)
            else:
                df          = df.drop([attribName + '_' + str(data[-1])], axis = 1)
                
            newShape    = df.shape[1]
            deltaShape  = newShape - oldShape + 1
            colNames    = df.columns
            for i in range(deltaShape):
                Convert2Float.append(df_actionMeta.Convert2Float[idx])
                New_List_RegType.append(df_actionMeta.RegType[idx])
                New_List_AttribName.append(colNames[oldShape - 1 + i])
                New_List_Simulate.append(df_actionMeta.Simulate[idx])

                
    df_actionMeta.RegType       = New_List_RegType
    df_actionMeta.Convert2Float = Convert2Float
    df_actionMeta.AttribNames   = New_List_AttribName
    df_actionMeta.Simulate      = New_List_Simulate


    if df.shape[1] == 0:
        sys.exit("No data to relate to each other")
        


    return df, df_actionMeta 


def get_AttribInfo(StatsDataInputFileName):
    """
    
    """
    # Initialization
    CompName            = []
    AttribName          = []
    Load                = []
    Simulate            = []
    isFloat             = []
    RegressionType      = []
    
    # checking that file exists for reading
    if os.path.isfile(StatsDataInputFileName) == False:
        print('ERROR: Required file ', StatsDataInputFileName, ' coult not be found. Program will terminate')
        return CompName, AttribName, Load, Simulate, isFloat, RegressionType, RegressionType
    
    
    # Opens file and goes through line by line
    with open(StatsDataInputFileName) as f:
        lis = [line.split() for line in f]        # create a list of lists
        for i, x in enumerate(lis):
            if i == 0:
                pass
            else:
                # getting new values
                x = x[0]
                Comp, Attrib, use, Sim, isF, Regression = x.split(";")
                # assigning new values
                CompName.append(Comp)
                AttribName.append(Attrib)
                Load.append(float(use))
                Simulate.append(Sim)
                isFloat.append(float(isF))
                RegressionType.append(Regression)
   
    return CompName, AttribName, Load, Simulate, isFloat, RegressionType
