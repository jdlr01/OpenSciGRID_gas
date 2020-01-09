# -*- coding: utf-8 -*-
"""
M_Shape
=======

Module containing functions that can be used for shape elements 

"""
import Code.M_FindPos     as M_FindPos
import Code.M_MatLab      as M_MatLab
import Code.M_Visuell     as M_Visuell
import Code.K_Component   as K_Component
import Code.M_DataAnalysis as M_DataAnalysis
from scipy.spatial        import distance

import numpy              as np
import math
import copy






def polyShape2PipeSegment(shape, type = 'normal', part = []):
    """Converting poly lines from shape files into PipeSegment.
	Shape supplied as **shape**, and method of conversion supplied 
	through **type**, with options of "normal" and "mean". The amount of 
    data to be converted can be supplied as integer indexes **part**.  """
    
    parts   = shape.parts
    vec     = shape.points
    X_coor1 = []
    Y_coor1 = []
    X_coor2 = []
    Y_coor2 = []
    werte   = []
    if len(part) == 0:
        startPart   = 0
        endPart     = len(parts)
    else:
        startPart   = part
        endPart     = part
        
    if type == 'normal':
        if len(parts) == 1:
            X_coor1 = vec[0][0]
            Y_coor1 = vec[0][1]
            X_coor2 = vec[-1][0]
            Y_coor2 = vec[-1][1]
        else:
            parts.append(len(vec))
            for ii in range(startPart, endPart):
                werte.append([vec[parts[ii]][0], vec[parts[ii + 1] - 1][0]])
    
            diffVal = M_MatLab.grad_Vector(parts)
            pos     = M_FindPos.find_pos_ValInVector(max(diffVal), diffVal, "==")
                
            X_coor1 = vec[parts[pos[0]]][0]
            Y_coor1 = vec[parts[pos[0]]][1]
            X_coor2 = vec[parts[pos[0] + 1] - 1][0]
            Y_coor2 = vec[parts[pos[0] + 1] - 1][1]
        return [X_coor1, Y_coor1, X_coor2, Y_coor2]
    
    
    elif type == 'mean':
        area = area_for_shape(vec)
        imax = len(vec) - 1#len(polygon) 
    
        result_x = 0
        result_y = 0
        for ii in range(0, imax):
            result_x += (vec[ii][0] + vec[ii+1][0]) * ((vec[ii][0] * vec[ii+1][1]) - (vec[ii+1][0] * vec[ii][1]))
            result_y += (vec[ii][1] + vec[ii+1][1]) * ((vec[ii][0] * vec[ii+1][1]) - (vec[ii+1][0] * vec[ii][1]))
        result_x += (vec[imax][0] + vec[0][0]) * ((vec[imax][0] * vec[0][1]) - (vec[0][0] * vec[imax][1]))
        result_y += (vec[imax][1] + vec[0][1]) * ((vec[imax][0] * vec[0][1]) - (vec[0][0] * vec[imax][1]))
        result_x /= (area * 6.0)
        result_y /= (area * 6.0)

        return [result_x, result_y]
     
        
    
        
def area_for_shape(vec):
    result  = 0
    imax    = len(vec) - 1
    
    for i in range(0, imax):
        result += (vec[i][0] * vec[i+1][1]) - (vec[i+1][0] * vec[i][1])
    result += (vec[imax][0] * vec[0][1]) - (vec[0][0] * vec[imax][1])
    return result / 2.




def Segments2Line(long = [], lat = []):
    """ Sorting pipeSegments given as **lat** and **long** list of list pairs, to 
    a pipeline.
    """
    Ret_long = []
    Ret_lat  = []
    coord    = []
    index_n  = []
    index_m  = []
    distVal  = []
    nn       = []
    m        = []
    if len(long)>1:
        # 2) retrieving all end points
        for ii in range(len(long)):
            coord.append((long[ii][0],   lat[ii][0]))
            coord.append((long[ii][-1],  lat[ii][-1]))
        
        # 3) Generation of distance matrix
        dist_matrix     = np.matrix
        dist_matrix     = distance.cdist(coord, coord)
        for ii  in range(len(coord)):
            dist_matrix[ii][ii] = np.inf
            if ii%2 == 0:
                dist_matrix[ii][ii+1] = np.inf
            else:
                dist_matrix[ii][ii-1] = np.inf
            for yy in range(ii):
                dist_matrix[ii][yy] = np.inf


        # 4) getting index of closest neighbors
        for ii in range(len(long) - 1):
            # n & m index
            nn   = int(math.floor(dist_matrix.argmin()/len(coord)))
            m    = dist_matrix.argmin()%len(coord)
            distVal.append(dist_matrix.min())
            index_n.append(nn)
            index_m.append(m)
            # setting distance position to infinite
            dist_matrix[nn][m] = np.inf
            if (nn%2 == 0) and (m%2 == 0):
                dist_matrix[nn][m+1]   = np.inf
                dist_matrix[nn+1][m]   = np.inf
                dist_matrix[nn+1][m+1] = np.inf
            elif (nn%2 == 1) and (m%2 == 0):
                dist_matrix[nn-1][m]   = np.inf
                dist_matrix[nn][m+1]   = np.inf
                dist_matrix[nn-1][m+1] = np.inf
            elif (nn%2 == 0) and (m%2 == 1):
                dist_matrix[nn][m-1]   = np.inf
                dist_matrix[nn+1][m]   = np.inf
                dist_matrix[nn+1][m-1] = np.inf
            elif (nn%2 == 1) and (m%2 == 1):
                dist_matrix[nn][m-1]   = np.inf
                dist_matrix[nn-1][m]   = np.inf
                dist_matrix[nn-1][m-1] = np.inf


        M_Visuell.Wrapper_PlotLines(coord)
            
            
        # sorting the joints
        index_mm        = []
        distanceTemp    = []
        [index_n, pos]  = M_MatLab.sort_Vector(index_n)
        for ii in pos:
            index_mm.append(index_m[ii])
            distanceTemp.append(distVal[ii])
        index_m = index_mm
        distVal = distanceTemp
        
        vecRet_lat  = lat[0]
        vecRet_long = long[0]
        posAnf      = 0
        # Joining according to index
        for ii in range(len(long)-1):
            nn  = index_n[ii]
            m   = index_m[ii]
            # Davor
            if nn == posAnf:
                # Zweiter umgekehrt an ersten Ersten Anfang vorgeschoben
                if m%2 == 0:
                    posAnf      = m + 1
                    m           = int(m/2)
                    temp_lat    = lat[m][::-1]
                    temp_long   = long[m][::-1]
                        
                    temp_lat.extend(vecRet_lat)
                    temp_long.extend(vecRet_long)
                    vecRet_lat  = temp_lat
                    vecRet_long = temp_long
                else:
                    posAnf      = m + 1
                    m           = int(m/2)
                    temp_lat    = lat[m]
                    temp_long   = long[m]
                        
                    temp_lat.extend(vecRet_lat)
                    temp_long.extend(vecRet_long)
                    vecRet_lat  = temp_lat
                    vecRet_long = temp_long
                    
            # hinten ankleben
            else:
                # extra nicht umdrehen
                if m%2 == 0:
                    m           = int(m/2)
                    vecRet_lat.extend(lat[m])
                    vecRet_long.extend(long[m])
                # neues umdrehen
                else:
                    m           = int(m/2)
                    vecRet_lat.extend(lat[m][::-1])
                    vecRet_long.extend(long[m][::-1])
                    
        coord = []   
        for ii in range(len(vecRet_lat)):
            coord.append([vecRet_long[ii],   vecRet_lat[ii]])
        M_Visuell.Wrapper_PlotLines(coord)
        coord = coord
        
    else:
        Ret_long = long
        Ret_lat  = lat
        distVal  = []

    return [Ret_long, Ret_lat, distVal]







def PolyLine2List(parts, long, lat):
    """ Converting Polyline to list of segments of lat/long, where break points gien by **parts**.  
    """ 
    
    Ret_lat     = []
    Ret_long    = []
    
    parts.append(len(long))
    for ii in range(len(parts)-1):
        b_lat   = []
        b_long  = []
        for jj in range(parts[ii], parts[ii+1]):
            b_long.append(long[jj])
            b_lat.append(lat[jj])
        Ret_lat.append(b_lat)
        Ret_long.append(b_long)
        
    return [Ret_long, Ret_lat]




