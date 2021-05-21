from pymongo import MongoClient
import json
from datetime import date


# Question/Answer action-Vote. The user should be able to vote on the selected question 
# or answer if not voted already on the same post (this constraint is only applicable 
# to users with a user id; anonymous users can vote with no constraint). The vote should 
# be recorded in Votes with a unique vote id assigned by your system, the post id set to the 
# question/answer id, vote type id set to 2, and the creation date set to the current date. 
# If the current user is not anonymous, the user id is set to the current user. 
# With each vote, the score field in Posts will also increase by one.

def post_vote(postID, userID):
    client = MongoClient()
    mydb = client["291db"]
    mycol = mydb["Votes"]

    temp = mydb.Votes.find({"UserID" : userID, "PostId" : postID }, {"UserID" : 1, "_id" :0})

    if( [row["UserID"] for row in temp] == [] ):

        x = mydb.Votes.find({}, {"Id":1, "_id":0}).sort("_id", -1).limit(1)
        newId = int([row["Id"] for row in x][0]) + 1

        # Getting current date
        today = date.today().strftime("%d/%m/%Y")

        # Getting the number of votes and then adding one and updating it
        x = mydb.Posts.find({"Id" : postID }, {"Score" : 1, "_id" :0})
        newVote = int([row["Score"] for row in x][0]) + 1
        mydb.Posts.update_one({"Id":"1"}, {"$set":{"Score":newVote}})

        Vote = {
            "Id": newId,
            "PostId": postID,
            "VoteTypeId": "2",
            "CreationDate": today,
            "UserID": userID
            }

        rec_id1 = mycol.insert_one(Vote)
    else:
        print("You already voted on this post")

if __name__ == "__main__":
    post_vote("2","3")