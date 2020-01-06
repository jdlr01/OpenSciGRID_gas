# -*- coding: utf-8 -*-
"""
M_GasLib
--------
Summary of all functions that are needed for handling specific GasLib data sets.

"""
import Code.K_Netze      as K_Netze
import Code.K_Component  as K_Component
#import Code.M_Shape      as M_Shape
import os
import xml.etree.ElementTree as ET
from   pathlib         import Path

ID_Add = 'GL_'

def read(NumDataSets = 1e+100, RelDirName  = 'Eingabe/GasLib/', sourceName = None, RelDirNameInter = 'Eingabe/InternetDaten/'):
    """ Reading of GasLib data sets from XML files, with **RelDirName** indicating which directory to 
	read data from, **NumDataSets** maximum number of records to read. 

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
    
    # Initialization
    Ret_Data                = K_Netze.NetComp()
#    RelDirName              = Path(RelDirName)
    RelDirName              = os.path.join(os.getcwd(),RelDirName)
    print('Read from: ',RelDirName)
    
    # Reading Raw Data
    Ret_Data.Nodes           = read_component('Nodes',        NumDataSets = NumDataSets, RelDirName = RelDirName, sourceName = sourceName + '.net')
    Ret_Data.PipeSegments    = read_component('PipeSegments', NumDataSets = NumDataSets, RelDirName = RelDirName, sourceName = sourceName + '.net', Nodes = Ret_Data.Nodes)
    Ret_Data.Compressors     = read_component('Compressors',  NumDataSets = NumDataSets, RelDirName = RelDirName, sourceName = sourceName + '.net')
    Ret_Data.EntryPoints     = read_component('EntryPoints',  NumDataSets = NumDataSets, RelDirName = RelDirName, sourceName = sourceName + '.net')
       
    
    # Adding LatLong to all components        
    Ret_Data.add_latLong()


    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['PipeSegments', 'Compressors', 'EntryPoints', 'Nodes'])
    Ret_Data.remove_unUsedNodes()


    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)


    # Adding further essential attributess
    Ret_Data.fill_length('PipeSegments')
    Ret_Data.make_Attrib(['PipeSegments'], 'lat',  'lat_mean',  'mean')
    Ret_Data.make_Attrib(['PipeSegments'], 'long',  'long_mean',  'mean')


    # Adding SourceName
    Ret_Data.SourceName     = ['GasLib']
    
    return Ret_Data




def read_component(DataType = '', NumDataSets = 100000, RelDirName  = None, sourceName = None, Nodes = []):
    """ Reading in GasLib data sets from XML file, **NumDataSets** maximum number of records to read, 
	and **requeYear** for which year to get data. Relative path name of CSV file location is **RelDirName**.

    \n.. comments: 
    Input:
        DataType:        	string, containing the data type to read, e.g 'Nodes'.
        NumDataSets:     	number of data sets to be read in 
                            (Default = 100000). 
        RelDirName:      	string, containing directory name where GasLib data can be found
                            (Default = 'Eingabe/GSE/'). 
		sourceName:     	string containing an abbreviation for the source of the data.
                            (Default = None)
		Nodes: 				list of nodes. Obsolete!!!!
    Return:
	    []
    """
        
    ReturnComponent = []
    
    if 'GasLib-135' in sourceName:
        ID_Add = 'GL135_'
    elif 'GasLib-4197' in sourceName:
        ID_Add = 'GL4197_'
    elif 'GasLib-582-v2' in sourceName:
        XML_fileName    = os.path.join(RelDirName, sourceName)
        XML_fileName    = Path(XML_fileName)
        ID_Add = 'GL582_'
    elif 'GasLib-134-v2' in sourceName:
        XML_fileName    = os.path.join(RelDirName, sourceName)
        XML_fileName    = Path(XML_fileName)
        ID_Add = 'GL134_'
    else:
        print('ERROR: M_GasLib.read_component: sourceName not known. Program Terminates')
        return []
    schrott         = '{http://gaslib.zib.de/Gas}'
    XML_fileName    = os.path.join(RelDirName, sourceName)
    XML_fileName    = Path(XML_fileName)
    if 'Nodes'  in DataType:
        # Accessing the xml file
        tree = ET.parse(XML_fileName)
        root = tree.getroot()
        
        # going through each entry
        for child in root[1]:
            id              = child.attrib['id']
            node_id         = [id ]
            if 'alias' in child.attrib.keys():
                name            = child.attrib['alias']
            else: 
                name = []
            if len(name) == 0:
                name    = id
            lat             = float(child.attrib['geoWGS84Lat'])
            long            = float(child.attrib['geoWGS84Long'])
            source_id       = [ID_Add + id] 
            country_code    = 'DE'
            
            elevation_m        = None
            min_pressure_bar= None
            max_pressure_bar= None

            for kind in child:
                if 'height' == kind.tag.replace(schrott, ''):
                    elevation_m         = float(kind.attrib['value'])
                elif 'pressureMin' == kind.tag.replace(schrott, ''):
                    min_pressure_bar    = float(kind.attrib['value'])
                elif 'pressureMax' == kind.tag.replace(schrott, ''):
                    max_pressure_bar    = float(kind.attrib['value'])

            ReturnComponent.append(K_Component.Nodes(id = id, 
                                node_id             = node_id, 
                                name                = name, 
                                lat                 = lat, 
                                long                = long, 
                                source_id           = source_id, 
                                country_code        = country_code,
                                param               = {'elevation_m': elevation_m, 
                                'min_pressure_bar'  : min_pressure_bar, 
                                'max_pressure_bar'  : max_pressure_bar}))


    elif 'EntryPoints' in DataType:
        # Accessing the XML file
        tree = ET.parse(XML_fileName)
        root = tree.getroot()
        
        # going through each entry
        for child in root[1]:
            id              = child.attrib['id']
            if 'source' in id:
                node_id                     = [id ]
                name                        = child.attrib['alias']
                if len(name) == 0:
                    name    = id
                lat                         = float(child.attrib['geoWGS84Lat'])
                long                        = float(child.attrib['geoWGS84Long']) 
                source_id                   = [ID_Add + id] 
                country_code                = 'DE'
                
                elevation_m                 = None
                min_pressure_bar            = None
                max_pressure_bar            = None
                min_cap_M_m3_per_d          = None
                max_cap_M_m3_per_d          = None
                gasTemperature_C            = None
                calorificValue_MJ_per_m3    = None
                normDensity_kg_per_m3       = None
                coefficient_A_heatCapacity  = None
                coefficient_B_heatCapacity  = None
                coefficient_C_heatCapacity  = None
                molarMass_kg_per_kmol       = None
                pseudocriticalPressure      = None
                pseudocriticalTemperature   = None
                for kind in child:
                    if 'height' == kind.tag.replace(schrott, ''):
                        elevation_m                = float(kind.attrib['value'])
                    elif 'pressureMin' == kind.tag.replace(schrott, ''):
                        min_pressure_bar        = float(kind.attrib['value'])
                    elif 'pressureMax' == kind.tag.replace(schrott, ''):
                        max_pressure_bar        = float(kind.attrib['value'])
                    elif 'flowMin' == kind.tag.replace(schrott, ''):
                        min_cap_M_m3_per_d      = float(kind.attrib['value'])/1000*24
                    elif 'flowMax' == kind.tag.replace(schrott, ''):
                        max_cap_M_m3_per_d      = float(kind.attrib['value'])/1000*24
                    elif 'gasTemperature' == kind.tag.replace(schrott, ''):
                        gasTemperature_C        = float(kind.attrib['value'])
                    elif 'calorificValue' == kind.tag.replace(schrott, ''):
                        calorificValue_MJ_per_m3= float(kind.attrib['value'])
                    elif 'normDensity' == kind.tag.replace(schrott, ''):
                        normDensity_kg_per_m3   = float(kind.attrib['value'])
                    elif 'coefficient_A_heatCapacity' == kind.tag.replace(schrott, ''):
                        coefficient_A_heatCapacity  = float(kind.attrib['value'])
                    elif 'coefficient_B_heatCapacity' == kind.tag.replace(schrott, ''):
                        coefficient_B_heatCapacity  = float(kind.attrib['value'])
                    elif 'coefficient_C_heatCapacity' == kind.tag.replace(schrott, ''):
                        coefficient_C_heatCapacity  = float(kind.attrib['value'])
                    elif 'molarMass' == kind.tag.replace(schrott, ''):
                        molarMass_kg_per_kmol         = float(kind.attrib['value'])
                    elif 'pseudocriticalPressure' == kind.tag.replace(schrott, ''):
                        pseudocriticalPressure  = float(kind.attrib['value'])
                    elif 'pseudocriticalTemperature' == kind.tag.replace(schrott, ''):
                        pseudocriticalTemperature  = float(kind.attrib['value'])
                
            
                ReturnComponent.append(K_Component.EntryPoints(id = id, 
                                    node_id                     = node_id, 
                                    name                        = name, 
                                    lat                         = lat, 
                                    long                        = long, 
                                    source_id                   = source_id, 
                                    country_code                = country_code,
                                    param                       = {'elevation_m': elevation_m, 
                                    'min_pressure_bar'          : min_pressure_bar, 
                                    'max_pressure_bar'          : max_pressure_bar,
                                    'min_cap_M_m3_per_d'        : min_cap_M_m3_per_d, 
                                    'max_cap_M_m3_per_d'        : max_cap_M_m3_per_d, 
                                    'gasTemperature_C'          : gasTemperature_C,
                                    'calorificValue_MJ_per_m3'  : calorificValue_MJ_per_m3, 
                                    'normDensity_kg_per_m3'     : normDensity_kg_per_m3,
                                    'coefficient_A_heatCapacity': coefficient_A_heatCapacity, 
                                    'coefficient_B_heatCapacity': coefficient_B_heatCapacity, 
                                    'coefficient_C_heatCapacity': coefficient_C_heatCapacity, 
                                    'molarMass_kg_per_kmol'     : molarMass_kg_per_kmol, 
                                    'pseudocriticalPressure'    : pseudocriticalPressure,
                                    'pseudocriticalTemperature' : pseudocriticalTemperature}))


        
    elif 'PipeSegments' in DataType:
        # Initialization
        tree    = ET.parse(XML_fileName)
        root    = tree.getroot()
        schrott = '{http://gaslib.zib.de/Gas}'
        # disecting entries from XML file        
        for child in root[2]:
            id                      = child.attrib['id']
            node_id                = [child.attrib['from'], child.attrib['to']]
            name                    = child.attrib['alias']
            if len(name) == 0:
                name    = id
            source_id               = [ID_Add + id]
            country_code            = 'DE'
            max_pressure_bar        = None
            min_cap_M_m3_per_d      = None
            max_cap_M_m3_per_d      = None
            length                  = None
            diameter_mm             = None
            roughness_mm            = None
            heatTransferCoefficient_W_per_m2_per_K = None
            for kind in child:
                if 'flowMin' == kind.tag.replace(schrott, ''):
                    min_cap_M_m3_per_d  = float(kind.attrib['value'])/1000*24
                elif 'flowMax' == kind.tag.replace(schrott, ''):
                    max_cap_M_m3_per_d  = float(kind.attrib['value'])/1000*24
                elif 'length' == kind.tag.replace(schrott, ''):
                    length           = float(kind.attrib['value'])
                elif 'diameter' == kind.tag.replace(schrott, ''):
                    diameter_mm         = float(kind.attrib['value'])
                elif 'roughness' == kind.tag.replace(schrott, ''):
                    roughness_mm        = float(kind.attrib['value'])
                elif 'pressure' == kind.tag.replace(schrott, ''):
                    max_pressure_bar    = float(kind.attrib['value'])
                elif 'heatTransferCoefficient' == kind.tag.replace(schrott, ''):
                    heatTransferCoefficient_W_per_m2_per_K = float(kind.attrib['value'])



            
            ReturnComponent.append(K_Component.PipeSegments( id = id, name = name, 
                            source_id           = source_id, 
                            node_id             = node_id, 
                            country_code        = country_code, 
                            param               = {'max_pressure_bar': max_pressure_bar, 
                            'min_cap_M_m3_per_d': min_cap_M_m3_per_d, 
                            'max_cap_M_m3_per_d': max_cap_M_m3_per_d, 
                            'length'            : length, 
                            'diameter_mm'       : diameter_mm, 
                            'roughness_mm'      : roughness_mm, 
                            'heatTransferCoefficient_W_per_m2_per_K' : heatTransferCoefficient_W_per_m2_per_K}))


    elif 'Compressors' in DataType:
        # Initialization
        tree    = ET.parse(XML_fileName)
        root    = tree.getroot()
        # disecting entries from XML file        
        # going through each entry
        for child in root[2]:
            id              = child.attrib['id']
            if 'compressorStation' in id:
                node_id                     = [child.attrib['from'] ]
                source_id                   = [ID_Add + id]
                country_code                = 'DE'
                name                        = child.attrib['alias']
                if len(name) == 0:
                    name    = id
                from_node                   = child.attrib['from'] 
                to_node                     = child.attrib['to'] 
                energy_node                 = child.attrib['fuelGasVertex'] 
                
                loss_pressure_pipe2comp_bar = None
                loss_pressure_comp2pipe_bar = None
                min_pressure_pipe2comp_bar  = None
                max_pressure_comp2pipe_bar  = None
                diameter_pipe2comp_mm       = None
                diameter_comp2pipe_mm       = None
                dragFactor_pipe2comp        = None
                dragFactor_comp2pipe        = None
                min_cap_M_m3_per_d          = None
                max_cap_M_m3_per_d          = None
                # has_gasCooler
                has_gasCooler               = float(child.attrib['gasCoolerExisting'])
                # internalBypassRequired
                internalBypassRequired      = float(child.attrib['internalBypassRequired'])
                
                for kind in child:
                    if 'flowMin' == kind.tag.replace(schrott, ''):
                        min_cap_M_m3_per_d  = float(kind.attrib['value'])/1000*24
                    elif 'flowMax' == kind.tag.replace(schrott, ''):
                        max_cap_M_m3_per_d  = float(kind.attrib['value'])/1000*24
                        
                    elif 'pressureLossIn' == kind.tag.replace(schrott, ''):
                        loss_pressure_pipe2comp_bar     = float(kind.attrib['value'])
                    elif 'pressureLossOut' == kind.tag.replace(schrott, ''):
                        loss_pressure_comp2pipe_bar     = float(kind.attrib['value'])
                    elif 'pressureInMin' == kind.tag.replace(schrott, ''):
                        min_pressure_pipe2comp_bar      = float(kind.attrib['value'])
                    elif 'pressureOutMax' == kind.tag.replace(schrott, ''):
                        max_pressure_comp2pipe_bar      = float(kind.attrib['value']) 
                    elif 'diameterIn' == kind.tag.replace(schrott, ''):
                        diameter_pipe2comp_mm      = float(kind.attrib['value'])   
                    elif 'diameterOut' == kind.tag.replace(schrott, ''):
                        diameter_comp2pipe_mm      = float(kind.attrib['value'])
                    elif 'dragFactorIn' == kind.tag.replace(schrott, ''):
                        dragFactor_pipe2comp      = float(kind.attrib['value'])
                    elif 'dragFactorOut' == kind.tag.replace(schrott, ''):
                        dragFactor_comp2pipe      = float(kind.attrib['value'])

            
                ReturnComponent.append(K_Component.Compressors( id = id, 
                                name                        = name, 
                                source_id                   = source_id,  
                                node_id                     = node_id, 
                                country_code                = country_code,
                                param                       = {'from_node': from_node, 
                                'to_node'                   : to_node, 
                                'has_gasCooler'             : has_gasCooler, 
                                'energy_node'               : energy_node, 
                                'loss_pressure_pipe2comp_bar': loss_pressure_pipe2comp_bar, 
                                'loss_pressure_comp2pipe_bar': loss_pressure_comp2pipe_bar, 
                                'min_pressure_pipe2comp_bar': min_pressure_pipe2comp_bar, 
                                'max_pressure_comp2pipe_bar': max_pressure_comp2pipe_bar, 
                                'diameter_pipe2comp_mm'     : diameter_pipe2comp_mm,
                                'diameter_comp2pipe_mm'     : diameter_comp2pipe_mm,
                                'dragFactor_pipe2comp'      : dragFactor_pipe2comp,
                                'dragFactor_comp2pipe'      : dragFactor_comp2pipe,
                                'internalBypassRequired'    : internalBypassRequired}))

    return ReturnComponent
        

