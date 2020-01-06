# -*- coding: utf-8 -*-
"""
K_LKD
-----

Collection of the GB class with methods, and components for the GB Data Set.
"""


from __future__        import print_function
import Code.K_Netze        as K_Netze
import Code.K_Component    as K_Component
import Code.M_Shape        as M_Shape
import Code.M_MatLab       as M_MatLab
import Code.M_CSV          as M_CSV
import shapefile
import Code.M_Projection   as M_Projection
from   pathlib         import Path
import os
import urllib3
import certifi

C_Code      = 'GB'
ID_Add      = C_Code + '_'



        
def read(NumDataSets = 100000, RelDirName  = 'Eingabe/GB/'):
    """ Reading of GasLib data sets from XML files, with **RelDirName** indicating which directory to 
	read data from, **NumDataSets** maximum number of records to read. 

    \n.. comments: 
    Input:
        NumDataSets:    	max number of data sets to be read in
                            (Default = 100000) 
        RelDirName:     	string, containing dir name where GasLib  data is found
                            (Default = 'Eingabe/GasLib/')
    Return:
	    Ret_Data:      Instance of K_Netze.NetComp class, with components Nodes and Storages populated."""

    RelDirName                      = Path(RelDirName)

    Ret_Data                        = K_Netze.NetComp()
    # Adding other elements, which come with own lat long
    
    Ret_Data.PipeLines              = read_component('PipeLines',        NumDataSets, RelDirName = RelDirName)
    Ret_Data.Compressors            = read_component('Compressors',      NumDataSets, RelDirName = RelDirName)
    Ret_Data.ConnectionPoints       = read_component('ConnectionPoints', NumDataSets, RelDirName = RelDirName)
    Ret_Data.Nodes                  = read_component('Nodes',            NumDataSets, RelDirName = RelDirName)
    FlowTimeSeries                  = get_timeSeries()
    Ret_Data.all()
    # Converting from PipeLines to PipeSegments
    Ret_Data.PipeLines2PipeSegments()
    Ret_Data.PipeLines      = []
    

    # removing of attribute compressor from Nodes    
    Ret_Data.removeAttrib('Nodes', ['compressor'])
    
    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['Compressors', 'ConnectionPoints', 'PipeSegments', 'Nodes'])
    Ret_Data.remove_unUsedNodes()

    
    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)

    
    # Adding further essential attributess
    Ret_Data.replace_length(compName = 'PipeSegments')
    Ret_Data.make_Attrib(['PipeSegments'], 'lat',  'lat_mean',    'mean')
    Ret_Data.make_Attrib(['PipeSegments'], 'long',  'long_mean',  'mean')
    Ret_Data.make_Attrib(['Nodes'],        '',      'exact',      'const', 1)
    Ret_Data.make_Attrib(['PipeSegments'], '',      'is_H_gas',   'const', 1)




    # Setting additional data in dataset
    Ret_Data.SourceName     = [C_Code]


    return Ret_Data




