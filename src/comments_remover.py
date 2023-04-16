import os
import re

def remove_single_line_comments(content):
    return re.sub(r'(?m)^\s*#.*\n?', '', content)

def remove_multi_line_comments(content):
    return re.sub(r'(?s)""".*?"""', '', content)

# Removing single-line comments and multi-line comments separately
def remove_comments(file_path):
    file_path = os.path.join(os.getcwd(), file_path)
    with open(file_path, 'r') as file:
        content = file.read()

    content = remove_single_line_comments(content)
    content = remove_multi_line_comments(content)

    with open(file_path, 'w') as file:
        file.write(content)
        
# remove_comments("src/unity_code_analyzer.py")
remove_comments("src/csharp_relationship.py")