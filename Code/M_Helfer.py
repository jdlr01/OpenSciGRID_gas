# -*- coding: utf-8 -*-
"""
M_Helfer
--------

Collection of functions, that are being called from other modules.
"""


import datetime
from   scipy.interpolate  import interp1d
from   fuzzywuzzy         import fuzz
import Code.M_FindPos         as M_FindPos
import Code.M_MatLab          as M_MatLab
import numpy as np
import unicodedata
import math





def getLineFromFile(pathPrivKey):
    """Reads first line in file, and returns as string"""
    
    f = open(pathPrivKey, "r")
    line = f.readline()
    f.close()
    return str(line)





def string2floats(string):
    """Converting a string into a float"""
	
    listVal = []
    string.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
    while 1:
        index = string.find(' ')
        if index == -1:
            if len(string) > 0:
                listVal.append(float(string))
            return listVal
        else:
            wert    = string[0:index]
            listVal.append(float(wert))
            string  = string[index+1:]




def get_attribFromList(Data, attribLabel):
    """ Returns a list of attribute values (**attribLabel**) from data **Data**.

    \n.. comments:     
    Input:
        Data:           instance of Netz Class 
        attribLabel:    String of attribute label
    Return:
        AlleAttribVal:   Variable von Type Liste, mit allen Namen
    """
    
    AlleNamen = []
    if 'comp_id' in attribLabel:
        for data in Data:
            AlleNamen.append(data.comp_id)
    elif 'name' in attribLabel:
        for data in Data:
            AlleNamen.append(data.name)
    else:
        for data in Data:
            AlleNamen.append(data.__dict__[attribLabel])
        
    return AlleNamen
    



def get_attribFromComp(Netz, compLabel, attribLabel, makeLower = False):
    """ Returns a list of attrib values (**attribLabel**) from selected component (**compLabel**) 

    \n.. comments:     
    Input:
        Netz:           instance of Netz Class 
        compLabel:      String of Component String
        attribLabel:    String of attribute label
		makeLower: 		Boolean to convert all string to lower	
						(default = False)
    Return:
        AlleAttribVal:   Variable of type list, containing all names
    """
    
    AlleAttribVal = []
    
    if makeLower == False:
        for comp in Netz.__dict__[compLabel]:
            if attribLabel in dir(comp):
                AlleAttribVal.append(comp.__dict__[attribLabel])
                
            elif attribLabel in comp.param:
                AlleAttribVal.append(comp.param[attribLabel])
                
            else:
                AlleAttribVal.append(None)
    else:
        
        for comp in Netz.__dict__[compLabel]:
            if attribLabel in dir(comp):
                AlleAttribVal.append(comp.__dict__[attribLabel].lower())
                
            elif attribLabel in comp.param:
                AlleAttribVal.append(comp.param[attribLabel].lower())
                
            else:
                AlleAttribVal.append(None)
        
    return AlleAttribVal
    
    


def strip_accents(textIn):
    """ Function to replace the "foreign" symbols to get simple UTF-8 writeabel data
    
    \n.. comments: 
    Input:
        text:        String or float, check will be done here
    Output:
        RetText:     String or float return, depending on inputt
    """
    
    if type(textIn) == float:
        return textIn
    else:
        try:
            wert = ''
            textIn = textIn.replace('Ü', 'Ue') 
            textIn = textIn.replace('ü', 'ue') 
            textIn = textIn.replace('Ä', 'Ae') 
            textIn = textIn.replace('ä', 'ae')
            textIn = textIn.replace('Ö', 'Oe') 
            textIn = textIn.replace('ö', 'oe')

            text = textIn
            wert = wert.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
            wert = wert.replace('á', '')
            wert = wert.replace('å', '')

            wert = wert.replace('ç', '')

            wert = wert.replace('é', 'e') 

            wert = wert.replace('н', 'h') 

            wert = wert.replace('í', '')

            wert = wert.replace('ł', 'l') 

            wert = wert.replace('ñ', '')

            wert = wert.replace('О', 'O')
            wert = wert.replace('О', 'O')
            
            wert = wert.replace('ó', '')

            wert = wert.replace('ř', 'r') 

            wert = wert.replace('ú', '')

            wert = wert.replace('н', 'h') 
            wert = wert.replace('л', 'l') 
            wert = wert.replace('ї', 'i') 
            wert = wert.replace('м', 'm') 
            wert = wert.replace('з', '3') 
            wert = wert.replace('ь', 'b') 
            wert = wert.replace('п', 'n') 
            wert = wert.replace('и', 'n') 
            wert = wert.replace('в', 'b') 
            wert = wert.replace('ð', '')
            wert = wert.replace('þ', '')
            wert = wert.replace('¿', '?')
            wert = wert.replace('', '')
            
        except:
            pass
            
        return wert




