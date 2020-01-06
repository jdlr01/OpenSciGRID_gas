# -*- coding: utf-8 -*-
"""
M_EntsoG
--------

Collection of functions, that are being called from other modules, for applying to EntsoG class instances.
"""

import Code.K_Netze        as K_Netze
import Code.M_Helfer       as M_Helfer
import Code.M_FindPos      as M_FindPos
import Code.M_Projection   as M_Projection
import Code.K_Component    as K_Component
import Code.M_Internet     as M_Internet
import Code.M_Netze        as M_Netze
#import Code.M_Shape        as M_Shape
import Code.M_Matching     as M_Matching
#import Code.M_CSV          as M_CSV
import Code.JoinNetz       as JoinNetz

from   pathlib         import Path
import json
import urllib3
import certifi
import sys
import math
import os
import statistics

ID_Add = 'EG_'


def read(NumDataSets = 100000, DateStartStr = '2016-01-01' , DateEndStr = '2016-05-01', RelDirName = 'Eingabe/EntsoG/GasFlowInter/', RelDirNameInter = '', SiteIsPlaned = None):
    """ Main function to read data off EntsoG API, except physical gas flow data.
	
	
    \n.. comments: 
    Input:
        NumDataSets:    	max number of data sets to be read in
                            (Default = 100000) 
        RelDirName:     	string, containing dir name where GasLib  data is found
                            (Default = 'Eingabe/GasLib/')
		sourceName: 	    String of source abbreviation.
							(Default = None)
		RelDirNameInter:     Not used, only included as option, as is option for other data source read functions.
							(Default = 'Eingabe/InternetDaten/')							
    Return:
	    Ret_Data:      Instance of K_Netze.NetComp class, with components Nodes and Storages populated."""
    
    Ret_Data            = K_Netze.NetComp()
    RelDirName          = Path(RelDirName)

    # Reading raw data from API
    Ret_Data.Operators                  = read_component('Operators',             NumDataSets = NumDataSets, SiteIsPlaned = SiteIsPlaned)
    Ret_Data.ConnectionPoints           = read_component('ConnectionPoints',      NumDataSets = NumDataSets, SiteIsPlaned = SiteIsPlaned)
    Ret_Data.InterConnectionPoints      = read_component('InterConnectionPoints', NumDataSets = NumDataSets, SiteIsPlaned = SiteIsPlaned)
        
    Ret_Data.Nodes                      = gen_component('Nodes', Ret_Data)
    

    # Reading physical flow data from CSV files
    Gas_Data = read_GasFlow(Ret_Data, RelDirName)
    
    Ret_Data = addMeta(Ret_Data, Gas_Data)
    
    # Generation of further components from existing Netz class instance components
    Ret_Data.Storages           = gen_component('Storages',     Ret_Data) # 168
    Ret_Data.Productions        = gen_component('Productions',  Ret_Data) # 37
    Ret_Data.LNGs               = gen_component('LNGs',         Ret_Data) # 37
    Ret_Data.Consumers          = gen_component('Consumers',    Ret_Data) # 37

    # Replacing the lat/long of nodes to be best of our knowledge gien through Internet data
    if len(RelDirNameInter) > 0:
        RelDirNameInter     = Path(RelDirNameInter)
        Netz_Internet       = K_Netze.NetComp()
        Netz_Internet.Nodes = M_Internet.read_component("Nodes",  NumDataSets, 0, RelDirName = RelDirNameInter)
        
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = JoinNetz.match(
            Netz_Internet, Ret_Data, compName = 'Nodes', threshold = 35, multiSelect = True,
            funcs = (lambda comp_0, comp_1: M_Matching.getMatch_Names_CountryCode(comp_0, comp_1, AddInWord = 100), 
                lambda comp_0, comp_1: M_Matching.getMatch_LatLong_CountryCode(comp_0, comp_1, method = 'inv')
                ))


        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'lat',  Ret_Data,'Nodes', 'lat', pos_match_Netz_0,  pos_match_Netz_1)
        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'long', Ret_Data,'Nodes', 'long', pos_match_Netz_0, pos_match_Netz_1)
        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'country_code', Ret_Data,'Nodes', 'country_code', pos_match_Netz_0, pos_match_Netz_1)
        Ret_Data = M_Netze.copy_ParamVals(Netz_Internet, 'Nodes', 'exact', Ret_Data,'Nodes', 'exact', pos_match_Netz_0, pos_match_Netz_1)
        

    Ret_Data.PipeLines = []

    # informing user of bad data
    for comp in Ret_Data.ConnectionPoints:
        if comp.country_code == None:
            print('M_EntsoG.read: No country code for: ' + str(comp.name))
            

    # Removing attributesw
    Ret_Data.removeAttrib('Storages',['to_countryLabel', 'to_systemLabel',
                        'from_TsoItemIdentifier', 'from_directionKey', 
                        'from_infrastructureTypeLabel', 'from_operatorKey', 
                        'to_countryLabel', 'to_infrastructureTypeLabel', 'tpMapX', 'tpMapY'])
    Ret_Data.removeAttrib('LNGs',['tpMapX', 'tpMapY'])
    Ret_Data.removeAttrib('InterConnectionPoints',['tpMapX', 'tpMapY'])
    
    
    # Unit Conversion
    Ret_Data.MoveUnits('Nodes', 'max_cap_Exit_kWh_per_d',  'max_cap_Exit_M_m3_per_d',  replace = True)
    Ret_Data.MoveUnits('Nodes', 'min_cap_Exit_kWh_per_d',  'min_cap_Exit_M_m3_per_d',  replace = True)
    Ret_Data.MoveUnits('Nodes', 'max_cap_Entry_kWh_per_d', 'max_cap_Entry_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Nodes', 'min_cap_Entry_kWh_per_d', 'min_cap_Entry_M_m3_per_d', replace = True)

    # Removing attributes
    Ret_Data.removeAttrib('Nodes',   ['max_cap_Exit_kWh_per_d', 'min_cap_Exit_kWh_per_d', 'max_cap_Entry_kWh_per_d', 'min_cap_Entry_kWh_per_d'])

#    Ret_Data.remove_Elements(CompNames = [], AttribName = 'lat', AttribVal = None)
    # Adding lat long
    Ret_Data.add_latLong()

    # Cleaning up node_id and nodes
    Ret_Data.select_byAttrib(CompNames = [], AttribName = 'lat', AttribVal = [], methodStr = '!=nan')
    Ret_Data.merge_Nodes_Comps(compNames = ['Storages', 'Productions', 'LNGs', 'Consumers', 'InterConnectionPoints', 'Nodes'])
    Ret_Data.remove_unUsedNodes()
    
    # remove all elements, where Lat is none
    Ret_Data.select_byAttrib(CompNames = [], AttribName = 'lat', AttribVal = [], methodStr = '!=nan')


    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)

    # Adding further essential attributess
    Ret_Data.fill_length('PipeSegments')
    
    # Adding SourceName
    Ret_Data.SourceName     = ['EntsoG']

    return Ret_Data
    
    


def read_GasFlow(Ret_Data, RelDirName = 'Eingabe/EntsoG/GasFlow', StartDate = '2010-10-01T00:00:00', StopDate = '2120-12-31T00:00:00'):
    """ Reading of all data from a CSV folder. Relative directory name of CSV files given through **RelDirName**.
	
    \n.. comments: 
    Input:
        Ret_Data:    	max number of data sets to be read in
		RelDirName: 	
						(default = 'Eingabe/EntsoG/GasFlow')
		StartDate: 		
						(default = '2010-10-01T00:00:00')
		StopDate: 		
						(default = '2120-12-31T00:00:00').
    Output:
		Data 			List of component elements.
	"""
    
    Data = []
    AllPointKeys = M_Helfer.get_attribFromComp(Ret_Data, 'Nodes', 'pointKey') 
    AllPointKeys = list(set(AllPointKeys))
    # going through each possible file
    filename     = str(RelDirName)
    
    
    for file in os.listdir(filename):
        if file.endswith(".csv"):
            pointKey    = file.replace(".csv","")
            pos         = pointKey.find('_')
            pointKey    = pointKey[:pos]
            if pointKey in AllPointKeys:
                FileName = os.path.join(filename, file)
                Data.append(K_Component.GasFlow())
                Data[-1].load_Physical_CSV(FileName, StartDate = StartDate, StopDate = StopDate)
    
    return Data




