#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 09:22:32 2019

@author: dase_ja
"""

# -*- coding: utf-8 -*-

from __future__        import print_function
import numpy               as np
import Code.K_Netze        as K_Netze
import Code.K_Component    as K_Component
import Code.M_Shape        as M_Shape
import Code.M_MatLab       as M_MatLab
import shapefile
import Code.M_Projection   as M_Projection
from   pathlib         import Path
import os 

C_Code      = 'NO'
ID_Add = C_Code + '_'

def read(NumDataSets = 100000, RelDirName  = 'Eingabe/NO/'):
    """ Reading of Norwegian Petroleum Directorate data sets from Shapefiles, with **RelDirName** indicating which directory to 
	read data from, **NumDataSets** maximum number of records to read. 

    \n.. comments: 
    Input:
        NumDataSets:    	max number of data sets to be read in
                            (Default = 100000) 
        RelDirName:     	string, containing dir name where GasLib  data is found
                            (Default = 'Eingabe/NO/')
    Return:
	    Ret_Data:      Instance of K_Netze.NetComp class, with Nodes and Pipesegments populated."""
    # parse string RelDirPath
    RelDirName                      = Path(RelDirName)
    
    # init object which to be returned
    Ret_Data                        = K_Netze.NetComp()
    
    # read out all pipelines from shapefile
    Ret_Data.PipeLines              = read_component('PipeLines',        NumDataSets, RelDirName = RelDirName)
    # read out all nodes from shapefile
    Ret_Data.Nodes                  = read_component('Nodes',            NumDataSets, RelDirName = RelDirName)
    
    # Converting from PipeLines to PipeSegments
    Ret_Data.PipeLines2PipeSegments()
    Ret_Data.PipeLines      = []
    
    # merge Nodes and Pipesegments
    Ret_Data.merge_Nodes_Comps(compNames = ['PipeSegments', 'Nodes'])
    
    # remove unused Nodes
    Ret_Data.remove_unUsedNodes()
    
    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)
    
   # Adding further essential attributes
    Ret_Data.replace_length(compName = 'PipeSegments')
    Ret_Data.make_Attrib(['PipeSegments'], 'lat',  'lat_mean',    'mean')
    Ret_Data.make_Attrib(['PipeSegments'], 'long',  'long_mean',  'mean')
    Ret_Data.make_Attrib(['Nodes'],        '',      'exact',      'const', 1)
    Ret_Data.make_Attrib(['PipeSegments'], '',      'is_H_gas',   'const', 1)
    Ret_Data.SourceName     = [C_Code]
    
    return Ret_Data
    
def read_component(DataType = '', NumDataSets = 1e+100, RelDirName  = None):
    """ Method of reading in Norway not infield pipelines from shape files. **RelDirName** 
	supplies the relative location of the shape files, whereas **DataType** specifies 
	which component is to be read in with options 'PipeSegments' and 'Nodes'

    \n.. comments: 
    Input:
        DataType 		String, specifying the component to be read in 
						(default = '')
		NumDataSets: 	Number, indicating the maximum number of elements to be read in 
						(default = 1e+100).
        RelDirName:     string, containing the relative path name of where data will be loaded from
                        Default = None
    Return:
        []
    """
    # init variable to return and counter
    ReturnComponent = []
    count       = 0
    
    # start and target 
    inCoord         = 'epsg:4230'
    outCoord        = 'epsg:4326'
    
    # Path to Shapefile
    FileName_Map     = os.path.join(RelDirName,'pipLine.shp')
    
    # Read in shapefile
    Shapes  = shapefile.Reader(FileName_Map)
    
    if DataType in 'PipeLines':
        
        # go through every pipeline stored in shapefile        
        for shape in Shapes.shapeRecords():
            
            # only read out gas pipelines
            if 'Gas' == shape.record[11]:
                
                # Getting the coordinates of the PipeSegment
                parts   = sorted(shape.shape.parts)
                
                # Joining X and Y coordinates from Shape.shape.points
                vec             = shape.shape.points
                polyLine        = K_Component.PolyLine(lat = [], long = [])
                for x,y in vec: 
                    polyLine.long.append(x)
                    polyLine.lat.append(y)
                
                # check if coordinates exists
                if len(polyLine.long) and len(polyLine.lat):  
                    
                    # Converting to LatLong 
                    polyLine = M_Projection.XY2LatLong(polyLine, inCoord, outCoord)            
                    
                    # Generation of PipeLine
                    PipeLine            = M_Shape.PolyLine2PipeLines(polyLine, parts, source = C_Code, country_code = C_Code)
                    for ii in range(len(PipeLine)):
                        PipeLine[ii].id         = 'N_'+str(count)
                        PipeLine[ii].source_id  = [C_Code + '_' + str(count)]
                        PipeLine[ii].name       = shape.record[1]
                        PipeLine[ii].node_id    = ['N_'+str(count * 2), 'N_'+str(count * 2 + 1)]
                        PipeLine[ii].param.update({'lat_mean': M_MatLab.get_mean(PipeLine[ii].lat)[0]})
                        PipeLine[ii].param.update({'long_mean': M_MatLab.get_mean(PipeLine[ii].long)[0]})
                        PipeLine[ii].param.update({'diameter_mm': convInchToMm(shape.record[13])}) # convert inches to mm
                        print(convInchToMm(shape.record[13]))
                        count = count + 1
                    
                ReturnComponent.extend(PipeLine)
                
                if count > NumDataSets:
                    return ReturnComponent
                
                
    elif DataType in 'Nodes':
        
        # go through every pipeline stored in shapefile  
        for shape in Shapes.shapeRecords():
            
            # Only read out nodes of gas pipelines
            if 'Gas' == shape.record[11]:
                # Getting the coordinates of the PipeSegment
                parts   = sorted(shape.shape.parts)
                
                # Joining X and Y coordinates from Shape.shape.points
                vec             = shape.shape.points
                polyLine        = K_Component.PolyLine(lat = [], long = [])
                for x,y in vec: 
                    polyLine.long.append(x)
                    polyLine.lat.append(y)
                
                # check if coordinates exists
                if len(polyLine.long) and len(polyLine.lat): 
                    # Converting to LatLong 
                    polyLine = M_Projection.XY2LatLong(polyLine, inCoord, outCoord)            
                    
                    # Generation of PipeSegments
                    Segments = M_Shape.PolyLine2PipeSegment(polyLine, parts, source = C_Code, country_code = C_Code)
                    
                    # Generation of the Nodes from PipeSegments
                    # two Nodes per PipeSegment
                    for seg in Segments:
                        id          = 'N_'+str(len(ReturnComponent))
                        name        = 'N_'+str(len(ReturnComponent))
                        node_id     = [id]
                        source_id   = [C_Code + '_' + str(len(ReturnComponent))]
                        country_code= C_Code
                        lat         = seg.lat[0]
                        long        = seg.long[0]
                        ReturnComponent.append(K_Component.Nodes(id = id, 
                                        node_id     = node_id, 
                                        name        = name, 
                                        lat         = lat, 
                                        long        = long,
                                        source_id   = source_id, 
                                        country_code = country_code, 
                                        param       = {}))
                        
                        id          = 'N_'+str(len(ReturnComponent))
                        name        = 'N_'+str(len(ReturnComponent))
                        node_id     = [id]
                        source_id   = [C_Code + '_' +str(len(ReturnComponent))]
                        country_code= C_Code
                        lat         = seg.lat[1]
                        long        = seg.long[1]
                        ReturnComponent.append(K_Component.Nodes(id = id, 
                                        node_id     = node_id, 
                                        name        = name, 
                                        lat         = lat, 
                                        long        = long, 
                                        country_code = country_code,
                                        source_id   = source_id, 
                                        param       = {}))
                        
                        count     = count + 1
                
                    # Terminate new data if exceeding user requests
                    if count > NumDataSets:
                        return ReturnComponent
                    
    return ReturnComponent


def replaceString(name_short):
    """Replacement of two strings due to formatting issues.
    """
    name_short       = name_short.replace('Å', 'A')
    name_short       = name_short.replace('å', 'a')
    name_short       = name_short.replace('Ø', 'O')
    name_short       = name_short.replace('ø', 'o')
    name_short       = name_short.replace('Æ', 'A')
    name_short       = name_short.replace('æ', 'A')
    
    return name_short
    
    
def convInchToMm(diameter):
    """Conversion of diameter unit from inches to mm.
    """
    
    diameter = np.round(diameter * 25.4)
    
    return diameter
    
    
    
    
        
                    
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            