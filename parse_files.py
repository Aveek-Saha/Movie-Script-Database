
import subprocess
import glob
import os
import numpy as np
import argparse
import re
import time
import codecs
import json

from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists

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
    parser.add_argument("-f", "--offsets",
                        help="Print offset indices (on/off)", default='off')
    args = parser.parse_args()
    if args.abridged not in ['on', 'off']:
        raise AssertionError(
            "Invalid value. Choose either off or on")
    if args.tags not in ['on', 'off']:
        raise AssertionError(
            "Invalid value. Choose either off or on")
    if args.char not in ['on', 'off']:
        raise AssertionError(
            "Invalid value. Choose either off or on")
    if args.offsets not in ['on', 'off']:
        raise AssertionError(
            "Invalid value. Choose either off or on")
    return os.path.abspath(args.input), os.path.abspath(args.output), args.abridged, args.tags, args.char, args.offsets


# FIND OFFSET INDICES FOR EACH LINE
def get_offset(script_lines, script_str):
    offset_mat = np.empty((0, 2), dtype=int)
    pos_init = 0
    for line_val in script_lines:
        if line_val != '':
            line_start = script_str.find(line_val, pos_init)
            sub_script = script_str[line_start: (line_start + len(line_val))]
            valid_indices = [(line_start + i)
                             for i, x in enumerate(sub_script) if x != ' ']
            offset_mat = np.append(offset_mat, np.array(
                [[min(valid_indices), (max(valid_indices) + 1)]]), axis=0)
            pos_init = line_start + len(line_val) + 1
        else:
            offset_mat = np.append(offset_mat, np.array(
                [[pos_init, (pos_init + 1)]]), axis=0)
            pos_init += 1

    return offset_mat + 1


# READ FILE
def read_txt(file_path):
    fid = codecs.open(file_path, mode='r', encoding='utf-8')
    txt_file = fid.read()
    fid.close()
    txt_lines = txt_file.splitlines()
    txt_offsets = get_offset(txt_lines, txt_file)
    return txt_lines, txt_offsets


# PROCESS FILE
def read_file(file_orig):
    if file_orig.endswith(".pdf"):
        file_name = file_orig.replace('.pdf', '.txt')
        subprocess.call(['pdftotext', '-enc', 'UTF-8',
                         '-layout', file_orig, file_name])
        script_orig, script_offsets = read_txt(file_name)
        subprocess.call('rm ' + file_name, shell=True)
    elif file_orig.endswith(".txt"):
        script_orig, script_offsets = read_txt(file_orig)
    else:
        raise AssertionError(
            "Movie script file format should be either pdf or txt")

    return script_orig, script_offsets


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
    trans_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set
                 and len(re_func.sub('', x).split()) < trans_thresh
                 and any([y in x.lower() for y in trans_set])]
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
    char_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and all([y.isupper() for y in x.split()])
                and i != 0 and i != (len(script_noind) - 1)\
                # and len(script_noind[i - 1].split()) == 0\
                and len(script_noind[i + 1].split()) > 0\
                and len(x.split()) < char_max_words\
                and any([separate_dial_meta(x)[y] for y in [0, 2]])]
    if char_ind[-1] < (len(script_noind) - 1):
        char_ind += [len(script_noind) - 1]
    else:
        char_ind += [len(script_noind)]

    for x in range(len(char_ind) - 1):
        tag_vec[char_ind[x]] = 'C'
        dial_flag = 1
        while dial_flag > 0:
            line_ind = char_ind[x] + dial_flag
            if len(script_noind[line_ind].split()) > 0 and line_ind < char_ind[x + 1]:
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


# CHECK IF LINES CONTAIN START OF PARENTHESES
def par_start(line_set):
    return [i for i, x in enumerate(line_set) if '(' in x]


# CHECK IF LINES CONTAIN START OF PARENTHESES
def par_end(line_set):
    return [i for i, x in enumerate(line_set) if ')' in x]


