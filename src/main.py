import logging
import re
import urllib.request
from typing import List

import pandas as pd
import requests
import tinycss2
from lxml import html

STORE_LIST = 'https://www.apple.com/retail/storelist/'
XPATH_MAIN = '//section[contains(@class,"section-store-summary") or contains(@class, "section-hero")]//figure[not(contains(@class, "360") or contains(@class,"loading"))]/@class'
XPATH_ADDITIONAL = '//div[contains(@class,"section-drawer")]//figure[not(contains(@class, "reptiles") or @class="image")]/@class'
XPATH_STYLESHEET = '//link[contains(@href, "store.built.css") or contains(@href, "store.css")]/@href'
APPLE_COM = 'https://www.apple.com'
logging.basicConfig(filename='main.log', filemode='w', level=logging.INFO)

def get_store_list() -> pd.DataFrame:
    """
    Create a data frame like the following
                    Link                                        Region
    The Summit      https://www.apple.com/retail/thesummit/     us
    Bridge Street   https://www.apple.com/retail/bridgestreet/  us
    """
    tree = get_html_tree(STORE_LIST)
    store_names = tree.xpath('//div[@id="main"]/section[3]//a/text()')
    store_links = tree.xpath('//div[@id="main"]/section[3]//a/@href')
    store_regions = [get_region_code(link) for link in store_links]
    return pd.DataFrame(data={'Link': store_links, 'Region': store_regions}, index=store_names)


def get_html_tree(link: str) -> html.HtmlElement:
    """
    Returns the root node of the html tree in the link.
    """
    page = requests.get(link)
    return html.fromstring(page.content)


def get_region_code(link: str) -> str:
    """
    Gets the 2-character country codes in a link. Return 'us' if missing.
    >>> get_region_code('https://www.apple.com/retail/storelist/')
    'us'
    >>> get_region_code('https://www.apple.com/hk/en/retail/ifcmall/')
    'hk'
    >>> get_region_code('https://www.apple.com.cn/cn/retail/kunming/')
    'cn'
    """
    return find_between(link, '.com', '/retail', ' us')[1:3]


def find_between(str, beg_str, end_str, default=''):
    """
    Find the string between beg_str and end_str exclusive.
    If there is no such string or the string is empty, return default.
    >>> find_between('https://www.apple.com.cn/cn/retail/kunming/', 'retail/', '/')
    'kunming'
    >>> find_between('https://www.apple.com.cn/cn/retail/kunming/', 'cn/', '/retail')
    'cn'
    >>> find_between('https://www.apple.com.cn/cn/retail/kunming/', 'cn/', '/fifthavenue', "not found")
    'not found'
    """
    start = str.find(beg_str) + len(beg_str)
    end = str.find(end_str, start)
    return str[start:end] if start < end else default


def find_after(str, beg_str, default=''):
    """
    Find the string after beg_str exclusive. If there is no such string or the string is empty, return default.
    >>> find_after('https://www.apple.com.cn/cn/retail/kunming/', 'retail/')
    'kunming/'
    >>> find_after('https://www.apple.com.cn/cn/retail/kunming/', 'kunming/', 'none')
    'none'
    >>> find_after('https://www.apple.com.cn/cn/retail/kunming/', 'abc/', 'none')
    'none'
    """
    start = str.find(beg_str) + len(beg_str)
    return str[start:] if start - len(beg_str) > -1 and start < len(str) else default


def find_before(str, beg_str, default=''):
    """
    Find the string before beg_str exclusive. If there is no such string or the string is empty, return default.
    >>> find_before('https://www.apple.com.cn/cn/retail/kunming/', 'retail/')
    'https://www.apple.com.cn/cn/'
    >>> find_before('https://www.apple.com.cn/cn/retail/kunming/', 'https', 'none')
    'none'
    >>> find_before('https://www.apple.com.cn/cn/retail/kunming/', 'abc/', 'none')
    'none'
    """
    start = str.find(beg_str)
    return str[:start] if start > 0 else default


def get_main_images(tree) -> List[str]:
    """
    Get the class name of the images in the main container.
    >>> len(get_main_images(get_html_tree('https://www.apple.com/hk/en/retail/ifcmall/')))
    8
    """
    classes = tree.xpath(XPATH_MAIN)
    output = []
    for cname in classes:
        if cname.find('hero') >= 0:
            output.append(cname.split()[0])
        else:
            output.append(cname.split()[-1])
    return output


def get_additional_images(tree) -> List[str]:
    """
    Get the class name of the additional images that are not located in the main container.
    >>> len(get_additional_images(get_html_tree('https://www.apple.com/it/retail/piazzaliberty/')))
    9
    >>> len(get_additional_images(get_html_tree('https://www.apple.com/retail/carnegielibrary/')))
    7
    """
    classes = tree.xpath(XPATH_ADDITIONAL)
    return [cname.split()[-1] for cname in classes]


def get_embedded_styles(tree, containing=None):
    """
    Get embedded styles in a html tree that contains the given string.
    >>> len(get_embedded_styles(get_html_tree('https://www.apple.com/retail/fifthavenue/'), 'image-hero'))
    1
    """
    xpath_style = '//style' + ('[contains(.,"' + containing + '")]' if containing else '') + '/text()'
    return tree.xpath(xpath_style)