def addMeta(Net_Data, Gas_Data):
    """ Adds meta data to EntsoG data, based on gas flow time series meta data    

    \n.. comments:
    Input:
        Net_Data: 	Netz data, into which meta data will be written
        Gas_Data: 	Gas flow, containing meta data
    Return:
        Ret_Data: 	Netz data as above, including further meta data."""
    
    Gas_pointKey_Label  = [gas.pointKey for gas in Gas_Data]
    Net_pointKey_Label  = [net.param['pointKey'] for net in Net_Data.Nodes]
    
    for node in Net_Data.Nodes:
        if node.param['pointKey'] in Gas_pointKey_Label:
            posNet  = M_FindPos.find_pos_StringInList(node.param['pointKey'], Net_pointKey_Label)
            posData = M_FindPos.find_pos_StringInList(node.param['pointKey'], Gas_pointKey_Label)
            for ii in posData:
                if 'MaxFlowValue_Exit' in Gas_Data[ii].MetaData:
                    Net_Data.Nodes[posNet[0]].max_cap_Exit_kWh_per_d = Gas_Data[ii].MetaData['MaxFlowValue_Exit']
                    Net_Data.Nodes[posNet[0]].min_cap_Exit_kWh_per_d = Gas_Data[ii].MetaData['MinFlowValue_Exit']
                if 'MaxFlowValue_Entry' in Gas_Data[ii].MetaData:
                    Net_Data.Nodes[posNet[0]].max_cap_Entry_kWh_per_d = Gas_Data[ii].MetaData['MaxFlowValue_Entry']
                    Net_Data.Nodes[posNet[0]].min_cap_Entry_kWh_per_d = Gas_Data[ii].MetaData['MinFlowValue_Entry']
        
    return Net_Data




