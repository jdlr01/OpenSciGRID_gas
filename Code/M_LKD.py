# -*- coding: utf-8 -*-
"""
K_LKD
-----

Collection of the LKD class with methods, and components of the LKD class.
"""


from __future__        import print_function
import Code.K_Netze        as K_Netze
import Code.K_Component    as K_Component
import Code.M_Projection   as M_Projection
import Code.M_Shape        as M_Shape
import Code.M_FindPos      as M_FindPos
import shapefile
import os.path
import csv
from   pathlib         import Path 
import copy

roundNum    = 4

ID_Add = 'LKD_'
C_Code = 'DE'
        


def read(NumDataSets = 100000, RelDirName  = 'Eingabe/LKD/'):
    """ Main function to load LKD data set from shape file. Relative location of data given through **RelDirName**.
    """
    Ret_Data                = K_Netze.NetComp()
    Nodes                   = []
    PipeSegments            = []
    Storages                = []
    Compressors             = []
    Productions             = []
    
    RelDirName              = Path(RelDirName)

    
    # reading of raw data components
    PipeSegments    = read_component('PipeSegments', NumDataSets, RelDirName = RelDirName)

    # fix for Inf in PipeSegment
    for pp in PipeSegments:
        for xx in range(len(pp.lat)):
            if str(pp.lat[xx]) == 'inf':
                pp.lat[xx]  = 52.3
                pp.long[xx] = 5.4


    Nodes           = read_component('Nodes', NumDataSets, RelDirName = RelDirName)
    Ret_Data.Nodes  = Nodes
    
    # fixes for inf in data
    for nn in Nodes:
        if str(nn.lat) == 'inf':
            nn.lat  = 52.3
            nn.long = 5.4
            
            
    
    # Fixing country code problems
    Ret_Data        = changeCountryCode(Ret_Data, RelDirName  = 'Eingabe/LKD/LKD_CountryCodeChanges.csv')
    Nodes           = Ret_Data.Nodes
    
    
    Productions     = read_component('Productions', NumDataSets, RelDirName = RelDirName)
        
    Storages        = read_component('Storages', NumDataSets, RelDirName = RelDirName)
        


    # Fixing of PipeSegments and Nodes differences
    PipeSegments = fixPipeSegmentsNode(PipeSegments, Nodes)

    # Fixing some of the LKD pipe Segments
    Ret_Data.PipeSegments   = PipeSegments
    Ret_Data.Nodes          = Nodes
    PipeSegments            = changePipeSegments(Ret_Data, RelDirName  = 'Eingabe/LKD/LKD_NodeChanges.csv')

    Ret_Data.moveAttriVal(sourceCompName = 'Nodes', destinCompName = 'PipeSegments', 
                          sourceFindAttribName = 'id', destinFindAttribName = 'node_id', 
                          sourceAttribName = 'country_code', destinAttribName = 'country_code')

    Ret_Data.Nodes          = M_Shape.reduceElement(Ret_Data.Nodes, reduceType = 'LatLong')
    
    # Generatin of other components
    Compressors             = gen_component('Compressors', Ret_Data.Nodes)
   
    Ret_Data.Storages       = Storages
    Ret_Data.Compressors    = Compressors
    Ret_Data.Productions    = Productions
    Ret_Data.PipeLines      = []
    
    # reduction of PipeSegments from 1809 -->  1261 
    Ret_Data.PipeSegments2PipeSegments(attribListNames = ['max_pressure_bar', 'gas_type_isH', 'diameter_mm', 'pipe_class_type'], exceptNodes = ['Haidach', 'N_805129'])
    
    # Adding lat long
    Ret_Data.add_latLong(CompNames = ['Storages', 'Compressors', 'Productions', 'PipeSegments'])

    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['Storages', 'Compressors', 'Productions', 'PipeSegments', 'Nodes'])
    Ret_Data.remove_unUsedNodes()

    # Unit Conversion
    Ret_Data.MoveUnits('Storages',     'max_cap_pipe2store_GWh_per_d', 'max_cap_pipe2store_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Storages',     'max_cap_store2pipe_GWh_per_d', 'max_cap_store2pipe_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('PipeSegments', 'max_cap_GWh_per_d',            'max_cap_M_m3_per_d',            replace = True)
    Ret_Data.MoveUnits('Productions',  'max_production_GWh_per_d',     'max_production_M_m3_per_d',     replace = True)
    
    # removing attributes
    Ret_Data.removeAttrib('PipeSegments', ['max_cap_GWh_per_d'])
    Ret_Data.removeAttrib('Storages',     ['max_cap_pipe2store_GWh_per_d', 'max_cap_store2pipe_GWh_per_d'])
    Ret_Data.removeAttrib('Nodes',        ['compressor', 'ugs', 'production', 'comp_units'])
    Ret_Data.removeAttrib('Productions',  ['max_production_GWh_per_d'])

    
    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)

    # Adding further essential attributess
    Ret_Data.fill_length('PipeSegments')
    Ret_Data.make_Attrib(['PipeSegments'], 'lat',  'lat_mean',  'mean')
    Ret_Data.make_Attrib(['PipeSegments'], 'long', 'long_mean', 'mean')
    
    
    # Adding SourceName
    Ret_Data.SourceName      = ['LKD']
    
    
    
    return Ret_Data




