# -*- coding: utf-8 -*-
"""
M_MatLab
--------

Collection of functions, that are being called from other modules, reflecting MatLab functionality.
"""

import Code.M_FindPos   as M_FindPos
import array    		as arr
import numpy            as np
np.seterr(divide='ignore', invalid='ignore')
import numbers
import sys
import copy
import math



def select_Vector(vecIn, posIn):
    """Selects elements of a list **vecIn**, based on positions supplied via **posIn**,
    and returns as list.	
	"""
    vecOut = []
    
    for pp in posIn:
        vecOut.append(vecIn[pp])
        
    return vecOut




def roundNone(val, prec):
    """Rounds number, but checks that number is not None."""
    
    if val is None:
        return None
    else:
        return round(val, prec)
    
    
    
    
def sort_Vector(vecIn):
    """ Sorting a list of values
    
    \n.. comments: 
    Input:
        vecIn:       list of floats/int
    Output:
        RetList:      list of sorted values
        PosList:      list of Positions
    """
    
    vecin = copy.deepcopy(vecIn)
    
    PosList = []    
    ReTransform = False
    if isinstance(vecin[0], int):
        ReTransform = True
        for ii in range(len(vecin)):
            vecin[ii] = float(vecin[ii])
        
    # Sorting data
    RetList = sorted([x for x in vecin if not math.isnan(x)], reverse = False)

    # determen position values
    for ii in range(len(RetList)):
        pos = M_FindPos.find_pos_ValInVector(RetList[ii], vecin, '==')
        PosList.append(pos[0])
        vecin[pos[0]] = np.inf

    # Transform back to Int if required
    if ReTransform == True:
        for ii in range(len(RetList)):
            RetList[ii] = int(RetList[ii])
        
    else: 
        print('ERROR: M_MatLab.sort_Vector: code not written yet')

    return RetList, PosList




def get_notNone(valList = []):
    """Returns elements of input list **valList**, where all None values are removed.
	"""
	
    retList = []
    
    if len(valList ) > 0:
        for val in valList:
            if val != None:
                retList.append(val)
                
    return retList




def grad_Vector(vecIn):
    """ Calculation of the gradient/difference between adjacent list elements: retVal = vecIn[ii+1] - vecIn[ii]. In addition, return list is bufferent with single value of '0' at end,  so that is has same length as input
    
    \n.. comments: 
    Input:
        vecIn:       list of floats/int
    Output:
        RetVal:      list of float values of vec1/vec2
    """
    
    RetVec = []
    for ii in range(len(vecIn)-1):
        RetVec.append(vecIn[ii+1] - vecIn[ii])
        
    RetVec.append(0)
    
    return RetVec

	

	
def div_Vectors(vec1, vec2):
    """ Executes **vec1/vec2** element by elemnt.
    
    \n.. comments: 
    Input:
        vec1:    list of floats/int
        vec2:    list of floats/int
    Output:
        RetVal:  list of float values of vec1/vec2
    """
    
    RetVal = []
    for ii in range(len(vec1)):
        if vec2[ii] != 0:
            RetVal.append(float(vec1[ii])/float(vec2[ii]))
        else:
            RetVal.append(float('nan'))
        
    return RetVal
        

		
		
def shrink_Matrix(GoodnessMatrix_Orig, EntsoG_pos, Netze_pos):
    """ Shrinking of Goodnes matrix **GoodnessMatrix_Orig** to elements that are left in data set to be done.  Elements to keep are given through **EntsoG_pos**, and **Netze_pos**.
    
    \n.. comments: 
    Input:
        GoodnessMatrix_Orig:     Matrix of goodness values
        EntsoG_pos:              Positions in X-dimension of elements to be kept
        Netze_pos:               Positions in Y-dimension of elements to be kept
    Output:
        ReMatrix:                Subset of Matrix of goodness values
		
    """
    
    ReMatrix = [[0 for x in range(len(Netze_pos))] for y in range(len(EntsoG_pos))] 
    try:
        for xx in range(len(EntsoG_pos)):
            for yy in range(len(Netze_pos)):
                ReMatrix[xx][yy] = GoodnessMatrix_Orig[EntsoG_pos[xx]][Netze_pos[yy]]
    except:
        
        pass
    return ReMatrix



	
