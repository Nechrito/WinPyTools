        
"""
classDiagram
classA <|-- classB
classC *-- classD
classE o-- classF
classG <-- classH
classI -- classJ
classK <.. classL
classM <|.. classN
classO .. classP

classDiagram
classA --|> classB : Inheritance
classC --* classD : Composition
classE --o classF : Aggregation
classG --> classH : Association
classI -- classJ : Link(Solid)
classK ..> classL : Dependency
classM ..|> classN : Realization
classO .. classP : Link(Dashed)

classDiagram
classA <|-- classB : implements
classC *-- classD : composition
classE o-- classF : aggregation

classDiagram
    Animal <|--|> Zebra
    
classDiagram
    Customer "1" --> "*" Ticket
    Student "1" --> "1..*" Course
    Galaxy --> "many" Star : Contains
"""

# https://mermaid.js.org/syntax/classDiagram.html

import os
import shutil
import sys
import re
from pathlib import Path
from collections import defaultdict

def find_most_common_relationship(relationships):
    relationship_counts = defaultdict(int)
    
    for relationship in relationships:
        relationship_counts[relationship[1]] += 1

    return max(relationship_counts, key=relationship_counts.get)

def format_class_name(class_name):
    return class_name \
        .replace("<", "&lt;") \
        .replace(">", "&gt;") \
        #.replace("SerializedMonoBehaviour", "MonoBehaviour") \
        #.replace("SerializedScriptableObject", "ScriptableObject") \
        #.replace("ScriptableObjectSingleton", "Singleton") \
        #.replace("GlobalConfigCollection", "Singleton")
        
"""

def parse_csharp_code(file_path):
    relationships = []
    class_info = defaultdict(dict)

    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    class_pattern = r'(public|private|protected)?\s+class\s+(\w+)(\s*:\s*(\w+))?'

    class_matches = re.finditer(class_pattern, code, re.MULTILINE)

    for match in class_matches:
        class_name = match.group(2)
        base_class_name = match.group(4)

        if base_class_name is not None:
            relationships.append((class_name, base_class_name))

        class_info[class_name]['base'] = base_class_name

    return relationships, class_info

def get_class_members(class_name, class_info):
    members = class_info[class_name].get('members', [])
    members_str = "\n".join([f"    {member}" for member in members])
    return members_str

def generate_mermaid_script(relationships, class_info):
    mermaid_script = '''classDiagram\n  direction RL\n'''
    
    # for relationship in relationships:
    #     class_name1 = format_class_name(relationship[0])
    #     class_name2 = format_class_name(relationship[1])

    #     # if relationship[1] in blacklist or relationship[0] in blacklist:
    #     #     if class_name1 not in defined_classes:
    #     #         defined_classes.add(class_name1)
    #     #         mermaid_script += f'class {class_name1}~{class_name2}~'
                
    #     #         mermaid_script += '{\n    \n'
                
    #     #         mermaid_script += '}\n'
        
    #     # if relationship[1] in blacklist or relationship[0] in blacklist:
    #     #     mermaid_script += f'{class_name1}\n{class_name2}\n'
    #     #     continue

    #     mermaid_script += f'"{class_name1}" --> "{class_name2}"\n'
    
    # return (mermaid_script.replace('"', ''))

    for relationship in relationships:
        class_name1 = format_class_name(relationship[0])
        class_name2 = format_class_name(relationship[1])

        members1 = get_class_members(class_name1, class_info)
        members2 = get_class_members(class_name2, class_info)

        if class_info[class_name1].get('base'):
            mermaid_script += f'  class {class_name1} "{class_name1}" {{\n{members1}\n  }}\n'
            mermaid_script += f'  {class_name1} <|-- {class_info[class_name1]["base"]}\n'

        if class_info[class_name2].get('base'):
            mermaid_script += f'  class {class_name2} "{class_name2}" {{\n{members2}\n  }}\n'
            mermaid_script += f'  {class_name2} <|-- {class_info[class_name2]["base"]}\n'

        mermaid_script += f'  {class_name1} -x {class_name2}"\n'
        #mermaid_script += f'  {class_name1}    {class_name2}\n'
        #mermaid_script += f'  "{class_name1}" --> "{class_name2}"\n'
    
    return mermaid_script.replace('"', '')
"""