def PolyLine2PipeSegment(polyLine, parts, source = '', country_code = ''):
    """ Converting Polyline to list of segments of lat/long, where start position 
    of pipeSegment given by **parts**. Function will erase all 
    unnecessary pairs of latlong.
    """ 
    # Initialization
    RetPipeSegments = []
    
    # finding last element of polyline for later looop
    parts.append(len(polyLine.long))
    
    # Find double entries of lat long, that are also start end points
    StartEndLat  = []
    StartEndLong = []
    for pp in range(len(parts)-1):
        StartEndLat.append(polyLine.lat[parts[pp]])
        StartEndLat.append(polyLine.lat[parts[pp+1]-1])
        StartEndLong.append(polyLine.long[parts[pp]])
        StartEndLong.append(polyLine.long[parts[pp+1]-1])

    
    
    # go through each double entry and in corresponding 
    countSegments = 0
    for pp in range(len(parts) - 1):
        # Creation of lat/long pair of current range
        Line    = K_Component.PolyLine(lat = [], long = [])
        for ii in range(parts[pp], parts[pp + 1]):
            Line.lat.append((polyLine.lat[ii]))
            Line.long.append((polyLine.long[ii]))
            
        # Creation of Other StartEndPoint
        otherLat    = StartEndLat.copy()
        otherLong   = StartEndLong.copy()
        EndLat      = otherLat.pop(pp*2 + 1)
        StartLat    = otherLat.pop(pp*2)
        EndLong     = otherLong.pop(pp*2 + 1)
        StartLong   = otherLong.pop(pp*2)
        
        # finding if other startEnd on this range
        posOnLine   = []
        for count in range(len(otherLat)):
            pos = M_FindPos.find_pos_LatLongInPoly([otherLong[count], otherLat[count]], Line, '==')
            posOnLine.extend(pos)
            
        if len(posOnLine) > 0:
            # Sorting the posibilities
            posOnLine.append(0)
            posOnLine.append(len(Line.lat)-1)
            posOnLine         = sorted(posOnLine)
            
            for ss in range(len(posOnLine)-1):
                id          = str(countSegments)
                name        = str(countSegments)
                node_id     = [id]
                source_id   = [source + '_' + str(countSegments)]
                lat         = [Line.lat[ posOnLine[ss]], Line.lat[ posOnLine[ss+1]] ]
                long        = [Line.long[posOnLine[ss]], Line.long[posOnLine[ss+1]] ]
                country_code = country_code
                max_pressure_bar    = None
                
                RetPipeSegments.append(K_Component.PipeSegments(id = id, node_id = node_id, 
                            name = name, source_id = source_id, lat = lat, long = long, 
                            country_code = country_code, param = {'max_pressure_bar': max_pressure_bar}))
                
                countSegments = countSegments + 1
            
            
        else:
            id          = str(countSegments)
            node_id     = [id]
            name        = str(countSegments)
            source_id   = [source + '_' + str(countSegments)]
            lat         = [StartLat,  EndLat]
            long        = [StartLong, EndLong]
            country_code = country_code
            max_pressure_bar    = None
            
            RetPipeSegments.append(K_Component.PipeSegments(id = id, node_id = node_id, 
                        name = name, source_id = source_id, lat = lat, long = long, 
                        country_code = country_code, param = {'max_pressure_bar': max_pressure_bar}))
            
            countSegments = countSegments + 1
    
    
    return RetPipeSegments
    
    


def PolyLine2PipeLinesWrong(polyLine, parts, source = '', country_code = ''):
    """ Converting Polyline to list of pipeLines of lat/long, 
    where start position of pipeSegment given by **parts**.
    Function will keep all latlong values of polyLine
    """ 
    # Initialization
    RetPipeLines = []
    
    # finding last element of polyline for later looop
    parts.append(len(polyLine.long))
    
    # Find double entries of lat long, that are also start end points
    StartEndLat  = []
    StartEndLong = []
    for pp in range(len(parts)-1):
        StartEndLat.append(polyLine.lat[parts[pp]])
        StartEndLat.append(polyLine.lat[parts[pp+1]-1])
        StartEndLong.append(polyLine.long[parts[pp]])
        StartEndLong.append(polyLine.long[parts[pp+1]-1])

    
    
    # go through each double entry and in corresponding 
    countSegments = 0
    for pp in range(len(parts) - 1):
        # Creation of lat/long pair of current range
        Line    = K_Component.PolyLine(lat = [], long = [])
        for ii in range(parts[pp], parts[pp + 1]):
            Line.lat.append((polyLine.lat[ii]))
            Line.long.append((polyLine.long[ii]))
            
        # Creation of Other StartEndPoint
        otherLat    = StartEndLat.copy()
        otherLong   = StartEndLong.copy()
        
        # finding if other startEnd on this range
        posOnLine   = []
        for count in range(len(otherLat)):
            pos = M_FindPos.find_pos_LatLongInPoly([otherLong[count], otherLat[count]], Line, '==')
            posOnLine.extend(pos)
            
        if (posOnLine[0] == 1) and (posOnLine[1] ==0 ) and (posOnLine[2] ==1512):
            posOnLine = posOnLine
            
        if len(posOnLine) > 0:
            # Sorting the posibilities
            posOnLine.append(0)
            posOnLine.append(len(Line.lat)-1)
            posOnLine         = sorted(posOnLine)
            
            for ss in range(len(posOnLine)-1):
                id                  = str(countSegments)
                name                = str(countSegments)
                source_id           = [source + '_' + str(countSegments)]
                lat                 = Line.lat
                long                = Line.long
                country_code        = country_code
                max_pressure_bar    = None
                
                RetPipeLines.append(K_Component.PipeLines(id = id, name = name, 
                            source_id = source_id, lat = lat, long = long, 
                            country_code = country_code, param = {'max_pressure_bar': max_pressure_bar}))
                
                countSegments = countSegments + 1
            
            
        else:
            id                  = str(countSegments)
            name                = str(countSegments)
            source_id           = [source + '_' + str(countSegments)]
            lat                 = Line.lat
            long                = Line.long
            country_code        = country_code
            max_pressure_bar    = None
            
            RetPipeLines.append(K_Component.PipeLines(id = id, name = name, 
                        source_id = source_id, lat = lat, long = long, 
                        country_code = country_code, param = {'max_pressure_bar': max_pressure_bar}))
            
            countSegments = countSegments + 1
    
    
    return RetPipeLines
    
    

def PolyLine2PipeLines(polyLine, parts, source = '', country_code = ''):
    """ Converting Polyline to list of pipeLines of lat/long, 
    where start position of pipeSegment given by **parts**.
    Function will keep all latlong values of polyLine
    """ 
    # Initialization
    RetPipeLines = []
    # total lenght of polyline
    Length = 0

    # finding last element of polyline for later looop
    parts.append(len(polyLine.long))
    
    
    # go through each double entry and in corresponding 
    countSegments = 0
    for pp in range(len(parts) - 1):
        Length   = 0
        # Creation of lat/long pair of current range
        Line    = K_Component.PolyLine(lat = [], long = [])
        for ii in range(parts[pp], parts[pp + 1]):
            Line.lat.append((polyLine.lat[ii]))
            Line.long.append((polyLine.long[ii]))
        
        # Determination of the lengthof each segment
        for ii in range(len(polyLine.long) - 1):
            try:
                long1 = polyLine.long[ii]
                lat1  = polyLine.lat[ii]
                long2 = polyLine.long[ii+1]
                lat2  = polyLine.lat[ii+1]
                if math.isfinite(long1) and math.isfinite(long2) and math.isfinite(lat1) and math.isfinite(lat2):
                    Length = Length + M_DataAnalysis.distance(long1, lat1, long2, lat2)
            except:
                pass
            

        id                  = str(countSegments)
        node_id             = [pp*2, pp*2 + 1]
        name                = str(countSegments)
        source_id           = [source + '_' + str(countSegments)]
        lat                 = Line.lat
        long                = Line.long
        

        RetPipeLines.append(K_Component.PipeLines(id = id, node_id = node_id, name = name, 
                    source_id = source_id, lat = lat, long = long, 
                    country_code = [country_code, country_code], param = {'length': Length}))
        
        countSegments = countSegments + 1


    
    return RetPipeLines




