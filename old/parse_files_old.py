import subprocess
import glob
import os
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
import numpy as np
import argparse
import re
import time
from tqdm import tqdm

# PROCESS ARGUMENTS


def read_args():
    parser = argparse.ArgumentParser(
        description='Script that parses a movie script pdf/txt into its constituent classes')
    parser.add_argument(
        "-i", "--input", help="Path to script PDF/TXT to be parsed", required=True)
    parser.add_argument(
        "-o", "--output", help="Path to directory for saving output", required=True)
    parser.add_argument("-a", "--abridged",
                        help="Print abridged version (on/off)", default='off')
    parser.add_argument(
        "-t", "--tags", help="Print class label tags (on/off)", default='off')
    parser.add_argument(
        "-c", "--char", help="Print char info file (on/off)", default='off')
    args = parser.parse_args()
    if args.abridged not in ['on', 'off']:
        raise AssertionError("Invalid value. Choose either off or on")
    if args.tags not in ['on', 'off']:
        raise AssertionError("Invalid value. Choose either off or on")
    if args.char not in ['on', 'off']:
        raise AssertionError("Invalid value. Choose either off or on")
    return os.path.abspath(args.input), os.path.abspath(args.output), args.abridged, args.tags, args.char


# READ FILE
def read_file(file_orig):
    if file_orig.endswith(".pdf"):
        file_name = file_orig.replace('.pdf', '.txt')
        subprocess.call('pdftotext -layout ' + file_orig +
                        ' ' + file_name, shell=True)
    elif file_orig.endswith(".txt"):
        file_name = file_orig
    else:
        raise AssertionError("File should be either pdf or txt")

    fid = open(file_name, 'r')
    script_orig = fid.read().splitlines()
    fid.close()
    if file_orig.endswith(".pdf"):
        subprocess.call('rm ' + file_name, shell=True)

    return script_orig


# DETECT SCENE BOUNDARIES:
# LOOK FOR ALL-CAPS LINES CONTAINING "INT." OR "EXT."
def get_scene_bound(script_noind, tag_vec, tag_set, bound_set):
    bound_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and
                 x.isupper() and
                 any([y in x.lower() for y in bound_set])]
    if len(bound_ind) > 0:
        for x in bound_ind:
            tag_vec[x] = 'S'

    return tag_vec, bound_ind


# DETECT TRANSITIONS:
# LOOK FOR ALL-CAPS LINES PRECEDED BY NEWLINE, FOLLOWED BY NEWLINE AND CONTAINING "CUT " OR "FADE "
def get_trans(script_noind, tag_vec, tag_set, trans_thresh, trans_set):
    re_func = re.compile('[^a-zA-Z ]')
    trans_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()
                 and len(re_func.sub('', x).split()) < trans_thresh
                 and any([y in x for y in trans_set])]
    if len(trans_ind) > 0:
        for x in trans_ind:
            tag_vec[x] = 'T'

    return tag_vec, trans_ind


# DETECT METADATA:
# LOOK FOR CONTENT PRECEDING SPECIFIC PHRASES THAT INDICATE BEGINNING OF MOVIE
def get_meta(script_noind, tag_vec, tag_set, meta_thresh, meta_set, sent_thresh, bound_ind, trans_ind):
    re_func = re.compile('[^a-zA-Z ]')
    met_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set
               and i != 0 and i != (len(script_noind) - 1)
               and len(x.split()) < meta_thresh
               and len(re_func.sub('', script_noind[i - 1]).split()) == 0
               and len(re_func.sub('', script_noind[i + 1]).split()) == 0
               and any([y in x for y in meta_set])]
    sent_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set
                and i != 0 and i != (len(script_noind) - 1)
                and len(x.split()) > sent_thresh
                and len(script_noind[i - 1].split()) == 0
                and len(script_noind[i + 1].split()) > 0]
    meta_ind = sorted(met_ind + bound_ind + trans_ind + sent_ind)
    if len(meta_ind) > 0:
        for i, x in enumerate(script_noind[: meta_ind[0]]):
            if len(x.split()) > 0:
                tag_vec[i] = 'M'

    return tag_vec


