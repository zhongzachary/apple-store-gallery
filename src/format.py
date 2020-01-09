
"""
The file are used to create a markdown file containing images in out/all_images.csv.
"""

from main import *

df_images = pd.read_csv('../output/all_images.csv')



md = open('../output/gallery.md', 'w')
md.write("# Apple Stores Around the World\n")

region = ''
store = ''
counter = 1
for index, row in df_images.iterrows():
    if not row['Region'] == region:
        region = row['Region']
        md.write('## ' + region + '\n')
    if not row['Store Name'] == store:
        store = row['Store Name']
        md.write('**' + store + "**\n")
        counter = 1
    md.write('<img src="' + row['Link'] + '"/>\n')
    counter += 1

md.close()
