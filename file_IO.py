# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 02:36:29 2019

@author: user
"""

import csv

def Write_one_patent_to_csv(patent_info, file_name, file_open_mode='a'):
    if patent_info is None:
        return

    # Separate the information to 5 .csv files
    fname_title = file_name + "_title_inventor.csv"
    fname_ass = file_name + "_assignee.csv"
    fname_US = file_name + "_US.csv"
    fname_CPC = file_name + "_CPC.csv"
    fname_International = file_name + "_International.csv"

    with open(fname_title, file_open_mode, newline='') as file_title, \
        open(fname_ass, file_open_mode, newline='') as file_ass,\
        open(fname_US, file_open_mode, newline='') as file_US, \
        open(fname_CPC, file_open_mode, newline='') as file_CPC, \
        open(fname_International, file_open_mode, newline='') as file_International:
#    with open(file_name, file_open_mode, newline='') as csv_file:

        p = patent_info

        # Title + Date + Inventors
        out_row_list = []
        w = csv.writer(file_title)
        out_row_list.extend(['original'])
        out_row_list.extend(['ID', p['ID']])
        out_row_list.extend(['title', p['title']])
        out_row_list.extend(['date', p['date']])

        for _inventor in p['inventors']:
            if 'name' in _inventor:
                out_row_list.extend(['inventor_name', _inventor['name']])
            if 'city' in _inventor:
                out_row_list.extend(['inventor_city', _inventor['city']])
            if 'country' in _inventor:
                out_row_list.extend(['inventor_country', _inventor['country']])
        # Write row
        w.writerow(out_row_list)

        # Assignee
        out_row_list = []
        w = csv.writer(file_ass)
        out_row_list.extend(['original'])
        out_row_list.extend(['ID', p['ID']])
        for _assignee in p['assignee']:
            if 'name' in _assignee:
                out_row_list.extend(['assignee_name', _assignee['name']])
            if 'city' in _assignee:
                out_row_list.extend(['assignee_city', _assignee['city']])
            if 'country' in _assignee:
                out_row_list.extend(['assignee_country', _assignee['country']])
        # Write row
        w.writerow(out_row_list)

        # US Class
        out_row_list = []
        w = csv.writer(file_US)
        out_row_list.extend(['original'])
        out_row_list.extend(['ID', p['ID']])
        for _US in p['US']:
            out_row_list.extend(['US_class', _US])
        # Write row
        w.writerow(out_row_list)

        # CPC Class
        out_row_list = []
        w = csv.writer(file_CPC)
        out_row_list.extend(['original'])
        out_row_list.extend(['ID', p['ID']])
        for _CPC in p['CPC']:
            out_row_list.extend(['CPC_class', _CPC])
        # Write row
        w.writerow(out_row_list)

        # CPC Class
        out_row_list = []
        w = csv.writer(file_International)
        out_row_list.extend(['original'])
        for _international in p['international']:
            out_row_list.extend(['international_class', _international])
        # Write row
        w.writerow(out_row_list)

        # For each reference patent
        for _ref in patent_info['reference']:
            p = _ref
            out_row_list = []
            out_row_list.extend(['reference'])
            out_row_list.extend(['ID', p['ID']])
            out_row_list.extend(['title', p['title']])
            out_row_list.extend(['date', p['date']])

            # Title + Date + Inventors
            w = csv.writer(file_title)
            for _inventor in p['inventors']:
                if 'name' in _inventor:
                    out_row_list.extend(['inventor_name', _inventor['name']])
                if 'city' in _inventor:
                    out_row_list.extend(['inventor_city', _inventor['city']])
                if 'country' in _inventor:
                    out_row_list.extend(['inventor_country', _inventor['country']])
            # Write row
            w.writerow(out_row_list)

            # Assignee
            out_row_list = []
            w = csv.writer(file_ass)
            out_row_list.extend(['reference'])
            out_row_list.extend(['ID', p['ID']])
            for _assignee in p['assignee']:
                if 'name' in _assignee:
                    out_row_list.extend(['assignee_name', _assignee['name']])
                if 'city' in _assignee:
                    out_row_list.extend(['assignee_city', _assignee['city']])
                if 'country' in _assignee:
                    out_row_list.extend(['assignee_country', _assignee['country']])
            # Write row
            w.writerow(out_row_list)

            # US Class
            out_row_list = []
            w = csv.writer(file_US)
            out_row_list.extend(['reference'])
            out_row_list.extend(['ID', p['ID']])
            for _US in p['US']:
                out_row_list.extend(['US_class', _US])
            # Write row
            w.writerow(out_row_list)

            # CPC Class
            out_row_list = []
            w = csv.writer(file_CPC)
            out_row_list.extend(['reference'])
            out_row_list.extend(['ID', p['ID']])
            for _CPC in p['CPC']:
                out_row_list.extend(['CPC_class', _CPC])
            # Write row
            w.writerow(out_row_list)

            # CPC Class
            out_row_list = []
            w = csv.writer(file_International)
            out_row_list.extend(['reference'])
            for _international in p['international']:
                out_row_list.extend(['international_class', _international])
            # Write row
            w.writerow(out_row_list)

        # For each referenced by patent
        for _ref in patent_info['referenced_by']:
            p = _ref
            out_row_list = []
            out_row_list.extend(['referenced_by'])
            out_row_list.extend(['ID', p['ID']])
            out_row_list.extend(['title', p['title']])
            out_row_list.extend(['date', p['date']])

            # Title + Date + Inventors
            w = csv.writer(file_title)
            for _inventor in p['inventors']:
                if 'name' in _inventor:
                    out_row_list.extend(['inventor_name', _inventor['name']])
                if 'city' in _inventor:
                    out_row_list.extend(['inventor_city', _inventor['city']])
                if 'country' in _inventor:
                    out_row_list.extend(['inventor_country', _inventor['country']])
            # Write row
            w.writerow(out_row_list)

            # Assignee
            out_row_list = []
            w = csv.writer(file_ass)
            out_row_list.extend(['referenced_by'])
            out_row_list.extend(['ID', p['ID']])
            for _assignee in p['assignee']:
                if 'name' in _assignee:
                    out_row_list.extend(['assignee_name', _assignee['name']])
                if 'city' in _assignee:
                    out_row_list.extend(['assignee_city', _assignee['city']])
                if 'country' in _assignee:
                    out_row_list.extend(['assignee_country', _assignee['country']])
            # Write row
            w.writerow(out_row_list)

            # US Class
            out_row_list = []
            w = csv.writer(file_US)
            out_row_list.extend(['referenced_by'])
            out_row_list.extend(['ID', p['ID']])
            for _US in p['US']:
                out_row_list.extend(['US_class', _US])
            # Write row
            w.writerow(out_row_list)

            # CPC Class
            out_row_list = []
            w = csv.writer(file_CPC)
            out_row_list.extend(['referenced_by'])
            out_row_list.extend(['ID', p['ID']])
            for _CPC in p['CPC']:
                out_row_list.extend(['CPC_class', _CPC])
            # Write row
            w.writerow(out_row_list)

            # CPC Class
            out_row_list = []
            w = csv.writer(file_International)
            out_row_list.extend(['referenced_by'])
            for _international in p['international']:
                out_row_list.extend(['international_class', _international])
            # Write row
            w.writerow(out_row_list)