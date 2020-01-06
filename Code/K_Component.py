# -*- coding: utf-8 -*-
"""
Component Class
***************
"""
import Code.M_Helfer          as M_Helfer
import Code.M_DataAnalysis    as M_DataAnalysis
import csv      


def typcheck(x):
    if x == 'None':
        x = None
        
    if x is None:
        return x
    else:
        return float(x)
    pass
    

      
class Component(object):
    """Class **Component** with the following fixed attributes **id**, **name**, **source_id**, **node_id**,** country_code**, 
	**lat**, **long**, and **comment**, and the following dicts, **tags**, **uncertainty**, **method**, **param**."""
	
    def __init__(self, id, name, source_id, node_id, country_code = None, lat = None, long = None, comment = None, tags = None, uncertainty = None, method = None, param = None):

        
        if lat is None:
            lat = None
        if long is None:
            long = None
        if tags is None:
            tags = {}
        if param is None:
            param = {}
        if uncertainty is None:
            uncertainty = {}
        if method is None:
            method = {}
            
            
        self.id             = id
        self.name           = name
        self.source_id      = source_id
        self.node_id        = node_id
        self.lat            = lat
        self.long           = long
        self.country_code   = country_code
        self.comment        = comment
        
        self.param          = param
        self.uncertainty    = uncertainty
        self.method         = method
        self.tags           = tags



    def all(self):
        """Method to get info on component of Netz instancde"""
        for key in sorted(self.__dict__.keys()): 
            print(key + ': ' + str(self.__dict__[key]))
            



    def __repr__(self):
        return str(self.name)


    
    
    def AttribLables(self):
        """Method that returns list of string, that are the attribute labels for the component."""
        return ['id', 'name', 'source_id', 'node_id', 'lat', 'long', 'country_code', 'comment']




    def getPipeLength(self):
        length = 0
        for idx in range(len(self.lat)-1):
            length = length + M_DataAnalysis.distance(self.long[idx], self.lat[idx], self.long[idx+1], self.lat[idx+1])
        return length
    
    
    
    
    def mergeAttribs(self, RetElement):
        """Merging of two elements by assuming that second element **RetElement** ios less dominant
        hence values from **RetElement** will only be copied accross if attrib in **self** 
        is not given or None.
        
        """
        tempKeys_Param  = self.param.keys()
        tempKeys_Uncert = RetElement.uncertainty.keys()
        tempKeys_Method = RetElement.method.keys()

        for key in RetElement.param.keys():
            if key not in tempKeys_Param:
                self.param.update({key: RetElement.param[key]})
                if key in tempKeys_Uncert:
                    self.uncertainty.update({key: RetElement.uncertainty[key]})
                if key in tempKeys_Method:
                    self.method.update({key: RetElement.method[key]})
            elif self.param[key] == None:
                self.param.update({key: RetElement.param[key]})
                if key in tempKeys_Uncert:
                    self.uncertainty.update({key: RetElement.uncertainty[key]})
                if key in tempKeys_Method:
                    self.method.update({key: RetElement.method[key]})
        self.source_id.append(*RetElement.source_id)


class BorderPoints(Component):
    """ Component Class BorderPoints"""
      

def Wert(val, uncer, method):
    
    try:
        val = float(val)
    except:
        raise ValueError('Could not convert value {} to float')
        
        
    return{"val":val , "uncer" : uncer, "method": method}
    
    



class Compressors(Component):
    """ Component Class Compressors"""
        

class ConnectionPoints(Component):
    """ Component Class ConnectionPoints"""


class Consumers(Component):
    """ Component Class Consumers"""
    

class EntryPoints(Component):
    """ Component Class EntryPoints"""

	
class InterConnectionPoints(Component):
    """ Component Class InterConnectionPoints"""

	
class LNGs(Component):
    """ Component Class LNGs"""
        

class Nodes(Component):
    """ Component Class Nodes"""

	
class Operators(Component):
    """ Component Class Operators"""

	
class PipeLines(Component):
    """ Component Class PipeLines"""


class PipePoints(Component):
    """ Component Class PipePoints"""

	
class PipeSegments(Component):
    """ Component Class PipeSegments"""

	
class Productions(Component):
    """ Component Class Productions"""

	
class Storages(Component):
    """ Component Class Storages"""

	
class Processes():
    def __init__(self, Commments):
        self.Commments  = Commments
    
    
class PolyLine():
    def __init__(self, long, lat):
        self.long = long
        self.lat  = lat
        


