import os
from app import db, DB_FILE
from models import *
import requests
import json
from bs4 import BeautifulSoup
import uuid

def create_user():
    josh = User(id="josh", email='josh@gmail.com', password = None)
    bill = User(id="bill", email='bill@gmail.com', password = None)
    db.session.add(josh)
    db.session.add(bill)
    db.session.commit()

# This method scrapes the club site and loads the clubs into the database
def scrape_load_data():
    input = requests.get("https://ocwp.pennlabs.org/")
    src = input.content
    soup = BeautifulSoup(src, 'lxml')
    # Names, descripts, and tags are raw html
    names = soup.find_all('strong')
    descrips = soup.find_all('em')
    # the tags start at index 3
    tags = soup.find_all('span')
    names_text = []
    descrips_text = []
    tags_text = []
    #Now we will extract text from html
    for n in names:
        names_text.append(n.get_text())
    for d in descrips:
        descrips_text.append(d.get_text())
    for i in range(3, len(tags)):
        tags_text.append(tags[i].get_text())
    existing_tags = {}
    # since each club only has one tag, there is no need to keep a list as in load_data()
    for i in range(0, len(names_text)):
        if tags_text[i] not in existing_tags:
            existing_tags[tags_text[i]] = Tag(id=tags_text[i])
        db.session.add(Club(id=str(uuid.uuid4()), name=names_text[i], description=descrips_text[i], 
            tags=[existing_tags[tags_text[i]]], users=[], comments=[]))
    db.session.commit()

def load_data():
    f = open('clubs.json')
    data = json.load(f)
    tagObjs = {}
    # only create a new tag if it has not been discovered yet
    for i in data:
        # this list keeps track of tag objects for a specific club
        clubTags = []
        for j in i['tags']:
            if j not in tagObjs:
                tagObjs[j] = Tag(id=j)
            clubTags.append(tagObjs[j])
        db.session.add(Club(id=i['code'], name=i['name'], description=i['description'], tags=clubTags, users=[]))
    f.close()
    db.session.commit()



# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
    # This method calls the webscraper method
    scrape_load_data()
