# -*- coding: utf-8 -*-
"""
M_Stats
-------
Module for statistical applications for the data

"""

import numpy              as np
import pandas             as pd
import json
import os
import ast 
import itertools
import copy
import math
import matplotlib.pyplot      as plt
import seaborn                as sns
from sklearn.linear_model     import Lasso
from sklearn.linear_model     import LogisticRegression
from sklearn.preprocessing    import StandardScaler
from pathlib                  import Path

import Code.M_FindPos         as M_FindPos
import Code.M_MatLab          as M_MatLab
import Code.M_DataFrame       as M_DataFrame
import Code.K_Component       as K_Component

# Do not remove below import, needed for 3D plotting
from mpl_toolkits.mplot3d import Axes3D


def convert2DataFrame(Netz, StatsInputDirName, This_AttribNames, thisCompName):
    df              = []
    df_actionMeta   = []
    NumElements     = 0
    MethodNames     = [] 
    Params          = []
    
    # =======================================
    # 1. Data import
    # =======================================
    df, df_actionMeta   = M_DataFrame.make_DataFrame(Netz, StatsInputDirName, This_AttribNames, thisCompName, ApplyLoad = True)
    NumElements         = df.shape[0]

    MethodNames, Params = get_MethodsSettings(StatsInputDirName / 'StatsMethodsSettings.csv')


    # =======================================
    # 2. removing NaNs
    # =======================================
    df, df_actionMeta = M_DataFrame.drop_nan(df, df_actionMeta)


    # =======================================
    # 3. converting strings to uint8 objects
    # =====================================
    df, df_actionMeta = M_DataFrame.Str2Uint(df, df_actionMeta)

    return df, df_actionMeta, NumElements, MethodNames, Params




def gen_DataHists(Netz, CompNames = [], 
         AttribNames   = [], 
         StatsInputDirName  = 'Eingabe/Input_Settings',
         DataStatsOutput    = 'Ausgabe/Heuristic/StatsData'):


    # Initialization
    DataStatsOutput     = Path.cwd() /  DataStatsOutput
    StatsInputDirName   = Path.cwd() /  StatsInputDirName
    
    if len(CompNames) == 0:
        CompNames = ['Compressors', 'LNGs', 'Storages','PipeSegments']


    for thisCompName in CompNames:
        # =======================================
        # Setting up output summary file
        # =======================================
        if os.path.isdir(DataStatsOutput) == False:
            os.makedirs(DataStatsOutput)
    
        if len(AttribNames) == 0:
            This_AttribNames    = []
        else:
            This_AttribNames    = AttribNames    
    
        # =======================================
        # 1. Gen data frame
        # =======================================
        df, df_actionMeta, NumElements, ModelName, Param = convert2DataFrame(Netz, StatsInputDirName, This_AttribNames, thisCompName)


        # =======================================
        # 2. General info on DataFrame
        # =======================================
        print(' ')
        print(' ')
        print('===============================')
        print('Info Data Frame Sizes:')
        print('# of entries:  ', df.shape[0])
        print('# of features: ', df.shape[1])
        print(' ')
        print(' ')
        print('===============================')
        print('Number of missing values:')
        print(df.isnull().sum())
        print(' ')


        # =======================================
        # 3. Data Visualization
        # =======================================
        sns.pairplot(df)
        #plt.title(thisCompName)
        # chekcing that dir exists
        dirName = DataStatsOutput / thisCompName 
        if os.path.isdir(dirName) == False:
            os.makedirs(dirName)
        plt.savefig(dirName / 'OverView.png' )
        plt.close()
        # Histogram plots
        dirName = DataStatsOutput / thisCompName / 'HistPlots'
        if os.path.isdir(dirName) == False:
            os.makedirs(dirName)
        
        for idc, attribName in enumerate(df_actionMeta.AttribNames):
            x   = df[attribName].to_numpy()
            M   = sum(df[attribName].notnull() == True)
            N   = len(x)

            # settup up the subplot
            plt.subplot(2, 1, 1)
            plt.plot(x, 'bo')
            plt.ylabel(attribName)
            plt.title(attribName + ': ' + str(M) + '/' + str(N) + ' (' +str(round(M/N*1000)/10) + '%)' )

            plt.subplot(2, 1, 2)
            plt.hist(x)
            plt.xlabel(attribName)
            plt.ylabel('count')
            
            plt.savefig(dirName / (attribName + '.png') )
            plt.close()
            

    


