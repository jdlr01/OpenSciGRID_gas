# -*- coding: utf-8 -*-
"""
M_Matching
**********

"""

import Code.K_Component       as K_Comp
import Code.M_FindPos         as M_FindPos
import Code.M_Helfer          as M_Helfer
import math







def getMatch_Names(comp_0, comp_1, AddInWord = 0):
    """Returns the measure of how similar two names are, ranging from 0..100
    """
    
    # Initialization
    
    if comp_0 == '':
        return 0
    elif comp_1 == '':
        return 0
    else:
        # Creation of list of names
        names_Netz_0    = comp_0.name.lower()
        names_Netz_1    = comp_1.name.lower()
        
        # Creation of matrix of largest sameness
        name_Matrix     = M_Helfer.get_NameMatrix_Fuzzy(names_Netz_0, names_Netz_1)
        retVal          = name_Matrix[0][0]
        if AddInWord > 0:
            if len(names_Netz_0) > 3 and len(names_Netz_1) > 3:
                if names_Netz_0.replace(' ', '') in names_Netz_1.replace(' ', '') or names_Netz_1.replace(' ', '') in names_Netz_0.replace(' ', ''):
                    retVal = retVal + AddInWord
        
    return retVal



    
def getMatch_Names_CountryCode(comp_0, comp_1, AddInWord  = 0):
    """Returns the measure of how similar two names are, and if in same country, 
    ranging from 0..100
    """
    
    # Initialization
    
    if comp_0 == '':
        return 0
    elif comp_1 == '':
        return 0
    else:
        # Creatoin of list of names
        names_Netz_0    = comp_0.name.lower()
        names_Netz_1    = comp_1.name.lower()

        cc_Netz_0    = comp_0.country_code
        cc_Netz_1    = comp_1.country_code
        
        
        if cc_Netz_0 == cc_Netz_1 or cc_Netz_1 == None or cc_Netz_0 == None:
            # Creation of matrix of largest sameness
            name_Matrix     = M_Helfer.get_NameMatrix_Fuzzy(names_Netz_0, names_Netz_1)
            retVal          = name_Matrix[0][0]
            if AddInWord > 0:
                if len(names_Netz_0) > 3 and len(names_Netz_1) > 3:
                    if names_Netz_0.replace(' ', '') in names_Netz_1.replace(' ', '') or names_Netz_1.replace(' ', '') in names_Netz_0.replace(' ', ''):
                        retVal = retVal + AddInWord
        else:
            return -100000
    
    return retVal




def getMath_LatLong_Threshold(comp_0, comp_1, methodVal = 50000):
    """Gets the separation between two points, and then checks if distance is 
    smaller than **methodVal**.  If Trued, then returns 100, if false, then returns 0
    """
    
    # Initialization
    RetVal  = 0
    
    # Netz_0 is empty
    if comp_0 == '':
        pass
        
    # Netz_1 is empty
    elif comp_1 == '':
        pass
    
    elif comp_0.long == None:
        pass
    
    elif comp_1.long == None:
        pass

    # Both Netze contain components  
    else:
        # Creation of LatLong "vector" from component latlong
        latlong_Netz_0  = K_Comp.PolyLine(lat = [comp_0.lat], long = [comp_0.long] ) #M_Netze.get_latlongPairs_Points(comp_0)
        thisLatLong     = K_Comp.PolyLine(lat = comp_1.lat, long = comp_1.long ) #M_Netze.get_latlongPairs_Points(comp_1)
        
        [pos, minVal]       = M_FindPos.find_pos_closestLatLongInList(thisLatLong, latlong_Netz_0)
        
        if math.isnan(minVal):
            RetVal = 0
        elif minVal <= methodVal:
            RetVal = 100
        else:
            RetVal = 0
                
    # Testig if nan, if so then set to zero
    if math.isnan(RetVal) :
        RetVal = 0
                
    return RetVal



	
def get_Comp_LatLong(comp_0, comp_1, method = 'inv'):
    """Gets the separation between two points in km, and returns as 100-1/distance and other methods.  
    Method allows to select different measures of distance returned (distance used here in [km]), from: 
    "inv"       (100 / distance), 
    "power2inv" (100 / (distance^2)), 
    "loginv"    (100 / log(distance), with base e),
    "log10inv"  (100 / log10(distance), with base 10),
    "distance" (distance)
    """
    
    # Initialization
    RetVal = 0
    
    # Netz_0 is empty
    if comp_0 == '':
        return  0
        
    # Netz_1 is empty
    elif comp_1 == '':
        return  0
    
    elif comp_0.long == None:
        return  0
    
    elif comp_1.long == None:
        return  0
    
    elif type(comp_0.lat) == str:
        print('ERROR: M_Matching.getComp_LatLong: input type is string.  Float expected. comp_0')
        
    elif type(comp_1.lat) == str:
        print('ERROR: M_Matching.getComp_LatLong: input type is string.  Float expected. comp_1')

    # Both Netze contain components  
    else:
        # Creation of LatLong "vector" from component latlong
        latlong_Netz_0  = K_Comp.PolyLine(lat = [comp_0.lat], long = [comp_0.long] ) #M_Netze.get_latlongPairs_Points(comp_0)
        thisLatLong     = K_Comp.PolyLine(lat = comp_1.lat, long = comp_1.long ) #M_Netze.get_latlongPairs_Points(comp_1)
        
        [pos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, latlong_Netz_0)
        minVal          = minVal/1000
        
        if minVal == 0.0:
            RetVal =  100
        elif method == 'inv':
            RetVal = min([100 / minVal, 100])
            
        elif method == 'power2inv':
            RetVal = 100 / minVal/minVal
            
        elif method == 'log10inv':
            RetVal = 100 / math.log(minVal, 10)
            
        elif method == 'loginv':
            RetVal = 100 / math.log(minVal)
            
        elif method == 'distance':
            RetVal = minVal
        else:
            print('ERROR: M_Matching: get_Comp_LatLong: method not defined.')
            
    # Testig if nan, if so then set to zero
    if math.isnan(RetVal) :
        RetVal = 0
        
    return RetVal




