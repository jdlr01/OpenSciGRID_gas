# -*- coding: utf-8 -*-
"""
M_Test
-------------

Collection of functions, that are being called from other modules, for testing network graphs.
"""
import Code.M_Helfer      as M_Helfer
import Code.M_Graph       as M_Graph
import Code.M_Leitungen   as M_Leitungen
import Code.M_MatLab      as M_MatLab
import Code.M_FindPos     as M_FindPos
import array              as arr
import networkx           as NX


def Test_Main(Info, Graph, Graph_MD, Daten):
    """Main-function of module M_Test, for testing networks.  Input of what to do through config parser **Info**, and data given as type Graph **Netz_Graph**, data as type MultiDiGraph graph **Netz_MDGraph**, and raw data as **Daten**.
    
    \n.. comments:
    Input:
        Info            Info Strukture    
        Netz_Graph      Netz von Klasse Netz (Type Graph())
        Netz_MDGraph    Netz von Klasse Netz (Type MultiDiGraph())
        Daten           Netz Elemente von Klasse MetaData
    Return:
        []
    
    """
    
    Ret = []
            
    if 'AnzahlKnoten' in Info:
        if float(Info['AnzahlKnoten']):
            Ret = Test_NumNodes(Graph_MD)

                
    if 'AnzahlLeitungen' in Info:
        if float(Info['AnzahlLeitungen']):
            Ret = Test_NumSegments(Daten)
            
            
    if 'AnzahlEdges' in Info:
        if float(Info['AnzahlEdges']):
            Ret = Test_NumEdges(Graph_MD)


    if 'EdgesProKnoten' in Info:
        if float(Info['EdgesProKnoten']):
            Ret = Test_EdgesPerNode(Graph_MD)


    if 'Degree' in Info:
        if float(Info['Degree']):
            Ret = Test_Degree(Graph_MD)

                
    if 'Durchmesser' in Info:
        if float(Info['Durchmesser']):
            Ret = Test_Diameter(Graph)


    if 'DurchschnittKuerzesteLaenge' in Info:
        if float(Info['DurchschnittKuerzesteLaenge']):
            Ret = Test_AvgShortLength(Graph)


    if 'GraphenStatistik' in Info:
        if float(Info['GraphenStatistik']):
            Ret = Test_GraphStatistics(Graph_MD)


    if 'DatenIntegritaet' in Info:
        if float(Info['DatenIntegritaet']):
            Ret = Test_DataIntegrity(Daten)

                
    if 'Histogram' in Info:
        if float(Info['Histogram']):
            Ret = Test_Histogram(Graph_MD)

    
    return Ret




def Test_DataIntegrity(Daten):
    """ Function to return feedback on integrety of dataset **Daten** by checking for 
    each component, if component elements have corresponding element in 
    component nodes.  Currently carried out for 'Compressors', 'LNGs', 'BorderPoints', 
    'EntryPoints', 'Storages', and 'InterConnectionPoint' (which are hard coded)
    
    \n.. comments:
    Input:
        Daten       Netz Elemente von Klasse MetaData
    Return:
        ReData: 	list of component elemetns, that are not defined in nodes.
            FehlIntConPunkte
            FehlKompPunkte
            FehlLNGPunkte
            FehlGrenzPunkte
            FehlEinspPunkte
            FehlSpeichPunkte 
		
    """
    NodeIDs                 = M_Helfer.get_attribFromComp(Daten, 'Nodes', 'id')
	
    Compressors             = Daten.Compressors
    LNGs                    = Daten.LNGs
    BorderPoints            = Daten.BorderPoints
    EntryPoints             = Daten.EntryPoints
    Storages                = Daten.Storages
    InterConnectionPoint    = Daten.InterConnectionPoints
    
    
    FehlIntConPunkte      = M_Leitungen.find_missing_points(InterConnectionPoint, "node_id", NodeIDs)
    M_Leitungen.print_missing_points("Die folgenden InterConnectionPoint sind nicht lat/long definiert in Punkte CSV Datei: ", FehlIntConPunkte)
	
    FehlKompPunkte      = M_Leitungen.find_missing_points(Compressors, "node_id", NodeIDs)
    M_Leitungen.print_missing_points("Die folgenden Kompressoren sind nicht lat/long definiert in Punkte CSV Datei: ", FehlKompPunkte)
	
    FehlLNGPunkte       = M_Leitungen.find_missing_points(LNGs, "node_id", NodeIDs)
    M_Leitungen.print_missing_points("Die folgenden LNG-Terminals sind nicht lat/long definiert in Punkte CSV Datei: ", FehlLNGPunkte)
	
    FehlGrenzPunkte     = M_Leitungen.find_missing_points(BorderPoints, "node_id", NodeIDs)
    M_Leitungen.print_missing_points("Die folgenden Grenzpunkte sind nicht lat/long definiert in Punkte CSV Datei: ", FehlGrenzPunkte)
	
    FehlEinspPunkte     = M_Leitungen.find_missing_points(EntryPoints, "node_id", NodeIDs)
    M_Leitungen.print_missing_points("Die folgenden Einspeisepunkte sind nicht lat/long definiert in Punkte CSV Datei: ", FehlEinspPunkte)
	
    FehlSpeichPunkte    = M_Leitungen.find_missing_points(Storages, "node_id", NodeIDs)
    M_Leitungen.print_missing_points("Die folgenden Speicher sind nicht lat/long definiert in Punkte CSV Datei: ", FehlSpeichPunkte)
    
    return [FehlIntConPunkte, FehlKompPunkte, FehlLNGPunkte, FehlGrenzPunkte, FehlEinspPunkte, FehlSpeichPunkte ]




