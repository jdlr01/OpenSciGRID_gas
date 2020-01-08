# -*- coding: utf-8 -*-
"""
M_Internet
----------
Summary of all functions that are needed for handling specific Internet data sets

"""
import Code.K_Netze      as K_Netze
import Code.K_Component  as K_Component
import Code.M_FindPos    as M_FindPos
import Code.M_Filter     as M_Filter
import Code.M_Helfer     as M_Helfer
from   pathlib       import Path
import os.path
import csv
from collections     import namedtuple

typemap = {
    'REAL': float,
    'TEXT': str,
    'INT': float,
}
ID_Add      = str('IN_')



def read( NumDataSets = 100000, requeYear = '', licenseType = '', GasType = 'H', RelDirName = 'Eingabe/InternetDaten/'):
    """ Reading in Internet data sets from CSV file, with  
    **NumDataSets** maximum number of records to read, and **requeYear** for which year to get data.
    
    \n.. comments: 
    Input:
        NumDataSets:    (Optional = 100000) number of data sets
		requeYear: 		(Optional = '2010') string containing year [####] for which data to be retrieved
        licenseType:    (Otopmnal = ''), string containing the kind of license that the data will be selected on
        GasType:        (Optional = 'H') a character indicating either H or L gas.
        RelDirName:     string, containing the relatie dir name where the Internet data can be loaded from.
    Return:
	    []
    """
    
    Filter      =	{"year": requeYear, "license": licenseType, "GasType": GasType}
    Ret_Data    = K_Netze.NetComp()
    MD          = K_Component.MetaData()
    RelDirName  = Path(RelDirName)

    # Reading Raw Data
    Ret_Data.Nodes                   = read_component("Nodes",          NumDataSets, 0, RelDirName = RelDirName)
    Ret_Data.BorderPoints            = read_component("BorderPoints",   NumDataSets, 0, RelDirName = RelDirName)
    Ret_Data.Compressors             = read_component("Compressors",    NumDataSets, 0, RelDirName = RelDirName)
    #Ret_Data.Consumers               = read_component("Consumers",      NumDataSets, 0, RelDirName = RelDirName)
    Ret_Data.EntryPoints             = read_component("EntryPoints",    NumDataSets, 0, RelDirName = RelDirName)
    Ret_Data.InterConnectionPoints   = read_component("InterConnectionPoints", NumDataSets, 0, RelDirName = RelDirName)
    Ret_Data.LNGs                    = read_component("LNGs",           NumDataSets, 0, RelDirName = RelDirName)
    Ret_Data.Storages                = read_component("Storages",       NumDataSets, 0, RelDirName = RelDirName)
    
    Ret_Data.PipeLines               = read_PipeLines(NumDataSets, RelDirName = RelDirName)
    
    
    # Meta Data 
    [MD.BorderPoints_Meta, MD.BorderPoints_Meta_Type, MD.BorderPoints_Meta_Name, MD.BorderPoints_methodName] = read_Meta("BorderPoints", RelDirName = RelDirName)
    [MD.Compressors_Meta, MD.Compressors_Meta_Type, MD.Compressors_Meta_Name, MD.Compressors_methodName]     = read_Meta("Compressors", RelDirName = RelDirName)
    [MD.EntryPoints_Meta, MD.EntryPoints_Type, MD.EntryPoints_Meta_Name, MD.EntryPoints_methodName]          = read_Meta("EntryPoints", RelDirName = RelDirName)
    [MD.LNGs_Meta, MD.LNGs_Meta_Type, MD.LNGs_Meta_Name, MD.LNGs_methodName]                                 = read_Meta("LNGs", RelDirName = RelDirName)
    [MD.PipeLines_Meta, MD.PipeLines_Meta_Type, MD.PipeLines_Meta_Name, MD.PipePoints_methodName]            = read_Meta("PipePoints", RelDirName = RelDirName)
    [MD.Storages_Meta, MD.Storages_Meta_Type, MD.Storages_Meta_Name, MD.Storages_methodName]                 = read_Meta("Storages", RelDirName = RelDirName)
    [MD.InterConnectionPoints_Meta, MD.InterConnectionPoints_Meta_Type, MD.InterConnectionPoints_Meta_Name, MD.InterConnectionPoints_methodName] = read_Meta("InterConnectionPoints", RelDirName = RelDirName)
    
    # Filter of Data
    MD.BorderPoints_Meta            = M_Filter.filter_Daten(Filter, MD.BorderPoints_Meta)
    MD.Compressors_Meta             = M_Filter.filter_Daten(Filter, MD.Compressors_Meta)
    MD.EntryPoints_Meta             = M_Filter.filter_Daten(Filter, MD.EntryPoints_Meta)
    MD.InterConnectionPoints_Meta   = M_Filter.filter_Daten(Filter, MD.InterConnectionPoints_Meta)
    MD.LNGs_Meta                    = M_Filter.filter_Daten(Filter, MD.LNGs_Meta)
    MD.PipeLines_Meta               = M_Filter.filter_Daten(Filter, MD.PipeLines_Meta)
    MD.Storages_Meta                = M_Filter.filter_Daten(Filter, MD.Storages_Meta)
        
    
    # Part of joining elements.
    Ret_Data.BorderPoints           = join_Component_Meta(Ret_Data.BorderPoints,    MD.BorderPoints_Meta,   MD.BorderPoints_Meta_Name,   MD.BorderPoints_Meta_Type,     MD.BorderPoints_methodName)
    Ret_Data.Compressors            = join_Component_Meta(Ret_Data.Compressors,     MD.Compressors_Meta,    MD.Compressors_Meta_Name,   MD.Compressors_Meta_Type,     MD.Compressors_methodName)
    Ret_Data.EntryPoints            = join_Component_Meta(Ret_Data.EntryPoints,     MD.EntryPoints_Meta,    MD.EntryPoints_Meta_Name,   MD.EntryPoints_Type,     MD.EntryPoints_methodName)
    Ret_Data.InterConnectionPoints  = join_Component_Meta(Ret_Data.InterConnectionPoints,     MD.InterConnectionPoints_Meta,    MD.InterConnectionPoints_Meta_Name,   MD.InterConnectionPoints_Meta_Type,     MD.InterConnectionPoints_methodName)
    Ret_Data.LNGs                   = join_Component_Meta(Ret_Data.LNGs,            MD.LNGs_Meta,           MD.LNGs_Meta_Name,   MD.LNGs_Meta_Type,     MD.LNGs_methodName)
    Ret_Data.Storages               = join_Component_Meta(Ret_Data.Storages,        MD.Storages_Meta,       MD.Storages_Meta_Name,   MD.Storages_Meta_Type,     MD.Storages_methodName)
    
    Ret_Data.PipeLines              = join_PipeLine_Meta(Ret_Data.PipeLines,        MD.PipeLines_Meta,      MD.PipeLines_Meta_Name,   MD.PipeLines_Meta_Type, MD.PipePoints_methodName)
    
    # Creation of PipeSegments and PipePoints
    Ret_Data.PipeLines2PipeSegments()
    Ret_Data.PipeSegments2PipePoints()


    # Unit conversion
    Ret_Data.MoveUnits('LNGs',      'storage_LNG_Mt',               'max_workingGas_M_m3',           replace = True)
    Ret_Data.MoveUnits('LNGs',      'max_cap_store2pipe_M_m3_per_a','max_cap_store2pipe_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Compressors','max_cap_M_m3_per_h',          'max_cap_M_m3_per_d',            replace = True)
    Ret_Data.MoveUnits('Storages',  'max_cap_pipe2store_GWh_per_d', 'max_cap_pipe2store_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Storages',  'max_cap_store2pipe_GWh_per_d', 'max_cap_store2pipe_M_m3_per_d', replace = True)
    Ret_Data.MoveUnits('Storages',  'max_workingGas_TWh',           'max_workingGas_M_m3',           replace = True)


    # Removing attributes
    Ret_Data.removeAttrib('PipeSegments',   ['meta_id'])
    Ret_Data.removeAttrib('LNGs',           ['storage_LNG_Mt', 'max_cap_store2pipe_M_m3_per_a'])
    Ret_Data.removeAttrib('Compressors',    ['max_cap_M_m3_per_h'])
    Ret_Data.removeAttrib('Storages',       ['max_cap_pipe2store_GWh_per_d', 'max_cap_store2pipe_GWh_per_d', 'max_workingGas_TWh'])
    
    
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Leeres Gas Feld', 'Depleted Field')
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Depleted gas field', 'Depleted Field')
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Leeres ?l Feld', 'Depleted Field')
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Leeres ?l/Gas Feld', 'Depleted Field')
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Leeres Feld', 'Depleted Field')
    
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Salz Kaverne', 'Salt cavern')
    
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Stein Kaverne', 'Rock Cavern')
    Ret_Data.replaceAttribVal('Storages', 'store_type', 'Leeres ?l Feld mit Gas Haube', 'Depleted Field')
    
    
    
    # Adding lat long
    Ret_Data.add_latLong()
    
    
    # removing unwanted components    
    Ret_Data.PipeLines  = []
    Ret_Data.PipePoints = []
    
    
    # Assuring that all elements of a component having same attributes, and 
    # keeping track of origin of data
    Ret_Data.setup_SameAttribs([], None)


    # Adding further essential attributess
    Ret_Data.fill_length('PipeSegments')
    Ret_Data.make_Attrib(['PipeSegments'], 'lat',  'lat_mean',  'mean')
    Ret_Data.make_Attrib(['PipeSegments'], 'long', 'long_mean', 'mean')


    # Replacing any '' with None
    Ret_Data.replace_attrib(compNames = [], attribNames = [], attribValIn = '', attribValOut = None)
    Ret_Data.replace_attrib(compNames = [], attribNames = [], attribValIn = 'True', attribValOut = 1)
    Ret_Data.replace_attrib(compNames = [], attribNames = [], attribValIn = 'False', attribValOut = 0)

    
    # Cleaning up node_id and nodes
    Ret_Data.merge_Nodes_Comps(compNames = ['LNGs', 'Compressors', 'Storages', 'PipeSegments', 'EntryPoints', 'InterConnectionPoints', 'BorderPoints', 'Nodes'])
    Ret_Data.remove_unUsedNodes()


    Ret_Data.SourceName             = ['InterNet']

    return Ret_Data



    
