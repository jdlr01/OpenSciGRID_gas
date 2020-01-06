# -*- coding: utf-8 -*-
"""
M_GIE
-----

Summary of all functions that are needed for handling specific GIE data set sets
"""

import Code.M_Helfer     as M_Helfer
import Code.K_Netze      as K_Netze
import Code.K_Component  as K_Component
import Code.M_MatLab     as M_MatLab
import Code.M_Internet   as M_Internet
import Code.M_Netze      as M_Netze 
import Code.M_Matching   as M_Matching
import Code.JoinNetz     as JoinNetz



from   pathlib       import Path
import urllib3
import certifi
import json
import math
import os

ID_Add  = 'GIE_'


def read( NumDataSets = 100000, requeYear = '2000', RelDirName = 'Eingabe/GIE/', RelDirNameInter = 'Eingabe/InternetDaten/'):
    """ Reading in GIE data sets from API, with **RelDirName** indicating which directory 
	from where to load the data from, **NumDataSets** maximum number of records to read, 
	and **requeYear** for which year to get data.

    \n.. comments: 
    Input:
        NumDataSets:     	number of data sets
                            (default = 100000) 
		requeYear: 			string containing year [####] for which data to be retrieved
                            (default = '2000') 
        RelDirName:     	string, of relative directory name where GIE meta data is loaded from
		RelDirNameInter: 	String of location of internet data so that Noders can be loaded from that and GIE stations
                            been given letlong values from Internet data set.
							(default ='Eingabe/InternetDaten/')
    Return:
	    Ret_Data: 			Instance of Netze class."""
    
    RelDirName          = Path(RelDirName)
    Ret_Data            = K_Netze.NetComp()
    LNGs                = []
    Storages            = []
    
    
    # Reading Raw Data
    Storages   = read_component('Storages', NumDataSets, requeYear, DirName = RelDirName)
    LNGs       = read_component('LNGs', NumDataSets, requeYear, DirName = RelDirName)


    # Generation of additional components
    Nodes1     = gen_component('Nodes', LNGs)       # check this one
    Nodes2     = gen_component('Nodes', Storages)   # check this one
        
        
    Ret_Data.Nodes      = Nodes1 + Nodes2
    Ret_Data.LNGs       = LNGs
    Ret_Data.Storages   = Storages
    

    Ret_Data.MoveUnits('LNGs', 'max_workingLNG_M_m3', 'max_workingGas_M_m3')
    

    # Adding lat long if Netz_Internet supplied
    if RelDirNameInter  != None:
        RelDirNameInter     = Path(RelDirNameInter)
        Netz_Internet       = K_Netze.NetComp()
        Netz_Internet.Nodes = M_Internet.read_component("Nodes",  NumDataSets, 0, RelDirName = RelDirNameInter)
        
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = JoinNetz.match(
            Netz_Internet, Ret_Data, compName = 'Nodes', threshold = 80, multiSelect = True,  
            funcs = lambda comp_0, comp_1: M_Matching.getMatch_Names_CountryCode(comp_0, comp_1, AddInWord = 100), numFuncs = 1)

        if len(pos_add_Netz_1)> 0:
            print('WARNING: M_GIE.read(): ' + str(len(pos_add_Netz_1)) + ' from ' + str(len(Ret_Data.Storages)) + ' locations could not be GeoReferenced.')

        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'lat',  Ret_Data,'Nodes', 'lat', pos_match_Netz_0,  pos_match_Netz_1)
        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'long', Ret_Data,'Nodes', 'long', pos_match_Netz_0, pos_match_Netz_1)
        Ret_Data = M_Netze.copy_ParamVals(Netz_Internet, 'Nodes', 'exact', Ret_Data,'Nodes', 'exact', pos_match_Netz_0, pos_match_Netz_1)
        
        Ret_Data.add_latLong()
    
    
        # Unit conversion
    Ret_Data.MoveUnits('LNGs',      'max_cap_store2pipe_GWh_per_d', 'max_cap_store2pipe_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('LNGs',      'median_cap_store2pipe_GWh_per_d', 'median_cap_store2pipe_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('LNGs',      'max_workingLNG_M_m3', 'max_workingGas_M_m3', replace = True)
    Ret_Data.MoveUnits('Storages',  'max_cap_pipe2store_GWh_per_d', 'max_cap_pipe2store_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Storages',  'max_cap_store2pipe_GWh_per_d', 'max_cap_store2pipe_M_m3_per_d', replace = True)
    

        # Removing attributes
    Ret_Data.removeAttrib('LNGs',       ['median_cap_store2pipe_GWh_per_d', 'max_cap_store2pipe_GWh_per_d', 'max_workingLNG_M_m3'])
    Ret_Data.removeAttrib('Storages',   ['max_cap_pipe2store_GWh_per_d', 'max_cap_store2pipe_GWh_per_d'])


    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['LNGs', 'Storages', 'Nodes'])
    Ret_Data.remove_unUsedNodes()


    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)


    # Adding SourceName
    Ret_Data.SourceName             = ['GIE']
    
    return Ret_Data