def read_component(DataType = '', CompSet = '', NumDataSets = 1e+100, SiteIsPlaned = None):
    """ Reading data from EntsoG API.  Input parameters are **CompLabel** (list of 
    component labels as source), and start and end date as string, **DateStartStr** , 
    **DateEndStr** respectively.  Options for **DataType** is 
    *GasFlow*, *InterConnectionPoints*, or *ConnectionPoints*.  
        
    \n.. comments: 		
    Input: 
        DataType:        String containing label of what to read: 'GasFlow', 'InterConnectionPoints', 'ConnectionPoints', 'Operators', and 'OperPointDirections'
        CompSet          Component from Netz class
        DateStart:       (Optional = '2015-01-01') string of start year, for gas flow data
        NumDataSets:     (Optional = 1e+100) number containing maximum number of component entries to read
    Return:
        RetComponent: 	list of elemetns of a single components """
    
    RetComponent    = []
    Limit 		    = 10000
    inCoord 		= 'epsg:6962'
    outCoord	 	= 'epsg:4326'
    MapProj_q0X 	= -556235.4714567756
    MapProj_q1X 	= 15642.580959008656
    MapProj_q0Y 	= 1118484.7137876498
    MapProj_q1Y 	= 18100.482102780363
    count           = 0
    
  
    
    if 'InterConnectionPoints' in DataType:
        # Initialization of variables
        URL 			= 'https://transparency.entsog.eu/api/v1/interconnections'
    
        try:
            # Creation of a Pool Manager
            http            = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
        
            # Get the data
            URLData         = http.request('GET', URL + '?limit=' + str(Limit))
            
            # Convert the data into dict
            tables          = []
            try:
                tables          = json.loads(URLData.data.decode('UTF-8'))
            except:
                print('ERROR: M_EntsoG.read_component:InterConnectionPoints: reading URL failed')
                return []
        
            # checking that results coming back are ok
            if tables.__contains__('error'):
                print('EntsoG M_EntsoG.read_component:InterConnectionPoints: something wrong while getting InterConnection data from EntsoG', True)
            
            # Data allowed to be parsed
            else:
                # Checking if returned data truncated due to limit
                if Limit == len(tables['interconnections']):
                    print('Increase limit to ' + tables['meta']['total'], True)
                    print('EntsoG: M_EntsoG.read_component:InterConnectionPoints: Data exceeded Limit of ' + URL, True)
        

                for tt in tables['interconnections']:
                    # Disecting the input
                    id                              = tt['pointKey']
                    node_id                         = [id]
                    source_id                       = [ID_Add + str(id)]
                    name                            = M_Helfer.strip_accents(tt['pointLabel'])
                    country_code                    = tt['fromCountryKey']              # 'PT'

                    pointKey                        = tt['pointKey']
                    pointLabel                      = M_Helfer.strip_accents(tt['pointLabel'])
                    is_singleOperator               = tt['isSingleOperator']
                    if is_singleOperator:
                        is_singleOperator = 1
                    elif is_singleOperator == False:
                        is_singleOperator = 0
                    dataSet                         = tt['dataSet']
                    
                    tpMapX                          = float(tt['pointTpMapX'])
                    tpMapY                          = float(tt['pointTpMapY'])
                    
                    from_systemLabel                = tt['fromSystemLabel']             # 'Portugal', pointDirection
                    from_infrastructureTypeLabel    = tt['fromInfrastructureTypeLabel'] # 'Transmission'
                    from_operatorKey                = tt['fromOperatorKey']             # 'PT-TSO-0001'
                    from_directionKey               = tt['fromDirectionKey']            # 'exit'
                    if from_directionKey == '':
                        from_directionKey = None
                    from_TsoItemIdentifier          = tt['fromTsoItemIdentifier']       # '16ZORDGN--------W'
                    if from_TsoItemIdentifier == '':
                        from_TsoItemIdentifier = None
                    from_pointKey                   = tt['fromPointKey']
                    from_pointLabel                 = tt['fromPointLabel']

                    to_systemLabel                  = tt['toSystemLabel']               # 'Distribution'
                    to_infrastructureTypeLabel      = tt['toInfrastructureTypeLabel']   # 'Distribution'
                    to_countryLabel                 = tt['toCountryLabel']              # 'Portugal'
                    to_BzKey                        = tt['toBzKey']
                    to_operatorKey                  = tt['toOperatorKey'] 
                    to_pointKey                     = tt['toPointKey'] 
                    
                    # Changing country code for Moffat and using GB instead of UK
                    if name == 'Moffat':
                        country_code = 'GB'
                    if country_code == 'UK':
                        country_code  = 'GB'
                    
                    
                    if from_operatorKey == None:
                        tfrom_operatorKey = ''
                    else:
                        tfrom_operatorKey = from_operatorKey
                        
                    if from_directionKey == None:
                        tfrom_directionKey = ''
                    else:
                        tfrom_directionKey = from_directionKey
                        
                    pointDirection                  = tfrom_operatorKey + pointKey + tfrom_directionKey

                    try:
                        Line    = K_Component.PolyLine(lat = tpMapY, long = tpMapX)
                        Line    = M_Projection.XY2LatLong(Line, inCoord, outCoord, MapProj_q0X, MapProj_q1X, MapProj_q0Y, MapProj_q1Y)
                        long    = Line.long
                        lat     = Line.lat
                    except:
                        long    = []
                        lat     = []
                    
                    RetComponent.append(K_Component.InterConnectionPoints(id = id, 
                                name        = name, 
                                country_code= country_code, 
                                source_id   = source_id, 
                                node_id     = node_id, 
                                long        = long, 
                                lat         = lat, 
                                param       = {'pointKey': pointKey, 
                                'pointLabel'    : pointLabel, 
                                'is_singleOperator': is_singleOperator, 
                                'dataSet'       : dataSet, 
                                'tpMapX'        : tpMapX, 
                                'tpMapY'        : tpMapY, 
                                'to_BzKey'      : to_BzKey, 
                                'to_pointKey'   : to_pointKey,
                                'to_operatorKey': to_operatorKey, 
                                'pointDirection': pointDirection, 
                                'from_pointKey' : from_pointKey, 
                                'to_systemLabel': to_systemLabel, 
                                'from_pointLabel': from_pointLabel, 
                                'to_countryLabel': to_countryLabel, 
                                'from_systemLabel': from_systemLabel,
                                'from_operatorKey': from_operatorKey,
                                'from_directionKey': from_directionKey, 
                                'from_TsoItemIdentifier': from_TsoItemIdentifier, 
                                'from_infrastructureTypeLabel': from_infrastructureTypeLabel, 
                                'to_infrastructureTypeLabel': to_infrastructureTypeLabel})) #
                    
                    count = count + 1
                    if count >= NumDataSets:
                        return RetComponent
        
        except:
            raise
        
        

        
    elif 'ConnectionPoints' in DataType:
        # Initialization of variables
        URL 			= 'https://transparency.entsog.eu/api/v1/connectionpoints'
        
        try:
            # Creation of a Pool Manager
            http            = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
        
            # Get the data
            URLData         = http.request('GET', URL + '?limit=' + str(Limit))
            
            # Convert the data into dict
            tables          = []
            tables          = json.loads(URLData.data.decode('UTF-8'))
        
            # checking that results coming back are ok
            if tables.__contains__('error'):
                print('K_EntsoG.read_component: something wrong while getting ConnectionPoints data from EntsoG')
            
            # Data allowed to be parsed
            else:
                # Checking if returned data truncated due to limit
                if Limit == len(tables['connectionpoints']):
                    print('EntsoG: read_component: Data exceeded Limit of ' + URL)
                    print('Increase limit to ' + tables['meta']['total'])
                    print('EntsoG: read_component: Data exceeded Limit of ' + URL)
        
                count   = 0
    

                for tt in tables['connectionpoints']:
                    # Disecting the input
                    id                      = str(tt['pointKey'])
                    node_id                = [id]
                    source_id               =[ ID_Add + str(id)]
                    name                    = M_Helfer.strip_accents(tt['pointLabel'])

                    pointKey                = tt['pointKey']
                    pointLabel              = M_Helfer.strip_accents(tt['pointLabel'])
                    pointType               = tt['pointType']               # 'Distribution Point'
                    controlPointType        = tt['controlPointType']
                    dataSet                 = tt['dataSet']
                    pointEicCode            = tt['pointEicCode']
                    has_data                = tt['hasData']
                    
                    tpMapX                  = float(tt['tpMapX'])
                    tpMapY                  = float(tt['tpMapY'])
                        
                    importFromCountryKey    = tt['importFromCountryKey']    # None
                    
                    is_interconnection      = tt['isInterconnection']       # True
                    is_import               = tt['isImport']                # False
                    is_pipeInPipe           = tt['isPipeInPipe']            # False
                    is_planned              = tt['isPlanned']
                    is_crossBorder          = tt['isCrossBorder']           # False

                    infrastructureLabel     = tt['infrastructureLabel']     # 'Distribution'
                    infrastructureKey       = tt['infrastructureKey']       # 'DIS'

                    is_euCrossing           = tt['euCrossing']              # 'EU'
                    
                    is_virtualPoint         = tt['hasVirtualPoint']
                    virtualPointKey         = tt['virtualPointKey']
                    virtualPointLabel       = tt['virtualPointLabel']
                    
                    # Trying to get a country code
                    country_code    = None
                    if pointLabel.find('(') >=0 and pointLabel.find(')'):
                        pos1 = pointLabel.find('(')
                        pos2 = pointLabel.find(')')
                        if pos2 - pos1 == 3:
                            country_code = pointLabel[pos1+1:pos2]
                    if name == 'Moffat':
                        country_code = 'GB'
                    if name == 'Greater Belfast':
                        country_code = 'GB'
                        
                    if country_code == 'UK':
                        country_code  = 'GB'

                    # Generation of lat long
                    try:
                        Line    = K_Component.PolyLine(lat = tpMapY, long = tpMapX)
                        Line    = M_Projection.XY2LatLong(Line, inCoord, outCoord, MapProj_q0X, MapProj_q1X, MapProj_q0Y, MapProj_q1Y)
                        long    = Line.long
                        lat     = Line.lat
                    except:
                        long    = []
                        lat     = []

                    # Creation of element                    
                    if SiteIsPlaned == None or SiteIsPlaned == is_planned:
                        RetComponent.append(K_Component.ConnectionPoints(id = id, 
                                    node_id     = node_id, 
                                    name        = name, 
                                    country_code = country_code, 
                                    long        = long, 
                                    lat         = lat, 
                                    source_id   = source_id, 
                                    param       = {'pointKey'  : pointKey, 
                                    'pointLabel': pointLabel, 
                                    'pointType' : pointType, 
                                    'pointEicCode': pointEicCode, 
                                    'controlPointType': controlPointType, 
                                    'dataSet'   : dataSet, 
                                    'has_data'  : has_data, 
                                    'tpMapX'    : tpMapX, 
                                    'tpMapY'    : tpMapY, 
                                    'importFromCountryKey' : importFromCountryKey, 
                                    'is_interconnection' : is_interconnection, 
                                    'is_import' : is_import, 
                                    'is_pipeInPipe' : is_pipeInPipe, 
                                    'is_planned' : is_planned, 
                                    'is_crossBorder' : is_crossBorder, 
                                    'infrastructureLabel' :  infrastructureLabel, 
                                    'infrastructureKey' : infrastructureKey, 
                                    'is_euCrossing' : is_euCrossing, 
                                    'is_virtualPoint' : is_virtualPoint, 
                                    'virtualPointKey' : virtualPointKey, 
                                    'virtualPointLabel' : virtualPointLabel}))
                        # 
                        count = count + 1
                        if count >= NumDataSets:
                            return RetComponent
        
        except:
            raise
            
            
            
            
    elif 'Operators' in DataType:
        URL = 'https://transparency.entsog.eu/api/v1/operators'

        try:
            # Creation of a Pool Manager
            http       = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        
            # Selecting data 
            # Get the data
            URLData    = http.request('GET', URL+ '?limit=' + str(Limit))
        
            # Convert the data into dict
            tables     = json.loads(URLData.data.decode('UTF-8'))
            
            # checking that results coming back are ok
            if tables.__contains__('error'):
                print('K_EntsoG.read_component: something wrong while getting Operators data from EntsoG')
                
            # Data allowed to be parsed
            else:
                # Informing user that returns truncated due to limit
                if float(str(Limit)) == len(tables['operators']):
                    print('EntsoG: read_Operators: Data exceeded Limit of ' + URL)
                    print('Increase limit to ' + tables['meta']['total'])
                        
                # Disecting the Table data 
                for tt in tables['operators']:
                    # Disecting the input
                    id                  = str(tt['operatorKey'])
                    node_id             = [id]
                    source_id           = [ID_Add + str(id)]
                    name                = M_Helfer.strip_accents(tt['operatorLabel'])
                    country_code        = tt['operatorCountryLabel']
                    if len(country_code) == 0:
                        print('Operator no country_code')
                    if name == 'Moffat':
                        country_code = 'GB'
                    if country_code == 'UK':
                        country_code  = 'GB'

                    del tt['operatorKey']
                    del tt['operatorLabel']
                    del tt['operatorCountryLabel']
                    del tt['id']
                    
                    # Creation of new point
                    RetComponent.append(K_Component.Operators(id = id, 
                                node_id     = node_id, 
                                name        = name, 
                                source_id   = source_id, 
                                country_code = country_code, 
                                param       = tt))
                    
                    count = count + 1
                    if count >= NumDataSets:
                        return RetComponent
                    
        except:
            print('ERROR: K_EntsoG.read_component(Operators): Something wrong  here')
            raise 
            return []    


    elif 'OperPointDirections' in DataType:
        URL = 'https://transparency.entsog.eu/api/v1/operatorpointdirections'

        try:
            # Creation of a Pool Managher
            http       = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            # Get the data
            URLData    = http.request('GET', URL + '?limit=' + str(Limit))
                
            # Convert the data into dict
            tables     = json.loads(URLData.data.decode('UTF-8'))
    
            # checking that results coming back are ok
            if tables.__contains__('error'):
                print('K_EntsoG.read_component: something wrong while getting OperPointDirections data from EntsoG')
                    
                    
            # Data allowed to be parsed
            else:
                # Checking if returned data truncated due to limit
                if float(str(Limit)) == len(tables['operatorpointdirections']):
                    print('EntsoG: read_OperPointDirections: Data exceeded Limit of ' + str(URL))
                    print('Increase limit to ' + tables['meta']['total'])
            
                for tt in tables['operatorpointdirections']:
                    # Disecting the input
                    #pointLabel      = json.dumps(tt['pointLabel'], ensure_ascii=False)
                    pointLabel      = M_Helfer.strip_accents(tt['pointLabel'])
                    pointKey        = tt['pointKey']
                    operatorKey     = tt['operatorKey']
                    operatorLabel   = tt['operatorLabel']
                    has_data        = tt['hasData']
                    tpTsoGCVMin     = tt['tpTsoGCVMin']
                    tpTsoGCVMax     = tt['tpTsoGCVMax']
                    tpTsoGCVUnit    = tt['tpTsoGCVUnit']
                    id              = tt['id']
                    node_id         = [id]
                    source_id       = [ID_Add + str(id)]
                    
                    RetComponent.append(K_Component.OperPointDirections( id = id, 
                        name        = pointLabel, 
                        source_id   = source_id, 
                        node_id     = node_id, 
                        param       = {'pointLabel': pointLabel, 
                        'pointKey'  : pointKey, 
                        'operatorKey' : operatorKey, 
                        'operatorLabel' : operatorLabel, 
                        'has_data'  : has_data, 
                        'tpTsoGCVMin' : tpTsoGCVMin,
                        'tpTsoGCVMax' : tpTsoGCVMax, 
                        'tpTsoGCVUnit': tpTsoGCVUnit}))
            
                    count = count + 1
                    if count >= NumDataSets:
                        return RetComponent

        except:
            print('ERROR: M_EntsoG.read_component(OperPointDirections): Something wrong  here')
            raise 
            return []    
        
    return RetComponent
        
        


