import sys
from pymongo import MongoClient
import json
import time
import re


# This function builds a "terms" array for each question. 
# It searches for character >=3 in Body, Title, and Tags. 
# It then adds the array to the corresponding question.
def buildTermsArray(file_data):
    
    print("Building terms")
    start_time = time.time()
    for d in file_data:
        body, title, tag = [], [], []

        if "Body" in d.keys(): # check if body field exists
            bodyString = d["Body"]
            body = [w.lower() for w in re.findall("[a-zA-Z0-9]{3,}", bodyString)]
        if "Title" in d.keys(): # check if title field exists
            titleString = d["Title"]
            title = [w.lower() for w in re.findall("[a-zA-Z0-9]{3,}", titleString)]
        if "Tags" in d.keys(): # check if tag field exists
            tagString = d["Tags"]
            tag = [w.lower() for w in re.findall("[a-zA-Z0-9]{3,}", tagString)]

        # fastest way of removing duplicates in python set oprations
        body.extend(tag)
        body.extend(title)
        body = list(set(body))

        d["Terms"] = body

    print("Building terms done")
    print("--- %s seconds ---" % (time.time() - start_time))
    return file_data

# This function inserts the json data into the database 
# with a specific port number to connect to the mongoDB sever.
# If the collections are there it drops them and then it adds
# the data into the database using insert_many().
# It reports the time spent on each part of insertion
# It then build the terms array. 

def buildCollection(port: int):
    client = MongoClient(port=port)
    dbnames = client.list_database_names()

    db = client['291db']
    
    #drop the collections
    if "Posts" in db.list_collection_names():
        db.Posts.drop()

    if "Tags" in db.list_collection_names():
        db.Tags.drop()

    if "Votes" in db.list_collection_names():
        db.Votes.drop()

    posts = db["Posts"]

    try:
        with open('Posts.json') as f:
            file_data = json.load(f)
    except:
        print("Error reading file Posts.json")

    
    dataWithTerms = buildTermsArray(file_data["posts"]["row"])
    print("inserting posts")
    start_time = time.time()
    posts.insert_many(dataWithTerms)
    print("--- %s seconds ---" % (time.time() - start_time))

    tags = db["Tags"]

    try:
        with open('Tags.json') as f:
            file_data = json.load(f)
    except:
        print("Error reading file Tags.json")

    print("inserting tags")
    start_time = time.time()
    tags.insert_many(file_data["tags"]["row"])
    print("--- %s seconds ---" % (time.time() - start_time))

    votes = db["Votes"]

    try:
        with open('Votes.json') as f:
            file_data = json.load(f)
    except:
        print("Error reading file Votes.json")

    print("inserting votes")
    start_time = time.time()
    votes.insert_many(file_data["votes"]["row"])
    print("--- %s seconds ---" % (time.time() - start_time))

    # buildTermsArray(db, posts, client)

    print("Creating index")
    start_time = time.time()
    db.Posts.create_index("Terms")
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    portIn = sys.argv[1]
    try:
        start_p_time = time.time()
        buildCollection(int(portIn))
        print("--- %s seconds ---" % (time.time() - start_p_time))
    except TypeError as e:
        print("invalid port. That's probably the issue. Maybe something else threw a typeError idk")
        raise e