def remCulDeSac(Netz, compName = '', remCulDeSac = 0, excepCulDeSac = []):
    """This function removes PipeLines/Segments that are connected to the network only on one
    side, hence one node is only connected to one PipeLines/Segments.
    PipeLine/Segment is not allowed to be longer than **remCulDeSac** in [km]
    """
    # check that there are Pipes to be done
    if len(Netz.__dict__[compName]) > 0:
        # get list of nodes to exclode (LNGs, Storages,....)
        NodesKeep = []
        for key in Netz.CompLabelsSpot():
            temp = Netz.get_Attrib(key, 'node_id')
            for tt in temp:
                NodesKeep.append(tt)
        # adding user specified nodes that are not to be taken out,...    
        for tt in excepCulDeSac:
            NodesKeep.append(tt)
            
        # get list of all Nodes from Pipes, and determin which nodes only have one pipe leading to it
        NodeId      = []
        UniqNodeId  = []
        SingleNode  = []
        for pipe in Netz.__dict__[compName]:
            NodeId.append(pipe.node_id[0])
            NodeId.append(pipe.node_id[-1])
        UniqNodeId = list(set(NodeId))
        
        for node in UniqNodeId:
            pos = M_FindPos.find_pos_StringInList(node, NodeId)
            if len(pos) == 1:
                SingleNode.append(node)
        
        # going through all pipes, and finding those ones that need to be removed
        for pipe in Netz.__dict__[compName]:
            if pipe.node_id[0] in SingleNode and pipe.node_id[0] not in NodesKeep and pipe.param['length'] < remCulDeSac:
                pipe.id = '-9999'
            elif pipe.node_id[-1] in SingleNode and pipe.node_id[-1] not in NodesKeep and pipe.param['length'] < remCulDeSac:
                pipe.id = '-9999'
        
        # remomving the SulDeSac Nodes
        Netz.select_byAttrib([compName], 'id', '-9999', '!=')
    return Netz
    



def mergePipeEndPoints(Netz, compName = '',  maxDistance = 0.0):
    """If there are two PipeLines/Segments (A and B), and both have end/start Nodes, 
    that are not the start/end of totaly different PipeLine/Segmentd, and if those two 
    Nodes are close together, then those Nodes can be merged into one and the same node.  
    The maximum separation of those two points is given by **maxDistance** [km].
    """
    
    if len(Netz.__dict__[compName]) > 0:
        RetPipes        = copy.deepcopy(Netz.__dict__[compName])
        Pipes           = Netz.__dict__[compName]
        # making helper matrix
        PipeNum         = []
        LatNum          = []
        NodeNum         = []
        NodePos         = []
        Comps2Kill      = []
        ShortLatLong    = K_Component.PolyLine(lat = [], long = [])
    
        # Creation of latlong for all pipeline points
        # Getting all start and end points of the pipeLines
        for idx in range(len(Pipes)):
            PipeNum.append(idx)
            PipeNum.append(idx)
            NodePos.append(0)
            NodePos.append(-1)
    
            LatNum.append(0)
            LatNum.append(len(Pipes[idx].lat)-1)
    
            ShortLatLong.lat.append( Pipes[idx].lat[0])
            ShortLatLong.lat.append( Pipes[idx].lat[-1])
    
            ShortLatLong.long.append(Pipes[idx].long[0])
            ShortLatLong.long.append(Pipes[idx].long[-1])
            NodeNum.append(Pipes[idx].node_id[0])
            NodeNum.append(Pipes[idx].node_id[-1])
            
            
        # Going through each lat long pair and see if there are other lat long pairs that
        # are with in merging distance
        for idx in range(len(ShortLatLong.lat)):
            # getting lat long of pipeline 
            thisLatLong             = K_Component.PolyLine(lat = ShortLatLong.lat[idx], long = ShortLatLong.long[idx])
            thisNode                = NodeNum[idx]
            if ShortLatLong.lat[idx] > -999:
                # "removing" PipeLatLong 
                ShortLatLong.lat[idx]     = -999
                ShortLatLong.long[idx]    = -999
                
                [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, ShortLatLong)
                posNode             = M_FindPos.find_pos_ValInVector(thisNode, NodeNum, '==')
                
                # Node in question exists more than once. hence no merging. 
                # All occurances of this node  set to -999 for 0ShortLatLong
                if len(posNode) > 1:
                    for pp in posNode:
                        ShortLatLong.lat[pp]       = -999
                        ShortLatLong.long[pp]      = -999
                        
                while minVal < maxDistance and len(posNode) == 1:
                    # Ashuring that this found pair is not of the same PipeLine/Segment
                    if PipeNum[idx] != PipeNum[distPos]:
                        # Only if of differnt PipeLine/Segment, moving latLong allowed
                        RetPipes[PipeNum[distPos]].lat[LatNum[distPos]]         = thisLatLong.lat
                        RetPipes[PipeNum[distPos]].long[LatNum[distPos]]        = thisLatLong.long
                        RetPipes[PipeNum[distPos]].node_id[NodePos[distPos]]    = thisNode
                    # removing possible ndoe from list
                    ShortLatLong.lat[distPos]       = -999
                    ShortLatLong.long[distPos]      = -999
                        
                    [distPos, minVal]               = M_FindPos.find_pos_closestLatLongInList(thisLatLong, ShortLatLong)
            

        # now removing pipes that have start and end node the same            
        # Now reducing the Nodes based on changed PipeLines/Segments
        maxDistance = maxDistance * 2
        for idx, pp in enumerate(RetPipes):
            if pp.node_id[0] == pp.node_id[-1]:
                if pp.param['length'] < maxDistance:
                    Comps2Kill.append(idx)
                    
        Comps2Kill = list(set(Comps2Kill))
        Comps2Kill.sort(reverse = True)

        for idx  in Comps2Kill:
            del RetPipes[idx]
            
        
        Netz.__dict__[compName] = RetPipes

        Netz.cleanUpNodes(compNames = [compName], skipNodes = True)

        # last final clean up
        Netz.cleanUpNodes(compNames = [compName], skipNodes = True)


#        Netz.Nodes              = Netz.add_Nodes(compName, [])
#        Netz.Nodes              = M_Shape.reduceElement(Netz.Nodes, reduceType = 'LatLong')
#        
#        roundVal        = 6
#        NodesID         = []
#        NodesLatLong    = K_Component.PolyLine(lat = [], long = [])
#        for nn in Netz.Nodes:
#            NodesLatLong.lat.append(round(nn.lat, roundVal))
#            NodesLatLong.long.append(round(nn.long, roundVal))
#            NodesID.append(nn.id)
#
#
#        for idx, pipe in enumerate(Netz.__dict__[compName]):
#            thisLatLong         = K_Component.PolyLine(lat = round(pipe.lat[0], roundVal), long = round(pipe.long[0], roundVal))
#            [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
#            Netz.__dict__[compName][idx].node_id[0] = NodesID[distPos]
#
#            thisLatLong         = K_Component.PolyLine(lat = round(pipe.lat[-1], roundVal), long = round(pipe.long[-1], roundVal))
#            [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
#            Netz.__dict__[compName][idx].node_id[-1] = NodesID[distPos]
            
#        # removing those pipes that are shorter than merge stistance and that are loops
#        # by keeping those ones, that are correct
#        RetComp = []
#        for idx, pipe in enumerate(Netz.__dict__[compName]):
#            if pipe.node_id[0] != pipe.node_id[1] and pipe.param['length'] > maxDistance:
#                RetComp.append(pipe)
#            elif pipe.param['length'] > maxDistance:
#                RetComp.append(pipe)
#        Netz.__dict__[compName] = RetComp
        
    
    return Netz




