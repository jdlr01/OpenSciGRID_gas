# -*- coding: utf-8 -*-
"""
M_GIE
-----
Summary of all functions that are needed for handling specific GIE data set sets

"""
import Code.M_Helfer     as M_Helfer
import Code.K_Netze      as K_Netze
import Code.K_Component  as K_Component
import Code.M_Internet   as M_Internet
import Code.M_Netze      as M_Netze 
import Code.M_Matching   as M_Matching
import Code.M_Shape      as M_Shape
import Code.JoinNetz     as JoinNetz
import time              as time
import random            as random
from   pathlib       import Path
from   bs4           import BeautifulSoup
import Code.C_colors     as CC
import urllib3
import certifi

ID_Add  = 'GIE_'


def read( NumDataSets = 100000, requeYear = '2000', RelDirName = '', RelDirNameInter = 'Eingabe/InternetDaten/'):
    """ Reading in GIE data sets from API, with **RelDirName** indicating which directory from where to 
    load the data from, **NumDataSets** maximum number of records to read, and **requeYear** for which 
    year to get data.

    \n.. comments: 
    Input:
        NumDataSets:    	number of data sets
							(default = 100000) 
		requeYear: 			string containing year [####] for which data to be retrieved
							(default = '2000') 
        RelDirName:     	string, of relative directory name where GIE meta data is loaded from
    Return:
	    Ret_Data: 	 	Data structure of components
    """
    
    Ret_Data   = K_Netze.NetComp()
    Storages   = []
    
    # Reading Raw Data
    Storages    = read_component('Storages', NumDataSets, requeYear)

    # Generation of additional components
    Nodes       = gen_component('Nodes', Storages)       # check this one

    # Assigning data to output Struct        
    Ret_Data.Nodes      = Nodes
    Ret_Data.Storages   = Storages
    

    # Adding lat long if Netz_Internet supplied
    if len(RelDirNameInter) > 0:
        RelDirNameInter     = Path(RelDirNameInter)
        Netz_Internet       = K_Netze.NetComp()
        Netz_Internet.Nodes = M_Internet.read_component("Nodes",  1e+100, 0, RelDirName = RelDirNameInter)
        
        
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = JoinNetz.match(
            Netz_Internet, Ret_Data, compName = 'Nodes', threshold = 75, multiSelect = True,  
            funcs = lambda comp_0, comp_1: M_Matching.getMatch_Names_CountryCode(comp_0, comp_1, AddInWord = 100), numFuncs = 1)

        if len(pos_add_Netz_1)> 0:
            print('WARNING: M_IGU.read(): ' + str(len(pos_add_Netz_1)) + ' from ' + str(len(Ret_Data.Storages)) + ' locations could not be GeoReferenced.')
        else:
            print('Comment: M_IGU.read(): All locations could were GeoReferenced.')

        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'lat',  Ret_Data,'Nodes', 'lat', pos_match_Netz_0,  pos_match_Netz_1)
        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'long', Ret_Data,'Nodes', 'long', pos_match_Netz_0, pos_match_Netz_1)
        Ret_Data = M_Netze.copy_ParamVals(Netz_Internet, 'Nodes', 'exact', Ret_Data,'Nodes', 'exact', pos_match_Netz_0, pos_match_Netz_1)
        
        Ret_Data.add_latLong()
    
    
    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['Storages', 'Nodes'])
    Ret_Data.remove_unUsedNodes()


    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)
    
    # Adding SourceName
    Ret_Data.SourceName             = ['IGU']


    return Ret_Data




def gen_component(dataType, CompIn):
    """ Generates a netz component from existing components of this netz, e.g. generation 
	of of nodes list from Segments.  Component name to be generated suplied as string 
	**dataType**, with current options implemented *Nodes* Data supplied via component **CompIn**.

    \n.. comments:
    Input:
        dataType:        string containing name of component to be created e.g. 'Nodes' 
        CompIn:          netz class instance
    Return:
        ReturnComponent: component list.  
    """

    Nodes = []
    if 'Nodes' == dataType:
        for comp in CompIn:
            Nodes.append( K_Component.Nodes( id = comp.id, 
                        node_id     = comp.node_id, 
                        name        = comp.name, 
                        source_id   = comp.source_id,  
                        country_code = comp.country_code, 
                        lat         = None, 
                        long        = None))
    
    return Nodes




