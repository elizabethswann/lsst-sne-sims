#This code generates SN template spectra. It does this for SN Ia and CC SN. It
#generates the spectra at a variety of SN phases, color, stretch and redshifts.
#All the templates are then scaled to an r-band sdss magnitude of 16.5.
#Author: Elizabeth Swann
#Date last updated: 17/07/18
#################################
#Imports
import matplotlib
matplotlib.use('agg')
import numpy as np
import sncosmo
from astropy.table import Table
from astropy.cosmology import FlatLambdaCDM, z_at_value
import astropy.units as u
import random
from astropy.io import fits
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from astropy import constants as const
#################################
#Define parameters

path_to_master_dir='/mnt/lustre/eswann/TiDES/code/SNcode/Jon_example/'
#################################

cosmo = FlatLambdaCDM(H0=70, Om0=0.3)

np.random.seed(12334423)

myfile=open(path_to_master_dir+'output_files/template_information.csv','wb')
myfile.write('template_name,sn_type,redshift,phase_restframe,x1,c\n')

#Set up survey parameters
mjd_start=0.
mjd_end=1000.

t0=100.

dm_Ia=24 - -19.1
dm_Ib = 24 - -17.54
dm_Ic = 24 - -17.67
dm_IIL = 24 - -17.98
dm_IIP = 24 - -16.8

#Phases from explosion date
phases_Ia=[10,20,30,45]
phases_91t=[18.,36.,54.,72.]
phases_91bg=[22.,44.,66.,88.]
phases_Ib=[35.,70.,105.,140.]
phases_Ic=[35.,70.,105.,140.]
phases_IIL=[40.,80.,120.,190.]
phases_IIP=[20.,40.,60.,80.]

start_phase_Ia=-20.
start_phase_91t=0.
start_phase_91bg=0.
start_phase_Ib=-35.3
start_phase_Ic=-35.37
start_phase_IIL=0.
start_phase_IIP=-19.

stretch=[-0.3,-0.15,0.0,0.15,0.3]
colour=[-0.1,-0.05,0.,0.05,0.1]

ab = sncosmo.get_magsystem('ab')
#################################


#Get redshifts
def get_redshifts(max_redshift):
	redshifts=list(np.arange(0.02,max_redshift+0.02,0.02))
	return redshifts

#Maximum z to which we can see SNe with LSST
def zmax(dm):
	return z_at_value(cosmo.distmod, dm*u.mag)

redshifts_Ia=get_redshifts(zmax(dm_Ia))
redshifts_91T=get_redshifts(zmax(dm_Ia))
redshifts_91bg=get_redshifts(zmax(dm_Ia))
redshifts_Ib=get_redshifts(zmax(dm_Ib))
redshifts_Ic=get_redshifts(zmax(dm_Ic))
redshifts_IIL=get_redshifts(zmax(dm_IIL))
redshifts_IIP=get_redshifts(zmax(dm_IIP))

#Define date in observer frame from phase
def get_date_spectrum(phase,start_phase,t0,redshift):
	mjd_spectrum=((phase+start_phase)*(1.+redshift))+t0
	return mjd_spectrum

#Define function to write out spectrum (for everything expect normal Ia's)
def write_out_spectrum(redshifts,model,phases,start_phase,peakabsmag,sn_type):
	for k in range(len(redshifts)):
		for l in range(len(phases)):
			model.set(z=redshifts[k],t0=t0)
			model.set_source_peakabsmag(peakabsmag,band='bessellb',magsys='ab')

			date_wanted=get_date_spectrum(phases[l],start_phase,t0,redshifts[k])
			wavelengths=np.arange(model.minwave(),model.maxwave(),1)

			flux=model.flux(date_wanted,wave=wavelengths)	#erg/s/cm2/AA
	
			actual_mag=get_magnitude(wavelengths,flux,flambda)
			if np.isfinite(actual_mag)==False:
				continue
			rescale_by=(10.**((16.5)/-2.5)) / (10.**((actual_mag)/-2.5))
	
			flux_new=flux*rescale_by	#erg/s/cm2/AA
			new_mag=get_magnitude(wavelengths,flux_new,flambda)
			#In the below set x1 and c to -99. as they are not parameters for these SNe
			write_out(sn_type,new_mag,flux_new,wavelengths,redshifts[k],phases[l],-99.,-99.)

			filename=str(sn_type)+'_z_'+str('%.2f' % redshifts[k])+'_phase_'+str('%.2f' % phases[l])+'.fits'
			myfile.write(filename+','+sn_type+','+str(redshifts[k])+','+str(phases[l])+',-99.,-99.\n')
	return

