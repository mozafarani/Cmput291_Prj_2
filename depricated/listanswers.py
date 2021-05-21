from pymongo import MongoClient
import json
from datetime import date


# Question action-List answers. The user should be able to see all answers of a selected question. 
# If an answer is marked as the accepted answer, it must be shown as the first answer
#  and should be marked with a star. Answers have a post type id of 2 in Posts. For each answer, 
# display the first 80 characters of the body text (or the full text if it is of length 80 or less characters), 
# the creation date, and the score. The user should be able to select an answer to see all fields of the answer 
# from Posts. After an answer is selected, the user may perform an answer action (as discussed next).

def list_answer(postID):
    client = MongoClient()
    db = client["291db"]

    db.Posts.find({"PostTypeId": "2", "ParentId": postID}, {"Id":1, "_id":0})
    accepted = db.Posts.find({"Id": postID})
    check = list(db.Posts.find({"Id": postID}, {"AcceptedAnswerId":1, "Body": 1, "CreationDate": 1, "Score": 1, "_id":0}))

    if check != [{}]:
        #print the accepted first
        acceptedans = list(db.Posts.aggregate([
                                        {"$match":{"Id": "6"}},
                                        {"$project":{"Body": 1, "CreationDate": 1, "Score": 1, "_id":0
                                        ,"Body" : { "$substr": [ "$Body", 0, 80 ] }}}]))
        print("* " + str(acceptedans))
    else:
        pass

    answers = db.Posts.find({"ParentId": postID})
    for answer in answers:
        print(answer)



if __name__ == "__main__":
    list_answer("4")