def read_component(ComponentName, NumDataSets = 1e+100, CheckLatLong = 0, RelDirName = None):
    """ Reading of point file from CSV files. Information is supplied via config parser **Info_EinLesen**,
	string **DataName** of what to read, e.g. 'Compressors', or 'Nodes', and **CheckLatLong** being a 
	boolean to check if lat/long were available. Further relative path name of where CSV files located 
	given through **RelDirName**. 

.. comments: 
    Input:
	    ComponentName: 	String of component name
		NumDataSets: 	Max number of values ot be read in	
						(default 1e+100)
        CheckLatLong:   Boolean (1/0) if value of lat/long shall be checked 
		                (default = 0)
		RelDirName: 	String of relative file location 
						(default = None) 
    Return:
        Nodes:           Information of the Nodes elements 
    """

    # Initializierung von Variabeln
    Punkte      = []
    countLine   = 0

    if ComponentName == "BorderPoints":
        DateiName = str(RelDirName /  'Loc_BorderPoints.csv')
    elif ComponentName == "Compressors":
        DateiName = str(RelDirName / 'Loc_Compressors.csv')
    elif ComponentName == "Consumers":
        DateiName = str(RelDirName / 'Loc_Consumers.csv')
    elif ComponentName == "EntryPoints":
        DateiName = str(RelDirName / 'Loc_EntryPoints.csv')
    elif ComponentName == "InterConnectionPoints":
        DateiName = str(RelDirName / 'Loc_InterConnectionPoints.csv')
    elif ComponentName == "LNGs":
        DateiName = str(RelDirName / 'Loc_LNGs.csv')
    elif ComponentName == "Nodes":
        DateiName = str(RelDirName / 'Loc_Nodes.csv')
    elif ComponentName == "Storages":
        DateiName = str(RelDirName / 'Loc_Storages.csv')
    else:
        print('ERROR: M_Internet.read_Points: type ' + ComponentName + ' nicht definiert')
        raise 

    if not os.path.exists(DateiName):
        print(DateiName+' does not exist\n')
    else:    
        # opening file    
        fid = open(DateiName, 'r', encoding="utf-8", errors = "ignore")
    #    fid  = open(DateiName, "r", encoding = "iso-8859-15", errors = "replace")

        for ii in list(range(1 + 2)):
            fid.readline()
    
        # reading with CSV    
        csv_reader = csv.reader(fid, delimiter = ";")
            
        try:
            if 'Nodes' in ComponentName:
                for row in csv_reader:
                    id          = row[0]
                    source_id   = [''.join([ID_Add,str(id)])]
                    name        = id
                    comment     = row[1]
                    country     = row[2]
                    lat         = row[3]
                    long        = row[4]
                    exact       = row[5]
                    node_id     = [id]
                    
                    Punkte.append(K_Component.Nodes(id = id, 
                                name        = name, 
                                node_id     = node_id, 
                                source_id   = source_id, 
                                country_code = country, 
                                lat         = float(lat), 
                                long        = float(long), 
                                comment     = comment,
                                param       = {'exact'     : exact}))
    
            
                    countLine = countLine + 1
                    if countLine > NumDataSets:
                        fid.close()
                        return Punkte
            else:
                for row in csv_reader:
                    id          = row[0]
                    source_id   = [''.join([ID_Add,str(id)])]
                    name        = id
                    comment     = row[1]
                    node_id     = [row[2]]
                    country_code = None
            
                    Punkte.append(K_Component.Nodes(id = id, 
                                name        = name, 
                                node_id     = node_id, 
                                source_id   = source_id, 
                                country_code = country_code, 
                                lat         = float('nan'), 
                                long        = float('nan'),
                                comment     = comment,
                                param       = {}))
    
            
                    countLine = countLine + 1
                    if countLine > NumDataSets:
                        fid.close()
                        return Punkte
                
            
                
                
        except Exception as inst:
            print(countLine)
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)  
            print(str(inst))
            raise 
        
        # schliessen der CSV Datei
        fid.close()
    
    return Punkte



    