def get_max(listValues):
    """ Function returning the max value of a list of values **listValues**.  
    None values are being ignored and removed before any calculation.

    \n.. comments: 
    Input:
        timeSeries:     time series list
    Return:
        ReturnVal:  	median value
		uncertVal:      error associated with maximum value
    """

    ReturnVal   = float('nan')
    values      = []
    uncertVal   = 0
    
    if len(listValues) > 0:
        listValues  = np.array([listValues])
        values      = listValues[listValues != None]
        valuesSort  = sorted([x for x in values], reverse = True)
        ReturnVal   = valuesSort[0]
        
        for ii in range(len(values)):
            wert        = np.concatenate((values[0:ii], values[ii+1:]), axis=0)
            meanVal     = sum(wert) / len(wert)
            uncertVal   = uncertVal + (values[ii] - meanVal)*(values[ii] - meanVal)
            
        uncertVal = math.sqrt(uncertVal)/ math.sqrt(len(values))

    return ReturnVal, uncertVal 




def get_min(listValues):
    """ Function returning the min value of a list of values **listValues**.  
    None values are being ignored and removed before any calculation.

    \n.. comments: 
    Input:
        listValues:     time series list
    Return:
        ReturnVal:  	minimum value
		uncertVal:      error associated with minimum value
    """
    
    ReturnVal = float('nan')
    values      = []
    uncertVal   = 0

    if len(listValues) > 0:
        listValues  = np.array([listValues])
        values      = listValues[listValues != None]
        valuesSort  = sorted([x for x in values], reverse = True)
        ReturnVal   = valuesSort[-1]
        
        for ii in range(len(values)):
            wert        = np.concatenate((values[0:ii], values[ii+1:]), axis=0)
            meanVal     = sum(wert) / len(wert)
            uncertVal   = uncertVal + (values[ii] - meanVal)*(values[ii] - meanVal)
            
        uncertVal = math.sqrt(uncertVal)/ math.sqrt(len(values))

    return ReturnVal, uncertVal  
	



def get_mean(listValues):
    """ Function returning the mean value of a list **listValues**.  
    None values are being ignored and removed before any calculation.

    \n.. comments: 
    Input:
        listValues:     List o
    Return:
        ReturnVal:  	median value
		uncertVal:      error associated with mean value
    """
    
    ReturnVal   = float('nan')
    uncertVal   = 0
    values      = []
    if len(listValues) > 0:
        listValues  = np.array([listValues])
        values      = listValues[listValues != None]
        ReturnVal   = sum(values) / len(values)
        
        for ii in range(len(values)):
            wert        = np.concatenate((values[0:ii], values[ii+1:]), axis=0)
            meanVal     = sum(wert) / len(wert)
            uncertVal   = uncertVal + (values[ii] - meanVal)*(values[ii] - meanVal)
            
        uncertVal = math.sqrt(uncertVal)/ math.sqrt(len(values))

    return ReturnVal, uncertVal 




def get_median(listValues):
    """ Function returning the median value of a list **listValues**.
    None values are being ignored and removed before any calculation.

    \n.. comments: 
    Input:
        listValues:     time series list
    Return:
        ReturnVal:  	median value
    """
    
    ReturnVal = float('nan')
    uncertVal   = 0
    values      = []
    if len(listValues) > 0:
        for val in listValues:
            if val != None:
                values.append(val)
        valuesSort = sorted([x for x in values if not math.isnan(x)], reverse = True)
        ReturnVal  = valuesSort[int(len(valuesSort)/2)]
        
        for ii in range(len(values)):
            wert        = np.concatenate((values[0:ii], values[ii+1:]), axis=0)
            meanVal     = sum(wert) / len(wert)
            uncertVal   = uncertVal + (values[ii] - meanVal)*(values[ii] - meanVal)
            
        uncertVal = math.sqrt(uncertVal)/ math.sqrt(len(values))

    return ReturnVal, uncertVal  




def get_STD(values, MeanVal = None):
    """Calculates the STD  of a list of values **values**.
    Mean value can be supplied through **MeanVal** or will be calculated on the fly.
    Here sqrt(N) will be used.
	"""
	
    uncertVal = float('nan')
    
    if MeanVal == None:
        MeanVal = sum(values) / len(values)

    wert = 0
    for val in values:
        wert = wert + (val - MeanVal) * (val - MeanVal)
        
    wert = math.sqrt(wert)
    
    wert = wert/math.sqrt(len(values))
    
    uncertVal = wert
    
    return uncertVal




def get_STD_minus_1(values, MeanVal = None):
    """Calculates the STD  of a list of values **values**.
    Mean value can be supplied through **MeanVal** or will be calculated on the fly.
    Here sqrt(N-1) will be used.	
	"""
    uncertVal = float('nan')
    
    if MeanVal == None:
        MeanVal = sum(values) / len(values)

    wert = 0
    for val in values:
        wert = wert + (val - MeanVal) * (val - MeanVal)
        
    wert = math.sqrt(wert)
    
    wert = wert/math.sqrt(len(values) - 1)
    
    uncertVal = wert
    
    return uncertVal







