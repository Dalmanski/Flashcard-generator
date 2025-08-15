import os
import re
import random
from difflib import SequenceMatcher
import ast  # For use ast.literal_eval(), safer method than eval(). Convert string to boolean

answerSet = "choices"
theme = "default"
switchItems = False
sameTypeChoices = False
capitalize = False
caseSenseAns = False
trimEndLastItem = 0
firstItemSymb = '>'
lastItemSymb = '~'
globalSetSymb = '!'
commentSymb = '#'

score = 0

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

def setTheme():
    global theme
    if theme == "amber_text_on_black":
        print(end="\033[38;2;255;165;0m")  # orange amber text
        print(end="\033[40m")  # black bg
    elif theme == "white_text_on_black":
        print(end="\033[37m")  # white text
        print(end="\033[40m")  # black bg
    elif theme in ["default", "none", ""]:
        print(end="\033[0m")

def textColor(color):
    if color == "red": print(end="\033[31m")
    elif color == "yellow": print(end="\033[33m")
    elif color == "orange": print(end="\033[38;2;255;165;0m")
    elif color == "green": print(end="\033[32m")

def processConfigLine(line):
    global answerSet, theme, switchItems, trimEndLastItem, sameTypeChoices
    global capitalize, caseSenseAns
    global firstItemSymb, lastItemSymb, globalSetSymb, commentSymb

    line = line[1:].strip()
    assignments = line.split(",")

    for assignment in assignments:
        try:
            var, value = assignment.split("=")
            var = var.strip()
            value = value.strip()

            if var == "answerSet":
                answerSet = str(value)
            elif var == "switchItems":
                switchItems = ast.literal_eval(value)
            elif var == "trimEndLastItem":
                trimEndLastItem = int(value)
            elif var == "firstItemSymb":
                firstItemSymb = str(value)
            elif var == "lastItemSymb":
                lastItemSymb = str(value)
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
    global switchItems, capitalize
    global firstItemSymb, lastItemSymb, globalSetSymb, commentSymb

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

        if line.startswith(firstItemSymb):
            if question:
                if capitalize:
                    question = question.capitalize()
                questions.append(question)
            question = line[1:].strip()
        elif line.startswith(lastItemSymb):
            answer = line[1:].strip()
            if question:
                if capitalize:
                    question = question.capitalize()
                    if answerSet != "identification":
                        answer = answer.capitalize()
                questions.append(question)
                answers.append(answer)
                question = ""
            else:
                print(f"Error: Answer found at line {lineNumber} without a matching question.")

    if len(questions) != len(answers):
        print(f"Error: Uneven number of questions and answers.")
        return [], []

    if switchItems:
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
    global trimEndLastItem, score
    length = len(correctAnswer)
    correctAnswer = correctAnswer[:length - trimEndLastItem]
    inputAnswer = inputAnswer[:length - trimEndLastItem]

    if caseSenseAns:
        correctAnswer = correctAnswer.lower()
        inputAnswer = inputAnswer.lower()

    correctAnswer = re.sub(r'\{.*?\}', '', correctAnswer).strip()

    if correctAnswer == inputAnswer:
        textColor("yellow")
        print("\nYour answer is correct!\n")
        setTheme()
        score += 1
    elif isAnswerClose(inputAnswer, correctAnswer):
        textColor("orange")
        print(f"\nSo close...")
        setTheme()
        print(f"The accurate answer is:\n{correctAnswer}\n")
        score += 1
    else:
        textColor("red")
        print(end="\nWrong. ")
        setTheme()
        print("The correct answer is:")
        textColor("green")
        print(f"{correctAnswer}\n")
        setTheme()

def presentChoices(correctAnswer, allAnswers):
    if answerSet == "identification":
        userInput = input("\nType your answer: ").strip()
        return [userInput], []
    elif answerSet == "flashcard":
        input("\nPress Enter to reveal the answer...")
        print(f"\nAnswer: ", end="")
        textColor("green")
        print(f"{correctAnswer}\n")
        setTheme()
        return [], []

def playQuiz():
    questionArr, answerArr = loadQuestions()
    setTheme()

    if not questionArr:
        print("Unable to start the quiz.\n")
        return

    currentQuestion = 0

    while currentQuestion < len(questionArr):
        if not answerSet == "flashcard":
            print(f"Score: {score}/{len(questionArr)}")
        print(f"\n{currentQuestion + 1}) {questionArr[currentQuestion]}")
        choices, _ = presentChoices(answerArr[currentQuestion], answerArr)

        if answerSet == "identification":
            inputAnswer = choices[0]
            submitChoice(inputAnswer, answerArr[currentQuestion])

        elif answerSet == "flashcard":
            pass

        userInput = input("Enter anything to go to the next question, or type 'e' to quit: ").strip().lower()
        if userInput == 'e':
            print("\nThank you for playing!\n")
            return

        clrScr()
        currentQuestion += 1

    print(f"\nEnd of questions!")
    if not answerSet == "flashcard":
        print(f"Your final score is {score}/{len(questionArr)}!")

# Main
while True:
    clrScr()
    playQuiz()
    restart = input("\nDo you want to play again? (y/n): ").strip().lower()
    if restart != 'y':
        break