def gen_component(compType, EntsoGInstance):
    """ Generation of storage data set from InterConnectionPoints and ConnectionPoints components.  
    
    \n.. comments: 
    Input:
        compType: 		string containing component type to be generated.
        NetzInstance: 	instance of EntsoG class
    Return:
        RetComponent    list of storage elements."""

    # Make internal copy of them
    Data1 = EntsoGInstance.copy()
    Data2 = EntsoGInstance.copy()
    Data3 = EntsoGInstance.copy()
    
    if compType in 'Storages':
        RetStorages    = []
        # Shrink data set of UnderGroundStorages
        if len(Data1.InterConnectionPoints) > 0:
            Data1.select_byAttrib(['InterConnectionPoints'], 'pointKey', 'UGS-')
            pointKey_InterConnections   = M_Helfer.get_attribFromComp(Data1, 'InterConnectionPoints', 'pointKey')
        else:
            Data1                       = []
            pointKey_InterConnections   = []
            
        if len(Data2.ConnectionPoints) > 0:
            Data2.select_byAttrib(['ConnectionPoints'], 'pointKey', 'UGS-')
            pointKey_ConnectionPoints   = M_Helfer.get_attribFromComp(Data2, 'ConnectionPoints', 'pointKey')
        else:
            Data2                       = []
            pointKey_ConnectionPoints   = []
            

        joindList                   = pointKey_InterConnections + pointKey_ConnectionPoints
        ListNodeNames = list(set(joindList))
        
        for nam in ListNodeNames:
            # First check in InterConnectionPoints
            pos = M_FindPos.find_pos_StringInList(nam, pointKey_InterConnections)
            
            # Check in ConnectionPoints if not found in InterConnectionPoints
            if len(pos) == 0:
                pos         = M_FindPos.find_pos_StringInList(nam, pointKey_ConnectionPoints)
                thisEntry   = Data2.ConnectionPoints[pos[0]]
            else:
                thisEntry = Data1.InterConnectionPoints[pos[0]]

            # Adding Storage
            is_planned                   = None
            from_infrastructureTypeLabel = None
            from_operatorKey             = None
            from_directionKey            = None
            to_systemLabel               = None
            to_infrastructureTypeLabel   = None
            to_countryLabel              = None
            from_TsoItemIdentifier       = None
            
            if 'is_planned' in thisEntry.param:
                is_planned = thisEntry.param['is_planned']
                
            if 'fromInfrastructureTypeLabel' in thisEntry.param:
                from_infrastructureTypeLabel = thisEntry.param['from_infrastructureTypeLabel']
                
            if 'from_operatorKey' in thisEntry.param:
                from_operatorKey = thisEntry.param['from_operatorKey']
                
            if 'from_directionKey' in thisEntry.param:
                from_directionKey = thisEntry.param['from_directionKey']
                
            if 'to_systemLabel' in thisEntry.param:
                to_systemLabel = thisEntry.param['to_systemLabel']
                
            if 'to_infrastructureTypeLabel' in thisEntry.param:
                to_infrastructureTypeLabel = thisEntry.param['to_infrastructureTypeLabel']
                
            if 'to_countryLabel' in thisEntry.param:
                to_countryLabel = thisEntry.param['to_countryLabel']
                
            if 'from_TsoItemIdentifier' in thisEntry.param:
                from_TsoItemIdentifier = thisEntry.param['from_TsoItemIdentifier']

            # WRiting data to output struct
            RetStorages.append(K_Component.Storages(id = thisEntry.id, 
                        node_id                     = thisEntry.node_id, 
                        name                        = thisEntry.param['pointLabel'], 
                        source_id                   = thisEntry.source_id, 
                        long                        = thisEntry.long, 
                        lat                         = thisEntry.lat, 
                        country_code                = thisEntry.country_code, 
                        param                       = {'is_planned':  is_planned, 
                        'tpMapX'                    : thisEntry.param['tpMapX'], 
                        'tpMapY'                    : thisEntry.param['tpMapY'], 
                        'from_infrastructureTypeLabel': from_infrastructureTypeLabel,  
                        'from_operatorKey'          : from_operatorKey, 
                        'from_directionKey'         : from_directionKey, 
                        'from_TsoItemIdentifier'    : from_TsoItemIdentifier, 
                        'to_systemLabel'            : to_systemLabel, 
                        'to_infrastructureTypeLabel': to_infrastructureTypeLabel, 
                        'to_countryLabel'           : to_countryLabel}))

        RetComponent = RetStorages


    elif compType in 'Productions':
        RetProductions    = []
        
        # InterConnectionPoints
        if len(EntsoGInstance.InterConnectionPoints) > 0:
            Data1.select_byAttrib(['InterConnectionPoints'], 'pointKey', 'PRD-')
            pointKey_InterConnections   = M_Helfer.get_attribFromComp(Data1, 'InterConnectionPoints', 'pointKey')
        else:
            Data1                       = []
            pointKey_InterConnections   = []
            
        # ConnectionPoints
        if len(EntsoGInstance.ConnectionPoints) > 0:
            Data2.select_byAttrib(['ConnectionPoints'], 'pointKey', 'PRD-')
            pointKey_ConnectionPoints   = M_Helfer.get_attribFromComp(Data2, 'ConnectionPoints', 'pointKey')
        else:
            Data2                       = []
            pointKey_ConnectionPoints   = []
        
        joindList                   = pointKey_InterConnections + pointKey_ConnectionPoints
        ListNodeNames = list(set(joindList))
        
        for nam in ListNodeNames:
            # First check in InterConnectionPoints
            pos = M_FindPos.find_pos_StringInList(nam, pointKey_InterConnections)
            
            # Check in ConnectionPoints if not found in InterConnectionPoints
            if len(pos) == 0:
                pos         = M_FindPos.find_pos_StringInList(nam, pointKey_ConnectionPoints)
                thisEntry   = Data2.ConnectionPoints[pos[0]]
                thisEntry.country_code = thisEntry.country_code
            else:
                thisEntry = Data1.InterConnectionPoints[pos[0]]
            
            # Adding Storage
            RetProductions.append(K_Component.Productions(id = thisEntry.id,
                            node_id         = thisEntry.node_id, 
                            name            = thisEntry.param['pointLabel'], 
                            source_id       = thisEntry.source_id, 
                            lat             = thisEntry.lat, 
                            long            = thisEntry.long, 
                            country_code    = thisEntry.country_code))
            
        RetComponent = RetProductions


    elif compType in 'LNGs':
        RetLNGs    = []
        # Shrink data set to LNG
        if len(Data1.InterConnectionPoints) > 0:
            Data1.select_byAttrib(['InterConnectionPoints'], 'pointKey', 'LNG-')
            pointKey_InterConnections   = M_Helfer.get_attribFromComp(Data1, 'InterConnectionPoints', 'pointKey')
        else:
            Data1                       = []
            pointKey_InterConnections   = []
            
        if len(Data2.ConnectionPoints) > 0:
            Data2.select_byAttrib(['ConnectionPoints'], 'pointKey', 'LNG-')
            pointKey_ConnectionPoints   = M_Helfer.get_attribFromComp(Data2, 'ConnectionPoints', 'pointKey')
        else:
            Data2                       = []
            pointKey_ConnectionPoints   = []
            
        if len(Data3.Nodes) > 0:
            Data3.select_byAttrib(['Nodes'], 'pointKey', 'LNG-')
            pointKey_Nodes   = M_Helfer.get_attribFromComp(Data3, 'Nodes', 'pointKey')
        else:
            Data3                       = []
            pointKey_Nodes              = []


        joindList       = pointKey_InterConnections + pointKey_ConnectionPoints
        ListNodeNames   = list(set(joindList))
        
        for nam in ListNodeNames:
            # First check in InterConnectionPoints
            pos = M_FindPos.find_pos_StringInList(nam, pointKey_InterConnections)
            
            # Check in ConnectionPoints if not found in InterConnectionPoints
            if len(pos) == 0:
                pos         = M_FindPos.find_pos_StringInList(nam, pointKey_ConnectionPoints)
                thisEntry   = Data2.ConnectionPoints[pos[0]]
            else:
                thisEntry = Data1.InterConnectionPoints[pos[0]]
            # Adding Storage
            is_planned = None
            pointType = None
            is_interconnection = None
            
            if 'is_planned' in thisEntry.param:
                is_planned = thisEntry.param['is_planned']
                
            if 'pointType' in thisEntry.param:
                pointType  = thisEntry.param['pointType']
                
            if 'is_interconnection' in thisEntry.param:
                is_interconnection  = thisEntry.param['is_interconnection']
                
            RetLNGs.append(K_Component.LNGs(id = thisEntry.id, 
                    source_id           = thisEntry.source_id, 
                    node_id             = thisEntry.node_id, 
                    name                = thisEntry.param['pointLabel'], 
                    long                = thisEntry.long, 
                    lat                 = thisEntry.lat, 
                    country_code        = thisEntry.country_code,
                    param               = {'pointKey': thisEntry.param['pointKey'], 
                    'pointLabel'        : thisEntry.param['pointLabel'], 
                    'tpMapX'            : thisEntry.param['tpMapX'], 
                    'tpMapY'            : thisEntry.param['tpMapY'], 
                    'is_planned'        : is_planned, 
                    'pointType'         : pointType, 
                    'is_interconnection': is_interconnection }))

        RetComponent = RetLNGs
           
    elif compType in 'Consumers':
        RetConsumers    = []
        # Shrink data set of UnderGroundStorages
        if len(Data1.InterConnectionPoints) > 0:
            Data1.select_byAttrib(['InterConnectionPoints'], 'pointKey', 'FNC-')
            pointKey_InterConnections   = M_Helfer.get_attribFromComp(Data1, 'InterConnectionPoints', 'pointKey')
        else:
            Data1                       = []
            pointKey_InterConnections   = []
            
        if len(Data2.ConnectionPoints) > 0:
            Data2.select_byAttrib(['ConnectionPoints'], 'pointKey', 'FNC-')
            pointKey_ConnectionPoints   = M_Helfer.get_attribFromComp(Data2, 'ConnectionPoints', 'pointKey')
        else:
            Data2                       = []
            pointKey_ConnectionPoints   = []
            
        if len(Data3.Nodes) > 0:
            Data3.select_byAttrib(['Nodes'], 'pointKey', 'FNC-')
            pointKey_Nodes   = M_Helfer.get_attribFromComp(Data3, 'Nodes', 'pointKey')
        else:
            Data2                       = []
            pointKey_Nodes              = []


        joindList     = pointKey_InterConnections + pointKey_ConnectionPoints
        ListNodeNames = list(set(joindList))
        
        for nam in ListNodeNames:
            # First check in InterConnectionPoints
            pos = M_FindPos.find_pos_StringInList(nam, pointKey_InterConnections)
            
            # Check in ConnectionPoints if not found in InterConnectionPoints
            if len(pos) == 0:
                pos = M_FindPos.find_pos_StringInList(nam, pointKey_ConnectionPoints)
                thisEntry = Data2.ConnectionPoints[pos[0]]
                thisEntry.country_code = thisEntry.country_code
            else:
                thisEntry = Data1.InterConnectionPoints[pos[0]]
            # Adding Storage
            RetConsumers.append(K_Component.Consumers(id = thisEntry.id, 
                        node_id         = thisEntry.node_id, 
                        source_id       = thisEntry.source_id, 
                        name            = thisEntry.param['pointLabel'], 
                        country_code    = thisEntry.country_code)) # , long = thisEntry.long, lat = thisEntry.lat
        RetComponent = RetConsumers

        
    elif compType == 'Nodes':
        RetNodes = []
        if len(EntsoGInstance.InterConnectionPoints) > 0:
            pointKey_InterConnections   = M_Helfer.get_attribFromComp(EntsoGInstance, 'InterConnectionPoints', 'pointKey')
        else:
            pointKey_InterConnections   = []
            
        if len(EntsoGInstance.ConnectionPoints) > 0:
            pointKey_ConnectionPoints   = M_Helfer.get_attribFromComp(EntsoGInstance, 'ConnectionPoints', 'pointKey')
        else:
            pointKey_ConnectionPoints   = []
            
        # Making unique list of locations via point key
        joindList     = pointKey_InterConnections + pointKey_ConnectionPoints
        ListNodeNames = list(set(joindList))
        
        # Populating attributes of Nodes
        for nam in ListNodeNames:
            # First check in InterConnectionPoints
            posInt = M_FindPos.find_pos_StringInList(nam, pointKey_InterConnections)
            posCon = M_FindPos.find_pos_StringInList(nam, pointKey_ConnectionPoints)
            
            # Check in ConnectionPoints if not found in InterConnectionPoints
            if len(posInt) == 0:
                thisEntryCon                = EntsoGInstance.ConnectionPoints[posCon[0]]
                
                id                          = thisEntryCon.id
                node_id                     = [id]
                country_code                = thisEntryCon.country_code
                source_id                   = thisEntryCon.source_id
                long                        = thisEntryCon.long
                lat                         = thisEntryCon.lat
                name                        = None
                # Param values
                pointKey                    = thisEntryCon.param['pointKey']
                name                        = thisEntryCon.param['pointLabel']
                tpMapX                      = thisEntryCon.param['tpMapX']
                tpMapY                      = thisEntryCon.param['tpMapY']
                to_infrastructureTypeLabel  = thisEntryCon.param['infrastructureLabel']
                is_planned                  = thisEntryCon.param['is_planned']
                nodeType                    = ['Con']
                from_infrastructureTypeLabel= None
                from_TsoItemIdentifier      = None
                from_directionKey           = None

                
            elif len(posCon) == 0:
                thisEntryInt                = EntsoGInstance.InterConnectionPoints[posInt[0]]
                
                id                          = thisEntryInt.id
                node_id                     = [id]
                name                        = None
                source_id                   = thisEntryInt.source_id
                country_code                = thisEntryInt.country_code
                long                        = thisEntryInt.long
                lat                         = thisEntryInt.lat
                # Param values
                pointKey                    = thisEntryInt.param['pointKey']
                name                        = thisEntryInt.param['pointLabel']
                tpMapX                      = thisEntryInt.param['tpMapX']
                tpMapY                      = thisEntryInt.param['tpMapY']
                from_infrastructureTypeLabel= thisEntryInt.param['from_infrastructureTypeLabel']
                from_directionKey           = thisEntryInt.param['from_directionKey']
                to_infrastructureTypeLabel  = thisEntryInt.param['to_infrastructureTypeLabel']
                from_TsoItemIdentifier      = thisEntryInt.param['from_TsoItemIdentifier']
                is_planned                  = None
                nodeType                    = ['Int']

                
            else:
                thisEntryCon                = EntsoGInstance.ConnectionPoints[posCon[0]]
                thisEntryInt                = EntsoGInstance.InterConnectionPoints[posInt[0]]
                
                id                          = thisEntryInt.id
                node_id                     = [id]
                source_id                   = thisEntryInt.source_id
                country_code                = thisEntryInt.country_code
                long                        = thisEntryInt.long
                lat                         = thisEntryInt.lat
                name                        = None
                # Param values
                pointKey                    = thisEntryInt.param['pointKey']
                name                        = thisEntryInt.param['pointLabel']
                tpMapX                      = thisEntryInt.param['tpMapX']
                tpMapY                      = thisEntryInt.param['tpMapY']
                from_infrastructureTypeLabel= thisEntryInt.param['from_infrastructureTypeLabel']
                from_directionKey           = thisEntryInt.param['from_directionKey']
                to_infrastructureTypeLabel  = thisEntryInt.param['to_infrastructureTypeLabel']
                from_TsoItemIdentifier      = thisEntryInt.param['from_TsoItemIdentifier']
                is_planned                  = thisEntryCon.param['is_planned']
                nodeType                    = ['Con', 'Int']
            # Create Node
            RetNodes.append(K_Component.Nodes(id = id, 
                     name                   = name, 
                     node_id                = node_id,
                     long                   = long,
                     lat                    = lat, 
                     source_id              = source_id, 
                     country_code           = country_code, 
                     
                     param                  = {'pointKey': pointKey, 
                     'tpMapX'               : tpMapX, 
                     'tpMapY'               : tpMapY, 
                     'from_infrastructureTypeLabel' : from_infrastructureTypeLabel, 
                     'from_directionKey'    : from_directionKey, 
                     'to_infrastructureTypeLabel' : to_infrastructureTypeLabel, 
                     'from_TsoItemIdentifier': from_TsoItemIdentifier, 
                     'is_planned'           : is_planned, 
                     'nodeType'             : nodeType, 
                     'max_cap_Exit_kWh_per_d': None, 
                     'min_cap_Exit_kWh_per_d': None, 
                     'max_cap_Entry_kWh_per_d': None, 
                     'min_cap_Entry_kWh_per_d': None, 
                     'exact'                : 2}))
            
        RetComponent = RetNodes
    
    return RetComponent



    