def get_strings(Daten, Name):
    """ Function to get all strings from classes **Daten** with element label **Name**.

    \n.. comments: 
    Input:
        Daten:       Daten
        Name:        string, containing label in class
    Return:
        AllStrings:  List of Strings
    """
    
    AllPointKeys = []
    for data in Daten:
        AllPointKeys.append(data.__dict__[Name])
    
    return AllPointKeys




def get_strings_unique(Daten, Name):
    """ Function to get unique strings from a data set **Daten** with element label **Name**.

    \n.. comments: 
    Input:
        Daten:       Daten
        Name:        string, containing label in class
    Return:
        AllStrings:  List of Strings
    """
    
    AllPointKeys    = get_strings(Daten, Name)
    myset           = set(AllPointKeys)
    AllStrings      = list(myset)

    return AllStrings




def zeros(TypeStr, VectorLaenge):
    """ Function to create a list of type **TypeStr**, with length **VectorLaenge** populated with zeros.

    \n.. comments: 
    Input:
        TypeStr:         Char fuer Typen von Ausgabe Variable
        VectorLaenge:    Integer, Laenge der Ausgabe Variable
    Return:
        VectorRet:       Vector voller Nullen
    """
    
    VectorRet = []
    if TypeStr == 'i':
        VectorRet = arr.array('i', list(range(0, VectorLaenge)))
    elif TypeStr == 'f':
        VectorRet = arr.array('f', list(range(0, VectorLaenge)))
    elif TypeStr == 'lf':
        VectorRet = []
        for ii in range(VectorLaenge):
            VectorRet.append(0.0)
    elif TypeStr == 'li':
        VectorRet = []
        for ii in range(VectorLaenge):
            VectorRet.append(0)
    else: 
        print(sys.argv[0] + '.zeros: code not written')
        raise 
    
    return VectorRet
   
    


def inv_Matrix(M1):
    """ Function to form the inverse of a matrixies **M1**.
	
    \n.. comments: 
    Input:
        M1:      matrix 1
        val:     float value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is multiplied 
                    with value val
    """	
    
    M2 = copy.deepcopy(M1)
    for ii in range(len(M1)):
        for jj in range(len(M1[0])):
            M2[ii][jj] = 1/M1[ii][jj]
            
    return M2




def div_MatrixConst(M1, val):
    """ Function to divide of a matrix *8M1** by a value **val**.
	
    \n.. comments: 
    Input:
        M1:      matrix 1
        val:     float value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is multiplied 
                    with value val
    """	
    
    M2 = copy.deepcopy(M1)
    for ii in range(len(M2)):
        for jj in range(len(M2[0])):
            M2[ii][jj] = M2[ii][jj] / val
            
    return M2


    

def multi_MatrixConst(M1, val):
    """ Function to multiply of a matrix **M1** with value **val**.
	
    \n.. comments: 
    Input:
        M1:      matrix 1
        val:     float value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is multiplied 
                    with value val
	"""	
    
    if type(M1) == type:
        M2 = list(M1)
    else:
        M2 = copy.deepcopy(M1)
    
    for ii in range(len(M2)):
        for jj in range(len(M2[0])):
            M2[ii][jj] = M2[ii][jj] * val
            
    return M2




def abs_Matrix(M1):
    """ Function to generate the abs value of a matrixies **M1**.

    \n.. comments: 
    Input:
        M1:      matrix 1
    Return:
        ReMatrix:    Matrix of size (M1), where each element is absolute
                     value val
    """	
    
    if type(M1) == type:
        M2 = list(M1)
    else:
        M2 = copy.deepcopy(M1)
    
    for ii in range(len(M2)):
        for jj in range(len(M2[0])):
            M2[ii][jj] = abs(M2[ii][jj])
            
    return M2




def pow_Matrix(M1, val):
    """ Function to multiply of a matrixies **M1** with a power value **val**.

    \n.. comments: 
    Input:
        M1:      matrix 1
        val:     float value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is multiplied 
                    with value val
    """	
    
    if type(M1) == type:
        M2 = list(M1)
    else:
        M2 = copy.deepcopy(M1)
    
    for ii in range(len(M2)):
        for jj in range(len(M2[0])):
            M2[ii][jj] = M2[ii][jj] ** val
            
    return M2