def moveComp2Pipe(Netz, compName, pipeName, maxDistance = 2):
    """Components, such as Compressors might not be connected to a PipeLine/Segment.
    Hence if a component is closer to a PipeLine/Segment, then the 
    LatLong of the component is changed to be equal to a closest LatLong polypoint of a PipeLine/Segment.
    Hence works only if the PipeLine/Segment is a polyline.
    This also results in beaking the PipeLine/Segment into two PipeLines/Segments.
    Max allowable movement of the component is given by **maxDistance** [km].
    
    
    \n.. comments: 
    Input:
        Netz           Instance of network class, best to be supplied as copy
        compName       String of component name
        pipeName       String, 'PipeLines' or 'PipeSegments'
        maxDistance    Integer of maximum moved distance for each element [default: 2]"""


    # Setting up input
    posPipes    = []
    posLatLong  = []
    RetPipes    = []
    # PipeLine/Segment
    Pipes               = Netz.__dict__[pipeName] 
    
    # Component of interest
    Components          = Netz.__dict__[compName]
    
    
    # Creation of latlong for all pipeline points
    # Creation of EndStart & EndEnd
    _, _, _, _, PolyPipeNum, PolyLatNum, PolyPipeLatLong, NodeID     = getLatLongVectors(Pipes)
    CompShortEndLat, CompShortEndLong, _, _, _, _, _, _         = getLatLongVectors(Components)
    
    


    # for each node, check if it could be joined to an existing pipeline point
    # if so, then change latlon of pipeline point
    for ii in range(0,len(CompShortEndLat)):
        thisLatLong         = K_Component.PolyLine(lat = CompShortEndLat[ii], long = CompShortEndLong[ii])
        
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, PolyPipeLatLong)
        
        if minVal > 0.0 and minVal < maxDistance:
            Netz.__dict__[compName][ii].lat     = Pipes[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]
            Netz.__dict__[compName][ii].long    = Pipes[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]
            Netz.__dict__[compName][ii].node_id = [NodeID[PolyPipeNum[distPos]]]
            posPipes.append(PolyPipeNum[distPos])
            posLatLong.append(PolyLatNum[distPos])
            
            
    extracount = len(Pipes)
    # sorting the posPipes
    # Cutting PipeLines where new element was moved to
    for  ii, pipe in enumerate(Pipes):
        # checking if this pipe needs breaking up
        if ii in posPipes:
            pos = M_FindPos.find_pos_ValInVector(ii, posPipes, '==')


            # Expanding thisLatLongPos by 0 and length(lat)
            thisLatLongPos = []
            for pp in pos:
                thisLatLongPos.append(posLatLong[pp])
                
            # check that first pos not 1, 
            if thisLatLongPos[0] != 0:
                thisLatLongPos  = [0] + thisLatLongPos 

            # check that last pos is end of latlong
            if thisLatLongPos[-1] != len(pipe.lat) - 1:
                thisLatLongPos  = thisLatLongPos + [len(pipe.lat)-1]

                
            thisLatLongPos.sort()
            thisLatLongPos  = list(set(thisLatLongPos))
            lat             = copy.deepcopy(pipe.lat)
            long            = copy.deepcopy(pipe.long)
            
            if len(thisLatLongPos) == 2:
                Pipes[ii].lat   = lat
                Pipes[ii].long  = long
                RetPipes.append(Pipes[ii])
            else:
                for pp in range(len(thisLatLongPos)-1):
                    p1          = thisLatLongPos[pp]
                    p2          = thisLatLongPos[pp + 1]
                    if pp == 0:
                        Pipes[ii].lat   = lat[0:p2+1]
                        Pipes[ii].long  = long[0:p2+1]
                        RetPipes.append(Pipes[ii])
                    else:
                        PPipe       = copy.deepcopy(pipe)
                        if p1 < p2:
                            extracount  = extracount + 1
                            PPipe.id    = str(extracount)
                            PPipe.lat   = lat[p1:p2+1]
                            PPipe.long  = long[p1:p2+1]
                            
                            RetPipes.append(PPipe)
                            # test
                            if isinstance(Pipes[ii].long, list):
                                if len(Pipes[ii].long) == 1:
                                    1 == 1                        
                
        # pipe stays as is, hence write to return 
        else:
            RetPipes.append(pipe)
                
                
    Netz.__dict__[pipeName]  = RetPipes
    
    return Netz 





def moveComp2Node(Netz, compName, maxDistance = 2):
    """Components, such as Compressors might not be connected to a PipeLine/Segment.
    Hence if a component is closer to a Node of a PipeLine/Segment, then the 
    LatLong of the component is changed to be equal to the closest Node of the PipeLine/Segment.
    Max allowable movement of the component is given by **maxDistance**.
    """
    
    # Setting up input
    
    # Nodes of input Netz
    #Nodes               = Netz.Nodes 
    Nodes   = Netz.add_Nodes('PipeSegments', [])
    
    # Component of interest
    Components          = Netz.__dict__[compName]
    
    # Creation of latlong for all pipeline points
    # Creation of EndStart & EndEnd
    EndLat, EndLong, EndStart, EndEnd, _, _, _, _  = getLatLongVectors(Components)
    _, _, _, _, _, _, PipeLatLong, _  = getLatLongVectors(Nodes)
    
    


    # for each node, check if it could be joined to an existing pipeline point
    # if so, then change latlon of pipeline point
    for ii in range(0,len(EndLat)):
        thisLatLong         = K_Component.PolyLine(lat = EndLat[ii], long = EndLong[ii])
#        thisStart           = EndStart[ii]
#        thisEnd             = EndEnd[ii]
#        thisLat             = []
#        thisLong            = []
        
        # Creating PipeLatLong, where pipeline of question id removed.
#        for jj in range(thisStart, thisEnd+1):
#            thisLat.append(PipeLatLong.lat[jj])
#            thisLong.append(PipeLatLong.long[jj])
#            PipeLatLong.lat[jj]     = -999
#            PipeLatLong.long[jj]    = -999
        
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, PipeLatLong)
        if minVal > 0.0 and minVal < maxDistance:
            Netz.__dict__[compName][ii].lat    = Nodes[distPos].lat
            Netz.__dict__[compName][ii].long   = Nodes[distPos].long

    
            # Resetting -999 
#        for jj in range(thisStart, thisEnd+1):
#            thisLat.append(PipeLatLong.lat[jj])
#            thisLong.append(PipeLatLong.long[jj])
#            PipeLatLong.lat[jj]     = thisLat[jj - thisStart]
#            PipeLatLong.long[jj]    = thisLong[jj - thisStart]

    return Netz




def countSameLatLong(ShortLatLong):
    """Counts for given list of points, how often same one occures.
    Returns list of same length, with occurence value.
    """
    
    CountNode   = []
    lat         = ShortLatLong.lat
    long        = ShortLatLong.long
    nodeStr     = []
    roundVal    = 10
    
    for idx in range(len(lat)):
        nodeStr.append(str(round(lat[idx], roundVal))+str(round(long[idx], roundVal)))
        
    for idx in range(len(lat)):
        thisLatLong = nodeStr[idx]
        pos         = M_FindPos.find_pos_StringInList(thisLatLong, nodeStr)
        CountNode.append(len(pos))
    
    return CountNode