#Function to write out the fits file in the correct format
def write_out(sntype,mag,flux,wavelength,redshift,phase,stretch,colour):
	if sntype=='SNIa':
		filename=path_to_master_dir+'sn_spectra/'+str(sntype)+'_z_'+str('%.2f' % redshift)+'_phase_'+str('%.2f' % phase)+'_x1_'+str('%.2f' % stretch)+'_c_'+str('%.2f' % colour)+'.fits'
	else:
		filename=path_to_master_dir+'sn_spectra/'+str(sntype)+'_z_'+str('%.2f' % redshift)+'_phase_'+str('%.2f' % phase)+'.fits'
	new_cols=fits.ColDefs([
		fits.Column(name='LAMBDA',format='D', array=wavelength, unit='Angstrom'),
		fits.Column(name='FLUX',format='D', array=flux, unit='erg/cm2/s/A'),
	])
				
	hdr=fits.Header()
	hdr['ABMAG']=np.round(mag,1)
	hdr['author']='ESwann'
	prim_hdu=fits.PrimaryHDU(header=hdr)
	
	data_hdu=fits.BinTableHDU.from_columns(new_cols)
	g = fits.HDUList([prim_hdu,data_hdu])
	g.writeto(filename, clobber=True)
		
	#print model.bandflux('sdssr',[t0,])
	#plt.plot(wavelength,flux)
	return

def find_abs(z):
	return 16.5-(5.*np.log10(cosmo.luminosity_distance(z).value))-25.


#Define function to claculate magnitude in the sdssr band
sdssr_wave,sdssr_trans=np.loadtxt(path_to_master_dir+'input_data_files/rSDSS.filter.txt',skiprows=1,usecols=(0,1),unpack=True,delimiter=' ')
sdssr_wave=sdssr_wave*u.AA
sdssr_wave_nu=sdssr_wave.to(u.Hz,equivalencies=u.spectral())	#Transmission as function of nu
flambda=interp1d(sdssr_wave, sdssr_trans, kind='cubic',fill_value=0.,bounds_error=False)

def get_magnitude(wavelengths,flux,flambda):
	wavelength=wavelengths*u.AA
	flux=flux*u.erg/u.s/(u.cm**2)/u.AA
	
	sdss_trans_lambda=flambda(wavelength)
	
	f_ab_nu=np.ones(len(wavelength.value))*3631.*(10.**-23.)	#erg/s/cm2/Hz
	f_ab=f_ab_nu*3.*(10.**18)/(wavelength.value**2.)
	
	upper_int=sdss_trans_lambda*flux.value*wavelength.value
	lower_int=f_ab*sdss_trans_lambda*wavelength.value
	
	int_upper=np.trapz(upper_int,wavelength.value)
	int_lower=np.trapz(lower_int,wavelength.value)
	
	magnitude=-2.5*np.log10(int_upper/int_lower)
	return magnitude

#######################################################################
#Create Ia parameters
sn_type='SNIa'

ab = sncosmo.get_magsystem('ab')
source = sncosmo.get_source(name='salt2', version='2.4')
model = sncosmo.Model(source=source)
band_r=sncosmo.get_bandpass('sdssr')
zp=ab.band_flux_to_mag(1.,band_r)

plt.figure()

