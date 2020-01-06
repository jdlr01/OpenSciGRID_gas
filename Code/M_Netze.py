# -*- coding: utf-8 -*-
"""
M_Netze
-------

Collection of functions, that are being called from other modules, for applications on Netz instances.
"""

import networkx              as NX
import array 			     as arr
import numpy                 as np
import Code.M_FindPos        as M_FindPos
import Code.M_MatLab         as M_MatLab
import Code.M_Helfer         as M_Helfer
import Code.M_Projection     as M_Projection 
import Code.K_Component      as K_Component
import Code.M_Visuell        as M_Visuell
import Code.M_Graph          as M_Graph
import Code.M_Matching       as M_Matching
import Code.JoinNetz         as JoinNetz
#import igraph                as iGraph
import math
import os
from scipy.spatial.distance import cdist    

import matplotlib.pyplot        as plt

def findEdges_All(Netz_Set_1, Netz_Set_2, NodeDistDiff, LengthPercDiff):

    ###########################################################################
    # Forming networkx networks off data
    ###########################################################################
    [_, G_Set_1,]   = M_Graph.build_nx(InfoDict = '', Daten = Netz_Set_1, Method = 'latLongNodes', removeExtraNodes = True)
    [_, G_Set_2,]   = M_Graph.build_nx(InfoDict = '', Daten = Netz_Set_2, Method = 'latLongNodes', removeExtraNodes = True)
    
    Netz_Set_2      = M_Graph.Graph2Netz(G_Set_2)
    Netz_Set_1      = M_Graph.Graph2Netz(G_Set_1)
    
    
    ###########################################################################
    # Finding matching friends of Nodes
    ###########################################################################
    [pos_match_Netz_1, pos_add_Netz_1, pos_match_Netz_2, pos_add_Netz_2] = JoinNetz.match(
            Netz_Set_1, Netz_Set_2, compName = 'Nodes', threshold = 15, multiSelect = True,
            numFuncs = 1,
            funcs = (
                lambda comp_0, comp_1: M_Matching.getMatch_LatLong_CountryCode(comp_0, comp_1, method = 'distanceThreshold', thresholdVal = NodeDistDiff)
            ))
        
            
    ###########################################################################
    # lists of Nodes for each network
    ###########################################################################
    # lists of Nodes for each network with friends
    nodeID_Set_1_Friends     = M_MatLab.select_Vector(Netz_Set_1.get_Attrib('Nodes', 'name'), pos_match_Netz_1)
    nodeID_Set_2_Friends     = M_MatLab.select_Vector(Netz_Set_2.get_Attrib('Nodes', 'name'), pos_match_Netz_2)
    
    
    
    ###########################################################################
    # working out which node has which friend in other data set
    ###########################################################################
    # Set 1
    # Creation of matrix with distance values between points
    coords_Set_1        = get_coordlist(G_Set_1.nodes(), nodeIds = nodeID_Set_1_Friends)
    dist_matrix_Set_1   = np.matrix        
    dist_matrix_Set_1   = CalcDistanceMatrix(coords_Set_1)
    # removing all zeros and replacing with Inf (indlucing diagonal and multiple 
    # entries), as elements on box axis are not unique
    dist_matrix_Set_1[dist_matrix_Set_1 == 0] = np.inf

    # Set 2
    coords_Set_2        = get_coordlist(G_Set_2.nodes(), nodeIds = nodeID_Set_2_Friends)
    dist_matrix_Set_2   = np.matrix        
    dist_matrix_Set_2   = CalcDistanceMatrix(coords_Set_2)
    # removing all zeros and replacing with Inf (indlucing diagonal and multiple 
    # entries), as elements on box axis are not unique
    dist_matrix_Set_2[dist_matrix_Set_2 == 0] = np.inf

    # Forming the difference in path between both data sets
    # Relative Difference matrix, value of  [0..inf]
    dist_matrix_Diff    = M_MatLab.relDiff_2Matrix(dist_matrix_Set_1, dist_matrix_Set_2)
    dist_matrix_Diff    = M_MatLab.abs_Matrix(dist_matrix_Diff)
    # removing all nan and replacing with Inf (indlucing diagonal and 
    # multiple entries), as while creation of this matrix np.inf were "converted"
    # to np.nan
    dist_matrix_Diff[np.isnan(dist_matrix_Diff) == True] = np.inf
    
    
    
    ###########################################################################
    # ???
    ###########################################################################
    # getting the minimum relative distance value and the corresponding index
    # Getting the node indices, of the pipeSegments that are same in both data sets, through distance matrix
    Ret_DiffIndex           = []
    Ret_MinVal              = []
    
    Final_Ret_DiffIndex     = []
    Final_Ret_MinVal        = []
    
    minimum_Diff_Index      = np.unravel_index(np.argmin(dist_matrix_Diff, axis=None), dist_matrix_Diff.shape)
    minVal                  = dist_matrix_Diff.min()
    
    
    while minVal < LengthPercDiff:
        Ret_DiffIndex.append(minimum_Diff_Index)
        Ret_MinVal.append(minVal)
        dist_matrix_Diff[minimum_Diff_Index[0]][minimum_Diff_Index[1]]    = np.inf
        dist_matrix_Diff[minimum_Diff_Index[1]][minimum_Diff_Index[0]]    = np.inf
        
        minimum_Diff_Index      = np.unravel_index(np.argmin(dist_matrix_Diff, axis=None), dist_matrix_Diff.shape)
        minVal                  = dist_matrix_Diff.min()

    for idx in range(len(Ret_MinVal)):
        minimum_Diff_Index  = Ret_DiffIndex[idx]
        source              = nodeID_Set_1_Friends[minimum_Diff_Index[0]]
        target              = nodeID_Set_1_Friends[minimum_Diff_Index[1]]
        dist1, numberNodes  = getLength(G_Set_1, source = source, target = target, weight = 'weight')
        dist2, __           = getLength(G_Set_2, source = nodeID_Set_2_Friends[minimum_Diff_Index[0]], target = nodeID_Set_2_Friends[minimum_Diff_Index[1]], weight = 'weight')
        
        
        minVal = abs(dist1 - dist2) / dist1
        if minVal < LengthPercDiff and numberNodes == 2:
            Final_Ret_DiffIndex.append(minimum_Diff_Index)
            Final_Ret_MinVal.append(minVal)

    
    return Final_Ret_DiffIndex, Final_Ret_MinVal, G_Set_1, G_Set_2, nodeID_Set_1_Friends, nodeID_Set_2_Friends






