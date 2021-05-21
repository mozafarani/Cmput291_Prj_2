from pymongo import MongoClient

from enum import Enum

# an enum that is used to express if the user chose to go back to main menu or not
terminateState = Enum('terminateState', 'menu cont exit')


# an class that is used to be a base class for all menu states
class menuState:
    # this is an abstract class
    def __init__(self, usr: int, db: MongoClient):
        self.user = usr
        self.db = db

    def execute(self, stack) -> terminateState:
        pass


# a stack that contains all menu states in the order they were opened.
class menuStack:

    def __init__(self):
        self.stack = []

    # This function adds to end of the stack
    def append(self, menu: menuState):
        self.stack.append(menu)

    # This function checks if the stack is Empty or not
    def isEmpty(self):
        if len(self.stack) > 0:
            return False
        return True

    # This function removes the last added thing to the stack
    def pop(self):
        self.stack.pop()

    # This function removes everything that is found in the stack
    def clear(self):
        self.stack = []

    def execute(self) -> terminateState:
        status = self.stack[-1].execute(self)

        return status

