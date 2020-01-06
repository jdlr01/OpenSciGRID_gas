# -*- coding: utf-8 -*-
"""
M_Visuell
---------
"""

#conda install git pip
#pip install git+git://github.com/mpld3/mpld3

#%matplotlib notebook
import matplotlib.pyplot   as plt
import matplotlib.lines    as lines
import Code.C_colors       as CC
import numpy               as np
from descartes         import PolygonPatch

from itertools         import cycle
from pathlib           import Path
from adjustText        import adjust_text
import json
import os,sys

import itertools
import mplcursors
import shapefile #pyshp

#other functions from Jan are currently in
from Code.M_Plots import *


def colorwheel(color):
    """
    Maps color to html color
    if color = colorwheel, it rotates through colors for each call
    """
    colors = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
    
    colordict={"t":'#597DFF',"o":'#C76730',"v":'#728C00',"r":"#FF0000","g":"#00CD00","mustard":'#FFDB58',"lime":'#E3FF00',"b":'#1022ff', 'y':'#ffed10', 'k':'000000'}
    if color =="colorwheel":
        return next(colors)
    if color in colordict:
        return colordict[color]
    else:
        return color


def get_bounding_box(countrycode):
    """
    called by PlotMap
    boundingboxes for all countries by official 2-digit countrycode
    can be used to set xlim, ylim of the European map in plots
    """
    if countrycode != None:
        if sys.platform == 'win32':
            RelDirName      = 'Code/'
            dataFolder      = Path.cwd()
            filename        = dataFolder /  RelDirName
            json_data       = str(filename / 'bounding-boxes.json')
        else:
            json_data=os.getcwd()+os.path.realpath("/Code/bounding-boxes.json")
            
            
        with open(json_data,'r') as f:
            box = json.load(f)
            result=box[countrycode][1]
    else:
        result = []
        

    return result




def PlotMap(countrycode = "EU", figureNum = 1, MapColor = True, SupTitleStr = ''):
    """
    Plotting contour of Country or Europe
    """
    fig = plt.figure(figureNum, figsize = (12.5,8.5),facecolor=('#FFFFFF'))
    ax  = fig.gca()
    if countrycode != None:
        if sys.platform == 'win32':
            RelDirName      = 'Eingabe/GraphischeDaten/'
            dataFolder      = Path.cwd()
            filename        = dataFolder /  RelDirName
            FileName_Map    = str(filename / 'TM_WORLD_BORDERS-0.3.shp')
        else:
            FileName_Map     = os.path.join(os.getcwd(),'Eingabe/GraphischeDaten/TM_WORLD_BORDERS-0.3.shp')
            
        sf = shapefile.Reader(FileName_Map)
        
        if MapColor == False:
            ax.set_facecolor('xkcd:light grey')
            countrycolors = itertools.cycle(['#ffffff'])
        else:
            countrycolors = itertools.cycle(['#ffffe5',
                                             '#c7e9c0',
                                             '#F5FFFA',
                                             '#f7fcf5',
                                             '#a8ddb5',
                                             '#F8F8FF',
                                             '#FFF5EE',
                                             '#FFEFD5',
                                             '#eafff5',
                                             '#e5f5e0'])
            ####old color 
            ax.set_facecolor('#f7fbff')

        for poly in sf.shapes():
            poly_geo=poly.__geo_interface__
            ax.add_patch(PolygonPatch(poly_geo, fc=next(countrycolors), ec='#000000', alpha=1, zorder=0,linewidth=0.25))
                           
        [xmin,ymin,xmax,ymax]=get_bounding_box(countrycode)
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.set_xlabel("long [°]")
        ax.set_ylabel("lat [°]")
        plt.xticks(np.arange(xmin,xmax , 2.0))
        plt.yticks(np.arange(ymin,ymax , 2.0))
        if len(SupTitleStr) > 0:
            plt.suptitle(SupTitleStr)

    return fig,ax


