#!/home/lmanrique/anaconda3/bin/python3
import os
import sys
import re
import time
from astropy.io import fits

def validate():
	if (len(sys.argv) == 1 or not os.path.isdir(sys.argv[1])):
		return False
	return True

def createList(path):
	listDir = os.listdir(path)
	resp = []
	regex = re.compile(r'^[0-9]{2}[a-zA-Z]{3}[0-9]{2}.?$')
	for ld in listDir:
		if os.path.isdir(sys.argv[1] + '/' + ld) and regex.match(ld): 
			resp.append(ld)		
	return resp

def printDir(listDir):
	for ld in listDir:
		print(os.path.abspath(sys.argv[1]) + '/' + ld)

def removeDir(listDir):
	rm = ['bias', 'flat', 'lixo', '.DS_Store'] # Add to this list the directories that should be ignored by splitHDR
	temp = list(listDir)
	for ld in listDir:
		if ld in rm:
			temp.remove(ld)
	return temp
	#lista do bias e flat (NUMKIN)

def simpleList(path, list_dir):
	for ld in list_dir:
		os.chdir(path + '/' + ld)
		files = os.listdir('.')
		listFile = open(ld + '.list', 'w')
		parent = os.path.dirname(os.getcwd())
		print('Creating a simple list for: ' + parent + '/' + ld)
		for lf in files:
			if lf.split('.')[-1] == 'fits':
				listFile.write(parent + '/' + ld + "/" + lf + "\n")

	
def splitHDR(listDir):
	for ld in listDir:
		temp = os.path.abspath(sys.argv[1]) + '/' + ld
		simpleList(temp, ['bias','flat']) # Add to this list directories that should be listed and not splitted
		os.chdir(temp)
		listObjects = os.listdir('.')
		listObjects = removeDir(listObjects)
		for lo in listObjects:
			if not os.path.isdir(lo): continue
			os.chdir(lo)
			listFile = open(lo + '.list', 'w')
			listFile_no_path = open(lo + '_no_path.list', 'w') 
			parent = os.path.dirname(os.getcwd())
			listFits = os.listdir('.')
			for lf in sorted(listFits):
				if lf.split('.')[-1] == 'fits':
					hdu = fits.open(lf)
					if ('NUMKIN' not in hdu[0].header.keys()) or ('SPLITHDR' in hdu[0].header.keys()): continue
					print('\nProcessing the file: ' + os.path.abspath(lf))
					hdu.info()
					n = hdu[0].header['NUMKIN']
					if n > 0 :
					    header = hdu[0].header
					    header['NUMKIN'] = 1
					    header['SPLITHDR'] = 1
					    header['SOURCE'] = lf
					    for i in range (n):
					        hdu_temp1 = fits.PrimaryHDU(hdu[0].data[i])
					        hdu_temp2 = fits.HDUList([hdu_temp1])
					        hdu_temp2[0].header = header
					        hdu_temp2.writeto(lf[:-len(lf.split('_')[-1])] + str("%02d" % i) + '.fits', overwrite=True)
					        listFile.write(parent + '/' + lo + "/" + lf[:-len(lf.split('_')[-1])] + str("%02d" % i) + '.fits' + "\n")
					        listFile_no_path.write(lf[:-len(lf.split('_')[-1])] + str("%02d" % i) + '.fits' + "\n")
			listFile.close()
			listFile_no_path.close()

			os.chdir('..')
		os.chdir('../..')

#Checking if the argument is a valid directory 
if not validate():
	print('You must specify a valid directory.')
	sys.exit()

#Creating a list of valid subdirectories using the pattern YY/month/DD
listDir = createList(sys.argv[1])

#Listing found directories 
print('The following directories will be processed by splitHDR')
printDir(listDir)
time.sleep(3)
print('')

#Calling the method splitHDR to split fits files using the variable NUMKIN and create a list of
#generated fits files
splitHDR(listDir)