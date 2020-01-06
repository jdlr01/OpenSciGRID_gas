# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 18:27:26 2019

@author: jadiet
"""


from __future__        import print_function
import Code.K_Netze        as K_Netze






class SuperNetz(K_Netze.CoreNetz):
    
    
    liste = ['Nodes', 'Compressors', 'Regulators', 'Valves', 'EntryPoints', 'ExitPoints', \
               'Storages', 'LNGs', 'Processes']
    
    def __init__(self):
        self.Nodes                  = []
        self.Compressors            = []
        self.Regulators             = []
        self.Valves                 = []
        self.EntryPoints            = []
        self.ExitPoints             = []
        self.Storages               = []
        self.LNGs                   = []
        
        self.Processes              = []
        self.Processes.append(Processes('Initialization of SuperNetz class instance'))
        
        
        
        
        
class Compressors():
    def __init__(self, id = None, name = '', comp_id = None, comment = '',
                 is_H_gas = None, gas_capacity = 0, total_power = 0, 
                 generator_type = None, max_outlet_pressure = 0):
        self.id                     = id
        self.name                   = name
        self.comp_id                = comp_id
        self.comment                = comment
        self.is_H_gas               = is_H_gas
        self.gas_capacity           = float(gas_capacity)
        self.max_outlet_pressure    = float(max_outlet_pressure)
        self.total_power            = float(total_power)
        self.generator_type         = generator_type
        
        
        
        
        
class Nodes():
    def __init__(self, id = None, comment = '', country = '', 
                 lat = 'nan', long = 'nan', exact = 'nan'):
        self.id         = str(id)
        self.comment    = comment
        self.country    = country
        self.lat        = float(lat)
        self.long       = float(long)
        self.exact      = float(exact)
        
        
        
        
class Processes():
    def __init__(self, Commments):
        self.Commments  = Commments
    
