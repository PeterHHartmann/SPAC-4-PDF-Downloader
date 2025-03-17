# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 15:37:08 2019

@author: hewi
"""

#### IF error : "ModuleNotFOundError: no module named PyPDF2"
# then uncomment line below (i.e. remove the #):

# pip install PyPDF2

import pandas as pd
import PyPDF2
from pathlib import Path
import shutil, os
import os.path
import urllib
import glob


###!!NB!! column with URL's should be called: "Pdf_URL" and the year should be in column named: "Pub_Year"

### File names will be the ID from the ID column (e.g. BR2005.pdf)

########## EDIT HERE:

### specify path to file containing the URLs
list_pth = "K:/TextMining/02 Analysis 8/10 TextMining Projects/CSR/CSR Train/02 Supporting Scripts/01 Scripts input/GRI_2017_2020_SAHO.xlsx"

###specify Output folder (in this case it moves one folder up and saves in the script output folder)
pth = "K:/TextMining/02 Analysis 8/10 TextMining Projects/CSR/CSR Train/02 Supporting Scripts/03 Scripts output/"

###Specify path for existing downloads
dwn_pth = "K:/TextMining/02 Analysis 8/10 TextMining Projects/CSR/CSR Train/02 Supporting Scripts/03 Scripts output/dwn/"

### cheack for files already downloaded
dwn_files = glob.glob(os.path.join(dwn_pth, "*.pdf"))
exist = [os.path.basename(f)[:-4] for f in dwn_files]

###specify the ID column name
ID = "BRnum"


##########

### read in file
df = pd.read_excel(list_pth, sheet_name=0, index_col=ID)

### filter out rows with no URL
non_empty = df.Pdf_URL.notnull() == True
df = df[non_empty]
df2 = df.copy()


# writer = pd.ExcelWriter(pth+'check_3.xlsx', engine='xlsxwriter', options={'strings_to_urls': False})


### filter out rows that have been downloaded
df2 = df2[~df2.index.isin(exist)]

### loop through dataset, try to download file.
for j in df2.index:
    savefile = str(pth + "dwn/" + str(j) + ".pdf")
    try:
        urllib.request.urlretrieve(df2.at[j, "Pdf_URL"], savefile)
        # if os.path.isfile(savefile):
        # try:
        # pdfFileObj = open(savefile, 'rb')
        # creating a pdf reader object
        # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        # with open(savefile, 'rb') as pdfFileObj:
        # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        # if pdfReader.numPages > 0:
        # df2.at[j, 'pdf_downloaded'] = "yes"
        # else:
        # df2.at[j, 'pdf_downloaded'] = "file_error"

        # except Exception as e:
        # df2.at[j, 'pdf_downloaded'] = str(e)
        # print(str(str(j)+" " + str(e)))
        # else:
        # df2.at[j, 'pdf_downloaded'] = "404"
        # print("not a file")

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        ConnectionResetError,
        Exception,
    ) as e:
        df2.at[j, "error"] = str(e)


# df2.to_excel(writer, sheet_name="dwn")
# writer.save()
# writer.close()
