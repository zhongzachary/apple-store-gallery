
"""
The file are used to create a markdown file containing images in out/all_images.csv.
"""
import os

from main import *

df_images = pd.read_csv('../output/all_images.csv')

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

        md_main.write('## ' + region + '\n')

        os.makedirs(gallery_root + region, exist_ok=True)
        md_curr = open(gallery_root + region + '/README.md', 'w')
        md_curr.write('## ' + region + '\n')

    if not row['Store Name'] == store:
        store = row['Store Name']

        md_main.write('### ' + store + "\n")

        md_curr.write('## ' + store + "\n")

    md_main.write('<img src="' + str(row['Link']) + '"/>\n')
    md_curr.write('<img src="' + str(row['Link']) + '"/>\n')

md_curr.close()
md_main.close()