def converteStr2DateTime(String):
    """ Function conversion of **String** to Python date, assuming format of %Y-%m-%dT%I:%M:%S.  
    Applying a datetime.timedelta as well in respect of '+' or '-' in time stamp string.
    
    \n.. comments: 
    Input:
        String      string to be dissected
    Return:
        DateTime    Date of type datetime.datetime
    Example:
        converteStr2DateTime('2013-10-01T01:00:00+02:00')
    """
    
    DateTime    = []
    try:
        
        if len(String) == 25:
            Format      = '%Y-%m-%dT%H:%M:%S'
            DateTime    = datetime.datetime.strptime(String[0:19], Format)
            DateTime.replace(tzinfo=datetime.timezone.utc)
        
            if String[19]=='+':
                DateTime -= datetime.timedelta(hours=int(String[20:22]),minutes=int(String[23:]))
            elif String[19]=='-':
                DateTime += datetime.timedelta(hours=int(String[20:22]),minutes=int(String[23:]))
                
        elif len(String) == 19:
            Format      = '%Y-%m-%dT%H:%M:%S'
            DateTime    = datetime.datetime.strptime(String, Format)
            DateTime.replace(tzinfo=datetime.timezone.utc)

        elif len(String) == 10:
            Format      = '%Y-%m-%d'
            DateTime    = datetime.datetime.strptime(String, Format)

        else:
            print(String)
            print('ERROR: M_Helfer.converteStr2DateTime: code not written yet.')
        
    except:
        print('Error: M_Helfer.converteStr2DateTime: ' + String)
        raise 
        
    return DateTime
    



def testData(timeSeries, TypeName, PercVal, TypeVal):
    """ Function to determine if time series **timeSeries** should not be used (set to zero length). 
    Two different tests can be done, given through **TypeName**, with additional values required
    fir **TypeName** = 'PercentAbsDiff', where **PercVal** is the percentile, where the sorted 
    absolute difference is required to have a value of **TypeVal**.
    
    \n.. comments:
    Input:
        timeSeries          list of values, time series
        TypeName            string containing type of test:
                                'MedianAbsDiff': 
                                'PercentAbsDiff': 
        PercVal             percent value [%] where on 
        TypeVal         
    Output:
        returnTimeSeries    time series of flow data, same if pasted test, 
                                otherwise of length 0."""
    
    returnTimeSeries    = []
    timeSeriesWork      = timeSeries
    if ('MedianAbsDiff' in TypeName) and (len(timeSeriesWork) > 3):
        returnTimeSeries    = testData(timeSeries, 'PercentAbsDiff', 0.5, TypeVal)
        
    elif ('PercentAbsDiff' in TypeName) and (len(timeSeriesWork) > 3):
        # forming diff between adjacent valus
        timeSeriesWork  = M_MatLab.grad_Vector(timeSeriesWork)
        # making diff absoluite
        timeSeriesWork  = [abs(x) for x in timeSeriesWork]
        # Sorting data set to then select median value, and test 
        timeSeriesWork  = sorted([x for x in timeSeriesWork if not math.isnan(x)], reverse = True)
        PercVal         = int(len(timeSeries) * PercVal / 100)
        if timeSeriesWork[PercVal] == TypeVal:
            returnTimeSeries = timeSeries
        
    elif len(timeSeriesWork) < 4:
        pass
    else:
        print('M_Helfer.testData: TypeName: ' + TypeName + ' not coded.')
        
    return returnTimeSeries    
        