def getLength(G_Set_1, source = '', target = '', weight = 'weight'):
    """Determine distance between two points using networkx **G_Set_1**, nodes **source** and **target**,
    using attribute given through **weight** from network. """
    
    Ret_dist1 = 0
    numberNodes = 1
    try:
        dist1 = NX.shortest_path(G_Set_1, source = source , target = target, weight = 'weight')
        
        for idx in range(len(dist1)-1):
            Ret_dist1 =  Ret_dist1 + G_Set_1[dist1[idx]][dist1[idx+1]][0][weight]
            numberNodes = numberNodes + 1
        
        return Ret_dist1, numberNodes
    except:
        Ret_dist1 = 99999999999999999999999999999
        return Ret_dist1, -999







    



def schrott():
    
    G_Set_1 = []
    G_Set_2 = []
    length_Set_1 = []
    length_Set_2 = []
    minimum_Diff_Val= []
    edge_id_set_1 = []
    PercDiff = []
    minimum_Diff_Index = []
    nodes_id_Set_1 = []
    nodes_id_Set_2 = []
    nodeID_Set_1_Friends = []
    nodeID_Set_2_Friends = []
    cutoff = []
    dist_matrix_Diff = []
    
    
    print('set 1 ', nodeID_Set_1_Friends[minimum_Diff_Index[0]])
    print('set 1 ', nodeID_Set_1_Friends[minimum_Diff_Index[1]])
    print(' ')
    print('set 2 ', nodeID_Set_2_Friends[minimum_Diff_Index[0]])
    print('set 2 ', nodeID_Set_2_Friends[minimum_Diff_Index[1]])
    print(' ')
    
    minimum_Diff_Index  = np.unravel_index(np.argmin(dist_matrix_Diff, axis=None), dist_matrix_Diff.shape)
    print('set 1 ', nodeID_Set_1_Friends[minimum_Diff_Index[0]])
    print('set 1 ', nodeID_Set_1_Friends[minimum_Diff_Index[1]])
    print(' ')
    print('set 2 ', nodeID_Set_2_Friends[minimum_Diff_Index[0]])
    print('set 2 ', nodeID_Set_2_Friends[minimum_Diff_Index[1]])

    
    edge_distMatrix     = makeRelDistMatrix(length_Set_1, length_Set_2)
    minimum_Diff_Index  = np.unravel_index(np.argmin(edge_distMatrix, axis=None), edge_distMatrix.shape)
    minimum_Diff_Val    = edge_distMatrix.min()

    print(' ')
    figNum  = 1
    fig = plt.figure(figNum)
    NX.draw(G_Set_1, NX.get_node_attributes(G_Set_1, 'pos'), node_size = 7)
    fig.show()
    figNum = figNum + 1
    
    # jumping into while loop, as long as relative distance value is smaller than threshold    
    while len(length_Set_1)>0 and len(length_Set_2) > 0 and minimum_Diff_Val < PercDiff:
        ####[]
        print('While Loop')
        print(edge_id_set_1)
        # 1) removing edges from  network 1
        for u, v, key, data in list(G_Set_1.edges(None, data = True, keys = True)):
            if data['id'] in edge_id_set_1[minimum_Diff_Index[0]]:
                print('removing edge: ', data['id'])
                # finding nodes set 
                pos     = M_FindPos.find_pos_StringInTouple(data['id'][0], edge_id_set_1[minimum_Diff_Index[0]])
                nodes   = nodes_id_Set_1[minimum_Diff_Index[0]][pos[0]]
                
                # Disecting nodes string
                pos     = M_FindPos.find_pos_CharInStr(',', nodes)
                node1   = nodes[:pos[0]]
                node2   = nodes[pos[0]+1:]
                
                # Removing Edge
                G_Set_1.remove_edge(node1, node2, key = key)
                
                
                # Now moving node position if same node in both data sets
                if node1 in nodeID_Set_1_Friends:
                    pos     = M_FindPos.find_pos_StringInList(node1, nodeID_Set_1_Friends)
                    lat     = G_Set_2.node[nodeID_Set_2_Friends[pos[0]]]['pos'][1]
                    long    = G_Set_2.node[nodeID_Set_2_Friends[pos[0]]]['pos'][0]
                    G_Set_1.node[node1]['pos'] = (long, lat)
                    
                if node2 in nodeID_Set_1_Friends:
                    pos     = M_FindPos.find_pos_StringInList(node2, nodeID_Set_1_Friends)
                    lat     = G_Set_2.node[nodeID_Set_2_Friends[pos[0]]]['pos'][1]
                    long    = G_Set_2.node[nodeID_Set_2_Friends[pos[0]]]['pos'][0]
                    G_Set_1.node[node2]['pos'] = (long, lat)
                    
        # Plotting resulting network
        fig = plt.figure(figNum)
        NX.draw(G_Set_1, NX.get_node_attributes(G_Set_1, 'pos'), node_size = 7)
        fig.show()
        figNum = figNum + 1

        
        # 2) rerunning get_matchingPath
        print('execution of get_PathInfo in while loop')
        lat_Set_1, long_Set_1, length_Set_1, edge_id_set_1, nodes_id_Set_1      = get_PathInfo(G_Set_1, nodeID_Set_1_Friends[minimum_Diff_Index[0]], nodeID_Set_1_Friends[minimum_Diff_Index[1]], cutoff  = cutoff )
        lat_Set_2, long_Set_2, length_Set_2, edge_id_set_2, nodes_id_Set_2      = get_PathInfo(G_Set_2, nodeID_Set_2_Friends[minimum_Diff_Index[0]], nodeID_Set_2_Friends[minimum_Diff_Index[1]], cutoff  = cutoff )
        
        if len(lat_Set_2)>0:
            edge_distMatrix     = makeRelDistMatrix(length_Set_1, length_Set_2)
            minimum_Diff_Index  = np.unravel_index(np.argmin(edge_distMatrix, axis=None), edge_distMatrix.shape)
            minimum_Diff_Val    = edge_distMatrix.min()
        else:
            minimum_Diff_Val    = PercDiff * 2 

    ###########################################################################
    # Joining the two networks
    ###########################################################################
    G_Set_Sum = NX.compose(G_Set_1, G_Set_2)
    
    # removing nodes of degree zero
    deg = G_Set_Sum.degree(G_Set_Sum)
    for n in list(G_Set_Sum.nodes()):
        if deg[n] == 0:
            G_Set_Sum.remove_node(n)
    
    # converting graph into network
    G_Netz = M_Graph.Graph2Netz(G_Set_Sum)
    print('leaving function')
    return G_Netz, G_Set_Sum




