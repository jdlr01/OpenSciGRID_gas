# -*- coding: utf-8 -*-
"""
M_Graph
-------
Modules for graphs, using the networkx module

"""

import networkx              as NX
import Code.M_FindPos        as M_FindPos
import Code.K_Netze          as K_Netze
import Code.M_DataAnalysis   as M_DataAnalysis
import Code.K_Component      as K_Component
# import igraph                as iGraph
import array 			     as arr
import copy




def build_nx(InfoDict = '', Daten = '', Method = 'Gleich', removeExtraNodes = False):
    """ Creation of a network using the external module networkx, by supplying 
	instance of  NetComp network via **Data**, and the method implemented can 
	be selected through the config-parser **InfoDict** or the string **Method**.  
	Function  returns two different types of networks, one networkx.Graph() and 
	one networkx.MultiDiGraph().
    
    \n.. comments:
    Input:
        InfoDict    	Info Dictionary, with element "Gewichtung", and current implemented setting is:
                        - 'Gleich'
        Daten       	NetComp instance with components "PipeSegments"
        Method:     	in case that method on how to create graph not supplied through InfoDict, then 
						it can be supplied via this string Method, with current option  implemented:
                        - 'Gleich'
    Return:
        NetGraph            An instance of the networks graph for the input data set, being of type networkx.Graph()
        NetGraphMultiDir    An instance of the networks graph, which can contain multi-directional information, being of type networkx.MultiDiGraph()
    """

    # Initializierung von Variabeln
    Netz_Graph           = NX.Graph()
    Netz_MultiDiGraph    = NX.MultiDiGraph()
    Netz_MultiDiGraph    = NX.MultiGraph()
    
    #Netz_iGraph          = iGraph.Graph()

    # checking that info given as PipeSegments, and not as PipeLines, otherwise convert
    if (len(Daten.PipeSegments) == 0) and (len(Daten.PipeLines) >0):
        Daten.PipeLines2PipeSegments()


    # Fuellen des Graphens G
    if len(InfoDict) > 0:
        for pipeLine in Daten.PipeSegments:
            if InfoDict['Weight'] == 'Gleich':
                weight = 1
            elif InfoDict['Weight'] == 'length_km':
                weight = pipeLine.param['length']
            elif InfoDict['Weight'] == 'latLongNodes':
                weight = M_DataAnalysis.distance(pipeLine.long[0], pipeLine.lat[0], pipeLine.long[-1], pipeLine.lat[-1])
            else:
                print('ERROR: M_Graph.build_nx(): Code not written')

            # NX.Graph
            Netz_Graph.add_node(pipeLine.node_id[0], **{'pos':(pipeLine.long[0],  pipeLine.lat[0]), 'id':pipeLine.node_id[0], 'country_code':pipeLine.country_code[0]})
            Netz_Graph.add_node(pipeLine.node_id[1], **{'pos':(pipeLine.long[-1], pipeLine.lat[-1]), 'id':pipeLine.node_id[1], 'country_code':pipeLine.country_code[1]})
            Netz_Graph.add_edge(pipeLine.node_id[0], pipeLine.node_id[1],        weight = 1, **{'id': pipeLine.id, 'param': pipeLine.param, 'country_code':pipeLine.country_code})
            
            # NX.MultiDiGraph
            Netz_MultiDiGraph.add_node(pipeLine.node_id[0], **{'pos':(pipeLine.long[0],  pipeLine.lat[0]), 'id':pipeLine.node_id[0], 'country_code':pipeLine.country_code[0]})
            Netz_MultiDiGraph.add_node(pipeLine.node_id[1], **{'pos':(pipeLine.long[-1], pipeLine.lat[-1]), 'id':pipeLine.node_id[1], 'country_code':pipeLine.country_code[1]})
            Netz_MultiDiGraph.add_edge(pipeLine.node_id[0], pipeLine.node_id[1], weight = 1, **{'id': pipeLine.id, 'param': pipeLine.param, 'country_code':pipeLine.country_code})

    else:
        for pipeLine in Daten.PipeSegments:
            if Method == 'Gleich':
                weight = 1
            elif Method == 'length_km':
                weight = pipeLine.param['length']
            elif Method == 'latLongNodes':
                weight  = M_DataAnalysis.distance(pipeLine.long[0], pipeLine.lat[0], pipeLine.long[-1], pipeLine.lat[-1])
            else:
                print('ERROR: M_Graph.build_nx(): Code not written')

            # NX.Graph
            Netz_Graph.add_node(pipeLine.node_id[0], **{'pos':(pipeLine.long[0],  pipeLine.lat[0]), 'id':[pipeLine.node_id[0]],  'country_code':pipeLine.country_code[0], 'param': pipeLine.param})
            Netz_Graph.add_node(pipeLine.node_id[1], **{'pos':(pipeLine.long[-1], pipeLine.lat[-1]), 'id':[pipeLine.node_id[1]], 'country_code':pipeLine.country_code[1], 'param': pipeLine.param})
            Netz_Graph.add_edge(pipeLine.node_id[0], pipeLine.node_id[1],  **{'weight':weight, 'country_code':pipeLine.country_code, 'id': [pipeLine.id], 'param': pipeLine.param})
            
            # NX.MultiDiGraph
            Netz_MultiDiGraph.add_node(pipeLine.node_id[0], **{'pos':(pipeLine.long[0],  pipeLine.lat[0]), 'id':[pipeLine.node_id[0]],  'country_code':pipeLine.country_code[0], 'param': pipeLine.param})
            Netz_MultiDiGraph.add_node(pipeLine.node_id[1], **{'pos':(pipeLine.long[-1], pipeLine.lat[-1]), 'id':[pipeLine.node_id[1]], 'country_code':pipeLine.country_code[1], 'param': pipeLine.param})
            Netz_MultiDiGraph.add_edge(pipeLine.node_id[0], pipeLine.node_id[1], **{'id': [pipeLine.id], 'country_code':pipeLine.country_code, 'weight': weight, 'param': pipeLine.param})


    # removed nodes that have no edges leading to it
    if removeExtraNodes == True:
        # Netz_Graph
        to_remove   = []
        outdeg      = dict(Netz_Graph.degree)
        for idx in range(len([*outdeg])):
            keyval = [*outdeg][idx]
            if outdeg[keyval] == 0:
                to_remove.append(keyval)
        Netz_Graph.remove_nodes_from(to_remove)
                
        to_remove   = []
        outdeg      = dict(Netz_MultiDiGraph.degree)
        for idx in range(len([*outdeg])):
            keyval = [*outdeg][idx]
            if outdeg[keyval] == 0:
                to_remove.append(keyval)
        Netz_MultiDiGraph.remove_nodes_from(to_remove)
        
        
    return [Netz_Graph, Netz_MultiDiGraph]