def gen_StatsParam(Netz, CompNames = [], 
         AttribNames   = [], 
         DataStatsOutput    = 'Ausgabe/Heuristic/StatsData', 
         StatsInputDirName  = 'Eingabe/Input_Settings',
         SavePlots = False,
         MaxCombDepth = 2):
    """Main function to get statistical regression values, for **CompNames** (string of component name) 
    **This_AttribNames** the list of attributes to do, 
    **DataStatsOutput** dir name of output of data, 
    **StatsInputDirName**dir name where settings CSV file can be found, and 
    **SavePlots**, boolean if plots shall be created and subsequently be saved (default = False)
    **MaxCombDepth**, integer number settign the maximum number of elements per combination
         DataStatsOutput    = 'Ausgabe/InternetDaten/StatsData', 
         StatsInputDirName  = 'Eingabe/Input_Settings',
    """
    # Dir name stuff
    DataStatsOutput     = Path.cwd() /  DataStatsOutput
    StatsInputDirName   = Path.cwd() /  StatsInputDirName


    df_actionMeta  = K_Component.DF_Action_Meta()


    if len(CompNames) == 0:
        CompNames = ['Compressors', 'LNGs', 'Storages','PipeSegments']


    for thisCompName in CompNames:
        compSummaryFileName = DataStatsOutput / ('RetSummary_' + thisCompName  + '.csv')

        # =======================================
        # Setting up output summary file
        # =======================================
        if os.path.isdir(DataStatsOutput) == False:
            os.makedirs(DataStatsOutput)
        if os.path.isfile(compSummaryFileName ):
            os.remove(compSummaryFileName )
        ListColNames = addStats2File()
        # writing header to file
        f = open(compSummaryFileName,"a+")
        f.write(ListColNames[0])
        for colName in ListColNames[1:-1]:
            f.write( ";" + colName)
        f.write( ";" + ListColNames[-1])
        f.write("\r")
        f.close()
        
        # closing all figures
        plt.close("all")


        print(' ')
        print('=========================================')
        print('=========================================')
        print('Component name: ', thisCompName)


        # =========================================
        # 0 Inittial settings
        # =========================================
        if len(AttribNames) == 0:
            This_AttribNames    = []
        else:
            This_AttribNames    = AttribNames


        # =======================================
        # 1. Gen data frame
        # =======================================
        df, df_actionMeta, NumElements, ModelName, Param = convert2DataFrame(Netz, StatsInputDirName, This_AttribNames, thisCompName)
            


        # Generating combination of variables
        values          = list(range(len(df.columns)-1))
        AllCombinations = totalCombinations(values, MaxCombDepth)


        # Loop over all columns
        for idc, attribName in enumerate(df_actionMeta.AttribNames):
            print('Attribute name: ', attribName)
            thisRegType     = df_actionMeta.RegType[idc]
            for idr, thisModelName in enumerate(ModelName):
                # Getting variables values
                thisRegLabel, thisMethod = get_labels(thisModelName)


                # getting features and predicted data set
                X_Feature_All   = df.drop(attribName, axis = 1)
                y_Predited_All  = df[attribName]

                FeatureNames    = list(X_Feature_All.columns)
                if "Lasso" == thisModelName and thisRegType == 'lin':
                    print('Model: Lasso')

                    for comb in AllCombinations:
                        NumFill             = 0
                        thisFeatureNames    = []
                        doOutput            = False 

                        for c in comb:
                            thisFeatureNames.append(FeatureNames[c])
                        if len(thisFeatureNames) == 2:
                            thisFeatureNames = thisFeatureNames
                        # Selecting the features
                        X_Feature       = X_Feature_All[thisFeatureNames].copy()
    
                        # copy of predictors
                        y_Predited      = y_Predited_All.copy()
                        
                        # Determin NumFill (number of resulting filled values)
                        X_Feature_Val   = FindNotNaN(df = X_Feature)
                        y_Predited_Val  = FindNotNaN(df =  pd.DataFrame(y_Predited), invert = 1)
                        NumFill         = sum(M_MatLab.Lists_multiply(X_Feature_Val, y_Predited_Val))
    
                        # joining both data sets so that nans can be removed
                        joined_df = pd.concat([X_Feature, y_Predited], axis=1, sort=False)
    
                        # removing any nans                
                        joined_df = joined_df.dropna()
                        if joined_df.shape[0] > 3:
                            # creating index from 0 to N
                            joined_df  = joined_df.reset_index(drop = True)
        
                            # ripping stuff appart again
                            X_Feature   = joined_df.drop(attribName, axis = 1)
                            y_Predited  = joined_df[attribName]
                            X_Feature4Plot  = X_Feature.copy()
        
                            # And use scaling factors later on as well (Z-transformation)
                            sc          = StandardScaler()
                            X_Feature   = sc.fit_transform(X_Feature)   # to training and testing dataset
         #                   X_Feature       = X_Feature.values
                            SC_Mean     = sc.mean_.tolist()
                            SC_Scale    = sc.scale_.tolist()
        
        
                            # getting pos for regression name
                            pos = M_FindPos.find_pos_StringInList(thisModelName, ModelName)
                            idr = pos[0]
        
                            listIntercepts  = []
                            listCoef        = []
        
                            # Linear Regreswsion 
                            N               = len(y_Predited)
                            N_Data          = sum(X_Feature_Val) + NumFill 
                            if N_Data > NumElements:
                                N_Data = NumElements
                        else:
                            N = 0
                        # check that there is enough data
                        if N > 3:
                            if len(Param[idr]) == 0:
                                Reg_Instance  = Lasso()
                            else:
                                Reg_Instance  = Lasso(**Param[idr])
    
                            # loop for each data point
                            for idt in range(N):
                                # preparation of data
                                X_train = np.delete(X_Feature, idt, 0)
                                y_train = y_Predited.drop(idt)
                                X_test  = X_Feature[idt][:].reshape(1, -1)
        
        
                                # carry out linear Regression
                                Reg_Instance.fit(X_train, y_train)
                                pred_Vals = Reg_Instance.predict(X_test)
        
                                # calc sum abs diff true vs. estimated
                                listIntercepts.append(Reg_Instance.intercept_)
                                listCoef.append(Reg_Instance.coef_)
                            # determine Mean sum Abs Diff
                            meanIntercept   = sum(listIntercepts) / N
                            meanCoef        = sum(listCoef) / N
    
                            # determing value after fit
                            Reg_Instance.coef_ 		= meanCoef
                            Reg_Instance.intercept_ = meanIntercept
                            pred_Vals               = Reg_Instance.predict(X_Feature)
                            # re output
                            doOutput                = sum(meanCoef) != 0 

                        if doOutput == True:
                            helper_DoOutput(compSummaryFileName, SavePlots, thisCompName,
                                            NumElements, attribName, thisFeatureNames, 
                                            N, comb, thisModelName, X_Feature4Plot, 
                                            y_Predited, pred_Vals, meanCoef, 
                                            SC_Mean, SC_Scale, meanIntercept, 
                                            DataStatsOutput, Reg_Instance, 
                                            thisRegLabel, N_Data)
    

                elif "LogisticReg" == thisModelName and thisRegType == 'log':
                    print('Model: LogisticReg')
                    # https://www.youtube.com/watch?v=1nWFHa6K23w
                    # https://towardsdatascience.com/logistic-regression-using-python-sklearn-numpy-mnist-handwriting-recognition-matplotlib-a6b31e2b166a
                    # sigmoid( dot([val1, val2], lr.coef_) + lr.intercept_ )

                    for comb in AllCombinations:
                        NumFill             = 0
                        thisFeatureNames    = []
                        doOutput            = False 

                        for c in comb:
                            thisFeatureNames.append(FeatureNames[c])
                        # Selecting the features
                        X_Feature   = X_Feature_All[thisFeatureNames].copy()
    
                        # copy of predictors
                        y_Predited  = y_Predited_All.copy()
    
                        # Determin NumFill (number of resulting filled values)
                        X_Feature_Val   = FindNotNaN(df = X_Feature)
                        y_Predited_NaN  = FindNotNaN(df = pd.DataFrame(y_Predited), invert = 1)
                        NumFill         = sum(M_MatLab.Lists_multiply(X_Feature_Val, y_Predited_NaN))

                        # joining both data sets so that nans can be removed
                        joined_df = pd.concat([X_Feature, y_Predited], axis=1, sort=False)
    
                        # removing any nans                
                        joined_df = joined_df.dropna()
                        if joined_df.shape[0] > 3:
                            # creating index from 0 to N
                            joined_df       = joined_df.reset_index(drop = True)
        
                            # ripping stuff appart again
                            X_Feature       = joined_df.drop(attribName, axis = 1)
                            y_Predited      = joined_df[attribName]
                            X_Feature4Plot  = X_Feature.copy()
        
                            # And use scaling factors later on as well (Z-transformation)
                            sc              = StandardScaler()
                            X_Feature       = sc.fit_transform(X_Feature)   # to training and testing dataset
         #                   X_Feature       = X_Feature.values
                            SC_Mean         = sc.mean_.tolist()
                            SC_Scale        = sc.scale_.tolist()
        
        
                            # getting pos for regression name
                            pos             = M_FindPos.find_pos_StringInList(thisModelName, ModelName)
                            idr             = pos[0]
        
                            listIntercepts  = []
                            listCoef        = []
        
                            # Linear Regreswsion 
                            N               = len(y_Predited)
                            N_Data          = sum(X_Feature_Val) + NumFill 
                            if N_Data > NumElements:
                                N_Data = NumElements
                        else:
                            N = 0
                        # check that there is enough data
                        if N > 3:
                            if len(Param[idr]) == 0:
                                Reg_Instance  = LogisticRegression()
                            else:
                                Reg_Instance  = LogisticRegression(**Param[idr])
    
                            # loop for each data point
                            for idt in range(N):
                                # preparation of data
                                y_train = y_Predited.drop(idt)
                                
                                #check that there are more than one unique value in y_train
                                if len(list(set(y_train.values.tolist()))) >1: 
                                    X_train = np.delete(X_Feature, idt, 0)
                                    X_test  = X_Feature[idt][:].reshape(1, -1)
            
            
                                    # carry out linear Regression
                                    Reg_Instance.fit(X_train, y_train)
                                    pred_Vals = Reg_Instance.predict(X_test)
            
                                    # calc sum abs diff true vs. estimated
                                    listIntercepts.append(Reg_Instance.intercept_)
                                    listCoef.append(Reg_Instance.coef_)
                            
                            # determine Mean sum Abs Diff
                            N               = len(listIntercepts)
                            if N > 1:
                                meanIntercept   = sum(listIntercepts)[0] / N
                                meanCoef        = sum(listCoef) / N
        
                                # determing value after fit
                                Reg_Instance.coef_ 		= meanCoef
                                Reg_Instance.intercept_ = meanIntercept
                                pred_Vals               = Reg_Instance.predict(X_Feature)
                                # re output
                                doOutput                = sum(meanCoef[0]) != 0 

                        if doOutput == True:
                            helper_DoOutput(compSummaryFileName, SavePlots, thisCompName,
                                            NumElements, attribName, thisFeatureNames, 
                                            N, comb, thisModelName, X_Feature4Plot, 
                                            y_Predited, pred_Vals, meanCoef[0], 
                                            SC_Mean, SC_Scale, meanIntercept, 
                                            DataStatsOutput, Reg_Instance, 
                                            thisRegLabel, N_Data)

                    # Fundamental states
                elif thisRegType == 'lin' and not  "LogisticReg" == thisModelName:
                    print('Model: ', thisModelName)
                    doOutput            = False 
                    NumFill             = NumElements
                    thisFeatureNames    = [attribName]
                    y_Predited          = y_Predited_All.copy()
                    y_Predited          = y_Predited.dropna()
                    # creating index from 0 to N
                    y_Predited          = y_Predited.reset_index(drop = True)
                    listIntercepts      = []
                    SC_Mean             = [0]
                    SC_Scale            = [0]
                    Reg_Instance        = Lasso()
                    N                   = len(y_Predited)
                    if N > 4:
                        # re output
                        doOutput = True 
                        # Stats estimation
                        for idt in range(N):
                            # preparation of data
                            y_train = y_Predited.drop(idt).tolist()
    
                            # carry out stats 
                            Value, RetError = get_Value(y_train, thisMethod, ErrorMethod = 'STD')
    
                            # calc sum abs diff true vs. estimated
                            listIntercepts.append(Value[0])
                        
                        # determine Mean sum Abs Diff
                        meanIntercept   = sum(listIntercepts) / N
                        meanCoef        = np.array([0])
                        Reg_Instance.coef_ 		= meanCoef
                        Reg_Instance.intercept_ = meanIntercept
                        pred_Vals       = [meanIntercept] * N 
                        NumFill         = NumElements - N

                    if doOutput == True:
                        vector = np.zeros(len(y_Predited))
                        for idv, val in enumerate(vector ):
                            vector[idv] = idv
                        dd = pd.DataFrame(vector, columns = ['first'])
                        
                        helper_DoOutput(compSummaryFileName, SavePlots, thisCompName,
                                        NumElements, attribName, thisFeatureNames, 
                                        N, [0], thisModelName, dd,
                                        y_Predited, pred_Vals, meanCoef, 
                                        SC_Mean, SC_Scale, meanIntercept, 
                                        DataStatsOutput, Reg_Instance, 
                                        thisRegLabel, NumElements)