def gen_component(dataType, CompIn):
    """ Generates a netz component from existing components of this netz, e.g. generation 
	of of nodes list from Segments.  Component name to be generated supplied as string 
	**dataType**, with current options implemented *Nodes* Data supplied via component **CompIn**.

    \n.. comments:
    Input:
        dataType:        string containing name of component to be created e.g. 'Nodes' 
        CompIn:          netz class instance
    Return:
        ReturnComponent: component list.  """

    Nodes = []
    if 'Nodes' == dataType:
        for comp in CompIn:
            Nodes.append( K_Component.Nodes( id = comp.id, 
                        node_id     = comp.node_id, 
                        name        = comp.name, 
                        source_id   = comp.source_id, 
                        country_code = comp.country_code, 
                        lat         = None, 
                        long        = None, 
                        param       = {'name_short': comp.param['name_short'], 
                        'facility_code': comp.param['facility_code'], 
                        'eic_code'  : comp.param['eic_code'] }))
    
    return Nodes




def read_component(DataType = 'LNGs', NumDataSets = 100000, requeYear = [2000], DirName = None):
    """ Reading in GIE LNGs data sets from API, **NumDataSets** maximum number of records to read, 
	and **requeYear** for which year to get data. **RelDirName** is the relative path name.

    \n.. comments: 
    Input:
        DataType:        string, containing the data type to read, otions are 'LNGs' or 'Storages'
        NumDataSets:     (Optional = 100000) number of data sets
		requeYear: 		(Optional = [2000]) list of numbers containing year [####] for which data to be retrieved
        RelDirName:     string, containing relative dir name where GIE meta data
                         default = 'Eingabe/GIE/'
    Return:
	    ReturnComponent	Instance of Component (list of single type elements)
    """
    
    # dealing with private key        
    ReturnComponent = []
    pathPrivKey     = os.path.join(os.getcwd(), 'Eingabe/GIE/GIE_PrivateKey.txt')
    if os.path.isfile(pathPrivKey) is False:
        print('ERROR: M_GIE.read_component: you will need to get a private key from the GIE API.')
        print('Please see documentation for help.')
        print('No data will be loaded')
        return ReturnComponent

    PrivKey         = M_Helfer.getLineFromFile(pathPrivKey)
        
    
    
    if 'LNGs' in DataType:
        # Initialization
        webCall_1   = 'https://alsi.gie.eu/api/data/'
        eic_code    = ''
        count       = 0
        filename    = str(DirName /  'GIE_LNG.csv')
        print('        LNGs progress:')

        # Reading Meta data from CSV file
        # connecting to CSV file
        fid         = open(filename, "r", encoding='iso-8859-15', errors='ignore')
        # Reading header line
        fid.readline()
        # Reading next line
        temp        = M_Helfer.strip_accents(fid.readline()[:-1])

        while (len(temp) > 0) and (count <NumDataSets):
            typeval    = temp.split(';')[1]
            if 'LSO' not in typeval:
                country_code    = temp.split(';')[0]
                id              = temp.split(';')[2]
                node_id         = [id]
                source_id       = [ID_Add + str(id)]
                facility_code   = temp.split(';')[2]
                name            = temp.split(';')[4]
                name_short      = temp.split(';')[5]
                name_short      = replaceString(name_short)

                ReturnComponent.append(K_Component.LNGs(name = name, 
                                id          = id,
                                node_id     = node_id, 
                                source_id   = source_id, 
                                country_code = country_code,
                                lat         = None, 
                                long        = None, 
                                param       = {'facility_code': facility_code, 
                                'name_short': name_short, 
                                'eic_code'  : eic_code}))
    
                count           = count + 1
            else:
                eic_code        = temp.split(';')[2]
                    
            # Reading next line
            temp    = M_Helfer.strip_accents(fid.readline()[:-1])
            
        # Creation of a Pool Manager
        http            = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        # Reading for all created storages the data off the web page
        #maxSets     = min([len(ReturnComponent), NumDataSets])
        maxSets     = len(ReturnComponent)
        #for ii in range(96, 100):
        count = 0
        for ii in range(maxSets):
            # Initialization
            workingLNGVolume    = []
            Store2PipeCap       = []
                
            # information from CSV file
            this_facility_code  = ReturnComponent[ii].param['facility_code']
            this_country_code   = ReturnComponent[ii].country_code
            this_eic_code       = ReturnComponent[ii].param['eic_code']
            thisURL             = webCall_1 + this_facility_code + '/' + this_country_code + '/' + this_eic_code
            # Get the data
            URLData    = http.request('GET', thisURL, headers = {'x-key' : PrivKey})
                
                
            # Convert the data into dict
            tables          = []
            try:
                tables          = json.loads(URLData.data.decode('UTF-8'))
            except:
                print('ERROR: M_GIE.read_component(LNGs): reading URL failed')
                return []
                
            # checking that results coming back are ok
            if tables.__contains__('error'):
                print('GIE load_Storages: something wrong while getting Storage data from GIE')#, True)
                print(tables)
            # Data allowed to be parsed
            else:
                for tt in tables:
                    # Disecting the input
                    for year in requeYear:
                        if (tt['dtmi'] != '-') and (str(year) in tt['gasDayStartedOn']):
                            workingLNGVolume.append(float(tt['dtmi']) * 1000)   # declared total maximum inventory 1000 m^3 LNG
                            Store2PipeCap.append(   float(tt['dtrs']))          # declared total reference sendout GWh/d (sernd out capacity)
                        
                    
                # Remove wrong data points
                workingLNGVolume  = M_Helfer.testData(workingLNGVolume, 'PercentAbsDiff', 4, 0)
                Store2PipeCap     = M_Helfer.testData(Store2PipeCap,    'PercentAbsDiff', 4, 0)
                        
                # Update screen with dot
                print('.', end='')

                # Deriving required values from time series
                ReturnComponent[ii].param.update({'max_workingLNG_M_m3': M_MatLab.get_median(workingLNGVolume)[0] / 1000000})
                ReturnComponent[ii].param.update({'median_cap_store2pipe_GWh_per_d': M_MatLab.get_median(Store2PipeCap)[0]})
                ReturnComponent[ii].param.update({'max_cap_store2pipe_GWh_per_d': M_MatLab.get_max(Store2PipeCap)[0]})
                
                count = count + 1
                if count > NumDataSets:
                    print(' ')
                    return ReturnComponent
    

    elif 'Storages'  in DataType:
        # Initialization
        webCall_1     = 'https://agsi.gie.eu/api/data/'
        eic_code    = ''
        count       = 0
        print('         STORAGES progress:')
            
        filename    = str(DirName / 'GIE_Storages.csv')

        # Reading Meta data from CSV file
        # connecting to CSV file
        fid         = open(filename, "r", encoding = "iso-8859-15", errors = "surrogateescape")        
        # Reading hearder line  
        fid.readline()
        # Reading next line
        temp        = M_Helfer.strip_accents(fid.readline()[:-1])
        while (len(temp) > 0) and (count <NumDataSets):
            typeval    = temp.split(';')[1]
            if 'Storage Facility' in typeval:
                country_code    = temp.split(';')[0]
                id              = temp.split(';')[2]
                node_id         = [id]
                source_id       = [ID_Add + str(id)]
                facility_code   = temp.split(';')[2]
                name            = temp.split(';')[4]
                name_short      = temp.split(';')[5]
                name_short       = replaceString(name_short)
                
                name_short      = name_short.replace(' ', '')
                name_short      = name_short.strip()
                if 'OudeStatenzijl' in name_short:
                    country_code = 'NL'
                elif 'KinsaleSouthwest' in name_short:
                    country_code = 'IRL'
                
                ReturnComponent.append(K_Component.Storages(name = name, 
                                id          = id,
                                node_id     = node_id, 
                                lat         = None, 
                                long        = None, 
                                source_id   = source_id, 
                                country_code = country_code,
                                param       ={'facility_code': facility_code, 
                                'eic_code'  : eic_code, 
                                'name_short': name_short }))
    
                count           = count + 1
            else:
                eic_code        = temp.split(';')[2]
                
            # Reading next line
            temp    = M_Helfer.strip_accents(fid.readline()[:-1])
                
                
        # Creation of a Pool Manager
        http            = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        # Reading for all created storages the data off the web page
        maxSets     = min([len(ReturnComponent), NumDataSets])
                
        count   = 0
        keepPos = []
        for ii in range(maxSets):
            # Initialization
            max_workingGas_M_m3 = []
            Store2PipeCap       = []
            Pipe2StoreCap1      = []
                
            # information from CSV file
            this_facility_code  = ReturnComponent[ii].param['facility_code']
            this_country_code   = ReturnComponent[ii].country_code
            this_eic_code       = ReturnComponent[ii].param['eic_code']
            thisURL             = webCall_1 + this_facility_code + '/' + this_country_code + '/' + this_eic_code
                
            # Get the data
            URLData             = http.request('GET', thisURL, headers = {'x-key' : PrivKey})
                
                
            # Convert the data into dict
            tables          = []
            try:
                tables          = json.loads(URLData.data.decode('UTF-8'))
                # checking that results coming back are ok
                if tables.__contains__('error'):
                    print('GIE load_Storages: something wrong while getting Storage data from GIE', True)
                    
                # Data allowed to be parsed
                else:
                    # print('len(tables[connectionpoints]) ' + str(len(tables['connectionpoints'])))
        
                    for tt in tables:
                        # Disecting the input
                        for year in requeYear:
                            if (tt['gasInStorage'] != '-') and (str(year) in tt['gasDayStartedOn']):
                                max_workingGas_M_m3.append(float(tt['workingGasVolume']))
                                Store2PipeCap.append(      float(tt['injectionCapacity']))
                                Pipe2StoreCap1.append(     float(tt['withdrawalCapacity']))
                            
                        
                    # Remove wrong data sets
                    max_workingGas_M_m3 = M_Helfer.testData(max_workingGas_M_m3, 'PercentAbsDiff', 4, 0)
                    Store2PipeCap       = M_Helfer.testData(Store2PipeCap,       'PercentAbsDiff', 4, 0)
                    Pipe2StoreCap       = M_Helfer.testData(Pipe2StoreCap1,      'PercentAbsDiff', 4, 0)
                            
                    # Deriving required values from time series