def read_PipeLines(NumDataSets = 1e+100, RelDirName = 'Eingabe/InternetDaten/'):
    """ Reading of pipeline information from CSV file. Number of pipelines to read given with 
	**NumDataSets**, and location of relative path folder is **RelDirName**
    
    \n.. comments:
    Input:
        NumDataSets: 	Maximum number of elements to be read
						(default = 1e+100)
		RelDirName: 	String containing relative directory name
						(default = 'Eingabe/InternetDaten/')
    Return:
        PipeLines:       PipeLines component
    """

    # Initializierung von Variabeln
    id          = []
    name        = []
    node_id     = []
    meta_id     = []
    source_id   = []
    PipeLines   = []
    
    dataFolder  = Path.cwd()
    filename    = dataFolder / RelDirName
    
    
    # Opening file and reading header lines
    FileName = str(filename / 'Loc_PipePoints.csv')
    
    if os.path.exists(FileName):
        fid  = open(FileName, 'r', encoding="utf-8")
    
        
        for ii in list(range(1 + 2)):
            fid.readline()
            
        # reading with CSV    
        csv_reader = csv.reader(fid, delimiter = ";")
        
        for row in csv_reader:
            id.append(row[0])
            source_id.append(''.join([ID_Add, str(row[0])]))
            name.append(row[1])
            node_id.append(row[2])
            meta_id.append(row[3])
    
            
        # schliezen der CSV Datei
        fid.close()
        
        # Initializieren von Variabeln
        countLeitung    = 0
        countLine       = 0
        MaxNum          = len(name)
        
        #     
        
        #max_pressure_bar oder pressure Hat hier nix verloren
        while countLine < MaxNum:
            PipeLines.append(K_Component.PipeLines(id = None, 
                    name        = '',  
                    node_id     = [], 
                    country_code = None, 
                    source_id   = [], 
                    lat         = None, 
                    long        = None))
            dieserLeitungsName                  = name[countLine]          # LeitungsNamen
            dieserPunktName                     = node_id[countLine]      # LeitungsNamen
            dieserMet_id                        = meta_id[countLine]
            dieserid                            = id[countLine]
            dieserSource_id                     = source_id[countLine]
            
            PipeLines[countLeitung].id          = dieserid
            PipeLines[countLeitung].name        = dieserLeitungsName
            PipeLines[countLeitung].node_id     = [dieserPunktName]          # PunktNamen
            PipeLines[countLeitung].source_id   = [dieserSource_id]
            PipeLines[countLeitung].param['meta_id']  = dieserMet_id
            
            # Kreiert restliche list von LeitungsNamen
            allLeitungsNames    = name[countLine+1:]
            if countLeitung == 31:
                countLeitung = countLeitung
            pos = M_FindPos.find_pos_StringInList(dieserLeitungsName, allLeitungsNames)
            if len(pos) == 1:
                dieserPunktName                     = node_id[countLine + 1 + pos[0]]
                PipeLines[countLeitung].node_id.append(dieserPunktName)
            elif len(pos) > 1:
                dieserPunktName                     = node_id[countLine + 1+ pos[len(pos) - 1]]
                pos                                 = pos[0:len(pos)-1]
                for p in pos:
                    PipeLines[countLeitung].node_id.append(node_id[countLine + 1 + p])
                PipeLines[countLeitung].node_id.append(dieserPunktName)
    
                pos.append(0)
            else:
                print('Leitung defekt')
            
            countLeitung    = countLeitung  + 1
            countLine       = countLine     + 1 + len(pos)
            
            # push user steop based on NumDataSets
            if countLeitung > NumDataSets:
                return PipeLines
        
    return PipeLines




