# -*- coding: utf-8 -*-
"""
GenFirstTestNetz
----------------
    
"""
import Code.M_Shape          as M_Shape
import Code.M_CSV            as M_CSV
import Code.M_Visuell        as M_Visuell
import matplotlib.pyplot     as plt
import Code.M_Internet       as M_Internet
import Code.M_GIE            as M_GIE
import Code.M_Stats          as M_Stats
import Code.M_IGU            as M_IGU
import Code.M_EntsoG         as M_EntsoG
import Code.M_GB             as M_GB
import Code.M_LKD            as M_LKD
import Code.M_GSE            as M_GSE
import Code.C_colors         as CC
import Code.M_GasLib         as M_GasLib
import Code.M_AutoDoku       as M_AutoDoku
import Code.JoinNetz         as JoinNetz
import Code.M_LoadAdditional as M_LoadAdditional





def main():
    


    #############################################################################
    # 1) Sections to execute under gain
    #############################################################################
    # Converting raw data into CSV files 
    MakeRawData_01              = False                       
    # Joining source data into single network
    MakeOverallNetwork_02       = False
    Print_MakeOverallNetwork_02 = False
    # Writing info to markdown text
    MakeOverallSummary_03       = False
    # Generation of histogram plots of the data
    PlotData_04                 = False
    # Testing heuristic methods setup
    TestMethods_05              = False
    
    
    # filling missing attribute values
    FillAttribValue_06          = False                        
    # simplifying network
    ShrinkNetz_07               = True
    
    
    #############################################################################
    # 2) Setting for plotting
    #############################################################################
    # Boolean to plot maps True  False
    PlotData            = True                                  
    # Starting figure number
    figureNum           = 0                                     
    # Booelan to turn on curers in plots or turn them off
    Cursor              = False
    
    #############################################################################
    # 3) Settings re data sources
    #############################################################################
    # options are "Data_Raw_CSV" and "source" and "Data_Modified_CSV"
    DataLocationType    = 'Data_Raw_CSV'                        
    # options are any component label in list
    CompNames2Join      = ['LNGs','Storages']
    CompNames2Test      = ['LNGs', 'Compressors', 'Storages', 'PipeSegments']
    # options are any non-OSM data source
    sourceList          = ['InterNet',  'GIE']  
    
    #############################################################################
    # 4) Settings for export
    #############################################################################
    # String giving the relative jpg file name where to save map of raw joined data
    save_Plot_Raw       = 'Dokumentation/Bilder/10_NetzGeneration/10_NonOSM/Map_RawSum.jpg'
    # String giving the relative jpg file name where to save map of final joined data
    save_Plot_Final     = 'Dokumentation/Bilder/10_NetzGeneration/10_NonOSM/Map_Final.jpg'
    # String giving the relative path name where to save CSV gas network data set files of raw data set
    dir_Data_Raw_Merged         = 'Ausgabe/GeneratedNetz/02_NonOSM/Data_Merged/'
    dir_Data_Raw_Component      = 'Ausgabe/GeneratedNetz/02_NonOSM/Data_Component/'
    # String giving the relative path name where to save CSV gas network data set files of final data set
    dir_Data_Final              = 'Ausgabe/GeneratedNetz/02_NonOSM/Data_Final/'
    
    



    #=========================================================================
    # 1) Creation CSV data from raw data
    #=========================================================================
    if MakeRawData_01:
        CC.printT('Make Raw Data for:')
        ## Netz_InterNet
        CC.printb('InterNet')
        Netz_InterNet   = M_Internet.read(RelDirName = 'Eingabe/InternetDaten/')
        M_CSV.write('Ausgabe/InternetDaten/Data_Raw/', Netz_InterNet)
   



    #=========================================================================
    # 2) Creation combined network
    #=========================================================================
    if MakeOverallNetwork_02:
        # Settings for summary generation
        
    
        # loading data from CSV files
        DataDict        = M_LoadAdditional.loadData(DataLocationType = DataLocationType, sourceList = sourceList)
    
        # Joining sources into a single network
        Netz_Merged     = JoinNetz.join('Scen_1', CompNames2Join, DataDict)
        Netz_Merged.cleanUpNodes(skipNodes = True)
        DataDict['DasNetz'] = Netz_Merged
        sourceList.append('DasNetz')
        
        
        # writing joined nework to CSV file
        M_CSV.write(dir_Data_Raw_Merged, Netz_Merged)
        Netz_Merged.all()
        

        if Print_MakeOverallNetwork_02:
            for compName in Netz_Merged.CompLabels():
                print(' ')
                print('===========================================================')
                print("{0:23s}  ".format(str(compName)) + str(len(Netz_Merged.__dict__[compName])) +'  found    missing    % missing')
                print('===========================================================')
                if len(Netz_Merged.__dict__[compName]) > 0:
                    for key in Netz_Merged.__dict__[compName][0].param.keys():
                        NumFound    = Netz_Merged.get_AttribDensity(compName, key)[key]
                        diff        = len(Netz_Merged.__dict__[compName]) - NumFound
                        perc        = round(diff / len(Netz_Merged.__dict__[compName]) * 100)
                        print("{0:30s} {1:>3s},  ".format(str(key), str(NumFound)) +  "{0:3s} {1:>3s},  ".format(' ', str(diff)) +  "{0:5s} {1:>3s}".format( ' ', str(perc)))                        
                        

            for compName in Netz_Merged.CompLabels():
                print(' ')
                print('===========================================================')
                print("{0:23s}  ".format(str(compName)) + str(len(Netz_Merged.__dict__[compName])) +'  found    missing    % missing')
                print('===========================================================')
                if len(Netz_Merged.__dict__[compName]) > 0:
                    for key in Netz_Merged.__dict__[compName][0].param.keys():
                        NumFound    = Netz_Merged.get_AttribDensity(compName, key)[key]
                        diff        = len(Netz_Merged.__dict__[compName]) - NumFound
                        perc        = round(diff / len(Netz_Merged.__dict__[compName]) * 100)
                        print(str(key))   


        M_Visuell.quickplot(Netz_Merged, figureNum = 0, LegendStr = '', LegendStyle = 'Str(Num)', countrycode = 'EU', Cursor = False, 
                             Save = True, savefile = save_Plot_Raw, PlotList =["Nodes"])

    #=========================================================================
    # 3) writing overall summary into markdown files
    #=========================================================================
    if MakeOverallSummary_03:
        # writing info on data ot markdown file
        M_AutoDoku.summary2File(DataDict, CompNames = CompNames2Join, sourceList = sourceList)


        
        
        
    #=========================================================================
    # 4) Creating histogram and other plots prior to attribute value method tests
    #=========================================================================
    if PlotData_04:
        Netz_Merged      = M_CSV.read(dir_Data_Raw_Merged)
        M_Stats.gen_DataHists(Netz_Merged, CompNames = [], 
             AttribNames        = [], 
             StatsInputDirName  = 'Eingabe/Input_Settings',
             DataStatsOutput    = 'Ausgabe/GeneratedNetz/02_NonOSM/StatsData')
         
         
         
        
    #=========================================================================
    # 5) Testing of all available heuristic methods and writing different error valus into CSV file
    #=========================================================================
    if TestMethods_05:
        Netz_Merged      = M_CSV.read(dir_Data_Raw_Merged)
        # Creation of error vals for all heuristic methods
        # RetStatsSummary = Netz_Final.test_methods(CompNames = ['Compressors'], InAttribNames = [],  CalcMethods = [], ErrorMethods = ['LOOCV'])
        M_Stats.gen_StatsParam(Netz_Merged, CompNames = CompNames2Test, SavePlots = True, MaxCombDepth = 1, 
                               StatsInputDirName  = 'Ausgabe/GeneratedNetz/02_NonOSM/SetupFiles',
                               DataStatsOutput    = 'Ausgabe/GeneratedNetz/02_NonOSM/StatsData')
        
        #RetStatsSummary.save2File(dir_Data_Stats)    
        
        
        

    #=========================================================================
    # 6) Generation of missing data
    #=========================================================================
    if FillAttribValue_06:
        
        Netz_Merged         = M_CSV.read(dir_Data_Raw_Merged)
        for compName in CompNames2Test:
            SettingsFileName    = ('Ausgabe/GeneratedNetz/02_NonOSM/SetupFiles/RetSummary_' + compName + '.csv')
            SimSettings         = M_CSV.read_CSV_raw(SettingsFileName)
        
            Netz_Component      = M_Stats.pop_Attribs(Netz_Merged, CompNames = [compName], SimSettings = SimSettings)
        
        
