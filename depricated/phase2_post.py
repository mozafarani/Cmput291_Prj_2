from pymongo import MongoClient
import json
from datetime import date


def post_question(userID):
    client = MongoClient()
    mydb = client["291db"]
    mycol = mydb["Posts"]

    title = input("Enter the tile: ")
    body = input("Enter the body: ")
    contin = input("Do you want to Enter tags? (Y/N)")
    if (contin == "Y"):
        bo = True
    else:
        bo = False
    
    tag = ""

    while(bo):
        inpu = input("Enter a tag: ")
        tag += "<"
        tag += inpu
        tag += ">"
        contin = input("Do you want to enter one more tag? (Y/N)")
        if(contin == "N"):
            break
   
    # MAKING ID SUCH THAT IT IS UNIQUE
    x = mydb.Posts.find({}, {"Id":1, "_id":0}).sort("_id", -1).limit(1).skip(1)
    if(x[0] == {}):
        x = mydb.Posts.find({}, {"Id":1, "_id":0}).sort("_id", -1).limit(1)
    newId = int([row["Id"] for row in x][0]) + 1

    # Getting current date
    today = date.today().strftime("%d/%m/%Y")
    
    
    Post = {
        "Id": newId,
        "PostTypeId": "1",
        "CreationDate": today,
        "Score": 0,
        "ViewCount": 0,
        "Body": body,
        "OwnerUserId": userID,
        "LastEditorUserId": "",
        "LastEditDate": today,
        "LastActivityDate": today,
        "Title": title,
        "Tags": tag,
        "AnswerCount": 0,
        "CommentCount": 0,
        "FavoriteCount": 0,
        "ContentLicense": "CC BY-SA 2.5"
      }

    rec_id1 = mycol.insert_one(Post)

if __name__ == "__main__":
    post_question("500000")