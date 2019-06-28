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


def get_size(obj, seen=None):
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
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

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
print("Memory usage : {} Mb".format(get_size(all_patent_info)/1000/1000))

target_year = "2018"
target_region = "Broomfield"
target_whole_area ="?"

# Localization
total_region_citation_count = 0
total_whole_area_citation_count = 0
total_region_cite_region_count = 0
total_not_cite_region_count = 0

# HHI
total_patent_count = 0
top_five_assignee_patent_count = 0

# Orginality

# Diversification
total_uspc_count = 0

# Cycle time
total_cycle_time = 0