def plotRawData(PlotOn, Netz_Set_1, Netz_Set_2, figureNum, countrycode, LegendOn, SingleSize = 250):
    if PlotOn:
        if LegendOn:
            M_Visuell.quickplot(Netz_Set_1, figureNum = figureNum, LegendStyle = 'Str(Num)', countrycode = countrycode, SingleSize = 60, SingleColor = 'r',
                                 PlotList = ['PipeSegments'], IgnoreList = 'all', Cursor = True, LegendStr = 'Set_1 Pipes')
            M_Visuell.quickplot(Netz_Set_1, figureNum = figureNum, LegendStyle = 'Str(Num)', countrycode = None, SingleSize = SingleSize, SingleColor = 'r',
                                 PlotList = ['Nodes'], IgnoreList = 'all', Cursor = True, LegendStr = 'Set_1 Nodes')
            M_Visuell.quickplot(Netz_Set_2, figureNum = figureNum, LegendStyle = 'Str(Num)', countrycode = None, SingleSize = 60, SingleColor = 'b',
                                 PlotList = ['PipeSegments'], IgnoreList = 'all', Cursor = True, LegendStr = 'Set_2 Pipes')
            M_Visuell.quickplot(Netz_Set_2, figureNum = figureNum, LegendStyle = 'Str(Num)', countrycode = None, SingleSize = SingleSize, SingleColor = 'b',
                                 PlotList = ['Nodes'], IgnoreList = 'all', Cursor = True, LegendStr = 'Set_2 Nodes')
        else:
            M_Visuell.quickplot(Netz_Set_1, figureNum = figureNum, countrycode = countrycode, SingleSize = 60, SingleColor = 'r',
                                 PlotList = ['PipeSegments'], IgnoreList = 'all', Cursor = True)
            M_Visuell.quickplot(Netz_Set_1, figureNum = figureNum, countrycode = None, SingleSize = SingleSize, SingleColor = 'r',
                                 PlotList = ['Nodes'], IgnoreList = 'all', Cursor = True)
            M_Visuell.quickplot(Netz_Set_2, figureNum = figureNum, countrycode = None, SingleSize = 60, SingleColor = 'b',
                                 PlotList = ['PipeSegments'], IgnoreList = 'all', Cursor = True)
            M_Visuell.quickplot(Netz_Set_2, figureNum = figureNum, countrycode = None, SingleSize = SingleSize, SingleColor = 'b',
                                 PlotList = ['Nodes'], IgnoreList = 'all', Cursor = True)




