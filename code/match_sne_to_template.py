#This code matchs the supernova created by the code simulate_lsst_sne to the appropriate spectral
#template, as created by make_sn_spectra.py.
#Author: Elizabeth Swann
#Date last updated: 17/07/18
#################################
import numpy as np
from scipy.spatial import cKDTree

path_to_master_dir='/mnt/lustre/eswann/TiDES/code/SNcode/Jon_example/'

myfile=open(path_to_master_dir+'output_files/Catalouge_sne_all_complete.csv','wb')
myfile.write('sn_id,rmag,start_date,end_date,sn_type,redshift,phase_restframe,x1,c,template_name\n')

#Define functions
def get_nearest_neighbour(sn_type,redshift,phase,stretch,colour,temp_name,temp_z,temp_phase,temp_c,temp_x1,k=1):
	idx=np.where(np.array([i.split('_',1)[0] for i in temp_name],dtype=str)==sn_type)[0]
	possible_temp_names=temp_name[idx]
	if sn_type!='SNIa':
		possible_matches=np.dstack([temp_z[idx],temp_phase[idx]])[0]
		sne_params=np.dstack([redshift,phase])[0]
		t=cKDTree(possible_matches)
		d,match_idx=t.query(sne_params,k=k)
		return possible_temp_names[match_idx][0]
	elif sn_type=='SNIa':
		possible_matches=np.dstack([temp_z[idx],temp_phase[idx],temp_c[idx],temp_x1[idx]])[0]
		sne_params=np.dstack([redshift,phase,colour,stretch])[0]
		t=cKDTree(possible_matches)
		d,match_idx=t.query(sne_params,k=k)
		return possible_temp_names[match_idx][0]

#Load in catalogue of the sne

sn_id,rmag,start_date,end_date,sn_type,redshift,phase_restframe,x1,c=np.loadtxt(
	path_to_master_dir+'output_files/Catalouge_sne_all.csv',delimiter=',',unpack=True,usecols=(0,1,2,3,4,5,6,7,8),dtype=str,skiprows=1
	)

sn_id=np.array(sn_id,dtype=int)
rmag=np.array(rmag,dtype=float)
start_date=np.array(start_date,dtype=float)
end_date=np.array(end_date,dtype=float)
redshift=np.array(redshift,dtype=float)
phase_restframe=np.array(phase_restframe,dtype=float)
x1=np.array(x1,dtype=float)
c=np.array(c,dtype=float)

#Load in template information
temp_name,temp_sn_type,temp_redshift,temp_phase,temp_x1,temp_c=np.loadtxt(
	path_to_master_dir+'output_files/template_information.csv',delimiter=',',unpack=True,usecols=(0,1,2,3,4,5),dtype=str,skiprows=1
	)

temp_redshift=np.array(temp_redshift,dtype=float)
temp_phase=np.array(temp_phase,dtype=float)
temp_x1=np.array(temp_x1,dtype=float)
temp_c=np.array(temp_c,dtype=float)

for m in range(len(sn_id)):
	sne_temp_name=get_nearest_neighbour(sn_type[m],redshift[m],phase_restframe[m],x1[m],c[m],temp_name,temp_redshift,temp_phase,temp_c,temp_x1,k=1)
	myfile.write(str(sn_id[m])+','+str(rmag[m])+','+str(start_date[m])+','+str(end_date[m])+','+str(sn_type[m])+','+str(redshift[m])+','+str(phase_restframe[m])+','+str(x1[m])+','+str(c[m])+','+sne_temp_name+'\n')


myfile.close()
