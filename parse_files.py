  
import subprocess
import glob
import os
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
from tqdm import tqdm
import numpy as np
import argparse
import re
import time

# PROCESS ARGUMENTS
def read_args():
	parser = argparse.ArgumentParser(description='Script that parses a movie script pdf/txt into its constituent classes')
	parser.add_argument("-i", "--input", help="Path to script PDF/TXT to be parsed", required=True)
	parser.add_argument("-o", "--output", help="Path to directory for saving output", required=True)
	parser.add_argument("-a", "--abridged", help="Print abridged version (on/off)", default='off')
	parser.add_argument("-t", "--tags", help="Print class label tags (on/off)", default='off')
	args = parser.parse_args()
	if args.abridged not in ['on', 'off']: raise AssertionError("Invalid value. Choose either off or on")
	if args.tags not in ['on', 'off']: raise AssertionError("Invalid value. Choose either off or on")
	return os.path.abspath(args.input), os.path.abspath(args.output), args.abridged, args.tags


# READ FILE
def read_file(file_orig):
	if file_orig.endswith(".pdf"):
		file_name = file_orig.replace('.pdf', '.txt')
		subprocess.call('pdftotext -layout ' + file_orig + ' ' + file_name, shell=True)
	elif file_orig.endswith(".txt"):
		file_name = file_orig
	else:
		raise AssertionError("File should be either pdf or txt")
    
	fid = open(file_name, 'r')
	script_orig = fid.read().splitlines()
	fid.close()
	return script_orig


# DETECT SCENE BOUNDARIES:
# LOOK FOR ALL-CAPS LINES CONTAINING "INT." OR "EXT."
def get_scene_bound(script_noind, tag_vec, tag_set, bound_set):
	bound_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and \
														x.isupper() and \
														any([y in x.lower() for y in bound_set])]
	if len(bound_ind) > 0:
		for x in bound_ind:
			tag_vec[x] = 'S'
    
	return tag_vec, bound_ind


# DETECT TRANSITIONS:
# LOOK FOR ALL-CAPS LINES PRECEDED BY NEWLINE, FOLLOWED BY NEWLINE AND CONTAINING "CUT " OR "FADE "
def get_trans(script_noind, tag_vec, tag_set, trans_thresh, trans_set):
	re_func = re.compile('[^a-zA-Z ]')
	trans_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()\
														and len(re_func.sub('', x).split()) < trans_thresh\
														and any([y in x for y in trans_set])]
	if len(trans_ind) > 0:
		for x in trans_ind:
			tag_vec[x] = 'T'
    
	return tag_vec, trans_ind


# DETECT METADATA:
# LOOK FOR CONTENT PRECEDING SPECIFIC PHRASES THAT INDICATE BEGINNING OF MOVIE
def get_meta(script_noind, tag_vec, tag_set, meta_thresh, meta_set, sent_thresh, bound_ind, trans_ind):
	re_func = re.compile('[^a-zA-Z ]')
	met_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set\
														and i != 0 and i != (len(script_noind) - 1)\
														and len(x.split()) < meta_thresh\
														and re_func.sub('', script_noind[i - 1]) == ''\
														and re_func.sub('', script_noind[i + 1]) == ''\
														and any([y in x for y in meta_set])]
	sent_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set\
														and i != 0 and i != (len(script_noind) - 1)\
														and len(x.split()) > sent_thresh\
														and script_noind[i - 1] == ''\
														and script_noind[i + 1] != '']
	meta_ind = sorted(met_ind + bound_ind + trans_ind + sent_ind)
	if len(meta_ind) > 0:
		for i, x in enumerate(script_noind[: meta_ind[0]]):
			if len(x.split()) > 0:
				tag_vec[i] = 'M'
    
	return tag_vec