def gen_pipeSegments(Ret_Data, RelDirName):
    """Generation of PipeSegments from EntsoG data sets (supplied via CSV files, 
    **RelDirName**) and data **Ret_Data**.
	
	
    \n.. comments: 
    Input:
        Ret_Data: 		string containing relative dir name of where data located.
        RelDirName: 	Relative path name for Internet Data.
    Return:
        RetPipeSegment  list of pipeSegment elements."""

    RetPipeSegment  = []
    count           = 0
    
    # getting the meta data from each CSV file
    Ret_Data.GasFlowData = read_GasFlow(Ret_Data, RelDirName, StartDate = '2010-10-01', StopDate = '2010-10-01')
    
    # setting up list of PointKey values for 'from' and 'to'
    allFromPointKeys    = M_Helfer.get_attribFromComp(Ret_Data, 'GasFlowData', 'fromPointKey')
    allToPointKeys      = M_Helfer.get_attribFromComp(Ret_Data, 'GasFlowData', 'toPointKey')
    
    # list of all node ids
    NodeIDs             = M_Helfer.get_attribFromComp(Ret_Data, 'Nodes', 'pointKey')
    
    # looping through each element of FromPointKey
    for ii in range(len(allFromPointKeys)):
        # testing that fromPointKey != toPointKey
        if (allFromPointKeys[ii] != allToPointKeys[ii]) and (allToPointKeys[ii] != 'null') and (allFromPointKeys[ii] != 'null') and (len(allToPointKeys[ii]) > 0) and (len(allFromPointKeys[ii]) > 0): 

            thisFromPointKey    = allFromPointKeys[ii]
            thisToPointKey      = allToPointKeys[ii]
            
            # now looking fro thisFrom/thisTo in Nodes
            posFrom         = M_FindPos.find_pos_StringInList(thisFromPointKey, NodeIDs)
            posTo           = M_FindPos.find_pos_StringInList(thisToPointKey,   NodeIDs)
            
            if len(posFrom) == 0:
                print(thisFromPointKey)
            else:
                print(thisToPointKey)
            
            if (len(posFrom) == 1) and (len(posTo) == 1):
                # pointKey        = Ret_Data.GasFlowData[ii].pointKey
                id              = str(count)
                source_id       = [ID_Add + str(id)]
                name            = Ret_Data.Nodes[posFrom[0]].name
                max_pressure_bar= None
                country_code    = Ret_Data.Nodes[posFrom[0]].country_code
                node_id         = [Ret_Data.Nodes[posFrom[0]].id, Ret_Data.Nodes[posTo[0]].id]
                RetPipeSegment.append(K_Component.PipeSegments(id = id, 
                                    name            = name, 
                                    source_id       = source_id, 
                                    node_id         = node_id,
                                    country_code    = country_code, 
                                    param           = {'max_pressure_bar': max_pressure_bar}))

    return RetPipeSegment