def PlotPoints(fig,ax,elements,cursor=False, cursor_data='', Size='', Symbol = '', 
               color = '', fontsize = '', legend = '_nolegend_', alpha='', 
               names ='', Info=[], selectList = []):
    
    cursor_data={'point': {}, 'line': {}}
    Size      = Info.get('Size',15)            if Size      == '' else Size
    Symbol    = Info.get('Symbol','.')         if Symbol    == '' else Symbol    
    color     = Info.get('color','b')          if color     == '' else color
    alpha     = Info.get('alpha',1)            if alpha     == '' else alpha
    names     = Info.get('names',False)        if names     == '' else names
    names     = bool(names == 'True' or names == True)
    fontsize  = Info.get('fontsize',13)        if fontsize  == '' else fontsize 
    [long,lat,labels] = elements   

    y = np.array(lat)
    x = np.array(long)
    if selectList != []:
        x = x[selectList]
        y = y[selectList]
    
    ma=plt.scatter(x, y, s = int(Size), marker = Symbol, edgecolor = 'black',
                   linewidths = 0.5, c = colorwheel(color), zorder = 3, alpha = int(alpha), label = legend)
    
    if legend != "_nolegend_":
        ax.legend()
    
    npx         = np.asarray(x, dtype=np.float32)
    npy         = np.asarray(y, dtype=np.float32)
    nplabels    = np.asarray(labels, dtype=np.str)
    nanlist     =np.argwhere(np.isnan(npx))
    nplabels    = np.delete(nplabels,nanlist)
    npx         = np.delete(npx,nanlist)
    npy         = np.delete(npy,nanlist)

    if names == True:
                texts = [plt.text(npx[i], npy[i], nplabels[i], fontsize = fontsize,ha='center', va='center') for i in range(len(npx))]
                adjust_text(texts)
                
    
    #if cursor_data != '':
    cursor_data["point"].update({ma:nplabels})
    if cursor==True:
        PlotCursor(cursor_data,multiple=False,hover=False)
    return 


def PlotLines(fig, ax, elements, PlotOptions = '', cursor_data = 'deactivate', linewidth = '', 
              color = "colorwheel", legend = "_nolegend_",
              alpha = 1, Info = [], selectList = []):
    colortmp=color
    alpha      = float(Info.get('alphalines',1))  if alpha      == '' else float(alpha)
    linewidth  = float(Info.get('linewidth','0.8'))   if linewidth  == '' else linewidth
    
    for count, element in enumerate(elements):
        # plot line if requested or none selected
        if count in selectList  or selectList == []:
            x       = element[0]
            y       = element[1]
            label   = str(element[2])
            l       = lines.Line2D(x,y, 
                                   color     = colorwheel(colortmp),
                                   linewidth = linewidth,
                                   label     = legend,
                                   alpha     = alpha)
            ax.add_line(l)
            legend  = "_nolegend_"
            if cursor_data!='' and cursor_data!='deactivate':
                cursor_data.get("line").update({l:label})
    if legend != '_nolegend_':
        ax.legend()
    return


def PlotCursor(cursor_data,multiple,hover):
    """
    Allows to show underlying data by clicking on the map, currently works only for node objects
    and only for a very small set of Pipelines.
    
    Parameters
    ----------
    cursor_data : Data you wish to hover
    multiple : If false only one hover at the same time
    hover : Boolean

    Returns
    -------
    None.
    """
    
    
    
    pointlist  = list(cursor_data["point"].keys())
    linelist   = list(cursor_data["line"].keys())
    cursorlist = pointlist+linelist
    cursor     = mplcursors.cursor(cursorlist,multiple = False,hover = False)
    
    @cursor.connect("add")
    def on_add(sel):
        if sel.artist in pointlist:
             text = cursor_data["point"][sel.artist][sel.target.index]
        elif sel.artist in linelist:
            text = cursor_data["line"][sel.artist]
            
        sel.annotation.set_text(text)
        sel.annotation.get_bbox_patch().set(fc = "white")
        sel.annotation.arrow_patch.set(arrowstyle = "simple", 
                                       fc         = "white", 
                                       alpha      = .5)
    return