def Test_NumNodes(Graph_MD):
    """ Function to calculate number of nodes for multi-directional graph network **Graph_MD**.
    
    \n.. comments:
    Input:
        Netz        Netz von Klasse Netz
    Return:
        N_Knoten    Variable mit wert Anzahl der Knoten im Netz
        
    """
    N_Knoten = Graph_MD.number_of_nodes()
    
    return N_Knoten




def Test_NumSegments(Daten):
    """ Function to calculate number of segments for dataset **Daten**.
    
    \n.. comments:
    Input:
        Netz            Netz von Klasse Netz
    Return:
        N_Leitungen     Variable mit wert Anzahl der Leitungen
        
    """
    N_Leitungen = len(Daten.PipeSegments)

    return N_Leitungen




def Test_NumEdges(Graph_MD):
    """ Calculate the number of edges for multi-directional graph network **Graph_MD**.
    
    \n.. comments:
    Input:
        Netz        Netz von Klasse Netz
    Return:
        N_Edges     Variable mit Anzahl der Edges
        
    """
    N_Edges  = float(Graph_MD.number_of_edges())

    return N_Edges




def Test_EdgesPerNode(Graph_MD):
    """ Calculate number of edges per node for multi-directional network graph **Graph_MD**.
    
    \n.. comments:
    Input:
        Graph_MD     Instance of multi-directional NZ graph class
    Return:
        KPS         Variable mit Anzahl der Edges pro Knoten
        
    """
    N_Knoten    = float(Graph_MD.number_of_nodes())
    N_Edges     = float(Graph_MD.number_of_edges())
    KPS         = N_Edges / N_Knoten

    return KPS




def Test_Degree(Graph_MD):
    """ Calculate the value degree for the multi-directinal network graph **Graph_MD**.
    
    \n.. comments:
    Input:
        Graph_MD     Instance of multi-directional NX graph class
    Return:
        KPS         Variable mit der des Degrees eines Netzwerkes
        
    """
        
    Degree      = M_Graph.get_Degree(Graph_MD)
    KPS         = float(sum(Degree)) / float(len(Degree))

    return KPS



def Test_Diameter(Graph):
    """ Calculate diameter for the network graph **Graph**.
    
    \n.. comments:
    Input:
        Graph       Instance of NX graph class
    Return:
        KPS         Variable mit dem Durchmessers eines Netzwerkes
        
    """

    Durchmesser = M_Graph.get_Diameter(Graph)
    KPS         = float(sum(Durchmesser)) / float(len(Durchmesser))

    return KPS



def Test_AvgShortLength(Graph):
    """ Calculates the average shortest edge length for the network graph **Graph**.
    
    \n.. comments:
    Input:
        Graph        Instance of NX graph
    Return:
        KPS         Variable mit dem durchschnittlichen kuerzesten Laenge eines Netzwerkes
        
    """
    DurchschnittKuerzesteLaenge_1 = M_Graph.get_AvgShortLength(Graph)
    KPS = float(sum(DurchschnittKuerzesteLaenge_1)) / float(len(DurchschnittKuerzesteLaenge_1))

    return KPS



def Test_GraphStatistics(Graph_MD):
    """ Calculate stats of multi-directinal network graph **Graph_MD**.
    
    \n.. comments:
    Input:
        Graph_MD        Netz von Klasse Netz
    Return:
        GraphStats  Variable mit dem statistischen Wert eines Netzwerkes
        
    """
    # Simulation der Statistiken for jedes Netz
    GraphStats = M_Graph.create_stats(Graph_MD)
    
    return GraphStats




    

def Test_Histogram(Graph_MD):
    """ Returns histrogram for multi-directinal network graph **Graph_MD**.
    
    \n.. comments:
    Input:
        Graph_MD        Instance of NX multi-directinal graph
    Return:
        HistSegmKnoten  Vektor, mit Werten
    
    """
    
    Edges       = NX.edges(Graph_MD)
    KnotenNamen = NX.nodes(Graph_MD)
        
    KnotenNamenListe    = M_Helfer.unique_String(KnotenNamen)
    NumKnotenListe      = len(KnotenNamenListe)
    KnotenLeitung       = arr.array('i', list(range(1, NumKnotenListe+1)))
    
    count = 0
    for Knoten in KnotenLeitung:
        KnotenLeitung[count] = 0
        count = count + 1
        
        
    for ii in list(range(NumKnotenListe)):
        KnotenName  = KnotenNamenListe[ii]
        for edge in Edges:
            posS = edge[0]   == KnotenName
            posE = edge[1]   == KnotenName
            
            if posS :
                KnotenLeitung[ii] = KnotenLeitung[ii] + 1
            if posE:
                KnotenLeitung[ii] = KnotenLeitung[ii] + 1
    
    MaxKnotenLeitung    = max(KnotenLeitung)
    HistSegmKnoten      = M_MatLab.zeros('i', MaxKnotenLeitung+1)
    
    for ii in list(range(0, MaxKnotenLeitung + 1)):
        HistSegmKnoten[ii] = len(M_FindPos.find_pos_ValInVector(ii, KnotenLeitung, '=='))


    return HistSegmKnoten





    