# DECOMPOSE LINE WITH DIALOGUE AND DIALOGUE METADATA INTO INDIVIDUAL CLASSES
def separate_dial_meta(line_str):
    if '(' in line_str and ')' in line_str:
        bef_par_str = ' '.join(line_str.split('(')[0].split())
        in_par_str = ' '.join(line_str.split('(')[1].split(')')[0].split())
        rem_str = ')'.join(line_str.split(')')[1:])
    else:
        bef_par_str = line_str
        in_par_str = ''
        rem_str = ''

    return bef_par_str, in_par_str, rem_str


# DETECT CHARACTER-DIALOGUE BLOCKS:
# CHARACTER IS ALL-CAPS LINE PRECEDED BY NEWLINE AND NOT FOLLOWED BY A NEWLINE
# DIALOGUE IS WHATEVER IMMEDIATELY FOLLOWS CHARACTER
# EITHER CHARACTER OR DIALOGUE MIGHT CONTAIN DILAOGUE METADATA; WILL BE DETECTED LATER
def get_char_dial(script_noind, tag_vec, tag_set, char_max_words):
    char_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()
                and i != 0 and i != (len(script_noind) - 1)\
                # and len(script_noind[i - 1].split()) == 0\
                and len(script_noind[i + 1].split()) > 0\
                and len(x.split()) < char_max_words\
                and any([separate_dial_meta(x)[y] for y in [0, 2]])]
    for x in char_ind:
        tag_vec[x] = 'C'
        dial_flag = 1
        while dial_flag > 0:
            line_ind = x + dial_flag
            if len(script_noind[line_ind].split()) > 0:
                dial_str, dial_meta_str, rem_str = separate_dial_meta(
                    script_noind[line_ind])
                if dial_str != '' or rem_str != '':
                    tag_vec[line_ind] = 'D'
                else:
                    tag_vec[line_ind] = 'E'

                dial_flag += 1
            else:
                dial_flag = 0

    return tag_vec


