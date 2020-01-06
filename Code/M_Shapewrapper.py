#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 14:44:29 2019

@author: apluta
"""
import Code.M_CSV       as M_CSV
import Code.M_Shape     as M_Shape
import os


write2File  = False

def wrapperShape(Ret_Data, mergePipeEndPoints = 0.0, connectPipesTop = 0, lonePipeEnd2PipePoly = 0.0, 
                 moveComp2Node = 0.0, moveComp2Pipe = 0.0, shrinkPipeLine = 0.0, remCulDeSac = 0, excepCulDeSac = []):
    """This is the wrapper for the spatial modification of the network elements:
    Netzwork **Ret_Data** , merking pipe points if they are close enough **mergePipeEndPoints**, 
    connecting pipes **lonePipeEnd2PipePoly**, moving components onto nodes of Pipes **moveComp2Node**, 
    moving components onto pipes (polypipe) **moveComp2Pipe**, 
    reducing Pipes to start and end lat long **shrinkPipeLine**, and
    removing Pipes that are connected only on one side **remCulDeSac**.
    
    \n.. comments: 
    Input:    
        Ret_Data:           Instance of a network class.
		mergePipeEndPoints  Function to merge PipeLine/Segments that are close to each other to one point
							(Default = 0.0)
		lonePipeEnd2PipePoly: 		Function to connect PipeLines/Segments
							(Default = 0.0)
		moveComp2Node:  	Function to move components (e.g. compressors) to  a Node.
							(Default = 0.0)
		moveComp2Pipe: 		Function to move components (e.g. compressors) to  a PipeLine/Segment, but works best if PipeLine/Segment is polyline.
							(Default = 0.0)
		shrinkPipeLine:		Function to reduce PipeLines/Segments to start/end latlong pair only (remove polypoints in-between start and end)
							(Default = 0.0)
        remCulDeSac         remove cul de sacs, with length shorter than this value, 
                            (Default = 0)
        excepCulDeSac:      List of ids of cul de sacs not to be removed
                            (Degfault = [])
    Output:
            Ret_Data        instance of netz structure
    """


    ####################################################################    
    ### Remove Sackgassen (Cul de sac), pipeLines/Segments that are connected
    ### only on one side
    ####################################################################    
    if len(Ret_Data.PipeLines) > 0 and remCulDeSac > 0.0:
        Ret_Data            = remCulDeSac(Ret_Data, 'PipeLines', remCulDeSac = remCulDeSac, excepCulDeSac = excepCulDeSac)
        # Creating Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
#        Ret_Data.Nodes      = Ret_Data.add_Nodes('PipeLines', [])
#        Ret_Data.Nodes      = M_Shape.reduceElement(Ret_Data.Nodes, reduceType = 'LatLong')
        
    elif len(Ret_Data.PipeSegments) > 0 and remCulDeSac > 0.0:
        Ret_Data            = remCulDeSac(Ret_Data, 'PipeSegments', remCulDeSac = remCulDeSac, excepCulDeSac  = excepCulDeSac)
        # Creating Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
#        Ret_Data.Nodes      = Ret_Data.add_Nodes('PipeSegments', [])
#        Ret_Data.Nodes      = M_Shape.reduceElement(Ret_Data.Nodes, reduceType = 'LatLong')
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/1_Sackgassen/')
            M_CSV.write(dirpath, Ret_Data)



    ####################################################################    
    ### Move PipeLine/Segments endpoints on same latlong if close together
    ####################################################################    
    if mergePipeEndPoints > 0.0 and len(Ret_Data.PipeLines) > 0:
        Ret_Data            = M_Shape.mergePipeEndPoints(Ret_Data, 'PipeLines', maxDistance = mergePipeEndPoints)
        # Creating Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        
    elif mergePipeEndPoints > 0.0 and len(Ret_Data.PipeSegments) > 0:
        Ret_Data            = M_Shape.mergePipeEndPoints(Ret_Data, 'PipeSegments', maxDistance = mergePipeEndPoints)
        # Creating Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/2_endpoints/')
            M_CSV.write(dirpath, Ret_Data)
        

    
    
    ####################################################################    
    ### Connecting PipeLines/Segments of end beding on top of other pipeSegments
    ####################################################################    
    if connectPipesTop > 0.0 and len(Ret_Data.PipeLines) > 0:
        # move pipe endpoints onto pipeline
        Ret_Data            = connectPipesTop(Ret_Data, 'PipeLines')
        # Add nodes where PipeLines are
        Ret_Data.cleanUpNodes(skipNodes = True)
        
    elif connectPipesTop > 0.0 and len(Ret_Data.PipeSegments) > 0:
        # move pipe endpoints onto pipeline
        Ret_Data            = connectPipesTop(Ret_Data, 'PipeSegments')
        # Add nodes where PipeSegments are
        Ret_Data.cleanUpNodes(skipNodes = True)
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/3_Connecting/')
            M_CSV.write(dirpath, Ret_Data)
    
    
    
    ####################################################################    
    ### Connecting PipeLines/Segments
    ####################################################################    
    if lonePipeEnd2PipePoly > 0.0 and len(Ret_Data.PipeLines) > 0:
        # move pipe endpoints onto pipeline
        Ret_Data            = lonePipeEnd2PipePoly(Ret_Data, 'PipeLines', maxDistance = lonePipeEnd2PipePoly)
        # Add nodes where PipeLines are
        Ret_Data.cleanUpNodes(skipNodes = True)
        
    elif lonePipeEnd2PipePoly > 0.0 and len(Ret_Data.PipeSegments) > 0:
        # move pipe endpoints onto pipeline
        Ret_Data            = lonePipeEnd2PipePoly(Ret_Data, 'PipeSegments', maxDistance = lonePipeEnd2PipePoly)
        # Add nodes where PipeSegments are
        Ret_Data.cleanUpNodes(skipNodes = True)
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/3_Connecting/')
            M_CSV.write(dirpath, Ret_Data)
        

   
    ####################################################################    
    ### Moving components onto Nodes of PipeLines/Segments
    ####################################################################    
    if  moveComp2Node > 0.0 and len(Ret_Data.ConnectionPoints) > 0 and len(Ret_Data.PipeLines) > 0:
        for compName in Ret_Data.CompLabelsSpot():
            # Connection Points
            Ret_Data        = moveComp2Node(Ret_Data, compName, maxDistance = moveComp2Node)
            Ret_Data.Nodes  = Ret_Data.add_Nodes('PipeLines', [])
        
        # Creation of unique Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        
    elif  moveComp2Node > 0.0 and len(Ret_Data.ConnectionPoints) > 0 and len(Ret_Data.PipeSegments) > 0:
        for compName in Ret_Data.CompLabelsSpot():
            Ret_Data        = moveComp2Node(Ret_Data, compName, maxDistance = moveComp2Node)
            Ret_Data.Nodes  = Ret_Data.add_Nodes('PipeSegments', [])
        
        # Creation of unique Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/4_Moving_2_Nodes/')
            M_CSV.write(dirpath, Ret_Data)
        

    ####################################################################    
    ### Moving components onto PipeLines/Segments
    ####################################################################    
    if  moveComp2Pipe > 0.0 and  len(Ret_Data.PipeLines) > 0:   # len(Ret_Data.ConnectionPoints) > 0 and
        for compName in Ret_Data.CompLabelsSpot():
            Ret_Data        = M_Shape.moveComp2Pipe(Ret_Data, compName, 'PipeLines', maxDistance = moveComp2Pipe)
            Ret_Data.Nodes  = Ret_Data.add_Nodes('PipeLines', [])
        
        # Creation of unique Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        
    elif  moveComp2Pipe > 0.0 and len(Ret_Data.PipeSegments) > 0:  # len(Ret_Data.ConnectionPoints) > 0 and 
        for compName in Ret_Data.CompLabelsSpot():
            Ret_Data        = M_Shape.moveComp2Pipe(Ret_Data, compName, 'PipeSegments', maxDistance = moveComp2Pipe)
            Ret_Data.Nodes  = Ret_Data.add_Nodes('PipeSegments', [])
        
        # Creation of unique Nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/5_Moving_2_Pipes/')
            M_CSV.write(dirpath, Ret_Data)
            

        
    ####################################################################    
    ### Shrinking of PipeLines/Segments
    ####################################################################    
    if shrinkPipeLine > 0 and len(Ret_Data.PipeLines) > 0:
        # Removing LatLongs from PipeLine that re not Nodes
        Ret_Data        = M_Shape.shrinkPipes(Ret_Data, 'PipeLines')
        # Reduce nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
    elif shrinkPipeLine > 0 and len(Ret_Data.PipeSegments) > 0:
        # Removing LatLongs from PipeLine that re not Nodes
        Ret_Data        = M_Shape.shrinkPipes(Ret_Data, 'PipeSegments')
        # Reduce nodes
        Ret_Data.cleanUpNodes(skipNodes = True)
        if write2File:
            dirpath=os.path.join(os.getcwd(),'Ausgabe/GB/6_Shrinking/')
            M_CSV.write(dirpath, Ret_Data)
            
    
    return Ret_Data