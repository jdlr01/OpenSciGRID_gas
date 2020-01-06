# -*- coding: utf-8 -*-
"""
M_Leitungen
-----------

Collection of functions, that are being called from other modules, for actions on pipelines.
"""

import Code.K_Netze      as K_Netze
import Code.M_FindPos    as M_FindPos
import sys




def find_missing_points(Punkte1, FeldName, Punkte2):
    """ Function returning points that are in data set **Punkte1** but not in **Punkte2**.  
    The attribute label that is being used to compare the to data sets is given through **FeldName**.

    \n.. comments: 
    Input:
        Punkte1:        List of points (first data set)
        FeldName:       String, which is link between the two data sets. Currently only "name" implemented
        Punkte2:         List of points (second data set)
    Return:
        FehlendePunkte:  List von String von (Punkte.name).
    """

    # Initializierung von Variabeln
    FehlendePunkte = []
    if FeldName.lower() == "name":
        for punke in Punkte1:
            pos = M_FindPos.find_pos_StringInList(punke.name, Punkte2)
            if len(pos) == 0:
                FehlendePunkte.append(punke.name)
    elif FeldName.lower() == "node_id":
        for punke in Punkte1:
            pos =  M_FindPos.find_pos_StringInList(punke.node_id, Punkte2)
            if len(pos) == 0:
                FehlendePunkte.append(punke.node_id)
    else:
        print('ERROR: ' + sys.argv[0] + '.find_missing_points: code not written yet!')
        raise 
    
    return FehlendePunkte    
    

    

def print_missing_points(HelperString, PunkteNamen):
    """ Function to print to screen points supplied through **PunkteNamen**.  
    **HelperString** is string that is printed to scene before point information once.
	
    \n.. comments: 
    Input:
        HelperString       String, der Print Befehl einleitet.
        PunkteNamen        List von Strings  
	Return:
        []
    """

    # Initializierung von Variabeln

    if len(PunkteNamen) > 0:
        print(HelperString)
        for punktName in PunkteNamen:
            print(r""" "{0}" """.format(punktName))
    
    return []
    
    