#                else:
#                    print('WARNING: For Attribute "', attribName,'" no model simulated')




#                y_Predited_All  = y_Predited.reset_index(drop = True)
    return 1



def pop_Attribs(Netz, CompNames = [], SimSettings = []):
    """Generation of attribute values from otehr attributes
    """
    
    if len(CompNames) == 0:
        CompNames = ['Compressors', 'LNGs', 'Storages', 'PipeSegments']

    
    for idc, compName in enumerate(CompNames):
        
        
        # loop going through each attrib in SimAttribSettings
        for ids in range(len(SimSettings)):
            compName = SimSettings[ids]['CompName']
            # checking that component exists.
            NumElements     = len(Netz.__dict__[compName])
            ReplaceType     = SimSettings[ids]['ReplaceType']
            if NumElements > 0 and isinstance(ReplaceType, str):
                # getting setting values from intput file
                AttribName      = SimSettings[ids]['AttribName']
                ModelName       = SimSettings[ids]['ModelName']
                FeatureNames    = json.loads(str(SimSettings[ids]['FeatureNames']))
                ReplaceType     = SimSettings[ids]['ReplaceType']
                ModelOutputParam= json.loads(SimSettings[ids]['ModelParam'])
                R_2_adj         = SimSettings[ids]['R_2_adj']
                
                # Checking that all requested data is present
                AllDataPres = True
                for attrib in FeatureNames:
                    if attrib not in  Netz.__dict__[compName][0].param.keys():
                        AllDataPres  = False
                if AllDataPres == False:
                    print('Not all data given for attribute "{}" in component "{}".'.format(AttribName, compName))
                else:
                    
                    val = []
                    
                    ## This mjight break as new MatLab.get_median call
                    if ModelName == 'Median':
                        DataIn  = Netz.get_Attrib(compName, FeatureNames[0])
                        val     = M_MatLab.get_median(DataIn)[0]
                        val     = [val] * NumElements
                        
                    elif ModelName == 'Mean':
                        DataIn  = Netz.get_Attrib(compName, FeatureNames[0])
                        val     = M_MatLab.get_mean(DataIn)[0]
                        val     = [val] * NumElements
                        
                    elif ModelName == 'Min':
                        DataIn  = Netz.get_Attrib(compName, FeatureNames[0])
                        val     = M_MatLab.get_min(DataIn)[0]
                        val     = [val] * NumElements
                        
                    elif ModelName == 'Max':
                        DataIn  = Netz.get_Attrib(compName, FeatureNames[0])
                        val     = M_MatLab.get_max(DataIn)[0]
                        val     = [val] * NumElements
                        
                    elif ModelName == 'Lasso':
                        # getting parameters
                        SC_Mean     = ModelOutputParam['SC_Mean']
                        SC_Scale    = ModelOutputParam['SC_Scale']
                        Intercept   = ModelOutputParam['Intercept']
                        Coef        = ModelOutputParam['Coef']
                        
        
                        # creation of a dataframe
                        df      = pd.DataFrame()
                        # creating column of intercept
                        df['Result'] = [Intercept] * NumElements
        
                        for idn, name in enumerate(FeatureNames):
                            val = Netz.get_Attrib(compName, name)
                            val = M_MatLab.Lists_subtract(val, [SC_Mean[idn]] * NumElements)
                            val = M_MatLab.Lists_devide(val,  [SC_Scale[idn]] * NumElements)
                            val = M_MatLab.Lists_multiply(val,  [Coef[idn]] * NumElements)
                            wert = df['Result']
                            df['Result'] = M_MatLab.Lists_addition(wert, val)
                        val = df['Result'].tolist()
                    
                    
                    elif ModelName == 'Const':
                        val = ModelOutputParam['Const']
                        val = [val] * NumElements
                        
                    else:
                        val = []
                    
                    if len(val) > 0:
                        # assigning data
                        if ReplaceType.lower() == 'all':
                            for idx in range(NumElements):
                                if val[idx] is not None and np.isnan(val[idx]) == False:
                                    Netz.__dict__[compName][idx].param.update({AttribName: val[idx]})
                                    Netz.__dict__[compName][idx].method.update({AttribName: ModelName})
                                    Netz.__dict__[compName][idx].uncertainty.update({AttribName: R_2_adj})
                                
                        elif ReplaceType.lower() == 'fill':
                            for idx in range(NumElements):
                                if Netz.__dict__[compName][idx].param[AttribName] == [] or Netz.__dict__[compName][idx].param[AttribName] == None:
                                    if val[idx] is not None and np.isnan(val[idx]) == False:
                                        Netz.__dict__[compName][idx].param.update({AttribName: val[idx]})
                                        Netz.__dict__[compName][idx].method.update({AttribName: ModelName})
                                        Netz.__dict__[compName][idx].uncertainty.update({AttribName: R_2_adj})
        
    return Netz