#Generate spectra for Ia supernovae with various phases, stretch, colour and redshifts
#Note: Do not use the function above as it doesn't include colour or stretch write out
for k in range(len(redshifts_Ia)):
	for j in range(len(phases_Ia)):
		for l in range(len(stretch)):
			for m in range(len(colour)):
				model.set(z=redshifts_Ia[k],c=colour[m],x1=stretch[l],t0=t0)
				model.set_source_peakabsmag(-19.1,band='bessellb',magsys='ab',cosmo=cosmo)
				
				date_wanted=get_date_spectrum(phases_Ia[j],start_phase_Ia,t0,redshifts_Ia[k])
				wavelengths=np.arange(model.minwave(),model.maxwave(),1)
				flux=model.flux(date_wanted,wave=wavelengths)	#erg/s/cm2/AA

				actual_mag=get_magnitude(wavelengths,flux,flambda)

				rescale_by=(10.**((16.5)/-2.5)) / (10.**((actual_mag)/-2.5))

				flux_new=flux*rescale_by	#erg/s/cm2/AA

				new_mag=get_magnitude(wavelengths,flux_new,flambda)

				#plt.plot(wavelengths,flux_new,label='%.2f' % redshifts_Ia[k])
				write_out(sn_type,new_mag,flux_new,wavelengths,redshifts_Ia[k],phases_Ia[j],stretch[l],colour[m])
				filename=str(sn_type)+'_z_'+str('%.2f' % redshifts_Ia[k])+'_phase_'+str('%.2f' % phases_Ia[j])+'_x1_'+str('%.2f' % stretch[l])+'_c_'+str('%.2f' % colour[m])+'.fits'
				myfile.write(filename+','+sn_type+','+str(redshifts_Ia[k])+','+str(phases_Ia[j])+','+str(stretch[l])+','+str(colour[m])+'\n')

#plt.xlabel(r'Wavelength $\AA$')
#plt.ylabel(r'Spectral flux density ergs/s/cm$^{2}$/$\AA$')
#plt.xlim(2000,10000)
#plt.legend(loc='best',ncol=2,fancybox=True,title='Redshift')
#plt.savefig('Ia_spectra.png')

print 'Type Ia done'

#91T
sn_type='SNIa-91T'
source=sncosmo.get_source(name='nugent-sn91t')
model=sncosmo.Model(source=source)
peakabsmag=-19.4

write_out_spectrum(redshifts_91T,model,phases_91t,start_phase_91t,peakabsmag,sn_type)

print '91T done'

#-------------------------------------------------------------------------------------------------
#Create Ia-91bg parameters
#-------------------------------------------------------------------------------------------------
source=sncosmo.get_source(name='nugent-sn91bg')
model=sncosmo.Model(source=source)
sn_type='SNIa-91bg'
peakabsmag=-18.5
write_out_spectrum(redshifts_91bg,model,phases_91bg,start_phase_91bg,peakabsmag,sn_type)

print '91bg done'

#-------------------------------------------------------------------------------------------------
#Create Ib parameters
#-------------------------------------------------------------------------------------------------
source=sncosmo.get_source(name='snana-2004gv')
model=sncosmo.Model(source=source)
sn_type='SNIb'
peakabsmag=-17.54
write_out_spectrum(redshifts_Ib,model,phases_Ib,start_phase_Ib,peakabsmag,sn_type)

print 'Ib done'

#-------------------------------------------------------------------------------------------------
#Create Ic parameters
#-------------------------------------------------------------------------------------------------
source=sncosmo.get_source(name='snana-2004fe')
model=sncosmo.Model(source=source)
sn_type='SNIc'
peakabsmag=-17.67
write_out_spectrum(redshifts_Ic,model,phases_Ic,start_phase_Ic,peakabsmag,sn_type)

print 'Ic done'

#-------------------------------------------------------------------------------------------------
#Create IIP parameters
#-------------------------------------------------------------------------------------------------
source=sncosmo.get_source(name='s11-2004hx')
model=sncosmo.Model(source=source)
sn_type='SNIIP'
peakabsmag=-16.8
write_out_spectrum(redshifts_IIP,model,phases_IIP,start_phase_IIP,peakabsmag,sn_type)

print 'IIP done'

#-------------------------------------------------------------------------------------------------
#Create IIL parameters
#-------------------------------------------------------------------------------------------------
source=sncosmo.get_source(name='nugent-sn2l')
model=sncosmo.Model(source=source)
sn_type='SNIIL'
peakabsmag=-17.98
write_out_spectrum(redshifts_IIL,model,phases_IIL,start_phase_IIL,peakabsmag,sn_type)

print 'IIL done, Finished'

myfile.close()
