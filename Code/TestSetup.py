# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 13:58:35 2019

@author: diet_jn
"""

import matplotlib.pyplot     as plt
import Code.M_Visuell         as M_Visuell


def main():
    """This is a small testing function, that is being called from the Jupyter 
    workbook, that has been created as  part of the Openbod 2020 Berlin SciGRID_gas 
    workshop."""
    fig  = plt.figure(1)
    fig.clf(1)
    
    [fig, ax] = M_Visuell.PlotMap(countrycode = 'EU', 
                                     figureNum   = 1, 
                                     MapColor    = True, 
                                     SupTitleStr = '')