def getAttrib(Gnode, paramStr, paraDefault = []):
    """Check that key in dict and return attribute value, otherwise return 
    **paraDefault** ( = [])"""
    
    if paramStr in Gnode:
        param = Gnode[paramStr]
    else:
        param = paraDefault
        
    return param




def Graph2Netz(G_Set_Sum):
    """ Creation of a Netz from a networkx network 
    
    \n.. comments:
    Input:
        G_Set_Sum   Network of type networkx
    Return:
        G_Netz      Netz of type K_Netze.NetComp
    """
    
    G_Netz      = K_Netze.NetComp()
    Pipe        = []
    Nodes       = []
    
    for node in G_Set_Sum.nodes():
        id              = G_Set_Sum.node[node]['id'][0]
        lat             = G_Set_Sum.node[node]['pos'][1]
        long            = G_Set_Sum.node[node]['pos'][0]
        country_code    = getAttrib(G_Set_Sum.node[node], 'country_code')
        param           = getAttrib(G_Set_Sum.node[node], 'param',        'param')
        source_id       = getAttrib(G_Set_Sum.node[node], 'source_id',    id)
        node_id         = getAttrib(G_Set_Sum.node[node], 'node_id',      id)
        name            = getAttrib(G_Set_Sum.node[node], 'name',         id)
        
        Nodes.append(K_Component.Nodes(id = id, name = name,  source_id = source_id,  node_id = node_id ,  
                    long = long, lat = lat, country_code = country_code, param = param))
        
    G_Netz.Nodes = Nodes


    for edge in G_Set_Sum.edges():
        for xx in range(len(G_Set_Sum[edge[0]][edge[1]])):
            id              = G_Set_Sum[edge[0]][edge[1]][xx]['id'][0]
            latS            = G_Set_Sum.node[edge[0]]['pos'][1]
            longS           = G_Set_Sum.node[edge[0]]['pos'][0]
            latE            = G_Set_Sum.node[edge[1]]['pos'][1]
            longE           = G_Set_Sum.node[edge[1]]['pos'][0]

            country_codeS   = G_Set_Sum.node[edge[0]]['country_code']
            country_codeE   = G_Set_Sum.node[edge[1]]['country_code']
            param           = getAttrib(G_Set_Sum[edge[0]][edge[1]][xx], 'param',        'param')
            source_id       = getAttrib(G_Set_Sum[edge[0]][edge[1]][xx], 'source_id',    id)
            node_id         = [str(edge[0]), str(edge[1])]
            name            = getAttrib(G_Set_Sum[edge[0]][edge[1]][xx], 'name',         id)
            
            Pipe.append(K_Component.PipeSegments(id = id, 
                        name        = name,  
                        source_id   = source_id, 
                        node_id     = node_id, 
                        long        = [longS, longE], 
                        lat         = [latS, latE], 
                        country_code = [country_codeS, country_codeE]))
    
    G_Netz.PipeSegments = Pipe

    return G_Netz 



    
