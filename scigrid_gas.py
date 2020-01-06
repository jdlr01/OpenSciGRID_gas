# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 12:56:49 2018

@author: JaDiet
w"""
from  pathlib            import Path

#import Code.M_Test           as M_Test
import Code.M_Filter         as M_Filter
import Code.M_Visuell        as M_Visuell
import Code.M_Helfer         as M_Helfer
import Code.M_EntsoG         as M_EntsoG
import Code.M_Test           as M_Test
import Code.M_CSV            as M_CSV
import Code.M_IGU            as M_IGU
import Code.M_GasLib         as M_GasLib
import Code.M_Matching       as M_Matching
import Code.M_GB             as M_GB
import Code.M_Internet       as M_Internet
import Code.M_LKD            as M_LKD
import Code.M_GIE            as M_GIE
import Code.M_GSE            as M_GSE

import configparser
from   configparser import  ExtendedInterpolation
import os
import Code.C_colors         as CC
import sys


#import Code.OSM.M_OSM_PF         as M_OSM_PF

#DirName_In_GB = testdir / 'TestsDaten/GB/'
#profile.run('M_GB.read(RelDirName = DirName_In_GB)', sort = 'tottime')



SetupFileName  = Path(os.getcwd() + '/Setup/AA_SetupFile.ini')
Setup_IO       = Path(os.getcwd() + '/Setup/Setup_IO.ini')
Setup_OSM      = Path(os.getcwd() + '/Setup/Setup_OSM.ini')
Setup_Visuell  = Path(os.getcwd() + '/Setup/Setup_Visuell.ini')

CSV_Path       = Path(os.getcwd() + '/Eingabe/TestData/')
CSV_Path_write = Path(os.getcwd() + '/Ausgabe/CSV/Test1')
OSM_Path       = Path(os.getcwd() + '/Eingabe/OSM')



print(CC.Caption + "=============================" + CC.End)
print(CC.Caption + "     SciGrid_gas Ver.0.5     " + CC.End)
print(CC.Caption + "=============================" + CC.End)
print(" ")
print(" ")
print(" ")

if sys.version_info.major == 2:
    raise RuntimeError('Unsupported python version')




###########################################################################
# Einlesung der Setup Datei
###########################################################################
Info            = configparser.ConfigParser()
Info.read(SetupFileName)
InfoIO          = configparser.ConfigParser()
InfoIO.read(Setup_IO)
currentDB       = InfoIO['SQL_5']
InfoOSM         = configparser.ConfigParser(interpolation=ExtendedInterpolation())
InfoOSM.read(Setup_OSM)
countrycode     = "EU"

InfoVisuell=configparser.ConfigParser()
InfoVisuell.read(Setup_Visuell)

InfoOSM1        = InfoOSM['OSM_' + countrycode + '_local']
PBF_inputfile   = InfoOSM1['PBF_inputfile']
PBF_outputfile  = InfoOSM1['PBF_outputfile']
JSON_outputfile = InfoOSM1['JSON_outputfile']




script_path = os.path.dirname(os.path.abspath( __file__ ))

if len(Info.sections()) == 0:
    print(CC.Caption + " Setup Datei wurde nicht gefunden." + CC.End)

###########################################################################
# User or Scripts
###########################################################################


user = 'GenDataset' # 'Modules' 'Adam' 'Script' 'Jan' 'ConfPars' 'None', 'GenDataset'

#Scriptes können nacheinander ausgeführt werden als ob sie im Hauptprogram stehen
#Scriptes sind im Ordner "Scripts" abgelegt
ScriptNames = ["Test_Script1.py","Test_Script2.py"]
ScriptNames = ['BuildDataDoco.py']
ScriptNames = ['Gen_02_NonOSM.py']



#ScriptNames = ['MakeRawData.py']
#ScriptNames = ['MakeModifiedData.py']
#ScriptNames = ['OverallSummary.py']
#ScriptNames = ['Plotting']
#ScriptNames = ['temp.py']
#ScriptNames = ['GenFirstTestNetz.py']
#ScriptNames = ['GenSampleStuff.py']


if user == 'Modules':
    

    make_MakeRawData    = True
    gen_StatsParam      = False
    get_AttribDensity   = False

    

    if make_MakeRawData:
        import Scripts.Jan.MakeRawData  as ThisOne
        ThisOne.main()

    
    baseDirName = os.getcwd()
    DirSource   = 'Data_Raw'
    CompNames   = ['Compressors', 'LNGs', 'Storages', 'PipeSegments']
    CompNames   = ['LNGs']
    
    import Code.M_Stats as M_Stats


    ##############################################################
    ### populating attributes with previously found statistical relationsships
    ##############################################################
    if gen_StatsParam == True:
        Netz        = M_CSV.read('Ausgabe/InternetDaten/' + DirSource )
        M_Stats.gen_StatsParam(Netz, CompNames = CompNames, SavePlots = True, MaxCombDepth = 2)



    ##############################################################
    ### populating attributes with previously found statistical relationsships
    ##############################################################
    if get_AttribDensity == True:
        Netz        = M_CSV.read('Ausgabe/InternetDaten/' + DirSource )
        for i in range(7):
            print(Netz.PipeSegments[i].param['max_cap_M_m3_per_d'])
#       Netz.print_ParamAttribDensity( CompName = CompNames[0])
        Netz        = M_Stats.pop_Attribs(Netz, CompNames = CompNames,  SettingsInputFileName  = 'Eingabe/Input_Settings' )
        print('After Attrib Generation')
        Netz.print_ParamAttribDensity( CompName = CompNames[0])
        for i in range(7):
            print('val', Netz.PipeSegments[i].param['max_cap_M_m3_per_d'])
            print('uncertainty',Netz.PipeSegments[i].uncertainty['max_cap_M_m3_per_d'])


elif user == 'GenDataset':
        import GenDataSets.Gen_01_Internet  as ThisOne
        ThisOne.main()




elif user == 'Script':
    for i in range(len(ScriptNames)):
        Script_Path = Path(os.getcwd() + '/GenDataSets/' +  ScriptNames[i])
        exec(open(Script_Path).read())


    
elif user == 'Adam':  
    
    InfoSQL = {'DataBaseName'   : 'esa_de_sgg_eurogastest_zz',
               'User'           : 'esa',
               'Host'           : '10.160.84.200',
               'Port'           : 5432,
               'PassWord'       : 'pg3sa'}
    
    PBF_inputfile  = InfoOSM1['PBF_inputfile']
    PBF_outputfile = InfoOSM1['PBF_outputfile']
    JSON_outputfile = InfoOSM1['JSON_outputfile']
    


elif user == 'Jan':  
    ScriptNames = ["Jan_CSV_1.py", "Jan_EntsoG_1.py", "Jan_EntsoG_2.py", "Jan_EntsoG_3.py", 
                   "Jan_EntsoG_CSV_1.py", "Jan_EntsoG_CSV_2.py", "Jan_GIE_1.py", "Jan_LKD_1.py"]



    import Code.M_Internet    as M_Internet
    import Code.M_LKD         as M_LKD
    import Code.M_GIE         as M_GIE
    import Code.M_GSE         as M_GSE
    import Code.M_GB          as M_GB
    import Code.M_Netze       as M_Netze
    import Code.M_Matching    as M_Matching
    import Code.OSM.M_OSM     as M_OSM
    


    # Joining components from different sources, e.g. LNG
    if 1 == 0:

        PlotList    = ['PipeSegments', 'PipeLines', 'LNG']

        Netz_Internet       = M_Internet.read(RelDirName  = 'Eingabe/InternetDaten/')
        #Netz_Internet       = M_Internet.read(RelDirName  = 'Eingabe/InternetDaten/', requeYear = ['1970'], GasType = ['H', ''])
        Netz_Internet_Orig  = M_Internet.read(RelDirName  = 'Eingabe/InternetDaten/', requeYear = ['2019'], GasType = ['H', ''])


#        Netz_EntsoG_Orig    = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInter/')
        Netz_EntsoG         = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInter/')
        # Netz_EntsoG.select_byAttrib(['LNGs'], 'is_planned', None, '==')
        # Netz_LKD           = M_LKD.read(RelDirName = 'Eingabe/LKD/')
        # Netz_GIE            = M_GIE.read(RelDirName = 'Eingabe/GIE/', RelDirNameInter = 'Eingabe/InternetDaten/', requeYear = ['2019'])
        # Netz_GB            = M_GB.read()
        # Netz_GSE           = M_GSE.read()



    if 1 == 0:
        Netz_IGU            = M_IGU.read(RelDirNameInter    = 'Eingabe/InternetDaten/')
        CSV_Path_write      = 'Eingabe/IGU/'
        M_CSV.write(CSV_Path_write, Netz_IGU)
        M_Visuell.quickplot(Netz_IGU, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
                             SingleSize = 60, SingleColor = 'r',
                             PlotList = ['Storages', 'Nodes'], IgnoreList = 'all', Cursor = True)
    
    
    
    
    if 1 == 1:
        PlotList            = ['PipeSegments', 'PipeLines', 'Storages']
        CSV_Path_write      = 'Eingabe/IGU/'
        Netz_IGU            = M_CSV.read(CSV_Path_write)
        Netz_LKD            = M_LKD.read(RelDirName = 'Eingabe/LKD/')
        Netz_GSE            = M_GSE.read()
#        Netz_LKD.select_byPos('Storages',[0,6])
#        Netz_GSE.select_byPos('Storages',[ 60,70])
        
        # Netz_LKD, Netz_GSE
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_LKD, Netz_GSE, compName = 'Storages', threshold = 65,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_LKD.join_comp(Netz_GSE, 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
        
        
        # Netz_LKD, Netz_GSE
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_LKD, Netz_IGU, compName = 'Storages', threshold = 65,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_LKD.join_comp(Netz_IGU, 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
        
        
        
        
        
        Netz_LKD.fill_attrib('Storages', 'start_year', 'math_mean_int')
#        M_Visuell.quickplot(Netz_GSE, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
#                             SingleSize = 60, SingleColor = 'g',
#                             PlotList = ['Storages'], IgnoreList = 'all', Cursor = True, SupTitleStr = 'Kombiniert')
#        M_Visuell.quickplot(Netz_GSE, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
#                             SingleSize = 60, SingleColor = 'g',
#                             PlotList = PlotList, IgnoreList = 'all', Cursor = True, SupTitleStr = 'Kombiniert')
        CSV_Path_write      = 'Ausgabe/Temp/'
        M_CSV.write(CSV_Path_write, Netz_LKD)
        Netz_LKD_2          = M_CSV.read(CSV_Path_write)
        
        
    if 'Storages' == 'Storas':
        PlotList            = ['PipeSegments', 'PipeLines', 'Storages']
        CSV_Path_write      = 'Eingabe/IGU/'
        Netz_IGU            = M_CSV.read(CSV_Path_write)
        Netz_LKD            = M_LKD.read(RelDirName = 'Eingabe/LKD/')
        Netz_GIE            = M_GIE.read(RelDirName = 'Eingabe/GIE/', RelDirNameInter = 'Eingabe/InternetDaten/', requeYear = ['2019'])
        Netz_GSE            = M_GSE.read()
        
        Netz_Final          = M_Internet.read(RelDirName  = 'Eingabe/InternetDaten/', requeYear = ['2019'], GasType = ['H', ''])
        Netz_Internet_Orig  = M_Internet.read(RelDirName  = 'Eingabe/InternetDaten/', requeYear = ['2019'], GasType = ['H', ''])

        Netz_EntsoG         = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInterEtzel/', locDirName = 'Eingabe/InternetDaten/')
        
        # EntsoG        
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_Final, Netz_EntsoG, compName = 'Storages', threshold = 20,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_Final.join_comp(Netz_EntsoG, 'Storages', pos_match_Netz_0, pos_match_Netz_1, pos_add_Netz_1, pos_add_Netz_0)

        # IGU
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_Final, Netz_IGU, compName = 'Storages', threshold = 20,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_Final.join_comp(Netz_IGU, 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)

#        # Netz_LKD --> Netz_Final
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_Final, Netz_LKD, compName = 'Storages', threshold = 80,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_Final.join_comp(Netz_LKD, 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
        
#        # Netz_GIE --> Netz_Final
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_Final, Netz_GIE, compName = 'Storages', threshold = 80,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_Final.join_comp(Netz_GIE, 'Storages', pos_match_Netz_0, pos_match_Netz_1, pos_add_Netz_1, pos_add_Netz_0)
        
#        # Netz_GSE --> Netz_Final
        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
            Netz_Final, Netz_GSE, compName = 'Storages', threshold = 80,
            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name_incl_CC(comp_0, comp_1), 
                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong(comp_0, comp_1, method = 'inv')
                ))
        Netz_Final.join_comp(Netz_GSE, 'Storages', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)


        M_Visuell.quickplot(Netz_Final, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
                             SingleSize = 60, SingleColor = 'g',
                             PlotList = PlotList, IgnoreList = 'all', Cursor = True, SupTitleStr = 'Kombiniert')
        M_Visuell.quickplot(Netz_EntsoG, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
                             SingleSize = 60, SingleColor = 'r',
                             PlotList = ['Storages'], IgnoreList = 'all', Cursor = True, SupTitleStr = 'Kombiniert')

        CSV_Path_write      = 'Eingabe/TempStorage/'
        M_CSV.write(CSV_Path_write, Netz_Final)




    if 1 == 0:
        CSV_Path_write      = 'Eingabe/TempStorage/'
        M_CSV.write(CSV_Path_write, Netz_Final)




    if 1 == 0:
        ### Merging Productions
        # Netz_EntsoG --> Netz_Internet
#        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
#            Netz_Internet, Netz_EntsoG, compName = 'Productions', threshold = 80,
#            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name(comp_0, comp_1), 
#                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong_Threshold(comp_0, comp_1, 50000)
#                ))
#        Netz_Internet.join_comp(Netz_EntsoG, 'Productions', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)
#        # Netz_LKD --> Netz_Internet
#        [pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1] = M_Matching.match(
#            Netz_Internet, Netz_LKD, compName = 'Productions', threshold = 80,
#            funcs = (lambda comp_0, comp_1: M_Matching.get_Comp_Name(comp_0, comp_1), 
#                lambda comp_0, comp_1: M_Matching.get_Comp_LatLong_Threshold(comp_0, comp_1, 50000)
#                ))
#        Netz_Internet.join_comp(Netz_LKD, 'Productions', pos_match_Netz_0, pos_add_Netz_0, pos_match_Netz_1, pos_add_Netz_1)


        M_Visuell.quickplot(Netz_Internet, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
                             SingleSize = 60, SingleColor = 'g',
                             PlotList = PlotList, IgnoreList = 'all', Cursor = True, SupTitleStr = 'Kombiniert')
        M_Visuell.quickplot(Netz_EntsoG, figureNum = 0, LegendStyle = 'Str(Num)', countrycode = 'EU',
                             SingleSize = 60, SingleColor = 'r',
                             PlotList = ['Storages'], IgnoreList = 'all', Cursor = True, SupTitleStr = 'Kombiniert')


    # OSM data
    if 1 == 0:
        PlotList    = ['PipeSegments']

        countrycode     = 'FR'
        OSM = M_OSM.read(Info = InfoOSM1, countrycode = countrycode)
    
    
    
        Netz_Internet_Orig   = M_Internet.read(RelDirName  = 'Eingabe/InternetDaten/', requeYear = ['2019'])

        M_Visuell.quickplot(Netz_Internet_Orig, figureNum = 1, LegendStyle = 'Str', countrycode = 'FR',
                             SupTitleStr = 'Internet', PlotList = PlotList, IgnoreList = 'all', Colour = ['r'],
                             RandomColorsMarkers = True, SingleLineWidth = 2.0)
    
        M_Visuell.quickplot(OSM, figureNum = 0, LegendStyle = 'Str', countrycode = 'FR',
                             SupTitleStr = 'OSM', PlotList = ['PipeLines'], IgnoreList = 'all',
                             SingleLineWidth = 2.0)



    if 1 == 0:
        Netz_GB_1 = M_GB.read()
        Netz_GB_1.source_summary2File('GB', 'Dokumentation/Source/SciGrid_GB.md', 'Dokumentation/Build/SciGrid_GB.md', 'Dokumentation/Bilder/Kapitel_GB/GB_DatasetSummary.jpg' )
        CSV_Path_write      = 'Ausgabe/GB/Daten/'
        M_CSV.write(CSV_Path_write, Netz_GB_1)
#        M_Visuell.quickplot(Netz_GB_1, countrycode = 'GB', figureNum = 10)#, 
                             #savefile = 'Ausgabe/Plots/Temp/DatasetSummary.jpg')
#        Netz_GB_1.all()


    # Internet
    if 1 == 0:
        Netz_Internet = M_Internet.read()
        Netz_Internet.source_summary2File('InternetDaten', 'Dokumentation/Source/SciGrid_InternetData.md', 'Dokumentation/Build/SciGrid_InternetData.md', 'Dokumentation/Bilder/Kapitel_InternetData/InternetData_DatasetSummary.jpg')
        CSV_Path_write      = 'Ausgabe/InternetDaten/Daten/'
        M_CSV.write(CSV_Path_write, Netz_Internet)
        #M_Visuell.quickplot(Netz_Internet, figureNum = 10,  countrycode = 'EU', Cursor = True)#, 
                             #savefile = 'Ausgabe/Plots/Temp/InternetDaten_DatasetSummary.jpg') # SupTitleStr = 'Internet', 
#        Netz_Internet.all()
        
        
    # EntsoG
    if 1 == 0:
        Netz_EntsoG2 = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInter/')
        Netz_EntsoG2.source_summary2File('EntsoG', 'Dokumentation/Source/SciGrid_EntsoG.md', 'Dokumentation/Build/SciGrid_EntsoG.md', 'Dokumentation/Bilder/Kapitel_EntsoG/SourceSummary_EntsoG.jpg')
        CSV_Path_write      = 'Ausgabe/EntsoG/Daten/'
        M_CSV.write(CSV_Path_write, Netz_EntsoG2)
#        M_Visuell.quickplot(Netz_EntsoG2, figureNum = 10)#,  countrycode = 'EU', SupTitleStr = 'EntsogG')
#        Netz_EntsoG2.all()
        
        
    # EntsoG
    if 1 == 0:
        Netz_EntsoG = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInter/')
        Netz_EntsoG.all()
        
        
        Netz_EntsoG.ConnectionPoints        = []
        Netz_EntsoG.Consumers               = []
#        Netz_EntsoG.InterConnectionPoints   = []
        Netz_EntsoG.LNGs                    = []
        Netz_EntsoG.Productions             = []
        Netz_EntsoG.Storages                = []
        Netz_EntsoG.Operators               = []
        Netz_EntsoG.Nodes                   = []
        
        M_Visuell.quickplot(Netz_EntsoG, figureNum = 1,  countrycode = 'EU', SupTitleStr = 'EntsogG')
        
        M_Visuell.quickplot(Netz_EntsoG, figureNum = 1,  countrycode = 'EU',SupTitleStr = 'EntsogG', 
                             savefile = 'Ausgabe/Plots/Temp/EntsoG_DatasetSummary.jpg')
        
        
    # EntsoG Time series plot
    if 1 == 0:
        Netz_EntsoG = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInter/')
        
        Netz_EntsoG.GasFlow = M_EntsoG.read_GasFlow(Netz_EntsoG, RelDirName = 'Eingabe/EntsoG/GasflowInter', 
                                        StartDate = '2010-10-01T00:00:00', StopDate = '2118-12-31T00:00:00')

        # Plot FDC
        for gasflow in Netz_EntsoG.GasFlow:
            M_Visuell.plot_FDC(gasflow, DirNamePlot = 'Ausgabe/EntsoG/Plots/FDC_Raw/')

        # Despike
        Netz_EntsoG.GasFlow     = M_EntsoG.deSpike_GasFlow(Netz_EntsoG.GasFlow)
        
        # Create FDC
        Netz_EntsoG.FDC         = M_EntsoG.create_FDC(Netz_EntsoG.GasFlow)
        
        # Plot FDC
        for gasflow in Netz_EntsoG.GasFlow:
            M_Visuell.plot_FDC(gasflow, DirNamePlot = 'Ausgabe/EntsoG/Plots/FDC_DeSpiked/')
        
        
        
    # EntsoG Loading Data off API
    if 1 == 0:
        Netz_EntsoG = M_EntsoG.read(RelDirNameGasData = 'Eingabe/EntsoG/GasflowInter/')
        M_EntsoG.GasFlowAPI2CSV(Netz_EntsoG, ['ConnectionPoints'], 
                                StartNum = 698,
                                DateStartStr = '2013-09-01', DateEndStr = '2019-04-01', 
                                DirName = 'Eingabe/EntsoG/GasflowConn/' )
        
        
    # LKD
    if 1 == 0:
        Netz_LKD = M_LKD.read(RelDirName = 'Eingabe/LKD/')
        Netz_LKD.source_summary2File('LKD', 'Dokumentation/Source/SciGrid_LKD.md', 'Dokumentation/Build/SciGrid_LKD.md', 'Dokumentation/Bilder/Kapitel_LKD/LKD_DatasetSummary.jpg')
        CSV_Path_write      = 'Ausgabe/LKD/Daten/'
        M_CSV.write(CSV_Path_write, Netz_LKD)
#        Netz_LKD.all()
#        M_Visuell.quickplot(Netz_LKD, figureNum = 10 )#,  countrycode = 'DE', SupTitleStr = 'LKD')#, 
                             #savefile = 'Ausgabe/Plots/Temp/LKD_DatasetSummary.jpg')
        

    # GIE
    if 1 == 0:
        Netz_GIE = M_GIE.read(RelDirName = 'Eingabe/GIE/', RelDirNameInter = 'Eingabe/InternetDaten/', requeYear = list(range(1999, 2020)))
        Netz_GIE.source_summary2File('GIE', 'Dokumentation/Source/SciGrid_GIE.md', 'Dokumentation/Build/SciGrid_GIE.md', 'Dokumentation/Bilder/Kapitel_GIE/GIE_DatasetSummary.jpg')
        CSV_Path_write      = 'Ausgabe/GIE/Daten/'
        M_CSV.write(CSV_Path_write, Netz_GIE)
#        Netz_GIE.Nodes = []
#        M_Visuell.quickplot(Netz_GIE, figureNum = 10)#,  SupTitleStr = 'GIE', 
                             #savefile = 'Ausgabe/Plots/Temp/GIE_DatasetSummary.jpg')
    
    
    # GSE
    if 1 == 0:
        Netz_GSE = M_GSE.read()
        Netz_GSE.source_summary2File('GSE', 'Dokumentation/Source/SciGrid_GSE.md', 'Dokumentation/Build/SciGrid_GSE.md', 'Dokumentation/Bilder/Kapitel_GSE/GSE_DatasetSummary.jpg')
        CSV_Path_write      = 'Ausgabe/GSE/Daten/'
        M_CSV.write(CSV_Path_write, Netz_GSE)
#        Netz_GSE.all()
#        M_Visuell.quickplot(Netz_GSE, figureNum = 10, SupTitleStr = 'Kombiniert',  
#                             savefile = 'Ausgabe/Plots/Temp/Kombiniert_DatasetSummary.jpg')



    # IGU
    if 1 == 0:
        Netz_IGU = M_IGU.read(RelDirNameInter = 'Eingabe/InternetDaten/')
        Netz_IGU.source_summary2File('IGU', 'Dokumentation/Source/SciGrid_IGU.md', 
                              'Dokumentation/Build/SciGrid_IGU.md', 
                              'Dokumentation/Bilder/Kapitel_IGU/IGU_DatasetSummary.jpg')
        CSV_Path_write      = 'Ausgabe/IGU/Daten/'
        M_CSV.write(CSV_Path_write, Netz_IGU)
#        Netz_IGU.all()
#        M_Visuell.quickplot(Netz_IGU, figureNum = 99, savefile = 'Dokumentation/Bilder/Kapitel_IGU/IGU_DatasetSummary.jpg')
    
    
    
    # GasLib_135
    if 1 == 0:
        Netz_GasLib_135 = M_GasLib.read(RelDirName = 'Eingabe/GasLib/', sourceName = 'GasLib-135')
        Netz_GasLib_135.source_summary2File('GasLib_135', 'Dokumentation/Source/SciGrid_GasLib_135.md', 
                                     'Dokumentation/Build/SciGrid_GasLib_135.md', 
                                     'Dokumentation/Bilder/Kapitel_GasLib_135/SciGrid_GasLib_135.jpg')
        CSV_Path_write      = 'Ausgabe/GasLib_135/Daten/'
        M_CSV.write(CSV_Path_write, Netz_GasLib_135)
#        Netz_GasLib_135.all()
#        M_Visuell.quickplot(Netz_GasLib_135, figureNum = 0,  SupTitleStr = 'GL-135', 
#                             countrycode = 'DE', LegendStyle = 'Str(Num)', Cursor = True)
#                             #savefile = 'Ausgabe/Plots/Temp/GL-135_DatasetSummary.jpg')
      
        
    # GasLib_4197
    if 1 == 0:
        Netz_GasLib_4197 = M_GasLib.read(RelDirName = 'Eingabe/GasLib/', sourceName = 'GasLib-4197')
        Netz_GasLib_4197.source_summary2File('GasLib_4197', 'Dokumentation/Source/SciGrid_GasLib_4197.md', 
                                      'Dokumentation/Build/SciGrid_GasLib_4197.md', 
                                      'Dokumentation/Bilder/Kapitel_GasLib_4197/SciGrid_GasLib_4197.jpg')
        CSV_Path_write      = 'Ausgabe/GasLib_4197/Daten/'
        M_CSV.write(CSV_Path_write, Netz_GasLib_4197)
#        Netz_GasLib_4197.all()
#        M_Visuell.quickplot(Netz_GasLib_4197, figureNum = 0,  SupTitleStr = 'GL-4197', 
#                             LegendStyle = 'Str(Num)', Cursor = True)
    
        
        
        
        
        
  
elif user == 'ConfPars':
    ###########################################################################
    # Setting up output file
    ###########################################################################
    LogDateiName = M_Helfer.getFileName(Info["Zusatz"], "LogDatei_OrdnerDateiName")
    # Schreiben aller Setup Information in Log Datei    
    M_Helfer.LogFileSetup(Info)
    figureNum = 0
    
    
    for prozess in Info["Zusatz"]["Prozesse"].split(','):
        Daten           = []
        Netz_MDGraph    = []
        Netz_Graph      = []
        Prozess         = prozess.strip()
        Eingabe         = Info[Prozess]["Eingabe"]
        Aktionen        = Info[Prozess]["Aktionen"]
    
        if len(Eingabe) > 0:
            Info_A  = M_Helfer.getSetup(Info, 'IO', Eingabe, LogDateiName)

            Ret         = M_Einlesen.Einlesen_Main(Info_A, Eingabe)
            Daten       = Ret[0]
            if len(Ret) > 1:
                Netz_Graph  = Ret[1]
            else:
                Netz_Graph  = []
            if len(Ret) >2:
                Netz_MDGraph = Ret[2]
            else:
                Netz_MDGraph = []
        
        
        # Durchfuehren aller Aktionen an den Netz
        for Aktion in Aktionen.split(','):
            aktion  = Aktion.strip()
        
            # ================= Filter ======================
            if aktion.find("Filter") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'Filter', aktion, LogDateiName)
                Daten   = M_Filter.Filter_Main(Info_A, Daten)
                    
            # ================= Test ======================
            elif aktion.find("Test") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'Test', aktion, LogDateiName)
                M_Test.Test_Main(Info_A, Netz_Graph, Netz_MDGraph, Daten)
    
            # ================= Visuell ======================
            elif aktion.find("Visuell") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'Visuell', aktion, LogDateiName)
                M_Visuell.Visuell_Main(Info_A, Daten, figureNum)
                figureNum                   = figureNum + 1
        
            # ================= Verknuepfe ======================
            elif aktion.find("Verknuepfe") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'Verknuepfe', aktion, LogDateiName)
                Ret     = M_Verknuepfe.Verknuepfe_Main(Info_A, Daten)
                Netz_Graph      = Ret[0]
                Netz_MDGraph    = Ret[1]
                Daten           = Ret[2]
        
            # ================= Speichern ======================
            elif aktion.find("CSV") == 0 or aktion.find("SQL") == 0 or aktion.find("PCK") == 0 or aktion.find("NCV") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'IO', aktion, LogDateiName)
                M_Ausgabe.Ausgabe_Main(Info_A, Daten)
                
            # ================= EntsoG ======================
            elif aktion.find("EntsoG") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'EntsoG', aktion, LogDateiName)
                Daten   = M_EntsoG.EntsoG_Main(Info_A, Info, Daten)
                
                
            # ================= CodeTest ======================
            elif aktion.find("CodeTest") == 0:
                Info_A  = M_Helfer.getSetup(Info, 'CodeTest', aktion, LogDateiName)
                M_CodeTest.CodeTest_Main(Info_A, Daten)