def changePipeSegments(Netz, RelDirName  = 'LKD_NodeChanges.csv'):
    """Changes some pipe Segments based on an input CSV file
    """
    
    if os.path.exists(RelDirName):
        fid = open(RelDirName, 'r', encoding="utf-8", errors = "ignore")
        # Read header line
        fid.readline()
        
        csv_reader  = csv.reader(fid, delimiter = ";")
        InPipeIds   = Netz.get_Attrib(compName = 'PipeSegments', attribName = 'id')
        
        for row in csv_reader:
            # Getting pipe from CSV file
            PipeID      = str(row[0])
            #NodeCorrect = row[1]
            NodeWrong   = row[2]
            NodeNew     = row[3]
            lat         = float(row[4])
            long        = float(row[5])
            cc          = row[6]
            
            # getting corresponding pipeSegment from LKD data set
            pos = M_FindPos.find_pos_StringInList(String = PipeID, ListOfStrings = InPipeIds)
            
            if len(pos) == 1:
                
                if NodeNew == 'None':
                    # Removing pipe
                     Netz.PipeSegments[pos[0]].id = '-9999'
                     
                elif Netz.PipeSegments[pos[0]].node_id[0] == NodeWrong:
                    # PipeSegment from node
                     Netz.PipeSegments[pos[0]].node_id[0]       = NodeNew
                     Netz.PipeSegments[pos[0]].lat[0]           = lat
                     Netz.PipeSegments[pos[0]].long[0]          = long
                     Netz.PipeSegments[pos[0]].country_code[0]  = cc
                     Netz.PipeSegments[pos[0]].param['length']  = M_Projection.LatLong2DistanceValue(lat, long, Netz.PipeSegments[pos[0]].lat[-1], Netz.PipeSegments[pos[0]].long[-1])
                     # Node
                     Netz.Nodes.append(K_Component.Nodes(id = NodeNew, 
                                        name        = NodeNew, 
                                        source_id   = ['LKD_' + PipeID], 
                                        node_id     = ['N_' + NodeNew], 
                                        country_code = cc,
                                        lat         = lat, 
                                        long        = long, 
                                        param = {'comp_units': 0, 
                                        'operator_name' : None, 
                                        'is_import'         : 0, 
                                        'is_export'          : 0, 
                                        'H_L_conver'    : 0, 
                                        'operator_Z'    : None, 
                                        'compressor'    : [], 
                                        'entsog_key'    : None, 
                                        'is_crossBorder': 0, 
                                        'ugs'           : 0, 
                                        'production'    : 0, 
                                        'exact'         : 2, 
                                        'license'       : 'open data'}))
                     
                elif Netz.PipeSegments[pos[0]].node_id[1] == NodeWrong:
                    # PipeSegment to node
                     Netz.PipeSegments[pos[0]].node_id[1]       = NodeNew
                     Netz.PipeSegments[pos[0]].lat[-1]          = lat
                     Netz.PipeSegments[pos[0]].long[-1]         = long
                     Netz.PipeSegments[pos[0]].country_code[-1] = cc
                     Netz.PipeSegments[pos[0]].country_code[-1] = cc
                     Netz.PipeSegments[pos[0]].param['length']  = M_Projection.LatLong2DistanceValue(Netz.PipeSegments[pos[0]].lat[0], Netz.PipeSegments[pos[0]].long[0], lat, long)
                     # Node
                     Netz.Nodes.append(K_Component.Nodes(id = NodeNew, 
                                        name        = NodeNew, 
                                        source_id   = ['LKD_' + PipeID], 
                                        node_id     = ['N_' + NodeNew], 
                                        country_code = cc,
                                        lat         = lat, 
                                        long        = long, 
                                        param = {'comp_units': 0, 
                                        'operator_name' : None, 
                                        'is_import'         : 0, 
                                        'is_export'          : 0, 
                                        'H_L_conver'    : 0, 
                                        'operator_Z'    : None, 
                                        'compressor'    : [], 
                                        'entsog_key'    : None, 
                                        'is_crossBorder': 0, 
                                        'ugs'           : 0, 
                                        'production'    : 0, 
                                        'exact'         : 2, 
                                        'license'       : 'open data'}))
                else:
                    print('M_LKD.changePipeSegments: something wrong here too')
            else:
                print('M_LKD.changePipeSegments: something wrong here')
        
        Netz.select_byAttrib(['PipeSegments'], 'id', '-9999', '!=')
        
    return Netz