def getLegendStr(LegendStyle, key, Num=0):
    '''Creation of the legend string, based on **LegendStyle** value
    
    '''
    
    if LegendStyle.lower() == 'Str'.lower():
        LegendString = str(key)
    elif LegendStyle.lower() == 'Str(Num)'.lower():
        LegendString = str(key) + ' (' + str(Num) +  ')'
    else:
        LegendString = '_nolegend_'
        
    return LegendString 

def SaveFig(fname,dpi=600):
    """
    use plt.savefig for quickplot
    
    Parameters
    ----------
    fname : namepathstring of save file
    """
    
    plt.savefig(fname, dpi = None, facecolor='w', edgecolor   ='w',
                                                  orientation = 'portrait', 
                                                  papertype   = None,
                                                  format      = None,
                                                  transparent = False,
                                                  bbox_inches = None,
                                                  pad_inches  = 0.1,
                                                  frameon     = None, 
                                                  metadata    = None)
    return



    """
    """
    
    '''
    Plotting K_netze Object
    You can add "all" to IgnoreList which will only plot the items in named in PlotList
    
    Info:  optional customisation via Setup/InfoVisuell.ini
           Parameter override parameter defined in Setupfile
    Sample:
           quickplot(Netz_1)
           quickplot(Netz_1,Info=InfoVisuell['Quickplot'],RandomColorsMarkers=True,
                     IgnoreList=['Nodes',],Names=True)
    '''


