# -*- coding: utf-8 -*-
"""
M_GSE
-----
Summary of all functions that are needed for handling specific GIE data set sets

"""
import Code.M_Helfer     as M_Helfer
import Code.K_Netze      as K_Netze
import Code.K_Component  as K_Component
import Code.M_Internet   as M_Internet
import Code.M_Netze      as M_Netze
import Code.M_Shape      as M_Shape
import Code.M_Matching   as M_Matching
import Code.JoinNetz     as JoinNetz
from   pathlib         import Path

ID_Add = 'GSE_'

def read( NumDataSets = 1e+100, requeYear = '2000', RelDirName  = 'Eingabe/GSE/', RelDirNameInter = 'Eingabe/InternetDaten/'):
    """ Reading in GIE data sets from API, with **DirName** indicating which directory to 
	store data to, **NumDataSets** maximum number of records to read, and **requeYear** for 
	which year to get data. **RelDirName** is relative path name of where CSV files can be found.

    \n.. comments: 
    Input:
        NumDataSets:    	number of data sets
                            (default = 100000) 
		requeYear: 			string containing year [####] for which data to be retrieved
                            (default = '2000') 
        RelDirName:     	string, containing dir name where GIE meta data
                            (default = 'Eingabe/GSE/')
    Return:
	    Ret_Data:      Instance of K_Netze.NetComp class, with components Nodes and Storages populated.
    """
    
    Ret_Data                = K_Netze.NetComp()
    Nodes                   = []
    Storages                = []
    RelDirName              = Path(RelDirName)
        
    # Reading Raw Data
    Storages   = read_component('Storages', NumDataSets = NumDataSets, requeYear = requeYear, RelDirName = RelDirName)

    # Generation of additional components
    Nodes      = gen_component('Nodes', Storages)   # check this one        
    
       
        
    Ret_Data.Nodes                  = Nodes
    Ret_Data.Storages               = Storages
    
    if RelDirNameInter != None:
        Netz_Internet       = K_Netze.NetComp()
        RelDirNameInter     = Path(RelDirNameInter)
        
        Netz_Internet.Nodes = M_Internet.read_component("Nodes",  NumDataSets, 0, RelDirName = RelDirNameInter)
        
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = JoinNetz.match(
            Netz_Internet, Ret_Data, compName = 'Nodes', threshold = 80, multiSelect = True,  
            funcs = lambda comp_0, comp_1: M_Matching.getMatch_Names_CountryCode(comp_0, comp_1, AddInWord = 100), numFuncs = 1)

        if len(pos_add_Netz_1)> 0:
            print('WARNING: M_GSE.read(): ' + str(len(pos_add_Netz_1)) + ' from ' + str(len(Ret_Data.Storages)) + ' locations could not be GeoReferenced.')
        else:
            print('Comment: M_GSE.read(): All locations were GeoReferenced.')
            
        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'lat',  Ret_Data,'Nodes', 'lat', pos_match_Netz_0,  pos_match_Netz_1)
        Ret_Data = M_Netze.copy_Vals(Netz_Internet, 'Nodes', 'long', Ret_Data,'Nodes', 'long', pos_match_Netz_0, pos_match_Netz_1)
        Ret_Data = M_Netze.copy_ParamVals(Netz_Internet, 'Nodes', 'exact', Ret_Data,'Nodes', 'exact', pos_match_Netz_0, pos_match_Netz_1)
        
        # Adding lat long to all component elements
        Ret_Data.add_latLong()



    # Unit conversion
    Ret_Data.MoveUnits('Storages', 'max_cap_pipe2store_GWh_per_d', 'max_cap_pipe2store_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Storages', 'max_cap_store2pipe_GWh_per_d', 'max_cap_store2pipe_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Storages', 'max_workingGas_TWh',           'max_workingGas_M_m3', replace = True)


    # Removing attributes
    Ret_Data.removeAttrib('Nodes',    ['name_short', 'operator_name', 'start_year', 'status'])
    Ret_Data.removeAttrib('Nodes',    ['max_cap_pipe2store_GWh_per_d', 'max_cap_store2pipe_GWh_per_d', 'max_workingGas_TWh'])
    Ret_Data.removeAttrib('Storages', ['max_cap_pipe2store_GWh_per_d', 'max_cap_store2pipe_GWh_per_d', 'max_workingGas_TWh'])
    
    
    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['Storages', 'Nodes'])
    Ret_Data.remove_unUsedNodes()
 
    
    
    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)
 
    
    # Adding SourceName
    Ret_Data.SourceName     = ['GSE']

    return Ret_Data