def get_NotPos3(data, posVec):
    """ Wrapper function to call getNotPos with three different inputs: 'name', 'lat', and 'long'.  
    Inputs are the data via **data**, and **posVec**.
        
    \n.. comments:
    Input:
        data:    Data
        posVec:  List of position values
    Return:
        valName:
        valLat:
        valLong:
    """

    valName     = get_NotPos(data, posVec, 'name')
    valLat      = get_NotPos(data, posVec, 'lat')
    valLong     = get_NotPos(data, posVec, 'long')
    
    return valName, valLat, valLong
    
    


def get_NotPos(data, posVec, attribName):
    """ Function to returns subset of data **data**, for where **posVec** 
    does not have an entry.  Currently implemented for attributes: 
	'name', 'lat', and 'long'.

    \n.. comments:
    Input:
        data:        Component with attributes (name, lat, long), where a subset
                     will be returned of those, where the index is NOT in posVec
        posVec:      list, of positions (integers)
        attribName:  string, of attribute name, currently only the following implemented: name, lat, long
    Return:
        reData:      truncated data.
    """
    
    reData  = []
    count   = 0
    # getting information from Netze
    for netze in data:
        if  (count in posVec) == False:
            if attribName in netze.param:
                reData.append(netze.param[attribName])
            else:
                reData.append(netze.__dict__[attribName])
        count = count + 1

    return reData




def get_NameMatch(Name_1, Name_2):
    """ Function constructs two position lists where elements from list of string 
    **Name_1** are identical to string in list **Name_2**.

    \n.. comments: 
    Input:
        Name_1:      list of strings
        Name_2:      lsit of strings
    Output:
        pos_1:       list of ints, of positions in Name_1        
        pos_2:       list of ints, of positions in Name_2
    """
    
    # Initialization
    c_1     = 0
    c_2     = 0
    pos_1   = []
    pos_2   = []
    
    # going through element by element
    try:
        for name1 in Name_1:
            c_2 = 0
            for name2 in Name_2:
                if name2 == name1:
                    pos_1.append(c_1)
                    pos_2.append(c_2)
                c_2 = c_2 + 1
        
            c_1 = c_1 + 1
    except:
        print('ERROR: M_Helfer.getNameMatchname1: ' + name1 + ', name2: ' + name2)
        raise 
    
    return pos_1, pos_2




def get_NameMatrix_Fuzzy(Data_1, Data_2, AddInWord = 0):
    """ Function constructs a matrix of how similar the list of strings is between 
	data sets **Data_1**, and **Data_2**, with values between 0 and 1. Method: 
	1) for each string of both data sets, derive max length of overlapping strings, 
	2) divide by length of strings from Name_1.
            
    \n.. comments:
    Input:
        Name_1      list of strings
        Name_2      lsit of strings
        AddInWord   value 
    Output:
        ReMatrix    matrix of floats, indicating how similar elements from 
                    Name_1 and Name_2 entries are.
    """
    
    # Initialization
    ReMatrix = [[0 for x in range(len(Data_2))] for y in range(len(Data_1))] 
    c_1 = 0
    c_2 = 0
    
    if type(Data_1) == str:
        ReMatrix        = [[0 for x in range(1)] for y in range(1)] 
        ReMatrix[0][0]  = fuzz.ratio(Data_1, Data_2)
    else:
    
        # going through element by element
        try:
            if AddInWord == 0:
                for name1 in Data_1:
                    c_2 = 0
                    for name2 in Data_2:
                        ReMatrix[c_1][c_2]    = fuzz.ratio(name1, name2)
                        c_2 = c_2 + 1
                    c_1 = c_1 + 1
            else:
                for name1 in Data_1:
                    c_2 = 0
                    for name2 in Data_2:
                        ReMatrix[c_1][c_2]    = fuzz.ratio(name1, name2)
                        if name1 != None and name2 != None:
                            if name1 in name2 or name2 in name1:
                                ReMatrix[c_1][c_2]    = ReMatrix[c_1][c_2] + AddInWord
                        c_2 = c_2 + 1
                    c_1 = c_1 + 1
                    
        except:
            print('ERROR: M_Helfer.getNameMatrix_Fuzzy: name1: ' + name1 + ', name2: ' + name2)
            raise 
    
    return ReMatrix

        