def join_Component_Meta(Elemente, Meta_Elemente, Meta_Namen, Meta_Typen, Method_Name):
    """ Function to join elements (**Elemente**) with meta data of elements **Meta_Elemente**.  

    \n.. comments: 
    Input:
        Elemente:            Gas Netzwerk elements (topological information)
        Meta_Elemente:       Information of Meta data por pipelines
        Meta_Typen:          Variable type of the different Meta_Elemente (e.g. text, real)
        Meta_Namen:          Variabele namen of the Meta_Elemente
        Meta_Typen:          List of strings indicating the type of data.
    Return:
        Elemente:            Gas Netzwerk elements, linked with  Meta daten.
    """

    # Initializierung von Variabeln
    Meta_comp_ids   = M_Helfer.get_attribFromList(Meta_Elemente, 'comp_id')
    countEle        = 0
    posKeep         = []
    posMeta         = []
    try:
        for ele in Elemente:
            countMet    = 0
            dieserWert  = ele.id
            diserNodeID = ele.node_id

            pos         = M_FindPos.find_pos_StringInList(dieserWert, Meta_comp_ids)
    
            if len(pos) > 0:
                posMeta.append(pos[0])
                posKeep.append(countEle)
                
                for idx, metName in enumerate(Meta_Namen):
                    if metName != 'comp_id' and metName != 'id':
                        # Check if param
                        if len(Method_Name[idx]) > 0:
                            Elemente[countEle].param.update({metName:getattr(Meta_Elemente[pos[0]], metName)}) # setattr(Elemente[countEle], metName, getattr(Meta_Elemente[pos[0]], metName))
                            if getattr(Meta_Elemente[pos[0]], metName) == None:    # getattr(Meta_Elemente[pos[0]], metName) == None:
                                Elemente[countEle].param.update({metName:None})    # setattr(Elemente[countEle], metName, None)
                                
                        # Non param
                        else:
                            setattr(Elemente[countEle], metName, getattr(Meta_Elemente[pos[0]], metName))
                            if getattr(Meta_Elemente[pos[0]], metName) == None:
                                setattr(Elemente[countEle], metName, None)
                        
                Elemente[countEle].node_id  = diserNodeID
                Elemente[countEle].id       = dieserWert

                countMet        = countMet + 1

            countEle = countEle + 1    
        
        Temp        = K_Netze.NetComp()
        Temp.Temp   = Elemente
        Temp.select_byPos('Temp', posKeep)
        Elemente    = Temp.Temp
        
    except:
        print("ERROR: M_Verknuepfe.join_Component_Meta")
        raise 
    
    return Elemente