def get_AvgShortLength(Netz):
    """ Function returning the average shorted pipeline length of a network **Netz**.
    
    \n.. comments:
    Input:
        Netz:       Netz instance
    Return:
        ReturnVal:   Vector of length of the network
    """
    
    # Initializierung von Variabeln
    # Formenen einenes Graphens G
    ReturnVal = []
    count = 0
    
    
    # Errrechnung vom average_shortest_path_length
    try:
        for g in NX.connected_component_subgraphs(Netz):
            ReturnVal.append(NX.average_shortest_path_length(g))
            count = count + 1
    except:
        print('{}{}'.format('ERROR: M_Graph.get_AvgShortLength: in Graph Element: ', count))
        raise 
    
    return ReturnVal    
    
    


def get_Diameter(Graph):
    """ Returns the diameter of the network graph **Graph**.
    
    \n.. comments:
    Input:
        Graph:       Instance of NX network graph
    Return:
        ReturnVal:   Vector of length of the network
    """
    
    # Initializierung von Variabeln
    ReturnVal = []
    
    # Errechnen des Durchmessers    
    count = 0
    try:
        for g in NX.connected_component_subgraphs(Graph):
            ReturnVal.append(NX.diameter(g))
            count = count + 1
    except:
        print('{}{}'.format('ERROR: M_Graph.get_Diameter: in Edge nummer ', count))
        raise 
    
    return ReturnVal    
    


    
def get_Degree(Graph_MD):
    """ Returning degrees as type array from multi-directional network graph **Graph_MD**. 	
	
    \n.. comments:
    Input:
        Graph_MD     Instance of NX multi-directional graph
    Return:
        ReturnVal:   The degree of the network
    """

    AllEdges    = NX.edges(Graph_MD)
    Punkte      = NX.nodes(Graph_MD)

    # Initializierung von Variabeln
    Degree      = arr.array('i', list(range(len(Punkte))))
    count       = 0
    
    for Punkt in Punkte:
        pos             = M_FindPos.find_pos_StringInTuple(Punkt, AllEdges)
        Degree[count]   = len(pos)
        count           = count + 1
    
    return  Degree

    


