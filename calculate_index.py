# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 14:30:05 2019

@author: Wei-Hsiang, Shen
"""

import numpy as np
import os, sys
import argparse
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

    if offset_year == 2019: # ignore patent in 2019
        return 0

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

def Calculate_Index(all_patent_info, target_year="2011", target_region=['Penang', 'penang'], window_length=[3,5], city_of_collaboration=[]):
    assert type(target_year) == str
#    assert type(target_region) == str

    USPC_COUNT = 472 # total number of all USPC available in the patent database
    CPC_COUNT = 664 # total number of all CPC available in the patent database

    # Localization
    total_region_reference_count = 0
    total_region_reference_itself_count = 0

    # HHI
    total_patent_count_in_target_year = 0
    assignee_histogram = {'__init__': 0}

    # Orginality
    total_originality1_uspc = 0
    total_originality2_uspc = 0
    total_originality3_uspc = 0
    total_originality4_uspc = 0
    total_originality1_cpc = 0
    total_originality2_cpc = 0
    total_originality3_cpc = 0
    total_originality4_cpc = 0

    # Diversification
    used_uspc_list = []
    used_cpc_list = []

    # Cycle time
    total_avg_cycle_time = 0
    total_avg_cycle_time_list = np.zeros(len(window_length))
    total_avg_cycle_time_backward = 0
    total_avg_cycle_time_backward_list = np.zeros(len(window_length))

    # Collabortaion
    total_intra_regional = 0
    total_inter_regional = 0
    total_international = 0

    # Loop through all patents
#    print("Calculate index for year: {}, region: {}, window length: {}".format(target_year, target_region, window_length))
    print("Calculate index for year: {}".format(target_year))

#    for patent in tqdm(all_patent_info):
    for patent in all_patent_info:
        if target_year not in patent['date']: # ignore patents that are not in the given year
            continue

        total_patent_count_in_target_year += 1
        total_region_reference_count += len(patent['reference'])

        # Count reference that is in the same region
        for reference in patent['reference']:
            for i_region in target_region:
                if i_region in reference['inventors'][0]['city']:
                    total_region_reference_itself_count += 1
                    break

#            if target_region in reference['inventors'][0]['city']:
            #if reference['inventors'][0]['city'] == target_region: # only check first inventor
#                total_region_reference_itself_count += 1

        # Add all assignee into the histogram
        for assignee in patent['assignee']:
            if assignee['name'] in assignee_histogram:
                assignee_histogram[assignee['name']] = assignee_histogram[assignee['name']] + 1
            else:
                assignee_histogram[assignee['name']] = 1

        # originality1_uspc
        if len(patent['reference'])!=0:
            this_patent_uspc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for uspc in reference['US']:
                    if uspc in this_patent_uspc_histogram:
                       this_patent_uspc_histogram[uspc] = this_patent_uspc_histogram[uspc] + 1
                    else:
                        this_patent_uspc_histogram[uspc] = 1
            this_patent_uspc_histogram_value = np.array(list(this_patent_uspc_histogram.values()))
            this_patent_uspc_histogram_value = this_patent_uspc_histogram_value / (len(patent['reference']))
            total_originality1_uspc += 1 - np.sum(this_patent_uspc_histogram_value**2) / len(patent['reference'])

        # originality1_cpc
        if len(patent['reference'])!=0:
            this_patent_cpc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for cpc in reference['CPC']:
                    if cpc in this_patent_cpc_histogram:
                       this_patent_cpc_histogram[cpc] = this_patent_cpc_histogram[cpc] + 1
                    else:
                        this_patent_cpc_histogram[cpc] = 1
            this_patent_cpc_histogram_value = np.array(list(this_patent_cpc_histogram.values()))
            this_patent_cpc_histogram_value = this_patent_cpc_histogram_value / (len(patent['reference']))
            total_originality1_cpc += 1 - np.sum(this_patent_cpc_histogram_value**2) / len(patent['reference'])

        # originality2_uspc
        if len(patent['reference'])!=0:
            this_patent_uspc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for uspc in reference['US']:
                    if uspc in this_patent_uspc_histogram:
                       this_patent_uspc_histogram[uspc] = this_patent_uspc_histogram[uspc] + 1
                    else:
                        this_patent_uspc_histogram[uspc] = 1
            this_patent_uspc_histogram_value = np.array(list(this_patent_uspc_histogram.values()))
            this_patent_uspc_histogram_value = this_patent_uspc_histogram_value / (len(patent['reference']))
            total_originality2_uspc += 1 - np.sum(this_patent_uspc_histogram_value**2)

        # originality2_cpc
        if len(patent['reference'])!=0:
            this_patent_cpc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for cpc in reference['CPC']:
                    if cpc in this_patent_cpc_histogram:
                       this_patent_cpc_histogram[cpc] = this_patent_cpc_histogram[cpc] + 1
                    else:
                        this_patent_cpc_histogram[cpc] = 1
            this_patent_cpc_histogram_value = np.array(list(this_patent_cpc_histogram.values()))
            this_patent_cpc_histogram_value = this_patent_cpc_histogram_value / (len(patent['reference']))
            total_originality2_cpc += 1 - np.sum(this_patent_cpc_histogram_value**2)

        # originality3_uspc
        if len(patent['reference'])!=0:
            this_patent_uspc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for uspc in reference['US']:
                    if uspc in this_patent_uspc_histogram:
                       this_patent_uspc_histogram[uspc] = this_patent_uspc_histogram[uspc] + 1
                    else:
                        this_patent_uspc_histogram[uspc] = 1
            this_patent_uspc_histogram_value = np.array(list(this_patent_uspc_histogram.values()))
            this_patent_uspc_histogram_value = this_patent_uspc_histogram_value / np.sum(this_patent_uspc_histogram_value)
            total_originality3_uspc += 1 - np.sum(this_patent_uspc_histogram_value**2)

        # originality3_cpc
        if len(patent['reference'])!=0:
            this_patent_cpc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for cpc in reference['CPC']:
                    if cpc in this_patent_cpc_histogram:
                       this_patent_cpc_histogram[cpc] = this_patent_cpc_histogram[cpc] + 1
                    else:
                        this_patent_cpc_histogram[cpc] = 1
            this_patent_cpc_histogram_value = np.array(list(this_patent_cpc_histogram.values()))
            this_patent_cpc_histogram_value = this_patent_cpc_histogram_value / np.sum(this_patent_cpc_histogram_value)
            total_originality3_cpc += 1 - np.sum(this_patent_cpc_histogram_value**2)

        # originality4_uspc
        if len(patent['reference'])!=0:
            this_patent_uspc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for uspc in reference['US'][0]:
                    if uspc in this_patent_uspc_histogram:
                       this_patent_uspc_histogram[uspc] = this_patent_uspc_histogram[uspc] + 1
                    else:
                        this_patent_uspc_histogram[uspc] = 1
            this_patent_uspc_histogram_value = np.array(list(this_patent_uspc_histogram.values()))
            this_patent_uspc_histogram_value = this_patent_uspc_histogram_value / np.sum(this_patent_uspc_histogram_value)
            total_originality4_uspc += 1 - np.sum(this_patent_uspc_histogram_value**2)

        # originality4_cpc
        if len(patent['reference'])!=0:
            this_patent_cpc_histogram = {'__init__': 0}
            for reference in patent['reference']:
                for cpc in reference['CPC'][0]:
                    if cpc in this_patent_cpc_histogram:
                       this_patent_cpc_histogram[cpc] = this_patent_cpc_histogram[cpc] + 1
                    else:
                        this_patent_cpc_histogram[cpc] = 1
            this_patent_cpc_histogram_value = np.array(list(this_patent_cpc_histogram.values()))
            this_patent_cpc_histogram_value = this_patent_cpc_histogram_value / np.sum(this_patent_cpc_histogram_value)
            total_originality4_cpc += 1 - np.sum(this_patent_cpc_histogram_value**2)

        # Add all used USPC number into the list
        for uspc in patent['US']:
            if uspc not in used_uspc_list:
                used_uspc_list.append(uspc)

        # Add all used CPC number into the list
        for cpc in patent['CPC']:
            if cpc not in used_cpc_list:
                used_cpc_list.append(cpc)

        # Add averaged cycle time from all future referenced by patents
        for i_index, i_window_length in enumerate(window_length):
            total_avg_cycle_time = 0
            if len(patent['referenced_by']) != 0:
                this_patent_total_cycle_time = 0
                counted_referenced_by = 0
                for referenced_by_patent in patent['referenced_by']:
                    temp = Get_Year_Difference(target_year, referenced_by_patent['date'])
                    if temp <= i_window_length: # the referenced_by patent is inside the window of cycle time
                        this_patent_total_cycle_time += temp
                        if temp!=0:
                            counted_referenced_by += 1
                if counted_referenced_by != 0:
                    total_avg_cycle_time += this_patent_total_cycle_time/counted_referenced_by # /len(patent['referenced_by'])
                else:
                    total_avg_cycle_time += 0
            total_avg_cycle_time_list[i_index] += total_avg_cycle_time

        # Add averaged cycle time from all past refernce patents
        for i_index, i_window_length in enumerate(window_length):
            total_avg_cycle_time_backward = 0
            if len(patent['reference']) != 0:
                this_patent_total_cycle_time_backward = 0
                counted_reference = 0
                for reference_patent in patent['reference']:
                    temp = abs(Get_Year_Difference(target_year, reference_patent['date']))
                    if temp <= i_window_length: # the referenced_by patent is inside the window of cycle time
                        this_patent_total_cycle_time_backward += temp
                        if temp!=0:
                            counted_reference += 1
                if counted_reference != 0:
                    total_avg_cycle_time_backward += this_patent_total_cycle_time_backward/counted_reference # /len(patent['referenced_by'])
                else:
                    total_avg_cycle_time_backward += 0
            total_avg_cycle_time_backward_list[i_index] += total_avg_cycle_time_backward

        # Check collaboration
        if len(city_of_collaboration) == 0: # if any city is acceptable
            if len(patent['inventors']) >= 2:
                if patent['inventors'][0]['city'] == patent['inventors'][1]['city']: # check first two inventors
                    total_intra_regional += 1
                elif patent['inventors'][0]['country'] == patent['inventors'][1]['country']: # check first two countries
                    total_inter_regional += 1
                else:
                    total_international += 1
            else:
                total_intra_regional += 1
        else:
            for i_city in city_of_collaboration:
                if patent['inventors'][0]['city'] == i_city: # if the 1st inventor is in the setted city
                    if len(patent['inventors']) >= 2:
                        if patent['inventors'][0]['city'] == patent['inventors'][1]['city']: # check first two inventors
                            total_intra_regional += 1
                        elif patent['inventors'][0]['country'] == patent['inventors'][1]['country']: # check first two countries
                            total_inter_regional += 1
                        else:
                            total_international += 1
                    else:
                        total_intra_regional += 1
                break

    # Calculate all the index
    try:
        index_localization = total_region_reference_itself_count / total_region_reference_count
    except ZeroDivisionError:
        index_localization = 0

    index_diversification_uspc = len(used_uspc_list) / USPC_COUNT
    index_diversification_cpc = len(used_cpc_list) / CPC_COUNT

    if total_patent_count_in_target_year != 0: # avoid zero division
        index_originality1_uspc = total_originality1_uspc / total_patent_count_in_target_year
        index_originality2_uspc = total_originality2_uspc / total_patent_count_in_target_year
        index_originality3_uspc = total_originality3_uspc / total_patent_count_in_target_year
        index_originality4_uspc = total_originality4_uspc / total_patent_count_in_target_year
        index_originality1_cpc = total_originality1_cpc / total_patent_count_in_target_year
        index_originality2_cpc = total_originality2_cpc / total_patent_count_in_target_year
        index_originality3_cpc = total_originality3_cpc / total_patent_count_in_target_year
        index_originality4_cpc = total_originality4_cpc / total_patent_count_in_target_year
#        print(total_avg_cycle_time_list)
        index_cycle_time = list(np.array(total_avg_cycle_time_list, dtype='float') / total_patent_count_in_target_year)
        index_cycle_time_backward = list(np.array(total_avg_cycle_time_backward_list, dtype='float') / total_patent_count_in_target_year)
        index_collab_intra_regional = total_intra_regional / total_patent_count_in_target_year
        index_collab_inter_regional = total_inter_regional / total_patent_count_in_target_year
        index_collab_international = total_international / total_patent_count_in_target_year
    else:
        index_originality1_uspc = 0
        index_originality2_uspc = 0
        index_originality3_uspc = 0
        index_originality4_uspc = 0
        index_originality1_cpc = 0
        index_originality2_cpc = 0
        index_originality3_cpc = 0
        index_originality4_cpc = 0
        index_cycle_time = list(np.zeros(len(window_length)))
        index_cycle_time_backward = list(np.zeros(len(window_length)))
        index_collab_intra_regional = 0
        index_collab_inter_regional = 0
        index_collab_international = 0

    # HHI
    if total_patent_count_in_target_year != 0:
        all_assignee_patent_count = list(assignee_histogram.values())
        all_assignee_patent_count.sort(reverse=True)
        all_assignee_patent_count = np.array(all_assignee_patent_count[0:5]) / total_patent_count_in_target_year
        index_HHI = np.sum(all_assignee_patent_count**2)
    else:
        index_HHI = 0
#    with open('assignee_histogram.json', 'w') as fp:
#        json.dump(assignee_histogram, fp)

    return index_localization, index_HHI, index_originality1_uspc, index_originality2_uspc, index_originality3_uspc, index_originality4_uspc,\
            index_originality1_cpc, index_originality2_cpc, index_originality3_cpc, index_originality4_cpc,\
            index_diversification_uspc, index_diversification_cpc, \
            index_cycle_time, index_cycle_time_backward, index_collab_intra_regional, index_collab_inter_regional, \
            index_collab_international, assignee_histogram, total_patent_count_in_target_year

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=False, type=str, default='./output_Penang/',
                    help="directory to input .json files")
    ap.add_argument("-o", "--output", required=False, type=str, default='./index_result/',
                    help="directory to save calculated indexes")
    ap.add_argument("-r", "--region", nargs='+', required=False, type=str, default=['Penang', 'penang'],
                    help="Target region (case-sensitive!)")
    ap.add_argument("-y", "--year", nargs='+', type=int, default=[1970, 2015],
                    help='the starting year and ending year of index calculation')
    ap.add_argument("-w", "--window", nargs='+',  type=int, default=[3, 1],
                    help='window length (in year) to calculate cycle time index')
    ap.add_argument("-cc", "--city_of_collaboration", nargs='+',  type=str, default=[],
                    help='Switch for collaboration index, if not setted then any city is acceptable')
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
    orginality1_uspc = []
    orginality2_uspc = []
    orginality3_uspc = []
    orginality4_uspc = []
    orginality1_cpc = []
    orginality2_cpc = []
    orginality3_cpc = []
    orginality4_cpc = []
    diversification_uspc = []
    diversification_cpc = []
    cycle_time = []
    cycle_time_backward = []
    intra_collab = []
    inter_collab = []
    international_collab = []

    print("Would start calculate indexes from {} to {}, region: {}, window_legnth: {}".format(ARGS.year[0], ARGS.year[1], ARGS.region, ARGS.window))
    if len(ARGS.city_of_collaboration) != 0:
        print("City of collaboration is setted to {}".format(ARGS.city_of_collaboration))
    else:
        print("City of collaboration is not setted, so any city is acceptable")

    input("Press Enter to continue...")
    for i_year in range(ARGS.year[0], ARGS.year[1]+1):
        index_localization, index_HHI, index_originality1_uspc, index_originality2_uspc, index_originality3_uspc, index_originality4_uspc,\
        index_originality1_cpc, index_originality2_cpc, index_originality3_cpc, index_originality4_cpc,\
        index_diversification_uspc, index_diversification_cpc, \
        index_cycle_time, index_cycle_time_backward, index_collab_intra_regional, index_collab_inter_regional, \
        index_collab_international, assignee_histogram, total_patent_count_in_target_year\
        = Calculate_Index(all_patent_info, str(i_year), ARGS.region, ARGS.window, ARGS.city_of_collaboration)

        # append index to list
        year.append(i_year)
        patent_count.append(total_patent_count_in_target_year)
        localization.append(index_localization)
        HHI.append(index_HHI)
        orginality1_uspc.append(index_originality1_uspc)
        orginality2_uspc.append(index_originality2_uspc)
        orginality3_uspc.append(index_originality3_uspc)
        orginality4_uspc.append(index_originality4_uspc)
        orginality1_cpc.append(index_originality1_cpc)
        orginality2_cpc.append(index_originality2_cpc)
        orginality3_cpc.append(index_originality3_cpc)
        orginality4_cpc.append(index_originality4_cpc)
        diversification_uspc.append(index_diversification_uspc)
        diversification_cpc.append(index_diversification_cpc)
        cycle_time.append(index_cycle_time)
        cycle_time_backward.append(index_cycle_time_backward)
        intra_collab.append(index_collab_intra_regional)
        inter_collab.append(index_collab_inter_regional)
        international_collab.append(index_collab_international)

    # Make dictionary
    index_dict = {
            'year': year,
            'patent_count': patent_count,
            'localization': localization,
            'HHI': HHI,
            'orginality1_uspc': orginality1_uspc,
            'orginality2_uspc': orginality2_uspc,
            'orginality3_uspc': orginality3_uspc,
            'orginality4_uspc': orginality4_uspc,
            'orginality1_cpc': orginality1_cpc,
            'orginality2_cpc': orginality2_cpc,
            'orginality3_cpc': orginality3_cpc,
            'orginality4_cpc': orginality4_cpc,
            'diversification_uspc': diversification_uspc,
            'diversification_cpc': diversification_cpc,
#            'cycle_time': cycle_time,
#            'cycle_time_backward': cycle_time_backward,
            'intra_regional_collaboration_{}'.format(ARGS.city_of_collaboration): intra_collab,
            'inter_regional_collaboration_{}'.format(ARGS.city_of_collaboration): inter_collab,
            'international_collaboration_{}.format(ARGS.city_of_collaboration)': international_collab
            }

    # List of cycle time with different window length
    for i in range(len(ARGS.window)):
        this_window_cycle_time = []
        for i_year in range(len(cycle_time)):
            this_window_cycle_time.append(cycle_time[i_year][i])
        index_dict['cycle_time_{}'.format(ARGS.window[i])] = this_window_cycle_time

    # List of cycle time backward with different window length
    for i in range(len(ARGS.window)):
        this_window_cycle_time_backward = []
        for i_year in range(len(cycle_time_backward)):
            this_window_cycle_time_backward.append(cycle_time_backward[i_year][i])
        index_dict['cycle_time_backward_{}'.format(ARGS.window[i])] = this_window_cycle_time_backward

#    for i in range(len(ARGS.window)):
#        index_dict['cycle_time_backward_{}'.format(ARGS.window[i])] = cycle_time_backward[i]

    index_df = pd.DataFrame(index_dict)
    print("Store calculated index result to {}".format(output_csv_path))
    index_df.to_csv(output_csv_path)
    index_df.to_pickle(output_pkl_path)