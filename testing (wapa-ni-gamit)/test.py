import pygame
import sys

# Initialize Pygame
pygame.init()

# Define some constants and colors
WIDTH, HEIGHT = 800, 600
colors = {
    "button": (255, 255, 0),  # Yellow
    "button_hover": (255, 255, 100),  # Light yellow for hover effect
    "button_click": (255, 0, 0),  # Red for click
    "background": (255, 255, 255),  # White background
}
small_font = pygame.font.SysFont("Arial", 20)

# Button class definition
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.clicked = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)  # Change color on hover
        else:
            pygame.draw.rect(screen, self.color, self.rect)  # Default color

        # Render the text
        text_surf = self.font.render(self.text, True, (0, 0, 0))  # Black text
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiple Buttons Color Change Example")

# List of labels and choices
labels = ["Option 1", "Option 2", "Option 3", "Option 4"]
choices = ["A", "B", "C", "D"]

# Button spacing and list creation using list comprehension
button_spacing = 60
buttons = [Button(100, 200 + i * button_spacing, 600, 40, labels[i] + ". " + choices[i], colors["button"], colors["button_hover"], small_font) for i in range(4)]

# Run the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check if any button is clicked
        for button in buttons:
            if button.is_clicked(event):
                button.color = colors["button_click"]  # Change color to red when clicked

    # Fill the background with white
    screen.fill(colors["background"])

    # Draw all the buttons
    for button in buttons:
        button.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
