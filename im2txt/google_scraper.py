from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os
import argparse
import sys
import json

# adapted from http://stackoverflow.com/questions/20716842/python-download-images-from-google-image-search

def get_soup(url,header):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)),'html.parser')

def main(query):
	max_images = 100
	save_directory = './im2txt/images/'
	save_directory_2 = './im2txt/saved_images/'
	image_type="Action"
	print(query, 'before split')
	arr= query.split()
	query='+'.join(arr)
	header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
	url="https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
	soup = get_soup(url,header)
	ActualImages=[]# contains the link for Large original images, type of  image
	for a in soup.find_all("div",{"class":"rg_meta"}):
	    link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
	    ActualImages.append((link,Type))
	print(len(ActualImages))
	for i , (img , Type) in enumerate( reversed(ActualImages[0:max_images])):
	    try:
	        req = urllib2.Request(img, headers={'User-Agent' : header})
	        raw_img = urllib2.urlopen(req).read()


	        if Type=="jpg":
	            f = open(os.path.join(save_directory , "img" + "_"+ str(i)+".jpg"), 'wb')
	            k = open(os.path.join(save_directory_2 , query+".jpg"), 'wb')
		    f.write(raw_img)
		    k.write(raw_img)
		    f.close()
		    k.close()
		    break

	    except Exception as e:
	        print "could not load : "+img
	        print e

if __name__ == '__main__':
    from sys import argv
    try:
        main(argv)
    except KeyboardInterrupt:
        pass
    sys.exit()
