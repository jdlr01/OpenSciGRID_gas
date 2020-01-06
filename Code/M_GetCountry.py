#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M_GetCountry
------------

Returns country codes from GeoCoordinates
"""

import shapefile 
import sys
from pathlib  import Path
from shapely.geometry import Point, Polygon
import multiprocessing as mp

#Context Manager for time measurement
import time
import os
import contextlib


#Example for Use:
#    countrypolydict=CountryPolyDict()
#    for i,pipeline in enumerate(OSM.PipeLines):
#        countrys=CountryCheckfromList(pipeline.long,pipeline.lat,countrypolydict)
#        print(i,countrys)


@contextlib.contextmanager
def benchmark(name):
    start = time.time()
    yield
    print('{} {:.2f}s'.format(name, time.time() - start))




def CountryPolyDict(predicted_countrycode=''):
    '''Creates and Returns Dictionary {countrycode:list_of_polygons_for_that_country}
    Uses Shapefile
    Only Countries in the list country tested'''
    
    countrypolydict={}
    if sys.platform == 'win32':
        RelDirName      = 'Eingabe/GraphischeDaten/'
        dataFolder      = Path.cwd()
        filename        = dataFolder /  RelDirName
        FileName_Map    = str(filename / 'TM_WORLD_BORDERS-0.3.shp')
    else:
        FileName_Map     = os.path.join(os.getcwd(),'Eingabe/GraphischeDaten/TM_WORLD_BORDERS-0.3.shp')

    sf = shapefile.Reader(FileName_Map, encoding="latin1")
    polygon=sf.shapes()
    countrylist=['DE','ES','FR','GB','IT','NL','UA','TR','RU','AL','AM','AT','AZ','BY','BE','BA','BG','HR','CY','CZ','DK','EE','FI','GE','GR','EL','HU','IS','IE','XK','LV','LI','LT','LU','MT','MD','ME','NO','PL','PT','RO','RS','SK','SA','SI','SE','CH']
    
    #speed up the routine if countrycode is correctly predicted
    countrys=[]
    if predicted_countrycode!='':
        if predicted_countrycode in countrylist:
            countrys.append(predicted_countrycode)
            countrylist.remove(predicted_countrycode)
        countrys.extend(countrylist)
    else:
        countrys=countrylist
        
    
    for i,poly in enumerate(polygon):
            if sf.record(i)[1] in countrys:
                geoshapelist=[]
                for shape in poly.__geo_interface__['coordinates']:
                    if isinstance(shape, list):
                        geoshape=Polygon(shape[0])
                    else:
                        geoshape=Polygon(shape)
                    geoshapelist.append(geoshape)
                countrypolydict.update({sf.record(i)[1]:geoshapelist})
    return countrypolydict 




def GetCountry(long,lat,countrypolydict='',predicted_countrycode=''):
    '''Get and return countrycode of the point(long,lat) else returns '??' as countrycode'''
    
    if countrypolydict=='':
        countrypolydict=CountryPolyDict(predicted_countrycode)
    
    p1=Point(long,lat)
    res_country='XX'
    found=False
    for country in countrypolydict:
        for shape in reversed(range(len(countrypolydict[country]))):
            if p1.within(countrypolydict[country][shape]):
                res_country=country
                found=True
                break
        if found:
            break
    return res_country




def GetCountry4List(long_list,lat_list,countrypolydict,predicted_countrycode=''):
    '''Calls CountryCheck for list of Points (e.g Pipelinepoints)
    Gets the countrypolydict from CountryPolyDict()
    Returns countrycodeslist'''
    
    countrycodelist=[]
    for long,lat in zip(long_list,lat_list):
        country=GetCountry(long,lat,countrypolydict,predicted_countrycode)
        countrycodelist.append(country)
    return countrycodelist




def GetCountry4Component(component,countrypolydict='',predicted_countrycode=''):
    '''Get countrycodes 4 all geopoints of a Netclass component e.g. OSM.PipeLines
    Returns list of list with country_codes'''
	
    if countrypolydict=='':
        countrypolydict=CountryPolyDict()
    with mp.Pool() as pool:
        jobs = [pool.apply_async(GetCountry4List, args=(element.long, element.lat,
                countrypolydict,predicted_countrycode)) for element in component]
        results=[x.get() for x in jobs]

    return results




#Quicktest of function
if __name__=="__main__":
    dicta=CountryPolyDict()
    print(GetCountry(-6.28,53.35,dicta))  #IE
    print(GetCountry(-3.2100984,40.3900748,dicta)) #ES

