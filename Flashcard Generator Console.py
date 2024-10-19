import os
import random
from difflib import SequenceMatcher

# Global variables
answerSet = "choices"
switchQuesAns = False 
removeEndAns = 0
questionSymb = '>'
answerSymb = '~'
globalSetSymb = '!'
commentSymb = '#'

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

def processConfigLine(line):
    global answerSet, switchQuesAns, removeEndAns
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
                switchQuesAns = eval(value)
            elif var == "removeEndAns":
                removeEndAns = int(value)
            elif var == "questionSymb":
                questionSymb = str(value)
            elif var == "answerSymb":
                answerSymb = str(value)
            else:
                print(f"Warning: Unknown configuration variable -> {var}")

        except ValueError:
            print(f"Error: Invalid configuration assignment -> {assignment}")
        except Exception as e:
            print(f"Error processing assignment '{assignment}': {e}")

def loadQuestions():
    global switchQuesAns
    global questionSymb, answerSymb, globalSetSymb, commentSymb
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
    questionLineNumbers = []
    answerLineNumbers = []

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
                questions.append(question)
                questionLineNumbers.append(lineNumber)
            question = line[1:].strip()
        elif line.startswith(answerSymb):
            answer = line[1:].strip()
            if question: 
                questions.append(question)
                answers.append(answer)
                questionLineNumbers.append(lineNumber - 1)
                answerLineNumbers.append(lineNumber)
                question = "" 
            else:
                print(f"Error: Answer found at line {lineNumber} without a matching question.")

    if not (line.startswith(questionSymb) or line.startswith(answerSymb) or 
        line.startswith(globalSetSymb) or line.startswith(commentSymb)):
        print(f"Syntax error: Invalid symbol at line {lineNumber}: {line}")
        return [], [] 
    
    if len(questions) != len(answers):
        print(f"Error: Uneven number of questions and answers.")
        print(f"Questions found at lines: {questionLineNumbers}")
        print(f"Answers found at lines: {answerLineNumbers}")
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
    global removeEndAns
    allAnswersCopy = allAnswers[:]  
    allAnswersCopy.remove(correctAnswer)  
    numIncorrectChoices = min(len(allAnswersCopy), 3)
    incorrectChoices = random.sample(allAnswersCopy, numIncorrectChoices)
    choices = [correctAnswer] + incorrectChoices

    while len(choices) < 4:
        choices.append("No more options") 
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
    if not questionArr:
        print("Unable to start the quiz due to syntax errors.")
        return
    
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
