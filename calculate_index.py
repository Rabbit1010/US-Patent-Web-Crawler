# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 14:30:05 2019

@author: Wei-Hsiang, Shen
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys
from tqdm import tqdm

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
    offset_year = referenced_by_year.split(', ')[-1]

    if base_year<=1500 or offset_year<=1500:
        print("[WARNING] One patent is weird (invented year before 1500), ID:{}".format(referenced_by_patent['ID']))

    if base_year>offset_year:
        return 0
    else:
        return offset_year - base_year

in_dir = './output/'
csv_title_inventor = './output/patent_info.json'

all_patent_info = []

print("Reading all patent data from disk to memory...")
for filename in tqdm(os.listdir(in_dir)):
    if filename.lower().endswith('.json') == False :
        continue
    file_path = os.path.join(in_dir, filename)

    all_patent_info.append(Read_json(file_path))
print("Patent count : {}".format(len(all_patent_info)))
print("Memory usage : {} Mb".format(Get_Object_Memory_Size(all_patent_info)/1000/1000))

target_year = "2018"
target_region = "Broomfield"
target_whole_area ="?"
USPC_COUNT = 472 # total number of all USPC available in the patent database

# Localization
total_region_citation_count = 0
total_whole_area_citation_count = 0
total_region_cite_region_count = 0
total_not_cite_region_count = 0

# HHI
total_patent_count_in_target_year = 0
assignee_histogram = {'__init__': 0}

# Orginality

# Diversification
used_uspc_list = []

# Cycle time
total_cycle_time = 0

# Loop through all patents
print("Going through all the patents...")
for patent in tqdm(all_patent_info):
    if target_year not in patent['date']: # ignore patents that are not in the given year
        continue

    total_patent_count_in_target_year += 1

    # Add all assignee into the histogram
    for assignee in patent['assignee']:
        if assignee['name'] in assignee_histogram:
            assignee_histogram[assignee['name']] = assignee_histogram[assignee['name']]+1
        else:
            assignee_histogram[assignee['name']] = 1

    # Add all used USPC number into the list
    for uspc in patent['US']:
        if uspc not in used_uspc_list:
            used_uspc_list.append(uspc)

    # Add cycle time from all future referenced by patents
    for referenced_by_patent in patent['referenced_by']:
        total_cycle_time += Get_Year_Difference(target_year, referenced_by_patent['date'])

# Calculate all the index
index_localization = 0
index_orginality = 0
index_diversification = len(used_uspc_list) / USPC_COUNT
index_cycle_time = total_cycle_time / total_patent_count_in_target_year

# HHI
all_assignee_patent_count = list(assignee_histogram.values())
all_assignee_patent_count.sort(reverse=True)
top_five_assignee_patent_count = np.mean(all_assignee_patent_count[0:5])