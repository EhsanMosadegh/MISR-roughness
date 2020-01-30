#!/usr/bin/python3
###############################################################################
# run_SurfSeaIce.py
# author: Ehsna Mosadegh (emosadegh@nevada.unr.edu)
# version history: 2 Dec 2019
# usage:
# - 
# data required:
#	inputs: 
#	outputs: 
# to do: 
# - define study domain in terms of path-block
# - 
# notes: 
#   - use python3
# debugging:
#	-
###############################################################################

import os, subprocess
import datetime as dt

###############################################################################
##### directory path setting (by USER) ########################################

# path of root dir that inclides all prcessing directories
root_dir = '/home/mare/Ehsan_lab/misr_proceesing_dir'

#===== input files ============================================================
# path to TOA radiance data (toa-rad_*)
toa_dir_name = 'toa_radiance/proj_july_1_2016' # path to toa dir; should be defined for each project

# path to downloaded geometric files (GP-GMP)
geo_param_dir_name = 'misr_download_files/dl_july_1_16_2016' # path to hdf radiance files reflectance (GRP_ELLIPSOID) files, where we downloaded files

# path to txt file (we are not uing it anymore)
study_domain_POB_file = 'study_domain_POB.txt'

#===== output file ============================================================
# define output directory == surface reflectance data
surf_refl_dir_name = 'surf_reflectance/july_14_2016'

#===== other settings (if you change exe name and/or band number) =========================================
band_no = 2 # 3 for red band; 0,1,2
exe_name = 'TOARad2SurfRefl' # name of executable for cmd command

##### directory path setting (by USER) ########################################
###############################################################################

def main():
	# create a list of POB from the POB list
	# study_domain_POB_list = domain_POB_list_maker(root_dir, study_domain_POB_file)
	# print(study_domain_POB_list)

	# make a list of all available toa files
	toa_file_list, toa_dir = check_toa_files(root_dir, toa_dir_name)
	# check if geo param dir is available
	geo_param_dir = check_GP_file_dir(root_dir, geo_param_dir_name)

	# pick each toa file and parse P,O,B
	for toa_file in toa_file_list:
		print('-> processing toa file: %s' % toa_file)
		toa_path, toa_orbit, toa_block, camera = parse_toa_files(toa_file)
		# # check if toa_file is inside domain, else continue to next toa_file
		# if not (is_toa_inside_domain(study_domain_POB_list, toa_path, toa_orbit, toa_block)):
		# 	continue # to next toa_file to check if the next one is inside of domain or not

		# check for GP file
		return_val = check_GP_files(toa_path, toa_orbit, geo_param_dir)
		# 
		if (return_val == False):
			continue
		else:
			GP_GMP_file_fullpath = return_val

		# define output files for C code; to do: include GP file also
		toa_file_fullpath, surf_file_fullpath, surf_img_fullpath = define_inputs_to_C(root_dir, surf_refl_dir_name, toa_path, toa_orbit, toa_block, camera, toa_dir, toa_file)

		# run the C program
		run_C_exe_from_cmd(exe_name, toa_file_fullpath, GP_GMP_file_fullpath, band_no, surf_file_fullpath, surf_img_fullpath)
	

	return 0

###############################################################################

def check_toa_files(root_dir, toa_dir_name):
	'''
	looks at the toa dir and make a list of the available files from there
	to do: check directory exists: toa_dir
	'''
	toa_dir = os.path.join(root_dir, toa_dir_name) # check exists
	print('-> toa dir: %s' %toa_dir)
	toa_file_list = sorted(os.listdir(toa_dir))
	print('-> list of toa files: %s' %len(toa_file_list))

	return toa_file_list, toa_dir

###############################################################################

def parse_toa_files(toa_file):
	#print('-> toa file is: %s' %toa_file)

	# extract p,o,b
	if toa_file.endswith('.dat'):

		# define toa path 
		i = toa_file.index('_P')
		#print('i is: %s' %i)
		toa_path = int(toa_file[i + 2: i + 5])
		#print('path: %s' %toa_path)

		# define toa orbit
		i = toa_file.index('_O')
		toa_orbit = int(toa_file[i + 2: i + 8])
		#print('orbit: %s' %toa_orbit)

		# define toa block
		i = toa_file.index('_B')
		#print('index of block: %s' %i)
		toa_block = int(toa_file[i + 2: i + 4])
		#print('block: %s' %toa_block)

		# define camera
		camera = '??'
		if toa_file.find('_cf') > -1:
			camera = 'cf'
		elif toa_file.find('_ca') > -1:
			camera = 'ca'
		# Ehsan: how about camera==an??? I added here
		elif toa_file.find('_an') > -1:
			camera = 'an'

	return toa_path, toa_orbit, toa_block, camera

###############################################################################

# def is_toa_inside_domain(study_domain_POB_list, toa_path, toa_orbit, toa_block):
# 	'''
# 	we compare each toa_file with all domain_POB. if toa file is in the domain, we output "toa_file_fullpath"
# 	as the processing file for C code, else we skip to next toa file
# 	only check if toa_file is inside the domain
# 	'''
# 	for domain_POB in study_domain_POB_list:  # l=?????; study_domain_POB_list, Q- for specific region??? does study_domain_POB_list define our study domain? how to obtain POB for the a study region?
# 		print('-> POB of domain: %s' %str(domain_POB))
# 		# print('-> path from domain: %s' %domain_POB[0])
# 		# print('-> path from toa file: %s' %toa_path)

# 		# now cross-check p/o/b with the list/ if toa_pob matches with the domain:
# 		if (domain_POB[0] == toa_path and domain_POB[1] == toa_orbit and domain_POB[2] == toa_block):
# 			print('-> toa_file is inside domain!')
# 			return True
# 		else:
# 			print('-> toa_file NOT inside domain, continue')
# 			return False

