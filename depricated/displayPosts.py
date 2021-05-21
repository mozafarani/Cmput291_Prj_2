from menuStack import *
from input import *
from postActions import *

from pymongo import MongoClient


# a method to initialize the state for displaying searched posts and to add it to the state stack
def setupDisplayPostsState(stack: menuStack, usr: int, db: MongoClient, posts, isQ: bool):
    state = displayPostsState(usr, db, posts, isQ)
    stack.append(state)


# a menu state that displays searched posts
class displayPostsState(menuState):

    def __init__(self, usr: int, db: MongoClient, posts, isQ):
        super(displayPostsState, self).__init__(usr, db)
        self.posts = posts
        self.isQ = isQ

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
            prompt = "Answer | Date of Creation | Score"
        count = 0
        expected = []
        for post in self.posts:
            if self.isQ:
                prompt = prompt+str(count)+": "+post["Title"]+"|"+post["CreationDate"]+"|"+str(post["Score"])+"|"+str(post["AnswerCount"])+"\n"
            else:
                prompt = prompt+str(count)+": "+post["Body"][:81]+"|"+post["CreationDate"]+"|"+str(post["Score"])+"\n"
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
            setupPostActionState(stack, self.user, self.db, self.posts[int(userChoice)])
            return terminateState.cont
