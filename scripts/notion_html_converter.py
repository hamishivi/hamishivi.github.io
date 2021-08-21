'''
A very loose script for converting a notion markdown export into a format that matches
the format my posts use. This isn't fully featured or anything that great - its literally
just a scrappy script for roughly doing what I want.
'''
import argparse
import re
import os
import glob
from pathlib import Path
from datetime import datetime
from imgur_uploader import upload_to_imgur

parser = argparse.ArgumentParser(description='Convert notion markdown to hamish markdown')
parser.add_argument('filename')
parser.add_argument('title')
args = parser.parse_args()

# read in
with open(args.filename) as file:
  lines = file.readlines()
path = Path(args.filename)

# full title is first line
fulltitle = lines[0][2:]
lines.pop(0)

# make dir for stuff
try:
    os.mkdir(f'public/post_images/{args.title}')
except FileExistsError: # okay for folder to exist, just wipe it.
    print('err')
    files = glob.glob(f'public/post_images/{args.title}/*')
    for f in files:
        os.remove(f)

# add title
title = f'''---
layout: post
title: {fulltitle}
excerpt_separator: <!--more-->
usemathjax: true
---'''.split('\n')
title = [t for t in title if t] # filter out empty string
lines = title + lines

# next, replace images. This is gonna require a bit of manual
# work: sometimes I want images side by side...
output = []
image_pat = re.compile(r'\!\[(.*)\]\(.*\)')
for line in lines:
    match = image_pat.search(line)
    if match := image_pat.search(line):
        image_path = match.group(1).replace('%20', ' ')
        print(f'Generating figure for: {image_path}')
        image_filename = image_path.split('/')[-1]
        print('Please enter caption: ', end='')
        caption = input()
        imgur_url = upload_to_imgur(image_path, image_filename)
        image_html = f'''<figure>
<img src="{imgur_url}" style="margin: 0 auto; width: 100%"/>

<figcaption>{caption}</figcaption>
</figure>'''
        # move image
        output += image_html.split('\n')
    else:
        output.append(line)

# finally, print everything to the post folder
with open(f'_posts/{datetime.today().strftime("%Y-%m-%d")}-{args.title}.md', 'w') as f:
    f.writelines(f'{o}\n' for o in output)
