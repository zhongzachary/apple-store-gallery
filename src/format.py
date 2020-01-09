"""
The file are used to create a markdown file containing images in out/all_images.csv.
"""
import os

import pycountry as pycountry
from main import *

df_stores = pd.read_csv('../output/apple_store_list.csv', index_col=0)
df_images = pd.read_csv('../output/all_images.csv')
df_images.sort_values(by='Region', inplace=True)


def get_store_link(store_name):
    return df_stores.at[store_name, 'Link']


def get_region_name(code: str):
    """
    >>> get_region_name('ae')
    'United Arab Emirates'
    >>> get_region_name('uk')
    'UK'
    >>> get_region_name('hk')
    'Hong Kong'
    >>> get_region_name('us')
    'United States'
    """
    try:
        return pycountry.countries.get(alpha_2=code.upper()).name
    except AttributeError:
        return code.upper()


gallery_root = '../output/gallery/'

os.makedirs(gallery_root, exist_ok=True)
md_main = open(gallery_root + 'README.md', 'w')
md_main.write("# Apple Stores Around the World\n")

region = ''
store = ''
md_curr = None

for index, row in df_images.iterrows():
    if not row['Region'] == region:
        region = row['Region']

        md_curr.close() if md_curr else None
        os.makedirs(gallery_root + region, exist_ok=True)
        md_curr = open(gallery_root + region + '/README.md', 'w')

        region_name = get_region_name(region)

        region_title = '# {0}\n'.format(region_name)
        md_main.write('\n#' + region_title)
        md_curr.write('\n' + region_title)

    if not row['Store Name'] == store:
        store = row['Store Name']

        store_title = '## [{0}]({1})\n'.format(store, get_store_link(store))
        md_main.write('\n#' + store_title)
        md_curr.write('\n' + store_title)

    image_link = '<img src="{0}"/>\n'.format(row['Link'])
    md_main.write(image_link)
    md_curr.write(image_link)

md_curr.close()
md_main.close()