def changeCountryCode(Netz, RelDirName  = 'LKD_CountryCodeChanges.csv'):
    """Changes some pipe Segments based on an input CSV file
    """
    
    if os.path.exists(RelDirName):
        
        # getting all new node ideas were to chnage counttry code
        fid = open(RelDirName, 'r', encoding="utf-8", errors = "ignore")
        # Read header line
        fid.readline()
        
        csv_reader  = csv.reader(fid, delimiter = ";")
        
        allPipeID   = []
        allCC       = []
        for row in csv_reader:
            allPipeID.append(str(row[0]))
            allCC.append(row[1])


        # going through each element in Netz and change countrycode
        for comp in Netz.CompLabels():
            for ii, elem in enumerate(Netz.__dict__[comp]):
                if isinstance(elem.node_id, list):
                    for jj, elemId in enumerate(elem.node_id):
                        pos = M_FindPos.find_pos_StringInList(str(elemId), allPipeID)
                        if len(pos) == 1:
                            if isinstance(elem.country_code, list):
                                elem.country_code[jj]  = allCC[pos[0]]
                            else:
                                elem.country_code  = allCC[pos[0]]
                else:
                    pos = M_FindPos.find_pos_StringInList(str(elem.node_id), allPipeID)
                    if len(pos) == 1:
                        elem.country_code  = allCC[pos[0]]
        
    return Netz




def fixPipeSegmentsNode(PipeSegments, Nodes):
    """ Fixing wrong Start_point and End_Point id in respect of lat long

    \n.. comments: 
    Input:
        PipeSegments:   List of PipeSegments
        Nodes:          List of Nodes
    Return:
        PipeSegments
    """    
    
    node_id     = []
    node_lat    = []
    node_long   = []
    count       = 0
#    sourceIDNotSwapt = []
#    sourceIDSwapt = []
    
    # Getting Node Id, lat and long of nodes
    for nod in Nodes:
        node_id.append(nod.id)
        node_lat.append(round(nod.lat, roundNum))
        node_long.append(round(nod.long, roundNum))
    
    
    # Checking of there is a node in twice
    for id in node_id:
        pos     = M_FindPos.find_pos_ValInVector(id, node_id, '==')
        if len(pos) != 1:
            print('node ' + str(id) + ' funny.  Found ' + str(len(pos)))

    
    # going through each PipeSegment, and finding corresponding Nodes lat Long values 
    # and checking if they are same with Pipe Lat LONGS
    for pipe in PipeSegments:
        S_pipe_node_id = copy.deepcopy(pipe.node_id[0])
        S_lat     = round(pipe.lat[0], roundNum)
        S_long    = round(pipe.long[0], roundNum)
        
        E_pipe_node_id = copy.deepcopy(pipe.node_id[1])
        E_lat     = round(pipe.lat[-1], roundNum)
        E_long    = round(pipe.long[-1], roundNum)
        
        S_pos     = M_FindPos.find_pos_ValInVector(S_pipe_node_id, node_id, '==')
        E_pos     = M_FindPos.find_pos_ValInVector(E_pipe_node_id, node_id, '==')
        

        if node_lat[S_pos[0]] != S_lat or node_long[S_pos[0]] != S_long:
            if len(S_pos) != 1:
                print('Warning: Start Node Multiple times ' + str(S_pipe_node_id))
            elif len(S_pos) != 1:
                print('Warning: End Node Multiple times ' + str(E_pipe_node_id))
            elif node_lat[S_pos[0]] == E_lat and  node_long[S_pos[0]] == E_long and node_lat[E_pos[0]] == S_lat and  node_long[E_pos[0]] == S_long:
                pipe.node_id = [E_pipe_node_id, S_pipe_node_id]
                count = count + 1
            else:
                print('Warning: still wrong start ' + str(S_pipe_node_id))
    