def join_PipeLine_Meta(Elemente, Meta_Elemente, Meta_Namen, Meta_Typen, Method_Name):
    """ Function to join elements (**Elemente**) with meta data of elements **Meta_Elemente**.  

    \n.. comments: 
    Input:
        Elemente:            Gas Netzwerk elements (topological information)
        Meta_Elemente:       Information from Meta data for PipeLines 
        Meta_Namen:          Variable names of Meta_Elemente
        Meta_Typen:          List of strings indicating the type of data
        Method_Name:         List of strings, containing indicator if column is to be stored in Param dict
    Return:
        Elemente:            Gas Netzwerk elements linked to the Meta data.
    """

    # Initializierung von Variabeln
    Meta_comp_ids   = M_Helfer.get_attribFromList(Meta_Elemente, 'comp_id')
    countEle        = 0
    posKeep         = []
    try:
        for ele in Elemente:
            dieserWert  = ele.param['meta_id']
            pos         = M_FindPos.find_pos_StringInList(dieserWert, Meta_comp_ids)
            if len(pos) > 0:
                posKeep.append(countEle)
                for idx, metName in enumerate(Meta_Namen):
                    if metName != 'comp_id' and metName != 'id':
                        if len(Method_Name[idx]) > 0:
                            Elemente[countEle].param.update({metName: getattr(Meta_Elemente[pos[0]], metName)})
                        else:
                            setattr(Elemente[countEle], metName, getattr(Meta_Elemente[pos[0]], metName))
            
            countEle = countEle + 1    
            
        Temp        = K_Netze.NetComp()
        Temp.Temp   = Elemente
        Temp.select_byPos('Temp', posKeep)
        Elemente    = Temp.Temp
        
    except:
        print("ERROR: M_Verknuepfe.join_Component_Meta")
        raise 
    
    return Elemente





