# -*- coding: utf-8 -*-
"""
M_PCKL
------
Module for pickle load and saving.

"""

import pickle
import os


def picklesavelist(element, filename, filedir):
    ''' Pickles list to file directory
	
	\n.. comments:
        Input: 
		    dictionary 
			filedirectory
    '''
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(os.path.join(filedir,filename), 'wb') as handle:
        pickle.dump(element, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    return




def pickleloadlist(filedirname,file):
    ''' UnPickles list from filedirectory
    '''

    with open(os.path.join(filedirname,file), 'rb') as handle:
        liste=pickle.load(handle)
        
    return liste




def picklesave(elements, filedir):
    ''' Saves network components into a Pickles file, where directory given through **filedir**.
	
	\n.. comments:
        Input: 
		    elements  		network component list
			filedir 		string of directory name
    '''
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    for elementname  in elements:
        with open(os.path.join(filedir, elementname+'.pickle'), 'wb') as handle:
            pickle.dump(elements[elementname], handle, protocol=pickle.HIGHEST_PROTOCOL)
            
    return           




def pickleload(elements, filedir):
    ''' Restores dict of dicts which was previously stored by pickelsave()
	
	\n.. comments:
        Input: 
		    elements  		network component list
			filedir 		string of directory name
    '''
    for elementname  in elements:
        with open(os.path.join(filedir, elementname+'.pickle'), 'rb') as handle:
            elements[elementname] = pickle.load(handle)
            
    return elements