def plotMatchedPoints(PlotOn, Netz_Set_1, Netz_Set_2, figureNum, countrycode, LegendOn, pos_match_Netz_0, pos_match_Netz_1, SingleSize = 250):
    if PlotOn:
        # with Legend
        if LegendOn:
            M_Visuell.quickplot(Netz_Set_1, figureNum = figureNum, LegendStyle = 'Str(Num)', countrycode = countrycode, SingleSize = SingleSize, SingleColor = 'g',
                                 PlotList = ['Nodes'], IgnoreList = 'all', selectList = pos_match_Netz_0, LegendStr = 'Set_1 Nodes Match')
            M_Visuell.quickplot(Netz_Set_2, figureNum = figureNum, LegendStyle = 'Str(Num)', countrycode = None, SingleSize = SingleSize, SingleColor = 'y',
                                 PlotList = ['Nodes'], IgnoreList = 'all', selectList = pos_match_Netz_1, LegendStr = 'Set_2 Nodes Match')
        # Without LegendOn
        else:
            M_Visuell.quickplot(Netz_Set_1, figureNum = figureNum, countrycode = None, SingleSize = SingleSize, SingleColor = 'g',
                                 PlotList = ['Nodes'], IgnoreList = 'all', selectList = pos_match_Netz_0)
            M_Visuell.quickplot(Netz_Set_2, figureNum = figureNum, countrycode = None, SingleSize = SingleSize, SingleColor = 'y',
                                 PlotList = ['Nodes'], IgnoreList = 'all', selectList = pos_match_Netz_1)
    


# Von Adam
def CalcDistanceMatrix(points):
    """Generation of a matrix of distance values, supplied to function as **points**."""
    
    retMatrix = cdist(points,points)
    for xx in range(len(points)):
        for yy in range(len(points)):
            retMatrix[xx][yy] = M_Projection.LatLong2DistanceValue(points[xx][0], points[xx][1], points[yy][0], points[yy][1])
        
    return retMatrix




def get_coordlist(nodes, nodeIds = []):
        """Get coordinates of all nodes **nodes**, or of subset given through **nodeIds**.
        """

        coords = []
        if len(nodeIds) == 0:
            for node in nodes:
                 coords.append(nodes[str(node)]['pos'])
        else:
            for nodeId in nodeIds:
#                coords.append(nodes[str(nodeId)]['pos'])
                try:
                    coords.append(nodes[str(nodeId)]['pos'])
                except:
#                    pass
                    print('Missing edge node ' + str(nodeId))
#                    coords.append((None, None))
        
        return np.asarray(coords)