def quickplot(Netz, 
              Info='', 
              Names=False, 
              alpha=1, 
              SingleColor='', 
              SingleMarker    = '',
              SingleLineWidth = '',
              tagstyle        = 1,
              Cursor          = False, 
              SingleLabel     = '', 
              SingleSize      = '', 
              SingleAlpha     = '', 
              savefile        = '', 
              PlotList        = [] ,
              IgnoreList      = ['PipePoints',
                                 'GasFlowData',
                                 'Processes',
                                 'Nodes',
                                 'SourceName'],
              MapColor        = True, 
              countrycode     = 'EU', 
              GridOn          = False,
              figureNum       = 1, 
              Save            = False, 
              save_dpi        = 300,
              SupTitleStr     = '', 
              LegendStyle     = 'Str', 
              selectList      = [], 
              LegendStr       = '_nolegend_'):
    """
    Creates Plot of Netz-Class object
    
    Parameters
    ----------
    Info            = Info object to customize quickplot 
    Names           = False, 
    alpha           = 1, 
    
    SingleColor     = str , same as in Matplotlib
    SingleMarker    = str , same as in Matplotlib
    SingleLineWidth = str , same as in Matplotlib
    SingleLabel     = str , same as in Matplotlib
    SingleSize      = str , same as in Matplotlib
    SingleAlpha     = str , same as in Matplotlib
    
    tagstyle        = int=1,2,3 or 4, how much details mpl cursor shows 
    Cursor          = boolean, if true you can get details on mouseover 
    savefile        = str, namepath
    PlotList        = List of plotable NetClass.Elements (e.g. Nodes, Pipelines)
    IgnoreList      = List of ignorable NetClass.Elements (e.g. Nodes, PipeLines)
    MapColor        = boolean, get background map in color or in blackwhite 
    countrycode     = str of 2-digit countrycode - will be used for the basemap
    GridOn          = boolean
    figureNum       = int
    Save            = boolean
    save_dpi        = int
    SupTitleStr     = str
    LegendStyle     = 'Str' or 'Str(Num)'
    LegendStr       = '_nolegend_'):
    selectList      = List of string, Netclass Elements, that should be hovered
    """

    import configparser
    import Code.M_PlotObjects      as PO
    from itertools             import cycle
    from pathlib               import Path

    Setup_Visuell   = Path(os.getcwd() + '/Setup/Setup_Visuell.ini')
    InfoVisuell     = configparser.ConfigParser()
    InfoVisuell.read(Setup_Visuell)
    Info            = InfoVisuell['Quickplot']  if Info  == '' else Info

    if countrycode == None:
        savefile  = str(Info.get('savefile',os.getcwd()+'/Ausgabe/Plots/Quickplot.pdf')) if savefile  == '' else savefile
    else:
        savefile  = str(Info.get('savefile',os.getcwd()+'/Ausgabe/Plots/Quickplot_'
                             +countrycode+'.pdf')) if savefile  == '' else savefile

    
    FigNum1     = [fig, ax] = PlotMap(countrycode = countrycode, 
                                     figureNum   = figureNum, 
                                     MapColor    = MapColor, 
                                     SupTitleStr = SupTitleStr)
    if Netz == None:
        keys        = []
    else:
        keys        = list(Netz.__dict__.keys())
        
        
    linekeys    = ['PipeSegments', 'PipeLines','PipeLines2',
                   'PipeLines3','Compressors_Lines','SeaMarkers']
    
    colors      = cycle(['b', 'g', 'r', 'm', 'c', 'y', 'k'])
    markers     = cycle(['o', 'x', '+', 'P', 'D', 's', '^'])
    
    size_default= 18
    line_size_default=1
    if SingleSize !='' :
        size=SingleSize
        
    if SingleLineWidth !='' :
        line_size_default=SingleLineWidth
        
    small = 20
    cursor_data={'point': {}, 'line': {}}
    custom={'BorderPoints':         {'color':'k', 'marker':'o', 'size':10},
            'Compressors':          {'color':'r', 'marker':'o', 'size':20},
            'Compressors_Lines':    {'color':'r', 'marker':'u', 'size':4*line_size_default},
            'SeaMarkers':           {'color':'m', 'marker':'u', 'size':2*line_size_default},
            'Markers':              {'color':'y', 'marker':'P', 'size':size_default},
            'ConnectionPoints':     {'color':'g', 'marker':'+', 'size':size_default},
            'Consumers':            {'color':'m', 'marker':'P', 'size':size_default},
            'EntryPoints':          {'color':'y', 'marker':'d', 'size':45},
            'InterConnectionPoints':{'color':'w', 'marker':'o', 'size':25},
            'LNGs':                 {'color':'b', 'marker':'v', 'size':38},
            'Nodes':                {'color':'r', 'marker':'.', 'size':10}, 
            'PipeLines':            {'color':'steelblue', 'marker':'u', 'size':line_size_default},
            'PipeLines2':           {'color':'g', 'marker':'u', 'size':line_size_default},
            'PipeLines3':           {'color':'b', 'marker':'u', 'size':line_size_default},
            'PipePoints':           {'color':'c', 'marker':'P', 'size':line_size_default},
            'PipeSegments':         {'color':'steelblue', 'marker':'D', 'size':line_size_default},
            'Processes':            {'color':'k', 'marker':'s', 'size':size_default},
            'Productions':          {'color':'b', 'marker':'^', 'size':size_default},
            'Storages':             {'color':'k', 'marker':'^', 'size':small}}

        
#    print('\n' + CC.Caption+'Plotting the following components:' + CC.End)
    # Plotting of line data (e.g. PipeSegments, PipeLines)
    if "all" not in IgnoreList:
        for key in keys:
            if key not in IgnoreList and key not in PlotList:
                if(len(Netz.__dict__[key]))>0:
                    if key in linekeys:
                        color       = custom.get(str(key),{}).get('color', next(colors))
                        SingleLineWidth  = custom.get(str(key),{}).get('size', size_default)
                        QuickObject = PO.Ways2Lines(Netz.__dict__[key], tagstyle = tagstyle)
                        color       = SingleColor  if SingleColor  != '' else color
                        key         = SingleLabel  if SingleLabel  != '' else key
                        alpha       = SingleAlpha  if SingleAlpha  != '' else alpha
                        if len(selectList) == 0:
                            if LegendStr == '':
                                LegendString = getLegendStr(LegendStyle, key, len(Netz.__dict__[key]))
                            else:
                                LegendString = getLegendStr(LegendStyle, LegendStr, len(Netz.__dict__[key]))
                            # Plotting
                            PlotLines(*FigNum1, QuickObject, cursor_data = 'deactivate', linewidth = SingleLineWidth,
                                         alpha = alpha, color = color, legend = LegendString, Info = Info, selectList = selectList)
                        else:
                            if LegendStr == '':
                                LegendString = getLegendStr(LegendStyle, key, len(selectList))
                            else:
                                LegendString = getLegendStr(LegendStyle, LegendStr, len(selectList))
                            # Plotting
                            PlotLines(*FigNum1, QuickObject, cursor_data = 'deactivate', linewidth = SingleLineWidth,
                                         alpha = alpha, color = color, legend = LegendString, Info = Info, selectList = selectList)
                            

                