def deSpike_GasFlow(GasFlow, NumSpikes = 12, MultiVal = 0.5):
    """ Takes time series of gas flow data and removes out-layers, using the inputs **NumSpikes**, and **MultiVal**.  
	Calls internally function M_Helfer.deSpike_GasFlow_Helfer().
    
    \n.. comments:  
    Input:  
	    GasFlow: 		Instance of EntsoG glass
        NumSpikes:   	number of points that can be de-spiked per time series
						(Default = 12)
        MultiVal:    	[0..1] multiplier value for threshold of spike value
						(Default = 0.5), 
    Return:
        GasFlow:       	Instance of EntsoG glass"""

    # Counter for later    
    DataCount = 0
        
    # Loop for each EntsoG data set
    for data in GasFlow:
        GasFlow[DataCount].values_Entry = deSpike_GasFlow_Helfer(data.values_Entry, 'FDC_TOP', NumSpikes, MultiVal)
        GasFlow[DataCount].values_Exit  = deSpike_GasFlow_Helfer(data.values_Exit,  'FDC_TOP', NumSpikes, MultiVal)
        
        DataCount = DataCount + 1
        
    return GasFlow
    


        
    
def create_FDC(GasFlow):
    """ Creating of FDC of physical gas flow data, where FDC is written into 'self.FDC_Entry' and 'self.FDC_Exit' respectively.
    
    \n.. comments:
    Input:
	    GasFlow:  		Instance of EntsoG glass
	Return:
	    FDC_Exit: 		FDC of exit gas flow, of 200 data points
		FDC_Entry:		FDC of entry gas flow, of 200 data points
    """

    values_Entry_sorted     = []
    values_Exit_sorted      = []
    FDC_Exit                = []
    FDC_Entry               = []
    if hasattr(GasFlow, 'values_Entry'):
        for vv in GasFlow.values_Entry:
            values_Entry_sorted.append(vv)
                
                
        # Removing zeros or nanas
        for ii in range(len(values_Entry_sorted)):
            if values_Entry_sorted[ii] == 0:
                values_Entry_sorted[ii] = float(0.01)
                
        values_Entry_sorted = sorted([x for x in values_Entry_sorted if not math.isnan(x)])
                
        [X_Entry, Y_Entry] = M_Helfer.shrink_Data(range(len(values_Entry_sorted)), values_Entry_sorted, 200)
                
        # scaling data
        for ii in range(len(Y_Entry)):
            Y_Entry[ii] = Y_Entry[ii]/max(Y_Entry)
                
        FDC_Entry  = Y_Entry
    else:
        FDC_Entry  = []
             
            
            
    if hasattr(GasFlow, 'values_Exit'):
        for vv in GasFlow.values_Exit:
            values_Exit_sorted.append(vv)
    
        # Removing zeros or nanas
        for ii in range(len(values_Exit_sorted)):
            if values_Exit_sorted[ii] == 0:
                values_Exit_sorted[ii] = float(0.01)
            
        values_Exit_sorted  = sorted([x for x in values_Exit_sorted  if not math.isnan(x)])
    
        [X_Exit, Y_Exit]   = M_Helfer.shrink_Data(range(len(values_Exit_sorted)),  values_Exit_sorted,  200)
    

        # scaling data
        for ii in range(len(Y_Exit)):
            Y_Exit[ii]  = Y_Exit[ii]/max(Y_Exit)
    
        FDC_Exit   = Y_Exit
    else:
        FDC_Exit   = []

    return [FDC_Exit, FDC_Entry]