def class_info_to_plantuml(class_info):
    #plantuml_code = "@startuml\n"
    plantuml_code = "classDiagram\n"

    for class_name, info in class_info.items():
        base_class_name = info.get('base', '')
        members = info.get('members', [])
        methods = info.get('methods', [])

        if base_class_name:
            plantuml_code += f"{class_name} --|> {base_class_name}\n"

        #plantuml_code += f"class {class_name} {{\n"
        plantuml_code += f'class {class_name} {{\n'
        plantuml_code += f"    \n"
        

        for member in members:
            access, _, member_type, member_name = member
            plantuml_code += f"  {access.strip()} {member_type} {member_name}\n"

        for method in methods:
            access, _, return_type, method_name = method
            plantuml_code += f"  {access.strip()} {return_type} {method_name}()\n"

        plantuml_code += "}\n"

    #plantuml_code += "@enduml\n"

    return plantuml_code

def unpack_to_mermaid_code(class_info):
    mermaid_code = "classDiagram\n"

    for class_name, info in class_info.items():
        base_class_name = info.get('base', '')
        members = info.get('members', [])
        methods = info.get('methods', [])

        if base_class_name:
            mermaid_code += f"{class_name} <|-- {base_class_name}\n"

        mermaid_code += f"class {class_name} {{\n"

        for member in members:
            access, _, member_type, member_name = member
            mermaid_code += f"  {access.strip()} {member_type} {member_name}\n"

        for method in methods:
            access, _, return_type, method_name = method
            mermaid_code += f"  {access.strip()} {return_type} {method_name}()\n"

        mermaid_code += "}\n"

    return mermaid_code


def parse_csharp_code(file_path):
    relationships = []

    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    class_pattern = r'(public|private|protected)?\s+class\s+(\w+)(\s*:\s*(\w+))?'
    class_matches = re.finditer(class_pattern, code, re.MULTILINE)

    class_info = {}

    for match in class_matches:
        class_name = match.group(2)
        base_class_name = match.group(4)

        if base_class_name is not None:
            relationships.append((class_name, base_class_name))

        class_info[class_name] = {'base': base_class_name}

    class_matches = re.findall(r'\bclass\b\s+(\w+)(?:\s*:\s*(\w+))?\s*{([\s\S]*?})', code, re.MULTILINE)

    for match in class_matches:
        class_name = match[0]
        base_class_name = match[1]

        class_data = match[2]
        members = re.findall(r'((public|private|protected)\s+)?(\w+)\s+(\w+);', class_data)
        methods = re.findall(r'((public|private|protected)\s+)?(\w+)\s+(\w+)\s*\(', class_data)

        class_info[class_name]['members'] = members
        class_info[class_name]['methods'] = methods

    return relationships, class_info


def parse_relationships_from_class_file(class_file):
    relationships = []
    
    try:
        with open(class_file, 'r') as f:
            for line in f:
                if 'relationship' in line:
                    relationship = line.replace('relationship', '').strip().split()
                    relationships.append(relationship)
    except FileNotFoundError:
        print(f'Unable to find file: {class_file}')

    return relationships

def write_mermaid_file(relationships, output_file, class_info):
    mermaid_script = []
    mermaid_script.append("classDiagram")

    for rel in relationships:
        base_class = rel[0]
        derived_class = rel[1]

        base_class = base_class.replace(".", "_")
        derived_class = derived_class.replace(".", "_")

        mermaid_script.append(f"{derived_class} --|> {base_class}")

    mermaid_script = "\n".join(mermaid_script)

    with open(output_file, "w") as f:
        f.write(mermaid_script)


        
def main():
    if len(sys.argv) < 2:
        print("Usage: python unity_code_analyzer.py <directory_with_csharp_files>")
        exit(1)

    directory = sys.argv[1]

    all_relationships = []
    
    class_info = defaultdict(dict)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                relationships, file_class_info = parse_csharp_code(file_path)
                all_relationships.extend(relationships)
                class_info.update(file_class_info)

    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mermaid")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        # os.remove(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    relations_per_file = 15
    
    # convert class_info to plantuml
    plantuml_code = class_info_to_plantuml(class_info)
    
    print(plantuml_code)
    
    with open('plantuml_code.puml', 'w') as f:
        f.write(plantuml_code)

    for i in range(0, len(all_relationships), relations_per_file):
        relationships_chunk = all_relationships[i:i+relations_per_file]
        common_relationship = find_most_common_relationship(relationships_chunk)
        output_file = os.path.join(output_dir, f"{common_relationship}.mmd")
        write_mermaid_file(relationships_chunk, output_file, class_info)

    print("Mermaid scripts have been generated in the mermaid_output directory.")

if __name__ == "__main__":
    main()