def unitConv(gasType = 'H', fromUnitSt = 'GWh', fromVal = 1, toUnitStr = 'm3'):
    """ Conversion of Gas for units: kWh..TWh, bcm, m3, m^3, ton LNG, m3 LNT, m^3 LNG

    \n.. comments:
    Input: 
        gasType:     	String, of gas type, default: 'H' = 41.1 MJ/m^3, L = 36.0 MJ/m^3
						(default = 'H')
        fromUnitSt:  	string of units of input gas 
						(default = 'GWh')
        fromVal      	float value of gas 
						(default =  1)
        toUnitStr    	string, of units to be returned
						(default = 'm3')
    Return:
        RetGasVal:  float of gas in different unit
    """
    
    RetGasVal = None
    multival  = 1
    multiva2  = 1
    if 'H' in gasType:
        GCV = 41.4 # MJ/m^3
    else: 
        GCV = 36.00 # MJ/m^3

    if 'GWh' == fromUnitSt:
        multival = 1e+9
        fromUnitSt = 'Wh'
    elif 'MWh' == fromUnitSt:
        multival = 1e+6
        fromUnitSt = 'Wh'
    elif 'kWh' == fromUnitSt:
        multival = 1+3
        fromUnitSt = 'Wh'
    elif 'TWh' == fromUnitSt:
        multival = 1e+12
        fromUnitSt = 'Wh'
        
    elif 'bcm' == fromUnitSt:
        multival = 1e+9
        fromUnitSt = 'm^3'
    elif 'm3' == fromUnitSt:
        multival = 1
        fromUnitSt = 'm^3'
        
    elif 'm3 LNG' == fromUnitSt:
        multival = 1
        fromUnitSt = 'm^3 LNG'
        
        
    if 'kWh' == toUnitStr:
        multiva2 = 1e-3
        toUnitStr = 'Wh'
    elif 'MWh' == toUnitStr:
        multiva2 = 1e-6
        toUnitStr = 'Wh'
    elif 'GWh' == toUnitStr:
        multiva2 = 1e-9
        toUnitStr = 'Wh'
    elif 'TWh' == toUnitStr:
        multiva2 = 1e-12
        toUnitStr = 'Wh'
        
    elif 'm3' == toUnitStr:
        toUnitStr = 'm^3'
        multiva2 = 1
    elif 'bcm' == toUnitStr:
        toUnitStr = 'm^3'
        multiva2 = 1e-9
    elif 'm3 LNG' == toUnitStr:
        toUnitStr = 'm^3 LNG'
        multiva2 = 1e-9
        
        
    print('fromUnitSt: ' + fromUnitSt)
    print('toUnitStr:  ' + toUnitStr)
    
    if 'Wh' == fromUnitSt:
        if 'm^3' == toUnitStr:                                                  # Tested
            RetGasVal = fromVal * 60*60 / GCV * multival / 1e+6
            print('multival  ' + str(multival) ) 
        elif 'm^3 LNG' == toUnitStr:                                            # Tested
            RetGasVal = fromVal * 0.00000017912 * multival 
            print('multival  ' + str(multival) ) 
        elif 'ton LNG' == toUnitStr:                                            # Tested
            RetGasVal = fromVal * 0.0000000797148 * multival 
            print('multival  ' + str(multival) ) 
        else:
            print('ERROR: M_Helfer.unitConv: Code not written.')
            
    elif 'm^3' == fromUnitSt:
        if 'Wh' == toUnitStr:                                                   # Tested
            RetGasVal = fromVal /3600 * GCV  * multival * multiva2 * 1e+6
            print('multival  ' + str(multival) ) 
            print('multival2 ' + str(multiva2) ) 
        elif 'm^3 LNG' == toUnitStr:                                            # Tested
            RetGasVal = fromVal * 0.0000497562 * GCV
        elif 'ton LNG' == toUnitStr:                                            # Tested
            RetGasVal = fromVal * 0.000022143 * GCV
        else:
            print('ERROR: M_Helfer.unitConv: Code not written.')
        
    elif 'm^3 LNG' == fromUnitSt:
        if 'Wh' == toUnitStr:                                                   # Tested
            RetGasVal = fromVal /0.00000017912 * multiva2 * multival
            print('multival  ' + str(multival) ) 
            print('multival2 ' + str(multiva2) ) 
        elif 'ton LNG' == toUnitStr:                                            # Tested
            RetGasVal = fromVal * 0.44503
        elif ('m3' == toUnitStr) or ('m^3' == toUnitStr):
            RetGasVal = fromVal / 0.0000497562 / GCV                            # Tested
        else:
            print('ERROR: M_Helfer.unitConv: Code not written.')


    elif 'ton LNG' == fromUnitSt:
        if 'Wh' == toUnitStr:
            RetGasVal = fromVal /  0.0000000797148  * multiva2
            print('multival2 ' + str(multiva2) ) 
        elif 'm^3' == toUnitStr:
            RetGasVal = fromVal / 0.000022143 / GCV
        elif 'm^3 LNG' == toUnitStr:
            RetGasVal = fromVal / 0.44503
        else:
            print('ERROR: M_Helfer.unitConv: Code not written.')
        
    else:
        print('ERROR: M_Helfer.unitConv: Code not written.')
        
    return RetGasVal
        


