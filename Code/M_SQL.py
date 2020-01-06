# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 13:32:44 2018

@author: apluta
"""
import Code.K_Netze      as K_Netze
import Code.M_FindPos    as M_FindPos
from   psycopg2      import connect
import psycopg2
import sys
import Code.C_colors as CC						  






def write_DB(currentDB, GridName, Grid):
    """
    Description:
    ------------
        Uses the cursor to the current Postgres Database connection to write an 
        instance of the NetzClass (Grid) with the Name 'Gridname' to the Database
    
    Example:
    --------
        currentDB=InfoIO['SQL_3']
        GridName="SciGrid"
        Grid is Instance of Netzclass
    """
    
    
    conn    = CreateDBConnection(currentDB)
    cur     = conn.cursor()

    for key in Grid.CompLabels(): # Run through all Gridattributes
        subkeys                 = []
        subvalues               = []
        inParam                 = []
        i                       = 0
        subkeylist              = ''
        drop_statement          = 'DROP TABLE IF EXISTS ' + GridName + "_"+key
        cur.execute(drop_statement)
        if (len(Grid.__dict__[key]) > 0) and ('PipeLines' not in key)  and ('PipeSegments' not in key):
            for subkey in Grid.__dict__[key][0].__dict__.keys():
                if 'param' == subkey:
                    for sskey in Grid.__dict__[key][0].param.keys():
                        subkeys.append(sskey)
                        inParam.append(1)
                else:
                    subkeys.append(subkey)
                    inParam.append(0)
            subkeylist              = (str(subkeys).replace("'", "").replace("[", "").replace("]", "").replace(",", " Text,") + " Text")
            CreateTable_statement   = "CREATE TABLE IF NOT EXISTS " + GridName + "_" + key + " (" + subkeylist+");"
            cur.execute(CreateTable_statement)
            for i in range(len(Grid.__dict__[key])):
                subvalue = []
                for ii in range(len(subkeys)):
                    if inParam[ii] == 0:
                        subvalue.append(Grid.__dict__[key][i].__dict__[subkeys[ii]])
                    else:
                        subvalue.append(Grid.__dict__[key][i].param[subkeys[ii]])
            
                # replacing None
                subvalue = ['' if (x == None) else x for x in subvalue]

                [str(x) for x in subvalue]
                i+=1
                subvalues.append(subvalue)
                insert_statement    = "INSERT INTO " + GridName + "_" + key +\
                " Values (" + str(subvalue).replace("[", "").replace("]", "").replace("nan", "''") + "); "
                cur.execute(insert_statement)

    cur.close()
    conn.close()




def CheckDB(currentDB):
    """
    Description:
    ------------
        See all Tables in the current DB connection
    
    Example:
    --------
        currentDB=InfoIO['SQL_3']
    """
    
    conn            = CreateDBConnection(currentDB)
    cur             = conn.cursor()
    rejected_list   = ('geography_columns','geometry_columns','raster_columns','raster_overviews','spatial_ref_sys')
    
    
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name ;")
    
    for table in cur.fetchall():
        tablename = str(*table)
#        if tablename not in rejected_list:
#            print(*table)
    cur.close()
    conn.close()

	
	
	
def my_import(name):
    '''
    Description:
    ------------
        HelpMethod to select a Class attributes from String
    '''
    
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
		
    return mod


	
	
def read_DB(currentDB,GridName):
    """
    Description:
    ------------
        Reads Grid with the Name 'Gridname' from Postgres Database 
        and writes to empty Grid (Instance of NetzClass)
    
    Eingabe:
    --------
        currentDB=InfoIO['SQL_3']
        GridName="SciGrid" 
    
    Ausgabe:
    --------
        Netz Class Object
    
    """
    
    conn    = CreateDBConnection(currentDB)
    cur     = conn.cursor()
    Grid    = K_Netze.NetComp()
    
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ;")
    tableDump = cur.fetchall()
    tableNames = []
    for tab in tableDump:
        tableNames.append(tab[0])
    
    for tablename in Grid.CompLabels():
        if GridName.lower()  + "_" + tablename.lower()   in tableNames:
            
            tablecommand    = "SELECT * FROM " + GridName.lower() + "_" + tablename.lower() + " ;"
            cur.execute(tablecommand)
            field_names = [i[0] for i in cur.description]
            results         = cur.fetchall()
            if cur.rowcount>0:
                my_class = my_import('Code.K_Component.' + tablename)
                
                #Grid.__setattr__(tablename,[my_class({'id':'4', 'name':'qwer'})])
    
                Grid.__setattr__(tablename,[my_class(**dict(zip(field_names, res))) for res in results])
            else:
               print(CC.Warning +"Warning, "+ "Could not read " + tablename + " from table: "+GridName.lower()+"_"+tablename.lower()+CC.End)
               
            # Now setting lat long to None instead of ''
            for ii in range(len(Grid.__dict__[tablename])):
                if len(Grid.__dict__[tablename][ii].__dict__['lat']) == 0:
                    Grid.__dict__[tablename][ii].__dict__['lat'] = float('nan')
                    Grid.__dict__[tablename][ii].__dict__['long'] = float('nan')
                else:
                    Grid.__dict__[tablename][ii].__dict__['lat'] = float(Grid.__dict__[tablename][ii].__dict__['lat'])
                    Grid.__dict__[tablename][ii].__dict__['long'] = float(Grid.__dict__[tablename][ii].__dict__['long'] )
                    
                

    cur.close()
    conn.close()

    return Grid

	
	

def CreateDBConnection(currentDB):

    """
    Description
    -----------
        Erzeuge Verbindung zur DatenBank
        Meldet bei Fehlschlag: "OperationalError: FATAL:  database "dbname" does not exist"
    
    Eingabe:
    --------
        currentDB=InfoIO['SQL_3']
    
    """
    
    conn                = psycopg2.connect(dbname = currentDB["DataBaseName"],
                        user = currentDB["User"],  host = currentDB["Host"],  
                        port = int(currentDB["Port"]),  password = currentDB["PassWord"])
    conn.autocommit     = True
    
    return conn

	


def CreateDB(currentDB):
    """
    Description:
    ------------
        Erstellen einer DatenBank, wennn nicht vorhanden.
    
    Eingabe:
    --------
        currentDB=InfoIO['SQL_3']
    
    Ausgabe:
    --------
        1 = DB Kreiert, 0 = DB NICHT Kreiert
    """
    
    created             = 0
    conn                = psycopg2.connect(dbname='postgres',user = currentDB["User"],  
                                host = currentDB["Host"],  port = int(currentDB["Port"]),  
                                password = currentDB["PassWord"])
    conn.autocommit     = True
    cur                 = conn.cursor()
    dbname              = currentDB["DataBaseName"]
    create_statement    = 'CREATE DATABASE {};'.format(dbname)

    print()
    print(CC.Caption+"Create Database: " + dbname + CC.End)
    try:
        cur.execute(create_statement)
        created = 1
        print(CC.Green + "Success" + CC.End)
    except:
        print(CC.Warning + "Fail" + CC.End)
        print('Database already exists!')
    cur.close()
    conn.close()

    return created




def DropDB(currentDB):
    """
    Description:
    ------------
        Löscht eine DatenBank, wennn vorhanden.
    
    Eingabe:
    --------
        currentDB=InfoIO['SQL_3']
    
    Ausgabe:
    --------
        1 = DB Dropped, 0 = DB NICHT Dropped
    """
    
    DB_Dropped      = 0 #return controll value vor return
    conn            = psycopg2.connect(dbname='postgres',user = currentDB["User"],  host = currentDB["Host"],  port = int(currentDB["Port"]),  password = currentDB["PassWord"])
    conn.autocommit = True
    cur             = conn.cursor()
    dbname          = currentDB["DataBaseName"]
    drop_statement  = 'DROP DATABASE IF EXISTS {};'.format(dbname)
    print()
    print(CC.Caption+"Drop the database " + dbname + CC.End)
    cur.execute(drop_statement)
    DB_Dropped = 1
    if conn.notices==[]: 
        print(CC.Green +"Success"+CC.End)
    else :
        print(CC.Red+"Fail"+CC.End)
        print("Does Database not exist?")						 
        print(conn.notices[0])
    cur.close()
    conn.close()
    
    return DB_Dropped




def getAlleSpaltenNamen(InfoSQL, TabellenName):
    """
    Hold alle Spaltennamen aus einer Tabelle 
    
    Eingabe:
        InfoSQL         Strukture von SQL DatenBank Zuganz Daten
        TabellenName    String mit Tabellen Namen drin.
    Ausgabe:
        SpaltenNamen    Liste mit Spalten Namen
    
    """
    
    SpaltenNamen = []
    
    con = connect(dbname = InfoSQL["DataBAseName"],  user = InfoSQL["User"],  host = InfoSQL["Host"],  port = int(InfoSQL["Port"]),  password = InfoSQL["PassWord"])
    cur = con.cursor()
    # um meta data on Tabelle zu bekomkmen
    cur.execute("    SELECT * FROM " + TabellenName + ".INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'Customers'")

    # cur.execute("SELECT * FROM Leitungen")
    TabellenNamen = cur.fetchall()
    
    for name in TabellenNamen:
        SpaltenNamen.append(name[0])
    
    if len(SpaltenNamen) == 0:
        print( sys.argv[0]  + ' hat keine Spalten Namen in Tabelle ' + TabellenName+ ' gefunden')
        
    return SpaltenNamen 




def getAllTableNames(InfoSQL):
    """
    Hold alle Tabellen Namen aus einer DatenBank
    
    Eingabe:
        InfoSQL         Strukture von SQL DatenBank Zuganz Daten
    Ausgabe:
        TabellenNamen   Liste von Tabellen Namen
    
    """
    
    TabellenNamen   = []
    con             = connect(dbname = InfoSQL['IO']["DataBaseName"],  user = InfoSQL['IO']["User"],  host = InfoSQL['IO']["Host"],  port = int(InfoSQL['IO']["Port"]),  password = InfoSQL['IO']["PassWord"])
    cur             = con.cursor()
    # um meta data on Tabelle zu bekomkmen
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")

    # cur.execute("SELECT * FROM Leitungen")
    TabellenString = cur.fetchall()
    
    for name in TabellenString:
        TabellenNamen.append(name[0])

    if len(TabellenNamen) == 0:
        print( sys.argv[0]  + ' hat keine Tabelle gefunden.')
    
    return TabellenNamen 




def leseSQL_Leitungen(InfoSQL):
    """
    Liest Leitungs Tabelle from SQL data base
    
    Eingabe:
        InfoSQL         Strukture von SQL DatenBank Zuganz Daten
    Ausgabe:
        Leitung         Liste von Leitung der Klasse NetzKlassen.Leitung()
    """
    
    Leitungen   = []
    
    con         = connect(dbname = InfoSQL['IO']["DataBaseName"],  user = InfoSQL['IO']["User"],  host = InfoSQL['IO']["Host"],  port = int(InfoSQL['IO']["Port"]),  password = InfoSQL['IO']["PassWord"])
    cur         = con.cursor()
    CurString   = "SELECT * FROM " + InfoSQL['IO']["TabName_Leitungen"]
    cur.execute(CurString)
    
    Leitungen = cur.fetchall()

    cur.close()
    con.close()
    
    # Initializieren von Variabeln
    countLeitung    = 0
    countLine       = 0
    MaxNum          = len(Leitungen)
    Leitung         = []
    
    AlleAlleName = []
    for ii in range(MaxNum):
         AlleAlleName.append(Leitungen[ii][2])
    
    #     
    while countLine < MaxNum:
        Leitung.append(K_Netze.Leitung())
        dieserLeitungsName                  = Leitungen[countLine][2]           # LeitungsNamen
        dieserPunktName                     = Leitungen[countLine][3]           # LeitungsNamen
        Leitung[countLeitung].name          = dieserLeitungsName
        Leitung[countLeitung].node_id       = dieserPunktName                   # PunktNamen
        Leitung[countLeitung].param['description']   = Leitungen[countLine][6]
        
        #Leitung[countLeitung].__dict__
        # dir(Leitung[countLeitung])
        
        # Kreiert restliche list von LeitungsNamen
        allLeitungsNames                = AlleAlleName[countLine+1:]
        pos = M_FindPos.find_pos_StringInList(dieserLeitungsName, allLeitungsNames)
        if len(pos) == 1:
            dieserPunktName                 = Leitungen[countLine + 1 + pos[0]][3]
            Leitung[countLeitung].node_id.append(dieserPunktName)
        elif len(pos) > 1:
            dieserPunktName                 = Leitungen[countLine + 1+ pos[len(pos) - 1]][3]
            pos                             = pos[0:len(pos)-1]
            for p in pos:
                Leitung[countLeitung].node_id.append(Leitungen[countLine + 1 + p][3])
            Leitung[countLeitung].node_id.append(dieserPunktName)
            pos.append(0)
        else:
            print('Leitung defekt')
        
        
        countLeitung    = countLeitung  + 1
        countLine       = countLine     + 1 + len(pos)

    return Leitung




def leseSQL_Meta(InfoSQL, TabellenName):
    """
    Lies Meta-Data from Tabellen from SQL data base

    Eingabe:
        InfoSQL         Strukture von SQL DatenBank Zuganz Daten
        TabellenName    String, von TabellenNamen, via InfoSQL[TabellenName] !!
    Ausgabe:
        MetaData        Meta data aus der Tabelle, in form eines Dict
        MetaType        Daten Type fuer die Spalten der Meta Daten
        ColumnNames     Name der Spalten der Meta Daten
    
    """
    
    MetaData = []
    MetaType = []
    
    # Ueberpruefe das Tabelle in DataBank ist
    AlleTabellenNamen = getAllTableNames(InfoSQL)
    Name = InfoSQL['IO'][TabellenName]
    if len(M_FindPos.find_pos_StringInList(Name, AlleTabellenNamen)):
        con = connect(dbname = InfoSQL['IO']["DataBaseName"],  user = InfoSQL['IO']["User"],  host = InfoSQL['IO']["Host"],  port = int(InfoSQL['IO']["Port"]),  password = InfoSQL['IO']["PassWord"])
        cur = con.cursor()
        CurString = "SELECT * FROM " + InfoSQL['IO'][TabellenName]
        cur.execute(CurString)
    
        MetaPunkte = cur.fetchall()

        cur.close()
        con.close()
    else:
        return MetaData
        
    # Lese SpaltenNamen ein
    con = connect(dbname = InfoSQL['IO']["DataBaseName"],  user = InfoSQL['IO']["User"],  host = InfoSQL['IO']["Host"],  port = int(InfoSQL['IO']["Port"]),  password = InfoSQL['IO']["PassWord"])
    cur = con.cursor()
    CurString = "select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + InfoSQL['IO'][TabellenName] + "'"
    CurString = "select * from " + InfoSQL['IO'][TabellenName] + " where 0=1"
    CurString = "select column_name, data_type from information_schema.columns where table_name = '" + InfoSQL['IO'][TabellenName] + "'"
    cur.execute(CurString)
    
    ColumnNames = []
    MetaTypeRaw = []
    ColumnNamesTuple = cur.fetchall()
    for name in ColumnNamesTuple:
        ColumnNames.append(name[0])
        MetaTypeRaw.append(name[1])
        
        
    cur.close()
    con.close()
    
    # Kreieren of Liste von MetaData
    count   = 0
    
    PassVall = []
#    for ii in list(range(len(MetaPunkte))):
#        PassVall.append(MetaPunkte[ii][count])
    
    
    
    for dicName in ColumnNames:
        for ii in list(range(len(MetaPunkte))):
            PassVall.append(MetaPunkte[ii][count])
        if count == 0:
            MetaData= {dicName: PassVall}
        else:
            MetaData[dicName] = PassVall
            
        count = count + 1
        
    MetaType      = [typemap[typename] for typename in MetaTypeRaw]
    
    return [MetaData, MetaType, ColumnNames]


	


def leseSQL_Punkte(InfoSQL, TabellenName):
    """
    Liest Punkte Tabellen from SQL data base
    
    Eingabe:
        InfoSQL         Strukture von SQL DatenBank Zuganz Daten
        TabellenName    String, von TabellenNamen, via InfoSQL[TabellenName] !!
    Ausgabe:
        Punkte          Liste von Punkten von Klasse NetzKlassen.Nodes()

    """
    Punkte = []
    # Ueberpruefe das Tabelle in DataBank ist
    AlleTabellenNamen = getAllTableNames(InfoSQL)
    Name = InfoSQL['IO'][TabellenName]
    if len(M_FindPos.find_pos_StringInList(Name, AlleTabellenNamen)):
        con = connect(dbname = InfoSQL['IO']["DataBAseName"],  user = InfoSQL['IO']["User"],  host = InfoSQL['IO']["Host"],  port = int(InfoSQL['IO']["Port"]),  password = InfoSQL['IO']["PassWord"])
        cur = con.cursor()
        CurString = "SELECT * FROM " + InfoSQL['IO'][TabellenName]
        cur.execute(CurString)
        TabPunkte = cur.fetchall()
        cur.close()
        con.close()
        count = 0
        for tab in TabPunkte:
            id    = tab[0]
            name  = tab[1]
            lat   = tab[5]
            long  = tab[6]
            land  = tab[4]
            Punkte.append(K_Netze.Nodes(id = id, name = name,  lat = lat, long = long, country_code = land, comment = None, param = {}))
            count = count + 1
    
    
    return Punkte
	
	