# COMBINE MULTI-LINE CLASSES, SPLIT MULTI-CLASS LINES
def combine_tag_lines(tag_valid, script_valid):
    tag_final = []
    script_final = []
    changed_tags = [x for x in tag_valid]
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
                comb_ind = []

            to_combine += script_valid[i].split()
            comb_ind.append(i)
            if i == (len(tag_valid) - 1) or x != tag_valid[i + 1]:
                combined_str = ' '.join(to_combine)
                if x == 'N':
                    # IF SCENE DESCRIPTION, WRITE AS IT IS
                    tag_final.append(x)
                    script_final.append(combined_str)
                else:
                    _, in_par, _ = separate_dial_meta(combined_str)
                    if in_par != '':
                        # FIND LINES CONTAINING DIALOGUE METADATA
                        comb_lines = [script_valid[j] for j in comb_ind]
                        dial_meta_ind = []
                        while len(par_start(comb_lines)) > 0 and len(par_end(comb_lines)) > 0:
                            start_ind = comb_ind[par_start(comb_lines)[0]]
                            end_ind = comb_ind[par_end(comb_lines)[0]]
                            dial_meta_ind.append([start_ind, end_ind])
                            comb_ind = [x for x in comb_ind if x > end_ind]
                            comb_lines = [script_valid[j] for j in comb_ind]

                        # REPLACE OLD TAGS WITH DIALOGUE METADATA TAGS
                        for dial_ind in dial_meta_ind:
                            for change_ind in range(dial_ind[0], (dial_ind[1] + 1)):
                                changed_tags[change_ind] = 'E'

                        # EXTRACT DIALOGUE METADATA
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

    return tag_final, script_final, changed_tags


# CHECK FOR UN-MERGED CLASSES
def find_same(tag_valid):
    same_ind_mat = np.empty((0, 2), dtype=int)
    if len(tag_valid) > 1:
        check_start = 0
        check_end = 1
        while check_start < (len(tag_valid) - 1):
            if tag_valid[check_start] != 'M' and tag_valid[check_start] == tag_valid[check_end]:
                while check_end < len(tag_valid) and tag_valid[check_start] == tag_valid[check_end]:
                    check_end += 1

                append_vec = np.array(
                    [[check_start, (check_end - 1)]], dtype=int)
                same_ind_mat = np.append(same_ind_mat, append_vec, axis=0)
                check_end += 1
                check_start = check_end - 1
            else:
                check_start += 1
                check_end += 1

    return same_ind_mat


# MERGE CONSECUTIVE IDENTICAL CLASSES
def merge_tag_lines(tag_final, script_final):
    merge_ind = find_same(tag_final)
    if merge_ind.shape[0] > 0:
        # PRE-MERGE DISSIMILAR
        tag_merged = tag_final[: merge_ind[0, 0]]
        script_merged = script_final[: merge_ind[0, 0]]
        for ind in range(merge_ind.shape[0] - 1):
            # CURRENT MERGE SIMILAR
            tag_merged += [tag_final[merge_ind[ind, 0]]]
            script_merged += [' '.join(script_final[merge_ind[ind, 0]: (merge_ind[ind, 1] + 1)])]
            # CURRENT MERGE DISSIMILAR
            tag_merged += tag_final[(merge_ind[ind, 1] + 1): merge_ind[(ind + 1), 0]]
            script_merged += script_final[(merge_ind[ind, 1] + 1): merge_ind[(ind + 1), 0]]

        # POST-MERGE SIMILAR
        tag_merged += [tag_final[merge_ind[-1, 0]]]
        script_merged += [' '.join(script_final[merge_ind[-1, 0]: (merge_ind[-1, 1] + 1)])]
        # POST-MERGE DISSIMILAR
        tag_merged += tag_final[(merge_ind[-1, 1] + 1):]
        script_merged += script_final[(merge_ind[-1, 1] + 1):]
    else:
        tag_merged = tag_final
        script_merged = script_final

    return tag_merged, script_merged


