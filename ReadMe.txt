SciGRID_GAS
===========

Date: 		27-Jan-2020
Version:	1.0
Institute: 	Vernetzet Energie Systeme-DLR
		Carl-von-Ossietzky-Straße 15
		26129 Oldenburg
		Germany

Project Name:	SciGRID_gas
Funding: 	Bundesministerium für Wirtschaft und Energie, Germany
Funding code: 	03ET4063


Overview:
---------
SciGRID_gas is a project trying to generate a public open source data set of the European gas 
transmission pipeline network.  

Here the first version ("02_NonOSM") is being presented, that was introduced at the 
OpenMOD workshop in Berlin in January 2020.  

The power point presentation of this workshop can be found in folder:
../Dokumentation/JupyterNotebook/Combined.pptx
which tries to :
- give an overview of the project 
- explains the terminology used within SciGRID_gas
- explains the data structure
- explains the steps required to generate the data


How to generate a gas transmission network data set:
----------------------------------------------------
There are two options of how you can generate the data set your self

1) Jupyter Notebook
Open a Jupyter notebook in the main folder of the project and execute all steps in the notebook

2) Python script
Copy the file 
../GenDataSets/Gen_02_NonOSM.py
into the main folder, and run the script from there


Documentation:
--------------
A first cut of a not yet completed user manual can be found under:
../Dokumentation/SciGRID_gas_UserManual.pdf


Feedback:
---------
We are seeking feedback on the data and all issues related to the project.
Please contact us through:
developers.gas@scigrid.de
