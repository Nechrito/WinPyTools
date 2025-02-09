import os
import re

# Extract classes from a C# file, specifically made to give context to AI with minimized tokens


def extract_classes(file_content):
    pattern = re.compile(r"(?:^|\n)\s*class\s+(\w+)\s*{", re.MULTILINE)
    matches = pattern.finditer(file_content)
    classes = []
    for match in matches:
        class_name = match.group(1)
        start_pos = match.start() + len(match.group(0)) - 1
        stack = ["{"]
        i = start_pos + 1
        while stack:
            if file_content[i] == "{":
                stack.append("{")
            elif file_content[i] == "}":
                stack.pop()
            i += 1
        end_pos = i
        classes.append((class_name, file_content[start_pos:end_pos]))
    return classes


def replace_base_class(file_content, new_base_class="MonoBehaviour"):
    pattern = re.compile(r"class\s+\w+\s*:\s*\w+")
    return pattern.sub(lambda match: match.group().split(":")[0] + f": {new_base_class}", file_content)


input_file = "C:\\Users\\Magical Moe\\Desktop\\Scripts\\The-Prophecy-of-Hank\\HandyHank\\Assets\\HandyHank\\Scripts\\Runtime\\Character\\Units\\Unit.cs"
output_dir = "C:\\Users\\Magical Moe\\Desktop\\Scripts\\The-Prophecy-of-Hank\\HandyHank\\Assets\\HandyHank\\Scripts\\Runtime\\Character"

with open(input_file, "r") as f:
    file_content = f.read()

classes = extract_classes(file_content)
print(f"Found {len(classes)} classes in {input_file}.")
for class_name, class_content in classes:
    print(f"Writing {class_name}.cs")
    class_content = replace_base_class(class_content)
    print(f"Content: {class_content}")
    output_file = os.path.join(output_dir, f"{class_name}.cs")
    print(f"Output file: {output_file}")
    with open(output_file, "w") as f:
        f.write(class_content)

print("Splitting completed.")