def addStats2File(FileName = [], CompName = [], NumElements = [], AttribName = [], FeatureNames = [], NumFeatures = [], NumSamples = [], BIC = [], ModelName = [], MeanAbsError = [], ModelParam = [], R_2 = [], R_2_adj = [], NumFill = [], PlotLink = []):
    """Writing Stats information into CSV file: **FileName**, **CompName**, **NumElements**, **AttribName**, **FeatureNames**, **NumFeatures**, **NumSamples**, **BIC**, 
    **ModelName**, **MeanAbsError**, **ModelParam**, **R_2**, **R_2_adj**, **NumFill**
    """
    
    # Order within file:
    # **CompName, AttribName, NumElements, ModelName, NumFeatures, FeatureNames, NumSamples, BIC, MeanAbsError, R_2, R_2_adj, ModelParam
    
    if FileName != []:
        try:
            f = open(FileName, "a+")
            f.write(CompName + ";" + AttribName + ";" + str(NumElements)+  ";" + ModelName + ";" + str(NumFeatures) + ";" )
            f.write(json.dumps(FeatureNames))
            f.write(";")
            f.write("\"=HYPERLINK(\"\"" + PlotLink + "\"\")\"")
            f.write(";" + str(NumSamples) + ";" + str(NumFill) + ";" + str(BIC) + ";" + str(MeanAbsError) + ";" + str(R_2) + ";" + str(R_2_adj) + ";;")
            f.write(json.dumps(ModelParam) )
            f.write("\r")
        except:
            pass
        try:
            f.close()
        except:
            pass

    return ['CompName', 'AttribName', 'NumElements', 'ModelName', 'NumFeatures', 'FeatureNames', 'Plots', 'NumSamples', 'NumFill', 'BIC', 'MeanAbsError', 'R_2', 'R_2_adj', 'ReplaceType','ModelParam']




