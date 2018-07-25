#This code runs all other codes in order, necessary to run the simulation
#Author: Elizabeth Swann
#Date last updated: 23/07/18
#################################

print 'Running SNe Simulation'
print '-----------------------------------------'
#Run the code that generates SN in LSST footprint
execfile('simulate_lsst_sne.py')

print '\nCreating SNe spectra'
print '-----------------------------------------'
#Run the code that generates sn spectra
execfile('make_sn_spectra.py')

print '\nMatching SNe to template'
print '-----------------------------------------'
#Run the code that matches SN observations to the relevant template
execfile('match_sne_to_template.py')

print '\nSimulating SNe host galaxies'
print '-----------------------------------------'
#Run the code that simulates SN host galaxies
execfile('simulate_galaxies.py')

print '\nWriting out final catalogue'
print '-----------------------------------------'
#Run the code that writes the catalogue out in a format understood by 4FS
execfile('write_out_catalogue.py')
