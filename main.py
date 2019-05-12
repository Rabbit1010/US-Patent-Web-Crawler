# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 14:12:17 2019

@author: user
"""

import os.path
import argparse
import requests
import pickle
from tqdm import tqdm
from bs4 import BeautifulSoup

from file_IO import Write_one_patent_to_csv

WARNINGS = True
DEBUG = False

def Get_HTML_in_URL(url):
    # Fake a header
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    r = requests.get(url, headers=headers)

    if r.status_code != requests.codes.ok:
        raise RuntimeError("[ERROR] Unable to access the server. (Is the website correct or the website is down?")

    return r.text

def Get_Patent_Info_by_First_Page(first_url):
    # Get Patent ID in title
    html_text = Get_HTML_in_URL(first_url)
    soup = BeautifulSoup(html_text, 'html.parser') # Load html raw text into soup
    patent_ID = soup.title.string.split(' ')[-1]

    # if this is not a query page but a patent page
    if Beautify_String(patent_ID) != "Collection":
        query_links = []
        query_links.append(first_url)
        return None, query_links

    html_text = Get_HTML_in_URL(first_url)
    query_result, next_link = Get_Query_Info_in_one_HTML(html_text)

    # Get all query result for every list (since each list only contains 50 result)
    while next_link is not None:
        html_text = Get_HTML_in_URL(url=next_link)
        patents_info_one_page, next_link = Get_Query_Info_in_one_HTML(html_text)
        query_result = [*query_result, *patents_info_one_page] # merge two list (PEP style)

    query_links = []
    for patent in query_result:
        query_links.append(patent['Link'])

    return query_result, query_links

def Beautify_String(string):
    out = string.replace('\n',' ')
    out = out.rstrip() # remove leading whit spaces
    out = out.lstrip() # remove trailing white spaces
    out = ' '.join(out.split()) # remove multiple white spaces

    return out

def Get_Patent_Info_in_one_URL(url, simple=False):
    # Ignore AppFT Database
    if url.find("appft") != -1:
        return None

    html_text = Get_HTML_in_URL(url)
    soup = BeautifulSoup(html_text, 'html.parser') # Load html raw text into soup

    # Single Document would brought us to another page
    if soup.title.string == "Single Document":
        translate_url = "http://patft.uspto.gov" + soup.findAll('meta')[0]['content'].split('URL=')[-1]
        html_text = Get_HTML_in_URL(translate_url)
        soup = BeautifulSoup(html_text, 'html.parser') # Load html raw text into soup

    # Get Patent ID in title
    patent_ID = soup.title.string.split(' ')[-1]
    if Beautify_String(patent_ID) == "Collection":
        return None

    # Get Patent Name
    fonts = soup.findAll('font')
    for font in fonts:
        try:
            if font['size'] == '+1':
                patent_title = Beautify_String(font.text)
        except KeyError: # this page probably is empty
            return None

#    print("[INFO] Crawling Patent url: {}".format(url))
    if DEBUG == True:
        print(patent_ID)

    # Find all tables
    tables = soup.findAll('table')
    links = soup.findAll('a')

    # The 3rd table is the table containing patent date
    patent_date = Beautify_String(tables[2].findAll('td')[3].find('b').string)

    # The 4st table is the table containing patent inventors and assignee
    patent_inventors = 'NONE'
    patent_assignee = 'NONE'
    for i in range(3,5):
        try:
            if tables[i].findAll('th')[0].text == 'Inventors:':
                patent_inventors = Beautify_String(tables[i].findAll('td')[0].text)
            if tables[i].findAll('th')[1].text == 'Assignee:':
                patent_assignee = Beautify_String(tables[i].findAll('td')[1].text)
            if tables[i].findAll('th')[2].text == 'Assignee:':
                patent_assignee = Beautify_String(tables[i].findAll('td')[2].text)
            if tables[i].findAll('th')[3].text == 'Assignee:':
                patent_assignee = Beautify_String(tables[i].findAll('td')[3].text)
        except IndexError:
            continue
        if patent_inventors!='NONE' and patent_assignee!='NONE':
            break

    if patent_inventors!='NONE' and patent_assignee=='NONE':
        trs = soup.findAll('tr')
        for tr in trs:
            if Beautify_String(tr.text).partition(' ')[0]=='Assignee:':
                patent_assignee = Beautify_String(tr.text).partition(' ')[1:][1]

    if patent_inventors=='NONE' and WARNINGS==True:
        print("[WARNING] Cannot parse inventors or there is no inventor information, ID: {}".format(patent_ID))

    if patent_assignee=='NONE' and WARNINGS==True:
        print("[WARNING] Cannot parse assignee or there is no assignee information, ID: {}".format(patent_ID))

    # Parse out each inventor
    patent_inventors_list = []
    # locate ',' that is outside parenthesis
    comma_loc = [-1,]
    flag = False
    for index, char in enumerate(patent_inventors):
        if flag==False and char==',':
            comma_loc.append(index)
        elif char=='(':
            flag = True
        elif char==')':
            flag = False
    comma_loc.append(len(patent_inventors))
    # string split to parse out each inventor using comma's location
    for loc in range(len(comma_loc)-1):
        patent_inventors_list.append(Beautify_String(patent_inventors[comma_loc[loc]+1:comma_loc[loc+1]]))

    # Get inventor info from string
    patent_inventors_info = []
    for _s in patent_inventors_list:
        if '(' in _s and ')' in _s:
            info = {'name': Beautify_String(_s.replace('('+_s[_s.find("(")+1:_s.find(")")]+')',''))}
            info['location'] = Beautify_String(_s[_s.find("(")+1:_s.find(")")])
        else:
            info = {'name': Beautify_String(_s)}
        patent_inventors_info.append(info)

    for _info in patent_inventors_info:
        if 'location' in _info: # the inventor has location information
            if len(_info['location'].split(',')) <= 1:
                _info['country'] = Beautify_String(_info['location'].split(',')[0])
            else:
                _info['city'] = Beautify_String(_info['location'].split(',')[-2].split(' ')[-1])
                _info['country'] = Beautify_String(_info['location'].split(',')[-1])

    # Parse out each assignee (string split using ';')
    patent_assignee_list = []
    for _assignee in patent_assignee.split(';'):
        patent_assignee_list.append(Beautify_String(_assignee))

    # Get assignee info from string
    patent_assignee_info = []
    for _s in patent_assignee_list:
        if '(' in _s and ')' in _s:
            info = {'name': Beautify_String(_s.replace('('+_s[_s.rfind("(")+1:_s.rfind(")")]+')',''))}
            info['location'] = Beautify_String(_s[_s.rfind("(")+1:_s.rfind(")")])
        else:
            info = {'name': Beautify_String(_s)}
        patent_assignee_info.append(info)

    for _info in patent_assignee_info:
        if 'location' in _info: # the inventor has location information
            if len(_info['location'].split(',')) <= 1:
                _info['country'] = Beautify_String(_info['location'].split(',')[0])
            else:
                _info['city'] = Beautify_String(_info['location'].split(',')[0])
                _info['country'] = Beautify_String(_info['location'].split(',')[1])

    # The 6st table is the table containing Class and its numbers
    patent_US_Class = 'NONE'
    patent_CPC_Class = 'NONE'
    patent_International_Class = 'NONE'
    for i in range(4,9):
        try:
            if Beautify_String(tables[i].findAll('td')[0].text) == 'Current U.S. Class:':
                patent_US_Class = Beautify_String(tables[i].findAll('td')[1].text)

            if Beautify_String(tables[i].findAll('td')[0].text) == 'Current CPC Class:':
                patent_CPC_Class = Beautify_String(tables[i].findAll('td')[1].text)
            if Beautify_String(tables[i].findAll('td')[2].text) == 'Current CPC Class:':
                patent_CPC_Class = Beautify_String(tables[i].findAll('td')[3].text)

            if Beautify_String(tables[i].findAll('td')[0].text) == 'Current International Class:':
                patent_International_Class = Beautify_String(tables[i].findAll('td')[1].text)
            if Beautify_String(tables[i].findAll('td')[2].text) == 'Current International Class:':
                patent_International_Class = Beautify_String(tables[i].findAll('td')[3].text)
            if Beautify_String(tables[i].findAll('td')[4].text) == 'Current International Class:':
                patent_International_Class = Beautify_String(tables[i].findAll('td')[5].text)
        except IndexError:
            continue

        if patent_US_Class!='NONE' and patent_CPC_Class!='NONE' and patent_International_Class!='NONE':
            break

    if patent_US_Class=='NONE' and WARNINGS==True:
        print("[WARNING] Cannot parse US Class, or there is no information, ID: {}".format(patent_ID))
    if patent_CPC_Class=='NONE' and WARNINGS==True:
        print("[WARNING] Cannot parse CPC Class, or there is no information, ID: {}".format(patent_ID))
    if patent_International_Class=='NONE' and WARNINGS==True:
        print("[WARNING] Cannot parse international Class, or there is no information, ID: {}".format(patent_ID))

    # Parse out each US Class (string split using ';')
    patent_US_Class_list = []
    for _s in patent_US_Class.split(';'):
        patent_US_Class_list.append(Beautify_String(_s)[:3].split('/')[0]) # only need the first 3 digits

    # Parse out each CPC Class (string split using ';')
    patent_CPC_Class_list = []
    for _s in patent_CPC_Class.split(';'):
        patent_CPC_Class_list.append(Beautify_String(_s)[:4]) # only need the first 4 digits

    # Parse out each International Class (string split using ';')
    patent_International_Class_list = []
    for _s in patent_International_Class.split(';'):
        patent_International_Class_list.append(Beautify_String(_s)[:4]) # only need the first 4 digits

    # Delete duplicated class number, so that it only appears once
    patent_US_Class_list = list(set(patent_US_Class_list))
    patent_CPC_Class_list = list(set(patent_CPC_Class_list))
    patent_International_Class_list = list(set(patent_International_Class_list))

    # Hand-code exceptions (Patents that are hard to parse)
    if patent_ID == "4825599":
        patent_inventors_info = []
        info = {'name': 'Swann, Jr.; Jack T.'}
        info['city'] = 'Huntsville'
        info['country'] = 'AL'
        patent_inventors_info.append(info)
    elif patent_ID == "9964563":
        patent_inventors_info = []
        info = {'name': 'Gunasing; David Durai Pandian Sam'}
        info['city'] = 'Penang'
        info['country'] = 'MY'
        patent_inventors_info.append(info)
        info = {'name': 'Min; Teh Wee'}
        info['city'] = 'Penang'
        info['country'] = 'MY'
        patent_inventors_info.append(info)

    if simple==False:
        # Find the link to all referenced by
        reference_link_index = 0
        referenced_by_link = 'NONE'
        for index, link in enumerate(links):
            if Beautify_String(link.text) == '[Referenced By]':
                referenced_by_link = 'http://patft.uspto.gov/' + link['href']
                reference_link_index = index

        # Go into referenced by link and get all link to referenced by
        if referenced_by_link != 'NONE':
            _, patent_referenced_by_links = Get_Patent_Info_by_First_Page(first_url=referenced_by_link)
        else:
            patent_referenced_by_links = []

        # Visit each link and get its simple info
        patent_referenced_by = []
        for link in patent_referenced_by_links:
            info = Get_Patent_Info_in_one_URL(link, simple=True)
            if info is not None:
                patent_referenced_by.append(info)

        # Find all links to reference
        patent_reference_links = []
        for index, link in enumerate(links):
            if index > reference_link_index and len(Beautify_String(link.text)) >= 7:
                patent_reference_links.append('http://patft.uspto.gov/' + link['href'])

        # Visit each link and get its simple info
        patent_reference = []
        for link in patent_reference_links:
            info = Get_Patent_Info_in_one_URL(link, simple=True)
            if info is not None:
                patent_reference.append(info)


    # Pack all info of this patent into a container
    patent_info = {'ID': patent_ID}
    patent_info['date'] = patent_date
    patent_info['inventors'] = patent_inventors_info
    patent_info['title'] = patent_title
    patent_info['assignee'] = patent_assignee_info
    patent_info['US'] = patent_US_Class_list
    patent_info['CPC'] = patent_CPC_Class_list
    patent_info['international'] = patent_International_Class_list
    if simple==False:
        patent_info['reference_link'] = patent_reference_links
        patent_info['referenced_by_link'] = patent_referenced_by_links
        patent_info['reference'] = patent_reference
        patent_info['referenced_by'] = patent_referenced_by

    return patent_info

def Get_Query_Info_in_one_HTML(html_text):
    # Load html raw text into soup
    soup = BeautifulSoup(html_text, 'html.parser')
    # Find all tables
    tables = soup.findAll(lambda tag: tag.name=='table')

    if len(tables)<=2: # no query
        return [], None

    # The 2nd table is the table containing all the patent search results
    patent_table = tables[1]
    # Find all links inside the patent table
    links = patent_table.findAll('a')

    patents_info = [] # a list of dictionaries

    for index, link in enumerate(links):
        if index % 2 == 0: # patent number with link
            patent_num_str = link.string
        else: # patent title with link
            patent_title = Beautify_String(link.string)
            patent_link = 'http://patft.uspto.gov/' + link['href']
            a_patent = {'ID': patent_num_str, 'Title': patent_title, 'Link': patent_link}
            patents_info.append(a_patent)

    # Find the next link of the list
    next_link = None
    links = soup.findAll('a')
    for link in links:
        if link.img!=None and link.img.has_attr('alt') and link.img['alt'] == '[NEXT_LIST]':
            next_link = 'http://patft.uspto.gov/' + link['href']

    return patents_info, next_link

def main():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--mode", required=False, default='single',
                    help="Mode, single or many")
    ap.add_argument("-i", "--input", required=False, default='./input_URL.txt',
                    help="Path to input .txt file")
    ap.add_argument("-o", "--output", required=False, default='./output/patent_info',
                    help="Path to output .csv file")
    ap.add_argument("-w", "--warnings", required=False, default=True,
                    help="Show warning messages or not")
    ap.add_argument("-d", "--debug", required=False, default=False,
                    help="Show debug message or not")
    args = vars(ap.parse_args())

    global DEBUG
    if args['debug']=='True' or args['debug']=='true':
        DEBUG = True

    global WARNINGS
    if args['warnings']=='False' or args['warnings']=='false':
        WARNINGS = False

    # Read input URL
    if not os.path.isfile(args['input']): # check if output file already exist
        print("[ERROR] Input file {} does not exist.".format(args['input']))
        return
    with open(args['input']) as f:
        print("[INFO] Read input file : {}".format(args['input']))
        URL_in = f.readline()
        print("[INFO] Read input URL : {}".format(URL_in))

    # Testing
    args['mode'] = 'single'
    URL_in = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=18&f=G&l=50&d=PTXT&p=1&S1=4825599&OS=4825599&RS=4825599'
#    args['mode'] = 'many'
#    URL_in = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&RS=%28%28IC%2FPenang+AND+APT%2F1%29+AND+ISD%2F20180501-%3E20180631%29&Refine=Refine+Search&Query=9964563'

    # Single mode
    if args['mode'] == 'single':
        if os.path.isfile(args['output'] + "_title_inventor.csv"): # check if output file already exist
            print("[WARNING] Output file {} already exist, will overwrite it.".format(args['output'] + "_title_inventor.csv"))
        patent_info = Get_Patent_Info_in_one_URL(url=URL_in)
        Write_one_patent_to_csv(patent_info, args['output'], file_open_mode='w')

    # Many mode
    if args['mode'] == 'many':
        if os.path.isfile(args['output'] + "_title_inventor.csv"): # check if output file already exist
            print("[WARNING] Output file {} already exist, will overwrite it.".format(args['output'] + "_title_inventor.csv"))
        print("[INFO] Getting the links to all patents")
        _, all_links = Get_Patent_Info_by_First_Page(first_url=URL_in)

        # link information and initiailize checkpoint file
        total_link = len(all_links)
        current_link = 0

        # Load checpoint
        checkpoint_fname = './output/checkpoint.pkl'
        if os.path.isfile(checkpoint_fname): # Check if checkpoint exist
            print("[INFO] Checkpoint file exist, loading from checkpoint...")
            with open(checkpoint_fname, 'rb') as f:  # Python 3: open(..., 'rb')
                current_link, total_link_test = pickle.load(f)
                if total_link != total_link_test:
                    raise RuntimeError("[ERROR] The checkpoint file is incorrect, please delete it manually and restart it")

        # for each patent link
        for i in tqdm(range(current_link, total_link)):
            link = all_links[i]
            patent_info = Get_Patent_Info_in_one_URL(url=link)
            if i == 0:
                Write_one_patent_to_csv(patent_info, args['output'], file_open_mode='w')
            else:
                Write_one_patent_to_csv(patent_info, args['output'], file_open_mode='a')
            current_link += 1

            # save check point
            with open(checkpoint_fname, 'wb') as f:
                pickle.dump([current_link, total_link], f)

            # finish all link
            if current_link > total_link:
                os.remove(checkpoint_fname) # delete checkpoint file

if __name__ == '__main__':
    main()