def totalCombinations(values, maxCombDepth = 2):
    """Generation of total combinations of indecees given through **values**, 
    where max combination depth is given through **maxCombDepth**.
    """
    string =''
    for val in values:
        string = string + str(val)
        
    output = []
    for idx in range(1, len(values)+1):
        newValues = list(itertools.combinations(values, idx))
        for val in newValues:
            if len(val)<=maxCombDepth:
                output.append(val)
            
    return output
    




def plottingLinear(X_Feature, y_Predited, statsVal, FeatureNames, thisCompName, attribName, PlotOn, DataStatsOutput, rsq, ModelName):
    """Plotting function of linear data
    """
    if PlotOn:
        if X_Feature.shape[1] == 1:
            X = X_Feature.tolist()
            Y = y_Predited.tolist()
            plt.figure()
            plt.scatter(X, Y)
            # making model data
            x = np.linspace(min(X ), max(X), 2)
            y = [statsVal, statsVal]
            # platting model data
            plt.plot(x, y, 'r')            
            # adding xlabel and title 
            #plt.xlabel(FeatureNames[0])
            plt.ylabel(attribName)
            plt.title('{}: value: {:.2E},  R^2:{:.2f}'.format(ModelName, statsVal, rsq))
        elif X_Feature.shape[1] == 2:
            pass
        else:
            pass
        
        plt.savefig(DataStatsOutput + '/' + thisCompName + '/' + attribName + '_' + ModelName + '.png' )





def plottingStats(SavePlots, X_Feature, y_Predited, FeatureNames, thisCompName, attribName, DataStatsOutput, LinReg, rsq, ModelName, param):
    """Plotting of data, linear and 
    """
    
    
    PlotName        = None
    PlotName_Out    = None
    
    if SavePlots:
        # checking that dir exist
        dirName = DataStatsOutput / thisCompName / ('AttribRelationPlots') /attribName
        if os.path.isdir(dirName) == False:
            os.makedirs(dirName)
            

        
        
        # plotting data    
        if X_Feature.shape[1] == 1 and not 'Logistic' in ModelName:
            plt.figure()
            #sns.regplot(x = X_Feature, y = y_Predited)
            plt.scatter(X_Feature.values, y_Predited.tolist())
            plt.xlabel(FeatureNames[0])
            plt.ylabel(attribName)
            plt.title ('{}, R^2_a:{:.2f}'.format(ModelName, rsq) )
            xmin = min(X_Feature.values)[0]
            xmax = max(X_Feature.values)[0]
            ymin = xmin - param['SC_Mean'][0]
            ymax = xmax - param['SC_Mean'][0]
            ymin = ymin / param['SC_Scale'][0]
            ymax = ymax / param['SC_Scale'][0]
            # Normal mean, median, min, max
            if param['Coef'][0] != 0:
                ymin = ymin * param['Coef'][0]
                ymax = ymax * param['Coef'][0]
                ymin = ymin + param['Intercept']
                ymax = ymax + param['Intercept']
            else:
                ymin = param['Intercept']
                ymax = param['Intercept']
                
            plt.plot([xmin, xmax], [ymin, ymax])
            
            PlotName = dirName / (attribName + '_' + ModelName + '_' + FeatureNames[0] + '.png')
            PlotName_Out = '../StatsData/' +  thisCompName  + '/AttribRelationPlots/' + attribName + '/' + (attribName + '_' + ModelName + '_' + FeatureNames[0] + '.png')
    
        elif X_Feature.shape[1] == 2 and not 'Logistic' in ModelName:
            
            # converting input to dataframe if required
            if type(X_Feature) == np.ndarray:
                X_Feature = pd.DataFrame(X_Feature)
                
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
            ax.scatter(X_Feature.iloc[:,0].values , X_Feature.iloc[:, 1].values, y_Predited.values, s = 50, alpha = 0.6, edgecolors = 'w')
            
            x = np.linspace(min(X_Feature.iloc[:,0].values ), max(X_Feature.iloc[:,0].values ), 100)
            y = np.linspace(min(X_Feature.iloc[:, 1].values), max(X_Feature.iloc[:, 1].values), 100)
            X, Y = np.meshgrid(x, y)
            X, Z = np.meshgrid(x, y)
            for idx, ix in enumerate(x):
                for idy, iy in enumerate(y):
                    Z[idx][idy] = LinReg.coef_[0] * ix + LinReg.coef_[1] * iy + LinReg.intercept_
            ax.contour3D(X, Y, Z, 50, cmap='binary')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel(attribName)
            plt.title('{}: R^2_a:{:.2f}'.format(ModelName, rsq))
            
            PlotName = dirName / (attribName + '_' + ModelName + '_' + FeatureNames[0] + '_' + FeatureNames[1] +'.png') 
            PlotName_Out = '../StatsData/' +  thisCompName  + '/AttribRelationPlots/' + attribName + '/' + (attribName + '_' + ModelName + '_' + FeatureNames[0] + '_' + FeatureNames[1] +'.png') 
        elif X_Feature.shape[1] == 1 and 'Logistic' in ModelName:
            plt.figure()
            #sns.regplot(x = X_Feature, y = y_Predited)
            plt.scatter(X_Feature.values, y_Predited.tolist())
            plt.xlabel(FeatureNames[0])
            plt.ylabel(attribName)
            plt.title ('{}, R^2_a:{:.2f}'.format(ModelName, rsq) )
            PlotName = dirName / (attribName + '_' + ModelName + '_' + FeatureNames[0] + '.png')
            PlotName_Out = '../StatsData/' +  thisCompName  + '/AttribRelationPlots/' + attribName + '/' + (attribName + '_' + ModelName + '_' + FeatureNames[0] + '.png')

