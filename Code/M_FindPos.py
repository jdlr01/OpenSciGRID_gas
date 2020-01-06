# -*- coding: utf-8 -*-
"""
M_FindPos
---------

Collection of functions, that are being called from other modules, for finding positions in lists/dicts/... 
or returning part of input for where user specified condition is true.  
"""

import array    		    as arr
import numpy                as np
import Code.M_Projection    as M_Projection



def find_pos_closestLatLongInList(thisLatLong, PipeLatLong):
    """Find the position in list of **PipeLatLong**, which is closest to point 
    given with **thisLatLong**. Input in units of degree.decimal.  
    Return is **distPos** and **minVal** (distance in [km]).
	
	\n.. comments:
    Input:
        thisLatLong     LatLong element (thisLatLong.lat and thisLatLong.long)
        PipeLatLong     Data of the class K_Netze.(component)
    Return:
        distPos 		List of points
		minVal          Corresponding minimum value"""

    # Initialization
    distPos         = None
    dist            = []
    # Creation of inputs for distance.cdist
    for ii in range(len(PipeLatLong.long)):
        dist.append(((thisLatLong.long - PipeLatLong.long[ii]) * (thisLatLong.long - PipeLatLong.long[ii]) + 
                        (thisLatLong.lat - PipeLatLong.lat[ii]) * (thisLatLong.lat - PipeLatLong.lat[ii])))
            
    distPos = np.argmin(dist)
    minVal  = M_Projection.LatLong2DistanceValue(thisLatLong.long, thisLatLong.lat, PipeLatLong.long[distPos], PipeLatLong.lat[distPos])
    
    return [distPos, minVal]




def find_pos_CharInStr(CharIn, StrIn):
    """Finds position of char in a list. Returns a list of positions."""
	
    posRet = []
    posRet = [pos for pos, char in enumerate(StrIn) if char == CharIn]

    return posRet




def find_pos_StringInTouple(String, ToupleofLists, Str2Lower = False):
    """Find position, where string is equal to a string in a tuple.  Input are **String**, and **ToupleofLists**
    
    \n.. comments: 
    Input:
        String:          String, 
        ToupleofLists:   Tuple containing list elements 
    Return:
        pos:             An array of type Integer, containing positions, where String was found in the ListOfStrings."""

    # Initializierung von Variabeln
    pos = arr.array('i', [])
    
    if Str2Lower == False:
        if type(String) == str:
            count = 0
            
            for Name in ToupleofLists:
                if len(Name) > 1:
                    print('WARNING: M_FindPos.find_pos_StringInTouple: Entries in list are more than one')
                if String == Name[0]:
                    pos.append(count)
                count = count + 1
                
        elif type(String) == list:
            
            for Str in String:
                count = 0
                for Name in ToupleofLists:
                    if len(Name) > 1:
                        print('WARNING: M_FindPos.find_pos_StringInTouple: Entries in list are more than one')
                    if Str == Name[0]:
                        pos.append(count)
                    count = count + 1
        elif isinstance(String, float):
            count = 0
            for Name in ToupleofLists:
                if len(Name) > 1:
                    print('WARNING: M_FindPos.find_pos_StringInTouple: Entries in list are more than one')
                if String == Name[0]:
                    pos.append(count)
                count = count + 1
        else:
            print('ERROR: M_FindPos.find_pos_StringInTouple: Code noch NICHT geschrieben')
    else:
        if type(String) == str:
            count   = 0
            String  = String.lower()
            
            for Name in ToupleofLists:
                if len(Name) > 1:
                    print('WARNING: M_FindPos.find_pos_StringInTouple: Entries in list are more than one')
                if String == Name[0].lower():
                    pos.append(count)
                count = count + 1
        elif type(String) == list:
            for Str in String:
                count   = 0
                Str     = Str.lower()
                for Name in ToupleofLists:
                    if len(Name) > 1:
                        print('WARNING: M_FindPos.find_pos_StringInTouple: Entries in list are more than one')
                    if Str == Name[0].lower():
                        pos.append(count)
                    count = count + 1
        elif isinstance(String, float):
            count   = 0
            Str     = String.lower()
            for Name in ToupleofLists:
                if len(Name) > 1:
                    print('WARNING: M_FindPos.find_pos_StringInTouple: Entries in list are more than one')
                if String == Name[0].lower():
                    pos.append(count)
                count = count + 1
        else:
            print('ERROR: M_FindPos.find_pos_StringInTouple: Code noch NICHT geschrieben')
        
    return pos
    



