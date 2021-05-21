from menuStack import *
from input import *
from datetime import date

from pymongo import MongoClient
import re


# a method to initialize the state for displaying searched posts and to add it to the state stack
def setupDisplayPostsState(stack: menuStack, usr: int, db: MongoClient, posts, isQ: bool, acc: bool = False):
    state = displayPostsState(usr, db, posts, isQ, acc)
    stack.append(state)


# a menu state that displays searched posts
class displayPostsState(menuState):

    def __init__(self, usr: int, db: MongoClient, posts, isQ, acc):
        super(displayPostsState, self).__init__(usr, db)
        self.posts = posts
        self.isQ = isQ
        self.acc = acc

    # This function overrides the execute function of the menuState object
    def execute(self, stack) -> terminateState:
        # check if the search results are empty
        if len(self.posts) == 0:
            prompt = "\nNo matches found!\n" \
                     "B: Back to your search\n" \
                     "M: Main Menu\n"
            userChoice = safeInput(prompt,
                                   checkExpected=True,
                                   expectedInputs=["B", "M"]).upper()
            if userChoice == "B":
                stack.pop()
            elif userChoice == "M":
                stack.clear()
            # terminate if no results
            return terminateState.cont
        if self.isQ:
            prompt = "Title | Date of Creation | Score | Number of Answers\n"
        else:
            prompt = "Answer | Date of Creation | Score\n"
        count = 0
        expected = []
        for post in self.posts:
            if self.isQ:
                # if a question, post the relevant fields
                prompt = prompt + str(count) + ": " + post["Title"] + "|" + post["CreationDate"] + "|" + str(
                    post["Score"]) + "|" + str(post["AnswerCount"]) + "\n"
            else:
                # if answer:
                if count == 0 and self.acc:
                    prompt = prompt + "*"
                prompt = prompt + str(count) + ": " + post["Body"][:81] + "|" + post["CreationDate"] + "|" + str(
                    post["Score"]) + "\n"
            # add the post index to acceptable user inputs
            expected.append(str(count))
            count += 1

        expected.append("B")
        expected.append("M")
        prompt = prompt + "B: Back to search\nM: Back to menu\n"

        userChoice = safeInput(prompt,
                               checkExpected=True,
                               expectedInputs=expected).upper()

        # handle the user options
        if userChoice == "B":  # pop self off of stack
            stack.pop()
            return terminateState.cont
        elif userChoice == "M":  # exit with terminateState.menu
            return terminateState.menu
        elif int(userChoice) < len(self.posts):  # go to post actions
            # increment views
            if self.isQ:
                pastViews = self.db.Posts.find({"Id": self.posts[int(userChoice)]["Id"]}, {"ViewCount": 1, "_id": 0})
                newViews = int([row["ViewCount"] for row in pastViews][0]) + 1
                self.db.Posts.update({"Id": self.posts[int(userChoice)]["Id"]}, {"$set": {"ViewCount": newViews}})
                print("The question with the title --> (" + self.posts[int(userChoice)]["Title"] + ") has been selected! \n")
            else:
                print("Answer " + userChoice + " was selected! ")

            setupPostActionState(stack, self.user, self.db, self.posts[int(userChoice)])
            return terminateState.cont


# This function is created to find whether the post is a question or an answer
# It searchs for the post in the questions database and if it found then it is a question
# If not then the post is an answer
def setupPostActionState(stack: menuStack, usr: int, db: MongoClient, post):
    # check if question
    if post["PostTypeId"] == "1":  # is a question
        state = questionActionState(usr, db, post)
    else:
        state = postActionState(usr, db, post)
    stack.append(state)