def GasFlowAPI2CSV(Netz = '', SourceCompLabels = [], StartNum = 0, NumDataSets = 1e+100, DateStartStr = '2015-01-01', DateEndStr = '2016-01-01', AttribName = [], AttribVal = [], DirName = ''):
    """ Main function to read gas flow data from web, and store to CSV files.

    \n.. comments:
    Input:
        Netz:               Netz class instance, 
        SourceCompLabels:   List of component labels, that are being used as source 
		                    meta data for API interrogation, mainly using pointKey
        DateEnd:            String of end year, for gas flow data
                            (Default = '2016-01-01') 
        AttribName:         List of string, of attribute to filter gas flow data on
                            (Default = []) 
        AttribVal:          List of values, for filtering with AttribName.
                            (Default = []) 
        DirName:            String containing location (dir) where gasFlow data shall 
                            be saved to 
							(Default = '').
    Return:
        []
    """
    
    count               = 0
    URL                 = 'https://transparency.entsog.eu/api/v1/operationaldatas'
    Limit               = '5000'
    intervalDays        = int('30')
    days                = M_Helfer.get_Days(DateStartStr, DateEndStr, intervalDays)
        
    # Creation of a Pool Manager
    http        = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    dirList     = ['exit', 'entry']
    dirList     = ['entry']
    # loop for each location point (either ConnectionPoints or InterConnection)
    for compLabel in SourceCompLabels:

        EndNum      = min(len(Netz.__dict__[compLabel]), NumDataSets)
        # loop through each component element        
        for ii in range(StartNum, EndNum):
            comp = Netz.__dict__[compLabel][ii]
            # loop through both directions
            for dirVal in dirList:
                # Initialization for new data set
                ValueGas                = []
                ValueFromPeroid         = []
                ValueToPeroid           = []
                ErsteDatenGefunden      = False
                gotMeta                 = False
                
                if compLabel == 'InterConnectionPoints':
                    MetaData            = {'tpMapX': comp.param['tpMapX'],
                                       'tpMapY': comp.param['tpMapY'],
                                       'pointLabel': comp.param['pointLabel'],
                                       'pointType': None,
                                       'pointKey':  comp.param['pointKey'],
                                       'is_singleOperator': comp.param['is_singleOperator'],
                                       'pointDirection': comp.param['pointDirection'],
                                       'from_operatorKey': comp.param['from_operatorKey'],
                                       'from_TsoItemIdentifier': comp.param['from_TsoItemIdentifier'],
                                       'from_infrastructureTypeLabel' : comp.param['from_infrastructureTypeLabel'],
                                       'from_systemLabel': comp.param['from_systemLabel'],
                                       'from_directionKey': comp.param['from_directionKey'],
                                       'from_pointKey': comp.param['from_pointKey'],
                                       'from_pointLabel': comp.param['from_pointLabel'],
                                       'to_InfrastructureTypeLabel': comp.param['to_InfrastructureTypeLabel'],
                                       'to_countryLabel': comp.param['to_countryLabel'],
                                       'to_systemLabel' : comp.param['to_systemLabel'],
                                       'to_BzKey': comp.param['to_BzKey'],
                                       'to_operatorKey': comp.param['to_operatorKey'],
                                       'to_pointKey': comp.param['to_pointKey'],
                                       'source': 'IntConnPoints'}
                                       #'is_planned': comp.is_planned, 'is_crossBorder': comp.is_crossBorder 
                elif compLabel == 'ConnectionPoints':
                    MetaData            = {'tpMapX': comp.param['tpMapX'],
                                       'tpMapY': comp.param['tpMapY'],
                                       'pointLabel': comp.param['pointLabel'],
                                       'pointType': comp.param['pointType'],
                                       'pointKey':  comp.param['pointKey'],
                                       'is_singleOperator': None,
                                       'pointDirection': None,
                                       'from_operatorKey': None,
                                       'from_TsoItemIdentifier': None,
                                       'from_infrastructureTypeLabel' : None,
                                       'from_systemLabel': None,
                                       'from_directionKey': None,
                                       'from_pointKey': None,
                                       'from_pointLabel': None,
                                       'to_InfrastructureTypeLabel': None,
                                       'to_countryLabel': None,
                                       'to_systemLabel' : None, 
                                       'to_BzKey': None,
                                       'to_operatorKey': None,
                                       'to_pointKey': None,
                                       'source': 'ConnPoints'}
                else:
                    print('ERROR: M_EntsoG.GasFlowAPI2CSV: Code not written for component: ' + compLabel)
                    
                    
                print(' ')
                print(' ')
                print('pointLabel: ', comp.pointLabel + ', dirVal: ', dirVal)
                print(' directionKey=' + dirVal)

                # Loop through days
                for dayCount in range(len(days)-1):
                    # Creation of the HTML request
                    DateStart       = days[dayCount]
                    DateEnd         = days[dayCount + 1]
                    
                    if compLabel == 'InterConnectionPoints':
                        URL_wert    = URL +  '?limit=' + Limit + '&pointKey=' + comp.param['pointKey'] + '&pointDirection=' 
                        + comp.param['pointDirection']+ '&from='  + DateStart.strftime("%Y-%m-%d")  + '&to=' + DateEnd.strftime("%Y-%m-%d") 
                        + '&indicator=Physical%20Flow'  + '&directionKey=' + dirVal
                                      
                        URLData    = http.request('GET', URL +  '?limit=' + Limit + '&pointKey=' + comp.param['pointKey'] + 
                                          '&pointDirection=' + comp.param['pointDirection'] + '&from='  + 
                                          DateStart.strftime("%Y-%m-%d")  + '&to=' + 
                                          DateEnd.strftime("%Y-%m-%d")  + '&indicator=Physical%20Flow'  
                                          + '&directionKey=' + dirVal)
                        
                        
                    elif compLabel == 'ConnectionPoints':
                        URL_wert = URL +  '?limit=' + Limit + '?pointKey=' + comp.param['pointKey'] + '&from='
                        +DateStart.strftime("%Y-%m-%d")  + '&to=' + DateEnd.strftime("%Y-%m-%d")  + '&indicator=Physical%20Flow'  + '&directionKey=' + dirVal
                                   
                        URLData    = http.request('GET', URL +  '?limit=' + Limit + '&pointKey=' + comp.param['pointKey'] + 
                                          '&from='  + DateStart.strftime("%Y-%m-%d")  + '&to=' + 
                                          DateEnd.strftime("%Y-%m-%d")  + '&indicator=Physical%20Flow'  + 
                                          '&directionKey=' + dirVal)
                        

                    # Check that there was no time out 
                    if '504 Gateway timeout' in str(URLData.data):
                        print(' ')
                        print('        504 Gateway timeout')
                        print(URL_wert)
                
                    else:
                        # Convert HTML data 
                        tables          = json.loads(URLData.data.decode('UTF-8'))
                        
                        # Check that no Error given
                        if tables.__contains__('error'):
                            sys.stdout.write('n')
                            sys.stdout.flush()
            
                        # RetComponent allowed to be parsed
                        else:
                            sys.stdout.write('.')
                            sys.stdout.flush()
                            # Checking if returned data truncated due to limit
                            if float(Limit) == len(tables['operationaldatas']):
                                # Write Comment into log file
                                print('RetComponent exceeded Limit:  Increase limit to ' + str(tables['meta']['total']))
    
            
                            for tt in tables['operationaldatas']:
                                # Dissecting the input
                                periodFrom          = tt['periodFrom']
                                periodTo            = tt['periodTo']
                                
                                # Grab value if present
                                if type(tt['value'])  == float:
                                    value               = float(tt['value'])
                                    ValueGas.append(value)
                                    ValueFromPeroid.append(periodFrom)
                                    ValueToPeroid.append(periodTo)
                                    ErsteDatenGefunden  = True
                                elif type(tt['value'])  == int:
                                    value               = float(tt['value'])
                                    ValueGas.append(value)
                                    ValueFromPeroid.append(periodFrom)
                                    ValueToPeroid.append(periodTo)
                                    ErsteDatenGefunden  = True
                                elif ErsteDatenGefunden:
                                    ValueGas.append(math.nan)
                                    ValueFromPeroid.append(periodFrom)
                                    ValueToPeroid.append(periodTo)
                                
                                # Grab meta data if not done so
                                if not gotMeta:
                                    id                  = str(tt['id'])
                                    source_id           = [ID_Add + str(id)]
                                    pointKey            = tt['pointKey']
                                    name                = pointKey
                                    directionKey        = tt['directionKey']
                                    
                                    gotMeta             = True
                                    MetaData.update({'operatorKey':         tt['operatorKey']})
                                    MetaData.update({'periodType ':         tt['periodType']})
                                    MetaData.update({'flowStatus':          tt['flowStatus']})
                                    MetaData.update({'indicator':           tt['indicator']})
                                    MetaData.update({'tsoEicCode':          tt['tsoEicCode']})
                                    MetaData.update({'tsoItemIdentifier':   tt['tsoItemIdentifier']})
                                    MetaData.update({'unit':                tt['unit']})
                                    MetaData.update({'capacityType':        tt['capacityType']})
                                    
                
                # and now assigning and saving the data if len(ValueGas) > 0
                # Simulate MaxFlowValue
                MaxFlowValue    = math.nan
                MinFlowValue    = math.nan
                if len(ValueGas) > 0:
                    MaxFlowValue = max(ValueGas)
                    MinFlowValue = min(ValueGas)

                MetaData.update({'MaxFlowValue': MaxFlowValue})
                MetaData.update({'MinFlowValue': MinFlowValue})
            
                # if any meta data/data to write,...
                if gotMeta:
                    DataTemp = []
                    DataTemp.append(K_Component.GasFlow(id = id, name = name, source_id = source_id, pointKey = pointKey, 
                                    directionKey = directionKey, MetaData = MetaData,  value = ValueGas, 
                                    intervalStart = ValueFromPeroid,  intervalEnd = ValueToPeroid))
                    for dat in DataTemp: 
                        dat.save_GasFlow_CSV(DirName, '_' + str(MetaData['operatorKey']) + '_' + str(MetaData['source']) + '_'+ dirVal)
                    

                # interrupting if number of data sets larger than maxElements
                count = count + 1
                if count >= NumDataSets:
                    return []
    
    return []    