def get_html_stylesheets(tree, containing=None) -> List[str]:
    """
    Get the store.built.css or store.css that is linked in the given html tree
    >>> len(get_html_stylesheets(get_html_tree('https://www.apple.com/hk/en/retail/ifcmall/')))
    3
    >>> len(get_html_stylesheets(get_html_tree('https://www.apple.com/hk/en/retail/ifcmall/'), 'image-retail-store-galleries-ifcmall-ifcmall-gallery-image2'))
    1
    """
    stylesheets = tree.xpath(XPATH_STYLESHEET)
    if containing:
        output = []
        for sheet in stylesheets:
            style = requests.get(APPLE_COM + sheet).content.decode()
            if style.find(containing) > -1:
                output.append(style)
        return output
    else:
        return [requests.get(APPLE_COM + sheet).content.decode() for sheet in stylesheets]

def collect_related_css_stylesheets(tree, keywords) -> List[str]:
    stylesheets = get_embedded_styles(tree) + get_html_stylesheets(tree)
    output = []
    for sheet in stylesheets:
        for keyword in keywords:
            if sheet.find(keyword) > -1:
                output.append(sheet)
                break
    return output

def get_css_rules(stylesheets):
    return [rule for stylesheet in stylesheets for rule in tinycss2.parse_stylesheet(stylesheet)]

def find_urls_in_css_rules(name, css_rules):
    """
    Find the url of the given image name in the given style.
    >>> stylesheet = get_embedded_styles(get_html_tree('https://www.apple.com/retail/fifthavenue/'), 'image-hero')[0]
    >>> css_rules = tinycss2.parse_stylesheet(stylesheet, skip_comments=True, skip_whitespace=True)
    >>> find_urls_in_css_rules('image-hero', css_rules)[1]
    'https://www.apple.com/retail/fifthavenue/images/hero_large_2x.jpg'
    """
    urls = []
    for rule in css_rules:
        if rule.type == 'qualified-rule':
            url = _get_url_if_contains_token_name(name, rule)
            urls.append(_format_url(url)) if url else None
        elif rule.type == 'at-rule' and rule.at_keyword == 'media':
            nested_rules = tinycss2.parse_rule_list(rule.content, skip_whitespace=True)
            urls.extend(find_urls_in_css_rules(name, nested_rules))
    return urls


def _format_url(url):
    """
    Turn relative path into absolute path.
    """
    if url.find('://') > -1:
        return url
    else:
        return APPLE_COM + url

def _get_url_if_contains_token_name(name, rule):
    """
    Given a css qualified rule, return the url in the rule if the prelude of the rule contains the given name
    """
    return _get_url_in_components(rule.content) if _contains_token_name(name, rule.prelude) else None

def _contains_token_name(name, css_comps) -> bool:
    """
    Given a list of css component values, look for if there is any IdentToken with the given value.
    """
    for comp in css_comps:
        if comp.type == 'ident' and comp.value == name:
            return True
    return False

def _get_url_in_components(css_comps):
    for comp in css_comps:
        if comp.type == 'url':
            return comp.value
    return None

def find_all_image_urls(store):
    """
    The aggregate function that find all relevant images of an Apple Store website and locate their links in the right stylesheets.
    >>> len(find_all_image_urls('https://www.apple.com/retail/fifthavenue/'))
    7
    >>> len(find_all_image_urls('https://www.apple.com/it/retail/piazzaliberty/'))
    10
    """
    tree = get_html_tree(store)
    image_names = get_main_images(tree)
    image_names.extend(get_additional_images(tree))
    stylesheets = collect_related_css_stylesheets(tree, image_names)
    css_rules = get_css_rules(stylesheets)
    logging.info("Finding " + str(len(image_names)) + " image(s) in " + str(len(stylesheets)) + " stylesheets for " + store)
    output = []
    for name in image_names:
        urls = find_urls_in_css_rules(name, css_rules)
        large_urls = list(filter(lambda l: l.find('large_2x') > -1, urls))
        if len(large_urls) > 0:
            output.append(large_urls[0])
        elif len(urls) > 0:
            output.append(urls[0])
        else:
            logging.critical(name + " not found.")
    return output

def get_cn_hidden_images():
    """
    Eastern eggs in the following stylesheet.
    """
    cn_stylesheet = 'https://www.apple.com.cn/cn/retail/store/styles/store.built.css'
    content = requests.get(cn_stylesheet).content.decode()
    items = re.findall('https(.*)retail/store/images/(.*)large_2x.jpg', content)
    items = ['https' + item[0] + 'retail/store/images/' + item[1] + 'large_2x.jpg' for item in items]
    return items

def save_image(link, name):
    """
    Save the linked image as the given name
    :param link: link of a image
    :param name: the save-as name
    """
    urllib.request.urlretrieve(link, name)

if __name__ == '__main__':
    # get a data frame of apple stores
    df_stores = get_store_list()
    df_stores.to_csv('../output/apple_store_list.csv')

    # get a data frame of images
    all_images = []
    for index, row in df_stores.iterrows():
        region = row['Region']
        website_link = row['Link']
        image_links = find_all_image_urls(website_link)
        counter = 1
        for link in image_links:
            all_images.append([region, index, counter, link])
            counter += 1
    df_images = pd.DataFrame(data=all_images, columns=['Region', 'Store Name', '#', 'Link'])
    df_images.sort_values(by=['Region', 'Store Name'], inplace=True)
    df_images.to_csv(path_or_buf='../output/all_images.csv', index=False)