# CHECK FOR DIALOGUE METADATA PRECEDING DIALOGUE
def find_arrange(tag_valid):
    c_ind = [i for i, x in enumerate(tag_valid) if x == 'C']
    c_segs = []
    arrange_ind = []
    invalid_set = [['C', 'E', 'D'], ['C', 'D', 'E', 'D']]
    if len(c_ind) > 0:
        # BREAK UP INTO C-* BLOCKS
        if c_ind[0] != 0:
            c_segs.append(tag_valid[: c_ind[0]])

        for i in range((len(c_ind) - 1)):
            c_segs.append(tag_valid[c_ind[i]: c_ind[i + 1]])

        c_segs.append(tag_valid[c_ind[-1]:])
        # RE-ARRANGE IN BLOCKS IF REQUIRED
        for i in range(len(c_segs)):
            inv_flag = 0
            if len(c_segs[i]) > 2:
                if any([c_segs[i][j: (j + len(invalid_set[0]))] == invalid_set[0]
                        for j in range(len(c_segs[i]) - len(invalid_set[0]) + 1)]):
                    inv_flag = 1

            if inv_flag == 0 and len(c_segs[i]) > 3:
                if any([c_segs[i][j: (j + len(invalid_set[1]))] == invalid_set[1]
                        for j in range(len(c_segs[i]) - len(invalid_set[1]) + 1)]):
                    inv_flag = 1

            if inv_flag == 1:
                arrange_ind.append(i)

    return c_segs, arrange_ind


# REARRANGE DIALOGUE METADATA TO ALWAYS APPEAR AFTER DIALOGUE
def rearrange_tag_lines(tag_merged, script_merged):
    tag_rear = []
    script_rear = []
    char_blocks, dial_met_ind = find_arrange(tag_merged)
    if len(dial_met_ind) > 0:
        last_ind = 0
        for ind in range(len(char_blocks)):
            if ind in dial_met_ind:
                # ADD CHARACTER
                tag_rear += ['C']
                script_rear.append(script_merged[last_ind])
                # ADD DIALOGUE
                if 'D' in char_blocks[ind]:
                    tag_rear += ['D']
                    script_rear.append(' '.join([script_merged[last_ind + i]
                                                 for i, x in enumerate(char_blocks[ind]) if x == 'D']))

                # ADD DIALOGUE METADATA
                if 'E' in char_blocks[ind]:
                    tag_rear += ['E']
                    script_rear.append(' '.join([script_merged[last_ind + i]
                                                 for i, x in enumerate(char_blocks[ind]) if x == 'E']))
                # ADD REMAINING
                tag_rear += [x for x in char_blocks[ind]
                             if x not in ['C', 'D', 'E']]
                script_rear += [script_merged[last_ind + i]
                                for i, x in enumerate(char_blocks[ind]) if x not in ['C', 'D', 'E']]
            else:
                tag_rear += char_blocks[ind]
                script_rear += script_merged[last_ind: (
                    last_ind + len(char_blocks[ind]))]

            last_ind += len(char_blocks[ind])

    return tag_rear, script_rear