# DETECT CHARACTER-DIALOGUE BLOCKS:
# CHARACTER IS ALL-CAPS LINE PRECEDED BY NEWLINE AND NOT FOLLOWED BY A NEWLINE
# DIALOGUE IS WHATEVER IMMEDIATELY FOLLOWS CHARACTER
# EITHER CHARACTER OR DIALOGUE MIGHT CONTAIN DILAOGUE METADATA; WILL BE DETECTED LATER
def get_char_dial(script_noind, tag_vec, tag_set, char_max_words):
	char_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()\
														and i != 0 and i != (len(script_noind) - 1)\
														and script_noind[i - 1] == ''\
														and script_noind[i + 1] != ''\
														and len(x.split()) < char_max_words]
	for x in char_ind:
		tag_vec[x] = 'C'
		dial_flag = 1
		while dial_flag > 0:
			line_ind = x + dial_flag
			if script_noind[line_ind] != '':
				if '(' in script_noind[line_ind] and ')' in script_noind[line_ind].split('(')[1]:
					tag_vec[line_ind] = 'E'
				else:
					tag_vec[line_ind] = 'D'
                
				dial_flag += 1
			else:
				dial_flag = 0
    
	return tag_vec


# DETECT SCENE DESCRIPTION
# LOOK FOR REMAINING LINES THAT ARE NOT PAGE BREAKS
def get_scene_desc(script_noind, tag_vec, tag_set):
	desc_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x != ''\
															and not x.strip('.').isdigit()]
	for x in desc_ind:
		tag_vec[x] = 'N'
    
	return tag_vec


# COMBINE MULTI-LINE CLASSES, SPLIT MULTI-CLASS LINES
def combine_tag_lines(tag_valid, script_valid):
	tag_final = []
	script_final = []
	for i, x in enumerate(tag_valid):
		if x in ['M', 'T', 'S']:
			# APPEND METADATA, TRANSITION AND SCENE BOUNDARY LINES AS THEY ARE
			tag_final.append(x)
			script_final.append(script_valid[i])
		elif x in ['C', 'D', 'N']:
			# IF CHARACTER, DIALOGUE OR SCENE DESCRIPTION CONSIST OF MULTIPLE LINES, COMBINE THEM
			if i == 0 or x != tag_valid[i - 1]:
				# INITIALIZE IF FIRST OF MULTIPLE LINES
				to_combine = []
            
			to_combine += script_valid[i].split()
			if i == (len(tag_valid) - 1) or x != tag_valid[i + 1]:
				combined_str = ' '.join(to_combine)
				if x == 'N':
					# IF SCENE DESCRIPTION, WRITE AS IT IS
					tag_final.append(x)
					script_final.append(combined_str)
				else:
					if '(' in combined_str and ')' in combined_str:
						# IF DIALOGUE METADATA PRESENT, EXTRACT IT
						dial_met = ''
						rem_str = ''
						while '(' in combined_str and ')' in combined_str:
							split_1 = combined_str.split('(')
							rem_str += ' ' + split_1[0]
							dial_met += ' ' + split_1[1].split(')')[0]
							combined_str = ')'.join(combined_str.split(')')[1: ])
                        
						rem_str += ' ' + combined_str
						rem_str = ' '.join(rem_str.split())
						dial_met = ' '.join(dial_met.split())
						if x == 'C':
							# IF CHARACTER, APPEND DIALOGUE METADATA
							tag_final.append(x)
							script_final.append(' '.join(rem_str.split()))
							tag_final.append('E')
							script_final.append(dial_met)
						elif x == 'D':
							# IF DIALOGUE, PREPEND DIALOGUE METADATA
							tag_final.append('E')
							script_final.append(dial_met)
							tag_final.append(x)
							script_final.append(' '.join(rem_str.split()))
					else:
						# IF NO DIALOGUE METADATA, WRITE AS IT IS
						tag_final.append(x)
						script_final.append(combined_str)
		elif x == 'E':
			# IF DIALOGUE METADATA LINE, WRITE WITHOUT PARENTHESIS
			split_1 = script_valid[i].split('(')
			split_2 = split_1[1].split(')')
			dial_met = split_2[0]
			tag_final.append('E')
			script_final.append(dial_met)
    
	return tag_final, script_final