def makeRelDistMatrix(len_S_1, len_S_2):
    """Returns matrix (numpy) of relative distances difference 
    [makeRelDistMatrix = abs(len_S_1 - len_S_2)/len_S_1 ]
    
    \n.. comments:
    Input:
        len_S_1                 list of distances
        len_S_2                 list of distances
    Return:
        edge_distMatrix:        Numpy matrix of relative distance difference
    """    
    
    edge_distMatrix = np.empty((len(len_S_1), len(len_S_2), ))
    for xx in range(len(len_S_1)):
        for yy in range(len(len_S_2)):
            edge_distMatrix[xx][yy] = abs((len_S_1[xx] -  len_S_2[yy]) / len_S_1[xx])
    
    return edge_distMatrix



       
def get_latlongPairs_Points(Components):
    """Returns lat long valus from **Components**, in format latlong.lat and latlong.long
    
    \n.. comments:
    Input:
        Components              list of elements of a single components
    Return:
        latlong:                latlong.lat and latlong.long are lists of lat and long values
    """    
     
    latlong         = K_Component.PolyLine(lat = [], long = [])
    
    for comp in Components:
        latlong.lat.append(comp.lat)
        latlong.long.append(comp.long)
        
    return latlong




def get_Dist2Neighbour(x, y):
    """ Function returning distance between neigbour's elements, with input list of X **x** and Y **y** values.  Return is of type array.
    
    \n.. comments:
    Input:
        x:                   Vector von X-Werten
        y:                   Vector von Y-Werten
    Return:
        Dist:                Vector von Laengen Werten zwischen den Punkten
    """

    # Initializierung von Variabeln
    Dist = arr.array('d')
    
    for ii in list(range(1,len(x) - 1)):
        dx = x[ii] - x[ii - 1]
        dy = y[ii] - y[ii - 1]
        dx = dx * dx
        dy = dy * dy
        Dist.append(math.sqrt(dx + dy))
    
    return Dist




def find_Match_Attrib(Netz_1, CompName_1, AttribName_1, Netz_2, CompName_2, AttribName_2, SearchOption = 'single', 
                      CountryOn = False, AddInWord = 0, String2Lower = False):
    """ Finds a vector containing the positions of which EntsoG component should be linked with which 
    point from Netz class instance. The following attributes are currently implemented: name, lat, 
    and long.  Input to method are **EntsoGCompName**, **Netz** instance, **NetzCompName**, 
    **multDist**, **testRun**, **powerVal**.  Return are the position lists for the EntsoG 
    instance, the Netz instance, and the Goodness value (ranging 0..1).
    
    \n.. comments: 
    Input:
        Netz_1:          Netz Class instance
        CompName_1:      string, of Netz_1 component name, to be used.  
        Netz_2:          instance of class Netz
        CompName_2:      string, of Netz_2 component name, to be used.  
        SearchOption     string indicating if entries from Netz_2 are allowed to be used multiple times,... 'multi', 'single', 
        CountryOn        [False], compares only locations in the same contry
        AddInWord        [0], adds value if name of one set is in name of other set.
        String2Lower     [False], if strings shall be converted to lower
    Return:  
        posEntsoG:       List of ints, of positions from EntsoG  
        posNetz:         List of ints, of positions from Netz  
        GoodnessVal:     list of floats, of goodness values  
    """

    # Selecting the dat based on Component from EntsoG
    Comp_1 = Netz_1.__dict__[CompName_1]
            
    # Selecting the dat based on Component from Netze
    Comp_2   = Netz_2.__dict__[CompName_2]
        
    # Initialization of variables
    pos_1  = []
    pos_2   = []
    GoodnessVal = []
    posLeft_1   = [s for s in range(len(Comp_1))]
    posLeft_2   = [s for s in range(len(Comp_2))]
    
    Run_1  = True
    Run_2    = True
        
    # Dealing with country subset
    if CountryOn:
        Country_1           = M_Helfer.get_NotPos(Comp_1, pos_1, 'country_code')
        Country_2           = M_Helfer.get_NotPos(Comp_2, pos_2, 'country_code')
        Country_Matrix_Orig = M_Helfer.get_NameMatrix_Fuzzy(Country_1, Country_2)
        for xx in range(len(Country_Matrix_Orig)):
            for yy in range(len(Country_Matrix_Orig[0])):
                if Country_Matrix_Orig[xx][yy] >= 100:
                    Country_Matrix_Orig[xx][yy] = 1
                elif Country_1[xx] == None or Country_2[yy] == None:
                    Country_Matrix_Orig[xx][yy] = 1
                else:
                    Country_Matrix_Orig[xx][yy] = 0
    else:
        Country_1           = M_Helfer.get_NotPos(Comp_1, pos_1, 'country_code')
        Country_2           = M_Helfer.get_NotPos(Comp_2, pos_2, 'country_code')
        Country_Matrix_Orig = M_Helfer.get_NameMatrix_Fuzzy(Country_1, Country_2)
        for xx in range(len(Country_Matrix_Orig)):
            for yy in range(len(Country_Matrix_Orig[0])):
                Country_Matrix_Orig[xx][yy] = 1
            
        
    if  String2Lower:
        print('change code')
        
    # Running through data set for first time, to catch all locations, where name is totally same        
    Name_1  = M_Helfer.get_NotPos(Comp_1, pos_1, AttribName_1)
    Name_2  = M_Helfer.get_NotPos(Comp_2, pos_2, AttribName_2)
    
    # Getting matching location names
    [New_pos_1, New_pos_2]  = M_Helfer.get_NameMatch(Name_1, Name_2)

    # Generating un-shrunk data for later
    Orig_Name_1             = M_Helfer.get_NotPos(Comp_1, [], AttribName_1)
    Orig_Name_2             = M_Helfer.get_NotPos(Comp_2, [], AttribName_2)

    Name_Matrix_Orig        = M_Helfer.get_NameMatrix_Fuzzy(Orig_Name_1, Orig_Name_2, AddInWord)
    Name_Matrix_Orig        = M_MatLab.multi_2Matrix(Name_Matrix_Orig, Country_Matrix_Orig)

    # Combining matrixes
    GoodnessMatrix_Orig     = Name_Matrix_Orig
    # Now going through the rest of the data set
    while Run_2 and Run_1:
        GoodnessMatrix_Shrunk       = M_MatLab.shrink_Matrix(GoodnessMatrix_Orig, posLeft_1, posLeft_2)

        # determin popsitions in shrunk data sets
        [pos_Shrunk_1, pos_Shrunk_2]    = M_FindPos.find_pos_ConditionInMatrix(GoodnessMatrix_Shrunk, 'max')
        
        
        GoodnessVal.append(GoodnessMatrix_Shrunk[pos_Shrunk_1][pos_Shrunk_2])
        # dtermin position in original data sets
        pos_Orig_1                   = posLeft_1[pos_Shrunk_1]
        pos_Orig_2                   = posLeft_2[pos_Shrunk_2]
            
        pos_1.append(pos_Orig_1)
        posLeft_1.remove(pos_Orig_1)
        pos_2.append(pos_Orig_2)
        if 'single' in SearchOption:
            posLeft_2.remove(pos_Orig_2)
        
        
        # Check if need to stop 
        if len(pos_1) == len(Comp_1):
            Run_1 = False
        if len(pos_2) == len(Comp_2):
            Run_2 = False
        
    return [pos_1, pos_2, GoodnessVal]
    