#                    wert, _ = 
                    ReturnComponent[ii].param.update({'max_workingGas_M_m3': M_MatLab.get_max(max_workingGas_M_m3)[0] })
                    ReturnComponent[ii].param.update({'max_cap_store2pipe_GWh_per_d': M_MatLab.get_max(Store2PipeCap)[0]})
                    ReturnComponent[ii].param.update({'max_cap_pipe2store_GWh_per_d': M_MatLab.get_max(Pipe2StoreCap)[0]})
                    
                    if math.isnan(ReturnComponent[ii].param['max_cap_pipe2store_GWh_per_d']):
                        ReturnComponent[ii].param['max_cap_pipe2store_GWh_per_d'] = None
                    if math.isnan(ReturnComponent[ii].param['max_cap_store2pipe_GWh_per_d']):
                        ReturnComponent[ii].param['max_cap_store2pipe_GWh_per_d'] = None
                    if math.isnan(ReturnComponent[ii].param['max_workingGas_M_m3']):
                        ReturnComponent[ii].param['max_workingGas_M_m3'] = None
                    # Update screen with dot
                    print('.', end='')
                    keepPos. append(ii)
                    count = count + 1
                    if count > NumDataSets:
                        # Dealing with bad elemebtsm that did not return any URL results
                        tempNetz            = K_Netze.NetComp()
                        tempNetz.Storages   = ReturnComponent
                        tempNetz.select_byPos('Storages', keepPos)
                        ReturnComponent     = tempNetz.Storages
                        print(' ')
                        return ReturnComponent
                    
            except:
                print('Warning: M_GIE.read_component(Storages): reading URL failed')
                print('  for ', thisURL)
                
        # Dealing with bad elemebtsm that did not return any URL results
        tempNetz            = K_Netze.NetComp()
        tempNetz.Storages   = ReturnComponent
        tempNetz.select_byPos('Storages', keepPos)
        ReturnComponent     = tempNetz.Storages
        print(' ')
    return ReturnComponent
        

def replaceString(name_short):
    """Converting/removing certain strings.
    """
	
    name_short       = name_short.replace('LNG Termninal', '')
    name_short       = name_short.replace('LNG', '')
    name_short       = name_short.replace('Terminal', '')
    name_short       = name_short.replace('Offshore', '')
    name_short       = name_short.replace('VGS', '')
    name_short       = name_short.replace('_', '')
    name_short       = name_short.replace('-', '')
    name_short       = name_short.replace('â', '')
    name_short       = name_short.replace('?', '')
    name_short       = name_short.replace('Sch\udcf6nkirchen', 'Schoenkirchen')
    name_short       = name_short.replace(' ', '')
    name_short       = name_short.strip()
    name_short       = name_short.replace('UGS', '')
    name_short       = name_short.replace('Gas Storage', '')
    name_short       = name_short.replace('Storage', '')
    
    return name_short