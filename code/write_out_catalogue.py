#This code writes out the SNe and Galaxy catalogues from simulate_lsst_sne.py and simulate_galaxie.py
#in a format that is ingestible by 4FS - the 4MOST simulations team.
#Author: Elizabeth Swann
#Date last updated: 17/07/18
#################################
from astropy.io import fits
import numpy as np
import os

path_to_master_dir='/mnt/lustre/eswann/TiDES/code/SNcode/Jon_example/'

path_2_out=path_to_master_dir+'output_files/s10_mock_catalogue_JON_VERSION.fits'

#Import galaxy catalogue
gal_z,gal_ra,gal_dec,gal_magr,gal_priority,gal_resolution,gal_template,gal_ruleset,gal_mjd_start,gal_mjd_end=np.loadtxt(path_to_master_dir+'output_files/Galaxy_catalogue.csv',unpack=True,dtype=str,delimiter=',',skiprows=1,usecols=(1,2,3,4,5,6,7,8,12,13))

gal_z=np.array(gal_z,dtype=float)
gal_ra=np.array(gal_ra,dtype=float)
gal_dec=np.array(gal_dec,dtype=float)
gal_magr=np.array(gal_magr,dtype=float)
gal_priority=np.array(gal_priority,dtype=float)
gal_priority=np.array(gal_priority,dtype=int)
gal_resolution=np.array(gal_resolution,dtype=float)
gal_resolution=np.array(gal_resolution,dtype=int)
gal_template=np.array(gal_template,dtype=object)
gal_ruleset=np.array(gal_ruleset,dtype=str)
gal_mjd_start=np.array(gal_mjd_start,dtype=float)
gal_mjd_start=np.array(gal_mjd_start,dtype=int)
gal_mjd_end=np.array(gal_mjd_end,dtype=float)
gal_mjd_end=np.array(gal_mjd_end,dtype=int)

for i in range(len(gal_template)):
	if gal_template[i][-2:]=='_r':
		new_string='{}_r20.fits'.format(gal_template[i][:-2])
		gal_template[i]=new_string
		print gal_template[i]==new_string
	elif gal_template[i][-4:]=='_r20':
		gal_template[i]='{}_r20.fits'.format(gal_template[i][:-4])

#Import supernova catalogue
sn_sub_id,sn_z,sn_ra,sn_dec,sn_rmag,sn_priority,sn_resolution,sn_template,sn_mjd_start,sn_mjd_end,sn_ruleset=np.loadtxt(path_to_master_dir+'output_files/Supernova_catalogue_reduced.csv',unpack=True,dtype=str,delimiter=',',skiprows=1,usecols=(0,1,2,3,4,6,7,8,9,10,11))
sn_sub_id=np.array(sn_sub_id,dtype=float)
sn_sub_id=np.array(sn_sub_id,dtype=int)
sn_z=np.array(sn_z,dtype=float)
sn_ra=np.array(sn_ra,dtype=float)
sn_dec=np.array(sn_dec,dtype=float)
sn_magr=np.array(sn_rmag,dtype=float)
sn_priority=np.array(sn_priority,dtype=float)
sn_priority=np.array(sn_priority,dtype=int)
sn_resolution=np.array(sn_resolution,dtype=float)
sn_resolution=np.array(sn_resolution,dtype=int)
sn_template=np.array(sn_template,dtype=object)
sn_ruleset=np.array(sn_ruleset,dtype=str)
sn_mjd_start=np.array(sn_mjd_start,dtype=float)
sn_mjd_start=np.array(sn_mjd_start,dtype=int)
sn_mjd_end=np.array(sn_mjd_end,dtype=float)
sn_mjd_end=np.array(sn_mjd_end,dtype=int)


for i in range(0,len(sn_template)):
	if sn_template[i][-3:]=='fit':
		sn_template[i]='{}fits'.format(sn_template[i][:-3])


redshift=np.concatenate((sn_z,gal_z))
ra=np.concatenate((sn_ra,gal_ra))
dec=np.concatenate((sn_dec,gal_dec))
magr=np.concatenate((sn_magr,gal_magr))
priority=np.concatenate((sn_priority,gal_priority))
resolution=np.concatenate((sn_resolution,gal_resolution))
template=np.concatenate((sn_template,gal_template))
ruleset=np.concatenate((sn_ruleset,gal_ruleset))
start=np.concatenate((sn_mjd_start,gal_mjd_start))
end=np.concatenate((sn_mjd_end,gal_mjd_end))
obj_id=np.arange(0,len(end))
gal_sub_id=np.array(np.arange(len(sn_sub_id)+1,len(sn_sub_id)+len(gal_ra)+1),dtype=float)
idnum=np.concatenate((sn_sub_id,gal_sub_id))

hdu_cols = fits.ColDefs([
fits.Column(name='OBJECT_ID'     , format='15A', array= idnum ),
fits.Column(name='IDNUM'         , format='1J' , array=obj_id ),
fits.Column(name='RA'            , format='1D' , array=ra ),
fits.Column(name='DEC'           , format='1D' , array=dec ),
fits.Column(name='PRIORITY'      , format='1I' , array=priority ),
fits.Column(name='ORIG_TEXP_B'   , format='1E' , array=np.ones_like(ra)*0. ),
fits.Column(name='ORIG_TEXP_D'   , format='1E' , array=np.ones_like(ra)*0. ),
fits.Column(name='ORIG_TEXP_G'   , format='1E' , array=np.ones_like(ra)*0. ),
fits.Column(name='RESOLUTION'    , format='1B' , array=resolution ),
fits.Column(name='R_MAG'         , format='1E' , array=magr ),
fits.Column(name='TEMPLATE'      , format='100A', array=template ),
fits.Column(name='RULESET'       , format='100A' , array=ruleset ),
fits.Column(name='MJD_START'     , format='1J' , array=start ),
fits.Column(name='MJD_END'       , format='1J' , array=end )
])

tb_hdu = fits.BinTableHDU.from_columns( hdu_cols )
#define the header
prihdr = fits.Header()
prihdr['author'] = 'SWANN'
prihdu = fits.PrimaryHDU(header=prihdr)
#writes the file
thdulist = fits.HDUList([prihdu, tb_hdu])

print( path_2_out )
if os.path.isfile(path_2_out):
        os.system("rm "+path_2_out)
thdulist.writeto(path_2_out)
