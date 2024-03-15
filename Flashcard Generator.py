import os
import random

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

# ANSI escape codes for formatting
BOLD = "\033[1m"
RESET = "\033[0m"
YELLOW = "\033[93m"

# Read from the text file
with open("questionnaire.txt", "r") as file:
    lines = file.readlines()

clrScr()
questionArr = []
answerArr = []
question = ""
answer = ""
for line in lines:
    line = line.strip()
    if line.startswith('>'):
        if question:  # If we have a previous question, add it
            questionArr.append(question)
            question = ""
        question += line[1:]  # Append the question without '>'
    elif line.startswith('['):
        answer += line[1:-1]  # Append the answer without '[' and ']'
        answerArr.append(answer.lower())  # Add the answer to the answer array
        answer = ""  # Reset the answer for the next question
if question:  # If there's a pending question at the end
    questionArr.append(question)

# Flush file buffer
file.close()

# Shuffle the questions and answers
indexes = list(range(len(questionArr)))
random.shuffle(indexes)

questionSize = len(questionArr)
for i in range(questionSize):
    randIndex = indexes[i]
    print(f"{BOLD}{i + 1}/{questionSize}) {questionArr[randIndex]}{RESET}")
    input_answer = input("Answer: ").lower()
    print()
    if answerArr[randIndex] == input_answer:
        print(f"{YELLOW}Your answer is correct!{RESET}")
    else:
        print(f"Eto... the correct answer is: {YELLOW}{answerArr[randIndex]}{RESET}")
    print()
