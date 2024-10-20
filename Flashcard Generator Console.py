import os
import random
from difflib import SequenceMatcher
import ast # For use ast.literal_eval(), safer method than eval(). Convert string to boolean

# Global variables
answerSet = "choices"
theme = "white_text_on_black"
switchQuesAns = False 
sameTypeChoices = False
capitalize = False
removeEndAns = 0
questionSymb = '>'
answerSymb = '~'
globalSetSymb = '!'
commentSymb = '#'

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

def setTheme():
    global theme
    if theme == "amber_text_on_black":
        print(end="\033[38;2;255;165;0m") # orange amber text
        print(end="\033[40m") # black bg
    elif theme == "white_text_on_black":
        print(end="\033[37m") # white text
        print(end="\033[40m") # black bg

def processConfigLine(line):
    global answerSet, theme, switchQuesAns, removeEndAns, sameTypeChoices, capitalize
    global questionSymb, answerSymb, globalSetSymb, commentSymb

    line = line[1:].strip()
    assignments = line.split(",")

    for assignment in assignments:
        try:
            var, value = assignment.split("=")
            var = var.strip()
            value = value.strip()

            if var == "answerSet":
                answerSet = str(value)
            elif var == "switchQuesAns":
                switchQuesAns = ast.literal_eval(value)
            elif var == "removeEndAns":
                removeEndAns = int(value)
            elif var == "questionSymb":
                questionSymb = str(value)
            elif var == "answerSymb":
                answerSymb = str(value)
            elif var == "sameTypeChoices":
                sameTypeChoices = ast.literal_eval(value)
            elif var == "capitalize":
                capitalize = ast.literal_eval(value)
            elif var == "theme":
                theme = str(value)
            else:
                print(f"Warning: Unknown configuration variable -> {var}")

        except ValueError:
            print(f"Error: Invalid configuration assignment -> {assignment}")
        except Exception as e:
            print(f"Error processing assignment '{assignment}': {e}")

def loadQuestions():
    global switchQuesAns, capitalize
    global questionSymb, answerSymb, globalSetSymb, commentSymb
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

    try:
        with open(selectedFile, "r", encoding='utf-8', errors='replace') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("The selected file was not found.")
        return [], []
    except Exception as e:
        print(f"An error occurred while opening the file: {e}")
        return [], []

    questions = []
    answers = []
    question = ""
    answer = ""

    for lineNumber, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith(commentSymb) or line == "":
            continue
        
        if line.startswith(globalSetSymb):
            try:
                processConfigLine(line)
            except Exception as e:
                print(f"Syntax error in config at line {lineNumber}: {line}")
                print(f"Error: {e}")
            continue

        if line.startswith(questionSymb):
            if question:
                if capitalize:
                    question = question.capitalize()
                questions.append(question)
            question = line[1:].strip()
        elif line.startswith(answerSymb):
            answer = line[1:].strip()
            if question: 
                if capitalize:
                    question = question.capitalize()
                    answer = answer.capitalize()
                questions.append(question)
                answers.append(answer)
                question = ""
            else:
                print(f"Error: Answer found at line {lineNumber} without a matching question.")

    if not (line.startswith(questionSymb) or line.startswith(answerSymb) or 
        line.startswith(globalSetSymb) or line.startswith(commentSymb)):
        print(f"Syntax error: Invalid symbol at line {lineNumber}: {line}")
        return [], [] 
    
    if len(questions) != len(answers):
        print(f"Error: Uneven number of questions and answers.")
        print(f"Please check if there's question and answer at the same time")
        return [], []
    
    if switchQuesAns:
        questions, answers = answers, questions
    
    combined = list(zip(questions, answers))
    
    if not combined:
        print("Error: No valid question-answer pairs found.")
        return [], []
    
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
    global removeEndAns, sameTypeChoices
    allAnswersCopy = allAnswers[:]  
    allAnswersCopy.remove(correctAnswer)  
    
    if sameTypeChoices:
        if correctAnswer.isdigit():
            allAnswersCopy = [ans for ans in allAnswersCopy if ans.isdigit()]
        elif not correctAnswer.isdigit(): 
            allAnswersCopy = [ans for ans in allAnswersCopy if not ans.isdigit()]

    uniqueChoices = {correctAnswer}
    numIncorrectChoices = min(len(allAnswersCopy), 3)

    while len(uniqueChoices) < 4:
        incorrectChoice = random.choice(allAnswersCopy)
        uniqueChoices.add(incorrectChoice) 

    choices = list(uniqueChoices)
    random.shuffle(choices)

    while len(choices) < 4:
        choices.append("No more options") 
    
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
    setTheme()

    if not questionArr:
        print("Unable to start the quiz due to syntax errors.\n")
        return
    
    currentQuestion = 0
    score = 0
    labelMap = {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}

    while currentQuestion < len(questionArr):
        print(f"Score: {score}/{len(questionArr)}\n")
        print(f"{currentQuestion + 1}) {questionArr[currentQuestion]}")
        choices, choiceLabels = presentChoices(answerArr[currentQuestion], answerArr)

        if answerSet == "choices":
            while True: 
                inputAnswer = input("\nChoose the correct answer (1-4 or a-d): ").lower().strip()

                if inputAnswer in labelMap:
                    inputAnswer = labelMap[inputAnswer]

                if inputAnswer in choiceLabels:
                    choiceIndex = choiceLabels.index(inputAnswer)
                    if choices[choiceIndex] == answerArr[currentQuestion]:
                        score += 1
                    submitChoice(choices[choiceIndex], answerArr[currentQuestion])
                    print()  
                    break  
                else:
                    print("Invalid choice. Please enter a number between 1 and 4 or a letter between a and d.")
        
        elif answerSet == "input":
            inputAnswer = choices[0]
            if inputAnswer == answerArr[currentQuestion]:
                score += 1
            submitChoice(inputAnswer, answerArr[currentQuestion])
            print()
        
        userInput = input("Enter anything to go to the next question, or type 'e' to quit: ").strip().lower()

        if userInput == 'e': 
            clrScr()
            print("\nThank you for playing!\n")
            return 
        
        clrScr()
        currentQuestion += 1

    print(f"End of questions! Your final score is {score}/{len(questionArr)}.\n")


# Main
while True:
    playQuiz()
    restart = input("Do you want to play again? (y/n): ").strip().lower()
    if restart != 'y':
        break