def connectPipesTop(Netz, compName = ''):
    """If a PipeLine/Segment (A) ends/starts closly along another PipeLine/Segment (B) section/pathway/polyline, 
    then the following steps are carried out: 
    1) PipeLine/Segment B is split closest to the PipeLine/Segment A start/end point, 
    2) PipeLine/Segment A endpoint is extended to connect to that newly created above node.
    This only works for PipeLines/Segments, that are Polylines, hence have many LatLong pairs
    along its path."""


    RetPipeLines = []
    
    # making helper matrix
    LatLongPos      = []
    PipePos         = []
    PipeNum         = []
    NodeIDAdd       = []
    NodeDist        = []
    NumLatVals      = []
    ShortNodeID     = []
    ShortLatLong    = K_Component.PolyLine(lat = [], long = [])

    # Generation of Nodesw and their latLong for later
    Nodes           = Netz.add_Nodes(compName, [])
    NodesLatLong    = K_Component.PolyLine(lat = [], long = [])
    NodesID         = []
    for nn in Nodes:
        NodesLatLong.lat.append(nn.lat)
        NodesLatLong.long.append(nn.long)
        NodesID.append(*nn.node_id)
        
        
    Pipe    = Netz.__dict__[compName]
    
    # 0. Pre-Processing for later:
    #    getting list of all lat/long Start/End points
        
    
    # Creation of latlong for all pipeline points
    # Creation of EndStart & EndEnd
    ShortLatLong, ShortLat, ShortLong, ShortPosStart, ShortPosEnd, ShortNodeID, ShortNodeID_Count, ShortPipeID, PipeLength  = getShortLatLong(Pipe)
    PolyLatLong, PolyPipeNum, PolyLatNum                                        = getPolyLatLong(Pipe)
    CountNode                                                                   = countSameLatLong(ShortLatLong)
    

    # 1. Check if node could be joined to an existing pipeline point
    # if so, then change latlon of pipeline point
    for ii in range(0,len(ShortLat)):
        if (CountNode[ii] == 1):
            thisLatLong         = K_Component.PolyLine(lat = ShortLat[ii], long = ShortLong[ii])
            thisPosStart        = ShortPosStart[ii]
            thisPosEnd          = ShortPosEnd[ii]
            thisLat             = []
            thisLong            = []
            
            # Creating PipeLatLong, where pipeline of question id removed.
            # Prep
            for jj in range(thisPosStart, thisPosEnd+1):
                thisLat.append(PolyLatLong.lat[jj])
                thisLong.append(PolyLatLong.long[jj])
                PolyLatLong.lat[jj]     = -999
                PolyLatLong.long[jj]    = -999
            
            # Find closest latlong to pipe end
            [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, PolyLatLong)
            # reverting prep
            for jj in range(thisPosStart, thisPosEnd+1):
                thisLat.append(PolyLatLong.lat[jj])
                thisLong.append(PolyLatLong.long[jj])
                PolyLatLong.lat[jj]     = thisLat[jj - thisPosStart]
                PolyLatLong.long[jj]    = thisLong[jj - thisPosStart]
            
            # Chancing end point of PipeLine/Segment
            if (minVal == 0.0):
                if len(PipePos) == 0:
                    # This is first time round having found a join
                    Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                    Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                    
                    # keepign track of where pipelinepoint where changed due to node
                    PipePos.append(PolyPipeNum[distPos])
                    LatLongPos.append(PolyLatNum[distPos])
                    NodeIDAdd.append(ShortNodeID[ii])
                    NodeDist.append(minVal)
                    NumLatVals.append(distPos)
                    PipeNum.append(ShortPipeID[ii])
                
                else:
                    if PipePos[-1] != PolyPipeNum[distPos]:
                        Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                        Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                        # keepign track of where pipelinepoint where changed due to node
                        PipePos.append(PolyPipeNum[distPos])
                        LatLongPos.append(PolyLatNum[distPos])
                        NodeIDAdd.append(ShortNodeID[ii])
                        PipeNum.append(ShortPipeID[ii])
                        NodeDist.append(minVal)
                        NumLatVals.append(distPos)
                        
                    elif NodeDist[-1] > minVal:
                        Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                        Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                        # keepign track of where pipelinepoint where changed due to node
                        PipePos[-1]     = PolyPipeNum[distPos]
                        LatLongPos[-1]  = PolyLatNum[distPos]
                        NodeIDAdd[-1]   = ShortNodeID[ii]
                        NodeDist[-1]    = minVal
                        NumLatVals[-1]  = distPos
                        
                    elif len(M_FindPos.find_pos_ValInVector(ShortPipeID[ii], PipeNum, '==')) == 0:
                        # In case that this pipe has not been connected at all yet to another pipeline
                        Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                        Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                        # keepign track of where pipelinepoint where changed due to node
                        PipePos.append(PolyPipeNum[distPos])
                        LatLongPos.append(PolyLatNum[distPos])
                        NodeIDAdd.append(ShortNodeID[ii])
                        NodeDist.append(minVal)
                        NumLatVals.append(distPos)
    
    
    # 2. Breaking up PipeLines, that contain a new Node
    for ii, pipe_ in enumerate(Pipe):
        pos = M_FindPos.find_pos_ValInVector(ii, PipePos,  '==')

        if len(pos) > 0:
            # creation of LatLong of pipe
            allLat                  = Pipe[ii].lat
            allLong                 = Pipe[ii].long
            
            # More than ONE node on Pipe
            thislatlongpos = []
            for pp in pos:
                thislatlongpos.append(LatLongPos[pp])
            
            # Adding start and end point to list
            if thislatlongpos[0] != 0:
                thislatlongpos.append(0)
            if thislatlongpos[-1] != len(allLong)-1:
                thislatlongpos.append(len(allLong)-1)
            
            # Sorting of break points
            thislatlongpos = sorted(thislatlongpos)
                
            for ss in range(len(thislatlongpos) - 1 ):
                pipe           = copy.deepcopy(Pipe[ii])
                pipe.lat       = allLat[ thislatlongpos[ss] : thislatlongpos[ss + 1] + 1]
                pipe.long      = allLong[thislatlongpos[ss] : thislatlongpos[ss + 1] + 1]
                pipe.param.update({'breakLine': 1})
                RetPipeLines.append(pipe)
                if len(pipe.long) == 1:
                    pipe.long = pipe.long
            
        # No extra node found, take existing Pipe
        else:
            Pipe[ii].param.update({'breakLine': 0})
            RetPipeLines.append(Pipe[ii])
            if len(Pipe[ii].long) == 1:
                Pipe[ii].long = Pipe[ii].long
            
    # Now assining the all pipelines back to netz.
    Netz.__dict__[compName] = RetPipeLines
    
    # 3. Giving pipes correct node_id s
    # Now reducing the Nodes based on changed PipeLines/Segments
    roundVal        = 6
    NodesID         = []
    NodesLatLong    = K_Component.PolyLine(lat = [], long = [])
    for nn in Netz.Nodes:
        NodesLatLong.lat.append(round(nn.lat, roundVal))
        NodesLatLong.long.append(round(nn.long, roundVal))
        NodesID.append(nn.id)


    for idx, pipe in enumerate(Netz.__dict__[compName]):
        thisLatLong         = K_Component.PolyLine(lat = round(pipe.lat[0], roundVal), long = round(pipe.long[0], roundVal))
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
        Netz.__dict__[compName][idx].node_id[0] = NodesID[distPos]

        thisLatLong         = K_Component.PolyLine(lat = round(pipe.lat[-1], roundVal), long = round(pipe.long[-1], roundVal))
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
        Netz.__dict__[compName][idx].node_id[-1] = NodesID[distPos]


    return Netz






def lonePipeEnd2PipePoly(Netz, compName = '', maxDistance = 1):
    """If a PipeLine/Segment (A) ends/starts closly along another PipeLine/Segment (B) section/pathway/polyline, 
    then the following steps are carried out: 
    1) PipeLine/Segment B is split closest to the PipeLine/Segment A start/end point, 
    2) PipeLine/Segment A endpoint is extended to connect to that newly created above node.
    This only works for PipeLines/Segments, that are Polylines, hence have many LatLong pairs
    along its path."""


    RetPipeLines = []
    
    # making helper matrix
    LatLongPos      = []
    PipePos         = []
    PipeNum         = []
    NodeIDAdd       = []
    NodeDist        = []
    NumLatVals      = []
    ShortNodeID     = []
    ShortLatLong    = K_Component.PolyLine(lat = [], long = [])

        
    Pipe    = Netz.__dict__[compName]
    
    # 0. Pre-Processing for later:
    #    getting list of all lat/long Start/End points
        
    
    # Creation of latlong for all pipeline points
    # Creation of EndStart & EndEnd
    ShortLatLong, ShortLat, ShortLong, ShortPosStart, ShortPosEnd, ShortNodeID, ShortNodeID_Count, ShortPipeID, PipeLength  = getShortLatLong(Pipe)
    PolyLatLong, PolyPipeNum, PolyLatNum                                        = getPolyLatLong(Pipe)
    CountNode                                                                   = countSameLatLong(ShortLatLong)
    

    # 1. Check if node could be joined to an existing pipeline point
    # if so, then change latlon of pipeline point
    for idx in range(0,len(ShortLat)):
        if (CountNode[idx] >= 1):
            thisLatLong         = K_Component.PolyLine(lat = ShortLat[idx], long = ShortLong[idx])
            thisPosStart        = ShortPosStart[idx]
            thisPosEnd          = ShortPosEnd[idx]
            thisLat             = []
            thisLong            = []
            
            # Creating PipeLatLong, where pipeline of question id removed.
            # Prep
            for jj in range(thisPosStart, thisPosEnd+1):
                thisLat.append(PolyLatLong.lat[jj])
                thisLong.append(PolyLatLong.long[jj])
                PolyLatLong.lat[jj]     = -999
                PolyLatLong.long[jj]    = -999
            
            # Find closest latlong to pipe end
            [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, PolyLatLong)
            # reverting prep
            for jj in range(thisPosStart, thisPosEnd+1):
                thisLat.append(PolyLatLong.lat[jj])
                thisLong.append(PolyLatLong.long[jj])
                PolyLatLong.lat[jj]     = thisLat[jj - thisPosStart]
                PolyLatLong.long[jj]    = thisLong[jj - thisPosStart]

            # Chancing end point of PipeLine/Segment