def find_pos_StringInList(String, ListOfStrings, Str2Lower = False):
    """Find positions, where string is equal to a string in a list.  Input are **String**, and **ListOfStrings**
    and boolean **Str2Lower**.
	
    \n.. comments: 
    Input:
        String:          	String, 
        ListVonStrings:  	List of strings 
		Str2Lower: 			Boolean re converting strings to lower.
							(default = False)
    Return:
        pos:             	An array of type Integer, containing positions, where String were found in ListOfStrings."""

    # Initializierung von Variabeln
    pos = arr.array('i', [])
    
    if Str2Lower == False:
        if type(String) == str:
            count = 0
            
            for Name in ListOfStrings:
                if String == Name:
                    pos.append(count)
                count = count + 1
                
        elif type(String) == list:
            
            for Str in String:
                count = 0
                for Name in ListOfStrings:
                    if Str == Name:
                        pos.append(count)
                    count = count + 1
        else:
            print('ERROR: M_FindPos.find_pos_StringInList: Code noch NICHT geschrieben')
    else:
        if type(String) == str:
            count = 0
            String = String.lower()
            
            for Name in ListOfStrings:
                if String == Name.lower():
                    pos.append(count)
                count = count + 1
                
        elif type(String) == list:
            
            for Str in String:
                count = 0
                Str = Str.lower()
                for Name in ListOfStrings:
                    if Str == Name.lower():
                        pos.append(count)
                    count = count + 1
        else:
            print('ERROR: M_FindPos.find_pos_StringInList: Code noch NICHT geschrieben')
        
    return pos
    



def find_pos_LatLongInPoly(LatLong, PolyPairs, Type):
    """Returns truncated array where condition given through **Type** (options are 
    '>', '<', '==', '<=', '>=') and **LatLong** applies to elements of vector **PolyPairs** true.  
    
    \n.. comments: 
    Input:
        LatLong         A single pair of LatLong
        PolyPairs       PolyPairs with components Lat and long.
        Type            String, types of comparison:
                            ">"
                            "<"
                            ">="
                            "<+"
                            "=="
    Return:
        VectorRet       Vector (Type integer), where condition true
    """
    
    pos0 = find_pos_ValInVector(LatLong[0], PolyPairs.long, Type)
    pos1 = find_pos_ValInVector(LatLong[1], PolyPairs.lat, Type)
    

    posdouble = []
    for ii in pos0:
        for jj in pos1:
            if jj == ii:
                posdouble.append(ii)
        
    return posdouble
        

        

def find_pos_ValInVector(Val, Vector, Type):
    """Returns truncated array where condition given through **Type** (options are 
    '>', '<', '==', '<=', '>=') and **Val** applies to elements of vector **Vector** true.  
    
    \n.. comments: 
    Input:
        Val             Value to be searched for (int/float)
        Vector          List of values
        Type            String, type of comparison:
                            ">"
                            "<"
                            ">="
                            "<+"
                            "=="
    Return:
        VectorRet       Vector (Type integer) of positions, where condition true"""
	
    PosLarger = arr.array('i')
    
    if Type == ">":
        PosLarger = [i for i, x in enumerate(Vector) if  x > Val ]
        
    elif Type == "<":
        PosLarger = [i for i, x in enumerate(Vector) if  x < Val ]

    elif Type == "==":
        PosLarger = [i for i, x in enumerate(Vector) if x == Val]
        
    elif Type == "<=":
        PosLarger = [i for i, x in enumerate(Vector) if  x <= Val ]

    elif Type == ">=":
        PosLarger = [i for i, x in enumerate(Vector) if  x >= Val ]
    
    return PosLarger
    
	


def find_pos_ConditionInMatrix(Matrix, typeString):
    """Returns positions (pos1, pos2) in matrix **Matrix**, where condition given through 
    **typeString** is true.  Implemented options are: 'max', and 'min'.
    
    \n.. comments: 
    Input:
        Matrix:      2 dim matrix
        typeString:  string, containing for what to find pos, e.g. min, max,..
    Return:
        pos1:    	position along first axis
        pos2:    	position along second axis"""

    pos1 = -1
    pos2 = -1
    maxVals  = []
    if 'max' in typeString:
        for mm in range(len(Matrix)):
            maxVals.append(max(Matrix[mm]))
            
        val     = max(maxVals)
    elif 'min' in typeString:
        for mm in range(len(Matrix)):
            maxVals.append(min(Matrix[mm]))
            
        val     = min(maxVals)
    else:
        print('error: M_FindPos.find_pos_ConditionInMatrix: code not written for: ' + typeString)
        raise 
    
    for ii in range(len(Matrix)):
        for jj in range(len(Matrix[0])):
            if val == Matrix[ii][jj]:
                pos1 = ii
                pos2 = jj
                return pos1, pos2

    return pos1, pos2

	


def find_pos_StringInTuple(String, TupleOfStrings):
    """ Find position (pos), where **String** can be found in **TupleOfStrings**.
    
    \n.. comments:
    Input:
        String          String, 
        TupleOfStrings  Tuple of strings
    Return:
        pos             An array of type integer, with positions, where string  
                        can be found in tuple. """

    # Initializierung von Variabeln
                        
    if type(String) == str:
        pos = arr.array('i', [])
        count = 0
        
        for Name in TupleOfStrings:
            for name in Name:
                if String == name:
                    pos.append(count)
                count = count + 1
            
    elif type(String) == list:
        pos = arr.array('i', [])
        
        for Str in String:
            count = 0
            for Name in TupleOfStrings:
                for name in Name:
                    if Str == name:
                        pos.append(count)
                    count = count + 1
        
    else:
        print('M_FindPos.find_pos_StringInTuple: Code not written yet')
        raise 
        
    return pos
    



