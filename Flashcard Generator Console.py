import os
import random
from difflib import SequenceMatcher

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_questions():
    questionSymb = '>'
    answerSymb = '~'
    questionArr = []
    answerArr = []

    folder_path = "questionnaire"
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    print("Available files:\n")
    for idx, file in enumerate(files):
        print(f"{idx + 1}: {file}")
    print()

    while True:
        try:
            file_choice = int(input(f"Select a file to load (1-{len(files)}): ")) - 1
            if 0 <= file_choice < len(files):
                selected_file = os.path.join(folder_path, files[file_choice])
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    with open(selected_file, "r") as file:
        lines = file.readlines()

    questions = []
    answers = []

    question = ""
    answer = ""
    for line in lines:
        line = line.strip()
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
            print(f"found abnormally contains: {line}") 
    if question:  
        questions.append(question)

    combined = list(zip(questions, answers))
    random.shuffle(combined)
    questions[:], answers[:] = zip(*combined)
    return questions, answers

def is_answer_close(input_answer, actual_answer):
    similarity_ratio = SequenceMatcher(None, input_answer, actual_answer).ratio()
    return similarity_ratio >= 0.8

def submit_choice(input_answer, correct_answer):
    if correct_answer == input_answer:
        print("Your answer is correct!\n")
    elif is_answer_close(input_answer, correct_answer):
        print(f"So close but the accurate answer is: {correct_answer}\n")
    else:
        print(f"Your answer is wrong. The correct answer is: {correct_answer}\n")

def present_choices(correct_answer, all_answers):
    all_answers_copy = all_answers[:]  
    all_answers_copy.remove(correct_answer)  
    incorrect_choices = random.sample(all_answers_copy, 3) 
    choices = [correct_answer] + incorrect_choices 
    random.shuffle(choices)  

    print("\nChoices:")
    choice_labels = ['a', 'b', 'c', 'd']
    for i, choice in enumerate(choices):
        print(f"{choice_labels[i]}) {choice}")  

    return choices, choice_labels

def play_quiz():
    clrScr()
    questionArr, answerArr = load_questions()
    clrScr()
    current_question = 0
    while current_question < len(questionArr):
        print(f"Question {current_question + 1}/{len(questionArr)}:")
        print(f"{questionArr[current_question]}")

        choices, choice_labels = present_choices(answerArr[current_question], answerArr)

        while True: 
            input_answer = input("\nChoose the correct answer (a-d): ").lower().strip()
            if input_answer in choice_labels:
                choice_index = choice_labels.index(input_answer)
                submit_choice(choices[choice_index], answerArr[current_question])
                print()  
                break  
            else:
                print("Invalid choice. Please enter a letter between a and d.")

        user_input = input("Enter anything to go to the next question, or type 'e' to quit: ").strip().lower()
        if user_input == 'e':  # Check if the user wants to quit
            print("Thank you for playing!")
            return  # Exit the current play_quiz function and stop the quiz

        clrScr()  # Clear the screen for the next question
        current_question += 1

    print("End of questions!")

# Main loop to allow for restarting the quiz
while True:
    play_quiz()
    restart = input("Do you want to play again? (y/n): ").strip().lower()
    if restart != 'y':
        break