#            #sns.regplot(x = X_Feature, y = y_Predited)
#            plt.scatter(X_Feature.values, y_Predited.tolist())
#            plt.xlabel(FeatureNames[0])
#            plt.ylabel(thisCompName)
#            plt.title ('{}, R^2_a:{:.2f}'.format(ModelName, rsq) )
#            xmin = min(X_Feature.values)[0]
#            xmax = max(X_Feature.values)[0]
#            X = np.linspace(xmin, xmax, 100)
#            Y = np.linspace(xmin, xmax, 100)
#
#            for y in Y:
#                y = y - param['SC_Mean'][0]
#                y = y / param['SC_Scale'][0]
#                # Normal mean, median, min, max
#                if param['Coef'][0] != 0:
#                    y = y * param['Coef'][0]
#                    y = y + param['Intercept']
#                else:
#                    ymin = param['Intercept']
#                
#            plt.plot(X, Y)
            
            
            
        elif X_Feature.shape[1] == 2 and 'Logistic' in ModelName:            
            # converting input to dataframe if required
            if type(X_Feature) == np.ndarray:
                X_Feature = pd.DataFrame(X_Feature)
                
            fig = plt.figure()
            PlotName     = dirName / (attribName + '_' + ModelName + '_' + FeatureNames[0] + '_' + FeatureNames[1] +'.png') 
            PlotName_Out = '../StatsData/' +  thisCompName  + '/AttribRelationPlots/' + attribName + '/' + (attribName + '_' + ModelName + '_' + FeatureNames[0] + '_' + FeatureNames[1] +'.png') 

#            ax  = fig.add_subplot(111, projection='3d')
#            ax.scatter(X_Feature.iloc[:,0].values , X_Feature.iloc[:, 1].values, y_Predited.values, s = 50, alpha = 0.6, edgecolors = 'w')
#            
#            x = np.linspace(min(X_Feature.iloc[:,0].values ), max(X_Feature.iloc[:,0].values ), 100)
#            y = np.linspace(min(X_Feature.iloc[:, 1].values), max(X_Feature.iloc[:, 1].values), 100)
##            X, Y = np.meshgrid(x, y)
##            X, Z = np.meshgrid(x, y)
##            for idx, ix in enumerate(x):
##                for idy, iy in enumerate(y):
##                    Z[idx][idy] = LinReg.coef_[0] * ix + LinReg.coef_[1] * iy + LinReg.intercept_
#            ax.contour3D(X, Y, Z, 50, cmap='binary')
#            ax.set_xlabel('x')
#            ax.set_ylabel('y')
#            ax.set_zlabel(attribName)
#            plt.title('{}: R^2_a:{:.2f}'.format(ModelName, rsq))
            


        if PlotName is not None:
            plt.grid(True)
            plt.savefig(PlotName)
            plt.close()
    
    return PlotName_Out
    



def get_MethodsSettings(StatsMethodsFileName):
    """Returns the method settings from file **StatsMethodsFileName** (StatsMethodsSettings.CSV). Return are the MethodNames and the Params."""
    # Initialization
    MethodNames     = []
    Params           = []
    
    # checking that file exists for reading
    if os.path.isfile(StatsMethodsFileName) == False:
        print('ERROR: Required file ', StatsMethodsFileName, ' coult not be found. Program will terminate.')
        return MethodNames, Params
    
    
    # Opens file and goes through line by line
    with open(StatsMethodsFileName) as f:
        lis = [line.split() for line in f]        # create a list of lists
        for i, x in enumerate(lis):
            if i == 0:
                pass
            else:
                # getting new values
                x = x[0]

                # checking for empty line at end of file, if so, then terminate
                if len(x) < 2:
                    return MethodNames, Params
                
                t1, t2, t3 = x.split(";")
                if t3 == '1':
                    # assigning new values
                    MethodNames.append(t1)
                    if len(t2)>0:
                        Params.append(ast.literal_eval(t2))
                    else:
                        Params.append([])
   
    return MethodNames, Params


    

def get_labels(thisRegName):
    thisRegLabel = []
    thisMethod   = []
    if "Median" == thisRegName:
        thisRegLabel    = 'Median (L1O)'
        thisMethod      = 'median'
    elif "Mean" == thisRegName:
        thisRegLabel    = 'Mean (L1O)'
        thisMethod      = 'mean'
    elif "Min" == thisRegName:
        thisRegLabel    = 'Min (L1O)'
        thisMethod      = 'min'
    elif "Max" == thisRegName:
        thisRegLabel    = 'Max (L1O)'
        thisMethod      = 'max'
    elif "Lasso" == thisRegName:
        thisRegLabel    = 'Lasso (L1O)'
        thisMethod      = 'Lasso'
    elif "LogisticReg" == thisRegName:
        thisRegLabel    = 'Logistic (L1O)'
        thisMethod      = 'Logistic'
    else:
        print('ERROr: SampleStats.Main: Code not written: 3')
        
    return thisRegLabel, thisMethod