# DETECT SCENE DESCRIPTION
# LOOK FOR REMAINING LINES THAT ARE NOT PAGE BREAKS
def get_scene_desc(script_noind, tag_vec, tag_set):
    desc_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and
                len(x.split()) > 0 and
                not x.strip('.').isdigit()]
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
                    _, in_par, _ = separate_dial_meta(combined_str)
                    if in_par != '':
                        # IF DIALOGUE METADATA PRESENT, EXTRACT IT
                        dial_meta_str = ''
                        char_dial_str = ''
                        while '(' in combined_str and ')' in combined_str:
                            before_par, in_par, combined_str = separate_dial_meta(
                                combined_str)
                            char_dial_str += ' ' + before_par
                            dial_meta_str += ' ' + in_par

                        char_dial_str += ' ' + combined_str
                        char_dial_str = ' '.join(char_dial_str.split())
                        dial_meta_str = ' '.join(dial_meta_str.split())
                        if x == 'C':
                            # IF CHARACTER, APPEND DIALOGUE METADATA
                            tag_final.append(x)
                            script_final.append(
                                ' '.join(char_dial_str.split()))
                            tag_final.append('E')
                            script_final.append(dial_meta_str)
                        elif x == 'D':
                            # IF DIALOGUE, PREPEND DIALOGUE METADATA
                            tag_final.append('E')
                            script_final.append(dial_meta_str)
                            tag_final.append(x)
                            script_final.append(
                                ' '.join(char_dial_str.split()))
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
    merge_ind = [i for i in range(len(tag_final) - 1) if tag_final[i + 1] != 'M' and
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
            tag_end = [i for i, x in enumerate(
                tag_final[(tag_ind + 1):]) if x != check_tag][0]
            tag_merged += [check_tag]
            script_merged += [' '.join(script_final[tag_ind: (tag_ind + tag_end + 1)])]
            last_ind = (tag_ind + tag_end + 1)
            if tag_ind == merge_unique[-1]:
                tag_merged += tag_final[last_ind:]
                script_merged += script_final[last_ind:]
    else:
        tag_merged = tag_final
        script_merged = script_final

    return tag_merged, script_merged


# REARRANGE DIALOGUE METADATA TO ALWAYS APPEAR AFTER DIALOGUE
def rearrange_tag_lines(tag_merged, script_merged):
    dial_met_ind = [i for i in range(1, (len(tag_merged) - 1)) if tag_merged[i] == 'E' and
                    tag_merged[i - 1] in ['C', 'D'] and
                    tag_merged[i + 1] == 'D']
    if len(dial_met_ind) > 0:
        for tag_ind in dial_met_ind:
            temp_ind = min([i for i, x in enumerate(
                tag_merged[(tag_ind + 1):]) if x != 'D'])
            # REARRANGE TAGS
            tag_merged[tag_ind: (
                tag_ind + temp_ind)] = tag_merged[(tag_ind + 1): (tag_ind + temp_ind + 1)]
            tag_merged[tag_ind + temp_ind] = 'E'
            # REARRANGE LINES
            temp_line = script_merged[tag_ind]
            script_merged[tag_ind: (
                tag_ind + temp_ind)] = script_merged[(tag_ind + 1): (tag_ind + temp_ind + 1)]
            script_merged[tag_ind + temp_ind] = temp_line

    return tag_merged, script_merged


# CHECK FOR UN-MERGED CLASSES
def find_same(tag_valid):
    same_ind = [i for i in range(len(tag_valid) - 1) if (tag_valid[i] != 'M' and
                                                         (tag_valid[i] == tag_valid[i + 1]))]
    return len(same_ind)


# CHECK FOR DIALOGUE METADATA PRECEDING DIALOGUE
def find_arrange(tag_valid):
    arrange_ind = [i for i in range(len(tag_valid) - 1) if tag_valid[i] == 'E' and
                   tag_valid[i + 1] == 'D']
    return len(arrange_ind)


# PARSER FUNCTION
def parse(file_orig, save_dir, abr_flag, tag_flag, char_flag, save_name=None, abridged_name=None, tag_name=None, charinfo_name=None):
    #------------------------------------------------------------------------------------
    # DEFINE
    tag_set = ['S', 'N', 'C', 'D', 'E', 'T', 'M']
    meta_set = ['BLACK', 'darkness']
    bound_set = ['int. ', 'ext. ', 'int ', 'ext ', 'EXTERIOR ', 'INTERIOR ']
    trans_set = ['CUT ', 'FADE ', 'cut ']
    char_max_words = 7
    meta_thresh = 2
    sent_thresh = 5
    trans_thresh = 5
    # READ PDF/TEXT FILE
    script_orig = read_file(file_orig)
    # REMOVE INDENTS
    alnum_filter = re.compile('[\W_]+', re.UNICODE)
    script_noind = []
    for script_line in script_orig:
        if len(script_line.split()) > 0 and alnum_filter.sub('', script_line) != '':
            script_noind.append(' '.join(script_line.split()))
        else:
            script_noind.append('')

    num_lines = len(script_noind)
    tag_vec = np.array(['0' for x in range(num_lines)])
    #------------------------------------------------------------------------------------
    # DETECT SCENE BOUNDARIES
    tag_vec, bound_ind = get_scene_bound(
        script_noind, tag_vec, tag_set, bound_set)
    # DETECT TRANSITIONS
    tag_vec, trans_ind = get_trans(
        script_noind, tag_vec, tag_set, trans_thresh, trans_set)
    # DETECT METADATA
    tag_vec = get_meta(script_noind, tag_vec, tag_set, meta_thresh,
                       meta_set, sent_thresh, bound_ind, trans_ind)
    # DETECT CHARACTER-DIALOGUE
    tag_vec = get_char_dial(script_noind, tag_vec, tag_set, char_max_words)
    # DETECT SCENE DESCRIPTION
    tag_vec = get_scene_desc(script_noind, tag_vec, tag_set)
    #------------------------------------------------------------------------------------
    # SAVE TAGS TO FILE
    if tag_flag == 'on':
        if tag_name is None:
            tag_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_tags.txt')
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
    max_rev = 0
    while find_same(tag_valid) > 0 or find_arrange(tag_valid) > 0:
        tag_valid, script_valid = merge_tag_lines(tag_valid, script_valid)
        tag_valid, script_valid = rearrange_tag_lines(tag_valid, script_valid)
        max_rev += 1
        if max_rev == 1000:
            raise AssertionError(
                "Too many revisions. Something must be wrong.")

    #------------------------------------------------------------------------------------
    # WRITE PARSED SCRIPT TO FILE
    if save_name is None:
        save_name = os.path.join(save_dir, '.'.join(
            file_orig.split('/')[-1].split('.')[: -1]) + '_parsed.txt')
    else:
        save_name = os.path.join(save_dir, "full", save_name)

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
            abridged_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_abridged.txt')
        else:
            abridged_name = os.path.join(save_dir, "abridged", abridged_name)

        abridged_ind = [i for i, x in enumerate(parsed_script) if x.startswith('C:') and
                        parsed_script[i + 1].startswith('D:')]
        fid = open(abridged_name, 'w')
        for i in abridged_ind:
            char_str = ' '.join(parsed_script[i].split('C:')[1].split())
            dial_str = ' '.join(parsed_script[i + 1].split('D:')[1].split())
            _ = fid.write(''.join([char_str, '=>', dial_str, '\n']))

        fid.close()

    #------------------------------------------------------------------------------------
    # CREATE CHAR INFO FILE
    if char_flag == 'on':
        tag_str_vec = np.array(tag_valid)
        script_vec = np.array(script_valid)
        char_ind = np.where(tag_str_vec == 'C')[0]
        char_set = sorted(set(script_vec[char_ind]))
        charinfo_vec = []
        for char_id in char_set:
            spk_ind = list(
                set(np.where(script_vec == char_id)[0]) & set(char_ind))
            if len(spk_ind) > 0:
                num_lines = len([i for i in spk_ind if i != (len(tag_str_vec) - 1) and
                                 tag_str_vec[i + 1] == 'D'])
                charinfo_str = char_id + ': ' + \
                    str(num_lines) + '|'.join([' ', ' ', ' ', ' '])
                charinfo_vec.append(charinfo_str)
        if charinfo_name is None:
            charinfo_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_charinfo.txt')
        else:
            charinfo_name = os.path.join(save_dir, "charinfo", charinfo_name)
        np.savetxt(charinfo_name, charinfo_vec, fmt='%s', delimiter='\n', encoding="utf-8")

# MAIN FUNCTION
if __name__ == "__main__":
    DIR_FINAL = join("scripts", "filtered")
    DIR_OUT = join("scripts", "parsed")
    DIR_OUT_FULL = join(DIR_OUT, "full")
    DIR_OUT_ABRIDGED = join(DIR_OUT, "abridged")
    DIR_OUT_CHARINFO = join(DIR_OUT, "charinfo")

    if not os.path.exists(DIR_OUT):
        os.makedirs(DIR_OUT)
    if not os.path.exists(DIR_OUT_FULL):
        os.makedirs(DIR_OUT_FULL)
    if not os.path.exists(DIR_OUT_ABRIDGED):
        os.makedirs(DIR_OUT_ABRIDGED)
    if not os.path.exists(DIR_OUT_CHARINFO):
        os.makedirs(DIR_OUT_CHARINFO)

    files = [join(DIR_FINAL, f) for f in listdir(DIR_FINAL)
             if isfile(join(DIR_FINAL, f)) and getsize(join(DIR_FINAL, f)) > 3000]
    for f in tqdm(files):

        file_orig, save_dir, abr_flag, tag_flag, char_flag, save_name, abridged_name, charinfo_name = f, DIR_OUT, 'on', 'off', 'on', f.split(
            sep)[-1], f.split(sep)[-1].split('.txt')[0] + '_abridged.txt', f.split(sep)[-1].split('.txt')[0] + '_charinfo.txt'
        try:
            parse(file_orig, save_dir, abr_flag,
                  tag_flag, char_flag, save_name, abridged_name, None, charinfo_name)
        except Exception as err:
            print(err)
            pass
