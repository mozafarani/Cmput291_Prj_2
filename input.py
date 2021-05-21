# This function checks if the user input is correct or not
# It does that by looping until the user enters a correct input
def safeInput(prompt: str,
              checkExpected: bool = True, expectedInputs=[], caseSens: bool = False,
              checkType: bool = False, expectedType: type = str,
              checkLength: bool = False, expectedLength: int = 0,
              checkEmpty: bool = False):
    if checkExpected and expectedInputs == []:
        raise Exception("no expected inputs given")

    while True:
        answer = input(prompt)
        # if type is to be checked
        if checkType:
            try:
                if expectedType == int:
                    answer = int(answer)
                elif expectedType == float:
                    answer = float(answer)
            except:
                print("Answer not of expected type...\n")
                continue
        # if a list of acceptable inputs is provided
        if checkExpected:
            if (not caseSens and answer.lower() not in expectedInputs) \
               and (not caseSens and answer.upper() not in expectedInputs) \
               or (caseSens and answer not in expectedInputs):
                print("Input does not match one of the expected inputs...\n")
                continue

        # if the input is to be checked for a blank input
        if checkEmpty:
            if answer == "":
                print("Cannot enter empty entry...\n")
                continue

        if checkLength:
            if len(answer) != expectedLength:
                print("Answer not expected length of "+str(expectedLength)+"\n")
                continue

        return answer
