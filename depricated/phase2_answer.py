from pymongo import MongoClient
import json
from datetime import date


def post_answer(postID, userID):
    client = MongoClient()
    mydb = client["291db"]
    mycol = mydb["Posts"]


    body = input("Enter your answer: ")
   

    # MAKING ID SUCH THAT IT IS UNIQUE
    x = mydb.Posts.find({}, {"Id":1, "_id":0}).sort("_id", -1).limit(1)
    newId = int([row["Id"] for row in x][0]) + 1

    # Getting current date
    today = date.today().strftime("%d/%m/%Y")

    Answer = {
        "Id": newId,
        "PostTypeId": "2",
        "ParentId": postID,
        "CreationDate": today,
        "Score": 0,
        "Body":  body,
        "OwnerUserId": userID,
        "LastActivityDate": today,
        "CommentCount": 0,
        "ContentLicense": "CC BY-SA 2.5"
      }

    rec_id1 = mycol.insert_one(Answer)


if __name__ == "__main__":
    post_answer("500000","500000")