def multi_2Matrix(M1, M2):
    """ Function to multiply of two matrixies **M1** and **M2**: element by element.

    \n.. comments: 
    Input:
        M1:      matrix 1
        M2:      matrix 2 OR single value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is multiplied 
    """
    
    M3 = copy.deepcopy(M1)
    if type(M2) != list:
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = M1[ii][jj] * M2
    else:
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = M1[ii][jj] * M2[ii][jj]
            
    return M3




def relDiff_2Matrix(M1, M2):
    """ Function to return percent difference of two matrixies **M1** and **M2**: element by element.

    \n.. comments: 
    Input:
        M1:      matrix 1
        M2:      matrix 2 OR single value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is multiplied 
    """
    
    if isinstance(M1, np.ndarray):
        M3   = np.subtract(M1, M2)
        M3   = np.divide(M3, M1)

    elif type(M2) != list:
        M3 = copy.deepcopy(M1)
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = (M1[ii][jj] - M2) / M1[ii][jj]
    else:
        M3 = copy.deepcopy(M1)
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = (M1[ii][jj] - M2[ii][jj]) / M1[ii][jj]
            
    return M3
    
    


def add_2Matrix(M1, M2):
    """ Function to addd two matrixies **M1** and **M2**: element by element.
    
    \n.. comments: 
    Input:
        M1:  		matrix 1
        M2:     	matrix 2 OR single value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is added 
    """
    
    M3 = copy.deepcopy(M1)
    if type(M2) != list:
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = M1[ii][jj] + M2
    else:
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = M1[ii][jj] + M2[ii][jj]
            
    return M3




def sub_2Matrix(M1, M2):
    """ Function to subtract two matrixies **M1** and **M2**, element by element.

    \n.. comments: 
    Input:
        M1:      matrix 1
        M2:      matrix 2 OR single value
    Return:
        ReMatrix:    Matrix of size (M1), where each element is subtracted
                    M1 - M2		
    """
    
    M3 = copy.deepcopy(M1)
    if type(M2) != list:
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = M1[ii][jj] - M2
    else:
        for ii in range(len(M1)):
            for jj in range(len(M1[0])):
                M3[ii][jj] = M1[ii][jj] - M2[ii][jj]
            
    return M3


	

def makeBins(N_Data = [], binNumbers = 10):
    """Generation of a histogram, using data **N_Data** supplied as a list, 
    and the number of bins given as **binNumbers**.

    \n.. comments: 
    Input:
        N_Data:      List of data values
        binNumbers:  Integer value, number of bins, 
					 Defautl = 10
    Return:
        X_N:    	Value of bin
        Y_N:        Number of elements in this bin
    """
    
    X_N     = []
    Y_N     = []
    try:
        if len(N_Data) > 0:
            if isinstance(N_Data[0], numbers.Number):
                X_N = np.linspace(min(N_Data), max(N_Data), binNumbers)
                
                Y_N = np.zeros_like(X_N)
        
                bin_indexes = np.searchsorted(X_N, N_Data)
                np.add.at(Y_N, bin_indexes, 1)
    except:
        return [X_N, Y_N]
    
    return [X_N, Y_N]



def Lists_subtract(l1, l2):
    """Subtractoin of two lists (**l1*, **l2**), element by element: l1 - l2
    """
    lOut = []
    for idx in range(len(l1)):
        if l1[idx] != None and  l2[idx] != None:
            lOut.append(l1[idx] - l2[idx])
        else:
            lOut.append(l1[idx])
        
    return lOut



def Lists_devide(l1, l2):
    """Devision of two lists (**l1*, **l2**), element by element: l1 / l2
    """
    lOut = []
    for idx in range(len(l1)):
        if l2[idx] == 0:
            lOut.append(None)
        elif l1[idx] != None and  l2[idx] != None:
            lOut.append(l1[idx] / l2[idx])
        else:
            lOut.append(l1[idx])
        
    return lOut


def Lists_multiply(l1, l2):
    """Multiplication of two lists, element by element
    """
    lOut = []
    for idx in range(len(l1)):
        if l1[idx] != None and  l2[idx] != None:
            lOut.append(l1[idx] * l2[idx])
        else:
            lOut.append(l1[idx])
        
    return lOut



def Lists_addition(l1, l2):
    """Addition of two lists (**l1*, **l2**), element by element: l1 + l2
    """
    lOut = []
    for idx in range(len(l1)):
        if l1[idx] != None and  l2[idx] != None:
            lOut.append(l1[idx] + l2[idx])
        elif l1[idx] == None:
            lOut.append(l1[idx])
        else:
            lOut.append(l2[idx])
        
    return lOut