# Plotting of point data (e.g. Storages)
        
        for key in keys:
            if key not in IgnoreList and key not in PlotList:
                if(len(Netz.__dict__[key]))>0:
                    if key not in linekeys:
                        # creatin of Plotting input
                        color       = custom.get(key,{}).get('color',  next(colors))
                        marker      = custom.get(key,{}).get('marker', next(markers))
                        size        = custom.get(key,{}).get('size',   size_default)
                        QuickObject = PO.Nodes2Points(Netz.__dict__[key],tagstyle=tagstyle)
                        color       = SingleColor  if SingleColor  != '' else color
                        key         = SingleLabel  if SingleLabel  != '' else key
                        marker      = SingleMarker if SingleMarker != '' else marker
                        size        = SingleSize   if SingleSize   != '' else size
                        alpha       = SingleAlpha  if SingleAlpha  != '' else alpha
                        if len(selectList) == 0:
                            if LegendStr == '':
                                LegendString = getLegendStr(LegendStyle, key, len(Netz.__dict__[key]))
                            else:
                                LegendString = getLegendStr(LegendStyle, LegendStr)#, len(Netz.__dict__[key]))
                            # Pottting
                            PlotPoints(*FigNum1, QuickObject, alpha=alpha, names = Names, 
                                       cursor=Cursor,cursor_data = cursor_data, 
                                       color = color, legend = LegendString, Symbol = marker, 
                                       Info = Info, Size = str(size), selectList = selectList)
                        else:
                            if LegendStr == '':
                                LegendString = getLegendStr(LegendStyle, key, len(selectList))
                            else:
                                LegendString = getLegendStr(LegendStyle, LegendStr)#, len(selectList))
                            # Pottting
                            PlotPoints(*FigNum1, QuickObject, alpha=alpha, names = Names, 
                                       cursor=Cursor,cursor_data = cursor_data, 
                                       color = color, legend = LegendString, Symbol = marker, 
                                       Info = Info, Size = str(size), selectList = selectList)
                            
                            
    # Plotting Nodes last
    for key in PlotList:
        if len(keys) > 0:
            if(len(Netz.__dict__[key]))>0:
                if key not in linekeys:
                    color       = custom.get(key,{}).get('color',  next(colors))
                    marker      = custom.get(key,{}).get('marker', next(markers))
                    size        = custom.get(key,{}).get('size',   size_default)
                    QuickObject = PO.Nodes2Points(Netz.__dict__[key],tagstyle=tagstyle)
                    color       = SingleColor  if SingleColor  != '' else color
                    key         = SingleLabel  if SingleLabel  != '' else key
                    marker      = SingleMarker if SingleMarker != '' else marker
                    size        = SingleSize   if SingleSize   != '' else size
                    alpha       = SingleAlpha  if SingleAlpha  != '' else alpha
                    if len(selectList) == 0:
                        if LegendStr == '':
                            LegendString = getLegendStr(LegendStyle, key, len(Netz.__dict__[key]))
                        else:
                            LegendString = getLegendStr(LegendStyle, LegendStr, len(Netz.__dict__[key]))
                        # Ploting
                        PlotPoints(*FigNum1, QuickObject, names = Names, cursor_data = cursor_data, cursor = Cursor,
                                   color = color, alpha=alpha, legend = LegendString, Symbol = marker, 
                                   Info = Info, Size = str(size), selectList = selectList)
                    else:
                        if LegendStr == '':
                            LegendString = getLegendStr(LegendStyle, key, len(selectList))
                        else:
                            LegendString = getLegendStr(LegendStyle, LegendStr, len(selectList))
                        # Ploting
                        PlotPoints(*FigNum1, QuickObject, names = Names, cursor_data = cursor_data, cursor = Cursor,
                                   color = color, alpha=alpha, legend = LegendString, Symbol = marker, 
                                   Info = Info, Size = str(size), selectList = selectList)
                        
                else:
    
                    if key in linekeys:
                        color       = custom.get(key,{}).get('color',  next(colors))
                        marker      = custom.get(key,{}).get('marker', next(markers))
                        size        = custom.get(key,{}).get('size',   size_default)
                        QuickObject = PO.Ways2Lines(Netz.__dict__[key],tagstyle=tagstyle)
                        color       = SingleColor  if SingleColor  != '' else color
                        key         = SingleLabel  if SingleLabel  != '' else key
                        marker      = SingleMarker if SingleMarker != '' else marker
                        size        = SingleSize   if SingleSize   != '' else size
                        alpha       = SingleAlpha  if SingleAlpha  != '' else alpha
                        if len(selectList) == 0:
                            if LegendStr == '':
                                LegendString = getLegendStr(LegendStyle, key, len(Netz.__dict__[key]))
                            else:
                                LegendString = getLegendStr(LegendStyle, LegendStr)#, len(Netz.__dict__[key]))
                            # Plotting
                            PlotLines(*FigNum1, QuickObject, cursor_data = 'deactivate',linewidth=SingleLineWidth, 
                                      alpha=alpha, color = color, legend = LegendString, Info = Info, selectList = selectList)
                        else:
                            if LegendStr == '':
                                LegendString = getLegendStr(LegendStyle, key, len(selectList))
                            else:
                                LegendString = getLegendStr(LegendStyle, LegendStr)#, len(selectList))
                            # Plotting
                            PlotLines(*FigNum1, QuickObject, cursor_data = 'deactivate',linewidth=SingleLineWidth, 
                                      alpha=alpha, color = color, legend = LegendString, Info = Info, selectList = selectList)
                        
    if LegendStyle == '':
        ax.legend()
        
    if GridOn:
        plt.grid()

    if Save == True:
        fig.savefig(savefile, dpi=save_dpi)
        print('\nFile saved to: ' + CC.Cyan + savefile +CC.End)
        
    if Cursor==True:
        PlotCursor(cursor_data,multiple=False,hover=False)
        
    return FigNum1