# MERGE CONSECUTIVE IDENTICAL CLASSES
def merge_tag_lines(tag_final, script_final):
	merge_ind = [i for i in range(len(tag_final) - 1) if tag_final[i + 1] != 'M' and \
														(tag_final[i] == tag_final[i + 1])]
	merge_ind += [len(tag_final) - 1]
	merge_unique = [merge_ind[i] for i in np.where(np.diff(merge_ind) != 1)[0]]
	if len(merge_unique) > 0:
		tag_merged = []
		script_merged = []
		last_ind = 0
		for merge_ind in range(len(merge_unique)):
			# PREPEND PREVIOUS
			tag_ind = merge_unique[merge_ind]
			tag_merged += tag_final[last_ind: tag_ind]
			script_merged += script_final[last_ind: tag_ind]
			# MERGE CURRENT
			check_tag = tag_final[tag_ind]
			tag_end = [i for i,x in enumerate(tag_final[(tag_ind + 1): ]) if x != check_tag][0]
			tag_merged += [check_tag]
			script_merged += [' '.join(script_final[tag_ind: (tag_ind + tag_end + 1)])]
			last_ind = (tag_ind + tag_end + 1)
			if tag_ind == merge_unique[-1]:
				tag_merged += tag_final[last_ind: ]
				script_merged += script_final[last_ind: ]
	else:
		tag_merged = tag_final
		script_merged = script_final
    
	return tag_merged, script_merged


# REARRANGE DIALOGUE METADATA TO ALWAYS APPEAR AFTER DIALOGUE
def rearrange_tag_lines(tag_merged, script_merged):	
	dial_met_ind = [i for i in range(1, (len(tag_merged) - 1)) if tag_merged[i] == 'E' and \
												  tag_merged[i - 1] in ['C', 'D'] and \
												  tag_merged[i + 1] == 'D']
	if len(dial_met_ind) > 0:
		for tag_ind in dial_met_ind:
			temp_ind = min([i for i, x in enumerate(tag_merged[(tag_ind + 1): ]) if x != 'D'])
			# REARRANGE TAGS
			tag_merged[tag_ind: (tag_ind + temp_ind)] = tag_merged[(tag_ind + 1): (tag_ind + temp_ind + 1)]
			tag_merged[tag_ind + temp_ind] = 'E'
			# REARRANGE LINES
			temp_line = script_merged[tag_ind]
			script_merged[tag_ind: (tag_ind + temp_ind)] = script_merged[(tag_ind + 1): (tag_ind + temp_ind + 1)]
			script_merged[tag_ind + temp_ind] = temp_line
    
	return tag_merged, script_merged


# CHECK FOR UN-MERGED CLASSES
def find_same(tag_valid):
	same_ind = [i for i in range(len(tag_valid) - 1) if (tag_valid[i] != 'M' and \
														(tag_valid[i] == tag_valid[i + 1]))]
	return len(same_ind)


# CHECK FOR DIALOGUE METADATA PRECEDING DIALOGUE
def find_arrange(tag_valid):
	arrange_ind = [i for i in range(len(tag_valid) - 1) if tag_valid[i] == 'E' and \
															tag_valid[i + 1] == 'D']
	return len(arrange_ind)