# This object is a menu state that contains the interface to do post actions
class postActionState(menuState):

    def __init__(self, usr: int, db: MongoClient, post):
        super(postActionState, self).__init__(usr, db)
        self.post = post
        self.actionLookUpTable = {}
        self.index = 0
        self.choice = ""
        # add actions to the look up table of actions
        self.addAction("back to search results")
        self.addAction("back to main menu")
        self.addAction("vote")

    def addAction(self, actionName):
        self.actionLookUpTable[str(self.index)] = actionName
        self.index += 1

    def actionEndPrompt(self, stack):
        self.actionLookUpTable = {}
        self.addAction("back to menu")
        self.addAction("exit")

        # the prompt that will be shown to the user
        prompt = ""
        # the list of expected user inputs
        expected = []
        # Build the prompt and expected inputs from action look up table
        for key, action in sorted(self.actionLookUpTable.items()):
            prompt = prompt + key + ": " + action + "\n"
            expected.append(key)

        # Take input from the user
        self.choice = safeInput(prompt,
                                checkExpected=True,
                                expectedInputs=expected).lower()

        # Handle user input
        if self.actionLookUpTable.get(self.choice) == "back to menu":
            stack.clear()
            return terminateState.cont
        elif self.actionLookUpTable.get(self.choice) == "exit":
            print("exiting program")
            return terminateState.exit

    def execute(self, stack) -> terminateState:
        for key, value in self.post.items():
            print(key+": "+str(value))
        # the prompt that will be shown to the user
        prompt = ""
        # the list of expected user inputs
        expected = []
        # Build the prompt and expected inputs from action look up table
        for key, action in sorted(self.actionLookUpTable.items()):
            prompt = prompt + key + ": " + action + "\n"
            expected.append(key)

        # Take input from the user
        self.choice = safeInput(prompt,
                                checkExpected=True,
                                expectedInputs=expected).lower()

        # Handle user input
        if self.actionLookUpTable.get(self.choice) == "vote":
            return self.__vote(stack)
        elif self.actionLookUpTable.get(self.choice) == "back to search results":
            stack.pop()
            return terminateState.cont
        elif self.actionLookUpTable.get(self.choice) == "back to main menu":
            print("menu")
            return terminateState.menu

    # This function makes the user able to vote on the selected post
    # It finds if the user already voted on the post or not
    # If not it increases the vote count by one and adds the user uid to that vote.
    # If the post has no votes, It creates a new vote entity where the vote number is = 1
    def __vote(self, stack):

        mycol = self.db["Votes"]

        if self.user:
            temp = self.db.Votes.find({"UserId": str(self.user), "PostId": str(self.post["Id"])},
                                      {"UserId": 1, "_id": 0})

        if self.user is None or temp.count() == 0:

            x = self.db.Votes.find({}, {"Id": 1, "_id": 0}).sort("_id", -1).limit(1)
            newId = int([row["Id"] for row in x][0]) + 1

            # Getting current date
            today = date.today().strftime("%d/%m/%Y")

            # Getting the number of votes and then adding one and updating it
            x = self.db.Posts.find({"Id": self.post["Id"]}, {"Score": 1, "_id": 0})
            newVote = int([row["Score"] for row in x][0]) + 1
            self.db.Posts.update_one({"Id": self.post["Id"]}, {"$set": {"Score": newVote}})

            # added for users with no user id
            if (self.user is None):
                Vote = {
                    "Id": str(newId),
                    "PostId": self.post["Id"],
                    "VoteTypeId": "2",
                    "CreationDate": today
                }
            else:
                Vote = {
                    "Id": str(newId),
                    "PostId": self.post["Id"],
                    "VoteTypeId": "2",
                    "CreationDate": today,
                    "UserId": str(self.user)
                }

            rec_id1 = mycol.insert_one(Vote)
            print("Vote recorded")
        else:
            print("You already voted on this post")

        return self.actionEndPrompt(stack)


class questionActionState(postActionState):

    def __init__(self, usr: int, db: MongoClient, post):
        super(questionActionState, self).__init__(usr, db, post)
        # Add the option to answer the question to the look up table
        self.addAction("answer")
        self.addAction("see answers")

    def execute(self, stack) -> terminateState:
        output = super(questionActionState, self).execute(stack)
        if output:
            return output

        # handle the question specific user actions
        if self.actionLookUpTable.get(self.choice) == "answer":
            return self.__answer(stack)
        elif self.actionLookUpTable.get(self.choice) == "see answers":
            return self.__displayAnswers(stack)

    # This function adds an answer to a particular question
    # It does that by asking the user to enter the title and body of the answer
    # Then it finds a unique answer id for the post
    # It then inserts the post as a post entity and as an answer entity
    def __answer(self, stack):

        terms = []

        body = safeInput("Enter your answer: ",
                         checkExpected=False,
                         checkEmpty=True)

        mycol = self.db["Posts"]

        # MAKING ID SUCH THAT IT IS UNIQUE
        x = self.db.Posts.find({}, {"Id": 1, "_id": 0}).sort("_id", -1).limit(1)
        newId = int([row["Id"] for row in x][0]) + 1

        # Getting current date
        today = date.today().strftime("%d/%m/%Y")

        bodyArr = [w.lower() for w in re.findall("[a-zA-Z0-9]{3,}", body)]

        terms = list(set(bodyArr))

        if (self.user != None): # case when user id is given and user wants to answer
            Answer = {
                "Id": str(newId),
                "PostTypeId": "2",
                "ParentId": self.post["Id"],
                "CreationDate": today,
                "Score": 0,
                "Body": body,
                "OwnerUserId": str(self.user),
                "LastActivityDate": today,
                "CommentCount": 0,
                "ContentLicense": "CC BY-SA 2.5",
                "Terms" : terms
            }
        else: # case when no user id is given
            Answer = {
                "Id": str(newId),
                "PostTypeId": "2",
                "ParentId": self.post["Id"],
                "CreationDate": today,
                "Score": 0,
                "Body": body,
                "LastActivityDate": today,
                "CommentCount": 0,
                "ContentLicense": "CC BY-SA 2.5",
                "Terms" : terms
            }

        rec_id1 = mycol.insert_one(Answer)

        pastAnsCount = self.db.Posts.find({"Id": self.post["Id"]}, {"AnswerCount": 1, "_id": 0})
        newAnsCount = int([row["AnswerCount"] for row in pastAnsCount][0]) + 1
        self.db.Posts.update({"Id": self.post["Id"]}, {"$set": {"AnswerCount": newAnsCount}})

        print("Answer recorded")

        return self.actionEndPrompt(stack)

    def __displayAnswers(self, stack):
        results = []
        acceptedId = ""
        acc = True

        # try to get an accepted answer
        try:
            accepted = self.db.Posts.find({"Id": self.post["AcceptedAnswerId"]})
        except KeyError:
            accepted = []
            acc = False

        for answer in accepted:
            results.append(answer)
            acceptedId = answer["Id"]

        # find answers
        answers = self.db.Posts.find({"$and": [{"ParentId": self.post["Id"]}, {"Id": {"$ne": acceptedId}}]})
        for answer in answers:
            results.append(answer)

        setupDisplayPostsState(stack, self.user, self.db, results, False, acc)
        return terminateState.cont
