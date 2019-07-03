# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 14:30:05 2019

@author: Wei-Hsiang, Shen
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys
import argparse
import json
from tqdm import tqdm
import pandas as pd

from file_IO import Read_json


def Get_Object_Memory_Size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([Get_Object_Memory_Size(v, seen) for v in obj.values()])
        size += sum([Get_Object_Memory_Size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += Get_Object_Memory_Size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([Get_Object_Memory_Size(i, seen) for i in obj])
    return size

def Get_Year_Difference(target_year, referenced_by_year):
    base_year = int(target_year)
    offset_year = int(referenced_by_year.split(', ')[-1])
    return offset_year - base_year

def Read_All_Patent_Data(in_dir='./output/'):
    all_patent_info = []
    print("Reading all patent data (.json) from disk to memory...")
    for filename in tqdm(os.listdir(in_dir)):
        if filename.lower().endswith('.json') == False :
            continue
        file_path = os.path.join(in_dir, filename)

        all_patent_info.append(Read_json(file_path))
    print("Patent count : {}".format(len(all_patent_info)))
    print("Memory usage : {} MB".format(Get_Object_Memory_Size(all_patent_info)/1000/1000))

    return all_patent_info

def Calculate_Index(all_patent_info, target_year="2011", target_region="Penang"):
    assert type(target_year) == str
    assert type(target_region) == str
    USPC_COUNT = 472 # total number of all USPC available in the patent database

    # Localization
    total_region_reference_count = 0
    total_region_reference_itself_count = 0

    # HHI
    total_patent_count_in_target_year = 0
    assignee_histogram = {'__init__': 0}

    # Orginality
    total_originality = 0

    # Diversification
    used_uspc_list = []

    # Cycle time
    total_avg_cycle_time = 0

    # Collabortaion
    total_intra_regional = 0
    total_inter_regional = 0
    total_international = 0

    # Loop through all patents
    print("Calculate index for year: {}, region: {}".format(target_year, target_region))
#    for patent in tqdm(all_patent_info):
    for patent in all_patent_info:
        if target_year not in patent['date']: # ignore patents that are not in the given year
            continue

        total_patent_count_in_target_year += 1
        total_region_reference_count += len(patent['reference'])

        # Count reference that is in the same region
        for reference in patent['reference']:
            if reference['inventors'][0]['city'] == target_region: # only check first inventor
                total_region_reference_itself_count += 1

        # Add all assignee into the histogram
        for assignee in patent['assignee']:
            if assignee['name'] in assignee_histogram:
                assignee_histogram[assignee['name']] = assignee_histogram[assignee['name']] + 1
            else:
                assignee_histogram[assignee['name']] = 1

        # Originality
        if len(patent['reference'])!=0:
            this_patent_uspc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for uspc in reference['US']:
                    if uspc in this_patent_uspc_histogram:
                       this_patent_uspc_histogram[uspc] = this_patent_uspc_histogram[uspc] + 1
                    else:
                        this_patent_uspc_histogram[uspc] = 1
            this_patent_uspc_histogram_value = np.array(list(this_patent_uspc_histogram.values()))
            this_patent_uspc_histogram_value = this_patent_uspc_histogram_value / (len(this_patent_uspc_histogram)-1)
            total_originality += np.sum(this_patent_uspc_histogram_value**2) / len(patent['reference'])

        # Add all used USPC number into the list
        for uspc in patent['US']:
            if uspc not in used_uspc_list:
                used_uspc_list.append(uspc)

        # Add averaged cycle time from all future referenced by patents
        if len(patent['referenced_by']) != 0:
            this_patent_total_cycle_time = 0
            for referenced_by_patent in patent['referenced_by']:
                this_patent_total_cycle_time += Get_Year_Difference(target_year, referenced_by_patent['date'])
            total_avg_cycle_time += this_patent_total_cycle_time/len(patent['referenced_by'])

        # Check collaboration
        if len(patent['inventors']) >= 2:
            if patent['inventors'][0]['city'] == patent['inventors'][1]['city']: # check first two inventors
                total_intra_regional += 1
            elif patent['inventors'][0]['country'] == patent['inventors'][1]['country']:
                total_inter_regional += 1
            else:
                total_international += 1
        else:
            total_intra_regional += 1


    # Calculate all the index
    try:
        index_localization = total_region_reference_itself_count / total_region_reference_count
    except ZeroDivisionError:
        index_localization = 0

    index_diversification = len(used_uspc_list) / USPC_COUNT

    if total_patent_count_in_target_year != 0: # avoid zero division
        index_orginality = total_originality / total_patent_count_in_target_year
        index_cycle_time = total_avg_cycle_time / total_patent_count_in_target_year
        index_collab_intra_regional = total_intra_regional / total_patent_count_in_target_year
        index_collab_inter_regional = total_inter_regional / total_patent_count_in_target_year
        index_collab_international = total_international / total_patent_count_in_target_year
    else:
        index_orginality = 0
        index_cycle_time = 0
        index_collab_intra_regional = 0
        index_collab_inter_regional = 0
        index_collab_international = 0

    # HHI
    all_assignee_patent_count = list(assignee_histogram.values())
    all_assignee_patent_count.sort(reverse=True)
    all_assignee_patent_count = np.array(all_assignee_patent_count[0:5]) / total_patent_count_in_target_year
    index_HHI = np.sum(all_assignee_patent_count**2)
#    with open('assignee_histogram.json', 'w') as fp:
#        json.dump(assignee_histogram, fp)

    return index_localization, index_HHI, index_orginality, index_diversification, \
            index_cycle_time, index_collab_intra_regional, index_collab_inter_regional, \
            index_collab_international, assignee_histogram, total_patent_count_in_target_year

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=False, type=str, default='./output/',
                    help="directory to input .json files")
    ap.add_argument("-o", "--output", required=False, type=str, default='./index_result/',
                    help="directory to save calculated indexes")
    ap.add_argument("-y", "--year", nargs='+', type=int, default=[1970, 2015],
                    help='the starting year and ending year of index calculation')
    ARGS = ap.parse_args()

    if os.path.isdir(ARGS.output) == False:
        print("Folder {} does not exist, create one".format(ARGS.output))
        os.mkdir(ARGS.output)
    output_csv_path = os.path.join(ARGS.output, 'index_result.csv')
    output_pkl_path = os.path.join(ARGS.output, 'index_result.pkl')

    all_patent_info = Read_All_Patent_Data(in_dir=ARGS.input)

    year = []
    patent_count = []
    localization = []
    HHI = []
    orginality = []
    diversification = []
    cycle_time = []
    intra_collab = []
    inter_collab = []
    international_collab = []

    print("Would start calculate indexes from {} to {}".format(ARGS.year[0], ARGS.year[1]))
    input("Press Enter to continue...")
    for i_year in range(ARGS.year[0], ARGS.year[1]+1):
        index_localization, index_HHI, index_orginality, index_diversification, \
        index_cycle_time, index_collab_intra_regional, index_collab_inter_regional, \
        index_collab_international, assignee_histogram, total_patent_count_in_target_year\
        = Calculate_Index(all_patent_info, str(i_year), "Penang")

        # append index to list
        year.append(i_year)
        patent_count.append(total_patent_count_in_target_year)
        localization.append(index_localization)
        HHI.append(index_HHI)
        orginality.append(index_orginality)
        diversification.append(index_diversification)
        cycle_time.append(index_cycle_time)
        intra_collab.append(index_collab_intra_regional)
        inter_collab.append(index_collab_inter_regional)
        international_collab.append(index_collab_international)

    # Make dictionary
    index_dict = {
            'year': year,
            'patent_count': patent_count,
            'localization': localization,
            'HHI': HHI,
            'orginality': orginality,
            'diversification': diversification,
            'cycle_time': cycle_time,
            'intra_regional_collaboration': intra_collab,
            'inter_regional_collaboration': inter_collab,
            'international_collaboration': international_collab
            }

    index_df = pd.DataFrame(index_dict)
    print("Store calculated index result to {}".format(output_csv_path))
    index_df.to_csv(output_csv_path)
    index_df.to_pickle(output_pkl_path)