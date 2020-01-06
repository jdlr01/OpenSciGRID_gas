# -*- coding: utf-8 -*-
"""
M_Projection
-------------

Collection of functions, that are being called from other modules, for projection of spatial information.
"""

from   math            import sin, cos, sqrt, atan2, radians
from pyproj            import Proj, transform




def XY2LatLong(Line, inCoord  = 'epsg:4326', outCoord  = 'epsg:3034', MapProj_q0X = 0, MapProj_q1X = 1, MapProj_q0Y = 0, MapProj_q1Y = 1):
    """ Conversion from EntsoG X,Y coordinates to long lat.  
    
    \n.. comments:
    Order of Processes:
        - Line.long     = Line.long* MapProj_q1X + MapProj_q0X
        - Line.lat      = Line.lat * MapProj_q1Y + MapProj_q0Y
        - [long, lat]   = transform(inProj, outProj, Line.long, Line.lat)
        - in case that values supplied is (0,0), then return will be empty
    
    \n.. comments:        
    Input:
        Line        Element with two parts, Lat, long, EntysoG X coordinate (in inCoord), can be list of values
        inCoord     (Optional = 'epsg:4326'), type string
        outCoord    (Optional = 'epsg:3034'), type string
        MapProj_q0X (Optional = 0) as there can be a further map projection 
                     that is being interpreted via a polynomial fit, this is 
                     the q0 value (offset), for the X-axis
        MapProj_q1X (Optional = 1) as there can be a further map projection 
                     that is being interpreted via a polynomial fit, this is 
                     the q1 value (slope), for the X-axis
        MapProj_q0Y (Optional = 0) as there can be a further map projection 
                     that is being interpreted via a polynomial fit, this is 
                     the q0 value (offset), for the Y-axis
        MapProj_q1Y (Optional = 1) as there can be a further map projection 
                     that is being interpreted via a polynomial fit, this is 
                     the q1 value (slope), for the Y-axis
    Return:
        long        float, longitude of location (in outCoord)
        lat         float, latitude of location (in outCoord)
		
    """
    
    # Initialization
    Ret_long    = []
    Ret_lat     = []
    
    try:
        
        if isinstance(Line.long, float) :
            # In case that supplied values are (0,0), meaning that values not correct in EntsoG data base
            if Line.long == 0 and Line.lat == 0:
                Line.long   = float('nan')
                Line.lat    = float('nan')
                return  Line
            
            Line.long       = Line.long * MapProj_q1X + MapProj_q0X
            Line.lat        = Line.lat  * MapProj_q1Y + MapProj_q0Y
        
            outProj         = Proj(init = outCoord)
            inProj          = Proj(init = inCoord)
            
            Ret_long, Ret_lat   = transform(inProj, outProj, Line.long, Line.lat)
        else:
            outProj     = Proj(init = outCoord)
            inProj      = Proj(init = inCoord)
            if isinstance(Line.long, list):
                lat     = []
                long    = []
                for ii in range(len(Line.long)):
                    long.append(Line.long[ii] * MapProj_q1X + MapProj_q0X)
                    lat.append(Line.lat[ii]  * MapProj_q1Y + MapProj_q0Y)
                Ret_long, Ret_lat   = transform(inProj, outProj, long, lat)
                    
            else:
                Line.long   = Line.long * MapProj_q1X + MapProj_q0X
                Line.lat    = Line.lat  * MapProj_q1Y + MapProj_q0Y
        
                long, lat   = transform(inProj, outProj, Line.long, Line.lat)
                Ret_long.append(long)
                Ret_lat.append(lat)
                
        
    except:
        print('Error: M_Projection.XY2LatLong: function failed.')
        raise 
        
    Line.long   = Ret_long
    Line.lat    = Ret_lat

    return Line




def LatLong2DistanceMatrix(lat_1, long_1, lat_2, long_2):
    """ Constructs a matrix of how far apart points are. By calculation 
	of Cartesian  distance 1/(sqrt( (x1-x2)^2 + (y12-y2)^2)).  For values 
	of sqrt( (x1-x2)^2 + (y12-y2)^2)) < 0.000001 a value of 0.0 is returned. 
    For supplying two identical points, function will return a value of 0.0.

    \n.. comments:            
    Input:
        lat_1       list of floats, of first data set
        long_1      lsit of floats, of first data set
        lat_2       list of floats, of second data set
        long_2      lsit of floats, of second data set
    Return:
        ReMatrix    matrix of floats, indicating how close each point is to 
                    points from other data set.   """

    # Initialization
    ReMatrix = [[0 for x in range(len(lat_2))] for y in range(len(lat_1))] 
    
    # going through element by element
    for c_1 in range(len(lat_1)):
        for c_2 in range(len(lat_2)):
            lat1    = lat_1[c_1]
            lon1    = long_1[c_1]
            lat2    = lat_2[c_2]
            lon2    = long_2[c_2]
            wert    = LatLong2DistanceValue(lon1, lat1, lon2, lat2)

            if wert <0.000001:
                wert = 0.0
            ReMatrix[c_1][c_2] = wert

    return ReMatrix

	
	

def LatLong2DistanceValue(lon1, lat1, lon2, lat2):
    """ Conversion of LatLong in decimal into a distance in [km].
    
    \n.. comments:
    Input:
        lon1        float of long start
        lat1        float of lat  start
        lon2        float of long end
        lat2        float of lat  end
    Return:
        distance    float of distance in [km]
    Example:
        latLong2Dist(2.2, 50.3, 2.5, 51.8)
         = 168.158
         (whereas using proper tools this would be 167.995km, so near enough)   """
    
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

	
	

def LatLongList2Distance(longList, latList):
    """ Conversion of LatLong lists in decimal into a distance in km.
    
    \n.. comments:
    Input:
        lon1        float of long start
        lat1        float of lat  start
        lon2        float of long end
        lat2        float of lat  end
    Return:
        distance    float of distance in [km]
    Example:
        latLong2Dist(2.2, 50.3, 2.5, 51.8)
         = 168.158
         (whereas using propper tools this would be 167.995km, so near enough)
		 
    """
    
    distReturn = 0
    for ii in range(len(longList)-1):
        lon1 = longList[ii]
        lat1 = latList[ii]
        lon2 = longList[ii + 1]
        lat2 = latList[ii + 1]
        distReturn = distReturn + LatLong2DistanceValue(lon1, lat1, lon2, lat2)
        
    return distReturn