# PARSER FUNCTION
def parse(file_orig, save_dir, abr_flag, tag_flag, char_flag, off_flag, save_name=None, abridged_name=None, tag_name=None, charinfo_name=None, offset_name=None):
    # ------------------------------------------------------------------------------------
    # DEFINE
    tag_set = ['S', 'N', 'C', 'D', 'E', 'T', 'M']
    meta_set = ['BLACK', 'darkness']
    bound_set = ['int.', 'ext.', 'int ', 'ext ', 'exterior ', 'interior ']
    trans_set = ['cut', 'fade', 'transition', 'dissolve']
    char_max_words = 5
    meta_thresh = 2
    sent_thresh = 5
    trans_thresh = 6
    # READ PDF/TEXT FILE
    script_orig, script_offsets = read_file(file_orig)
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
    # ------------------------------------------------------------------------------------
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
    # ------------------------------------------------------------------------------------
    # REMOVE UN-TAGGED LINES
    nz_ind_vec = np.where(tag_vec != '0')[0]
    tag_valid = []
    script_valid = []
    for i, x in enumerate(tag_vec):
        if x != '0':
            tag_valid.append(x)
            script_valid.append(script_noind[i])

    # UPDATE TAGS
    tag_valid, script_valid, changed_tags = combine_tag_lines(
        tag_valid, script_valid)
    for change_ind in range(len(nz_ind_vec)):
        if tag_vec[nz_ind_vec[change_ind]] == 'D':
            tag_vec[nz_ind_vec[change_ind]] = changed_tags[change_ind]

    # SAVE TAGS TO FILE
    if tag_flag == 'on':
        if tag_name is None:
            tag_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_tags.txt')
        else:
            tag_name = os.path.join(save_dir, tag_name)

        np.savetxt(tag_name, tag_vec, fmt='%s', delimiter='\n')

    # SAVE OFFSETS TO FILE
    if off_flag == 'on':
        if offset_name is None:
            offset_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_offsets.txt')
        else:
            offset_name = os.path.join(save_dir, offset_name)

        np.savetxt(offset_name, script_offsets, fmt='%s', delimiter=',')

    # FORMAT TAGS, LINES
    max_rev = 0
    while find_same(tag_valid).shape[0] > 0 or len(find_arrange(tag_valid)[1]) > 0:
        tag_valid, script_valid = merge_tag_lines(tag_valid, script_valid)
        tag_valid, script_valid = rearrange_tag_lines(tag_valid, script_valid)
        max_rev += 1
        if max_rev == 1000:
            raise AssertionError(
                "Too many revisions. Something must be wrong.")

    # ------------------------------------------------------------------------------------
    # WRITE PARSED SCRIPT TO FILE
    if save_name is None:
        save_name = os.path.join(save_dir, '.'.join(
            file_orig.split('/')[-1].split('.')[: -1]) + '_parsed.txt')
    else:
        save_name = os.path.join(save_dir, "tagged", save_name)

    fid = open(save_name, 'w')
    for tag_ind in range(len(tag_valid)):
        _ = fid.write(tag_valid[tag_ind] + ': ' + script_valid[tag_ind] + '\n')

    fid.close()
    # ------------------------------------------------------------------------------------
    # CREATE CHARACTER=>DIALOGUE ABRIDGED VERSION
    if abr_flag == 'on':
        fid = open(save_name, 'r')
        parsed_script = fid.read().splitlines()
        fid.close()
        if abridged_name is None:
            abridged_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_abridged.txt')
        else:
            abridged_name = os.path.join(save_dir, "dialogue", abridged_name)

        abridged_ind = [i for i, x in enumerate(parsed_script) if x.startswith('C:') and
                        parsed_script[i + 1].startswith('D:')]
        fid = open(abridged_name, 'w')
        for i in abridged_ind:
            char_str = ' '.join(parsed_script[i].split('C:')[1].split())
            dial_str = ' '.join(parsed_script[i + 1].split('D:')[1].split())
            _ = fid.write(''.join([char_str, '=>', dial_str, '\n']))

        fid.close()

    # ------------------------------------------------------------------------------------
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
                    str(num_lines)
                charinfo_vec.append(charinfo_str)
        if charinfo_name is None:
            charinfo_name = os.path.join(save_dir, '.'.join(
                file_orig.split('/')[-1].split('.')[: -1]) + '_charinfo.txt')
        else:
            charinfo_name = os.path.join(save_dir, "charinfo", charinfo_name)
        np.savetxt(charinfo_name, charinfo_vec, fmt='%s',
                   delimiter='\n', encoding="utf-8")


# MAIN FUNCTION
if __name__ == "__main__":
    DIR_FINAL = join("scripts", "filtered")
    DIR_OUT = join("scripts", "parsed")
    DIR_OUT_FULL = join(DIR_OUT, "tagged")
    DIR_OUT_ABRIDGED = join(DIR_OUT, "dialogue")
    DIR_OUT_CHARINFO = join(DIR_OUT, "charinfo")
    META_DIR = join("scripts", "metadata")
    CLEAN_META = join(META_DIR, "clean_files_meta.json")
    PARSED_META = join(META_DIR, "clean_parsed_meta.json")

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

    f = open(CLEAN_META, 'r')
    meta = json.load(f)
    f.close()

    for script in tqdm(meta):
        file = meta[script]["file"]
        file_orig = join(DIR_FINAL, file["file_name"] + ".txt")
        save_dir = DIR_OUT
        abr_flag = "on"
        tag_flag = "off"
        char_flag = "on"
        off_flag = "off"
        save_name = file["file_name"] + "_parsed.txt"
        abridged_name = file["file_name"] + "_dialogue.txt"
        tag_name = None
        charinfo_name = file["file_name"] + "_charinfo.txt"

        try:
            parse(file_orig, save_dir, abr_flag, tag_flag, char_flag,
                  off_flag, save_name, abridged_name, tag_name, charinfo_name)
            meta[script]["parsed"] = {
                "dialogue": abridged_name,
                "charinfo": charinfo_name,
                "tagged": save_name
            }
        except Exception as err:
            print(err)
            pass
    with open(join(PARSED_META), "w") as outfile:
        json.dump(meta, outfile, indent=4)
