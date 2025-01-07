import pygame
import os
import random
import ast
import re
from difflib import SequenceMatcher

# Initialize Pygame
pygame.init()

# Global Variables
answerSet = "choices"
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

# Pygame Screen Setup
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Quiz Game")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Color theme (Quizizz-like)
colors = {
    "text": (255, 255, 255),  # White text
    "bg": (34, 34, 34),       # Dark background
    "button": (75, 160, 75),  # Green button color
    "button_hover": (50, 120, 50),  # Darker green when hovered
    "button_correct": (255, 255, 0),  # Yellow (correct)
    "button_wrong": (255, 0, 0),  # Red (wrong)
    "button_disabled": (169, 169, 169)  # Gray (disabled)
}

# Button class to handle button drawing and events
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.text_surf = self.wrap_text(text, width)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.disabled = False

    def wrap_text(self, text, max_width):
        # Wrap the text to fit the button width
        lines = []
        words = text.split(' ')
        line = words[0]

        for word in words[1:]:
            if self.font.size(line + ' ' + word)[0] <= max_width:
                line += ' ' + word
            else:
                lines.append(line)
                line = word
        lines.append(line)

        wrapped_text = '\n'.join(lines)
        return self.font.render(wrapped_text, True, (255, 255, 255))  # White text color

    def draw(self, surface):
        if self.disabled:
            pygame.draw.rect(surface, colors["button_disabled"], self.rect)
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, self.hover_color, self.rect)
            else:
                pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

# Function to clear screen
def clrScr():
    screen.fill(colors["bg"])

def processConfigLine(line):
    global answerSet, switchQuesAns, trimEndAns, sameTypeChoices
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
                pass  # We are not using the theme() anymore
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

    if not files:
        return [], []

    selectedFile = files[0]  # Default to the first file

    try:
        with open(selectedFile, "r", encoding='utf-8', errors='replace') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return [], []
    except Exception as e:
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
                return [], []

    if len(questions) != len(answers):
        return [], []
    
    if switchQuesAns:
        questions, answers = answers, questions
    
    combined = list(zip(questions, answers))
    random.shuffle(combined)
    questions[:], answers[:] = zip(*combined)
    clrScr()
    return questions, answers

def presentChoices(correctAnswer, answerArr):
    choices = [correctAnswer]
    while len(choices) < 4:
        random_choice = random.choice(answerArr)
        if random_choice not in choices:
            choices.append(random_choice)
    
    random.shuffle(choices)
    return choices, ['a', 'b', 'c', 'd']

def submitChoice(inputAnswer, correctAnswer, choiceButtons):
    global trimEndAns, score
    length = len(correctAnswer)
    correctAnswer = correctAnswer[:length - trimEndAns]
    inputAnswer = inputAnswer[:length - trimEndAns]

    if caseSenseAns:
        correctAnswer = correctAnswer.lower()
        inputAnswer = inputAnswer.lower()

    correctAnswer = re.sub(r'\{.*?\}', '', correctAnswer).strip()

    # Highlight correct and incorrect answers
    if correctAnswer == inputAnswer:
        print("\nYour answer is correct!\n")
        score += 1
        highlightButtons(choiceButtons, correctAnswer, 'yellow')  # Correct answer to yellow
    else:
        print(f"\nYour answer is wrong.\nThe correct answer is:\n{correctAnswer}\n")
        highlightButtons(choiceButtons, correctAnswer, 'yellow')  # Correct answer to yellow
        highlightButtons(choiceButtons, inputAnswer, 'red')  # Incorrect answer to red
        
    # After the choice is made, turn all buttons gray
    for button in choiceButtons:
        if button.text != correctAnswer and button.text != inputAnswer:
            button.color = colors["button_disabled"]  # Other buttons to gray
            button.disable()  # Disable the buttons after choice is made


def highlightButtons(choiceButtons, answer, color):
    """
    Update the color of the buttons.
    If answer matches the button text, color it with the provided color.
    If the answer is correct, color it yellow.
    """
    for button in choiceButtons: 
        if button.text == answer:
            button.color = color  # Highlight correct answer in yellow or red
        else:
            button.color = colors["button_disabled"]  # Set the other buttons to gray



# Wrap the question text to fit inside the box with center alignment
def wrap_text_to_box(text, max_width, font):
    words = text.split(' ')
    lines = []
    current_line = ''
    
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)  # Add the last line
    
    return lines

# Function to display wrapped text in the question box
def display_question(screen, question, x, y, max_width, font, box_height):
    wrapped_question = wrap_text_to_box(question, max_width, font)
    
    # Calculate the position of the text based on the longest line
    for i, line in enumerate(wrapped_question):
        text_surface = font.render(line, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect(center=(x, y + i * 30))  # Center the text
        screen.blit(text_surface, text_rect)


def playQuiz():
    questionArr, answerArr = loadQuestions()

    if not questionArr:
        print("Error: No questions available.")
        pygame.quit()
        quit()

    currentQuestion = 0
    while currentQuestion < len(questionArr):
        clrScr()

        question = questionArr[currentQuestion]
        answer = answerArr[currentQuestion]

        # Display the question at the top
        display_question(screen, question, screen_width // 2, 100, 600, font, 200)

        # Generate button choices
        choices, labels = presentChoices(answer, answerArr)

        button_spacing = 60  # Vertical spacing between buttons
        buttons = [Button(100, 200 + i * button_spacing, 600, 40, labels[i] + ". " + choices[i], colors["button"], colors["button_hover"], small_font) for i in range(4)]

        for button in buttons:
            button.draw(screen)

        # Next button at the bottom
        next_button = Button(300, 500 + button_spacing, 200, 40, "Next", colors["button"], colors["button_hover"], small_font)
        next_button.draw(screen)
        pygame.display.flip()

        waiting_for_click = True
        while waiting_for_click:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if next_button.is_clicked(mouse_pos):
                        next_button.color = colors["button_wrong"]
                        waiting_for_click = False
                    else:
                        for i, button in enumerate(buttons):
                            if button.is_clicked(mouse_pos):
                                
                                print(f"The choices[{i}] is clicked")
                                userChoice = labels[i]
                                

                                # Process answer submission
                                submitChoice(userChoice, answerArr[currentQuestion], buttons)

                                # Proceed to the next question
                                currentQuestion += 1
                                break

    pygame.quit()


# Start the quiz
playQuiz()