def read_component(DataType = 'Storages', NumDataSets = 100000, requeYear = ['2000']):
    """ Reading in GIE LNGs data sets from API, **NumDataSets** maximum number of records to read, 
	and **requeYear** for which year to get data. **RelDirName** is the relative path name.

    \n.. comments: 
    Input:
        DataType:        	string, containing the data type to read, options are 'LNGs' or 'Storages'
							(Default = 'Storages')
        NumDataSets:      	number of data sets
							(Default =  100000)
		requeYear: 			list of string containing year [####] for which data to be retrieved
							(Default = '2000')
        RelDirName:     	string, containing relative dir name where GIE meta data
							(default = 'Eingabe/GIE/')
    Return:
	    ReturnComponent:	Data structure of IGU data.
    """
        
    ReturnComponent = []

    
    if 'Storages'  in DataType:
        # Initialization
        webCall_1   = 'http://members.igu.org/html/wgc2003/WGC_pdffiles/data/Europe/att/UGS_'

        # Creation of a Pool Manager
        http        = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
        # Reading for all created storages the data off the web page
        maxSets     = min([169, NumDataSets])
                
        for nn in range(maxSets):
            time.sleep(0.001 + random.randint(1,100)/100000)
            # information from CSV file
            thisURL     = webCall_1 + str(nn) + '.html' 
            # Get the data
            URLData     = http.request('GET', thisURL)
                
            # Convert the data into dict
            try:
                if 'Application Error' not in str(URLData.data) and 'Appliance Error' not in str(URLData.data) and '404 Not Found</title>' not in str(URLData.data) :
                    soup                            = BeautifulSoup(URLData.data, 'html.parser')
                    
                    ii = -0.5
                    for td in soup.find_all('td'):
                        if ii == 0:
                            id              = td.font.string.replace('\n', '').strip()
                            source_id       = ['IGU_' + str(id)]
                            node_id         = [id] # Stimmt das??
                            
                        elif ii == 1:
                            name            = replaceString(td.font.string.replace('\n', '').strip())
                            id              = name
                            node_id         = [id]
                            
                            
                        elif ii == 2:
                            is_abandoned 	= td.font.string.replace('\n', '').strip()
                            if 'in operation' == is_abandoned:
                                is_abandoned = False
                            else:
                                is_abandoned = True
                                
                        elif ii == 3:
                            country_code     = M_Helfer.countryName2TwoLetter(td.font.string.replace('\n', '').strip())  # Germany
                            
                        elif ii == 4:
                            store_type       = td.font.string.replace('\n', '').strip() 	# Oil/Gasfield
                            
                        elif ii == 5:
                            operator_name    = td.font.string.replace('\n', '').strip() 	# BEB
                            
                        elif ii == 6:
                            wert             = td.font.string.replace('\n', '').replace(',','.').strip()
                            if '/' in wert:
                                wert         = M_Helfer.string2floats(wert.replace('/', ' '))
                                start_year   = wert[0]
                            elif 'Jan. ' in wert:
                                wert         = wert.replace('Jan. ', '')
                                start_year   = float(wert)
                            elif len(wert)>0:
                                start_year   = float(wert)       # 2001
                            else:
                                start_year   = None              # 2001
                                
                        elif ii == 7:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert)>0:
                                max_workingGas_M_m3         = float(wert)
                            else:
                                max_workingGas_M_m3         = None              # [mill m³] 	2025
                                
                        elif ii == 8:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert)>0:
                                max_cushionGas_M_m3  = float(wert)              # [mill m³] 	2358
                            else:
                                max_cushionGas_M_m3  = None                     # [mill m³] 	2358
                                
                        elif ii == 9:
                            wert  = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert)>0:
                                max_cap_store2pipe_M_m3_per_d         = float(wert)/1000*24
                            else:
                                max_cap_store2pipe_M_m3_per_d         = None    # Peak withdrawal capacity [10³ m³/h] 	840
                                
                        elif ii == 10:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()  # Injection capacity [10³ m³/h] 	810
                            if len(wert)>0:
                                max_cap_pipe2store_M_m3_per_d          = float(wert)/1000*24
                            else:
                                max_cap_pipe2store_M_m3_per_d          = None
                                
                        elif ii == 11:
                            wert      = td.font.string.replace('\n', '').strip()  # Storage formation 	Solling sandstone middle Bunter
                            if wert == '---':
                                storage_formation    = None
                            elif wert == '':
                                storage_formation    = None
                            else:
                                storage_formation    = wert
                                
                        elif ii == 12:
                            wert       = td.font.string.replace('\n', '').replace(',','.').strip()  # Storage formation 	Solling sandstone middle Bunter
                            if len(wert)>0:
                                structure_depth_m           = float(wert)       # Depth top structure, resp. cavern roof [m] 	2650
                            else:
                                structure_depth_m           = None              # Depth top structure, resp. cavern roof [m] 	2650
                                
                        elif ii == 13:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert) > 0:
                                min_storage_pressure_bphBar = float(wert)       # Min storage pressure [BHP bar] 	90
                            else:
                                min_storage_pressure_bphBar = None
                                
                        elif ii == 14:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert) > 0:
                                max_storage_pressure_bphBar = float(wert)       # Max allowable storage pressure [BHP bar] 	460
                            else:
                                max_storage_pressure_bphBar = None
                                
                        elif ii == 15:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if wert== '---':
                                net_thickness_m             = None              # Net thickness [m] 	22
                            elif '..' in wert:
                                wert = M_Helfer.string2floats(wert.replace('..', ' '))
                                net_thickness_m             = sum(wert)/float(len(wert))
                            elif '/' in wert:
                                wert = M_Helfer.string2floats(wert.replace('/', ' '))
                                net_thickness_m             = sum(wert)/float(len(wert))
                            elif ' - ' in wert:
                                wert = M_Helfer.string2floats(wert.replace(' - ', ' '))
                                net_thickness_m             = sum(wert)/float(len(wert))
                            elif '-' in wert:
                                wert = M_Helfer.string2floats(wert.replace('-', ' '))
                                net_thickness_m             = sum(wert)/float(len(wert))
                            elif len(wert) > 0:
                                net_thickness_m             = float(wert)       # Net thickness [m] 	22
                            else:
                                net_thickness_m             = None              # Net thickness [m] 	22
                                
                        elif ii == 16:
                            wert                   = td.font.string.replace('\n', '').replace(',','.').strip()  # Porosity [%] 	22
                            if wert == '---':
                                porosity_perc = None
                            elif len(wert) == 0:
                                porosity_perc = None
                            elif '(' in wert and ')' in wert:
                                wert            = M_Helfer.string2floats(wert.replace('(', '').replace(')', '').replace(' - ', ' '))
                                porosity_perc   = sum(wert)/float(len(wert))                           
                            elif ' - ' in wert:
                                wert            = M_Helfer.string2floats(wert.replace(' - ', ' '))
                                porosity_perc   = sum(wert)/float(len(wert))
                            elif '/' in wert:
                                wert            = M_Helfer.string2floats(wert.replace('/', ' '))
                                porosity_perc   = sum(wert)/float(len(wert))
                            elif ' -' in wert:
                                wert            = wert.replace(' -', ' ')
                                if len(wert)>1:
                                    wert            = M_Helfer.string2floats(wert)
                                    porosity_perc   = sum(wert)/float(len(wert))
                                else:
                                    porosity_perc   = None
                            elif '-' in wert:
                                wert            = wert.replace('-', ' ')
                                if len(wert)>1:
                                    wert            = M_Helfer.string2floats(wert)
                                    porosity_perc   = sum(wert)/float(len(wert))
                                else:
                                    porosity_perc   = None
                            else:
                                porosity_perc = wert
                                
                        elif ii == 17:
                            wert            = td.font.string.replace('\n', '').replace(',','.').strip().replace(' mD','')  # Permeability [mD] 	10 - 1000 (500)
                            if wert == '---':
                                permeability_mD = None
                            elif len(wert) == 0:
                                permeability_mD = None
                            elif '(' in wert and ')' in wert:
                                wert            = M_Helfer.string2floats(wert.replace('(', '').replace(')', '').replace(' - ', ' '))
                                permeability_mD = sum(wert)/float(len(wert))                           
                            elif ' - ' in wert:
                                wert            = M_Helfer.string2floats(wert.replace(' - ', ' '))
                                permeability_mD = sum(wert)/float(len(wert))
                            elif '-' in wert:
                                wert            = wert.replace('-', ' ')
                                if len(wert) > 1:
                                    wert            = M_Helfer.string2floats(wert)
                                    permeability_mD = sum(wert)/float(len(wert))
                                else:
                                    permeability_mD  = None
                                    
                            elif '/' in wert:
                                wert            = M_Helfer.string2floats(wert.replace('/', ' '))
                                permeability_mD = sum(wert)/float(len(wert))
                            else:
                                permeability_mD = wert
                                
                        elif ii == 18:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert) > 0:
                                num_storage_wells           = int(wert)         # No of storage wells, resp. caverns 	15
                            else:
                                num_storage_wells           = None              # No of storage wells, resp. caverns 	15
                                
                        elif ii == 19:
                            wert                            = td.font.string.replace('\n', '').replace(',','.').strip()
                            if len(wert) > 0:
                                max_power_MW              = float(wert)         # Installed compressor power [MW] 
                            else:
                                max_power_MW              = None                # Installed compressor power [MW] 
    
                        ii = ii + 0.5
                            
                    if len(country_code) > 0 and is_abandoned == False:
                        # creating of component Storage
                        ReturnComponent.append(K_Component.Storages(id = id, 
                                            name        = name, 
                                            node_id     = node_id, 
                                            source_id   = source_id, 
                                            country_code = country_code, 
                                            lat         = None, 
                                            long        = None,
                                            param       = {'store_type'        : store_type,
                                            'operator_name'     : operator_name, 
                                            'start_year'        : start_year, 
                                            'max_workingGas_M_m3': max_workingGas_M_m3, 
                                            'max_cushionGas_M_m3': max_cushionGas_M_m3, 
                                            'storage_formation' : storage_formation, 
                                            'structure_depth_m' : structure_depth_m, 
                                            'net_thickness_m'   : net_thickness_m,
                                            'porosity_perc'     : porosity_perc,
                                            'permeability_mD'   : permeability_mD,
                                            'num_storage_wells' : num_storage_wells,
                                            'max_power_MW'      : max_power_MW,
                                            'max_cap_store2pipe_M_m3_per_d': max_cap_store2pipe_M_m3_per_d,
                                            'max_cap_pipe2store_M_m3_per_d': max_cap_pipe2store_M_m3_per_d, 
                                            'min_storage_pressure_bphBar': min_storage_pressure_bphBar, 
                                            'max_storage_pressure_bphBar': max_storage_pressure_bphBar}))
                        if len(ReturnComponent) == 7:
                            pass
                            
            except:
                print(CC.Warning+'Warning: M_IGU.read_component: reading URL failed'+CC.End)
                pass
        
    return ReturnComponent
        


def replaceString(name_short):
    """Function replacing parts of a string with Umlaute into 
    non-Umlaute
	
    \n.. comments: 
    Input:
		name_short:		String 
    Input:
		name_short:		String without Umlaute 
    """
    name_short       = name_short.replace('ü', 'ue')
    name_short       = name_short.replace('ö', 'oe')
    name_short       = name_short.replace('ä', 'ae')
    
    return name_short