def deSpike_GasFlow_Helfer(values, TypeName, NumPoints, MultiVal):
    """ Helper function to de-spike a time series data. 
    
    \n.. comments:     
    Input:
        values          time series of flow data
        TypeName        string containing type of de-spiking:
                            'FDC_TOP': sorting the time series, and then removing the highest values
                            'FDC_BOT': sorting the time series, and then removing the lowest values
                            'SinglePoint': indevidual points removed if data point 
                                            prior and after are roughly same and point
                                            in question totally out
                            'STD' using the STD as a threshold
        NumPoints       for type 'FDC_TOP': Number of spikes
        MultiVal        for type 'FDC': multiplication value 
                        for type 'SinglePointDiff': threshold (in percent [0..1]) to select 
                                                values to be replaced
                        for type 'STD' threshold is MiltiVal * STD of data
    Return:
        values              time series of flow data, without spike values"""
    
    valuesSort_TOP = sorted([x for x in values if not math.isnan(x)], reverse = True)
    valuesSort_BOT = sorted([x for x in values if not math.isnan(x)], reverse = False)
            
            
    if 'FDC_TOP' in TypeName:
        # now checking for Spikes
        if len(valuesSort_TOP) >  NumPoints:
            valuesGood      = valuesSort_TOP[NumPoints : ]
        
            # finding each spike
            meanVal         = sum(valuesGood)/len(valuesGood)
            thresholdVal    = meanVal * (1 + MultiVal)
            for jj in range(NumPoints):
                if valuesSort_TOP[jj] > thresholdVal:
                    pos = M_FindPos.find_pos_ValInVector(max(values), values, '==')
                    if len(pos) > 0:
                        values[pos[0]] = meanVal
                        
    elif 'FDC_BOT' in TypeName:
        # now checking for Spikes
        if len(valuesSort_BOT) > NumPoints:
            valuesGood      = valuesSort_BOT[NumPoints : ]
        
            # finding each spike
            meanVal         = sum(valuesGood)/len(valuesGood)
            thresholdVal    = meanVal * (1 - MultiVal)
            for jj in range(NumPoints):
                if valuesSort_BOT[jj] < thresholdVal:
                    pos = M_FindPos.find_pos_ValInVector(min(values), values, '==')
                    if len(pos) > 0:
                        values[pos[0]] = meanVal
                        
    elif 'STD' in TypeName:
        if len(valuesSort_TOP) > 0:
            STD             = statistics.stdev(valuesSort_TOP)
            if STD > 0.0:
                thresholdVal    = STD * MultiVal
                if len(valuesSort_TOP) > NumPoints*2:
                    meanVal         = sum(valuesSort_TOP[NumPoints: - NumPoints])/len(valuesSort_TOP[NumPoints: - NumPoints])
                else:
                    meanVal         = sum(valuesSort_TOP)/len(valuesSort_TOP)
                ThVa_TOP        = meanVal + thresholdVal
                ThVa_BOT        = meanVal - thresholdVal
                # top end
                for jj in range(NumPoints):
                    if valuesSort_TOP[jj] > ThVa_TOP:
                        pos = M_FindPos.find_pos_ValInVector(max(values), values, '==')
                        if len(pos) > 0:
                            values[pos[0]] = meanVal
                # Bottom end
                for jj in range(NumPoints):
                    if valuesSort_BOT[jj] < ThVa_BOT:
                        pos = M_FindPos.find_pos_ValInVector(min(values), values, '==')
                        if len(pos) > 0:
                            values[pos[0]] = meanVal
    else:
        print('M_EntsoG.deSpike_GasFlow_Helfer: TypeName: ' + TypeName + ' not coded.')
    
    return values


              
