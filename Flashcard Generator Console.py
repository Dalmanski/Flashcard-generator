import os
import random
from difflib import SequenceMatcher

# Global variables
answerSet = "choices"
switchQuesAns = False 
removeEndAns = 0

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

def processConfigLine(line):
    global answerSet, switchQuesAns, removeEndAns
    line = line[1:].strip()
    assignments = line.split(",")

    for assignment in assignments:
        var, value = assignment.split("=")
        var = var.strip()
        value = value.strip()

        if var == "answerSet":
            answerSet = str(value)
        elif var == "switchQuesAns":
            switchQuesAns = eval(value)
        elif var == "removeEndAns":
            removeEndAns = int(value)

def loadQuestions():
    global switchQuesAns
    questionSymb = '>'
    answerSymb = '~'
    globalSetSymb = '!'
    questionArr = []
    answerArr = []

    folderPath = "questionnaire"
    files = [f for f in os.listdir(folderPath) if f.endswith('.txt')]

    print("Available files:\n")
    for idx, file in enumerate(files):
        print(f"{idx + 1}: {file}")
    print()

    while True:
        try:
            fileChoice = int(input(f"\nSelect a file to load (1-{len(files)}): ")) - 1
            if 0 <= fileChoice < len(files):
                selectedFile = os.path.join(folderPath, files[fileChoice])
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    with open(selectedFile, "r") as file:
        lines = file.readlines()

    questions = []
    answers = []

    question = ""
    answer = ""

    for line in lines:
        line = line.strip()
        
        if line.startswith(globalSetSymb):
            processConfigLine(line)
            continue
        
        if line.startswith(questionSymb):
            if question:  
                questions.append(question)
                question = ""
            question += line[1:].strip()
        elif line.startswith(answerSymb):
            answer += line[1:].strip()
            answers.append(answer)  
            answer = "" 
        elif line != "":
            print(f"Found abnormally contains: {line}") 

    if switchQuesAns:
        questions, answers = answers, questions

    combined = list(zip(questions, answers))
    random.shuffle(combined)
    questions[:], answers[:] = zip(*combined)
    clrScr()
    return questions, answers

def isAnswerClose(inputAnswer, actualAnswer):
    similarityRatio = SequenceMatcher(None, inputAnswer, actualAnswer).ratio()
    return similarityRatio >= 0.8

def submitChoice(inputAnswer, correctAnswer):
    global removeEndAns
    length = len(correctAnswer)
    correctAnswer = correctAnswer[:length-removeEndAns]
    inputAnswer = inputAnswer[:length-removeEndAns]
    if correctAnswer == inputAnswer:
        print("\nYour answer is correct!")
    elif isAnswerClose(inputAnswer, correctAnswer):
        print(f"\nSo close but the accurate answer is:\n{correctAnswer}")
    else:
        print(f"\nYour answer is wrong. The correct answer is:\n{correctAnswer}")

def presentChoices(correctAnswer, allAnswers):
    global removeEndAns
    allAnswersCopy = allAnswers[:]  
    allAnswersCopy.remove(correctAnswer)  
    incorrectChoices = random.sample(allAnswersCopy, 3) 
    choices = [correctAnswer] + incorrectChoices 
    random.shuffle(choices)  

    if answerSet == "choices":
        print("\nChoices:")
        choiceLabels = ['a', 'b', 'c', 'd']
        for i, choice in enumerate(choices):
            length = len(choice)
            print(f"{choiceLabels[i]}) {choice[:length-removeEndAns]}")
        return choices, choiceLabels
    elif answerSet == "input":
        userInput = input("\nType your answer: ").strip()
        return [userInput], []

def playQuiz():
    clrScr()
    questionArr, answerArr = loadQuestions()
    currentQuestion = 0
    while currentQuestion < len(questionArr):
        print(f"\nQuestion {currentQuestion + 1}/{len(questionArr)}:\n")
        print(f"{questionArr[currentQuestion]}")

        choices, choiceLabels = presentChoices(answerArr[currentQuestion], answerArr)

        if answerSet == "choices":
            while True: 
                inputAnswer = input("\nChoose the correct answer (a-d): ").lower().strip()
                if inputAnswer in choiceLabels:
                    choiceIndex = choiceLabels.index(inputAnswer)
                    submitChoice(choices[choiceIndex], answerArr[currentQuestion])
                    print()  
                    break  
                else:
                    print("Invalid choice. Please enter a letter between a and d.")
        elif answerSet == "input":
            inputAnswer = choices[0]
            submitChoice(inputAnswer, answerArr[currentQuestion])
            print()

        userInput = input("Enter anything to go to the next question, or type 'e' to quit: ").strip().lower()
        if userInput == 'e': 
            print("Thank you for playing!")
            return 

        clrScr()
        currentQuestion += 1

    print("End of questions!")


# Main
while True:
    playQuiz()
    restart = input("Do you want to play again? (y/n): ").strip().lower()
    if restart != 'y':
        break
