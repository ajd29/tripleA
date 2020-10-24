#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 10:28:39 2020

@author: ebw29954

Do not distribute the code within this package.

Your own due diligence will be required to make sure the image processing
and extracted chips are being performed as desired and over the location of interest.
This code should provide a good start to creating image chips to train on.
"""


from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from skimage import io
import os
import lat_lon_from_goes as llfg
import pickle as pk

class ABI_Process(object):
    def __init__(self,center_lat,center_lon,buffer,save_directory=None,cmap=None,norm=None):
        '''Script to subset region from GOES-16 imagery and save chips.
        center_lat - latitude in degrees of desired scene center (float)
        center_lon - latitude in degrees of desired scene center (float)
        buffer     - number of  pixels around scene center to include in chip (int)
        save_directory - path/to/desired/save/location (str)
        cmap - matplotlib object loaded from a pkl file; optional, may be useful for saving colorized chips
        norm - matplotlib object loaded from a pkl file; optional, may be useful for saving colorized chips'''

        self.center_lat = center_lat
        self.center_lon = center_lon
        self.buffer = buffer

        self.save_directory = save_directory
        if self.save_directory:
            os.makedirs(self.save_directory,exist_ok=True)
        self.cmap = cmap
        self.norm = norm

    def channel_proc(self,file_path,save=True):
        '''Pull image subregion from netcdf file and save chips if desired
        file_path - /path/to/netcdf/file (str)
        save      - option to save out chips (bool)'''

        #Read the .nc file
        data = Dataset(file_path,'r')

        #Load image x,y arrays
        X =  data.variables['x'][:]
        Y =  data.variables['y'][:]

        #Convert lat/lon to image relative x/y - treating lat/lon as scene center
        center_x,center_y = llfg.latlon_to_GOES_xy(data,self.center_lat,self.center_lon)

        #Pull the data array - it is a masked array; you should not need to worry about the mask here
        #The mask is only for removing points outside Earth's limb, which we won't be near anyway.
        #CMI here is already floating point Brightness Temperature - you shoudl not need to do anything else
        CMI = data.variables['CMI'][:] #.data

        #Determine closest image pixel location to center_x,center_y
        diff_x = np.abs(center_x - X)
        xmin = np.argmin(diff_x)
        diff_y = np.abs(center_y-Y)
        ymin = np.argmin(diff_y)

        #Chip the scene around the center based on buffer pixels
        CMI_sub = CMI[ymin-self.buffer:ymin+self.buffer,xmin-self.buffer:xmin+self.buffer]

        time_coverage_start = data.time_coverage_start
        time_coverage_end   = data.time_coverage_end
        tag = '_'.join(['Chip',time_coverage_start,time_coverage_end])

        if save:
            self.save_native_chip(CMI_sub,'_'.join(['Native',tag]))
            self.save_colorized_chip(CMI_sub,'_'.join(['Colorized',tag]),self.cmap,self.norm)

    def save_native_chip(self,chip,chip_tag,im_type='png'):
        #im_type of "tif" will allow you to save the native float32 brightness temperature; you will need
        #some software to view the images easily - e.g., imageJ/ or load into Python
        #you can always rescale to 8 bit jpg or 8 or 16 bit png if it suits you - these will be easily viewable
        out_path = os.path.join(self.save_directory,'.'.join([chip_tag,im_type]))
        io.imsave(out_path,chip)

    def save_colorized_chip(self,chip,chip_tag,cmap,norm,im_type='png'):
        chip-=273.15 #convert from K to C --> needed if using provided pkl colormap itemsssssssss
        cmap.set_under('k')
        out_path = os.path.join(self.save_directory,'.'.join([chip_tag,im_type]))
        plt.ioff() #keeps figure from opening
        im  = plt.imshow(chip, cmap=cmap, norm=norm,alpha=None)
        rgb = im.cmap(im.norm(chip)) #convert im to rgb to save out native resolution chip
        io.imsave(out_path,rgb)


if __name__=="__main__":

    center_lat = 28.3922   #approx lat of Cape Canaveral
    center_lon = -80.6077  #appeox lon of Cape Canaveral
    buffer = 200 #pixels - choose large enough area to capture evolving weather ; 200 ~= 400km x 400km area

    # file_folder = '/home/ebw29954/VT_Capstone/FY21_Example_Process/Files'
    file_folder = '/Users/allisondesantis/school/fall_2020/capstone/aerospace\
    /scripts/FY21_Example_Process'
    save_folder = '/Users/allisondesantis/school/fall_2020/capstone/aerospace\
    /scripts/FY21_Example_Process'

    files = glob(os.path.join(file_folder,'*.nc'))

    #Optional - the colormap files here map the brightness temperature to a commonly used colormap by NOAA
    #You can totally skip this or save cihps out however you want
    colormap_path = '/Users/allisondesantis/school/fall_2020/capstone/aerospace\
    /scripts/FY21_Example_Process'
    IR_TPC_R_CMAP_path = os.path.join(colormap_path,'LongwaveInfraredDeepConvection_CMAP.pk')
    IR_TPC_R_NORM_path = os.path.join(colormap_path,'LongwaveInfraredDeepConvection_NORM.pk')
    with open(IR_TPC_R_CMAP_path,'rb') as cmap_file, open(IR_TPC_R_NORM_path,'rb') as norm_file:
        IR_TPC_R_CMAP = pk.load(cmap_file,fix_imports=True,encoding='latin1')
        IR_TPC_R_NORM= pk.load(norm_file,fix_imports=True,encoding='latin1')

    #Initialize  processing class
    ABI_proc = ABI_Process(center_lat,center_lon,buffer,save_directory=save_folder,cmap=IR_TPC_R_CMAP,norm=IR_TPC_R_NORM)
    #Process a file
    ABI_proc.channel_proc(files[0])