def create_stats(Graph_MD):
    """ Returning stats values for input **Graph_MD** of type networks. 
	Stats are: 
	- number of graphs, 
	- number of unconnected graphs, 
	- number of nodes per graph, 
	- number of edges per graph, 
	- number of unconnected nodes. 

    \n.. comments:
    Input:
        Graph_MD:           instance of a networkx Graph 
    Return:
        StatsValues         Variables of type NetzKlassen.StatsValue() with values.
    """    

    # Initializierung von Variabeln
    StatsValues = K_Netze.StatsValue()
    
    # Erstellugn von Variabeln
    tot_num_nodes = Graph_MD.number_of_nodes()
    num_nodes       = 0
    num_edges       = 0
    tot_length      = 0
    num_graphen     = 0                             # number of graphs
    num_dg          = 0
    num_dg_nodes    = 0
    countE          = 0
    count           = 0
    try:
        if Graph_MD.is_multigraph():
            num_graphen = 2
        else:
            num_graphen = 1
        num_nodes   = num_nodes + Graph_MD.number_of_nodes()       # number of nodes
        num_edges   = num_edges + Graph_MD.number_of_edges()       # number of edges
        num_dg      = num_graphen - 1                       # number of disconnected graphs
        tot_length  = tot_length + Graph_MD.size(weight='weight')
        countE      = countE + 1
        count       = count + 1
        num_dg_nodes = tot_num_nodes - num_nodes                 # total number of disconnected graphs nodes
    except:
        print('{}'.format('ERROR: M_Graph.create_stats: im ersten Segment'))
        raise 
        

    print("num_graphen:  {0}".format(num_graphen))
    print("num_dg:       {0}".format(num_dg))
    print("num_nodes:    {0}".format(num_nodes))
    print("num_edges:    {0}".format(num_edges))
    print("num_dg_nodes: {0}".format(num_dg_nodes))
    print("tot_length:   {0}".format(tot_length))
    StatsValues.num_Graphen     = num_graphen
    StatsValues.num_disGraphen  = num_dg
    StatsValues.num_Knoten      = num_nodes/num_graphen
    StatsValues.num_Kanten      = num_edges/num_graphen
    StatsValues.num_disKnoten   = num_dg_nodes
    StatsValues.summe_Kanten    = tot_length
    StatsValues.durchschnitt_KantenLaenge   = tot_length/num_edges

    return StatsValues
    
    


def get_shortest_paths_distances(graph, pair, edge_weight_name = 'length_km'):
    """Compute shortest distance between each pair of nodes in a graph.  
    Return a dictionary keyed on node pairs (tuples)."""
    
    distances = NX.dijkstra_path_length(graph, pair[0], pair[1], weight = edge_weight_name)
    
    return distances    


	

def get_shortest_paths_distances_2(graph, pair, edge_weight_name = 'length_km'):
    """Compute shortest distance between each pair of nodes in a graph.  
    Return a dictionary keyed on node pairs (tuples)."""
    
    distances   = 0
    Path        = NX.shortest_path(graph, pair[0], pair[1], weight = edge_weight_name)
    
    for ii in range(len(Path)-1):
        edge        = graph.get_edge_data(Path[ii], Path[ii+1])['weight']
        distances   = distances + edge
        
    return distances




def redNodes(Graph, nodeIDs):
    """Reduces the network **Graph** of type networkx and only keeps those edges and nodes, 
    that are (connected) to nodes with id **nodeID**.  Hence will only contain
    those edges, that start and finish at nodes that are in output network.
    
    
    \n.. comments: 
    Input:
        Graph:      Network of type networkx
        nodeID:     list of IDs of nodes.
    Return:
        RetGraph:   Network of type neworkx, only containing nodes as selected and 
                    those edges, that are running between those nodes.
    """

    RetGraph        = copy.deepcopy(Graph)
    allIds          = NX.nodes(Graph)
    for nodeID in allIds:
        if nodeID in nodeIDs:
            pass
        else:
            RetGraph.remove_node(nodeID)

    return RetGraph