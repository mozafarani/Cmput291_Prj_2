from menuStack import *
from input import *
from datetime import date
from pymongo import MongoClient
from datetime import datetime
import re


# Create the state that makes a question and adds it to the stack
def setupPostingState(stack: menuStack, usr: int, db: MongoClient):
    state = makePostState(usr, db)
    stack.append(state)


# The state that has the interface to create a question
class makePostState(menuState):

    def __init__(self, usr: int, db: MongoClient):
        super(makePostState, self).__init__(usr, db)

    # This functions posts a question and is properly recorded in the database
    # It asks the user to enter a title and a body for that question
    # It also asks the user if they want to enter tags to the question
    # It then looks for a unique Post ID for the question
    # It then adds it to the database with the current date
    # It is overridden from the menuState object
    def execute(self, stack) -> terminateState:

        mycol = self.db["Posts"]

        # MAKING ID SUCH THAT IT IS UNIQUE
        x = self.db.Posts.find({}, {"Id": 1, "_id": 0}).sort("_id", -1).limit(1)
        newId = int([row["Id"] for row in x][0]) + 1

        terms, titleArr, bodyArr = [], [], [] # empty array of terms

        title = safeInput("\nPlease enter the title that you want to use for the question: ",
                          checkExpected=False,
                          checkEmpty=True)
        body = safeInput("\nEnter your question: ",
                         checkExpected=False,
                         checkEmpty=True)
        contin = safeInput("\nDo you want to Enter tags? (Y/N) ",
                           checkExpected=True,
                           expectedInputs=["Y", "N"])

        if contin.upper() == "Y":
            bo = True
        else:
            bo = False

        tag = ""
        tags = []
        while bo:
            inpu = input("Enter a tag: ")
            inpu = inpu.lower()
            Found = self.db.Tags.count_documents({ 'TagName': inpu }, limit = 1) != 0
            if inpu.lower() in tags:
                print("This post already has that tag!")
            else:
                if not Found:
                    # getting a unique tag
                    tagid = self.db.Tags.find({}, {"Id":1, "_id":0}).sort("_id", -1).limit(1)
                    tagID = int([row["Id"] for row in tagid][0]) + 1
                    tag += "<"
                    tag += inpu
                    tag += ">"
                    tags.append(inpu)
                    Tag = {
                            "Id": str(tagID),
                            "TagName": inpu,
                            "Count": 1,
                            "ExcerptPostId": str(newId),
                        }

                    record = self.db.Tags.insert_one(Tag)
                    print("Tag is inserted !")
                else:
                    tag += "<"
                    tag += inpu
                    tag += ">"
                    tags.append(inpu)
                    tag_count = self.db.Tags.find({"TagName" : inpu}, {"Count":1, "_id":0})
                    newcount = int([row["Count"] for row in tag_count][0]) + 1

                    self.db.Tags.update_many({"TagName":inpu},{"$set":{"Count": newcount}})
                    print("Tag count is updated !")

            contin = safeInput("Do you want to enter one more tag? (Y/N)",
                               checkExpected=True,
                               expectedInputs=["Y", "N"])
            if contin.upper() == "N":
                break

        # Getting current date
        today = date.today().strftime("%d/%m/%Y")

        if (title != ""): #
            titleArr = [w.lower() for w in re.findall("[a-zA-Z0-9]{3,}", title)]

        if (body != ""):
            bodyArr = [w.lower() for w in re.findall("[a-zA-Z0-9]{3,}", body)]
        
        bodyArr.extend(titleArr)
        terms = list(set(bodyArr))
        
        # added for the no tag case
        if (tag == "" and self.user != None): # case when uid is given but no tag
            Post = {
                "Id": str(newId),
                "PostTypeId": "1",
                "CreationDate": today,
                "Score": 0,
                "ViewCount": 0,
                "Body": body,
                "OwnerUserId": str(self.user),
                "LastEditorUserId": "",
                "LastEditDate": today,
                "LastActivityDate": today,
                "Title": title,
                "AnswerCount": 0,
                "CommentCount": 0,
                "FavoriteCount": 0,
                "ContentLicense": "CC BY-SA 2.5",
                "Terms": terms
            }
        elif (tag != "" and self.user == None): # case when tag is given but no user id
            Post = {
            "Id": str(newId),
            "PostTypeId": "1",
            "CreationDate": today,
            "Score": 0,
            "ViewCount": 0,
            "Body": body,
            "LastEditorUserId": "",
            "LastEditDate": today,
            "LastActivityDate": today,
            "Title": title,
            "Tags": tag,
            "AnswerCount": 0,
            "CommentCount": 0,
            "FavoriteCount": 0,
            "ContentLicense": "CC BY-SA 2.5",
            "Terms" : terms
            }
        elif (tag == "" and self.user == None): # case when no tag and no user id
            Post = {
            "Id": str(newId),
            "PostTypeId": "1",
            "CreationDate": today,
            "Score": 0,
            "ViewCount": 0,
            "Body": body,
            "LastEditorUserId": "",
            "LastEditDate": today,
            "LastActivityDate": today,
            "Title": title,
            "AnswerCount": 0,
            "CommentCount": 0,
            "FavoriteCount": 0,
            "ContentLicense": "CC BY-SA 2.5",
            "Terms" : terms
            }
        else: # tag and user id is given
            Post = {
                "Id": str(newId),
                "PostTypeId": "1",
                "CreationDate": today,
                "Score": 0,
                "ViewCount": 0,
                "Body": body,
                "OwnerUserId": str(self.user),
                "LastEditorUserId": "",
                "LastEditDate": today,
                "LastActivityDate": today,
                "Title": title,
                "Tags": tag,
                "AnswerCount": 0,
                "CommentCount": 0,
                "FavoriteCount": 0,
                "ContentLicense": "CC BY-SA 2.5",
                "Terms" : terms
            }

        rec_id1 = mycol.insert_one(Post)

        print("\nQuestion posted!")

        stack.pop()
        return terminateState.cont
