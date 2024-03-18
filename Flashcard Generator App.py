import tkinter as tk
import os
import random

def clrScr():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_questions():
    questionSymb = '>'
    answerSymb = '~'
    questionArr = []
    answerArr = []
    with open("questionnaire.txt", "r") as file:
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
            question += line[1:]  
        elif line.startswith(answerSymb):
            answer += line[1:]  
            answers.append(answer.lower())  
            answer = "" 
        elif line != "":
            print(f"found abnormally contains: {line}") 
    if question:  
        questions.append(question)
    combined = list(zip(questions, answers))
    random.shuffle(combined)
    questions[:], answers[:] = zip(*combined)
    return questions, answers

def submit_choice(choice=None):
    global answerArr, current_question
    if choice:
        input_answer = choice.lower()
    else:
        input_answer = entry.get().lower()
    if answerArr[current_question] == input_answer:
        result_label.config(text="Your answer is correct!", fg="green")
    else:
        result_label.config(text=f"Your answer is wrong, the correct answer is: {answerArr[current_question]}", fg="red")
    current_question += 1
    if current_question < len(questionArr):
        question_label.config(text=f"{current_question + 1}/{len(questionArr)}) {questionArr[current_question]}")
        set_choices()
        entry.delete(0, tk.END)
        submit_button.config(text="Submit Answer")
        hide_choices()
        question_and_answer_text.pack_forget()  # Hide question and answer text if shown
    else:
        question_label.config(text="End of questions!")
        try_again_button.pack(pady=5)
        question_and_answer_text.pack_forget()  # Hide question and answer text if shown

def show_hide_choices():
    global choices_buttons, choices_visible
    if not choices_visible:
        for button in choices_buttons:
            button.pack(pady=5)
        choices_visible = True
        show_hide_choices_button.config(text="Hide Choices")
    else:
        hide_choices()

def hide_choices():
    global choices_buttons, choices_visible
    for button in choices_buttons:
        button.pack_forget()
    choices_visible = False
    show_hide_choices_button.config(text="Show Choices")

def try_again():
    global current_question
    current_question = 0
    question_label.config(text=f"{current_question + 1}/{len(questionArr)}) {questionArr[current_question]}")
    result_label.config(text="")
    entry.delete(0, tk.END)
    try_again_button.pack_forget()

def show_question_and_answer():
    global current_question, questionArr, answerArr, question_and_answer_visible
    if not question_and_answer_visible:
        previous_question_index = max(0, current_question - 1)
        previous_question = questionArr[previous_question_index]
        previous_answer = answerArr[previous_question_index]

        current_question_text = questionArr[current_question]
        current_answer_text = answerArr[current_question]

        question_and_answer_text.delete("1.0", tk.END)
        question_and_answer_text.insert(tk.END, f"Previous Question:\n{previous_question}\n\nPrevious Answer:\n{previous_answer}\n\nCurrent Question:\n{current_question_text}\n\nCurrent Answer:\n{current_answer_text}")
        question_and_answer_text.pack()
        question_and_answer_visible = True
    else:
        question_and_answer_text.pack_forget()
        question_and_answer_visible = False

def set_choices():
    global current_question, answerArr, choices_buttons
    correct_answer = answerArr[current_question]
    all_answers = answerArr[:]
    all_answers.remove(correct_answer)
    choices = [correct_answer] + random.sample(all_answers, 3)
    random.shuffle(choices)
    for i, button in enumerate(choices_buttons):
        button.config(text=choices[i], command=lambda choice=choices[i]: submit_choice(choice))

clrScr()
questionArr, answerArr = load_questions()
current_question = 0
choices_visible = False
question_and_answer_visible = False

# Dark mode theme colors
bg_color = "#121212"
fg_color = "white"
highlight_color = "#1f1f1f"
button_color = "#303030"
button_fg_color = "white"

root = tk.Tk()
root.title("Questionnaire")
root.state('zoomed')  # Maximize the window
root.configure(bg=bg_color)

question_font = ("Arial", 30)
button_font = ("Arial", 20)

question_frame = tk.Frame(root, bg=bg_color)
question_frame.pack(expand=True)

question_label = tk.Label(question_frame, text=f"{current_question + 1}/{len(questionArr)}) {questionArr[current_question]}", font=question_font, wraplength=1200, bg=bg_color, fg=fg_color)
question_label.pack(pady=(50, 10))

entry = tk.Entry(root, width=40, bg=highlight_color, fg=fg_color, justify="center", font=("Arial", 20))
entry.pack(pady=5)
entry.bind("<Return>", lambda event=None: submit_choice())

submit_button = tk.Button(root, text="Submit Answer", command=submit_choice, bg=button_color, fg=button_fg_color, font=button_font)
submit_button.pack(pady=5)

result_label = tk.Label(root, text="", fg="green", bg=bg_color)
result_label.pack(pady=10)

choices_buttons = []
for _ in range(4):
    button = tk.Button(root, text="", bg=button_color, fg=button_fg_color, font=button_font)
    button.pack_forget()
    choices_buttons.append(button)

set_choices()  # Set choices for the first question

show_hide_choices_button = tk.Button(root, text="Show Choices", command=show_hide_choices, bg=button_color, fg=button_fg_color, font=button_font)
show_hide_choices_button.pack(pady=5)

show_question_button = tk.Button(root, text="Show Question and Answer", command=show_question_and_answer, bg=button_color, fg=button_fg_color, font=button_font)
show_question_button.pack(pady=5)

try_again_button = tk.Button(root, text="Try Again", command=try_again, bg=button_color, fg=button_fg_color, font=button_font)
try_again_button.pack_forget()

question_and_answer_text = tk.Text(root, bg=highlight_color, fg=fg_color, height=20, width=60, font=("Arial", 20))
question_and_answer_text.pack_forget()

root.mainloop()