#            if (minVal > 0.0) and (minVal < maxDistance) and ShortNodeID_Count[ii] == 1 and PipeLength[ii] > maxDistance:
            if (minVal > 0.0) and (minVal < maxDistance) and PipeLength[idx] > maxDistance:
                if len(PipePos) == 0:
                    # This is first time round having found a join
                    Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                    Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                    
                    # keepign track of where pipelinepoint where changed due to node
                    PipePos.append(PolyPipeNum[distPos])
                    LatLongPos.append(PolyLatNum[distPos])
                    NodeIDAdd.append(ShortNodeID[idx])
                    NodeDist.append(minVal)
                    NumLatVals.append(distPos)
                    PipeNum.append(ShortPipeID[idx])
                
                else:
                    if PipePos[-1] != PolyPipeNum[distPos]:
                        Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                        Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                        # keepign track of where pipelinepoint where changed due to node
                        PipePos.append(PolyPipeNum[distPos])
                        LatLongPos.append(PolyLatNum[distPos])
                        NodeIDAdd.append(ShortNodeID[idx])
                        PipeNum.append(ShortPipeID[idx])
                        NodeDist.append(minVal)
                        NumLatVals.append(distPos)
                        
                    elif NodeDist[-1] > minVal:
                        Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                        Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                        # keepign track of where pipelinepoint where changed due to node
                        PipePos[-1]     = PolyPipeNum[distPos]
                        LatLongPos[-1]  = PolyLatNum[distPos]
                        NodeIDAdd[-1]   = ShortNodeID[idx]
                        NodeDist[-1]    = minVal
                        NumLatVals[-1]  = distPos
                        
                    elif len(M_FindPos.find_pos_ValInVector(ShortPipeID[idx], PipeNum, '==')) == 0:
                        # In case that this pipe has not been connected at all yet to another pipeline
                        Pipe[PolyPipeNum[distPos]].lat[PolyLatNum[distPos]]    = thisLatLong.lat
                        Pipe[PolyPipeNum[distPos]].long[PolyLatNum[distPos]]   = thisLatLong.long
                        # keepign track of where pipelinepoint where changed due to node
                        PipePos.append(PolyPipeNum[distPos])
                        LatLongPos.append(PolyLatNum[distPos])
                        NodeIDAdd.append(ShortNodeID[idx])
                        NodeDist.append(minVal)
                        NumLatVals.append(distPos)
    
    
    # 2. Breaking up PipeLines, that contain a new Node
    for idx, pipe_ in enumerate(Pipe):
        pos = M_FindPos.find_pos_ValInVector(idx, PipePos,  '==')

        if len(pos) > 0:
            # creation of LatLong of pipe
            allLat                  = Pipe[idx].lat
            allLong                 = Pipe[idx].long
            
            # More than ONE node on Pipe
            thislatlongpos = []
            for pp in pos:
                thislatlongpos.append(LatLongPos[pp])
            thislatlongpos.sort()
            
            # Adding start and end point to list
                
            if thislatlongpos[-1] != len(allLong)-1:
                thislatlongpos.append(len(allLong)-1)

            if thislatlongpos[0] != 0:
                thislatlongpos.append(0)
            thislatlongpos.sort()
            
            # Sorting of break points
            for ss in range(len(thislatlongpos) - 1 ):
                pipe           = copy.deepcopy(Pipe[idx])
                pipe.lat       = allLat[ thislatlongpos[ss] : thislatlongpos[ss + 1] + 1]
                pipe.long      = allLong[thislatlongpos[ss] : thislatlongpos[ss + 1] + 1]
                pipe.param.update({'breakLine': 1})
                RetPipeLines.append(pipe)
                if len(pipe.long) == 1:
                    pipe.long = pipe.long
            
        # No extra node found, take existing Pipe
        else:
            Pipe[idx].param.update({'breakLine': 0})
            RetPipeLines.append(Pipe[idx])
            if len(Pipe[idx].long) == 1:
                Pipe[idx].long = Pipe[idx].long
            
    # Now assining the all pipelines back to netz.
    Netz.__dict__[compName] = RetPipeLines
    
    # 3. Giving pipes correct node_id s
    # Now reducing the Nodes based on changed PipeLines/Segments
    roundVal        = 6
    NodesID         = []
    NodesLatLong    = K_Component.PolyLine(lat = [], long = [])
    for nn in Netz.Nodes:
        NodesLatLong.lat.append(round(nn.lat, roundVal))
        NodesLatLong.long.append(round(nn.long, roundVal))
        NodesID.append(nn.id)


    for idx, pipe in enumerate(Netz.__dict__[compName]):
        thisLatLong         = K_Component.PolyLine(lat = round(pipe.lat[0], roundVal), long = round(pipe.long[0], roundVal))
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
        Netz.__dict__[compName][idx].node_id[0] = NodesID[distPos]

        thisLatLong         = K_Component.PolyLine(lat = round(pipe.lat[-1], roundVal), long = round(pipe.long[-1], roundVal))
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
        Netz.__dict__[compName][idx].node_id[-1] = NodesID[distPos]


    return Netz






def addNodes2PipeLines(Netz, compName, posNodes = [], maxDistance = 0.0):
    """Adding of Nodes to PipeLines **PipeLines**, so that only coordinates 
    that are in **Nodes** are also in PipeLines. No LatLongs will be removed.  
    **maxDistance** specifies, how far pipeline LatLongs are allowed to be away 
    from the Nodes.  
    """
    # Initialization
    RetPipeLines    = []
    PipePos         = []
    LatLongPos      = []
    PipeCount       = 0
    NotFoundCount   = 0
    
    # Check that entry values are all given
    if len(posNodes) == 0:
        return Netz
    
    # making helper matrix
    PipeLines   = Netz.__dict__[compName]
    Nodes       = Netz.Nodes
    
    _, _, _, _, PipeNum, LatNum, PipeLatLong, _  = getLatLongVectors(PipeLines)

    
    # Creation of latlong for all pipeline points
    for ii in range(len(PipeLines)):
        for jj in range(len(PipeLines[ii].lat)):
            PipeNum.append(ii)
            LatNum.append(jj)
            PipeLatLong.lat.append( PipeLines[ii].lat[jj])
            PipeLatLong.long.append(PipeLines[ii].long[jj])
            
    
    # for each node, check if it could be joined to an existing pipeline point
    # if so, then change latlon of pipeline point
    for ii in range(len(posNodes)):
        node                = Nodes[posNodes[ii]]
        thisLatLong         = K_Component.PolyLine(lat = node.lat, long = node.long)
        [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, PipeLatLong)
        
        if minVal > maxDistance:
            #print('Node not close enough: ' + node.id)
            NotFoundCount = NotFoundCount + 1
        else:
            PipeLines[PipeNum[distPos]].lat[LatNum[distPos]]    = thisLatLong.lat
            PipeLines[PipeNum[distPos]].long[LatNum[distPos]]   = thisLatLong.long
            # keepign track of where pipelinepoint where changed due to node
            PipePos.append(PipeNum[distPos])
            LatLongPos.append(LatNum[distPos])

    [sortedPipePos, pospos] = M_MatLab.sort_Vector(PipePos)
    
    if NotFoundCount == 0:
        print('addNodes2PipeLines: All Sites have closest Pipeline. Tick')
    else:
        print('addNodes2PipeLines: Number of Sites not connected: ' + str(NotFoundCount))
    
    # Breaking up PipeLines, that contain a new Node
    for ii, pipe_ in enumerate(PipeLines):
        pos = M_FindPos.find_pos_ValInVector(ii, PipePos,  '==')
        if len(pos) > 0:
            # creation of LatLong of pipe
            allLat                  = PipeLines[ii].lat
            allLong                 = PipeLines[ii].long
            
            # More than ONE node on pipeline
            thislatlongpos = []
            for pp in pos:
                thislatlongpos.append(LatLongPos[pp])
                
            # Adding start and end point to list
            thislatlongpos.append(0)
            thislatlongpos.append(len(allLong)-1)
            # Sorting of break points
            thislatlongpos = sorted(thislatlongpos)
            
            for ss in range(len(thislatlongpos) - 1 ):