def copy_Vals(Netz_2, CompName_2, attribName_2, Netz_1, CompName_1, attribName_1, pos_2, pos_1, check4Val = False):
    """ Finds a vector containing the positions of which EntsoG component should be 
    linked with which point from Netz class instance. The following attributes are 
    currently implemented: name, lat, and long.  Input to method are **Netz_2**, 
    **CompName_2** attribName_2, **Netz_1**, **CompName_1**, **attribName_1**, **pos_2** and **pos_1**.  
    Return is Netz_1 (containing vaues from Netz_2) 
    
    \n.. comments: 
    Input:
        Netz_2:          Netz Class instance
        CompName_2:      string, of Netz_1 component name, to be used. 
        attribName_2     String of the attribute name
        Netz_1:          Netz Class instance
        CompName_1:      string, of Netz_1 component name, to be used. 
        attribName_1     String of the attribute name
        pos_2            list of positions where Netz_2 linked to Nez_1
        pos_1            list of positions where Netz_1 linked to Nez_2
    Return:  
        posEntsoG:       List of ints, of positions from EntsoG  
        posNetz:         List of ints, of positions from Netz  
        GoodnessVal:     list of floats, of goodness values  
    """
    
    if check4Val == False:
        for ii in range(len(pos_2)):
            comp2 = Netz_2.__dict__[CompName_2][pos_2[ii]]
            Netz_1.__dict__[CompName_1][pos_1[ii]].__dict__[attribName_1] = comp2.__dict__[attribName_2]
    else:
        for ii in range(len(pos_2)):
            comp2 = Netz_2.__dict__[CompName_2][pos_2[ii]]
            if comp2 != None:
                Netz_1.__dict__[CompName_1][pos_1[ii]].__dict__[attribName_1] = comp2.__dict__[attribName_2]
        
    
    return Netz_1
    