# PARSER FUNCTION
def parse(file_orig, save_dir, abr_flag, tag_flag, save_name=None, abridged_name=None, tag_name=None):
	#------------------------------------------------------------------------------------
	# DEFINE
	tag_set = ['S', 'N', 'C', 'D', 'E', 'T', 'M']
	meta_set = ['BLACK', 'darkness']
	bound_set = ['int. ', 'ext. ', 'int ', 'ext ']
	trans_set = ['CUT ', 'FADE ', 'cut ']
	char_max_words = 7
	meta_thresh = 2
	sent_thresh = 5
	trans_thresh = 5
	# READ PDF/TEXT FILE
	script_orig = read_file(file_orig)
	# REMOVE INDENTS
	script_noind = []
	for script_line in script_orig:
		if len(script_line.split()) > 0:
			script_noind.append(' '.join(script_line.split()))
		else:
			script_noind.append('')
    
	num_lines = len(script_noind)
	tag_vec = np.array(['0' for x in range(num_lines)])
	#------------------------------------------------------------------------------------
	# DETECT SCENE BOUNDARIES
	tag_vec, bound_ind = get_scene_bound(script_noind, tag_vec, tag_set, bound_set)
	# DETECT TRANSITIONS
	tag_vec, trans_ind = get_trans(script_noind, tag_vec, tag_set, trans_thresh, trans_set)
	# DETECT METADATA
	tag_vec = get_meta(script_noind, tag_vec, tag_set, meta_thresh, meta_set, sent_thresh, bound_ind, trans_ind)
	# DETECT CHARACTER-DIALOGUE
	tag_vec = get_char_dial(script_noind, tag_vec, tag_set, char_max_words)
	# DETECT SCENE DESCRIPTION
	tag_vec = get_scene_desc(script_noind, tag_vec, tag_set)
	#------------------------------------------------------------------------------------
	# SAVE TAGS TO FILE
	if tag_flag == 'on':
		if tag_name is None:
			tag_name = os.path.join(save_dir, '.'.join(file_orig.split('/')[-1].split('.')[: -1]) + '_tags.txt')
		else:
			tag_name = os.path.join(save_dir, tag_name)
        
		np.savetxt(tag_name, tag_vec, fmt='%s', delimiter='\n')
    
	# REMOVE UN-TAGGED LINES
	tag_valid = []
	script_valid = []
	for i, x in enumerate(tag_vec):
		if x != '0':
			tag_valid.append(x)
			script_valid.append(script_noind[i])
    
	# FORMAT TAGS, LINES
	tag_valid, script_valid = combine_tag_lines(tag_valid, script_valid)
	while find_same(tag_valid) > 0 or find_arrange(tag_valid) > 0:
		tag_valid, script_valid = merge_tag_lines(tag_valid, script_valid)
		tag_valid, script_valid = rearrange_tag_lines(tag_valid, script_valid)
    
	#------------------------------------------------------------------------------------
	# WRITE PARSED SCRIPT TO FILE
	if save_name is None:
		save_name = os.path.join(save_dir, '.'.join(file_orig.split('/')[-1].split('.')[: -1]) + '_parsed.txt')
	else:
		save_name = os.path.join(save_dir, save_name)
    
	fid = open(save_name, 'w')
	for tag_ind in range(len(tag_valid)):
		_ = fid.write(tag_valid[tag_ind] + ': ' + script_valid[tag_ind] + '\n')
    
	fid.close()
	#------------------------------------------------------------------------------------
	# CREATE CHARACTER=>DIALOGUE ABRIDGED VERSION
	if abr_flag == 'on':
		fid = open(save_name, 'r')
		parsed_script = fid.read().splitlines()
		fid.close()
		if abridged_name is None:
			abridged_name = os.path.join(save_dir, '.'.join(file_orig.split('/')[-1].split('.')[: -1]) + '_abridged.txt')
		else:
			abridged_name = os.path.join(save_dir, abridged_name)
        
		abridged_script = [x for x in parsed_script if x.startswith('C') or x.startswith('D')]
		fid = open(abridged_name, 'w')
		for i in range(0, len(abridged_script), 2):
			try:
				char_str = ' '.join(abridged_script[i].split('C:')[1].split())
				dial_str = ' '.join(abridged_script[i + 1].split('D:')[1].split())
				_ = fid.write(''.join([char_str, '=>', dial_str, '\n']))
			except:
				pass
        
		fid.close()


# MAIN FUNCTION
if __name__ == "__main__":
    DIR_FINAL = join("scripts", "final")
    DIR_OUT = join("scripts", "parsed")

    files = [join(DIR_FINAL, f) for f in listdir(DIR_FINAL)
             if isfile(join(DIR_FINAL, f)) and getsize(join(DIR_FINAL, f)) > 3000]
    for f in tqdm(files):

        file_orig, save_dir, abr_flag, tag_flag, save_name, abridged_name = f, DIR_OUT, 'off', 'off', f.split(
            sep)[-1], f.split(sep)[-1].split('.txt')[0] + '_abridged.txt'
        parse(file_orig, save_dir, abr_flag,
              tag_flag, save_name, abridged_name)