def helper_DoOutput(compSummaryFileName, SavePlots, thisCompName,NumElements, attribName, 
             thisFeatureNames, N, comb, thisRegName, X_Feature4Plot, y_Predited, 
             pred_Vals, meanCoef, SC_Mean, SC_Scale, meanIntercept, DataStatsOutput, 
             Reg_Instance, thisRegLabel, NumFill):
    sumAbsDiff = []
    squareAbsDiff = []
    # determing Error values
    for idt, y in enumerate(y_Predited):
        sumAbsDiff.append(abs(y - pred_Vals[idt]))
        squareAbsDiff.append((y - pred_Vals[idt]) * (y - pred_Vals[idt]))
    
    meansquareAbsDiff   = sum(squareAbsDiff) / N
    meanSumAbsDiff      = sum(sumAbsDiff) / N
    R_2                 = r_squared(y_Predited, pred_Vals)
    R_2_adj             = r_squared_adjusted(y_Predited, pred_Vals, len(meanCoef))
    
    
    BIC             = np.log(N) * len(comb) + N * np.log(meansquareAbsDiff)
    # Model Parameter
    param = {}
    param.update({'SC_Mean':SC_Mean})
    param.update({'SC_Scale':SC_Scale})
    param.update({'Intercept': meanIntercept})
    param.update({'Coef': meanCoef.tolist()})
    # plotting data
    PlotLink = plottingStats(SavePlots, X_Feature4Plot, y_Predited, thisFeatureNames, thisCompName, attribName, DataStatsOutput, Reg_Instance, R_2_adj, thisRegLabel, param)
    # Writing summary to file: 
    addStats2File(compSummaryFileName, thisCompName, NumElements, attribName, thisFeatureNames, len(comb), N, BIC, thisRegName, meanSumAbsDiff, param, R_2, R_2_adj, NumFill, PlotLink)
    




def FindNotNaN(df , invert = 0):
    X_Feature_Val = []
    colNames = df.columns
    
    wert =  df[colNames[0]].isnull()
    # first run through
    for idy in range(len(wert)):
        if wert[idy] == True:
            X_Feature_Val.append(0)
        else:
            X_Feature_Val.append(1)
    
    # Any subsequent run through
    for idx in range(1, df.shape[1]):
        # getting next data set
        wert =  df[colNames[idx]].isnull()
        
        for idy in range(len(wert)):
            # check if 
            if wert[idy] == False and X_Feature_Val[idy] == 1:
                X_Feature_Val[idy] = 1
            else:
                X_Feature_Val[idy] = 0
            
        
    if invert == 1:
        for idy in range(len(wert)):
            if X_Feature_Val[idy] == 1:
                X_Feature_Val[idy] = 0
            else:
                X_Feature_Val[idy] = 1
            
            
    
    return X_Feature_Val 







def get_Value(DataIn, CalcMethod, ErrorMethod = 'STD'):
    ''' 
    '''
    RetValue = []
    RetError = []
    DataType = []
    if len(DataIn) == 0:
        return RetValue, RetError
        
    # Cleaning data
    Data = [x for x in copy.deepcopy(DataIn) if x != None]
    # check that at least three valus gievn
    if len(Data) <= 3:
        return RetValue, RetError
    
    # Further cleaning of data
    if isinstance(DataIn, list):
        if isinstance(Data[0], float):
            Data = [x for x in copy.deepcopy(Data) if ~np.isnan(x)]
            Data = [x for x in copy.deepcopy(Data) if ~np.isinf(x)]
            DataType = 'float'
        elif isinstance(Data[0], str):
            Data = [x for x in copy.deepcopy(Data) if x != 'nan']
            Data = [x for x in copy.deepcopy(Data) if x != 'None']
            DataType = 'str'
        elif isinstance(Data[0], int):
            Data = [x for x in copy.deepcopy(Data) if x != 'nan']
            Data = [x for x in copy.deepcopy(Data) if x != 'None']
            DataType = 'int'
        else:
            Data = []
            DataType = 'float'
            for dd in Data:
                if isinstance(dd, float):
                    Data.append(dd)
			
    elif isinstance(DataIn, float):
        Data = [x for x in copy.deepcopy(Data) if ~np.isnan(x)]
        Data = [x for x in copy.deepcopy(Data) if ~np.isinf(x)]
		
    elif isinstance(DataIn, str):
        pass
    else:
        print('M_Stats.get_Value: code not written yet 56.')
	
    # simulation
    if len(Data)> 3 :
        if CalcMethod == 'median':
            if DataType == 'float' or DataType == 'int':
                sortedLst 	= sorted(Data)
                lstLen 		= len(Data)
                index 		= (lstLen - 1) // 2
                val 		= sortedLst[index]
                if ErrorMethod == 'STD':
                    error 		= std(Data, val)
                elif ErrorMethod == 'OOB':
                    error 		= OOB(Data, CalcMethod)
                elif ErrorMethod == 'LOOCV':
                    error 		= LOOCV(Data, CalcMethod)
            else:
                sortedLst 	= sorted(Data)
                lstLen 		= len(Data)
                index 		= (lstLen - 1) // 2
                val 		= sortedLst[index]
					
                if ErrorMethod == 'STD':
                    error 		= std(Data, val)
                elif ErrorMethod == 'OOB':
                    error 		= OOB(Data, CalcMethod)
                elif ErrorMethod == 'LOOCV':
                    error 		= LOOCV(Data, CalcMethod)
        elif CalcMethod == 'mean':
            if DataType == 'float' or DataType == 'int':
                val, _ 		= M_MatLab.get_mean(Data)
                if ErrorMethod == 'STD':
                    error 		= std(Data, val)
                elif ErrorMethod == 'OOB':
                    error 		= OOB(Data, CalcMethod)
                elif ErrorMethod == 'LOOCV':
                    error 		= LOOCV(Data, CalcMethod)
            else:
                val = []
                error = []
                print('M_Stats.get_Value: Calc Method mean for string does not make sense.')

        elif CalcMethod == 'min':
            if DataType == 'float' or DataType == 'int':
                val, _ 	= M_MatLab.get_min(Data)
                if ErrorMethod == 'STD':
                    error 		= std(Data, val)
                elif ErrorMethod == 'OOB':
                    error 		= OOB(Data, CalcMethod)
                elif ErrorMethod == 'LOOCV':
                    error 		= LOOCV(Data, CalcMethod)
            else:
                val = []
                error = []
                print('M_Stats.get_Value: Calc Method min for string does not make sense.')

        elif CalcMethod == 'max':
            if DataType == 'float' or DataType == 'int':
                val, _ 		= M_MatLab.get_max(Data)
                if ErrorMethod == 'STD':
                    error 		= std(Data, val)
                elif ErrorMethod == 'OOB':
                    error 		= OOB(Data, CalcMethod)
                elif ErrorMethod == 'LOOCV':
                    error 		= LOOCV(Data, CalcMethod)
            else:
                val = []
                error = []
                print('M_Stats.get_Value: Calc Method max for string does not make sense.')
		
        else:
            val = []
            error = []