###############################################################################

# def domain_POB_list_maker(root_dir, study_domain_POB_file):
# 	'''
# 	creates a list of POB from the POB list
# 	'''
# 	study_domain_POB_list = [] # a list of desired toa_p-o-b --> ???????????????????????????? what is this list? where is it coming from? how can I make it for each project?  
# 	with open(os.path.join(root_dir, study_domain_POB_file), 'r') as file_obj: # this list has a list of desired (path-orbit-block)
# 		domain_POB_file = file_obj.readlines()

# 		for line in domain_POB_file:

# 			fields = line.strip().split(',')  # format of the file???
# 			#print(type(fields))
# 			domain_path = int(fields[0])
# 			domain_orbit = int(fields[1])
# 			domain_block = int(fields[2])
# 			study_domain_POB_list.append((domain_path, domain_orbit, domain_block))
	
# 	print('-> POB list: %s' %study_domain_POB_list)

# 	return study_domain_POB_list

###############################################################################

def define_inputs_to_C(root_dir, surf_refl_dir_name, toa_path, toa_orbit, toa_block, camera, toa_dir, toa_file):
	# to do: include GP file pattern,

	toa_file_fullpath = os.path.join(toa_dir, toa_file) # if toa file in the list is availabe in the dir, then pich the toa.dat -> fname1 = toa.dat
	#print('-> toa path for C program: %s' %toa_file_fullpath)

	# define output dir- add toa file fullpath
	output_dir = os.path.join(root_dir, surf_refl_dir_name)
	# define output files
	surf_file_name = ('surf_refl_P%03d_O%06d_B%03d_%s.dat' % (toa_path, toa_orbit, toa_block, camera)) # dir1 and dir2 = output dir for surface reflectance
	surf_img_name = ('surf_refl_P%03d_O%06d_B%03d_%s.png' % (toa_path, toa_orbit, toa_block, camera))	# if camera is cf, it goes to dir1
	# join data file names and paths now 
	surf_file_fullpath = os.path.join(output_dir, surf_file_name)
	surf_img_fullpath = os.path.join(output_dir, surf_img_name)

	return toa_file_fullpath, surf_file_fullpath, surf_img_fullpath

###############################################################################

def check_GP_file_dir(root_dir, geo_param_dir_name):
	'''
	looks for a geometric parameter file that matches the path-orbit,
	if finds the GP file returns a GP full path, else returns False
	'''
	# to-do: edit download script to seperate files to 2 folders for ellipoid and geometric, 
	# here refer to only geometric dir and make a list only from geometric files
	geo_param_dir = os.path.join(root_dir, geo_param_dir_name)
	print('-> geo-param dir= %s' , geo_param_dir)

	return geo_param_dir

###############################################################################

def check_GP_files(toa_path, toa_orbit, geo_param_dir):
	'''
	looks for a geometric parameter file that matches the path-orbit,
	if finds the GP file returns a GP full path, else returns False

	'''
	GP_file_pattern = ('MISR_AM1_GP_GMP_P%03d_O%06d_F03_0013' % (toa_path, toa_orbit))
	#print("GP file pattern is:" , GP_file_pattern)

	# # to-do: edit download script to seperate files to 2 folders for ellipoid and geometric, 
	# # here refer to only geometric dir and make a list only from geometric files
	# geo_param_dir = os.path.join(root_dir, geo_param_dir_name)
	# print('-> geo param dir= %s' % geo_param_dir)

	# now make a list from all files in the GP directory
	list_of_all_avail_GP_files = sorted(os.listdir(geo_param_dir))
	#print('list of GP files:')
	#print(list_of_all_avail_GP_files)

	# now check each GP file inside the available list
	for each_avail_GP_file in list_of_all_avail_GP_files:
		#print("-> checking GP file:" , (each_avail_GP_file))
		# check if thats the file we are looking for:
		if each_avail_GP_file.startswith(GP_file_pattern) and each_avail_GP_file.endswith('.hdf'):
		
			GP_GMP_file_fullpath = os.path.join(geo_param_dir, each_avail_GP_file)
			print('-> GP file found: %s' %GP_GMP_file_fullpath)
			return GP_GMP_file_fullpath

		else:
			print('-> geometric parametr file NOT found!')
			return False

###############################################################################

def run_C_exe_from_cmd(exe_name, toa_file, GP_GMP_file_fullpath, band_no, surf_file_fullpath, surf_img_fullpath):

	cmd = ('%s %s \"%s\" \"%s\" %s %s' %(exe_name, toa_file, GP_GMP_file_fullpath, band_no, surf_file_fullpath, surf_img_fullpath)) # band=? before surf_file_fullpath; bandshould be 2 similar to run_TOA.py
	# run the cmd command
	return_value_of_cmd = subprocess.call(cmd, shell=True)
	print('-> return value of cmd= %s' %return_value_of_cmd)

	if (return_value_of_cmd < 0): # what it means?
		print('-> ERROR: %s.exe NOT found in $PATH. Exiting...' %exe_name) 
		raise SystemExit()

	if (return_value_of_cmd == 1): # what it means?
		print('-> ERROR: something went wrong. Exiting...') 
		raise SystemExit()

###############################################################################

if __name__ == '__main__':

	start_time = dt.datetime.now()
	print("-> running program: %s" % exe_name)
	print('-> start time: %s' % start_time)
	print(" ")
	main()
	end_time = dt.datetime.now()
	print('-> end time= %s' % end_time)
	print('-> runtime duration= %s' % (end_time-start_time))
	print(" ")
	print('######################## SurfSeaIce COMPLETED SUCCESSFULLY ########################')