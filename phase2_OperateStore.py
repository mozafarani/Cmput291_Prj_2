from menuStack import *
from input import *
from makePost import *
from searchPosts import *

from pymongo import MongoClient
import sys


# perform setup on the forum object
def setup(port: int):
    return forum(MongoClient(port=port)["291db"])


# The main class of the program
class forum:

    def __init__(self, database):
        # remember to private these
        self.user = None
        self.menus = menuStack()
        self.db = database

    # Starts the program
    def start(self):
        while True:
            if not self.__login():
                return # if false, exit.

            if not self.__menu():
                return  # if false, exit. else just logout

    # This function prints the user report if the user provides a user ID on login
    def __showReport(self):
        # If a user id is provided, the user will be shown a report that includes 
        # (1) the number of questions owned and the average score for those questions,

        # count of questions
        rows = self.db.Posts.aggregate([
            {"$match" : { "PostTypeId": "1", "OwnerUserId": str(self.user) }},
            {"$count": "Score"}
        ])

        data = list(rows)
        
        if (len(data) != 0):
            for count in data:
                print("Amount of questions posted: "+str(count["Score"]))
        else:
            print("Amount of questions posted: 0")

        # average Score
        rows = self.db.Posts.aggregate([
            {"$match" : { "PostTypeId": "1", "OwnerUserId": str(self.user) }},
            {"$group":{"_id":"_id", "AverageValue" : { "$avg": "$Score" }}}    
        ])

        data = list(rows)

        if (len(data) != 0):  
            for count in data:
                print("Average question score: "+str(count["AverageValue"]))
        else:
            print("Average question score: 0")

        # (2) the number of answers owned and the average score for those answers, and 
        
        # count of answers
        rows = self.db.Posts.aggregate([
            {"$match" : { "PostTypeId": "2", "OwnerUserId": str(self.user) }},
            {"$count": "Score"}    
        ])

        data = list(rows)

        if (len(data) != 0):
            for count in data:
                print("Amount of questions posted: "+str(count["Score"]))
        else:
            print("Amount of questions posted: 0")

        # average Score
        rows = self.db.Posts.aggregate([
            {"$match" : { "PostTypeId": "2", "OwnerUserId": str(self.user) }},
            {"$group":{"_id":"_id", "AverageValue" : { "$avg": "$Score" }}}    
        ])

        data = list(rows)

        if (len(data) != 0):
            for count in data:
                print("Average answer score: "+str(count["AverageValue"]))
        else:
            print("Average answer score: 0")

        # (3) the number of votes registered for the user.
        votes = self.db.Votes.count_documents({ "UserId" : str(self.user) })

        print("Number of votes: "+str(votes))

    # This function asks the user to enter a user ID and prints a report if they do
    def __login(self):
        password = ""  # note passwords do not have to be encrypted
        userID = ""
        result = ""

        print("\nWelcome to the Forum!\n")

        result = safeInput("Would you like to enter a user ID?",
                           checkExpected=True,
                           expectedInputs=["Y", "N", "E"])

        result = result.upper()
        if result == "E":
            return False
        if result == "Y":
            result = safeInput("Enter a user ID: ",
                               checkExpected=False,
                               checkType=True,
                               expectedType=int)
            self.user = result
            self.__showReport()
            return True
        elif result == "N":
            return True

    # This function displays the main menu for the user after they log in.
    # It prints out the main menu and promts the user to enter one of the options given.
    # It then calls the function that the user chose to run.
    def __menu(self):
        forward = False
        prompt = "\nForum Menu:\n\n" \
                 "Choose one of the following options (1 - 4): \n\n" \
                 "1- Create a question\n" \
                 "2- Search for posts\n" \
                 "3- Exit the program\n"
        forwardOption = "4- Forward\n"

        while True:
            if forward:
                action = safeInput(prompt + forwardOption,
                                   checkExpected=True,
                                   expectedInputs=["1", "2", "3", "4"])
            else:
                action = safeInput(prompt,
                                   checkExpected=True,
                                   expectedInputs=["1", "2", "3"])

            if action == "1":
                # create post state
                self.menus.clear()
                setupPostingState(self.menus, self.user, self.db)
            elif action == "2":
                # search state
                self.menus.clear()
                setupSearchPostsState(self.menus, self.user, self.db)
            elif action == "3":
                return False  # False for exit

            returnCode = self.__runMenuStates()
            if returnCode:  # if True it means states were saved
                forward = True
            elif returnCode is None:
                return False
            else:
                forward = False

    def __runMenuStates(self):
        while not self.menus.isEmpty():
            returnCode = self.menus.execute()
            if returnCode == terminateState.menu:
                return True
            elif returnCode == terminateState.exit:
                return None
        return False


if __name__ == '__main__':
    portIn = sys.argv[1]
    try:
        forum = setup(int(portIn))
        forum.start()
    except TypeError as e:
        print("invalid port. That's probably the issue. Maybe something else threw a typeError idk")
        raise e