#    if count > 0:
#        print('needed to rotate ' + str(count) + ' pipelines')
    
    return PipeSegments 



    
def read_component(DataType = '', NumDataSets = 1e+100, RelDirName  = None):
    """ Method of reading in LKD components from shape files. **RelDirName** supplies the relative location of the shape files, whereas **DataType** specifies which component is to be reaad in with options 'PipeSegments', 'Nodes', 'Storages', and 'Productions'.

    \n.. comments: 
    Input:
        self:            self
        RelDirName:      string, containing the relative path name of where data will be loaded from
                         Default = 'Eingabe/LKD/'
    Return:
        []
    """
    
    ReturnComponent = []
    inCoord 		= 'epsg:31468'
    outCoord	 	= 'epsg:4326'
    count           = 0
    if DataType in 'PipeSegments':
#        start = time.time()

        FileName_Shape  = str(RelDirName / 'pipelines_utf8.shp')
        # Loading from shape file
        Shapes          = shapefile.Reader(FileName_Shape, encoding = "utf8")
        # Malen der Europa Karte
#        print('there are pipesegments: ' + str(len(Shapes.shapeRecords())))
        for shape in Shapes.shapeRecords():
            # Getting PolyLine
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
            PipeLine        = M_Shape.PolyLine2PipeLines(polyLine, parts, source = C_Code, country_code = C_Code)

            lat             = PipeLine[0].lat
            long            = PipeLine[0].long
            
            # Getting Meta data
            id          = str(shape.record[0])
            source_id   = [ID_Add + str(id)]
            name        = replaceString(shape.record[1])
            if len(name) == 0:
                name = 'PS_' + str(id)
            # Converting gas_type to boolean
            is_H_gas        = shape.record[2]
            if is_H_gas == 'L':
                is_H_gas = 0
            elif is_H_gas == 'H':
                is_H_gas = 1
            
            length          = float(shape.record[3])/1000
            pipe_class_type = shape.record[6]
            if pipe_class_type == '':
                pipe_class_type = None
            # is_virtualPipe
            is_virtualPipe = False
            if len(shape.record[4]) > 0:
                if shape.record[4] == 1:
                    is_virtualPipe    = True

            # diameter_mm
            if len(shape.record[5]) > 0:
                if 'NULL' == shape.record[5]:
                    diameter_mm    = float('nan')
                else:
                    diameter_mm    = float(shape.record[5])
            else:
                diameter_mm    = float('nan')

            # max_pressure_bar
            if shape.record[7] == None:
                max_pressure_bar    = float('nan')
            elif type(shape.record[7]) == int:
                max_pressure_bar   = float(shape.record[7])
                if max_pressure_bar > 200:
                    max_pressure_bar = float('nan')
            elif len(shape.record[7]) > 0:
                if 'NULL' == shape.record[7]:
                    max_pressure_bar    = float('nan')
                else:
                    max_pressure_bar   = float(shape.record[7])
                    if max_pressure_bar > 200:
                        max_pressure_bar = float('nan')
            else:
                max_pressure_bar  = float('nan')
            
            diam_est            = shape.record[8]
            class_est           = shape.record[9]
            press_est           = shape.record[10]
            if isinstance(diam_est, str):
                if diam_est == 'NULL':
                    diam_est = float('nan')
                    diam_est_method      = 'raw'
                    diam_est_uncertainty = 0
                else:
                    diam_est = diam_est
                    diam_est_method      = 'raw'
                    diam_est_uncertainty = 0
            else:
                if diam_est == 1:
                    diam_est_method      = 'estimated'
                    diam_est_uncertainty = 1
                else:
                    diam_est_method      = 'raw'
                    diam_est_uncertainty = 0
                

            if isinstance(class_est, str):
                if class_est == 'NULL':
                    class_est = float('nan')
                    class_est_method      = 'raw'
                    class_est_uncertainty = 0
                else:
                    class_est = class_est
                    class_est_method      = 'raw'
                    class_est_uncertainty = 0
            else:
                if class_est == 1:
                    class_est_method      = 'estimated'
                    class_est_uncertainty = 1
                else:
                    class_est_method      = 'raw'
                    class_est_uncertainty = 0


            if isinstance(press_est, str):
                if press_est == 'NULL':
                    press_est = float('nan')
                    press_est_method      = 'raw'
                    press_est_uncertainty = 0
                else:
                    press_est_method      = 'raw'
                    press_est_uncertainty = 0
            else:
                if press_est == 1:
                    press_est_method      = 'estimated'
                    press_est_uncertainty = 1
                else:
                    press_est_method      = 'raw'
                    press_est_uncertainty = 0