def read_Meta(DataName, RelDirName = 'Eingabe/InternetDaten/'):
    """ Reading meta data from CSV files. Directory name supplied 
    through **DataName**, and relative path for location lat/long 
    given through **RelDirName**.
    
    \n.. comments:
    Input:
        DataName: 			Name of component to be read (of type string)
		RelDirName:         Relative path name of where other data can be
							found for lat/long matching.
							(default = Eingabe/InternetDaten/')
    Return:
        Meta            	Meta data
        converters:      	
        NamesListe:      	
		methodName:			
    """

    # Initializierung von Variabeln
    Meta            = []
    DataSeperator   = ";"
    dataFolder      = Path.cwd()
    DirName         = dataFolder /  RelDirName
    
    if DataName == "BorderPoints":        
        DateiName = str(DirName / 'Meta_BorderPoints.csv')
    elif DataName == "Compressors":
        DateiName = str(DirName / 'Meta_Compressors.csv')
    elif DataName == "EntryPoints":
        DateiName = str(DirName / 'Meta_EntryPoints.csv')
    elif DataName == "InterConnectionPoints":
        DateiName = str(DirName / 'Meta_InterConnectionPoints.csv')
    elif DataName == "LNGs":
        DateiName = str(DirName / 'Meta_LNGs.csv')
    elif DataName == "PipePoints":        
        DateiName = str(DirName / 'Meta_PipePoints.csv')
    elif DataName == "Storages":
        DateiName = str(DirName / 'Meta_Storages.csv')
    else:
        print('ERROR: M_Internet.read_Meta: type ' + DataName + ' not defined')
    
    dirname     = os.path.dirname(__file__)
    filename    = os.path.join(dirname, DateiName)

    
    # Kontrollieren, dass Datei gefunden werden kann        
    if os.path.isfile(filename) != 1:
        return [Meta, [], [], []]
    
    # Oeffnen der Datei
    fid = open(filename, 'r', encoding="Latin-1")
    #fid = open(filename, "r", encoding = "iso-8859-15", errors = "replace")

        
    # Kopfzeilen einlese und Verarbeiten
    KopfZeile       = fid.readline()
    TypenZeile      = fid.readline()
    TypenListe      = TypenZeile.strip().split(DataSeperator)
    NamesListe      = KopfZeile.strip().split( DataSeperator)
    NamesListeOut   = []
    methodName      = []
    
    for idx, name in enumerate(NamesListe):
        if name != 'comment':
            if idx > 2:
                methodName.append('param')
            else:
                methodName.append('')
            NamesListeOut.append(name)
            
    # Lesen der anderen unbenutzen Header Zeilen
    for ii in list(range(1)):
        fid.readline()
    
    
    # Umaenderung der DatenTypen Label fuer Spalten
    converters      = [typemap[typename] for typename in TypenListe]
    # Initializierung von Rueckgabe Wert
    TempData        = namedtuple('TempData', NamesListeOut)
    
    # Datei Leser fuer CSV Datei
    csv_reader      = csv.reader(fid, delimiter = DataSeperator)
        
    for line in csv_reader:
        textvalues  = line
        values      = []
        for idx, converter in enumerate(converters):
            textvalue = textvalues[idx]
            if NamesListe[idx] != 'comment':
                if (converter == float) and (len(textvalue) == 0):
                    values.append(None)
                else:
                    values.append(converter(textvalue))

        Meta.append(TempData(*values))

    # schliessen der CSV Datei
    fid.close()
    
        
    return [Meta, converters, NamesListeOut, methodName]