def copy_ParamVals(Netz_2, CompName_2, attribName_2, Netz_1, CompName_1, attribName_1, pos_2, pos_1, check4Val = False):
    """ Finds a vector containing the positions of which EntsoG component should be 
    linked with which point from Netz class instance. The following attributes are 
    currently implemented: name, lat, and long.  Input to method are **Netz_2**, 
    **CompName_2** attribName_2, **Netz_1**, **CompName_1**, **attribName_1**, **pos_2** and **pos_1**.  
    Return is Netz_1 (containing vaues from Netz_2) 
    
    \n.. comments: 
    Input:
        Netz_2:          Netz Class instance
        CompName_2:      string, of Netz_1 component name, to be used. 
        attribName_2     String of the attribute name
        Netz_1:          Netz Class instance
        CompName_1:      string, of Netz_1 component name, to be used. 
        attribName_1     String of the attribute name
        pos_2            list of positions where Netz_2 linked to Nez_1
        pos_1            list of positions where Netz_1 linked to Nez_2
    Return:  
        posEntsoG:       List of ints, of positions from EntsoG  
        posNetz:         List of ints, of positions from Netz  
        GoodnessVal:     list of floats, of goodness values  
    """
    
    if check4Val == False:
        for ii in range(len(pos_2)):
            comp2 = Netz_2.__dict__[CompName_2][pos_2[ii]]
            Netz_1.__dict__[CompName_1][pos_1[ii]].param[attribName_1] = comp2.param[attribName_2]
    else:
        for ii in range(len(pos_2)):
            comp2 = Netz_2.__dict__[CompName_2][pos_2[ii]]
            if comp2 != None:
                Netz_1.__dict__[CompName_1][pos_1[ii]].param[attribName_1] = comp2.param[attribName_2]
        
    
    return Netz_1
    