#            if isinstance(class_est, str):
#                if class_est == 'NULL':
#                    class_est = float('nan')
#            if isinstance(press_est, str):
#                if press_est == 'NULL':
#                    press_est = float('nan')
            
            
            max_cap_GWh_per_d   = shape.record[11]
            operator_name       = str(shape.record[12])
            node_id             = ['N_' + str(shape.record[13]), 'N_' + str(shape.record[14])]
            if 'N_809066' in node_id and 'N_809063' in node_id:
                if node_id[0] == 'N_809066':
                    node_id[0] = 'N_809076'
                else:
                    node_id[1] = 'N_809076'
            if 'N_809066' in node_id and 'N_1000001' in node_id:
                if node_id[0] == 'N_809066':
                    node_id[0] = 'N_809076'
                else:
                    node_id[1] = 'N_809076'
                    
            if 'N_809065' in node_id and 'N_809025' in node_id:
                if node_id[0] == 'N_809065':
                    node_id[0] = 'N_809075'
                else:
                    node_id[1] = 'N_809075'
            if 'N_809065' in node_id and 'N_1000001' in node_id:
                if node_id[0] == 'N_809065':
                    node_id[0] = 'N_809075'
                else:
                    node_id[1] = 'N_809075'
                    
            if 'N_809064' in node_id and 'N_809026' in node_id:
                if node_id[0] == 'N_809064':
                    node_id[0] = 'N_809074'
                else:
                    node_id[1] = 'N_809074'
            if 'N_809064' in node_id and 'N_1000001' in node_id:
                if node_id[0] == 'N_809064':
                    node_id[0] = 'N_809074'
                else:
                    node_id[1] = 'N_809074'
                
            country_code        = ['DE', 'DE']
            
            if is_virtualPipe == False:
                ReturnComponent.append(K_Component.PipeSegments(id = id, 
                        name        = name, 
                        lat         = lat, 
                        long        = long, 
                        country_code = country_code, 
                        node_id     = node_id, 
                        source_id   = source_id, 
                        param = {'max_pressure_bar': max_pressure_bar, 
                        'is_H_gas'      : is_H_gas, 
                        'length'        : length, 
                        'diameter_mm'   : diameter_mm, 
                        'pipe_class_type': pipe_class_type, 
                        'max_cap_GWh_per_d': max_cap_GWh_per_d, 
                        'operator_name' : operator_name},
                        method = {'diameter_mm'     : diam_est_method, 
                        'pipe_class_type'           : class_est_method, 
                        'max_pressure_bar'          : press_est_method},
                        uncertainty = {'diameter_mm': diam_est_uncertainty, 
                        'pipe_class_type'           : class_est_uncertainty, 
                        'max_pressure_bar'          : press_est_uncertainty},
                        )) 
                count           = count + 1
            if count > NumDataSets:
                return ReturnComponent
    
    elif DataType in 'Nodes':
        inCoord 		= 'epsg:31468'
        outCoord	 	= 'epsg:4326'
        FileName_Shape = str(RelDirName / 'nodes_utf8.shp')
        # Loading from shape file
        Shapes  = shapefile.Reader(FileName_Shape, encoding = "utf8")
        # Malen der Europa Karte
        for shape in Shapes.shapeRecords():
            id              = 'N_' + shape.record[0]
            source_id       = [ID_Add + str(shape.record[0])]
            name            = replaceString(shape.record[1])
            operator_name   = str(shape.record[2])
            is_import           = shape.record[3]
            is_export            = shape.record[4]
            H_L_conver      = int(shape.record[5])
            operator_Z      = shape.record[6]
            compressor      = shape.record[7]
            compUnit        = shape.record[8]
            if 'NULL' in compUnit:
                compUnit = 0
            elif len(compUnit) == 0:
                compUnit = 0
            else:
                compUnit = float(compUnit)
                
            country_code= shape.record[12]
            X_coor      = shape.record[13]
            Y_coor      = shape.record[14]
            entsog_nam  = str(shape.record[15])
            if len(entsog_nam) > 0:
                name            = entsog_nam
            if name == '':
                name = 'Ort_' + str(id)
            entsog_key  = shape.record[16]
            if entsog_key == '':
                entsog_key = None
            is_crossBorder = shape.record[17]
            ugs         = shape.record[19]
            production  = shape.record[20]
            exact       = 1
            license     = 'open data'
            Line        = K_Component.PolyLine(lat = Y_coor, long = X_coor)
            Line        = M_Projection.XY2LatLong(Line, inCoord, outCoord)
            lat         = Line.lat
            long        = Line.long
            if id == 'N_809066' and country_code == 'AT':
                id = 'N_809076'
            elif id == 'N_809065' and country_code == 'AT':
                id = 'N_809075'
            elif id == 'N_809064' and country_code == 'AT':
                id = 'N_809074'
            
            ReturnComponent.append(K_Component.Nodes(id = id, 
                    node_id     = [id], 
                    name        = name, 
                    source_id   = source_id, 
                    long        = long, 
                    lat         = lat, 
                    country_code= country_code,
                    param       = {'exact': exact, 
                    'H_L_conver': H_L_conver, 
                    'operator_Z': operator_Z, 
                    'compressor': compressor, 
                    'comp_units': compUnit,
                    'entsog_key': entsog_key, 
                    'is_crossBorder': is_crossBorder, 
                    'ugs'       : ugs, 
                    'production': production, 
                    'operator_name': operator_name, 
                    'is_import' : is_import, 
                    'is_export' : is_export, 
                    'license'   : license}))
            count           = count + 1
            if count > NumDataSets:
                return ReturnComponent
    
    
    elif DataType in 'Storages':
        FileName_Shape = str(RelDirName / 'storages_utf8.shp')
        # Loading from shape file
        Shapes  = shapefile.Reader(FileName_Shape, encoding = "utf8")
        # Malen der Europa Karte
        for shape in Shapes.shapeRecords():
            id              = 'N_' + shape.record[0]
            source_id       = [ID_Add + str(shape.record[0])]
            name            = replaceString(shape.record[1])
            operator_name   = str(shape.record[2])
            entsog_nam      = str(shape.record[9])
            if len(entsog_nam) > 0:
                name            = entsog_nam
                
            entsog_key      = shape.record[10]
            if entsog_key == '':
                entsog_key = None
            max_cap_pipe2store_GWh_per_d   = shape.record[11]
            max_cap_store2pipe_GWh_per_d   = shape.record[12]
            node_id         = ['N_' + shape.record[0]]
            country_code    = shape.record[6]
            ReturnComponent.append(K_Component.Storages(id = id, 
                    name        = name, 
                    source_id   = source_id, 
                    country_code = country_code, 
                    node_id     = node_id, 
                    param       = {'operator_name': operator_name, 
                    'entsog_key'                  : entsog_key, 
                    'max_cap_pipe2store_GWh_per_d': max_cap_pipe2store_GWh_per_d, 
                    'max_cap_store2pipe_GWh_per_d': max_cap_store2pipe_GWh_per_d}))
                    
            count           = count + 1
            if count > NumDataSets:
                return ReturnComponent
        

    elif DataType in 'Productions':
        FileName_Shape = str(RelDirName / 'productions_utf8.shp')
        # Loading from shape file
        Shapes  = shapefile.Reader(FileName_Shape, encoding = "utf8")
        # Malen der Europa Karte
        for shape in Shapes.shapeRecords():
            id              = 'N_' + shape.record[0]
            source_id       = [ID_Add + str(shape.record[0])]
            name            = replaceString(shape.record[1])
            operator_name   = str(shape.record[2])
            entsog_nam      = str(shape.record[9])
            if len(entsog_nam) > 0:
                name            = entsog_nam
            entsog_key      = shape.record[10]
            if entsog_key == '':
                entsog_key = None
            max_production  = shape.record[11]
            node_id         = ['N_' + shape.record[0]]
            country_code    = shape.record[6]
            ReturnComponent.append(K_Component.Productions(id =  id, 
                    name        = name, 
                    source_id   = source_id, 
                    node_id     = node_id, 
                    country_code = country_code, 
                    param       = {'entsog_key': entsog_key, 
                    'operator_name': operator_name, 
                    'is_H_gas'     : 1, 
                    'max_production_GWh_per_d': max_production}))
            count           = count + 1
            if count > NumDataSets:
                return ReturnComponent
    
    return ReturnComponent