class MetaData(object):
    def __init__(self):
        self.BorderPoints           = []
        self.Compressors            = []
        self.EntryPoints            = []
        self.InterConnectionPoints  = []
        self.LNGs                   = []
        self.PipePoints             = []
        self.Storages               = []
        
class GasFlow(object):
    """ Gas flow data class for EntsoG API querier.  
    
    \n.. comments: 
    Elemente:
        id:                  string, Kurzname
        name:                string, name
        indicator:           float,  Gasmenge
        operatorKey:         string, Einheit von Gasmenge
        tsoEicCode:          string, Richtungsanweiser des Gasflusses
        pointKey:            string, Positions ID
        tsoItemIdentifier:   string, ???
        directionKey:        string, indicating direction of flow data    
        unit:                string, unit of gas flow
        capacityType:        
        
        value:          	Float time series of gas flow, exiting the operator
        intervalStart:  	Time series of inerval begin time stamps, exiting the operator
        intervalEnd:    	Time series of inerval end time stamps, exiting the operator

    """
    
    def __init__(self, id = None, name = '', source_id = None, pointKey = '', directionKey = '',
                 MetaData = [], value = [], intervalStart = [], intervalEnd = []):
        """ Initialization of Consumers class instance, with the following input: **id**, **indicator**, operatorKey**, **tsoEicCode**, **pointKey**, **tsoItemIdentifier**, **unit**, **capacityType**, **MetaData**, **value_Entry**, **intervalStart_Entry**, **intervalEnd_Entry**, **value_Exit**, **intervalStart_Exit**, **intervalEnd_Exit**, and **fileName**.  
		
        """
        self.id                 	= str(id)
        self.name               	= name
        self.source_id          	= source_id
        self.pointKey           	= pointKey
        self.MetaData           	= MetaData
        self.directionKey       	= directionKey
        
        self.values_Exit            = []
        self.intervalStart_Exit     = []
        self.intervalEnd_Exit       = []
        
        self.values_Entry           = []
        self.intervalStart_Entry    = []
        self.intervalEnd_Entry      = []
        
        if 'exit' in directionKey.lower():
            if len(value) > 0:
                self.values_Exit            = value
                self.intervalStart_Exit     = intervalStart
                self.intervalEnd_Exit       = intervalEnd
        else:
            if len(value) > 0:
                self.values_Entry           = value
                self.intervalStart_Entry    = intervalStart
                self.intervalEnd_Entry      = intervalEnd

    def save_GasFlow_CSV(self, fileName, dirString):
        """ Saving the Physical EntsoG data into CSV  file.  Inputs are **fileName** as the string containing path and name of file to be savede into, and **dirString** is a string indicating the direction of the flow (options are 'entry' and 'exit').

    
        \n.. comments:  
            Input: 
                self:        self
                FileName:    String of file name, including path
                dirString:   string containing  file name add re direction of the 
                             flow supplied, e.g. 'entry', 'excit'
            Return:
                []"""

        fileName = fileName + str(self.pointKey) + '_' +  dirString + '.csv'

        with open(fileName, mode='w', newline='', encoding='utf-8') as csv_file:
        #with open(fileName, mode = 'w', newline = '', encoding = "iso-8859-15", errors = "replace") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Write Header
            try:
                csv_writer.writerow(['id',              self.id])
                csv_writer.writerow(['name',            self.name])
                csv_writer.writerow(['pointKey',        self.pointKey])
                csv_writer.writerow(['directionKey',    self.directionKey])

                for dd in self.MetaData:
                    csv_writer.writerow([dd, self.MetaData[dd]])
            
                csv_writer.writerow([])
                csv_writer.writerow(['IntervalStart', 'IntervalEnd', 'GasValue'])
                
                if 'entry' in dirString:
                    for count in range(len(self.values_Entry)):
                        csv_writer.writerow([self.intervalStart_Entry[count], self.intervalEnd_Entry[count], self.values_Entry[count]])
                elif 'exit' in dirString:
                    for count in range(len(self.values_Exit)):
                        csv_writer.writerow([self.intervalStart_Exit[count], self.intervalEnd_Exit[count], self.values_Exit[count]])
                else:
                    print('ERROR: K_Component.GasFlow.save_GasFlow_CSV: Code not written')
                    raise 

            except:
                print('Error K_Component.GasFlow.save_GasFlow_CSV: Saving data to ascii file.')
                raise 
                
        return []

    def load_Physical_CSV(self, fileName, StartDate = '2010-10-01T00:00:00', StopDate = '2120-12-31T00:00:00'):
        """ Reading the Physical CSV EntsoG data from files. File name and path is supplied via **fileName**.

    
        \n.. comments: 
            Input: 
                FileName:     String of file name, including path
            Return:
                []"""
				
        StartDate   = M_Helfer.converteStr2DateTime(StartDate)
        StopDate    = M_Helfer.converteStr2DateTime(StopDate)
        
        # Opening the file
        fid = open(fileName, "r")        
        #fid = open(fileName, "r", encoding = "iso-8859-15", errors = "replace")

        # Rading the header information
        self.fileName               = fileName
        self.id                     = str(M_Helfer.strip_accents(fid.readline()[:-1].split(';')[1]))
        self.name                   = M_Helfer.strip_accents(fid.readline()[:-1].split(';')[1])

        # Getting the meta Data (everything upto empty line)
        self.MetaData   = {}
        self.param   = {}
        temp            = M_Helfer.strip_accents(fid.readline()[:-1])
        while len(temp) > 0:
            key     = temp.split(';')[0]
            value   = temp.split(';')[1]
                
            if key == 'directionKey':
                self.directionKey  = value
            elif key == 'pointKey':
                self.pointKey  = value
            elif key == 'name':
                self.name  = value
            elif key == 'unit':
                self.unit  = value
            else:
                try:
                    self.MetaData[key]  = float(value)
                    self.param[key]     = float(value)
                except:
                    self.MetaData[key]  = value
                    self.param[key]     = value
                    
            # Reading next line
            temp    = M_Helfer.strip_accents(fid.readline()[:-1])

        # Reading data header line
        temp    = fid.readline()[:-1]
        
        # Reading the actuel data
        self.intervalStart  = []
        self.intervalEnd    = []
        self.values         = []
        
        # Now read data only if requested dates allow
        if StartDate<StopDate:
            temp    = fid.readline()[:-1]
            
            if 'entry' in self.directionKey:
                while len(temp) > 0:
                    ThreeVals   = temp.split(';')
                    wert1       = M_Helfer.converteStr2DateTime(ThreeVals[0])
                    wert2       = M_Helfer.converteStr2DateTime(ThreeVals[1])
                    if (wert1 > StartDate) and (wert1 < StopDate):
                        self.intervalStart_Entry.append(wert1)
                        self.intervalEnd_Entry.append(wert2)
                        self.values_Entry.append(float(ThreeVals[2]))
                    temp    = fid.readline()[:-1]
                    
            elif 'exit' in self.directionKey:
                while len(temp) > 0:
                    ThreeVals   = temp.split(';')
                    wert1       = M_Helfer.converteStr2DateTime(ThreeVals[0])
                    wert2       = M_Helfer.converteStr2DateTime(ThreeVals[1])
                    if (wert1 > StartDate) and (wert1 < StopDate):
                        self.intervalStart_Exit.append(wert1)
                        self.intervalEnd_Exit.append(wert2)
                        self.values_Exit.append(float(ThreeVals[2]))
                    temp    = fid.readline()[:-1]
            else:
                print('ERROR: K_EntsoG.GasFlow.load_GasFlow_CSV: Code not written')
                raise 
        
        # Closing the file
        fid.close()
        
        return []



#class Component(object):
def makeLine(X = [], Y = []):
    
    polyLine        = PolyLine(lat = [], long = [])
    polyLine.long   = X
    polyLine.lat    = Y

    
    return polyLine

class OSMComponent(Component):
    def __init__(self, id, name, source_id, node_id, lat, long, country_code, tags,**param):
        self.id             = id
        self.name           = name
        self.source_id      = source_id
        self.node_id        = node_id
        self.lat            = lat
        self.long           = long
        self.country_code   = country_code
        self.tags           = tags
        # Caveat: Setting param as an attribute of self will lock further
        # additions to self. All attributes set on self will be put into the
        # dictionary param.
        # This means that subclasses need to set attributes before calling
        # Component.__init__()!
        self.param = param
        self.uncer = {}
        self.method = {}
        
        for key in param:
            if key!= 'uncer' and key != 'method' and key != 'source' and key != 'license':
                self.uncer[key]  = None
                self.method[key] = None



    




class DF_Action_Meta():
    def __int__(self):
      
        self.RegType        = []
        self.Convert2Float  = []
        self.AttribNames    = []
        self.DataDensity    = []
        self.Simulate       = []
