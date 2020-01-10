"""
The file are used to create a markdown file containing images in out/all_images.csv.
"""
import os

import pycountry
import numpy as np
from main import *

df_images = pd.read_csv('../output/all_images.csv')
df_images = df_images.iloc[np.lexsort((df_images.index, df_images.Region.values))]

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
md_main.write('## Apple Stores in Each Region\n')

selected_stores_indices = set()
region = ''
store = ''
md_curr = None

for index, row in df_images.iterrows():
    if not row['Region'] == region:  # new region
        region = row['Region']

        md_curr.close() if md_curr else None
        os.makedirs(gallery_root + region, exist_ok=True)
        md_curr = open(gallery_root + region + '/README.md', 'w')

        region_name = get_region_name(region)

        md_main.write('\n- [{0}](./{1})\n'.format(region_name, region))
        md_curr.write('\n# {0}\n'.format(region_name))

    if not row['Store Name'] == store:
        store = row['Store Name']

        store_title = '[{0}]({1})'.format(store, row['Store Link'])
        md_curr.write('\n## {0}\n'.format(store_title))
    else:  # it is a important store
        selected_stores_indices.add(index-1)
        selected_stores_indices.add(index)
    image_link = '\n<img src="{0}"/>\n'.format(row['Link'])
    md_curr.write(image_link)

md_curr.close()

store = ''
md_main.write('\n## Selected Stores\n')
for index, row in df_images.iterrows():
    curr_store = row['Store Name']
    if index in selected_stores_indices:
        if not curr_store == store:
            store = row['Store Name']
            store_title = '[{0}]({1}), {2}'.format(store, row['Store Link'], row['Region'].upper())
            md_main.write('\n### {0}\n'.format(store_title))
        image_link = '\n<img src="{0}"/>\n'.format(row['Link'])
        md_main.write(image_link)

md_main.close()