def find_MatchNetzPoint(Netz_1, CompName_1, Netz_2, CompName_2, multDist = 1, testRun = False, powerVal = 1):
    """ Finds a vector containing the positions of which EntsoG component should be 
    linked with which point from Netz class instance. The following attributes are 
    currently implemented: name, lat, and long.  Input to method are **EntsoGCompName**, 
    **Netz** instance, **NetzCompName**, **multDist**, **testRun**, **powerVal**.  
    Return are the position lists for the EntsoG instance, the Netz instance, 
    and the Goodness value (ranging 0..1).

    \n.. comments: 
    Input:
        Netz_1:          Netz Class instance
        CompName_1:      string, of Netz_1 component name, to be used.  
        Netz_2:          instance of class Netz
        CompName_2:      string, of Netz_2 component name, to be used.  
        multDist:        (Optional = 1)  
        testRun:         (Optional = False), for:  
                             True  = will NOT carry out the long while loop  
                             False = will carry out the long while loop  
                             []    = will carry out the long while loop  
    Return:  
        posEntsoG:       List of ints, of positions from EntsoG  
        posNetz:         List of ints, of positions from Netz  
        GoodnessVal:     list of floats, of goodness values  
    """
        
    # Selecting the dat based on Component from EntsoG
    Comp_1 = Netz_1.__dict__[CompName_1]
            
    # Selecting the dat based on Component from Netze
    Comp_2   = Netz_2.__dict__[CompName_2]
        
            
    # Initialization of variables
    pos_1  = []
    pos_2   = []
    GoodnessVal = []
    posLeft_1   = [s for s in range(len(Comp_1))]
    posLeft_2   = [s for s in range(len(Comp_2))]
    
    Run_1  = True
    Run_2    = True
        
    # So that Test Runs with shorter time can be executed
    if testRun:
        Run_1  = False
            
    #script_dir  = path.dirname(__file__)
    #logFileName = path.join(script_dir, '../Ausgabe/log_' + str(multDist) + '.csv')
    logFileName = '../Ausgabe/log_' + str(multDist) + '.csv'

        
    Name_Orig_1 = M_Helfer.get_NotPos(Comp_1, pos_1, 'name')
    Name_Orig_2  = M_Helfer.get_NotPos(Comp_2, pos_2,  'name')
    
        
    # Running through data set for first time, to catch all locations, where name is totally same        
    [Name_1, lat_1, long_1]  = M_Helfer.get_NotPos3(Comp_1, pos_1)
    [Name_2, lat_2, long_2]  = M_Helfer.get_NotPos3(Comp_2, pos_2)
    
    # Getting matching location names
    [New_pos_1, New_pos_2]   = M_Helfer.get_NameMatch(Name_1, Name_2)
    
    # Getting 
    Distances       = M_Projection.LatLong2DistanceMatrix(lat_1, long_1, lat_2, long_2)
    InvDistReal2    = M_MatLab.pow_Matrix(Distances, powerVal)
    InvDistReal     = M_MatLab.multi_MatrixConst(InvDistReal2, multDist)
    
        
    # Schreiben von Ergebnissen in eine CSV Datei
    if os.path.isfile(logFileName):
        os.remove(logFileName)
    M_Helfer.txt2File(logFileName, 'EntsoG_Name;Netz_Name;NameSim;Distance;Goodness;EntsoG_pos;Netz_pos')
    for ii in range(len(New_pos_1)):
        # adding new positoins to vec of positions found
        pos_1.append(New_pos_1[ii])
        pos_2.append(New_pos_2[ii])
        GoodnessVal.append(100 - InvDistReal[New_pos_1[ii]][New_pos_2[ii]])
        # removing positions that are found from vector of Pos to be found
        try:
            posLeft_1.remove(New_pos_1[ii])
        except:
            pass
        try:
            posLeft_2.remove(New_pos_2[ii])
        except:
            pass
        
        # writing to log file
        strstr = Name_Orig_1[New_pos_1[ii]] + ';' + \
            Name_Orig_2[New_pos_2[ii]] + ';' + \
            '100;' + \
            str(Distances[New_pos_1[ii]][New_pos_2[ii]]) + ';' + \
            str(100 - InvDistReal[New_pos_1[ii]][New_pos_2[ii]]) + ';' + \
            str(New_pos_1[ii]) + ';' + str(New_pos_2[ii])
        M_Helfer.txt2File(logFileName, strstr)
        
        

    # Generating un-shrunk data for later
    [Orig_Name_1, Orig_lat_1, Orig_long_1]  = M_Helfer.get_NotPos3(Comp_1, [])
    [Orig_Name_2, Orig_lat_2, Orig_long_2]   = M_Helfer.get_NotPos3(Comp_2, [])
            
    # Forming matrixes
    Name_Matrix_Orig          = M_Helfer.get_NameMatrix_Fuzzy(Orig_Name_1, Orig_Name_2)
        
    Dist_Matrix_Orig          = M_Projection.LatLong2DistanceMatrix(Orig_lat_1, Orig_long_1, Orig_lat_2, Orig_long_2)
    Dist_Matrix_Orig2         = M_MatLab.pow_Matrix(Dist_Matrix_Orig, powerVal)
    Dist_Matrix_Orig3         = M_MatLab.multi_MatrixConst(Dist_Matrix_Orig2, multDist)
            
    # Combining matrixes
    GoodnessMatrix_Orig       = M_MatLab.sub_2Matrix(Name_Matrix_Orig, Dist_Matrix_Orig3)

        
    # Now going through the rest of the data set
    while Run_2 and Run_1:

        GoodnessMatrix_Shrunk       = M_MatLab.shrink_Matrix(GoodnessMatrix_Orig, posLeft_1, posLeft_2)
        Name_Matrix_Shrunk          = M_MatLab.shrink_Matrix(Name_Matrix_Orig,    posLeft_1, posLeft_2)
        Dist_Matrix_Shrunk          = M_MatLab.shrink_Matrix(Dist_Matrix_Orig,    posLeft_1, posLeft_2)
            
        # determin popsitions in shrunk data sets
        [pos_Shrunk_1, pos_Shrunk_2]  = M_FindPos.find_pos_ConditionInMatrix(GoodnessMatrix_Shrunk, 'max')
            
        nam                         = Name_Matrix_Shrunk[pos_Shrunk_1][pos_Shrunk_2]
        dis                         = Dist_Matrix_Shrunk[pos_Shrunk_1][pos_Shrunk_2]
            
        GoodnessVal.append(GoodnessMatrix_Shrunk[pos_Shrunk_1][pos_Shrunk_2])
        # dtermin position in original data sets
        pos_Orig_1                   = posLeft_1[pos_Shrunk_1]
        pos_Orig_2                   = posLeft_2[pos_Shrunk_2]
            
        pos_1.append(pos_Orig_1)
        pos_2.append(pos_Orig_2)
            
        posLeft_1.remove(pos_Orig_1)
        posLeft_2.remove(pos_Orig_2)

        # For Log file
        strstr = Name_Orig_1[pos_Orig_1] + ';' + Name_Orig_2[pos_Orig_2] + \
                      ';' + str(nam) + ';' + str(dis) + ';' + \
                      str(GoodnessMatrix_Shrunk[pos_Shrunk_1][pos_Shrunk_2]) + ';' + \
                      str(pos_Orig_1) + ';' + str(pos_Orig_2)
        M_Helfer.txt2File(logFileName, strstr)
            
        # Check if need to stop 
        if len(pos_1) == len(Comp_1):
            Run_1 = False
        if len(pos_2) == len(Comp_2):
            Run_2 = False
                
        
    return pos_1, pos_2, GoodnessVal
    
  