def gen_component(dataType, CompIn):
    """ Generates a netz component from existing components of this netz, e.g. generation of of 
	nodes list from Segments.  Component name to be generated suplied as string **dataType**, 
	with current options implemented *Nodes* Data supplied via component **CompIn**.

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
                        country_code = comp.country_code, 
                        lat         = comp.lat, 
                        long        = comp.long, 
                        source_id   = comp.source_id, 
                        param       = {'name_short' : comp.param['name_short'], 
                        'operator_name'             : comp.param['operator_name'], 
                        'status'                    : comp.param['status'], 
                        'start_year'                : comp.param['start_year'], 
                        'max_cap_store2pipe_GWh_per_d': comp.param['max_cap_store2pipe_GWh_per_d'],
                        'max_cap_pipe2store_GWh_per_d': comp.param['max_cap_pipe2store_GWh_per_d'], 
                        'max_workingGas_TWh'        : comp.param['max_workingGas_TWh']}))
    
    return Nodes




def read_component(DataType = '', NumDataSets = 100000, requeYear = '', RelDirName  = None):
    """ Reading in GIE LNGs data sets from API, **NumDataSets** maximum number of records to read, 
	and **requeYear** for which year to get data. Relative path name of CSV file location is **RelDirName**.

    \n.. comments: 
    Input:
        DataType:        	string, containing the data type to read, otions are 'LNGs' or 'Storages'
        NumDataSets:     	number of data sets to be read in 
                            (default = 100000) 
		requeYear: 		 	string containing year [####] for which data to be retrieved
                            (default = '2000')
        RelDirName:      	string, containing dir name where GIE meta data
                            (default = 'Eingabe/GSE/') 
    Return:
	    ReturnComponent:	list of elements of a single component.
    """
        
    ReturnComponent = []

    if'Storages'  in DataType:
        # Initialization
        count       = 0
        
        FileName = str(RelDirName / 'GSE_Storage.csv')
            
        # Reading Meta data from CSV file
        # connecting to CSV file
        FileEncoding = "ISO-8859-15"  # "utf8"
        fid         = open(FileName, "r", encoding = FileEncoding, errors = 'ignore')
        # Reading hearder line
        for ii in range(23):
            fid.readline()
        # Reading next line
        temp        = M_Helfer.strip_accents(fid.readline()[:-1])
        while (len(temp) > 0) and (count <NumDataSets):
            Save                    = False
            country_code            = temp.split(';')[2]
            operator_name           = temp.split(';')[5]
            name                    = temp.split(';')[6]
            id                      = temp.split(';')[6]
            id                      = id.replace("'", ' ')
            node_id                 = [id]
            source_id               = [ID_Add + str(id)]
            status                  = temp.split(';')[7]
            
            # start_year
            start_year              = temp.split(';')[9]
            if len(start_year) == 0:
                start_year  = None
                Save        = True
            else:
                start_year   = int(start_year)
                if requeYear == '':
                    Save    = True
                elif start_year <= int(requeYear):
                    Save    = True
                
            # max_workingGas_TWh
            max_workingGas_TWh      = temp.split(';')[14]
            if len(max_workingGas_TWh) == 0:
                max_workingGas_TWh = None
            else:
                max_workingGas_TWh = float(max_workingGas_TWh)
                
            # max_cap_store2pipe_GWh_per_d 
            max_cap_store2pipe_GWh_per_d     = temp.split(';')[16]
            if len(max_cap_store2pipe_GWh_per_d) == 0:
                max_cap_store2pipe_GWh_per_d = None
            else:
                max_cap_store2pipe_GWh_per_d = float(max_cap_store2pipe_GWh_per_d)
                
            # max_cap_pipe2store_GWh_per_d    
            max_cap_pipe2store_GWh_per_d    = temp.split(';')[20]
            if len(max_cap_pipe2store_GWh_per_d) == 0:
                max_cap_pipe2store_GWh_per_d    = None
            else:
                max_cap_pipe2store_GWh_per_d    = float(max_cap_pipe2store_GWh_per_d)
                
            is_inEU                    = temp.split(';')[25]
            # is_inEU
            if is_inEU.lower() == 'yes':
                is_inEU    = True
            else:
                is_inEU    = False
                
                
            inEUMember              = temp.split(';')[23]
            
            if 'y' ==  inEUMember and is_inEU == True and Save:
                name_short       = name
                name_short       = name_short.replace('SERENE Nord: ', '')
                name_short       = name_short.replace('VGS SEDIANE B: ', '')
                name_short       = name_short.replace('SERENE SUD', '')
                name_short       = name_short.replace('SEDIANE LITTORAL:', '')
                name_short       = name_short.replace('(XIV-XV)', '')
                name_short       = name_short.replace('(Atwick)', '')
                name_short       = name_short.replace('SEDIANE: ', '')
                name_short       = name_short.replace('GSF ', '')
                name_short       = name_short.replace('VGS ', '')
                name_short       = name_short.replace('Eneco', '')
                name_short       = name_short.replace('Uniper', '')
                name_short       = name_short.replace('HGas', 'H')
                name_short       = name_short.replace('LGas', 'L')
                name_short       = name_short.replace('H-Gas', 'H')
                name_short       = name_short.replace('L-Gas', 'L')
                name_short       = name_short.replace('complex', '')
                name_short       = name_short.replace('Trianel', '')
                name_short       = name_short.replace('Offshore', '')
                name_short       = name_short.replace('/', '')
                name_short       = name_short.replace('-', '')
                name_short       = name_short.replace('?', '')
                name_short       = name_short.replace(':', '')
                name_short       = name_short.replace('\'', '')
                name_short       = name_short.replace('t', 'T')
    
                name_short       = name_short.replace(' ', '')
    
    
#'operator_name': operator_name, 
#'status'    : status,     
# 'start_year': start_year, 
                ReturnComponent.append(K_Component.Storages(name = name, 
                                id          = id,
                                node_id     = node_id, 
                                country_code = country_code, 
                                lat         = None, 
                                long        = None, 
                                source_id   = source_id, 
                                param       = {'name_short': name_short,
                                'max_cap_store2pipe_GWh_per_d': max_cap_store2pipe_GWh_per_d, 
                                'max_cap_pipe2store_GWh_per_d': max_cap_pipe2store_GWh_per_d, 
                                'max_workingGas_TWh':  max_workingGas_TWh}))
                count           = count + 1
                # Reading next line
            temp    = M_Helfer.strip_accents(fid.readline()[:-1])
    
    return ReturnComponent
        

