from menuStack import *
from postActions import *
import time

from pymongo import MongoClient


# function sets up the state that searches posts and adds it to the menu stack
def setupSearchPostsState(stack: menuStack, usr: int, db: MongoClient):
    state = searchPostsState(usr, db)
    stack.append(state)


# the menu state that contains the interface to search for posts
class searchPostsState(menuState):

    def __init__(self, usr: int, db: MongoClient):
        super(searchPostsState, self).__init__(usr, db)

    def execute(self, stack) -> terminateState:
        keywords = safeInput("Please enter a space separated list of keywords: ",
                             checkExpected=False,
                             checkEmpty=True).split()

        results = []
        found = {}
        start_time = time.time()
        for keyword in keywords:
            # Search in terms
            if len(keyword) >= 3:
                output = self.db.Posts.aggregate([{"$match": {"Terms": keyword.lower()}}, {"$match": {"PostTypeId": "1"}}])

                for post in output:
                    if post["Id"] in found:
                        pass
                    else:
                        results.append(post)
                        found[post["Id"]] = None
            else:
                regex = "(^|[\s.?,:;'<])" + keyword + "([\s.?,:;'>]|$)"

                # Search in title
                output = self.db.Posts.find({"$and": [{"Title": {"$regex": regex}}, {"PostTypeId": "1"}]})
                for post in output:
                    if post["Id"] in found:
                        pass
                    else:
                        results.append(post)
                        found[post["Id"]] = None

                # Search in Body
                output = self.db.Posts.find({"$and": [{"Body": {"$regex": regex}}, {"PostTypeId": "1"}]})
                for post in output:
                    if post["Id"] in found:
                        pass
                    else:
                        results.append(post)
                        found[post["Id"]] = None

                # search in Tags
                output = self.db.Posts.find({"$and": [{"Tags": {"$regex": regex}}, {"PostTypeId": "1"}]})
                for post in output:
                    if post["Id"] in found:
                        pass
                    else:
                        results.append(post)
                        found[post["Id"]] = None

        print("--- %s seconds ---" % (time.time() - start_time))
        print("Found " + str(len(results)) + " results. Printing...")
        # search the posts and display them
        setupDisplayPostsState(stack, self.user, self.db, results, True)
        return terminateState.cont