#        # writing constant values into attributes
        Netz_Component.make_Attrib([], '',    'end_year',   'const', 2050)
        Netz_Component.make_Attrib([], '',    'start_year', 'const', 1983)
#        
#        # writing joined nework to CSV file
        M_CSV.write(dir_Data_Raw_Component, Netz_Component)




    #=========================================================================
    # 7) Shrinking Dataset to one single network
    #=========================================================================
    if ShrinkNetz_07:
        # Loading network
        Netz_Component         = M_CSV.read(dir_Data_Raw_Component)
        
        # Simplifying network
        Netz_Component.cleanUpNodes(compNames = [], skipNodes = True)
        Netz_Final  = M_Shape.moveComp2Pipe(Netz_Component.copy2(), 'Compressors',      'PipeSegments', maxDistance = 100.0)
        Netz_Final  = M_Shape.moveComp2Pipe(Netz_Final.copy2(), 'Storages',         'PipeSegments', maxDistance = 100.0)
        Netz_Final  = M_Shape.moveComp2Pipe(Netz_Final.copy2(), 'ConnectionPoints', 'PipeSegments', maxDistance = 100.0)
        Netz_Final  = M_Shape.moveComp2Pipe(Netz_Final.copy2(), 'EntryPoints',      'PipeSegments', maxDistance = 100.0)
        Netz_Final  = M_Shape.moveComp2Pipe(Netz_Final.copy2(), 'BorderPoints',     'PipeSegments', maxDistance = 100.0)
        Netz_Final  = M_Shape.moveComp2Pipe(Netz_Final.copy2(), 'LNGs',             'PipeSegments', maxDistance = 100.0)
        
        # Ceaning up network
        Netz_Final.Nodes  = Netz_Final.add_Nodes([], [])
        Netz_Final.Nodes  = M_Shape.reduceElement(Netz_Final.Nodes, reduceType = 'LatLong')
        
        Netz_Final.remove_unConnectedComponents()
        Netz_Final.remove_unUsedNodes()
        
        Netz_Final.Nodes  = Netz_Final.add_Nodes([], [])

        # Writing final network to CSV
        M_CSV.write(dir_Data_Final, Netz_Final)
        # Plotting 
        if PlotData:
            figureNum       = 5
            fig             = plt.figure(figureNum)
            fig.clf(figureNum)
            M_Visuell.quickplot(Netz_Final, figureNum = figureNum, LegendStr = '', LegendStyle = 'Str(Num)', countrycode = 'EU', Cursor = Cursor,
                                 Save = True, savefile = save_Plot_Final, PlotList =["Nodes"])
