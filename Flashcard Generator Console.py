import os
import re
import random
from difflib import SequenceMatcher
import ast # For use ast.literal_eval(), safer method than eval(). Convert string to boolean

# Global variables
answerSet = "choices"
theme = ""
switchQuesAns = False 
sameTypeChoices = False
capitalize = False
caseSenseAns = False
trimEndAns = 0
questionSymb = '>'
answerSymb = '~'
globalSetSymb = '!'
commentSymb = '#'

score = 0

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
    elif theme == "default" or theme == "none":
        print(end="\033[0m")

def processConfigLine(line):
    global answerSet, theme, switchQuesAns, trimEndAns, sameTypeChoices
    global capitalize, caseSenseAns
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
            elif var == "trimEndAns":
                trimEndAns = int(value)
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
            elif var == "caseSenseAns":
                caseSenseAns = ast.literal_eval(value)
            else:
                print(f"Warning: Unknown configuration variable -> {var}")

        except ValueError:
            print(f"Error: Invalid configuration assignment -> {assignment}")
        except Exception as e:
            print(f"Error processing assignment '{assignment}': {e}")

def loadQuestions():
    global switchQuesAns, capitalize
    global questionSymb, answerSymb, globalSetSymb, commentSymb
    
    def find_txt_files(folder):
        txt_files = []
        for entry in os.listdir(folder):
            full_path = os.path.join(folder, entry)
            if os.path.isdir(full_path):
                txt_files.extend(find_txt_files(full_path))
            elif entry.endswith('.txt'):
                txt_files.append(full_path)
        return txt_files

    folderPath = "questionnaire"
    files = find_txt_files(folderPath) 
    print("\nAvailable files:\n")

    if not files:
        print("No .txt files found in the directory.")
        return [], []

    for idx, file in enumerate(files):
        relative_path = os.path.relpath(file, folderPath)
        print(f"{idx + 1}) {relative_path}")

    while True:
        user_input = input(f"\nSelect a file to load (1-{len(files)}): ").strip().lower()
     
        try:
            fileChoice = int(user_input) - 1
            if 0 <= fileChoice < len(files):
                selectedFile = files[fileChoice]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number or 'back'.")

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
                    if not answerSet == "input":
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
    global trimEndAns, score
    length = len(correctAnswer)
    correctAnswer = correctAnswer[:length-trimEndAns]
    inputAnswer = inputAnswer[:length-trimEndAns]

    if caseSenseAns:
        correctAnswer = correctAnswer.lower()
        inputAnswer = inputAnswer.lower()

    correctAnswer = re.sub(r'\{.*?\}', '', correctAnswer).strip()

    if correctAnswer == inputAnswer:
        print("\nYour answer is correct!\n")
        score += 1
    elif isAnswerClose(inputAnswer, correctAnswer):
        print(f"\nSo close...\nThe accurate answer is:\n{correctAnswer}\n")
        score += 1
    else:
        print(f"\nYour answer is wrong.\nThe correct answer is: {correctAnswer}\n")

def presentChoices(correctAnswer, allAnswers):
    global trimEndAns, sameTypeChoices
    allAnswersCopy = allAnswers[:]  
    allAnswersCopy.remove(correctAnswer)  

    categoryChoices = re.findall(r'\{(.*?)\}', correctAnswer)
    if categoryChoices:
        category = categoryChoices[0]
        allAnswersCopy = [ans for ans in allAnswersCopy if f'{{{category}}}' in ans]
        correctAnswer = correctAnswer.replace(f'{{{category}}}', "").strip()
        allAnswersCopy = [ans.replace(f'{{{category}}}', "").strip() for ans in allAnswersCopy]
    else:
        allAnswersCopy = [ans for ans in allAnswersCopy if not re.search(r'\{.*?\}', ans)]
    
    allAnswersCopy = [re.sub(r'\{.*?\}', '', ans).strip() for ans in allAnswersCopy]

    if sameTypeChoices:
        if correctAnswer.isdigit():
            allAnswersCopy = [ans for ans in allAnswersCopy if ans.isdigit()]
        else:
            allAnswersCopy = [ans for ans in allAnswersCopy if not ans.isdigit()]

    uniqueChoices = {correctAnswer}
    max_choices = min(4, len(allAnswersCopy) + 1)

    while len(uniqueChoices) < max_choices:
        incorrectChoice = random.choice(allAnswersCopy)
        uniqueChoices.add(incorrectChoice) 

    choices = list(uniqueChoices)
    random.shuffle(choices)

    if answerSet == "choices":
        print("\nChoices:")
        choiceLabels = ['a', 'b', 'c', 'd'][:len(choices)]
        for i, choice in enumerate(choices):
            length = len(choice)
            print(f"{choiceLabels[i]}) {choice[:length-trimEndAns]}")
        return choices, choiceLabels
    elif answerSet == "input":
        userInput = input("\nType your answer: ").strip()
        return [userInput], []

def playQuiz():
    questionArr, answerArr = loadQuestions()
    setTheme()

    if not questionArr:
        print("Unable to start the quiz due to syntax errors.\n")
        return
    
    currentQuestion = 0
    labelMap = {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}

    while currentQuestion < len(questionArr):
        print(f"Score: {score}/{len(questionArr)}\n")
        print(f"{currentQuestion + 1}) {questionArr[currentQuestion]}")
        choices, choiceLabels = presentChoices(answerArr[currentQuestion], answerArr)

        if answerSet == "choices":
            while True: 
                inputAnswer = input("\nChoose the correct answer\n(1-4 or a-d): ").lower().strip()

                if inputAnswer in labelMap:
                    inputAnswer = labelMap[inputAnswer]

                if inputAnswer in choiceLabels:
                    choiceIndex = choiceLabels.index(inputAnswer)
                    submitChoice(choices[choiceIndex], answerArr[currentQuestion])
                    break  
                else:
                    print("Invalid choice. Please enter a number between 1 and 4 or a letter between a and d.")
        
        elif answerSet == "input":
            inputAnswer = choices[0]
            submitChoice(inputAnswer, answerArr[currentQuestion])
        
        userInput = input("Enter anything to go to the next question,\nor type 'e' to quit: ").strip().lower()

        if userInput == 'e': 
            print("\nThank you for playing!\n")
            return 
        
        clrScr()
        currentQuestion += 1

    print(f"\nEnd of questions!")
    print(f"Your final score is {score}/{len(questionArr)}!\n")


# Main
while True:
    clrScr()
    playQuiz()
    restart = input("Do you want to play again? (y/n): ").strip().lower()
    if restart != 'y':
        break