def read_component(DataType = '', NumDataSets = 1e+100, RelDirName  = None):
    """ Method of reading in Great Britain components from shape files. **RelDirName** 
	supplies the relative location of the shape files, whereas **DataType** specifies 
	which component is to be read in with options 'PipeSegments', 'Nodes', 'Storages', 
	and 'Productions'.

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
   
    ReturnComponent = []
    count           = 0
    
    if DataType in 'PipeLines':
        
        ReturnComponent     = []
        
        # for coordinate projection
        inCoord         = 'epsg:27700'
        outCoord        = 'epsg:4326'
        base            = os.getcwd()
        x               = os.path.join(base,RelDirName)
        FileName_Shape  = os.path.join(RelDirName,'Gas_Pipe.shp')

        # Loading from shape file
        Shapes  = shapefile.Reader(FileName_Shape)
        # Malen der Europa Karte
        count    = 0
        for shape in Shapes.shapeRecords():
            
            if 'N' == shape.record[5]:
                # Getting the coordinates of the PipeSegment
                parts   = sorted(shape.shape.parts)
                # Joining X and Y coordinates from Shape.shape.points
                vec             = shape.shape.points
                polyLine        = K_Component.PolyLine(lat = [], long = [])
                for x,y in vec: 
                    polyLine.long.append(x)
                    polyLine.lat.append(y)
                
                    
                # Converting to LatLong 
                polyLine = M_Projection.XY2LatLong(polyLine, inCoord, outCoord)            
                
                # Generation of PipeLine
                PipeLine            = M_Shape.PolyLine2PipeLines(polyLine, parts, source = C_Code, country_code = C_Code)
                for ii in range(len(PipeLine)):
                    PipeLine[ii].id         = 'N_'+str(count)
                    PipeLine[ii].source_id  = [C_Code + '_' + str(count)]
                    PipeLine[ii].name       = shape.record[1]
                    PipeLine[ii].node_id    = ['N_'+str(count * 2), 'N_'+str(count * 2 + 1)]
                    PipeLine[ii].param.update({'diameter_mm': shape.record[3]})
                    PipeLine[ii].param.update({'length': shape.record[4]})
                    PipeLine[ii].param.update({'lat_mean': M_MatLab.get_mean(PipeLine[ii].lat)[0]})
                    PipeLine[ii].param.update({'long_mean': M_MatLab.get_mean(PipeLine[ii].long)[0]})
                    
                    count = count + 1
                    
                ReturnComponent.extend(PipeLine)
                
                if count > NumDataSets:
                    return ReturnComponent
            
    
    elif DataType in 'Nodes':
        ReturnComponent = []
        
        # for coordinate projection
        inCoord 		= 'epsg:27700'
        outCoord	 	= 'epsg:4326'
        FileName_Shape  = os.path.join(os.getcwd(),RelDirName,'Gas_Pipe.shp')

        # Loading from shape file
        Shapes  = shapefile.Reader(FileName_Shape)
        # Malen der Europa Karte
        count    = 0
        for shape in Shapes.shapeRecords():
            if 'N' == shape.record[5]:
                # Getting the coordinates of the PipeSegment
                parts   = sorted(shape.shape.parts)
                # Joining X and Y coordinates from Shape.shape.points
                vec             = shape.shape.points
                polyLine        = K_Component.PolyLine(lat = [], long = [])
                for x,y in vec: 
                    polyLine.long.append(x)
                    polyLine.lat.append(y)
                    
                # Converting to LatLong 
                polyLine = M_Projection.XY2LatLong(polyLine, inCoord, outCoord)            
                
                # Generation of PipeSegments
                Segments = M_Shape.PolyLine2PipeSegment(polyLine, parts, source = C_Code, country_code = C_Code)
                # Generation of the Nodes from PipeSegments
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
            
            
    elif DataType in 'ConnectionPoints':
        # for coordinate projection
        inCoord 		= 'epsg:27700'
        outCoord	 	= 'epsg:4326'
        FileName_Shape  = os.path.join(os.getcwd(),RelDirName,'Gas_Site.shp')

        # Loading from shape file
        Shapes          = shapefile.Reader(FileName_Shape)
        # Malen der Europa Karte
        countSeg        = 0
        count           = 0
        for shape in Shapes.shapeRecords():
            
            # Getting values from table
            if (str(shape.record[1]) == 'AGI') or (str(shape.record[1]) == 'TCSITE'):
                # Getting the coordinates of the PipeSegment
                [X_coor, Y_coor]    = M_Shape.polyShape2PipeSegment(shape.shape, 'mean')

                polyLine            = K_Component.PolyLine(lat = [], long = [])
                polyLine.long.append(X_coor)
                polyLine.lat.append(Y_coor)
                
                # Converting to LatLong 
                polyLine = M_Projection.XY2LatLong(polyLine, inCoord, outCoord)                            



                id              = 'N_'+str(count)
                source_id       = [ID_Add + str(id)]
                node_id         = [id]
                name            = str(shape.record[2])
                license         = None
                country_code    = C_Code

                # Writing of start point
                ReturnComponent.append(K_Component.ConnectionPoints(id = id, 
                                name        = name, 
                                source_id   = source_id, 
                                node_id     = node_id, 
                                long        = polyLine.long[0], 
                                lat         = polyLine.lat[0],  
                                country_code = country_code,
                                param       = {'license'   : license}))
                
                count    = count + 1
                countSeg = countSeg + 1

                if count > NumDataSets:
                    return ReturnComponent    
    
    elif DataType in 'Compressors':
        # for coordinate projection
        inCoord 		= 'epsg:27700'
        outCoord	 	= 'epsg:4326'
        FileName_Shape  = os.path.join(os.getcwd(),RelDirName,'Gas_Site.shp')

        # Loading from shape file
        Shapes  = shapefile.Reader(FileName_Shape)
        # Malen der Europa Karte
        countSeg = 0
        count = 0
        for shape in Shapes.shapeRecords():
            
            # Getting values from table
            if str(shape.record[1]) == 'COMP':
                # Getting the coordinates of the PipeSegment
                [X_coor, Y_coor] = M_Shape.polyShape2PipeSegment(shape.shape, 'mean')
                
                polyLine        = K_Component.PolyLine(lat = [], long = [])
                polyLine.long.append(X_coor)
                polyLine.lat.append(Y_coor)
                
                # Converting to LatLong 
                polyLine = M_Projection.XY2LatLong(polyLine, inCoord, outCoord)                            
                
                
                id              = 'N_'+str(count)
                source_id       = [ID_Add + str(id)]
                node_id         = ['N_'+id]
                name            = str(shape.record[2])
                license         = None
                country_code    = C_Code

                # Writing of start point
                ReturnComponent.append(K_Component.Compressors(id = id, 
                                node_id     = node_id, 
                                name        = name, 
                                source_id   = source_id, 
                                long        = polyLine.long[0], 
                                lat         = polyLine.lat[0], 
                                country_code = country_code,
                                param       = {'license'   : license}))
                
                count    = count + 1
                countSeg = countSeg + 1

                if count > NumDataSets:
                    return ReturnComponent
    
    return ReturnComponent




def gen_component(dataType, NodesIn):
    """ Generates a Netz component from existing components of this Netz, e.g. 
	generation of of Nodes list from Segments.  Needs list of elements of component via  
	**NodesIn**.  Component name to be generated supplied as string 
	**dataType**, with current options implemented *Compressors*

    \n.. comments:
    Input:
        dataType:        string containing name of component to be created e.g. 'Compressors' 
        NodesIn:     	 list of elements of a component
    Return:
        ReturnComponent: component list.  
    """
    
    ReturnComponent = []
    
    
    if dataType in 'Compressors':
        for seg in NodesIn:
            if float(seg.comp_units):
                if seg.comp_units > 0:
                    id              = str(seg.id)
                    node_id         = str(seg.id)
                    name            = seg.name
                    lat             = seg.lat
                    long            = seg.long
                    country_code    = seg.country_code
                    operator_name   = seg.param['operator']
                    license         = seg.param['license']
                    num_turb        = seg.param['comp_units']
                    entsog_key      = seg.param['entsog_key']
                    entsog_nam      = seg.param['entsog_nam']
                    max_power_MW    = None

                    ReturnComponent.append(K_Component.Compressors(id = id, 
                                        name        = name,  
                                        country_code = country_code, 
                                        param       = {'max_power_MW' : max_power_MW, 
                                        'node_id'   : node_id, 
                                        'operator_name' : operator_name, 
                                        'num_turb'  : num_turb, 
                                        'entsog_key': entsog_key, 
                                        'entsog_nam': entsog_nam,
                                        'lat'       : lat, 
                                        'long'      : long, 
                                        'license'   : license}))
    
            elif ((len(seg.compressor) > 0) and 
                      ('Regelanlage' not in seg.compressor) and 
                      ('NULL' not in seg.compressor)):
                id              = str(seg.id)
                node_id         = str(seg.id)
                name            = seg.name
                lat             = seg.lat
                long            = seg.long
                country_code    = seg.country_code

                operator_name   = seg.param['operator']
                license         = seg.param['license']
                num_turb        = seg.param['comp_units']
                entsog_key      = seg.param['entsog_key']
                entsog_nam      = seg.param['entsog_nam']
                max_power_MW    = None
                
                ReturnComponent.append(K_Component.Compressors(id = id, 
                                    name        = name,  
                                    country_code = country_code, 
                                    param       = {'max_power_MW' : max_power_MW, 
                                    'node_id'   : node_id, 
                                    'operator_name' : operator_name, 
                                    'num_turb'  : num_turb, 
                                    'entsog_key': entsog_key, 
                                    'entsog_nam': entsog_nam,
                                    'lat'       : lat, 
                                    'long'      : long, 
                                    'license'   : license}))
        
    return ReturnComponent


            
def get_timeSeries():
    Limit 		    = 10000    
    URL 			= 'https://transparency.entsog.eu/api/v1/interconnections'
    # Creation of a Pool Manager
    http            = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
        
    # Get the data
    URLData         = http.request('GET', URL + '?limit=' + str(Limit))
            
    
    'https://mip-prod-web.azurewebsites.net/UserDefinedFileDownload/DownloadFile?inclusiveStartDate=2019-11-01&inclusiveEndDate=2019-11-12&UserDefinedDownloadTimeQueryType=CustomDates&inclusiveStartDate=01-Nov-19&inclusiveEndDate=12-Nov-19&LatestPublishedOriginallyPublished=OriginalPublished&SelectedLocationClassificationIds=527&UserDefinedDownloadRadioSelection=None'
    
