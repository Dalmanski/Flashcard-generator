import re

# Example string
string = "asidjasoidjasoid {nakit-an na} oisahdoiashjd"

# Regular expression to find text inside curly braces
matches = re.findall(r'\{(.*?)\}', string)

# Output the result
print("Output inside {}:", matches[0])

# Input strings
string = "hello world"
print(string.replace("llo w", ""))