def getMatch_LatLong_CountryCode(comp_0, comp_1, method = 'inv', thresholdVal = None):
    """Gets the separation between two points in km, and returns as 100-1/distance and other methods.  
    Method allows to select different measures of distance returned (distance used here in [km]), from: 
    "inv"       (100 / distance), 
    "power2inv" (100 / (distance^2)), 
    "loginv"    (100 / log(distance), with base e),
    "log10inv"  (100 / log10(distance), with base 10),
    "distance" (distance)
    """
    # Initialization
        
    RetVal = 0
    # Netz_0 is empty
    if comp_0 == '':
        RetVal = 0
        
    # Netz_1 is empty
    elif comp_1 == '':
        RetVal = 0
    
    elif comp_0.long == None:
        RetVal = 0
    
    elif comp_1.long == None:
        RetVal = 0
    
    elif type(comp_0.lat) == str:
        print('ERROR: M_Matching.getComp_LatLong: input type is string.  Float expected. comp_0')
        RetVal
    elif type(comp_1.lat) == str:
        print('ERROR: M_Matching.getComp_LatLong: input type is string.  Float expected. comp_1')
        RetVal = 0

    # Both Netze contain components  
    else:
        cc_Netz_0    = comp_0.country_code
        cc_Netz_1    = comp_1.country_code
        
        if cc_Netz_0 == cc_Netz_1 or cc_Netz_1 == None or cc_Netz_0 == None:
            # Creation of LatLong "vector" from component latlong
            
            latlong_Netz_0  = K_Comp.PolyLine(lat = [comp_0.lat], long = [comp_0.long] ) #M_Netze.get_latlongPairs_Points(comp_0)
            thisLatLong     = K_Comp.PolyLine(lat = comp_1.lat, long = comp_1.long ) #M_Netze.get_latlongPairs_Points(comp_1)
            
            [pos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, latlong_Netz_0)
            #minVal          = minVal/1000
            
            if minVal == 0.0:
                RetVal = 100
            elif method == 'inv':
                RetVal = min([100 / minVal, 100])
            elif method == 'power2inv':
                RetVal = 100 / minVal/minVal
            elif method == 'log10inv':
                RetVal = 100 / math.log(minVal, 10)
            elif method == 'loginv':
                RetVal = 100 / math.log(minVal)
            elif method == 'distance':
                RetVal = minVal
            elif method == 'distanceThreshold':
                if minVal <= thresholdVal:
                    RetVal = 100
            elif method == 'exp':
                    RetVal = 100 *  math.exp(-minVal*1000/thresholdVal)
            else:
                print('ERROR: M_Matching: get_Comp_LatLong: method not defined.')
        else:
            return -100000

    # Testig if nan, if so then set to zero
    if math.isnan(RetVal) :
        RetVal = 0
                
    return RetVal

	
	
	
#def replacePipeSegments(Netz_Main, Netz_Fine, nodeDistance = 10000, lengthDistance = 0.2):
#    """This function does not do a thing
#    """	
#   # Determine which nodes are the same in both data sets
#    [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = match(
#        Netz_Main, Netz_Fine, compName = 'Nodes', threshold = 45, multiSelect = False,
#        numFuncs = 1,
#        funcs = (
#        lambda comp_0, comp_1: getMatch_LatLong_CountryCode(comp_0, comp_1, method = 'inv')
#        ))
#    
#    # Convert Netz_Fine into NetWorkx
#    InfoDict = {'Gewichtung': 'Gleich', 'Weight': 'Gleich'}
#    [Graph_Fine, MDGraph_Fine]    = M_Graph.build_nx(InfoDict, Netz_Fine)
#    [Graph_Main, MDGraph_Main]    = M_Graph.build_nx(InfoDict, Netz_Main)
#    
#    for pipe1 in Netz_Main.PipeSegments:
#        # Determine length of network 1
#        pair        = [pipe1.node_id[0], pipe1.node_id[1]]
#        length_Main = M_Graph.get_shortest_paths_distances(Graph_Main, pair, edge_weight_name = 'length')
#        
#        # Determine length of network 2
#        #pos = M_FindPos.find_pos_ValInVector(Val, Vector, Type)
#        length_Fine = M_Graph.get_shortest_paths_distances(Graph_Fine, pair, edge_weight_name = 'length')
#    
#    print('M_Matching.replacePipeSegments: this function need checking, currently does nothing')
#    
#    return Netz_Main
	