import numpy as np
from netCDF4 import Dataset
import pandas as pd
''' The following functions convert GOES Fixed Grid Format 
x/y points to lat/lon and from lat/lon to x/y
- The key reference is https://www.goes-r.gov/users/docs/PUG-L1b-vol3.pdf
- Around page 8 the fixed grid section starts
'''

def GOES_xy_to_latlon(data,x_o,y_o):
    '''Input data as read by netCDF4 Dataset('file','r'), x_o, y_o
    are also from netCDF4 variables as 
    x = data.variables['x'][:]
    y = data.variables['y'][:]
    then, pull a value of x and y as x_o,y_o to convert'''    
    req = data['goes_imager_projection'].semi_major_axis
    inv_flat = data['goes_imager_projection'].inverse_flattening
    rpol = data['goes_imager_projection'].semi_minor_axis
    e = 0.0818191910435
    pers_h = data['goes_imager_projection'].perspective_point_height
    H = pers_h + req
    Lo = np.radians(data['goes_imager_projection'].longitude_of_projection_origin)
    
    a = np.sin(x_o)**2+np.cos(x_o)**2*(np.cos(y_o)**2+req**2/rpol**2*np.sin(y_o)**2)
    b = -2*H*np.cos(x_o)*np.cos(y_o)
    c = H**2-req**2
    rs = (-b-np.sqrt(b**2-4*a*c))/(2*a)
    sx = rs*np.cos(x_o)*np.cos(y_o)
    sy = -rs*np.sin(x_o)
    sz = rs*np.cos(x_o)*np.sin(y_o)
    
    
    lat_p1 = req**2/rpol**2
    lat_p2 = np.sqrt((H-sx)**2+sy**2)
    
    lat = np.degrees(np.arctan(lat_p1*sz/lat_p2))
    
    lon = np.degrees(Lo-np.arctan((sy/(H-sx))))
    return lat,lon
    
    
def latlon_to_GOES_xy(data,lat,lon):
    '''Give lat/lon in degrees'''
    req = data['goes_imager_projection'].semi_major_axis
    rpol = data['goes_imager_projection'].semi_minor_axis
    e = 0.0818191910435
    pers_h = data['goes_imager_projection'].perspective_point_height
    H = pers_h + req
    Lo = np.radians(data['goes_imager_projection'].longitude_of_projection_origin)
    
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    
    latc = np.arctan(rpol**2/req**2*np.tan(lat_r))
    
    rc = rpol/np.sqrt(1-e**2*np.cos(latc)**2)
    
    sx = H-rc*np.cos(latc)*np.cos(lon_r-Lo)
    sy = -rc*np.cos(latc)*np.sin(lon_r-Lo)
    sz = rc*np.sin(latc)
    
    yn = np.arctan(sz/sx)
    xn = np.arcsin((-sy/(np.sqrt(sx**2+sy**2+sz**2))))
    return xn,yn
        










