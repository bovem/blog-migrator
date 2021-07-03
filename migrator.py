import os
from pathlib import Path
import time
import shutil
import json

with open('config.json', 'r') as f:
    config = json.load(f)

note_files = list(set(os.listdir(config['blog_src'])) - set(config['blog_src_exclude']))
category_post_map = {} 

for cat in note_files:
    file_list = []
    for f in os.listdir("{}{}/".format(config['blog_src'], cat)):
        #file_list.append(f)
        shutil.copy2("{}{}/{}".format(config['blog_src'],cat, f), "old-files/")
        category_post_map[f] = cat

old_names = sorted(Path("old-files").iterdir(), key=os.path.getmtime)
files = os.listdir("old-files/")
file_time_list = [os.path.getmtime("old-files/{}".format(file)) for file in files]
file_time_list = list(map(time.gmtime, file_time_list))
file_time_list_formatted = ["{}-{:02d}-{:02d}".format(ftime.tm_year, 
                         ftime.tm_mon, ftime.tm_mday) for ftime in file_time_list]
file_date_map = dict(zip(files, file_time_list_formatted))

old_names = [str(o).replace('old-files/', '') for o in old_names]
new_names = [o.lower().replace(' ', '-') for o in old_names]

for i in range(len(old_names)):
    new_names[i] = file_date_map[old_names[i]]+"-"+new_names[i]

wikilinks = ["[[{}]]".format(link.replace('.md', '')) for link in old_names]
markdown_links = ["[{}]".format(old_names[i].replace('/', '').replace('.md', '')) + 
                  "({% post_url " + "{}".format(new_names[i].replace(".md", '')) + 
                  " %})" for i in range(len(wikilinks))]
link_map = dict(zip(wikilinks, markdown_links))

def replace_link(blog_content_list):
    new_content = []
    for line in blog_content_list:
        for wiki in wikilinks:
            line = line.replace(wiki, link_map[wiki])
            if "$" in line:
                line = line + "\n"
        new_content.append(line)
    return new_content

def remove_tags(blog_content_list):
    new_content = []
    for line in blog_content_list:
        if "Tags: " in line:
            continue
        else:
            new_content.append(line)
    return new_content

def description_cleaner(desc):
    for k, v in link_map.items():
        desc = desc.replace(v, k.replace('[[', '').replace(']]', ''))
    
    for sym in ["**", "[[", "]]", "*", "\n"]:
        if ((sym=="*") & ("*$" in desc)):
            continue
        else:
             desc = desc.replace(sym, '')

    for sym2 in [".png", ":", "-", "`"]:
        if sym2 in desc:
            desc = " "

    return desc

def replace_image_links(blog_content_list):
    new_content = []
    for line in blog_content_list:
        if  "![[" in line:
            line = line.replace("![[", "<img src=\"../assets/images/posts/").replace("]]", "\"/>")
            #print("Replaced image link")
        new_content.append(line)
    return new_content
        
def clean_orphan_links(blog_content_list):
    new_content = []
    for line in blog_content_list:
        if "[[" in line:
            line = line.replace("[[","<b>").replace("]]", "</b>")
        new_content.append(line)
    return new_content

front_matter = """---\nlayout: article\nmathjax: true\ntitle: {}\nimage: "/assets/images/{}"\ncategories:\n- {}\ndesc: {} \nimagealt: {}\n---\n\n"""
desc = "\'\'"
imagealt = "Cover Image for article"

for n2 in os.listdir("new-files"):
    os.remove("new-files/{}".format(n2))


for o, n in zip(old_names, new_names):
    with open("old-files/{}".format(o), "r") as f:
        title = o.replace('.md', '')
        print()
        print()
        print(title)
        category = category_post_map[o]
        image = "covers/{}".format(config['category_image_map'][0][category])
        lines = replace_link(f.readlines())

        if lines == []:
            description  = ''
        else:
            description = description_cleaner(lines[0])

        content = [front_matter.format(title, image, category, description, imagealt)]+\
                    clean_orphan_links(replace_image_links(remove_tags(lines))) +\
                ["\n\nThis blog was published directly from my notes.\nTo check the source of my notes and images used in this blog, visit <a href=\"/credits.html\" target=\"_blank\">Credits</a>."+\
                    "\n\nTo read my notes, download this <a href=\"https://github.com/bovem/CS\" target=\"blank\">repository</a>."]
        
    with open("new-files/{}".format(n), "w+") as f:
        f.write("".join(content)) 
    
    destination_link = config["blog_dest"]
    shutil.copy2("new-files/{}".format(n), "{}{}".format(destination_link, n))

img_destination_link = config["img_dest"]
img_source_link = config["img_src"]
for image in os.listdir(img_source_link): 
    shutil.copy2("{}{}".format(img_source_link, image), "{}{}".format(img_destination_link, image))