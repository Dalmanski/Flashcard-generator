import re

# Example string
correctAnswer = "This is a test {example1} and another {example2} and yet another {example3}"

# Find all matches of text within {}
matches = re.findall(r'\{(.*?)\}', correctAnswer)

# Count the number of matches
count = len(matches)

print("Number of matches:", count)
