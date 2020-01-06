# -*- coding: utf-8 -*-
"""
Stats class
*********
"""

from __future__ import print_function
import os
import csv

roundVal    = 4




        
class StatsSummary():
    def __init__(self):
        
        self.BorderPoints           = []    # BP
        self.Compressors            = []    # CO
        self.ConnectionPoints       = []    # CP
        self.Consumers              = []    # CS
        self.EntryPoints            = []    # EP
        self.InterConnectionPoints  = []    # IC
        self.LNGs                   = []    # LG
        self.Nodes                  = []    # NO
        self.PipeSegments           = []    # PS
        self.PipeLines              = []    # PL
        self.Productions            = []    # PD
        self.Storages               = []    # SR
        

    def CompLabels(self):
        return ['BorderPoints', 'Compressors', 'Consumers', 'ConnectionPoints', 
                'EntryPoints', 'InterConnectionPoints','LNGs', 'Nodes',  
                'Productions', 'PipeSegments', 'PipeLines','Storages',]


    def save2File(self, FileName):
        """Writing Stats Results into CSV file
        """        
        FileList = self.CompLabels()
        # Combining current path with input folder
        dataFolder = os.getcwd()
        DirName = os.path.join(dataFolder, FileName)        
        
        # Checking that destination folder is given 
        if os.path.isdir(DirName) is not True:
            print('ERROR: M_CSV.write: directory doesnot exist: ', DirName)
            return 0
        
        for comp in FileList:
            if len(self.__dict__[comp]) > 0:
                # Creatin of output file name
                thisFileName    = DirName + 'Stats_' + comp + '.CSV'
                
                # Getting compopnent data
                thisData        = self.__dict__[comp]
                
                with open(thisFileName, mode='w', newline = '') as f:
                    theWriter = csv.writer(f, delimiter = ";")
                    theWriter.writerow(['AttribName', 'ModelName', 'ErrorName', 'ModelVal', 'ErrorVal'])
                    
                    for dat in thisData:
                        theWriter.writerow([dat.AttribName, dat.ModelName, dat.ErrorName, dat.ModelVal, dat.ErrorVal])

        return 1                    

        
        
  
        
        
    
class StatsComp(object):
    """Class **Component** with the following fixed attributes **id**, **name**, **source_id**, **node_id**,** country_code**, 
	**lat**, **long**, and **comment**, and the following dicts, **tags**, **uncertainty**, **method**, **param**."""
	
    def __init__(self, AttribName = '',ModelName = '', ErrorName = '', ModelVal = None, ErrorVal = None):
        
        self.AttribName = AttribName
        self.ModelName  = ModelName
        self.ErrorName  = ErrorName
        self.ModelVal   = ModelVal
        self.ErrorVal   = ErrorVal
        
        
        



class BorderPoints(StatsComp):
    """ Component Class BorderPoints"""
        

class Compressors(StatsComp):
    """ Component Class Compressors"""
        

class ConnectionPoints(StatsComp):
    """ Component Class ConnectionPoints"""


class Consumers(StatsComp):
    """ Component Class Consumers"""
    

class EntryPoints(StatsComp):
    """ Component Class EntryPoints"""

	
class InterConnectionPoints(StatsComp):
    """ Component Class InterConnectionPoints"""

	
class LNGs(StatsComp):
    """ Component Class LNGs"""
        

class Nodes(StatsComp):
    """ Component Class Nodes"""

		
class PipeLines(StatsComp):
    """ Component Class PipeLines"""


	
class PipeSegments(StatsComp):
    """ Component Class PipeSegments"""

	
class Productions(StatsComp):
    """ Component Class Productions"""

	
class Storages(StatsComp):
    """ Component Class Storages"""

	
            
        
        