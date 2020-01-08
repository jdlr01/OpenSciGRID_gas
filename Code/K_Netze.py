# -*- coding: utf-8 -*-
"""
Net class
*********
"""

from __future__ import print_function
import Code.M_Helfer        as M_Helfer
import Code.M_FindPos       as M_FindPos
import Code.M_DataAnalysis  as M_DataAnalysis
import Code.M_Shape         as M_Shape
import Code.K_Component     as K_Component
import Code.M_MatLab        as M_MatLab
#import Code.M_Stats         as M_Stats
#import Code.K_Stats         as K_Stats

import copy
import math
import ast


roundVal    = 4

class NetComp(object):
    """Main class **NetComp**. Class containing components such as **BorderPoints** or 
    **Compressors**, used for the non-OSM data set.
    """
    def __init__(self):
        self.SourceName             = ['']
        self.BorderPoints           = []    # BP
        self.Compressors            = []    # CO
        self.ConnectionPoints       = []    # CP
        self.Consumers              = []    # CS
        self.EntryPoints            = []    # EP
        self.InterConnectionPoints  = []    # IC
        self.LNGs                   = []    # LG
        self.Nodes                  = []    # NO
        self.PipePoints             = []    # PP
        self.PipeSegments           = []    # PS
        self.PipeLines              = []    # PL
        self.Productions            = []    # PD
        self.Storages               = []    # SR
        
        self.Processes              = []
        

        
        
    def copy2(self):
        """Method of creating a true independent copy of a class instance.
        """
        RetNetz      = NetComp()
        
        RetNetz      = copy.deepcopy(self)
            
        return RetNetz
        
    
    def AttribLables(self):
        return ['id', 'name', 'source_id', 'node_id', 'lat', 'long', 'country_code', 'comment']


    
        
    def CompLabelsSpot(self):
        return ['Compressors', 'Consumers', 'ConnectionPoints', 'InterConnectionPoints',
                'BorderPoints', 'LNGs', 'Storages', 'EntryPoints', 'Productions', ]




    def CompLabelsNoNodes(self):
        return [*self.CompLabelsSpot(), 'PipePoints', 
                'PipeSegments', 'PipeLines']




    def CompLabels(self):
        return [*self.CompLabelsNoNodes(),  'Nodes']






    def test_methods(self, CompNames = [], InAttribNames = [],  CalcMethods = [], ErrorMethods = ['STD']):
        """Method that fills missing attribute values.  Input is **CompNames** a list of components, **InAttribNames** a list of attribute names, 
        **CalcMethods ** a list of strings indicating the method used to generate the attribute values.
        Different method of estimating the uncertainty of the estimate is given with **ErrorMethods**.
        
        \n.. comments: 
		Input:
			CompNames       List of component string names, for which this 
                            shall be carried out.
                            (default = [], hence all possible components)
            InAttribNames   List of attrribute names, that are the source of the data
                            (default = [], hence all possible components)
            CalcMethods     List of strings, indicating the method used to generate
                            the missing attribute values.  
                            (default = all available one)
            ErrorMethods    List of strings, indicating the method used to generate
                            the associated uncertainty of the estimate.  
                            (default = ['STD'])
        
        """
        import Code.K_Stats         as K_Stats
        import Code.M_Stats         as M_Stats
        RetStatsSummary        =  K_Stats.StatsSummary()
        
        
        
        # in case that no Component Labels are given
        if CompNames  == []:
            CompNames  = self.CompLabels()
            
        if CalcMethods == []:
            CalcMethods = ['min', 'median', 'mean', 'max']
            
            
        # Loop for each Component
        for compName in CompNames:
            if len(self.__dict__[compName]) > 0:
                # Working out which attributes to do if not supplied
                if InAttribNames == []:
                    if len(self.__dict__[compName]) > 0:
                        TheseInAttribNames = []
                        for key in self.__dict__[compName][0].param.keys():
                            TheseInAttribNames.append(key)
                else:
                    TheseInAttribNames = InAttribNames
                    
    
                    
                # getting list of ErrorMethods
                ThisErrorMethods = []
                if len(ErrorMethods) != len(TheseInAttribNames):
                    for idx in range(len(TheseInAttribNames)):
                        ThisErrorMethods.append(ErrorMethods[0])
                else:
                    ThisErrorMethods = ErrorMethods
    
                    
                    
                    
                #KLoop to go through each attribute
                for idx, thisAttribName in enumerate(TheseInAttribNames):
                    for calcMethod in CalcMethods:
                        # getting list of CalcMethods
                        CalcMethod = []
                        CalcMethod.append(calcMethod)
                        ThisCalcMethods = []
                        CalcMethod = list(CalcMethod)
                        if len(CalcMethod) != len(TheseInAttribNames):
                            for idx in range(len(TheseInAttribNames)):
                                ThisCalcMethods.append(CalcMethod[0])
                        else:
                            ThisCalcMethods = CalcMethod
                            
                        
                        thisCalcMethod      = ThisCalcMethods[idx]
                        thisErrorMethod     = ThisErrorMethods[idx]
        
                        if thisAttribName != 'source' and thisAttribName != 'license' and thisAttribName != 'operator_name' and thisAttribName != 'comment' and thisAttribName != 'pipe_name' and thisAttribName != 'lat_mean'  and thisAttribName  != 'long_mean':
                            if thisAttribName  =='end_year':
                                thisAttribName  = thisAttribName 
                            
                            # Get the data
                            thisData = self.get_Attrib(compName, thisAttribName)
#                            print('===================')
#                            print('compName',compName)
#                            print('thisAttribName', thisAttribName)
#                            print('thisCalcMethod', thisCalcMethod)
#                            print('thisErrorMethod',thisErrorMethod)
    
                            # derive new attrib value and uncertainty
                            value, uncertainty = M_Stats.get_Value(thisData, thisCalcMethod, thisErrorMethod)
                            if len(value) >0 and len(uncertainty)>0:
                                RetStatsSummary.__dict__[compName].append(K_Stats.__dict__[compName](AttribName = thisAttribName, ModelName = thisCalcMethod, ErrorName = thisErrorMethod, ModelVal = value[0], ErrorVal = uncertainty[0]))
                            else:
                                RetStatsSummary.__dict__[compName].append(K_Stats.__dict__[compName](AttribName = thisAttribName, ModelName = thisCalcMethod, ErrorName = thisErrorMethod, ModelVal = 'NDA', ErrorVal = -999))
    
        

        return RetStatsSummary


    def sim_attribValues(self, CompNames = [], InAttribNames = [], OutAttribNames = [], CalcMethods = ['median'], ErrorMethods = ['STD'], ReplaceMethods = ['missingValues']):
        """Method that fills missing attribute values.  Input is **CompNames** a list of components, **InAttribNames** a list of attribute names, 
        **OutAttribNames**  a list of attribute names into which the attribute values will be written to, **CalcMethods ** a list of strings indicating
        the method used to generate the attribute values, and **ReplaceMethods** a list of string, indicating for which attribute elements this shall be carried out.
        Different method of estimating the uncertainty of the estimate is given with **ErrorMethods**.
        
        \n.. comments: 
		Input:
			CompNames       List of component string names, for which this 
                            shall be carried out.
                            (default = [], hence all possible components)
            InAttribNames   List of attrribute names, that are the source of the data
                            (default = [], hence all possible components)
            OutAttribNames  List of attribute names, into which the generated attribute
                            values shall be written into. 
                            (default = InAttribNames)
            CalcMethods     List of strings, indicating the method used to generate
                            the missing attribute values.  
                            (default = ['median'])
            ErrorMethods    List of strings, indicating the method used to generate
                            the associated uncertainty of the estimate.  
                            (default = ['STD'])
            ReplaceMethods  List of string, indicating for which data values 
                            the simulation shall be carried out
                            (default  ['missingValues'])
        
        """
        
        # in case that no Component Labels are given
        if CompNames  == []:
            CompNames  = self.CompLabels()
            
        # Loop for each Component
        for compName in CompNames:
            # Working out which attributes to do if not supplied
            if InAttribNames == []:
                if len(self.__dict__[compName]) > 0:
                    TheseInAttribNames = []
                    for key in self.__dict__[compName][0].param.keys():
                        TheseInAttribNames.append(key)
            else:
                TheseInAttribNames = InAttribNames
                
                
            # getting output data list
            ThisOutAttribNames = []
            if len(OutAttribNames) != len(TheseInAttribNames):
                if len(OutAttribNames) > 0:
                    for idx in range(len(TheseInAttribNames)):
                        ThisOutAttribNames.append(OutAttribNames[0])
                else:
                    ThisOutAttribNames = TheseInAttribNames
            else:
                ThisOutAttribNames = OutAttribNames
            
            
            # getting list of CalcMethods
            ThisCalcMethods = []
            if len(CalcMethods) != len(TheseInAttribNames):
                for idx in range(len(TheseInAttribNames)):
                    ThisCalcMethods.append(CalcMethods[0])
            else:
                ThisCalcMethods = CalcMethods

                
            # getting list of CalcMethods
            ThisErrorMethods = []
            if len(ErrorMethods) != len(TheseInAttribNames):
                for idx in range(len(TheseInAttribNames)):
                    ThisErrorMethods.append(ErrorMethods[0])
            else:
                ThisErrorMethods = ErrorMethods

                
            # getting list of ReplaceMethods
            ThisReplaceMethods = []
            if len(ReplaceMethods) != len(TheseInAttribNames):
                for idx in range(len(TheseInAttribNames)):
                    ThisReplaceMethods.append(ReplaceMethods[0])
            else:
                ThisReplaceMethods = ReplaceMethods
                
                
            #KLoop to go through each attribute
            for idx, thisAttribName in enumerate(TheseInAttribNames):
                
                
#                print('    Component:', compName, '  Attrib:', thisAttribName)
                thisOutAttribName   = ThisOutAttribNames[idx]
                thisCalcMethod      = ThisCalcMethods[idx]
                thisReplaceMethod   = ThisReplaceMethods[idx]
                thisErrorMethod     = ThisErrorMethods[idx]

                # Get the data
                thisData = self.get_Attrib(compName, thisAttribName)
                
                # derive new attrib value and uncertainty
                value, uncertainty = M_Stats.get_Value(thisData, thisCalcMethod, thisErrorMethod)
                
                # place new attrib value
                if len(value) > 0:
#                    print('            Data found')
                    if thisReplaceMethod == 'missingValues':
                        for idx, elem in enumerate(self.__dict__[compName]):
                            if elem.uncertainty[thisOutAttribName] == -999:
                                elem.param[thisOutAttribName]       = value[idx]
                                elem.uncertainty[thisOutAttribName] = uncertainty[idx]
                                elem.method[thisOutAttribName]      = thisCalcMethod
                            
                    else:
                        print('ERROR: K_Netze.sim_attribValues: code not written for this method.')