#            print('M_Stats.get_Value: code not written yet 34.')
    else:
        return RetValue, RetError
	    
    # Expanding the return vectors
    for idx in range(len(DataIn)):
	    RetValue.append(val)
	    RetError.append(error)
	
    # return
    return RetValue, RetError
	

def LOOCV(xi, ModName):
    """Returns the Leave-one-out-Cross-Validation mean difference between measured 
    and estimated value **xi**, where **ModName** specifies the model method.
	"""
    
    sumDiffVals = 0
    retVal      = -999
    
    if isinstance(xi[0], str):
        N = len(xi)
        for pos in range(len(xi)-1):
            # reducing by one element
            SubData = xi.copy()
            SubData.pop(pos)
            # predicted
            thisPredicted       = xi[pos]
            thisEstimated, _    = get_Value(SubData, ModName)
            if thisEstimated[0] != thisPredicted:
                sumDiffVals         = sumDiffVals + 1
        retVal = sumDiffVals / N

        
    else:
        N = len(xi)
        for pos in range(len(xi)-1):
            print('pos', pos)
            # reducing by one element
            SubData = xi.copy()
            SubData.pop(pos)
            # predicted
            thisPredicted       = xi[pos]
            thisEstimated, _    = get_Value(SubData, ModName)
            sumDiffVals         = sumDiffVals + abs(thisEstimated[0] - thisPredicted)
        retVal = sumDiffVals / N
        
    return retVal
    
    


def OOB(xi, ModName):
    """Returns the Out-of-Bag mean difference between measured and estimated value **xi**, where **ModName** specifies the model name.
	"""
    
    sumDiffVals = 0
    retVal      = -999
    
    if isinstance(xi[0], str):
        N = len(xi)
        for pos in range(len(xi)-1):
            # reducing by one element
            SubData = xi.copy()
            SubData.pop(pos)
            # predicted
            thisPredicted       = xi[pos]
            thisEstimated, _    = get_Value(SubData, ModName)
            if thisEstimated[0] != thisPredicted:
                sumDiffVals         = sumDiffVals + 1
        retVal = sumDiffVals / N

        
    else:
        N = len(xi)
        for pos in range(len(xi)-1):
            # reducing by one element
            SubData = xi.copy()
            SubData.pop(pos)
            # predicted
            thisPredicted       = xi[pos]
            thisEstimated, _    = get_Value(SubData, ModName)
            sumDiffVals         = sumDiffVals + abs(thisEstimated[0] - thisPredicted)
        retVal = sumDiffVals / N
        
    return retVal
    
    
    
	
def std(xi, xbar):
    """Returns the STD like value for data **xi**, where expected value given through **xbar**.
	"""
    
    top     = 0
    bottom  = len(xi) - 1
    if bottom == 0:
        return -888
    
    if isinstance(xi[0], str):
        for xx in xi:
            if xx != xbar:
                top = top + 1
        
    else:
        for xx in xi:
            top = top + (xx - xbar) * (xx - xbar) 
	
    return math.sqrt(top / bottom)




def stdOfStr(Data, val):
    """Determin the STD of a list of strings ?????
    """
    RetError = []
    DataConv = []
    
    
    uniqueData = list(set(Data))
    uniqueValue = []
    for ii in range(len(uniqueData)):
        uniqueValue.append(ii)
        if val == uniqueData[ii]:
            valNum = ii
    
    
    for dd in Data[1:]:
        pos = M_FindPos.find_pos_StringInList(dd, uniqueData )
        DataConv.append(uniqueValue[pos[0]])
        
    RetError = std( DataConv, valNum)
    return RetError
        
    


def r_squared(data, pred):
    """Returns the R^2, for input **data**, **pred**
    """
    SS_tot  = []
    SS_res  = []
    N       = len(data )
    mean_obs = sum(data) / N
    
    for idx in range(len(data)):
        SS_tot.append((data[idx] - mean_obs) * (data[idx] - mean_obs))
        SS_res.append((data[idx] - pred[idx]) * (data[idx] - pred[idx]))
        
    SS_res = sum(SS_res)
    SS_tot = sum(SS_tot)
    R2 = 1 - SS_res / SS_tot
    
    return R2

    
    
    
def r_squared_adjusted(data, pred, p):
    """Returns the adjusted R^2, for input **data**, **pred**, **p** 
    (the number of explanatory variables, not including the constant term)
    """
    R2 = r_squared(data, pred)
    R2adj = 1 - (1 - R2) * (len(data) - 1) / (len(data) - p - 1)
    
    return R2adj



