# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 22:41:36 2019

@author: user
"""

import requests

def Get_HTML_in_URL_with_query(search_params, url='http://patft.uspto.gov/netacgi/nph-Parser'):
     # Fake a header
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    r = requests.get(url, params = search_params, headers=headers)
    print("[INFO] Crawling the webpage = {}".format(r.url[-80:-10]))

    if r.status_code != requests.codes.ok:
        raise RuntimeError("Unable to access the server. (Is the website correct or the website is down?")

    return r.text

def Get_Patent_Info_by_Query(query='IC/Seoul AND APT/1 AND ISD/19950101->19951231', rs='((IC/Seoul AND APT/1) AND ISD/19950101->19951231)'):
    """
    %20 -> space
    %2F -> /
    %3e -> >
    """
    # Make a legal query
    search_params = {'Sect1': 'PTO2', 'Sect2': 'HITOFF'} # pre-defined search query
    search_params['u'] = "/netahtml/PTO/search-adv.htm"
    search_params['r'] = '0'
    search_params['f'] = 'S'
    search_params['l'] = '50'
    search_params['d'] = 'PTXT'
    search_params['RS'] = rs
    search_params['Refine'] = 'Refine Search'
    search_params['Query'] = query

    html_text = Get_HTML_in_URL_with_query(search_params)
    patents_info = []
    patents_info, next_link = Get_Patent_Info_in_one_HTML(html_text)

    while next_link is not None:
        html_text = Get_HTML_in_URL(url=next_link)
        patents_info_one_page, next_link = Get_Patent_Info_in_one_HTML(html_text)
        patents_info = [*patents_info, *patents_info_one_page] # merge two list (PEP style)

    return patents_info