#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 15:21:10 2019

@author: apluta
"""


import Code.M_Matching        as M_Matching
import Code.M_FindPos         as M_FindPos
import Code.M_Helfer          as M_Helfer
import itertools              as itertools
import numpy                  as np
import networkx               as NX
#import Code.M_Netze           as M_Netze

import copy



def join(scenaName, CompNames, data_sources):
    """Main function of joining components **CompNames** from the following data sources as combined in the dict **data_sources**.
    Currently only one scenario implemented **scenaName** ('Scen_1').
    """
    
    
        
        
    if scenaName == 'Scen_1':
        # check that Netz_InterNet can be used as starting network.
        if 'InterNet' not in data_sources:
            print('Error: M_Matching.join: Internet Data set required as part of the data sources. Function will return empty')
            return []
        
        DasNetz          = data_sources['InterNet']

        if CompNames    == []:
            CompNames = DasNetz.CompLabels()
        
        ### LNGs
        if 'LNGs' in CompNames:
#           Netz_EntsoG
            if 'EntsoG' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['EntsoG'], compName = 'LNGs', threshold = 10, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 50), 
                        lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                        ))
                DasNetz.join_comp(data_sources['EntsoG'], 'LNGs', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            
            
#           Netz_GIE
            if 'GIE' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GIE'], compName = 'LNGs', threshold = 20, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 50), 
                        lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                        ))
                DasNetz.join_comp(data_sources['GIE'], 'LNGs', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
        
        
#        ###  Compressors
        if 'Compressors' in CompNames:
#           Netz_GB
            if 'GB' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GB'], compName = 'Compressors', threshold = 50, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                        lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                        ))
                DasNetz.join_comp(data_sources['GB'], 'Compressors', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
#           Netz_LKD
            if 'LKD' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['LKD'], compName = 'Compressors', threshold = 20, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                        lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                        ))
                DasNetz.join_comp(data_sources['LKD'], 'Compressors', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
        

        ###  Storages
        if 'Storages' in CompNames:
            # Netz_EntsoG
            if 'EntsoG' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['EntsoG'], compName = 'Storages', threshold = 34, multiSelect = True,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['EntsoG'], 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_LKD
            if 'LKD' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['LKD'], compName = 'Storages', threshold = 30, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['LKD'], 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_GIE
            if 'GIE' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GIE'], compName = 'Storages', threshold = 30, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['GIE'], 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_GSE
            if 'GSE' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GSE'], compName = 'Storages', threshold = 36, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['GSE'], 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_IGU
            if 'IGU' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['IGU'], compName = 'Storages', threshold = 30, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['IGU'], 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
        

        ###  Nodes
        if 'Nodes' in CompNames:
            # Netz_EntsoG
            if 'EntsoG' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['EntsoG'], compName = 'Nodes', threshold = 45, multiSelect = True,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['EntsoG'], 'Nodes', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_LKD
            if 'LKD' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['LKD'], compName = 'Nodes', threshold = 20, multiSelect = True,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names_CountryCode(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['LKD'], 'Nodes', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_GB
            if 'GB' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GB'], compName = 'Nodes', threshold = 50, multiSelect = False,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names_CountryCode(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['GB'], 'Nodes', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_GIE
            if 'GIE' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GIE'], compName = 'Nodes', threshold = 30, multiSelect = True,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['GIE'], 'Nodes', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_GSE
            if 'GSE' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['GSE'], compName = 'Nodes', threshold = 30, multiSelect = True,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['GSE'], 'Nodes', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
            # Netz_IGU
            if 'IGU' in data_sources:
                [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
                    DasNetz, data_sources['IGU'], compName = 'Nodes', threshold = 45, multiSelect = True,
                    funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1, AddInWord = 100), 
                    lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, method = 'inv')
                    ))
                DasNetz.join_comp(data_sources['IGU'], 'Nodes', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)


        ###  PipeSegments
        if 'PipeSegments' in CompNames:
            if 'LKD' in data_sources:
                DasNetz, G_Set_Sum = joiningNetze(DasNetz.copy2(), data_sources['LKD'], LengthPercDiff = 0.2, country_code = [])
            if 'GB' in data_sources:
                DasNetz, G_Set_Sum = joiningNetze(DasNetz.copy2(), data_sources['GB'], LengthPercDiff = 0.2, country_code = [])
            

    else:
        print('Error: M_Matching.join: code not written yet')
        

    # assuring that all elements of a component have the same attributes
    DasNetz.setup_SameAttribs([], None)
    
    return DasNetz





def match(Netz_0, Netz_1, compName, threshold, multiSelect, funcs, numFuncs = 2):
    """
    Main function that matches positions of component from different sources/.. 
    to each other, by using different functions that the user specifies.
    
    \n.. comments: 
    Input:
        Netz_0          Instance of first network netz 
        Netz_1          Instance of second network netz 
        compName        string containing compnent lable
        threshold       overall threshold for selection between points, value 
                        between 0 and 100
        funcs           functions, that the user wants to use to find the match
    Return:
        pos_match_Netz_0    ordered list of positions, in respect of Netz_0, that have been linked with positions from Netz_1
        pos_match_Netz_1    ordered list of positions, in respect of Netz_1, that have been linked with positions from Netz_0
        pos_add_Netz_1      list of positions of Netz_1, that need to be added to Netz_0
        pos_add_Netz_0      list of positions of Netz_0, for which a corresponding element was not found in Netz_1
    Example:
        [pos_match_Netz_0, pos_match_Netz_1, pos_add_Netz_1, pos_add_Netz_0] = M_Matching.match(
            Netz_0, Netz_1, compName = 'LNGs', threshold = 80,
            funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.getMatch_LatLong(comp_0, comp_1, 50000)
                ))
    """
    # Initialization
    pos_match_Netz_0    = []
    pos_match_Netz_1    = []
    pos_add_Netz_1      = []
    pos_add_Netz_0      = []
    num_comp_Netz_0     = len(Netz_0.__dict__[compName])
    num_comp_Netz_1     = len(Netz_1.__dict__[compName])

    # creating of a dummy matrix of size of the number of elements from both data set.
    goodness_Matrix     = M_Helfer.get_NameMatrix_Fuzzy([str(x) for x in range(len(Netz_0.__dict__[compName]))], [str(y) for y in range(len(Netz_1.__dict__[compName]))])
    if numFuncs == 1:
        goodness_Matrix_2   = copy.deepcopy(goodness_Matrix)
    else:
        goodness_Matrix_2   = [copy.deepcopy(goodness_Matrix), copy.deepcopy(goodness_Matrix)]
    
    # loops that goes through each combination of component pairs from both data
    # sets and calculating a goodness value, with values between 0 and 100, 
    # based on the sum of the functions supplied by the user
    
    if numFuncs == 1:
        for ii in range(len(Netz_0.__dict__[compName])):
            # going through each element of Netz_0
            comp_0  = Netz_0.__dict__[compName][ii]
            
            # going through each element of Netz_1
            for jj in range(len(Netz_1.__dict__[compName])):
                comp_1  = Netz_1.__dict__[compName][jj]
                # getting goodness over all functions
                goodness                    = funcs(comp_0, comp_1)
                goodness_Matrix_2[ii][jj]   = goodness
                goodness_Matrix[ii][jj]     = goodness + goodness_Matrix_2[ii][jj]
                
    else:
        for ii in range(len(Netz_0.__dict__[compName])):
            # going through each element of Netz_0
            comp_0  = Netz_0.__dict__[compName][ii]
            
            # going through each element of Netz_1
            for jj in range(len(Netz_1.__dict__[compName])):
                comp_1  = Netz_1.__dict__[compName][jj]
                # getting goodness over all functions
                goodness   = 0
                ff = 0
                for func in funcs:
                    goodness_Matrix_2[ff][ii][jj]   = func(comp_0, comp_1)
                    goodness                        = goodness + goodness_Matrix_2[ff][ii][jj]
                    ff = ff + 1
                goodness   = goodness / len(funcs)
    #                goodness   = sum(func(comp_0, comp_1) for func in funcs) / len(funcs)`
    
                # writing goodness value to matrix.            
                goodness_Matrix[ii][jj] = goodness
            
    #goodness_Matrix_Const   = copy.deepcopy(goodness_Matrix)
    
    # now finding the best matching pairs, so looking at the goodness_Matrix and 
    # starting off by selecting the one with the largest goodness, removing this pair
    # from the options and then looking for the next highest goodness value, and 
    # removing this pair, and then repeating this till the goodness value dropps 
    # below the threshold supplied by user.
    while True:
        # finding largest goodness vlue
        [pos_0, pos_1]  = M_FindPos.find_pos_ConditionInMatrix(goodness_Matrix , 'max')

        # check if gooddness value still above threshold value
        if goodness_Matrix[pos_0][pos_1] > threshold:
            # Keeping the positions thare are best    
            pos_match_Netz_0.append(pos_0)
            pos_match_Netz_1.append(pos_1)
        
            # removing pairs from options, by setting values to -inf
            for xx in range(num_comp_Netz_0):
                goodness_Matrix[xx][pos_1] = -np.inf
                
            if multiSelect != True:
                for yy in range(num_comp_Netz_1):
                    goodness_Matrix[pos_0][yy] = -np.inf

        # if next goodnes value is smaller than threshold or none left, then 
        # creating of further return parameters and then leaving function
        elif (goodness_Matrix[pos_0][pos_1] == -np.inf) or (goodness_Matrix[pos_0][pos_1] <= threshold):
            temp_1  = [item for item in range(num_comp_Netz_1) if item not in pos_match_Netz_1] 
            temp_0  = [item for item in range(num_comp_Netz_0) if item not in pos_match_Netz_0] 
            
            for wert in temp_1:
                pos_add_Netz_1.append(wert)
            for wert in temp_0:
                pos_add_Netz_0.append(wert)
            
            break
        
    return [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1]



def joiningNetze(Netz_Set_1, Netz_Set_2, NodeDistDiff = 20, LengthPercDiff = 0.1, country_code = [], MatchList = [], MatchDiff = []):
    """Joining two different networks (of nodes and edges), so that same pipesegments are removed before joining.
    
    \n.. comments:
    Input:
        Netz_Set_1:         Network 1
        Netz_Set_2:         Network 2
        NodeDistDiff:       Distance of separation in km that nodes will be 
                            concidered to be same from different data sources.
                            (Default = 20 km)
        LengthPercDiff :    relative difference in path length difference  
                            (Default = 0.2) 
        country_code:       String of country code that will be pre-selected.
                            (default = [])
    Return:
        Ret_Path_Set_1          
        Ret_Path_Set_2          
    """    
    
    
    ###########################################################################
    # Selection based on country code
    ###########################################################################
    if country_code != []:
        Netz_Set_1.select_byAttrib([], 'country_code', country_code, methodStr = 'inList')
        Netz_Set_2.select_byAttrib([], 'country_code', country_code, methodStr = 'inList')
    
    # finding all possible friends of pipeSegments in both data sets.
    Ret_DiffIndex, RetMinVal, G_Set_1, G_Set_2, nodeID_Set_1_Friends, nodeID_Set_2_Friends     = M_Netze.findEdges_All(Netz_Set_1, Netz_Set_2, NodeDistDiff, LengthPercDiff)
    
    
#    minimum_Diff_Index, minVal, G_Set_1, G_Set_2, nodeID_Set_1_Friends, nodeID_Set_2_Friends = findEdges(Netz_Set_1, Netz_Set_2)
    
    Netz_Set_1, Netz_Set_2      = removedEdge_all(Ret_DiffIndex, Netz_Set_1, Netz_Set_2, G_Set_1, G_Set_2, nodeID_Set_1_Friends, nodeID_Set_2_Friends, MatchList, MatchDiff)

    for comp in Netz_Set_2.__dict__['PipeSegments']:
        Netz_Set_1.__dict__['PipeSegments'].append(comp)
        
    Netz_Set_1.Nodes      = Netz_Set_1.add_Nodes(['PipeSegments'], [])

        
    
    return Netz_Set_1, Netz_Set_2

def removedEdge_all(Minimum_Diff_Index, Netz_Set_1, Netz_Set_2, G_Set_1, G_Set_2, nodeID_Set_1_Friends, nodeID_Set_2_Friends, MatchList = [], MatchDiff = []):

    ###########################################################################
    # working out which path to take between selecgted nodes
    ###########################################################################
    

    NewEdge     = []
    count       = 0
    for id1, minimum_Diff_Index in enumerate(Minimum_Diff_Index):
        
        try:
            if id1 == 3:
                pass
            lat_Set_1, long_Set_1, length_Set_1, edge_id_set_1, nodes_id_Set_1, addValues_1  = get_PathInfo(G_Set_1, nodeID_Set_1_Friends[minimum_Diff_Index[0]], nodeID_Set_1_Friends[minimum_Diff_Index[1]], MatchList)
            lat_Set_2, long_Set_2, length_Set_2, edge_id_set_2, nodes_id_Set_2, addValues_2  = get_PathInfo(G_Set_2, nodeID_Set_2_Friends[minimum_Diff_Index[0]], nodeID_Set_2_Friends[minimum_Diff_Index[1]], MatchList)
            
#            ############################################
#            # further criteria
#            ############################################
            UseLine = True
            for idx, match in enumerate(MatchList):
                wert1 = addValues_1[0][idx]
                wert2 = addValues_2[0][idx]
                if wert1 != None and wert2 != None:
                    if wert2 < wert1 * (1 - MatchDiff[idx]) or wert2 > wert1 * (1 + MatchDiff[idx]):
                        UseLine = False
            
            ############################################
            # removing and adding of pipeLines/Segments
            ############################################
            if len(lat_Set_1) > 0 and len(lat_Set_2) > 0 and UseLine == True:
                # Removing Edge in set one
                for edge in edge_id_set_1[0]:
                    RetElement  = Netz_Set_1.select_byAttrib(CompNames = ['PipeSegments'], AttribName = 'id', AttribVal = edge[0], methodStr = '!=')
                    count = count + len(RetElement)
            
                # Removing edges in second data set, 
                # and returning those, that need to be copied to set 1
                if len(RetElement) > 0:
                    for edge in edge_id_set_2[0]:
                        temp = Netz_Set_2.select_byAttrib(CompNames = ['PipeSegments'], AttribName = 'id', AttribVal = edge[0], methodStr = '!=')
                        if temp != []:
                            # Merging meta data in Param
                            temp[0].mergeAttribs(RetElement[0])
                            NewEdge.append(temp[0])
#            else:
#                print('y', end = '')

        except:
#            print('x', id1, end = '')
            pass
    
    # adding edges from second to first data set
    for edge in NewEdge:
        Netz_Set_1.addElement(CompName = 'PipeSegments', element = edge)
    
    
    # assuring that all PipeSegments have the same attribs
    Netz_Set_1.declar_SameAttribs(CompNames = ['PipeSegments'], fillVal = None)
    
    
    Netz_Set_1.Nodes      = Netz_Set_1.add_Nodes(['PipeSegments'], [])
    Netz_Set_2.Nodes      = Netz_Set_2.add_Nodes(['PipeSegments'], [])
    

    return Netz_Set_1, Netz_Set_2
    




def removedEdge(minimum_Diff_Index, Netz_Set_1, Netz_Set_2, G_Set_1, G_Set_2, nodeID_Set_1_Friends, nodeID_Set_2_Friends, NodeDistThreshold = 20000, cutoff = 3, MatchList = [], MatchDiff = []):

    ###########################################################################
    # working out which path to take between selecgted nodes
    ###########################################################################
    removedTrue = False
    try:
        lat_Set_1, long_Set_1, length_Set_1, edge_id_set_1, nodes_id_Set_1, addValues_1  = get_PathInfo(G_Set_1, nodeID_Set_1_Friends[minimum_Diff_Index[0]], nodeID_Set_1_Friends[minimum_Diff_Index[1]], cutoff = cutoff, MatchList  = MatchList )
        lat_Set_2, long_Set_2, length_Set_2, edge_id_set_2, nodes_id_Set_2, addValues_2  = get_PathInfo(G_Set_2, nodeID_Set_2_Friends[minimum_Diff_Index[0]], nodeID_Set_2_Friends[minimum_Diff_Index[1]], cutoff = cutoff, MatchList  = MatchList )
    except:
        return Netz_Set_1, Netz_Set_2, removedTrue
    
    
    if len(lat_Set_1) > 0 and len(lat_Set_2) > 0:
        NewEdge = []
        # Removing Edge in set one
        for edge in edge_id_set_1[0]:
            Netz_Set_1.select_byAttrib(CompNames = ['PipeSegments'], AttribName = 'id', AttribVal = edge[0], methodStr = '!=')
    
    
        # Removing edges in second data set, and keepin those        
        for edge in edge_id_set_2[0]:
            temp = Netz_Set_2.select_byAttrib(CompNames = ['PipeSegments'], AttribName = 'id', AttribVal = edge[0], methodStr = '!=')
            if temp != []:
                NewEdge.append(temp[0])
                
                
        # adding edges from second to first data set
        for edge in NewEdge:
            Netz_Set_1.addElement(CompName = 'PipeSegments', element = edge)
        
        Netz_Set_1.Nodes      = Netz_Set_1.add_Nodes(['PipeSegments'], [])
        Netz_Set_2.Nodes      = Netz_Set_2.add_Nodes(['PipeSegments'], [])
        removedTrue             = True

    
    return Netz_Set_1, Netz_Set_2, removedTrue




def get_PathInfo(G_Set, node_Start, node_End, MatchList = []):
    """Gets information on paths between two points (**node_Start**, **node_End**), 
    for graph **G_Set**
    
    \n.. comments:
    Input:
        G_Set           networkX graph
        node_Start      node of start point
        node_End        node of end point
    Return:
        lat_Set         list of lat values for each segment
        long_Set        list of long values for each segment
        lengths_set     list of length values for each segment
        edge_id_set     list of edge IDs for each segment
        nodes_id_set:   list of node IDs for each segment
    """    
    
    lat_Set         = []
    long_Set        = []
    lengths_set     = []
    edge_id_set     = []
    nodes_id_set    = []
    addValues       = []
    
    # Setting upper limit of itteration of different path options
    
        
    if G_Set.degree(node_Start) == 0:
        return  lat_Set, long_Set, lengths_set, edge_id_set, nodes_id_set
    elif G_Set.degree(node_End) == 0:
        return  lat_Set, long_Set, lengths_set, edge_id_set, nodes_id_set
    
    # Getting first shortest path
    try:
        p       = NX.shortest_path(G_Set, source = node_Start, target = node_End, weight = 'weight')
    except:
        p       = []
    
    if len(p) > 0:
        # working out how many different path options there are for those edges due to parallel edges
        lenPos          = []
        tempedge_id_set = []
        templength      = []
        tempLong        = []
        tempLat         = []
        tempNodes       = []
        for indx_p in range(len(p)-1):
            lenPos.append(len(G_Set[p[indx_p]][p[indx_p+1]]))
            wert    = []
            wert2   = []
            length  = []
            lat     = []
            long    = []
            nodes   = []
            for idx_edge in range(len(G_Set[p[indx_p]][p[indx_p+1]])):
                
                wert.append(G_Set[p[indx_p]][p[indx_p + 1]][idx_edge]['id'])
                length.append(G_Set[p[indx_p]][p[indx_p + 1]][idx_edge]['weight'])
                for match in MatchList:
                    try:
                        wert2.append(G_Set[p[indx_p]][p[indx_p + 1]][idx_edge]['param'][match])
                    except:
                        wert2.append(None)
#                    addProperties.append(match)
                addValues.append(wert2)
                lat.append(G_Set.node[p[indx_p]]['pos'][1])
                long.append(G_Set.node[p[indx_p]]['pos'][0])
                lat.append(G_Set.node[p[indx_p + 1]]['pos'][1])
                long.append(G_Set.node[p[indx_p + 1]]['pos'][0])
                nodes.append(p[indx_p] + ',' + p[indx_p+1])
            tempedge_id_set.append(wert)
            templength.append(length)
            tempLat.append(lat)
            tempLong.append(long)
            tempNodes.append(nodes)
            
        
        
        for columns in  itertools.product(*tempedge_id_set):
            edge_id_set.append(columns)
        for columns in  itertools.product(*tempNodes):
            nodes_id_set.append(columns)
        for columns in  itertools.product(*templength):
            aa = 0
            for cc in columns:
                aa = aa + cc
            lengths_set.append(aa)
        for columns in  itertools.product(*tempLat):
            lat_Set.append(sum(columns) / len(columns))
        for columns in  itertools.product(*tempLong):
            long_Set.append(sum(columns) / len(columns))
                
    return  lat_Set, long_Set, lengths_set, edge_id_set, nodes_id_set, addValues