#            for a, b in zip(thislatlongpos[:-1], thislatlongpos[1:]):
                pipe                    = copy.deepcopy(PipeLines[ii])
                pipe.id                 = str(PipeCount)
                pipe.node_id            = [str(PipeCount)]
                source_id               = PipeLines[ii].source_id[0]
                source_id               = changeString(source_id, '_', str(PipeCount))
                pipe.source_id          = [source_id]
                pipe.lat                = allLat[ thislatlongpos[ss] : thislatlongpos[ss + 1] + 1]
                pipe.long               = allLong[thislatlongpos[ss] : thislatlongpos[ss + 1] + 1]
                pipe.param['breakLine'] = 1
                RetPipeLines.append(pipe)
                PipeCount               = PipeCount + 1
                    
            
        # No extra node found, take existing pipeline
        else:
            PipeLines[ii].id                    = str(PipeCount)
            PipeLines[ii].node_id               = [str(PipeCount)]
            source_id                           = PipeLines[ii].source_id[0]
            source_id                           = changeString(source_id, '_', str(PipeCount))
            PipeLines[ii].source_id             = [source_id]
            PipeLines[ii].param['breakLine']    = 0
            RetPipeLines.append(PipeLines[ii])
            PipeCount                           = PipeCount + 1
        
    Netz.__dict__[compName] = RetPipeLines
    return Netz





    
def changeString(InStr, Marker, NewStr):
    
    RetStr  = []
    
    pos     = M_FindPos.find_pos_CharInStr(Marker, InStr)
    
    RetStr  = InStr[0:pos[-1]+1] + NewStr
    
    return RetStr







def shrinkPipes(Netz, compName ):
    """Removing all LatLlongs from PipeLine/Segment, except first and last
    """

    PipeLines = Netz.__dict__[compName]
    for idx, pipe in enumerate(PipeLines):
        if len(Netz.__dict__[compName][idx].lat)> 2:
            Netz.__dict__[compName][idx].lat    = [Netz.__dict__[compName][idx].lat[0],  Netz.__dict__[compName][idx].lat[-1]]
            Netz.__dict__[compName][idx].long   = [Netz.__dict__[compName][idx].long[0], Netz.__dict__[compName][idx].long[-1]]
                
    
    Netz.Nodes = reduceElement(Netz.Nodes, reduceType = 'LatLong')

    
    return Netz






def shrinkPipeLine2Nodes(PipeLines, Nodes):
    """Removing all LatLlongs polyline paris from a PipeLines/Segment, that are not Nodes.
    """
    RetPipeLines    = []
    NodesLatLong    = K_Component.PolyLine(lat = [], long = [])
    for ii in range(len(Nodes)):
        NodesLatLong.lat.append( Nodes[ii].lat)
        NodesLatLong.long.append(Nodes[ii].long)


    for pipe in PipeLines:
        if len(pipe.lat) > 2:
            posKeep = []
            for ii in range(len(pipe.lat)):
                thisLatLong         = K_Component.PolyLine(lat = pipe.lat[ii], long = pipe.long[ii])
                [distPos, minVal]   = M_FindPos.find_pos_closestLatLongInList(thisLatLong, NodesLatLong)
                
                # check if distance 0.0, then node point
                if minVal == 0.0:
                    posKeep.append(ii)
                    
            # remove all latlongs 
            if len(posKeep) == 0:
                pipe.lat    = [pipe.lat[0],  pipe.lat[-1]]
                pipe.long   = [pipe.long[0], pipe.long[-1]]
                RetPipeLines.append(pipe)
                
            # split up pipeLine
            else:
                # Adding Start and End
                posKeep.append(0)
                posKeep.append(len(pipe.long)-1)
                posKeep = sorted(posKeep)
                # Grabbing lat long
                lat     = pipe.lat
                long    = pipe.long
                # assigning new latlong, and then adding as pipe
                for ii in range(len(posKeep)-1):
                    pipe.lat     = [lat[posKeep[ii]],  lat[posKeep[ii+1]]]
                    pipe.long    = [long[posKeep[ii]], long[posKeep[ii+1]]]
                    RetPipeLines.append(pipe)
                    
        # Nothing to do, pipeline only has two points
        else:
            RetPipeLines.append(pipe)
    
    
    
    return RetPipeLines




def reduceElement(Elements, reduceType = 'LatLong', exceptNodes = [], makeUnique = False):
    """ Function to reduce elements of a component that are the same, e.g. same Nodes.  Element supplied 
    via **Elements** and type of reduction process supplied via **reduceType**.
    
    \n.. comments: 
    Input:    
        Elements:       List of elements to be reduced.
        reduceType      String containing name of reduction type
                        (default = 'LatLong')
        exceptNodes     List of nodes, that are also part of the output list of nodes.
                        (default = [])
    """
    roundNum    = 4
    
    # Type of reduction method LatLong
    if reduceType == 'LatLong':
        # Generation of list of all latlong
        LatLong = K_Component.PolyLine(lat = [], long = [])
        for elem in Elements:
            LatLong.lat.append(M_MatLab.roundNone(elem.lat, roundNum))
            LatLong.long.append(M_MatLab.roundNone(elem.long, roundNum))
        
        # Now go through and find doubles
        ii = 0
        while ii < len(LatLong.lat):
            thisLatLong = [M_MatLab.roundNone(LatLong.long[ii], roundNum), M_MatLab.roundNone(LatLong.lat[ii], roundNum)]
            pos         = M_FindPos.find_pos_LatLongInPoly(thisLatLong, LatLong, Type = '==')
            if len(pos) == 1:
                pasVall = True
                if isinstance(Elements[pos[0]].node_id, list):
                    for tt in Elements[pos[0]].node_id:
                         if tt in exceptNodes:
                             pasVall  = False
                else:
                    if Elements[pos[0]].node_id in exceptNodes:
                        pasVall = False
                        
                if pasVall :
                    for jj in range(len(pos)-1, 0, -1):
                        thisPos = pos.pop(jj)
                        Elements.pop(thisPos)
                        LatLong.lat.pop(thisPos)
                        LatLong.long.pop(thisPos)
            elif len(pos) > 1:
                for pp in pos:
                    pasVall = True
                    if isinstance(Elements[pp].node_id, list):
                        for tt in Elements[pp].node_id:
                             if tt in exceptNodes:
                                 pasVall  = False
                    else:
                        if Elements[pp].node_id in exceptNodes:
                            pasVall = False
                            
                if pasVall :
                    for jj in range(len(pos)-1, 0, -1):
                        thisPos = pos.pop(jj)
                        Elements.pop(thisPos)
                        LatLong.lat.pop(thisPos)
                        LatLong.long.pop(thisPos)
                
                
            else:
                print('reduceElement, not enough:', ii)
            ii = ii + 1
        
    # Other option not found
    else:
        print('ERROR: M_Shape.reduceElement: Code not written yet.')
    
    if makeUnique == True:
        # Renaming Nodes ids
        count = 0
        for nod in Elements:
            nod.id = 'N_' + str(count)
            nod.node_id = ['N_' + str(count)]
            count = count + 1

    return Elements