def shrink_Data(X_in, Y_in, StepNum):
    """ Function to shrink data, such as polyline, where data is given 
	as **X_in**, **Y_in**, and step length as **StepNum**.
    """
    
    X_out = []
    Y_out = []
    if len(Y_in) <= 1:
        return  X_out, Y_out
    else:
        f       = interp1d(X_in, Y_in)
        X_out   = np.linspace(0, len(X_in)-1, num=StepNum, endpoint=True)
        Y_out   = f(X_out)
    
        X_out   = np.linspace(0, 100, num=StepNum, endpoint=True)
    
    return X_out, Y_out




def get_Days(DateStart, DateEnd, intervalDays = 1):
    """ Returns list of days between two dates, given as **DateStart**, and **DateEnd**, and the interval of the resulting list is given as **intervalDays**. 

    \n.. comments: 
    Input:
        DateStart       String of format '%Y-%m-%d' of first day
        DateEnd         String of format '%Y-%m-%d' of last day
        intervalDays    (Optional = 1)
    Output:
        DayList         list of datetime elements of days, 
                        starting at DateStart
                        and ending at excluding DateEnd
    """
    
    Dates       = []
    
    start_date  = datetime.datetime.strptime(DateStart, '%Y-%m-%d')
    end_date    = datetime.datetime.strptime(DateEnd,   '%Y-%m-%d')

    Dates       = [ start_date + datetime.timedelta(n) for n in range(int ((end_date - start_date).days))]
    
    if intervalDays > 1:
        temp    = [int(i) for i in range(0, len(Dates), intervalDays)]
        temp2   = [Dates[i] for i in temp]
        Dates   = temp2   
    
    return Dates




def unique_String(Punkte):
    """ Function returning a list of unique string from input **Punkte**, using 
    function M_FindPos.find_pos_StringInList.  Data supplied through **Punkte**.

    \n.. comments:    
    Input:
        Punkte          Liste of type Gas_Klassen_Netz.Punkt
    Output:
        Punkte_Return   Liste of type String based on Punkte.name.
    """

    Punkte_Return   = []
    for DieserPunkt in Punkte:
        pos = M_FindPos.find_pos_StringInList(DieserPunkt, Punkte_Return)
        if len(pos) == 0:
            Punkte_Return.append(DieserPunkt)
    
    return Punkte_Return




