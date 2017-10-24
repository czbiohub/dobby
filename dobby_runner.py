#!/usr/bin/python

import pandas as pd
import glob as glob
import dobby as dobby
import os

filenames =  glob.glob("*.txt")

#Dobby runner click option ideas:
#For metadata csv path

metadata = pd.read_csv('/Users/foad.green/googledrive/MACA/Metadata/MACA_Metadata - 384_well_plates.csv',index_col=0)

for filename in filenames:
	platename = filename.split('.')[0]
	mouse_id = metadata.loc[platename, 'mouse.id']
	print(filename)
	os.system("dobby cherrypick %s %s %s --plot" %(filename, platename, mouse_id))