def getShortLatLong(Comps):
    """ Function to return a list of variables used by other functions.
    **Comps** are the list of components of interest, and the following 
    lists are being returned: EndLat, EndLong, EndStart, EndEnd, PipeNum, 
    LatNum, PipeLatLong, NodeID.
    """
    
    NodeID      = []
    PipeID      = []
    EndLat      = []
    EndLong     = []
    EndStart    = []
    EndEnd      = []
    NodeID_Count = []
    PipeLength  = []
    PipeLatLong = K_Component.PolyLine(lat = [], long = [])
    ShortLatLong = K_Component.PolyLine(lat = [], long = [])
    
    
    if len(Comps)>0:
        if type(Comps[0].lat) == list:
        
            # For lists
            for ii in range(len(Comps)):
                # Positions of pipelineLatLong in PipeLatLong
                EndStart.append(len(PipeLatLong.lat))
                EndStart.append(len(PipeLatLong.lat))
                EndEnd.append(len(PipeLatLong.lat) + len(Comps[ii].lat) - 1)
                EndEnd.append(len(PipeLatLong.lat) + len(Comps[ii].lat) - 1)
                
                EndLat.append(Comps[ii].lat[0])
                EndLat.append(Comps[ii].lat[-1])
                EndLong.append(Comps[ii].long[0])
                EndLong.append(Comps[ii].long[-1])
                NodeID.append(Comps[ii].node_id[0])
                NodeID.append(Comps[ii].node_id[-1])
                PipeLength.append(Comps[ii].param['length'])
                PipeLength.append(Comps[ii].param['length'])
                PipeID.append(Comps[ii].id)
                PipeID.append(Comps[ii].id)
        
                for jj in range(len(Comps[ii].lat)):
                    PipeLatLong.lat.append( Comps[ii].lat[jj])
                    PipeLatLong.long.append(Comps[ii].long[jj])
                    
                ShortLatLong.lat.append(Comps[ii].lat[0])
                ShortLatLong.lat.append(Comps[ii].lat[-1])
                ShortLatLong.long.append(Comps[ii].long[0])
                ShortLatLong.long.append(Comps[ii].long[-1])
        # For indevidual values
        else:
            for ii in range(len(Comps)):
                # Positions of pipelineLatLong in PipeLatLong
                EndStart.append(len(PipeLatLong.lat))
                EndEnd.append(len(PipeLatLong.lat))
                
                EndLat.append(Comps[ii].lat)
                EndLong.append(Comps[ii].long)
                if isinstance(Comps[ii].node_id, list):
                    NodeID.append(Comps[ii].node_id[0])
                else:
                    NodeID.append(Comps[ii].node_id)

                PipeID.append(Comps[ii].id)
                PipeLength.append(Comps[ii].param['length'])
        
                PipeLatLong.lat.append( Comps[ii].lat)
                PipeLatLong.long.append(Comps[ii].long)
            
                ShortLatLong.lat.append(Comps[ii].lat)
                ShortLatLong.long.append(Comps[ii].long)
    
        pipeID = []
        for pp in Comps:
            pipeID.append(pp.node_id[0])
            pipeID.append(pp.node_id[-1])
            
        for id in NodeID:
            pos = M_FindPos.find_pos_StringInList(id, pipeID)
            NodeID_Count.append(len(pos))
            
    return ShortLatLong, EndLat, EndLong, EndStart, EndEnd, NodeID, NodeID_Count, PipeID, PipeLength




def getPolyLatLong(Comps):
    """ Function to return a list of variables used by other functions.
    **Comps** are the list of components of interest, and the following 
    lists are being returned: EndLat, EndLong, EndStart, EndEnd, PipeNum, 
    LatNum, PipeLatLong, NodeID.
    """
    
    
    NodeID      = []
    EndStart    = []
    EndEnd      = []
    PipeNum     = []
    LatNum      = []
    PipeLatLong = K_Component.PolyLine(lat = [], long = [])
    
    
    
    if len(Comps)>0:
        if type(Comps[0].lat) == list:
        
            # For lists
            for ii in range(len(Comps)):
                # Positions of pipelineLatLong in PipeLatLong
                EndStart.append(len(PipeLatLong.lat))
                EndStart.append(len(PipeLatLong.lat))
                EndEnd.append(len(PipeLatLong.lat) + len(Comps[ii].lat) - 1)
                EndEnd.append(len(PipeLatLong.lat) + len(Comps[ii].lat) - 1)
                
                NodeID.append(Comps[ii].node_id[0])
                NodeID.append(Comps[ii].node_id[-1])
        
                for jj in range(len(Comps[ii].lat)):
                    PipeNum.append(ii)
                    LatNum.append(jj)
                    PipeLatLong.lat.append( Comps[ii].lat[jj])
                    PipeLatLong.long.append(Comps[ii].long[jj])
                    
        # For indevidual values
        else:
            for ii in range(len(Comps)):
                # Positions of pipelineLatLong in PipeLatLong
                EndStart.append(len(PipeLatLong.lat))
                EndEnd.append(len(PipeLatLong.lat))
                
                if isinstance(Comps[ii].node_id, list):
                    NodeID.append(Comps[ii].node_id[0])
                else:
                    NodeID.append(Comps[ii].node_id)
        
                PipeNum.append(ii)
                LatNum.append(0)
                PipeLatLong.lat.append( Comps[ii].lat)
                PipeLatLong.long.append(Comps[ii].long)
            

    
    
    
    
    return PipeLatLong, PipeNum, LatNum                                        




def getLatLongVectors(Comps):
    """ Function to return a list of variables used by other functions.
    **Comps** are the list of components of interest, and the following 
    lists are being returned: EndLat, EndLong, EndStart, EndEnd, PipeNum, 
    LatNum, PipeLatLong, NodeID.
    """
    
    NodeID      = []
    EndLat      = []
    EndLong     = []
    EndStart    = []
    EndEnd      = []
    PipeNum     = []
    LatNum      = []
    PipeLatLong = K_Component.PolyLine(lat = [], long = [])
    
    
    
    if len(Comps)>0:
        if type(Comps[0].lat) == list:
        
            # For lists
            for ii in range(len(Comps)):
                # Positions of pipelineLatLong in PipeLatLong
                EndStart.append(len(PipeLatLong.lat))
                EndStart.append(len(PipeLatLong.lat))
                EndEnd.append(len(PipeLatLong.lat) + len(Comps[ii].lat) - 1)
                EndEnd.append(len(PipeLatLong.lat) + len(Comps[ii].lat) - 1)
                
                EndLat.append(Comps[ii].lat[0])
                EndLat.append(Comps[ii].lat[-1])
                EndLong.append(Comps[ii].long[0])
                EndLong.append(Comps[ii].long[-1])
                if isinstance(Comps[ii].node_id, list):
                    NodeID.append(Comps[ii].node_id[0])
                    NodeID.append(Comps[ii].node_id[-1])
                else:
                    NodeID.append(Comps[ii].node_id)
                    NodeID.append(Comps[ii].node_id)

        
                for jj in range(len(Comps[ii].lat)):
                    PipeNum.append(ii)
                    LatNum.append(jj)
                    PipeLatLong.lat.append( Comps[ii].lat[jj])
                    PipeLatLong.long.append(Comps[ii].long[jj])
                    
        # For indevidual values
        else:
            for ii in range(len(Comps)):
                # Positions of pipelineLatLong in PipeLatLong
                EndStart.append(len(PipeLatLong.lat))
                EndEnd.append(len(PipeLatLong.lat))
                
                EndLat.append(Comps[ii].lat)
                EndLong.append(Comps[ii].long)
                if isinstance(Comps[ii].node_id, list):
                    NodeID.append(Comps[ii].node_id[0])
                else:
                    NodeID.append(Comps[ii].node_id)
        
                PipeNum.append(ii)
                LatNum.append(0)
                PipeLatLong.lat.append( Comps[ii].lat)
                PipeLatLong.long.append(Comps[ii].long)
            

    return EndLat, EndLong, EndStart, EndEnd, PipeNum, LatNum, PipeLatLong, NodeID




def fixAdjacent(thisLatLongPos):
    
    
    return thisLatLongPos  