def gen_component(dataType, NodesIn):
    """ Generates a netz component from existing components of this netz, e.g. 
    generation of of nodes list from Segments.  Needs instance of netz as input 
    via **LKDInstance**.  Component name to be generated suplied as string **dataType**, 
    with current options implemented *Compressors*

    \n.. comments:
    Input:
        dataType:        string containing name of component to be created e.g. 'Compressors' 
        LKDInstance:     netz class instance
    Return:
        ReturnComponent: component list.  
    """
    
    ReturnComponent = []
    
    if dataType in 'Compressors':
        for seg in NodesIn:
            if float(seg.param['comp_units']):
                if seg.param['comp_units'] > 0:
                    id              = str(seg.id)
                    source_id       = [ID_Add + str(id)]
                    node_id         = [str(seg.id)]
                    name            = replaceString(seg.param['compressor'])
                    name            = str(seg.name)
                    lat             = seg.lat
                    long            = seg.long
                    country_code    = seg.country_code
                    # Param values
                    operator_name   = seg.param['operator_name']
                    license         = seg.param['license']
                    num_turb        = seg.param['comp_units']
                    entsog_key      = seg.param['entsog_key']

                    ReturnComponent.append(K_Component.Compressors(id = id, 
                                        name        = name,  
                                        source_id   = source_id, 
                                        country_code= country_code, 
                                        node_id     = node_id, 
                                        lat         = lat, 
                                        long        = long, 
                                        param       = {'operator_name': operator_name, 
                                        'num_turb'  : num_turb, 
                                        'entsog_key': entsog_key,
                                        'license'   : license}))

            elif ((len(seg.param['compressor']) > 0) and 
                      ('Regelanlage' not in seg.param['compressor']) and 
                      ('NULL' not in seg.param['compressor']) and
                      ('VErdichter' in seg.param['compressor'])):
                id              = str(seg.id)
                source_id       = [ID_Add + str(id)]
                node_id         = [str(seg.id)]
                name            = replaceString(seg.name)
                name            = str(seg.name)
                lat             = seg.lat
                long            = seg.long
                country_code    = seg.country_code
                # Param values
                operator_name   = seg.param['operator_name']
                license         = seg.param['license']
                num_turb        = seg.param['comp_units']
                entsog_key      = seg.param['entsog_key']
                
                ReturnComponent.append(K_Component.Compressors(id = id, 
                                name        = name,  
                                source_id   = source_id, 
                                country_code = country_code, 
                                node_id     = node_id, 
                                lat         = lat, 
                                long        = long, 
                                param       = {'operator_name': operator_name, 
                               'num_turb'   : num_turb, 
                               'entsog_key' : entsog_key,
                               'license'    : license}))
        
    return ReturnComponent
            
    


def replaceString(name_short):
    """Replacement of two strings due to formatting issues.
    """
    name_short       = name_short.replace('ü', 'ue')
    name_short       = name_short.replace('Ã¤', 'ae')
    
    return name_short