# def quickplot(Netz, Info = '', alpha = 1, Names = False, savefile = '', PlotList =["Nodes",],
#               IgnoreList = ['GasFlowData','Processes','Nodes', 'SourceName'],
#               RandomColorsMarkers = False, countrycode = 'EU', figureNum = 1, 
#               MapColor = True, SupTitleStr = '', LegendStyle = 'Str', Cursor = False,
#               RandamColour = [], SingleLineWidth = '', SingleSize = '', SingleColor = '', GridOn = False,
#               selectList = [], LegendStr = '_nolegend_', Save = False):

#     FigNum1 = quickplot(Netz, Info=Info, alpha=alpha, savefile = savefile, 
#               PlotList = PlotList, IgnoreList = IgnoreList, Cursor = Cursor, 
#               RandomColorsMarkers = RandomColorsMarkers, countrycode = countrycode, 
#               Names=Names, figureNum = figureNum, RandamColour = RandamColour, SingleColor = SingleColor, 
#               SingleLineWidth = SingleLineWidth, SingleSize = SingleSize, GridOn = GridOn, 
#               MapColor=MapColor, SupTitleStr = SupTitleStr, LegendStyle = LegendStyle,
#               selectList = selectList, LegendStr = LegendStr, Save = Save)

#     return FigNum1

    

        



  	



















