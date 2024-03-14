import os
import random

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

# Read from the text file
with open("questionnaire.txt", "r") as file:
    questionnaire = file.read()

# questionnaire = input("Enter your questionnaire: \n")
clrScr()
questionArr = []
answerArr = []
questionSymb = '>'
openAnsSymb = '['
closeAnsSymb = ']'
pos = 0
while pos < len(questionnaire) - 1:
    question = ""
    # Find until >
    while questionnaire[pos] != questionSymb:
        pos += 1
    pos += 1
    # Find until [
    while questionnaire[pos] != openAnsSymb:
        question += questionnaire[pos]
        pos += 1
    questionArr.append(question)
    pos += 1
    # Skip the spaces
    while questionnaire[pos] == ' ':
        pos += 1
    answer = ""
    # Find until ]
    while questionnaire[pos] != closeAnsSymb:
        answer += questionnaire[pos]
        pos += 1
    pos += 1
    answer = answer.lower()
    answerArr.append(answer)

# Shuffle the questions and answers
indexes = list(range(len(questionArr)))
random.shuffle(indexes)

questionSize = len(questionArr)
for i in range(questionSize):
    randIndex = indexes[i]
    print(f"{i + 1}/{questionSize}) {questionArr[randIndex]}")
    input_answer = input("Answer: ").lower()
    print()
    if answerArr[randIndex] == input_answer:
        print("Your answer is correct!")
    else:
        print("Your answer is wrong, the correct answer is:")
        print(answerArr[randIndex])
    print()