def countryName2TwoLetter(countryName):
    """Converting country name into 2 letter acrunume.
    """
    
    if (countryName == 'Albania') or (countryName == 'Albanien'):
        return 'AL'
    elif (countryName == 'Austria') or (countryName == 'Oesterreich'):
        return 'AT'
    elif (countryName == 'Algeria') or (countryName == 'Algerien'):
        return 'DZ'
    elif (countryName == 'Belgium') or (countryName == 'Belgien'):
        return 'BE'
    elif (countryName == 'Bulgaria') or (countryName == 'Bulgarien'):
        return 'BG'
    elif (countryName == 'Bosnia Herzegovina') or (countryName == 'Bosnien Herzegowina'):
        return 'BA'#
    elif (countryName == 'Weissrussland') or (countryName == 'Belarus'):
        return 'BY'
    elif (countryName == 'Switzerland') or (countryName == 'Schweiz'):
        return 'CH'
    elif (countryName == 'Cyprus') or (countryName == 'Zypern'):
        return 'CY'
    elif (countryName == 'Czech Republic') or (countryName == 'Tschechien'):
        return 'CZ'
    elif (countryName == 'Germany') or (countryName == 'Deutschland'):
        return 'DE'
    elif (countryName == 'Denmark') or (countryName == 'Daenemark'):
        return 'DK'
    elif (countryName == 'Mediteranian') or (countryName == 'Mittelmeer'):
        return 'DZ'
    elif (countryName == 'Estonia') or (countryName == 'Estland'):
        return 'EE'
    elif (countryName == 'Spain') or (countryName == 'Spanien'):
        return 'ES'
    elif (countryName == 'Finland') or (countryName == 'Finnland'):
        return 'FI'
    elif (countryName == 'France') or (countryName == 'Frankreich'):
        return 'FR'
    elif (countryName == 'Greece') or (countryName == 'Griechenland'):
        return 'GR'
    elif (countryName == 'Croatia') or (countryName == 'Kroatien'):
        return 'HR'
    elif (countryName == 'Hungary') or (countryName == 'Ungarn'):
        return 'HU'
    elif (countryName == 'Ireland') or (countryName == 'Irland'):
        return 'IE'
    elif (countryName == 'Italy') or (countryName == 'Italien'):
        return 'IT'
    elif (countryName == 'Litauen') or (countryName == 'Lithuania'):
        return 'LT'
    elif (countryName == 'Luxemburg'):
        return 'LU'
    elif (countryName == 'Lettland') or (countryName == 'Latvia'):
        return 'LV'
    elif (countryName == 'Libyen') or (countryName == 'Lybia'):
        return 'LY'
    elif (countryName == 'Malta'):
        return 'MT'
    elif (countryName == 'Moldavia') or (countryName == 'Moldavien'):
        return 'MD'
    elif (countryName == 'Nordmazedonien') or (countryName == 'Mazedonia') or (countryName == 'North Mazedonia'):
        return 'MK'
    elif (countryName == 'Holland') or (countryName == 'Netherlands'):
        return 'NL'
    elif (countryName == 'Norwegen') or (countryName == 'Norway') :
        return 'NO'
    elif (countryName == 'Polen') or (countryName == 'Poland'):
        return 'PL'
    elif (countryName == 'Portugal'):
        return 'PT'
    elif (countryName == 'Romania') or (countryName == 'Rumaenien'):
        return 'RO'
    elif (countryName == 'Serbia') or (countryName == 'Serbien'):
        return 'RS'
    elif (countryName == 'Russia') or (countryName == 'Russland'):
        return 'RU'
    elif (countryName == 'Sweeden') or (countryName == 'Schweden'):
        return 'SE'
    elif (countryName == 'Slovenia') or (countryName == 'Slowenien'):
        return 'SI'
    elif (countryName == 'Slovakia') or (countryName == 'Slovakei'):
        return 'SK'
    elif (countryName == 'Turkey') or (countryName == 'Tuerkei'):
        return 'TR'
    elif (countryName == 'Ukrain') or (countryName == 'Ukraine'):
        return 'UA'
    elif (countryName == 'United Kingdom') or (countryName == 'England'):
        return 'GB' # 
    
    
    return ''
    
    
    
    