#                else:
#                    print('            No data found')
                
                
            
        

        
        
    def setup_SameAttribs(self, CompNames = [], fillVal = None):    
        """Sets up the attributes for each element of a component. Results that each element has the same 
        attributes, and that that under method and uncertainty it is stated: two options are possible:
            1) data value was read in, hence method will 'raw', and uncertainty will be 0
            2) data value not given, hence method is None, and uncertinaty will be -999
        
        """
    
        # In case no Componenten given, hence do all
        if len(CompNames) == 0:
            CompNames = self.CompLabels()
            

        # Loop for each component
        for compName in CompNames:
            paramList   = []
            # doing each element and getting keys
            for elem in self.__dict__[compName]:
                for key in elem.param.keys():
                    paramList.append(key)
            
            # making unique keys
            paramList = list(set(paramList))

            # populating with fill value for all attributes not initiated.
            for elem in self.__dict__[compName]:
                for key in paramList:
                    if key not in elem.param.keys():
                        elem.param.update({key: fillVal})
                        elem.method.update({key: None})
                        elem.uncertainty.update({key: -999})
                    elif elem.param[key] == None:
                        elem.method.update({key: None})
                        elem.uncertainty.update({key: -999})
                    elif elem.param[key] == '':
                        elem.method.update({key: None})
                        elem.uncertainty.update({key: -999})
                    elif isinstance(elem.param[key], float):
                        if math.isnan(elem.param[key]):
                            elem.method.update({key: None})
                            elem.uncertainty.update({key: -999})
                        else:
                            elem.method.update({key: 'raw'})
                            elem.uncertainty.update({key: 0})
                    else:
                        elem.method.update({key: 'raw'})
                        elem.uncertainty.update({key: 0})
                
                # sorting the dicts
                elem.uncertainty    = dict(sorted(elem.uncertainty.items()))
                elem.param          = dict(sorted(elem.param.items()))
                elem.method         = dict(sorted(elem.method.items()))

        
        
    def declar_SameAttribs(self, CompNames = [], fillVal = None):    
        """Assures, that all elements in a component have the same attributes.  Hence 
        elements will get attributes with value **fillVal**, in case that attribute
        not given in either param, method, and or uncertainty.
        
        """
    
        # In case no Componenten given, hence do all
        if len(CompNames) == 0:
            CompNames = self.CompLabels()
            
        # Loop for each component
        for compName in CompNames:
            # doing each element and getting keys
            for elem in self.__dict__[compName]:
                paramList   = []
                methodList  = []
                uncertList  = []
                for key in elem.param.keys():
                    paramList.append(key)
                for key in elem.method.keys():
                    methodList.append(key)
                for key in elem.uncertainty.keys():
                    uncertList.append(key)
            
            # making unique keys
            paramList  = list(set(paramList))
            methodList = list(set(methodList))
            uncertList = list(set(uncertList))
            
            # populating with fill value for all attributes not initiated.
            for elem in self.__dict__[compName]:
                for key in paramList:
                    if key not in elem.param.keys():
                        elem.param.update({key: fillVal})
                
                for key in methodList:
                    if key not in elem.method.keys():
                        elem.method.update({key: fillVal})
                    
                for key in uncertList:
                    if key not in elem.uncertainty.keys():
                        elem.uncertainty.update({key: fillVal})



        
    def fill_length(self, compName = 'PipeSegments'):
        """Fills alle None or missing values of param['length'] with length in [km] for each element
        
		\n.. comments: 
		Input:
			compName        string, of Component element
        """

        for pipe in self.__dict__[compName]:
            if pipe.param['length'] is None:
                pipe.param['length']        = pipe.getPipeLength()
                pipe.uncertainty['length']  = 1/len(pipe.lat)
                pipe.method['length']       = 'fill_length(' + compName + ')'



            
    def replace_length(self, compName = 'PipeSegments'):
        """Determins all param['length'] with length in [km] for each element
        
		\n.. comments: 
		Input:
			compName        string, of Component element
        """

        for pipe in self.__dict__[compName]:
            pipe.param['length'] = pipe.getPipeLength()
            pipe.uncertainty['length']  =  1 / len(pipe.lat)
            pipe.method['length']       = 'replace_length(' + compName + ')'


        
        
    def copyAttribValue(self, compName1 = 'Nodes', compName2 = 'PipeSegments', attribName1 = 'id', atribName2 = 'node_id', methodName = 'latlong'):
        """Method of copying of attribute values, from one component elements to another component elements
        
		\n.. comments: 
		Input:
			compName1       string, of source Component
							(default = 'Nodes'), 
			compName2       string, of destination component
							(default = 'PipeSegments'), 
			attribName1     string, attribute from source elements
							(default = 'id'), 
			atribName2      string, attribute from destination elements
							(default = 'node_id'), 
			methodName      string, selecting the method to use.  Currently only one implemented.
							'latlong': lat long values need to be the same in source and destination component elements.
							(default = 'latlong') 
        
        """
        
        if methodName == 'latlong':
            
            # disecting the input source data 
            attribName1  = []
            PolyPairs1   = K_Component.PolyLine(lat = [], long = [])
            
            for comp in self.__dict__[compName1]:
                attribName1.append(comp.id)
                if type(comp.lat) == list:
                    for ll in comp.lat:
                        PolyPairs1.lat.append(round(ll, roundVal))
                    for ll in comp.long:
                        PolyPairs1.long.append(round(ll, roundVal))
                elif comp.lat == None:
                    print('Somtihing fishy here for: ' + compName1)
                    comp.all()
                    print(' ')
                else:
                    PolyPairs1.lat.append(round(comp.lat, roundVal))
                    PolyPairs1.long.append(round(comp.long, roundVal))
            
            
            # now going through each element of the destination data set
            for idx, comp2 in enumerate(self.__dict__[compName2]):
                if isinstance(comp2.__dict__[atribName2], list):
                    Vals = comp2.__dict__[atribName2]
                    if len(Vals) == 2:
                        latlong0    = [round(comp2.long[0], roundVal), round(comp2.lat[0], roundVal)]
                        pops0       = M_FindPos.find_pos_LatLongInPoly(latlong0, PolyPairs1, '==')
                        latlong1    = [round(comp2.long[-1], roundVal), round(comp2.lat[-1], roundVal)]
                        pops1       = M_FindPos.find_pos_LatLongInPoly(latlong1, PolyPairs1, '==')
                        
                        if len(pops1) == 1 and len(pops0) ==1:
                            comp2.__dict__[atribName2] = [attribName1[pops0[0]], attribName1[pops1[0]]]
                        else:
                            print('ERROR: K_Netze.copyAttribValue: incorrect number of entries for  element ' + atribName2 + '. Code not written yet 1.')
                            print('pops1: ')
                            print(comp2.name)
                            print(comp2.node_id)
                    elif len(Vals) == 1 and isinstance(comp2.long, float):
                        latlong0    = [round(comp2.long, roundVal), round(comp2.lat,roundVal)]
                        pops0       = M_FindPos.find_pos_LatLongInPoly(latlong0, PolyPairs1, '==')
                        if len(pops0) == 1:
                            if isinstance(comp2.__dict__[atribName2], list):
                                comp2.__dict__[atribName2] = [attribName1[pops0[0]]]
                            else:
                                comp2.__dict__[atribName2] = attribName1[pops0[0]]
                        else:
                            print('ERROR: K_Netze.copyAttribValue: incorrect number of entries for  element ' + atribName2 + '. Code not written yet 2.')
                            print('pops1: ')
                            print(comp2.name)
                            print(comp2.node_id)
                        
                    
                    elif len(Vals) == len(comp2.long):
                        for idx_2 in range(len(Vals)):
                            latlong0    = [round(comp2.long[idx_2], roundVal), round(comp2.lat[idx_2],roundVal)]
                            pops0       = M_FindPos.find_pos_LatLongInPoly(latlong0, PolyPairs1, '==')
                            if len(pops0) == 1:
                                comp2.__dict__[atribName2][idx_2] = attribName1[pops0[0]]
                            else:
                                print('ERROR: K_Netze.copyAttribValue: incorrect number of entries for  element ' + atribName2 + '. Code not written yet 3.')
                                print('pops1: ')
                                print(comp2.name)
                                print(comp2.node_id)

                    else:
                        print('ERROR: K_Netze.copyAttribValue: code for element ' + atribName2 + ' not written yet 3.')
                elif  isinstance(comp2.__dict__[atribName2], str):
                    if isinstance(comp2.long, list):
                        latlong = [round(comp2.long[0], roundVal), round(comp2.lat[0], roundVal)]
                    else:
                        latlong = [round(comp2.long, roundVal), round(comp2.lat, roundVal)]
                    pops    = M_FindPos.find_pos_LatLongInPoly(latlong, PolyPairs1, '==')
                    if len(pops) == 1:
                        comp2.__dict__[atribName2] = attribName1[pops[0]]
                        
                else:
                    print('ERROR: K_Netze.copyAttribValue: code for element type ' + atribName2 + ' not written yet 4.')
            
        else:
            print('ERROR: K_Netze.copyAttribValue: code for input method ' + methodName + ' not written yet 5.')
            self.__dict__[compName2] = []
        
        
        
        
    def testUniqueAttribVal(self, compName = 'Nodes', attribName = 'node_id'):
        """Method to check if attributes of all elements of a component are unique.
        Component supplied via **compName** as string, and attribute label given as 
        **attribName** as string as well.
		
		\n.. comments: 
		Input:
			compName: 	String of component namen
						(default = 'Nodes')
			attribName: String of attribute name
						(default = 'node_id')
		Output:
			Boolean		True/False
        """
        
        values = []
        if attribName in ['id', 'name', 'source_id', 'node_id', 'country_code']:
            for elem in self.__dict__[compName]:
                values.append(elem.__dict__[attribName])
        else:
            for elem in self.__dict__[compName]:
                values.append(elem.param.__dict__[attribName])
        
        if len(self.__dict__[compName]) == len(list(set(values))):
            return True
            
        return False
    
    
    

    def AttribDesc(self):
        """Method of supplying a dict of attribute names and their meanings.
		
		\n.. comments: 
		Output:
			Boolean		True/False
        """        
        return {'id': 								'unique id of element', 
                    'name': 						'', 
                    'name_short':					'',
                    'source_id': 					'', 	
                    'node_id':						'node id',
                    'lat':							'latitude in decimal degrees',
                    'long':							'longitude in decimal degrees',
                    'lat_mean':                     'average latitude in decimal degrees',
                    'long_mean':                    'average longitude in decimal degrees',
                    'country_code':					'2 letter country code',
                    'comp_id':						'element ID',
                    'start_year':                   'start year',
                    'end_year':                     'end year',
                    'source':                       'source of data',
                    'license':                      'License of data',
                    'elevation_m':                  'elevation of location [m]', 
                    
                    'access_regime':                '???? (options found are: TPA, nTPA, rTPA, NoTPA)',
                    'diameter_mm':                  'diameter of pipeline/pipesegment [mm]',
                    'diameter_pipe2comp_mm':        'diameter of pipeline/pipesegment [mm]',
                    'diameter_comp2pipe_mm':        'diameter of pipeline/pipesegment [mm]',
                    
                    'exact':                        'exact location of element, verefication through sat data',
                    'eic_code':                     'EIC facility code',
                    'entsog_key':                   'EntsoG key',
                    'entsog_nam':                   'EntsoG name',
                    'facility_code':                'GIE facility code',
                    'operator_name':                'operator name of element',
                    'operator_Z':                   'additional operator name of element',
                    'pipe_name':                    'name of pipe',
                    'uncer':                        'uncertainty',
                    'method':                       'mothod of determining value if not given as part of source data set',
                    'energy_node':                  'node from which gas (energy) taken to run compressors', 

                    'Is_H_gas':                     'boolean if gas is of type H',
                    'H_L_conver':                   'gas type converter (H2L and L2H)',
                    'gas_capacity':                 'capacity (e.g. of commpressor or pipe segment)',

                    'is_planned':                   'boolean if element is planned',
                    'is_bothDirection':             'boolean if direction is reversable',
                    'is_crossBorder':               'boolean if location of element is on border',
                    'is_euCrossing':                'EntsoG boolean if element is located on border',
                    'is_inEU':                      'is in EU', 
                    'is_onShore':                   'boolean if storage is onshore',
                    'is_abandoned':                 'indicating if pipeline is abandoned',
                    'is_singleOperator':            'EntsoG boolean if element is operatored by single operator',
                    'is_virtualPoint':              'EntsoG boolean if element is a virtuell element',
                    'is_virtualPipe':               'LKD boolean, if pipe is virtual',
                    'is_interconnection':           'is interconnection between ???',
                    'is_import':                    'boolean if element is import/entry point',
                    'is_export':                    'boolean if element is expor/exitt point',
                    'is_pipeInPipe':                'is ???',
                    
                    
                    'has_data':                     'EntsoG boolean to have data or not to have data',
                    'has_gasCooler':                'boolean re existance of gas cooler for compressors',
                    
                    
                    'from_systemLabel'              :'Gas flow from system label',
                    'from_infrastructureTypeLabel'  :'Gas flow from infrastructure type label',
                    'from_operatorKey'              :'Gas flow from operator key',
                    'from_directionKey'             :'either entry or exit',
                    'from_TsoItemIdentifier'        :'Gas flow from TSO item identifier?',
                    'from_pointKey'                 :'Gas flow from point Key',
                    'from_pointLabel'               :'Gas flow from point label',
                    'from_node':                    'from node', 
                    
                    'to_systemLabel'                :'Gas flow to system label',
                    'to_infrastructureTypeLabel'    :'Gas flow to infrastructure type label',
                    'to_BzKey'                      :'Gas flow to Bz key',
                    'to_operatorKey'                :'Gas flow to opertor key',
                    'to_pointKey'                   :'Gas flow to point key',
                    'to_node':                      'to node', 
                    'to_countryLabel':              'node information to which gas flow is going with country code of', 
                    
                    'length':                       'length of pipeline/pipesegment [km]',
                    
                    'heatTransferCoefficient_W_per_m2_per_K':'Heat Transfer coefficient in [W m^-2 K^-1]', 
                    'gasTemperature_C':             'temperature of gas [degree C]', 
                    'calorificValue_MJ_per_m3':     'gas property [MJ m^-3]', 
                    'normDensity_kg_per_m3':        'normalized gas density [kg m^-3]', 
                    'molarMass_kg_per_kmol':        'molar mass fo the gas [kg kmol^-1]', 
                    'dragFactor_pipe2comp':         '???', 
                    'dragFactor_comp2pipe':         '???', 
                    'internalBypassRequired':       '???', 
                    
                    'max_pressure_bar':             'maximum operating pressure e.g. compressor) [bar]',
                    'min_pressure_bar':             'maximum operating pressure e.g. compressor) [bar]',
                    'min_pressure_pipe2comp_bar':   'minimum pressure from pipe to compressor [bar]', 
                    'max_pressure_comp2pipe_bar':   'maximum pressure from compressor to pipe [bar]', 
                    'max_cap_M_m3_per_d':           'maximum daily gas flow [M m^3 d^-1]',
                    'min_cap_M_m3_per_d':           'minimum daily gas flow [M m^3 d^-1]',
                    
                    'max_cap_store2pipe_M_m3_per_d':'max gas flow from storage into pipe [M m^3 d^-1]',
                    'max_cap_pipe2store_M_m3_per_d':'max gas flow from pipe into store [M m^3 d^-1]',
                    
                    'max_cap_store2pipe_GWh_per_d': 'max rate of gasflow from storage into pipe [GWh d^-1]',
                    'max_cap_pipe2store_GWh_per_d': 'max rate of gasflow from pipe into storage [GWh d^-1]',
                    'max_cap_GWh_per_d':            'max rate of gasflow in an element [GWh d^-1]', 
                    
                    'max_workingGas_M_m3':          'max woking gas in units of [M m^3]',
                    'max_workingLNG_M_m3':          'max working LNG gas volume  [M m^3]',
                    'max_cushionGas_M_m3':          'max cushion gas in a UGS [M m^3]', 
                    'max_workingGas_TWh':           'max storage working gas in units of [TWh]',
                    'max_production':               '???',
                    
                    'loss_pressure_pipe2comp_bar':  'pressure loss from pipe to compressor [bar]', 
                    'loss_pressure_comp2pipe_bar':  'pressure loss from compressor to pipe [bar]', 
                    

                    'max_power_MW':                 'total power of sum of turbines  [MW]',

                    'max_cap_store2pipe':           'max gas flow from storage into pipe [M m^3 d^-1]',
                    'max_cap_pipe2store':           'maximum capacity of gas flow from pipeline into storage',
                    'median_cap_store2pipe':        'median capacity of gas flow from storage into pipeline',


                    'num_turb':                     'number of gas turbines at compressor location',
                    'num_compressor':               'number of compressors along the pipeline/pipesegment',
                    
                    'roughness_mm':                 'roughness value of the gas pipeline [mm]',
                    'storage_LNG_Mt':               'storage at LNG terminal [Mt]',
                    'store_type':                   'type of gas storage (e.g. empty gas field)',
                    
                    'turbine_fuel_isGas_1':         'boolean if energy source of turbine 1 is gas (0 = electic)',
                    'turbine_type_1':               'type or name of the turbine 1', 
                    'turbine_power_1_MW':           'max power of turbine 1 [MW]',
                    'turbine_fuel_isGas_2':         'boolean if energy source of turbine 2 is gas (0 = electic)',
                    'turbine_type_2':               'type or name of the turbine 2', 
                    'turbine_power_2_MW':           'max power of turbine 2 [MW]',
                    'turbine_fuel_isGas_3':         'boolean if energy source of turbine 3 is gas (0 = electic)',
                    'turbine_type_3':               'type or name of the turbine 3', 
                    'turbine_power_3_MW':           'max power of turbine 3 [MW]',
                    'turbine_fuel_isGas_4':         'boolean if energy source of turbine 4 is gas (0 = electic)',
                    'turbine_type_4':               'type or name of the turbine 4', 
                    'turbine_power_4_MW':           'max power of turbine 4 [MW]',
                    'turbine_fuel_isGas_5':         'boolean if energy source of turbine 5 is gas (0 = electic)',
                    'turbine_type_5':               'type or name of the turbine 5', 
                    'turbine_power_5_MW':           'max power of turbine 5 [MW]',
                    'turbine_fuel_isGas_6':         'boolean if energy source of turbine 6 is gas (0 = electic)',
                    'turbine_type_6':               'type or name of the turbine 6', 
                    'turbine_power_6_MW':           'max power of turbine 6 [MW]',
                    
                    'porosity_perc':                'porosity of storage medium [%]',
                    'permeability_mD':              'rate of diffusion of a gas under pressure through soil [mD]',
                    'num_storage_wells':            'number of storage wells associated with the UGS',
                    'net_thickness_m':              'net thickness of ??? [m]',
                    'structure_depth_m':            'Depth top structure, resp. cavern roof [m]', 
                    'storage_formation':            'storage formation, e.g. Solling sandstone middle Bunter',
                    'pipe_class_type':              'pipe class type (A..E)'}
#                    }
        

    
    
    
    
    def remove_unConnectedComponents(self, CompNames = []):
        """Removing spot components (e.g. Compressors) from network, in case 
        that they are not connected to a PipeSegment
        """
        # Generation of list for which components to apply this method
        if CompNames == []:
            CompNames = self.CompLabelsSpot()
            
        # Generation of Nodes list of PipeSegments
        NodesOut    = []
        for nn in self.PipeSegments:
                NodesOut.append(nn.node_id[0])
                NodesOut.append(nn.node_id[-1])
    
        # going through all elements of all s[pot components and marke those ones
        # where their 
        NodesKill = []
        for compName in CompNames:
            for elem in self.__dict__[compName]:
                if elem.node_id[0] not in NodesOut:
                    elem.lat = None
                    NodesKill.append(elem.node_id)
                    
        # removing those components that have been marked
        self.select_byAttrib(CompNames = [], AttribName = 'lat', AttribVal = [], methodStr = '!=None')
    
        # now removing those nodes
        for node in self.Nodes:
                if node.node_id[0] not in NodesKill:
                    node.lat = None
        # removing those components that have been marked
        self.select_byAttrib(CompNames = ['Nodes'], AttribName = 'lat', AttribVal = [], methodStr = '!=None')
        
        return []
    
    
    
    
    def remove_unUsedNodes(self):
        
        CompNames   = self.CompLabelsNoNodes()
        Nodes       = []
        AllNodesId  = []
        
        for compName in CompNames:
            Nodes = self.add_Nodes(compName,[])
            for nn in Nodes:
                AllNodesId.append(*nn.node_id)
                
        NodesOut = []
        for nn in self.Nodes:
            if nn.id in AllNodesId:
                NodesOut.append(nn)
        
        self.Nodes = NodesOut
        
        
        
    
    def removePolyPoints(self, compName = None):
        """Method of removing any polyPoints from PipeLine/Segment **compName**
		
		\n.. comments: 
		Input:
			compName 	String of component (works only for PipeLines and PipeSegments)
						(default = None)
		Output:
			[] """
        
        for pipe in self.__dict__[compName]:
            pipe.lat    = [pipe.lat[0],  pipe.lat[-1]]
            pipe.long   = [pipe.long[0], pipe.long[-1]]
        
        
        
    
    def cleanUpNodes(self, compNames = [], skipNodes = False):
        
        if len(compNames) == 0:
            compNames = self.CompLabels()
            
        if skipNodes == True:
            if 'Nodes' in compNames:
                compNames.remove('Nodes')
            
        Nodes = []
        for comp in compNames:
            Nodes   = self.add_Nodes(comp, Nodes)
            
            
        Nodes   = M_Shape.reduceElement(Nodes, reduceType = 'LatLong', makeUnique = True)
        self.Nodes = Nodes

        for comp in compNames:
            self.copyAttribValue('Nodes', comp,  'id', 'node_id',  'latlong')

        self.copyAttribValue('Nodes', 'Nodes',  'id', 'name', 'latlong')
        
        
        
        
    def merge_Nodes_Comps(self, compNames = []):
        """???"""
        
        # in case that no component labels given, hence will do all of them.            
        if compNames == []:
            compNames = self.CompLabels()
            
        
        # Getting Nodes of components, except Nodes
        compNodes  = []
        for compName in compNames:
            compNodes = self.add_Nodes(compName, compNodes)
            
        # Shrinking CompNodes to same
        compNodes = M_Shape.reduceElement(compNodes, reduceType = 'LatLong', makeUnique = True)
        
        latLong = []
        nodeId  = []
        for idx, nn in enumerate(compNodes):
            nodeId.append('N_' + str(idx))
            latLong.append(str(round(nn.lat, roundVal)) + str(round(nn.long, roundVal)))
        
        
        for compName in compNames:
            
            # All components that are spot components
            if compName in self.CompLabelsSpot():
                for idx, elem in enumerate(self.__dict__[compName]):
                    thisLatLong     = str(round(elem.lat, roundVal)) + str(round(elem.long, roundVal)) 
                    pos             = M_FindPos.find_pos_StringInList(thisLatLong, latLong)
                    pos
                    elem.node_id    = [nodeId[pos[0]]]
                
            # Component Nodes
            elif compName == 'Nodes':
                NodeId = []
                for idx, elem in enumerate(self.Nodes):
                    thisLatLong     = str(round(elem.lat, roundVal)) + str(round(elem.long, roundVal)) 
                    pos             = M_FindPos.find_pos_StringInList(thisLatLong, latLong)
                    if nodeId[pos[0]] not in  NodeId:
                        elem.id         = nodeId[pos[0]]
                        elem.node_id    = [nodeId[pos[0]]]
                        NodeId.append(nodeId[pos[0]])
                
            # Component PipeSegments
            elif compName == 'PipeSegments':
                for idx, elem in enumerate(self.PipeSegments):
                    thisLatLong     = str(round(elem.lat[0], roundVal)) + str(round(elem.long[0], roundVal)) 
                    pos             = M_FindPos.find_pos_StringInList(thisLatLong, latLong)
                    elem.node_id[0] = nodeId[pos[0]]
            
                    thisLatLong     = str(round(elem.lat[-1], roundVal)) + str(round(elem.long[-1], roundVal)) 
                    pos             = M_FindPos.find_pos_StringInList(thisLatLong, latLong)
                    elem.node_id[1] = nodeId[pos[-1]]
        
        
        
        
    
    def add_Nodes(self, compName = [], NodesIn = []):
        """Method of converting of non-Node elements to Node elements, and adding them to Nodes

		\n.. comments: 
		Input:
			compName: 	String of component (works only for PipeLines and PipeSegments)
						(default = None)
			NodesIn: 	List of existing nodes.
						(default = [])
        """    
        
        RetNodes   = NodesIn.copy()
        if compName == []:
            # in case that no component labels given, hence will do all of them.            
            for comp in self.CompLabelsNoNodes():
                if len(self.__dict__[comp]) > 0:
                    #print(comp )
                    NodesIn = self.add_Nodes(comp, NodesIn)
            
            self.Nodes  = M_Shape.reduceElement(NodesIn, reduceType = 'LatLong')
            RetNodes    = self.Nodes

        elif isinstance(compName, list):
            # in case that no component labels given, hence will do all of them.            
            for comp in compName:
                if len(self.__dict__[comp]) > 0:
                    #print(comp )
                    NodesIn = self.add_Nodes(comp, NodesIn)
            
            self.Nodes  = M_Shape.reduceElement(NodesIn, reduceType = 'LatLong')
            RetNodes    = self.Nodes
            
        elif len(self.__dict__[compName]) > 0:
            # in case that long long are list
            if compName == 'Nodes':
                RetNodes = copy.deepcopy(self.Nodes) + copy.deepcopy(NodesIn)
            else:
                if isinstance(self.__dict__[compName][0].lat, list):
                    # check if lat/long given as list, applies to PipeLines
                    for elem in self.__dict__[compName]:
                        id              = elem.node_id[0] # str(len(RetNodes))
                        node_id         = [id]
                        name            = id # elem.name + '_S'
                        country_code    = elem.country_code
                        if isinstance(country_code, list):
                            source_id       = [country_code[0] + '_' + str(len(RetNodes))]
                            country_code_in = country_code[0]
                        else:
                            source_id       = [country_code + '_' + str(len(RetNodes))]
                            country_code_in = country_code
                        lat             = elem.lat[0]
                        long            = elem.long[0]
                        # Start Node
                        RetNodes.append(K_Component.Nodes(id = id, 
                                name        = name, 
                                node_id     = node_id, 
                                source_id   = source_id, 
                                lat         = lat, 
                                long        = long, 
                                country_code = country_code_in))
                        # End Node
                        id              = elem.node_id[-1] # str(len(RetNodes))
                        node_id         = [id]
                        name            = id #elem.name + '_E'
                        lat             = elem.lat[-1]
                        long            = elem.long[-1]
                        if isinstance(country_code, list):
                            source_id       = [country_code[-1] + '_' + str(len(RetNodes))]
                            country_code_in = country_code[-1]
                            
                        else:
                            source_id       = [country_code + '_' + str(len(RetNodes))]
                            country_code_in = country_code
                            
                        RetNodes.append(K_Component.Nodes(id = id, 
                                name        = name, 
                                node_id     = node_id, 
                                source_id   = source_id, 
                                lat         = lat, 
                                long        = long, 
                                country_code = country_code_in))
                        
                # in case that lat long are just numbers, but not lists
                else:
                    for idx_3, elem in enumerate(self.__dict__[compName]):
                        if isinstance(elem.node_id, list):
                            id              = elem.node_id[0]
                        else:
                            id              = elem.node_id
                        node_id         = [id]
                        name            = id #elem.name
                        country_code    = elem.country_code
                        if isinstance(country_code, list):
                            source_id       = [country_code[-1] + '_' + str(len(RetNodes))]
                            country_code_in = country_code[-1]
                            
                        else:
                            try:
                                source_id       = [country_code + '_' + str(len(RetNodes))]
                            except:
                                source_id       = ['EU' + '_' + str(len(RetNodes))]
                            country_code_in = country_code
                        
                        RetNodes.append(K_Component.Nodes(id = id, 
                                name        = name, 
                                node_id     = node_id,
                                source_id   = source_id, 
                                lat         = elem.lat, 
                                long        = elem.long, 
                                country_code = country_code_in))
            
        return RetNodes
    
        
       
  
    
    def copy(self):
        """Method to create copy of instance.
        """
        
         # BookKeeping
        self.Processes.append(K_Component.Processes('K_Netze.Netz..copy: Creation of copy of  Netze instance'))
        
        # Initialization
        self2 = NetComp()
        try:
            for key in sorted(self.__dict__.keys()): 
                if self.__dict__[key] is not None:
                    for dd  in self.__dict__[key]:
                        self2.__dict__[key].append(dd)
        except:
            pass
        return self2
    
    
    

    def getcountry4pipelines(self):
        """Method of getting pipeline CountryCode from Nodes-list exists
        """
        
        for i in range(len(self.PipeLines)):
            countrycodelist=[]
            for id in self.PipeLines[i].node_id:
                countrycode=self.Nodes[ast.literal_eval(repr(self.Nodes)).index(id)].country_code
                countrycodelist.append(countrycode)
            self.PipeLines[i].country_code=countrycodelist
        print('Got countrycodes for pipelines from nodes list')
        pass

    
    
    
    def all(self):
        """Method of displaying of all attributes from the NetComp class instance.
        """
        
        # checking how many components have more than zero elements
        CompCount = 0
        for key in self.__dict__.keys():
            if len(self.__dict__[key]) > 0:
                CompCount = CompCount + 1
        
        print("--------------------------------------")
        print("{0:30s} {1:>6s}".format('Source ', str(self.SourceName[0])))
        print("{0:30s} {1:>6s}".format('total component type count',str(CompCount)))
        print("--------------------------------------")
        for key in sorted(self.__dict__.keys()): 
            if key == 'SourceName':
                pass
            else:
                print("{0:30s} {1:>6s}".format(key, str(len(self.__dict__[key]))))
                
        print("--------------------------------------")
        print("{0:30s} {1:>6s}".format('Length of PipeLines    [km]', str(round(self.sumLength('PipeLines')))))
        print("{0:30s} {1:>6s}".format('Length of PipeSegments [km]', str(round(self.sumLength('PipeSegments')))))
                



    def sumLength(self, compName):
        """Method returning total sum length of all pipeline/pipeSegment in units of [km]."""
        
        RetSum = 0
        for pipe in self.__dict__[compName]:
            if 'length' in pipe.param:
                if pipe.param['length'] != None:
                    RetSum = RetSum + float(pipe.param['length'])
        return RetSum
        
    
    
    
    def addElement(self, CompName = 'PipeSegments', element = []):
        """Method to add elements **element** to component given through string **CompName**.

        \n.. comments: 
            Input:
				CompName: 	string containing component name to which data is to be added.
							(default = 'PipeSegments')
				element: 	
							(default = [])
			"""

        if element != []:
            comp = self.__dict__[CompName]
            comp.append(element)
            
            self.__dict__[CompName] = comp
        
    
    def remove_Elements(self, CompNames = [], AttribName = 'id', AttribVal = []):
        """Method to remove elements from component **CompName**, where their attribute **AttribName** has the 
        values **AttribVal**.
        
        \n.. comments: 
            Input:
            ------
                CompNames       List of string of name of Component names, or [], then all 
                                component names will generated
								(default = [])
                AttribName      string of attribute name of component to filter on
								(default = 'id')
                AttribVal       value (can be of any type, e.g. int, float, string)
                                on which to filter
								(default = []) """


        if CompNames == []:
            CompNames = self.CompLabels()
        
        for CompName in CompNames:
            RetComp = []
            if AttribVal == None:
                for comp in self.__dict__[CompName]:
                    # checking which ones to remove or keep
                    if comp.__dict__[AttribName] is not None:
                        RetComp.append(comp)
            elif AttribVal == 'nan':
                for idx, comp in enumerate(self.__dict__[CompName]):
                    # checking which ones to remove or keep
                    if math.isnan(comp.__dict__[AttribName]) == False:
                        RetComp.append(comp)
                
            else:
                for comp in self.__dict__[CompName]:
                    # checking which ones to remove or keep
                    if comp.__dict__[AttribName] not in AttribVal:
                        RetComp.append(comp)
            
            self.__dict__[CompName] = RetComp

        pass



    def move_Attrib(self, CompName, AttribNameIn, DictNameIn = '', AttribNamweOut = '', DictNameOut = ''):
        """Method to move attribute values within a element of a component **CompName**, from one attribute **AttribNameIn**, 
        to another attribute **AttribNamweOut**, where the attributes can 
        reside in different dicts **DictNameIn** and **DictNameOut**. 
        
        \n.. comments: 
            Input:
                CompName            String of name of LKD Component name, or string 'all', or string of single component.
                AttribNameIn        String of attribute name of component where the data come from (source)
                DictNameIn          String of the dictionary where the attribute source is part of
                AttribNamweOut      String of attribute name, into which new values will be written into.
                DictNameOut         String of the dictionary where the attribute destination is part of   """
        
        self.Processes.append(K_Component.Processes('move_Attrib: AttribNameIn: ' + AttribNameIn + ', DictNameIn: ' + DictNameIn + ', AttribNamweOut: ' + AttribNamweOut + ', DictNameOut: ' + DictNameOut ))


        if DictNameIn == '' and DictNameOut == '' :
            for comp in self.__dict__[CompName]:
                wert = comp.__dict__[AttribNameIn]
                comp.__dict__[AttribNamweOut] = wert
        elif DictNameIn == '':
            if DictNameOut == 'param':
                for comp in self.__dict__[CompName]:
                    wert = comp.__dict__[AttribNameIn]
                    comp.param.update({AttribNamweOut:  wert})
            elif DictNameOut == 'method':
                for comp in self.__dict__[CompName]:
                    wert = comp.__dict__[AttribNameIn]
                    comp.method.update({AttribNamweOut:  wert})
            elif DictNameOut == 'uncertainty':
                for comp in self.__dict__[CompName]:
                    wert = comp.__dict__[AttribNameIn]
                    comp.uncertainty.update({AttribNamweOut:  wert})
        elif DictNameOut == '' :
            if DictNameIn == 'param':
                for comp in self.__dict__[CompName]:
                    wert = comp.param[AttribNameIn]
                    comp.__dict__[AttribNamweOut] = wert
            elif DictNameIn == 'method':
                for comp in self.__dict__[CompName]:
                    wert = comp.method[AttribNameIn]
                    comp.__dict__[AttribNamweOut] = wert
            elif DictNameIn == 'uncertainty':
                for comp in self.__dict__[CompName]:
                    wert = comp.uncertainty[AttribNameIn]
                    comp.__dict__[AttribNamweOut] = wert
                    
        elif DictNameIn == 'param' and DictNameOut == 'param':
            for comp in self.__dict__[CompName]:
                wert = comp.param[AttribNameIn]
                comp.param.update({AttribNamweOut:  wert})
        elif DictNameIn == 'param' and DictNameOut == 'method':
            for comp in self.__dict__[CompName]:
                wert = comp.param[AttribNameIn]
                comp.method.update({AttribNamweOut:  wert})
        elif DictNameIn == 'param' and DictNameOut == 'uncertainty':
            for comp in self.__dict__[CompName]:
                wert = comp.param[AttribNameIn]
                comp.uncertainty.update({AttribNamweOut:  wert})
            
        elif DictNameIn == 'method' and DictNameOut == 'param':
            for comp in self.__dict__[CompName]:
                wert = comp.method[AttribNameIn]
                comp.param.update({AttribNamweOut:  wert})
        elif DictNameIn == 'method' and DictNameOut == 'method':
            for comp in self.__dict__[CompName]:
                wert = comp.method[AttribNameIn]
                comp.method.update({AttribNamweOut:  wert})
        elif DictNameIn == 'method' and DictNameOut == 'uncertainty':
            for comp in self.__dict__[CompName]:
                wert = comp.method[AttribNameIn]
                comp.uncertainty.update({AttribNamweOut:  wert})
            
        elif DictNameIn == 'uncertainty' and DictNameOut == 'param':
            for comp in self.__dict__[CompName]:
                wert = comp.uncertainty[AttribNameIn]
                comp.param.update({AttribNamweOut:  wert})
        elif DictNameIn == 'uncertainty' and DictNameOut == 'method':
            for comp in self.__dict__[CompName]:
                wert = comp.uncertainty[AttribNameIn]
                comp.method.update({AttribNamweOut:  wert})
        elif DictNameIn == 'uncertainty' and DictNameOut == 'uncertainty':
            for comp in self.__dict__[CompName]:
                wert = comp.uncertainty[AttribNameIn]
                comp.uncertainty.update({AttribNamweOut:  wert})




    def make_Attrib(self, CompNames = [], AttribNameSource = '', AttribNameDestination = '', MethodName = 'median', MethodVal = []):
        """Method to create an additional attribute **AttribNameDestination** for all elements of component **CompName**, 
        where the source attribute is **AttribNameSource**, and the method is given by **MethodName**.
        
        \n.. comments: 
            Input:
                CompName                List of Strings of names of Component name
                                             (default = self.CompLabels())
                AttribNameSource        String of attribute name of component where the data come from (source)
                AttribNameDestination   String of attribute name, into which new values will be written into.
                MethodName              String of method used to generate the new attribute value. Currently implemented options:
                                            'mean'
                                            'min'
                                            'max'    
                                            'const'
                MethodVal               String or value to be used for the 'const' MethodName method.
                    """
        
        
        self.Processes.append(K_Component.Processes('make_Attrib: AttribNameSource: ' + AttribNameSource + ', AttribNameDestination: ' + AttribNameDestination + ', MethodName: ' + MethodName ))
        
        # check if there is a destination attribute, if not then jump out of the function
        if AttribNameDestination == '':
            print('ERROR: K_Netze.make_Attrib: No destination attribute was specified.  No attribute values were generated and written to the network.')
            return
        if AttribNameSource == '' and MethodName != 'const':
            print('ERROR: K_Netze.make_Attrib: No source attribute was specified.  No attribute values were generated and written to the network.')
            return
            
        
        
        if CompNames  == []:
            CompNames  = self.CompLabels()
            
        for CompName in CompNames:
            if MethodName == 'mean':
                if AttribNameDestination in self.AttribLables():
                    for comp in self.__dict__[CompName]:
                        wert = sum(comp.__dict__[AttribNameSource]) / len(comp.__dict__[AttribNameSource])
                        comp.__dict__[AttribNameDestination] = wert
                else :
                    for comp in self.__dict__[CompName]:
                        if AttribNameSource in comp.param:
                            wert = comp.param[AttribNameSource]
                        else:
                            wert = comp.__dict__[AttribNameSource]
                                
                        if wert != None:
                            wert = sum(wert) / len(wert)
                            comp.param.update({AttribNameDestination:  wert})
                            comp.method.update({AttribNameDestination:  'make_Attrib(' + MethodName + ')'})
                            comp.uncertainty.update({AttribNameDestination:  1 / len(comp.__dict__[AttribNameSource])})

            elif MethodName == 'min':
                if AttribNameDestination in self.AttribLables():
                    for comp in self.__dict__[CompName]:
                        wert = min(comp.__dict__[AttribNameSource]) 
                        comp.__dict__[AttribNameDestination] = wert
                else :
                    for comp in self.__dict__[CompName]:
                        wert = min(comp.__dict__[AttribNameSource])
                        comp.param.update({AttribNameDestination:  wert})
                        comp.method.update({AttribNameDestination:  'make_Attrib(' + MethodName + ')'})
                        comp.uncertainty.update({AttribNameDestination:  1 / len(comp.__dict__[AttribNameSource])})
                
            elif MethodName == 'max':
                if AttribNameDestination in self.AttribLables():
                    for comp in self.__dict__[CompName]:
                        wert = max(comp.__dict__[AttribNameSource])
                        comp.__dict__[AttribNameDestination] = wert
                else :
                    for comp in self.__dict__[CompName]:
                        wert = max(comp.__dict__[AttribNameSource])
                        comp.param.update({AttribNameDestination:  wert})
                        comp.method.update({AttribNameDestination:  'make_Attrib(' + MethodName + ')'})
                        comp.uncertainty.update({AttribNameDestination:  1 / len(comp.__dict__[AttribNameSource])})
                
            elif MethodName == 'const':
                if AttribNameDestination in self.AttribLables():
                    for comp in self.__dict__[CompName]:
                        comp.__dict__[AttribNameDestination] = MethodVal
                else :
                    for comp in self.__dict__[CompName]:
                        wert = MethodVal
                        comp.param.update({AttribNameDestination:  wert})
                        comp.method.update({AttribNameDestination:  'make_Attrib(' + MethodName + ')'})
                        comp.uncertainty.update({AttribNameDestination:  0})
            
            else:
                print('K_NEtze.make_Attrib: Code not written in method.')
            


    def select_byAttribLabel(self, CompNames = [], AttribName = '', dict_label = ''):
        """Method of selecting of elements of a component based on the presence of an  attribute label.
        
        \n.. comments: 
            Input:
                CompNames       List of string of name of Component names
                                (default = [], then all comp names will be done)
                AttribName      string of attribute name of component to filter on
			Output:
				RetElement		List of elements that will be discarded.  """
        
        ToBeRemoved = []
        
        # BookKeeping
        self.Processes.append(K_Component.Processes('select_byAttribLabel: AttribName: ' + AttribName ))
        # Initialization ERROR: K_Netze.add_latLong: Adding LatLong from Component Consumers

        if CompNames == []:
            CompNames = self.CompLabels()
        elif isinstance(CompNames, str):
            CompNames = [CompNames]

        # doing all the components
        if dict_label == '':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        ToKeep.append(dat)
                    else:
                        ToBeRemoved.append(dat)
                self.__dict__[CompName] = ToKeep
        
        elif dict_label == 'param':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dat.__dict__['param'].keys():
                        ToKeep.append(dat)
                    else:
                        ToBeRemoved.append(dat)
                self.__dict__[CompName] = ToKeep


        return ToBeRemoved




    def select_byAttrib(self, CompNames = [], AttribName = '', AttribVal = [], methodStr = 'in', accuracy = 5):
        """Method of selecting of elements of a component based on an Attribute label and a given value.
        
        \n.. comments: 
            Input:
                CompNames       List of string of name of Component names
                                (default = [], then all comp names will be done)
                AttribName      string of attribute name of component to filter on
                AttribVal       value (can be of any type, e.g. int, flote, string)
                                on which to filter
                methodStr       string of selecting method:
                                'in', '!=empty', '==', 'inList', '>', '<', 
                                '!=', '!=None', 'not equ Str', '!=nan'
								(default = 'in')
				accuracy: 		In case of float values, values will be rounded to this precision 
								(default = 5)
			Output:
				RetElement		List of elements that will be discarded.  """
								
        ToBeRemoved = []
        
        # BookKeeping
        self.Processes.append(K_Component.Processes('select_byAttrib: AttribName: ' + AttribName + ', AttribVal: ' + str(AttribVal)))
        # Initialization ERROR: K_Netze.add_latLong: Adding LatLong from Component Consumers
        #ToKeep = []

        if CompNames == []:
            CompNames = self.CompLabels()
        elif isinstance(CompNames, str):
            CompNames = [CompNames]
        
    ### '=='
        if methodStr == '==':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        if isinstance(AttribVal, float):
                            if round(AttribVal, accuracy)  == round(dat.__dict__[AttribName], accuracy):
                                ToKeep.append(dat)
                            else:
                                ToBeRemoved.append(dat)
                        else:
                            if AttribVal == dat.__dict__[AttribName]:
                                ToKeep.append(dat)
                            else:
                                ToBeRemoved.append(dat)
                    else:
                        if isinstance(AttribVal, float):
                            if round(AttribVal, accuracy) == round(dat.param[AttribName], accuracy):
                                ToKeep.append(dat)
                            else:
                                ToBeRemoved.append(dat)
                        else:
                            if AttribVal == dat.param[AttribName]:
                                ToKeep.append(dat)
                            else:
                                ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep
            pass 
        
        ### 'inList'
        elif methodStr == 'inList':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        if AttribVal in dat.__dict__[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    else:
                        if AttribVal in dat.param[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep
            pass 
        
        ### '>'
        elif methodStr == '>':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        if AttribVal < dat.__dict__[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    else:
                        if AttribVal < dat.param[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep
            pass 
        
        ### '<'
        elif methodStr == '<':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        if AttribVal > dat.__dict__[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    else:
                        if AttribVal > dat.param[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep
            pass 
        
        ## '!='
        elif methodStr == '!=':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        if AttribVal != dat.__dict__[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    else:
                        if AttribVal != dat.param[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep
                
        ### '!=empty'
        elif methodStr == '!=empty':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    # not in para
                    if AttribName in dir(dat):
                        if AttribVal != dat.__dict__[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    # ub oara
                    else:
                        keep = 1
                        if AttribName not in dat.param:
                            keep = 0
                        elif '' == dat.param[AttribName]:
                            keep = 0
                        elif None == dat.param[AttribName]:
                            keep = 0
                        
                        if keep == 1:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep

        ### '!=None'
        elif methodStr == '!=None':
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    # not in para
                    if AttribName in dir(dat):
                        if dat.__dict__[AttribName] != None:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    # ub oara
                    else:
                        keep = 1
                        if AttribName in dat.param:
                            if type(dat.param[AttribName]) is not float:
                                if dat.param[AttribName] == None:
                                    keep = 0
                        
                        if keep == 1:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep

        ### '!=nan'
        elif methodStr == '!=nan':
            for CompName in CompNames:
                ToKeep = []
                for idx, dat in enumerate(self.__dict__[CompName]):
                    # not in para
                    if AttribName in dir(dat):
                        if dat.__dict__[AttribName] == None:
                            ToKeep.append(dat)
                        elif math.isnan(dat.__dict__[AttribName]) == False:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    # ub oara
                    else:
                        keep = 1
                        if type(dat.param[AttribName]) is float:
                            if math.isnan(dat.param[AttribName]):
                                keep = 0
                        
                        if keep == 1:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep

        ### 'not equ Str'
        elif methodStr == 'not equ Str':
            for CompName in CompNames:
                ToKeep = []

        else:
            for CompName in CompNames:
                ToKeep = []
                for dat in self.__dict__[CompName]:
                    if AttribName in dir(dat):
                        if AttribVal in dat.__dict__[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    else:
                        if AttribVal in dat.param[AttribName]:
                            ToKeep.append(dat)
                        else:
                            ToBeRemoved.append(dat)
                    self.__dict__[CompName] = ToKeep
            pass 

        return ToBeRemoved

		
		

    def reduce(self, AttribVal, AttribName = 'country_code'):
        '''Method of reducing data to a country specified by AttribVal=country_code 

        \n.. comments:
            Input:
				AttribVal: 		Attribute value
				AttribName: 	String of attribute name
								(default = 'country_code')''' 
        
        print('Reduce data to Country:', AttribVal)
        self.select_byAttrib( AttribName = AttribName, AttribVal = AttribVal)
        pass




    def get_ParamAttribDensity(self, CompName, AttribName = []):
        """Method of visualization (print) of number of useful data for each attribute in param for a component.

        \n.. comments:
            Input:
                CompName:       string of name of Netz Component name
                AttriName:      string of single attribute name to done
								(default = []) """
        
        # Initialization
        returnDict          = {}
        if CompName in self.__dict__.keys():
            if len(self.__dict__[CompName]) > 0:
                paramAttribs_Netz   = list(self.__dict__[CompName][0].__dict__['param'].keys())
                    
                if AttribName == []:
                    for key in paramAttribs_Netz:
                        Netz        = self.copy()
                        Netz.select_byAttrib([CompName], key, '', '!=empty')
                        returnDict.update({key:len(Netz.__dict__[CompName])})
                else:
                    Netz        = self.copy()
                    if AttribName in paramAttribs_Netz:
                        Netz.select_byAttribLabel([CompName], AttribName, dict_label = 'param')
                        Netz.select_byAttrib([CompName], AttribName, '', '!=empty')
                        Netz.select_byAttrib([CompName], AttribName, '', '!=None')
                        returnDict.update({AttribName:len(Netz.__dict__[CompName])})
                    else:
                        returnDict.update({AttribName:0})
            else:
                if AttribName != []:
                    returnDict.update({AttribName:0})
        else:
            if AttribName != []:
                returnDict.update({AttribName:0})
            
        return returnDict


    def print_ParamAttribDensity(self, CompName, AttribName = []):
        
        wert = self.get_ParamAttribDensity(CompName, AttribName = AttribName)
        N    = len(self.__dict__[CompName])
        print('Compname', CompName)
        print('% missing')
        for key, value in wert.items():
            print(key, '  ', math.floor((N - value)/N*1000)/10)
        

        
    
    def get_AttribDensity(self, CompName, AttribName = []):
        """Method of visualization (print) of number of useful data for each attribute for a component.

        \n.. comments:
            Input:
                CompName:       string of name of Netz Component name
                AttriName:      string of single attribute name to done
								(default = []) """
        
        # Initialization
        returnDict          = {}
        if CompName in self.__dict__.keys():
            if len(self.__dict__[CompName]) > 0:
                paramAttribs_Netz   = list(self.__dict__[CompName][0].__dict__['param'].keys())
                Attribs_Netz        = list(self.__dict__[CompName][0].__dict__.keys())
                    
                if AttribName == []:
                    for key in Attribs_Netz:
                        Netz        = self.copy()
                        Netz.select_byAttrib([CompName], key, None, '!=')
                        if key != 'param':
                            returnDict.update({key:len(Netz.__dict__[CompName])})
                    for key in paramAttribs_Netz:
                        Netz        = self.copy()
                        Netz.select_byAttrib([CompName], key, '', '!=empty')
                        returnDict.update({key:len(Netz.__dict__[CompName])})
                else:
                    Netz        = self.copy()
                    if AttribName in Attribs_Netz:
                        Netz.select_byAttrib([CompName], AttribName, None, '!=')
                        if AttribName != 'param':
                            returnDict.update({AttribName:len(Netz.__dict__[CompName])})
        
                    elif AttribName in paramAttribs_Netz:
                        Netz.select_byAttribLabel([CompName], AttribName, dict_label = 'param')
                        Netz.select_byAttrib([CompName], AttribName, '', '!=empty')
                        Netz.select_byAttrib([CompName], AttribName, '', '!=None')
                        returnDict.update({AttribName:len(Netz.__dict__[CompName])})
                    else:
                        returnDict.update({AttribName:0})
            else:
                if AttribName != []:
                    returnDict.update({AttribName:0})
        else:
            if AttribName != []:
                returnDict.update({AttribName:0})
            
        return returnDict
        



    def select_byPos(self, CompName, posVal):
        """Method of selecting of elements of a LKD component based list of position values

        \n.. comments:
            Input:
                CompName:        string of name of Netz Component name
                posVal:          list of int values of components to keep
            Return:
                []  """
        
        # BookKeeping
        self.Processes.append(K_Component.Processes('select_byPos: keeping ' + str(len(posVal)) + ' of components'))

        # Initialization 
        ReData = []
        
        # Selecting the data based on Component from LKD
        for ii in range(len(posVal)):
            ReData.append(self.__dict__[CompName][posVal[ii]])
        
        self.__dict__[CompName] = ReData
        
        return ReData




    def retComponents2Nodes(self, compListNames = []):
        """Method of reducing all Nodes from all Non-Nodes component or 
        user requested Components through **compListNames**.

        \n.. comments:
        Input:
            compListNames:       	List of string of component names.
        """
        
        Nodes = []
        if compListNames == []:
            compListNames = self.CompLabelsNoNodes()
            
        for key in compListNames:
            Nodes          = self.add_Nodes(key, Nodes)
        
        self.Nodes  = M_Shape.reduceElement(Nodes, reduceType = 'LatLong')

        return self.Nodes
        



    def Components2Nodes(self, compListNames = []):
        """Method of getting all Nodes from all Non-Nodes component or user 
        requested Components through **compListNames**.

        \n.. comments:
        Input:
            compListNames:       	List of string of component names.
        """
        
        self.Nodes  = self.retComponents2Nodes(compListNames = compListNames)

        
        

    def PipeSegments2PipeSegments(self, attribListNames = [], exceptNodes = []):
        """Method of merging PipeSegments, where values in attributes **attribListNames**
        need to be the same.
		
        \n.. comments:
        Input:
            attribListNames:       	String of component name to from which to remove an attribute.
									(default = []) 
			exceptNodes: 			List of nodes not be be used in merge process 
									(default = [])
        """
        
        allNodes        = []
        PipePos         = []
        PipeSegments    = copy.deepcopy(self.PipeSegments)
        
        count = 0 
        for pipe in PipeSegments:
            allNodes.append(pipe.node_id[0])
            allNodes.append(pipe.node_id[1])
            if len(pipe.node_id) != 2:
                print('ERROR: K_Netze.PipeSegments2PipeSegments: PipeSegment has unexpected number of node_id s. id"' + str(pipe.id))
            PipePos.append(count)
            PipePos.append(count)
            count = count + 1
            
        uniqueNodes     = copy.deepcopy(allNodes)
        uniqueNodes     = list(set(uniqueNodes))
        
        # Getting all nodes, where pipes shall not be merged
        node_id_notMerge    = []
        for nn in self.Compressors:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.LNGs:
            node_id_notMerge.append*(nn.node_id)
        for nn in self.Storages:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.BorderPoints:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.ConnectionPoints:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.Consumers:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.EntryPoints:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.InterConnectionPoints:
            node_id_notMerge.append(*nn.node_id)
        for nn in self.Productions:
            node_id_notMerge.append(*nn.node_id)
        
        
        # Checking for the first two PipePoints
        PassVal     = False
        count       = 0
        countError  = 0
        Node999     = []
        NodeChanged = []
        for nodeID in uniqueNodes:
            # this if statement for debugging only
            if PassVal:
                pass
            else:
                pos             = M_FindPos.find_pos_ValInVector(nodeID, allNodes, '==')
                # Do not merge on other component nodes, such as Compmressors, or entry points
                pos_NotMerge    = M_FindPos.find_pos_ValInVector(nodeID, node_id_notMerge, '==')
                
                if len(pos) == 2 and len(pos_NotMerge) == 0:
                    Join    = True

                    # node_id_0 = node ids of first pipe
                    # node_id_1 = node ids of second pipe
                    # they both need to have one, and only one same id.
                    node_id_0   = PipeSegments[PipePos[pos[0]]].node_id
                    node_id_1   = PipeSegments[PipePos[pos[1]]].node_id
                        
                    # Check that both pipes have same attributes
                    for name in attribListNames:
                        if PipeSegments[PipePos[pos[0]]].param[name] != PipeSegments[PipePos[pos[1]]].param[name]:
                            if str(PipeSegments[PipePos[pos[0]]].param[name]) != str(PipeSegments[PipePos[pos[1]]].param[name]):
                                Join    = False
                            
                    
                    # complement of node ids
                    node_id_3   = set(set(node_id_0) ^set(node_id_1))
                    if len(node_id_3) != 2:
                        Join    = False
                        
                    # id not allosed to be -9999, however this should not have happened in the first place
                    if PipeSegments[PipePos[pos[0]]].id == -9999:
                        Join    = False
                        print('K_Netze.: Pipe with id -9999 selected: has node_ids of : ' + str(node_id_0[0]) + ', ' + str(node_id_0[1]))
                        
                    # checking if there are node to be merged/removed
                    if PipeSegments[PipePos[pos[0]]].node_id[0] in exceptNodes or PipeSegments[PipePos[pos[0]]].node_id[-1] in exceptNodes or PipeSegments[PipePos[pos[1]]].node_id[0] in exceptNodes or PipeSegments[PipePos[pos[1]]].node_id[-1] in exceptNodes:
                        Join = False
                    
                    if Join:
                        if PipePos[pos[0]] == 0 or PipePos[pos[1]] == 0:
                            PipePos[pos[0]] = PipePos[pos[0]]

                        # adding lat/long to node that is being kept
                        if PipeSegments[PipePos[pos[0]]].lat != None and PipeSegments[PipePos[pos[1]]].lat != None:
                            # checking for wrong data
                            if PipeSegments[PipePos[pos[0]]].id == '-9999':
                                countError = countError + 1
                                Node999.append(PipeSegments[PipePos[pos[0]]].source_id)
                            if PipeSegments[PipePos[pos[1]]].id == '-9999':
                                countError = countError + 1
                                Node999.append(PipeSegments[PipePos[pos[1]]].source_id)
                                
                            # glue 1 behind 0
                            if node_id_0[1] == node_id_1[0]:
                                #Lat Long
                                latVal     = []
                                longVal    = []
                                for lat in PipeSegments[PipePos[pos[0]]].lat:
                                    latVal.append(lat)
                                for lat in PipeSegments[PipePos[pos[1]]].lat:
                                    latVal.append(lat)
                                PipeSegments[PipePos[pos[0]]].lat     = copy.deepcopy(latVal)                                    
                                for long in PipeSegments[PipePos[pos[0]]].long:
                                    longVal.append(long)
                                for long in PipeSegments[PipePos[pos[1]]].long:
                                    longVal.append(long)
                                PipeSegments[PipePos[pos[0]]].long    = copy.deepcopy(longVal)
    
                                # Creation of new node_id
                                PipeSegments[PipePos[pos[0]]].node_id = [node_id_0[0], node_id_1[1]] 
                                # changing access
                                NodeChanged.append(PipeSegments[PipePos[pos[1]]].source_id)
                                PipeSegments[PipePos[pos[1]]].id      = '-9999'
                                # Copy country code accross
                                PipeSegments[PipePos[pos[0]]].country_code[-1] = copy.deepcopy(PipeSegments[PipePos[pos[1]]].country_code[-1])
                                p_pos = M_FindPos.find_pos_ValInVector(PipePos[pos[1]], PipePos, '==')
                                for ppos in p_pos:
                                    PipePos[ppos] = copy.deepcopy(PipePos[pos[0]])

                                
                            # glue reverse 1 behind 0
                            elif node_id_0[1] == node_id_1[1]:
                                #Lat Long
                                latVal     = []
                                longVal    = []
                                for lat in PipeSegments[PipePos[pos[0]]].lat:
                                    latVal.append(lat)
                                for lat in list(reversed(PipeSegments[PipePos[pos[1]]].lat)):
                                    latVal.append(lat)
                                    
                                for long in PipeSegments[PipePos[pos[0]]].long:
                                    longVal.append(long)
                                for long in list(reversed(PipeSegments[PipePos[pos[1]]].long)):
                                    longVal.append(long)
                                # creating new Node_id and LatLong
                                PipeSegments[PipePos[pos[0]]].long    = copy.deepcopy(longVal)
                                PipeSegments[PipePos[pos[0]]].lat     = copy.deepcopy(latVal)
                                PipeSegments[PipePos[pos[0]]].node_id = [node_id_0[0], node_id_1[0]] 
                                # changing access
                                PipeSegments[PipePos[pos[1]]].id      = '-9999'
                                # Copy country code accross
                                PipeSegments[PipePos[pos[0]]].country_code[-1] = PipeSegments[PipePos[pos[1]]].country_code[0]
                                p_pos = M_FindPos.find_pos_ValInVector(PipePos[pos[1]], PipePos, '==')
                                for ppos in p_pos:
                                    PipePos[ppos] = copy.deepcopy(PipePos[pos[0]])
                                    
                                
                            # glue reverse 1 infront of 0
                            elif node_id_0[0] == node_id_1[0]:
                                #Lat Long
                                latVal     = []
                                longVal    = []
                                for lat in list(reversed(PipeSegments[PipePos[pos[1]]].lat)):
                                    latVal.append(lat)
                                for lat in PipeSegments[PipePos[pos[0]]].lat:
                                    latVal.append(lat)
                                    
                                for long in list(reversed(PipeSegments[PipePos[pos[1]]].long)):
                                    longVal.append(long)
                                for long in PipeSegments[PipePos[pos[0]]].long:
                                    longVal.append(long)
                                # creating new Node_id and LatLong
                                PipeSegments[PipePos[pos[0]]].long    = copy.deepcopy(longVal)
                                PipeSegments[PipePos[pos[0]]].lat     = copy.deepcopy(latVal)
                                PipeSegments[PipePos[pos[0]]].node_id = [node_id_1[1], node_id_0[1]] 
                                # changing access
                                PipeSegments[PipePos[pos[1]]].id      = '-9999'
                                # Copy country code accross
                                PipeSegments[PipePos[pos[0]]].country_code[0] = PipeSegments[PipePos[pos[1]]].country_code[-1]
                                p_pos = M_FindPos.find_pos_ValInVector(PipePos[pos[1]], PipePos, '==')
                                for ppos in p_pos:
                                    PipePos[ppos] = copy.deepcopy(PipePos[pos[0]])

                                
                            # glue 1 infront of 0
                            elif node_id_0[0] == node_id_1[1]:
                                #Lat Long
                                latVal     = []
                                longVal    = []
                                for lat in PipeSegments[PipePos[pos[1]]].lat:
                                    latVal.append(lat)
                                for lat in PipeSegments[PipePos[pos[0]]].lat:
                                    latVal.append(lat)
                                    
                                for long in PipeSegments[PipePos[pos[1]]].long:
                                    longVal.append(long)
                                for long in PipeSegments[PipePos[pos[0]]].long:
                                    longVal.append(long)
                                # changing Node_id and LatLong
                                PipeSegments[PipePos[pos[0]]].long    = copy.deepcopy(longVal)
                                PipeSegments[PipePos[pos[0]]].lat     = copy.deepcopy(latVal)
                                PipeSegments[PipePos[pos[0]]].node_id = [node_id_1[0], node_id_0[1]] 
                                # changing access
                                PipeSegments[PipePos[pos[1]]].id      = '-9999'
                                # Copy country code accross
                                PipeSegments[PipePos[pos[0]]].country_code[0] = PipeSegments[PipePos[pos[1]]].country_code[0]
                                p_pos = M_FindPos.find_pos_ValInVector(PipePos[pos[1]], PipePos, '==')
                                for ppos in p_pos:
                                    PipePos[ppos] = copy.deepcopy(PipePos[pos[0]])

        # now removing all those pipeSegments, taht are not needed any more, the ones with and id == -9999
        self.PipeSegments = PipeSegments 
        self.select_byAttrib(['PipeSegments'], 'id', '-9999', '!=')


    

    def PipeLines2PipeSegments(self):
        """Method of converting PipeLines to PipeSegments.
        """
        
        RetPipeSegments = []
            
        # Checking for the first two PipePoints
        for pipe in self.PipeLines:
            if len(pipe.node_id) == 2:
                RetPipeSegments.append(K_Component.PipeSegments(id = pipe.id, 
                                name        = pipe.name, 
                                source_id   = pipe.source_id, 
                                node_id     = pipe.node_id,  
                                lat         = pipe.lat, 
                                long        = pipe.long,
                                country_code = pipe.country_code, 
                                param       = pipe.param.copy()))
            else:
                for ii in range(len(pipe.node_id) - 1):
                    if pipe.lat == None:
                        RetPipeSegments.append(K_Component.PipeSegments(id = pipe.id+str(ii), 
                                name        = pipe.name+str(ii), 
                                source_id   = pipe.source_id, 
                                lat         = None, 
                                long        = None, 
                                node_id     = pipe.node_id[ii : ii+2], 
                                country_code = pipe.country_code, 
                                param       = pipe.param.copy()))
                    else:
                        print('ERROR: K_Netze.PipeLines2PipeSegments: code not written yet, as lat long missing.')
                        RetPipeSegments.append(K_Component.PipeSegments(id = pipe.id+str(ii), 
                                name        = pipe.name+str(ii), 
                                source_id   = pipe.source_id,  
                                node_id     = pipe.node_id[ii : ii+2],  
                                country_code = pipe.country_code, 
                                param       = pipe.param.copy()))
                        
                    
        self.PipeSegments = RetPipeSegments 
        #return []
    

    

    def PipeSegments2PipePoints(self):
        """ Method of converting PipeSegments to PipePoints
        """
        
        RetPipePunkte = []
        count = 0
        # Checking for the first two PipePoints
        for pipe in self.PipeSegments:
            RetPipePunkte.append(K_Component.PipePoints(id = pipe.id, 
                          name      = pipe.name, 
                          source_id = pipe.source_id, 
                          node_id   = [pipe.node_id[0]], 
                          country_code = pipe.country_code, 
                          lat       = None, 
                          long      = None))
            RetPipePunkte.append(K_Component.PipePoints(id = pipe.id, 
                          name      = pipe.name, 
                          source_id = pipe.source_id, 
                          node_id   = [pipe.node_id[1]],  
                          country_code = pipe.country_code, 
                          lat = None, 
                          long = None))
            count = count + 1
        self.PipePoints = RetPipePunkte




    def replace_attrib(self, compNames = [], attribNames = [], attribValIn = [], attribValOut = ''):
        """Replaces Attribute values, where **compNames** is a list of components to do, 
        **attribNames** a list of attributes to do, **attribValIn** being the attribute value
        to be replace, **attribValOut** the attribute value to be replaced with.
        
        Input
            compNames       List of strings of component names
                            (default = all comp names will be used)
            attribNames     List of strings of attribute names
                            (default = all attrib names will be used)
            attribValIn     string/float/None 
            attribValOut    string/float/None
        Output
        """
        # Getting comp names to do
        if compNames == []:
            compNames = self.CompLabels()
            
        # Loop for each compname
        for compName in compNames:
            if compName == 'InterConnectionPoints':
                compName = 'InterConnectionPoints'
                
            # Get Attribute names to do
            if attribNames == []:
                thisAttribNames = []
                if len(self.__dict__[compName]) > 0:
                    for key in self.__dict__[compName][0].param.keys():
                        thisAttribNames.append(key)
            else:
                thisAttribNames = attribNames
                        
            # Loop for each attribute
            for attribName in thisAttribNames:
                
                # Loop for each element of the component
                for elem in self.__dict__[compName]:
                    if elem.param[attribName] == attribValIn:
                        elem.param[attribName] = attribValOut
                    

    

    def MoveUnits(self, compName, attrib_from = '', attrib_to = '', replace = False):
        """ Method of converting units of attributes, including attribute name.

        \n.. comments:
        Input:
            CompName:       String of component name to from which to remove an attribute.
            attrib_from:    String of attributes of where value can be found.
			attrib_to: 		String of attribute, to which to be converted.
			replace: 		???
							(default = False)
        """
        
        if attrib_from == 'storage_LNG_Mt' and attrib_to == 'max_workingGas_M_m3':
            multVal     = 2.47 * 584
            
        elif attrib_from == 'max_workingLNG_M_m3'and attrib_to == 'max_workingGas_M_m3':
            multVal     = 584

        elif 'TWh_per_d' in attrib_from and 'M_m3_per_d' in attrib_to:
            multVal     = 94.277364
        elif 'GWh_per_d' in attrib_from and 'M_m3_per_d' in attrib_to:
            multVal     = 0.094277364
        elif 'MWh_per_d' in attrib_from and 'M_m3_per_d' in attrib_to:
            multVal     = 0.094277364/1000
        elif 'kWh_per_d' in attrib_from and 'M_m3_per_d' in attrib_to:
            multVal     = 0.094277364/1000000
            
        elif 'M_m3_per_h' in attrib_from   and  'M_m3_per_d' in attrib_to:
            multVal     = 24
        elif 'M_m3_per_a' in attrib_from and 'M_m3_per_d' in attrib_to:
            multVal     = 1.0 / 365
        elif 'TWh' in attrib_from and 'M_m3' in attrib_to:
            multVal     = 94.277364
            
            
            
        else:
            wert_to     = None
            print('K_Netze: MoveUnits: Conversion not coded')
            print('attrib_from: ' +  attrib_from)
            print('attrib_to: ' + attrib_to)
            return []



        for ii in range(len(self.__dict__[compName])):
            comp    = self.__dict__[compName][ii]
            
            # Not in Param
            if attrib_from in comp.__dict__.keys():
                wert_from   = comp.__dict__[attrib_from]
                if wert_from != None:
                    wert_to     = wert_from * multVal
                        
                    if attrib_to in list(comp.__dict__.keys()):
                        if replace:
                            self.__dict__[compName][ii].__dict__[attrib_to] = wert_to
                        elif self.__dict__[compName][ii].__dict__[attrib_to] == None:
                            self.__dict__[compName][ii].__dict__[attrib_to] = wert_to
                    else:
                        self.__dict__[compName][ii].__dict__['param'][attrib_to] = wert_to
                else:
                    self.__dict__[compName][ii].__dict__[attrib_to] = None
                    # removing old attribute
                
            # In Param 
            elif attrib_from in comp.__dict__['param'].keys():
                wert_from   = comp.__dict__['param'][attrib_from]
                if wert_from != None:
                    wert_to     = wert_from * multVal
                    
                    if attrib_to in comp.__dict__['param'].keys():
                        if replace:
                            self.__dict__[compName][ii].__dict__['param'][attrib_to] = wert_to
                        elif self.__dict__[compName][ii].__dict__['param'][attrib_to] == None:
                            self.__dict__[compName][ii].__dict__['param'][attrib_to] = wert_to
    
                    else:
                        self.__dict__[compName][ii].__dict__['param'][attrib_to] = wert_to
                else:
                    self.__dict__[compName][ii].__dict__['param'][attrib_to] = None
            # not present
            else:
                print('K_Netze: MoveUnits: from attribute not present')
                
                
    def Str2Val(self, CompName = '', AttribName = '', inDicts = True):
        """ Method to converting String value in  **AttribName** to number value for component **CompName**
    
        \n.. comments:
        Input:
            CompName:       String of component name to chagne attribute.
            AttribName:     List of strings of attributes to be chagned.
            inDicts:        Boolean, indicating that attrib in dicts (param, method, uncertainty) or not
                            (default = True)
        """
        if inDicts:
            for attrib in AttribName:
                for ii in range(len(self.__dict__[CompName])):
                    if attrib in self.__dict__[CompName][ii].param.keys():
                        if len(self.__dict__[CompName][ii].param[attrib]) == 1:
                            if self.__dict__[CompName][ii].param[attrib] == '1':
                                self.__dict__[CompName][ii].param[attrib] = 1.0
                            elif self.__dict__[CompName][ii].param[attrib] == '0':
                                self.__dict__[CompName][ii].param[attrib] = 0.0
                            elif self.__dict__[CompName][ii].param[attrib] == None:
                                self.__dict__[CompName][ii].param[attrib] = None
                            elif type(self.__dict__[CompName][ii].param[attrib]) ==  list:
                                Werte = self.__dict__[CompName][ii].param[attrib]
                                for idx in range(len(Werte)):
                                    if len(Werte[idx]) == 1:
                                        if Werte[idx] == '1':
                                            Werte[idx] = 1.0
                                        elif Werte[idx] == 0:
                                            Werte[idx] = 0.0
                                        elif Werte[idx] == None:
                                            Werte[idx] = None
                                        else:
                                            Werte[idx] = float(Werte[idx])
                                self.__dict__[CompName][ii].param[attrib] = Werte 
                            else: 
                                self.__dict__[CompName][ii].param[attrib] = float(self.__dict__[CompName][ii].param[attrib])
                        elif self.__dict__[CompName][ii].param[attrib] == None:
                            self.__dict__[CompName][ii].param[attrib] = None
                        elif len(self.__dict__[CompName][ii].param[attrib]) == 0:
                            self.__dict__[CompName][ii].param[attrib] = None
                        else: 
                            self.__dict__[CompName][ii].param[attrib] = float(self.__dict__[CompName][ii].param[attrib])
                            
        else:
            for attrib in AttribName:
                for ii in range(len(self.__dict__[CompName])):
                    if attrib in self.__dict__[CompName][ii].__dict__.keys():
                        if len(self.__dict__[CompName][ii][attrib]) == 1:
                            if self.__dict__[CompName][ii][attrib] == '1':
                                self.__dict__[CompName][ii][attrib] = 1.0
                            elif self.__dict__[CompName][ii][attrib] == '0':
                                self.__dict__[CompName][ii][attrib] = 0.0
                            elif self.__dict__[CompName][ii][attrib] == None:
                                self.__dict__[CompName][ii][attrib] = None
                            elif type(self.__dict__[CompName][ii][attrib]) == list:
                                Werte = self.__dict__[CompName][ii][attrib]
                                for idx in range(len(Werte)):
                                    if len(Werte[idx]) == 1:
                                        if Werte[idx] == '1':
                                            Werte[idx] = 1.0
                                        elif Werte[idx] == 0:
                                            Werte[idx] = 0.0
                                        elif Werte[idx] == None:
                                            Werte[idx] = None
                                        else:
                                            Werte[idx] = float(Werte[idx])
                                self.__dict__[CompName][ii][attrib] = Werte 
                            else:
                                self.__dict__[CompName][ii][attrib] = float(self.__dict__[CompName][ii][attrib])
                        elif self.__dict__[CompName][ii][attrib] == None:
                            self.__dict__[CompName][ii][attrib] = None
                        elif len(self.__dict__[CompName][ii][attrib]) == 0:
                            self.__dict__[CompName][ii][attrib] = None
                        else:
                            self.__dict__[CompName][ii][attrib] = float(self.__dict__[CompName][ii][attrib])
        
        
        
        
    def replaceAttribVal(self, CompName  = [], AttribName  = [], AttribValIn = [], AttribValOut = []):
        """Swapping Key values given through **CompName**, **AttribName**, **AttribValIn**, **AttribValOut**
        """
        
        if len(CompName) == 0 or  len(AttribName) == 0 or len(AttribValIn) == 0 or len(AttribValOut) == 0:
            return
        else:
            for ii in range(len(self.__dict__[CompName])):
                if self.__dict__[CompName][ii].param[AttribName] == AttribValIn:
                    self.__dict__[CompName][ii].param[AttribName]  = AttribValOut
            
        

    def removeAttrib(self, CompName = '', AttribName = '', inDicts = True):
        """ Method to remove **AttribName** from component **CompName**
    
        \n.. comments:
        Input:
            CompName:       String of component name to from which to remove an attribute.
            AttribName:     List of strings of attributes to be removed.
            inDicts:        Boolean, indicating that attrib in dicts (param, method, uncertainty) or not
                            (default = True)
        """
        
        if inDicts:
            for attrib in AttribName:
                for ii in range(len(self.__dict__[CompName])):
                    if attrib in self.__dict__[CompName][ii].param.keys():
                        del self.__dict__[CompName][ii].param[attrib]
                    if attrib in self.__dict__[CompName][ii].method.keys():
                        del self.__dict__[CompName][ii].method[attrib]
                    if attrib in self.__dict__[CompName][ii].uncertainty.keys():
                        del self.__dict__[CompName][ii].uncertainty[attrib]
        else:
            for attrib in AttribName:
                for ii in range(len(self.__dict__[CompName])):
                    if attrib in self.__dict__[CompName][ii].__dict__.keys():
                        del self.__dict__[CompName][ii][attrib]
                

        
        
    def moveAttriVal(self, sourceNetz = [], sourceCompName = 'Nodes', destinCompName = 'PipeSegments', sourceFindAttribName = 'id', destinFindAttribName = 'node_id', sourceAttribName = 'country_code', destinAttribName = 'country_code'):
        """ Method copy attribute values from one comp to another comp, where elements are linked by equal attribute values
    
        \n.. comments:
        Input:
            sourceNetz              Netz, if = [], then self will be used as source
            sourceCompName          string, of component name of data source
            destinCompName          string, of component name of data destination
            sourceFindAttribName    string, of attribute from source, that is used to linke with destination
            destinFindAttribName    string, of attribute from destination, that is used to linek with source
            sourceAttribName        string, of attribute, where value from source will be used
            destinAttribName        string, of attribute of destination where value will be written to.
        Return:
            []
        """
        
        if sourceNetz == []:
            sourceNetz = self
            
        sourceFind = sourceNetz.get_Attrib(sourceCompName, sourceFindAttribName)
        
        for elem in self.__dict__[destinCompName]:
            if isinstance(elem.__dict__[destinFindAttribName], list):
                for ii, ele in enumerate(elem.__dict__[destinFindAttribName]):
                    pos = M_FindPos.find_pos_StringInList(ele, sourceFind)
                    if len(pos) == 1:
                        elem.__dict__[destinAttribName][ii] = sourceNetz.__dict__[sourceCompName][pos[0]].__dict__[sourceAttribName]
            else:
                pos = M_FindPos.find_pos_StringInList(elem.__dict__[destinFindAttribName], sourceFind)
                if len(pos) == 1:
                    elem.__dict__[destinAttribName] = sourceNetz.__dict__[sourceCompName][pos[0]].__dict__[sourceAttribName]
                    
        


    def add_latLong(self, CompNames = ''):
        """ Method to add LatLong to  component **CompName**, where LatLong info is taken from Nodes component.
    
        \n.. comments:
        Input:
            CompNames: 	List of strings of component name to "copy" lat long values from Nodes to component
						If CompNames = empty, then will be carried out for all Components.
						(default = '', which will do all components)
        Return:
            []
        """
        nodeIDs = M_Helfer.get_attribFromComp(self, 'Nodes', 'id', makeLower = True)
        
        if len(CompNames) == 0:
            CompNames = self.CompLabels()
            
        for compName in CompNames:
            if 'Nodes' == compName:
                pass
            elif 'PipeLines' in compName:
                for ii in range(len(self.PipeLines)):
                    lat         = []
                    long        = []
                    country_code= []
                    thisComp    = self.PipeLines[ii]
                    node_id    = thisComp.node_id
                    
                    for nn in node_id:
                        pos        = M_FindPos.find_pos_StringInList(nn, nodeIDs, Str2Lower = True)
                        if len(pos) == 0:
                            print('ERROR: K_Netze.add_latLong: Adding LatLong to pipeline: location ' + nn + ' does not exist in Nodes table')
                            print('PRogram will terminate.')
                            return
                        lat.append(self.Nodes[pos[0]].lat)
                        long.append(self.Nodes[pos[0]].long)
                        country_code.append(self.Nodes[pos[0]].country_code)
                        
                    # Adding to PipeLines
                    self.PipeLines[ii].lat          = lat
                    self.PipeLines[ii].long         = long
                    self.PipeLines[ii].country_code = country_code
                    self.PipeLines[ii].param['length']    = 0 
                    for jj in range(len(lat) - 1):
                        self.PipeLines[ii].param['length']   = self.PipeLines[ii].param['length'] + M_DataAnalysis.distance(long[jj], lat[jj], long[jj + 1], lat[jj + 1])
                    
            elif 'PipeSegments' in compName:
                for ii in range(len(self.PipeSegments)):
                    lat         = []
                    long        = []
                    country_code= []
                    thisComp    = self.PipeSegments[ii]
                    node_id    = thisComp.node_id
                    if len(node_id) >0:
                        for nn in node_id:
                            pos        = M_FindPos.find_pos_StringInList(nn, nodeIDs, Str2Lower = True)
                            if len(pos) == 0:
                                print('ERROR: K_Netze.add_latLong: Adding LatLong to pipeline: location ' + nn + ' does not exist in Nodes table')
                                print('PRogram will terminate.')
                                return
                            lat.append(self.Nodes[pos[0]].lat)
                            long.append(self.Nodes[pos[0]].long)
                            country_code.append(self.Nodes[pos[0]].country_code)
                            
                        
                        #Der Teil geht so nicht: Wieso die Pipelinecoordinaten hier gehts um Pipesegments

#                        # Adding to PipeLines
                        self.PipeSegments[ii].lat           = lat
                        self.PipeSegments[ii].long          = long
                        self.PipeSegments[ii].country_code  = country_code
                        
                        self.PipeSegments[ii].param['length']= M_DataAnalysis.distance(long[0], lat[0], long[1], lat[1])                       
#                       sorry aber das km gehoert da nun wirklich nicht rein
                    else:
                        print('missing node_id: ' + str(ii))
                        thisComp.all()
          
            elif 'PipePoints' in compName:
                 for ii in range(len(self.PipePoints)):
                    thisComp    = self.PipePoints[ii]
                    pos         = M_FindPos.find_pos_StringInList(thisComp.node_id, nodeIDs, Str2Lower = True)
                    if len(pos) == 0:
                        print('ERROR: K_Netze.add_latLong: Adding LatLong to PipePoints: location ' + str(thisComp.node_id) + ' does not exist in Nodes table')
                        print('PRogram will terminate.')
                        return
                    self.PipePoints[ii].lat      = self.Nodes[pos[0]].lat
                    self.PipePoints[ii].long     = self.Nodes[pos[0]].long
                    self.PipePoints[ii].country_code     = self.Nodes[pos[0]].country_code
                    
            else:
                #print(compName)
                for ii in range(len(self.__dict__[compName])):
                    thisComp    = self.__dict__[compName][ii]
                    id          = thisComp.node_id
                    if isinstance(id, list):
                        pos         = M_FindPos.find_pos_StringInList(id[0], nodeIDs, Str2Lower = True)
                    else:
                        pos         = M_FindPos.find_pos_StringInList(id, nodeIDs, Str2Lower = True)
                    if len(pos) == 0:
                        if isinstance(id, list):
                            print('ERROR: K_Netze.add_latLong: Adding LatLong from Component ' + compName + ' : location ' + id[0] + ' does not exist in Nodes table')
                        else:
                            print('ERROR: K_Netze.add_latLong: Adding LatLong from Component ' + compName + ' : location ' + id + ' does not exist in Nodes table')

                    self.__dict__[compName][ii].lat  = self.Nodes[pos[0]].lat
                    self.__dict__[compName][ii].long = self.Nodes[pos[0]].long
                    self.__dict__[compName][ii].country_code = self.Nodes[pos[0]].country_code





    def fill_attrib(self, compName, attribName, methodName = 'math_mean_int'):
        """Filling attribute values for each element of a component for a single attribute.
		
        \n.. comments:
        Input:
			compName 		String of component name
			attribName 		String of attribute name
			methodName  	String of method name
							'math_mean_int'
							'math_mean_float'
							'math_median_int'
							'math_median_float'
							(default = 'math_mean_int')
        """
        values      = self.get_Attrib(compName, attribName)

        # determin fill value        
        if methodName == 'math_mean_int':
            [fillVal, uncertVal] 	= M_MatLab.get_mean(values)
            fillVal              	= int(round(fillVal))
        elif methodName == 'math_mean_float':
            [fillVal, uncertVal] 	= M_MatLab.get_mean(values)
        elif methodName == 'math_median_int':
            [fillVal, uncertVal] 	= M_MatLab.get_median(values)
            fillVal            		= int(round(fillVal))
        elif methodName == 'math_median_float':
            [fillVal, uncertVal] 	= M_MatLab.get_median(values)
        else:
            print('ERROR: K_Netze.fill_attrib: Method option not written yet.')
            
            
        # filling missing values
        for ii in range(len(self.__dict__[compName])):
            if attribName in list(self.__dict__[compName][ii].__dict__['param'].keys()):
                if self.__dict__[compName][ii].param[attribName] == None:
                    self.__dict__[compName][ii].__dict__['param'][attribName]   = fillVal
                    self.__dict__[compName][ii].__dict__['uncer'][attribName]   = uncertVal
                    self.__dict__[compName][ii].__dict__['method'][attribName]  = methodName
                else:
                    self.__dict__[compName][ii].__dict__['uncer'][attribName]   = 0
                    self.__dict__[compName][ii].__dict__['method'][attribName]  = 'raw'
            else:
                if self.__dict__[compName][ii].__dict__[attribName] == None:
                    self.__dict__[compName][ii].__dict__[attribName] = fillVal
                    self.__dict__[compName][ii].__dict__['uncer'][attribName]   = uncertVal
                    self.__dict__[compName][ii].__dict__['method'][attribName]  = methodName
                else:
                    self.__dict__[compName][ii].__dict__['uncer'][attribName]   = 0
                    self.__dict__[compName][ii].__dict__['method'][attribName]  = 'raw'
            
            
            
            
            
    def get_Attrib(self, compName, attribName):
        """Method to get attribute values from a all elements from a component.
        **compName** and **attribName** are the inputs, and a list of values will
        be returned.
        
        \n.. comments:
        Input:
            compName:           string of component name/label
            attribName:         string of attribute name/label
        Return:
            attribList:         list of values 
        """
        attribList = []
        
        for comp in self.__dict__[compName]:
            
            if attribName in comp.__dict__['param'].keys():
                if isinstance(comp.param[attribName], list):
                    for tt in comp.param[attribName]:
                        attribList.append(tt)
                else:
                    attribList.append(comp.param[attribName])
            elif attribName in comp.__dict__.keys():
                if isinstance(comp.__dict__[attribName], list):
                    for tt in comp.__dict__[attribName]:
                        attribList.append(tt)
                else:
                    attribList.append(comp.__dict__[attribName])
            else:
                return []
    
        return attribList
    
    
    

    def join_comp(self, Netz_In, compName, pos_match_self = [], pos_unmatch_self = [], pos_match_Netz = [], pos_add_Netz = []):
        """ Method of adding additional component elements from another network (**Netz_In**).  
        Component in question given through through **compName** (name of component).  
        Method also needs list of positions of component elements for both networks: 
        **pos_match_self**, **pos_match_Netz**, **pos_add_Netz**, and 
        **pos_unmatch_self**, which are all outputs from function M_Matching.match.
        Special care has been taken to assure, that the attributes, that are 
        in one data set but not the other will appear in final data set. In 
        output data set, all components have all the same attributes, no matter 
        from which data set they originated.  If values not given to attribute, then
        will be populated with None.  
    
        \n.. comments:
        Input:
            Netz:               Instance of other Netz class
            compName:           string of component name to add
            pos_match_self    	ordered list of positions, in respect of Netz_0 (self), that have been linked with positions from Netz_In
								(default = [])
            pos_unmatch_self    list of positions of Netz_0 (self), for which a corresponding element was not found in Netz_In
								(default = [])
            pos_match_Netz    	ordered list of positions, in respect of Netz_In, that have been linked with positions from Netz_0 (self)
								(default = [])
            pos_add_Netz      	list of positions of Netz_In, that need to be added to Netz_0 (self)
								(default = [])
        Return:
            []
        """
        
        # Initialization
        Netz_1                  = copy.deepcopy(Netz_In)
        simpleMove              = False
        doNothing               = False
        num_comp_Netz           = len(Netz_1.__dict__[compName])
        paramAttribs_Netz       = []
        paramAttribs_self       = []
        
        # Check if there are existing components, and what are their attributes
        if len(self.__dict__[compName]) > 0:
            paramAttribs_self   = list(self.__dict__[compName][0].__dict__['param'].keys())
        else:
            simpleMove          = True
        
        # check if something is needed to be copied, and what are their attributes
        if len(Netz_1.__dict__[compName]) > 0:
            paramAttribs_Netz   = list(Netz_1.__dict__[compName][0].__dict__['param'].keys())
        else:
            doNothing           = True
            
        # determine all keys
        attribNames_sum         = list(set(list(paramAttribs_Netz + paramAttribs_self)))
        attribNames_Netz_only   = [item for item in paramAttribs_Netz if item not in paramAttribs_self] 
        attribNames_self_only   = [item for item in paramAttribs_self if item not in paramAttribs_Netz] 
        
        # loop for all possible new Netz components
        if doNothing:
            return []
        
        elif simpleMove:
            for ii in range(num_comp_Netz):
                self.__dict__[compName].append(Netz_1.__dict__[compName][ii])
        
        else:

            # for pos_unmatch_self, they are in self, but not in Netz, 
            # hence only attribds that are in Netz but not in self need to be added
            # with NaN to componentsadd other attribs from Netz
            for key in attribNames_Netz_only:
                for ii in pos_unmatch_self:
                    self.__dict__[compName][ii].param[key] = None


            # both data sets have component for same location
            # needs to copy from Netz to self
            for ii in range(len(pos_match_self)):
                selfComp = self.__dict__[compName][pos_match_self[ii]]
                netzComp = Netz_1.__dict__[compName][pos_match_Netz[ii]]
                
                # doing main attributes
                selfComp.source_id = [selfComp.source_id[0], netzComp.source_id[0]]
                
                # doing the param attributes
                for key in attribNames_sum:
                    # attrib in both data sets, hence if no value in self, 
                    # then copy value from Netz
                    if key in paramAttribs_self and key in paramAttribs_Netz:
                        # if None or nan in self, then use value from Netz
                        if str(selfComp.param[key]) in 'nan':
                            if key in netzComp.param:
                                selfComp.param[key] = netzComp.param[key]
                        elif selfComp.param[key] == None:
                            if key in netzComp.param:
                                selfComp.param[key] = netzComp.param[key]
                        
                    # attribute only in Netz, hence needs adding to self
                    elif key in paramAttribs_Netz:
                        selfComp.param[key] = netzComp.param[key]
                        
                # now write back to self.
                self.__dict__[compName][pos_match_self[ii]] = selfComp
                
            # Adding components from Netz into self
            for ii in pos_add_Netz:
                # Adding component from Netz
                selfComp = Netz_1.__dict__[compName][ii]
                
                # creating attributes that are in new self but not in Netz
                for key in attribNames_self_only:
                    selfComp.param[key] = None
                    
                # now adding component to self
                self.__dict__[compName].append(selfComp)
      
        
        return []

		
		
class NetComp_OSM(NetComp):
    """
    same as NetComp but more elements, [outdated]
    """
    def __init__(self):
        self.SourceName             = ['']
        self.BorderPoints           = []    # BP
        self.Compressors            = []    # CO
        self.Compressors_Lines      = []    # CO
        self.ConnectionPoints       = []    # CP
        self.Consumers              = []    # CS
        self.EntryPoints            = []    # EP
        self.InterConnectionPoints  = []    # IC
        self.LNGs                   = []    # LG
        self.Nodes                  = []    # NO
        self.PipePoints             = []    # PP
        self.PipeSegments           = []    # PS
        self.PipeLines              = []    # PL
        self.Markers                = []
        self.SeaMarkers             = []
        self.Productions            = []    # PD
        self.Storages               = []    # SR
        self.Processes              = []

    pass





