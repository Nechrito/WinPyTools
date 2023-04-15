        
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

def get_class_members(class_name, class_info):
    members = class_info[class_name].get('members', [])
    members_str = "\n".join([f"    {member}" for member in members])
    return members_str
        
import re
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
        members_and_methods = re.findall(r'([+\-#])(\w+\s+\w+(?:\(.*?\))?)', match[2])

        for member in members_and_methods:
            member = [m.strip() for m in member]
            member = [re.sub(r'\s+', ' ', m) for m in member]
            member = [re.sub(r'(public|private|protected)\s+', '' , m) for m in member]
            member = [re.sub(r'\s+\w+\s+\w+\(.*?\)', '' , m) for m in member]
            member = [re.sub(r'\(.*?\)', '', m) for m in member]
            member = [re.sub(r';', '', m) for m in member]
            member = [re.sub(r'{\s*get;\s*set;\s*}', '', m) for m in member]
            member = [re.sub(r'{\s*get;\s*}', '', m) for m in member]
            member = [re.sub(r'{\s*set;\s*}', '', m) for m in member]
            member = [re.sub(r'{\s*}', '', m) for m in member]
            member = [re.sub(r'{\s*get;\s*set;\s*} =', '', m) for m in member]
            member = [re.sub(r'{\s*get;\s*} =', '', m) for m in member]
            member = [re.sub(r'{\s*set;\s*} =', '', m) for m in member]
            member = [re.sub(r'{\s*} =', '', m) for m in member]
            member = [re.sub(r'{\s*get;\s*set;\s*} =>', '', m) for m in member]
            member = [re.sub(r'{\s*get;\s*} =>', '', m) for m in member]
            member = [re.sub(r'{\s*}', '', m) for m in member]
            member = [re.sub(r'\bnew\b', '', m) for m in member]
            member = [re.sub(r'\bstatic\b', '', m) for m in member]
            member = [re.sub(r'\boverride\b', '', m) for m in member]
            member = [re.sub(r'\babstract\b', '', m) for m in member]
            member = [re.sub(r'\bvirtual\b', '', m) for m in member]
            member = [re.sub(r'\bsealed\b', '', m) for m in member]
            member = [re.sub(r'\breadonly\b', '', m) for m in member]
            member = [re.sub(r'\bconst\b', '', m) for m in member]
            member = [re.sub(r'\s+', ' ', m) for m in member]
            member = [re.sub(r'(public|private|protected)\s+', '' , m) for m in member]
            
            #class_members[member[0]] = member[1]
        #class_info[class_name] = class_members

        class_info[class_name]['members_and_methods'] = members_and_methods

    return relationships, class_info

def generate_mermaid_script(relationships, class_info):
    mermaid_script = '''classDiagram\n'''

    for relationship in relationships:
        #class_name1 = format_class_name(relationship[0])
        
        class_name1 = relationship[0]
        class_name2 = relationship[1]
        
        mermaid_script += f'{class_name1} <|-- {class_name2}\n'

    for class_name, members_and_methods in class_info.items():
        
        if len(members_and_methods) > 0:
            
            #print(f'Class: {class_name}------------------\nMembers: {members_and_methods}\n------------------')
        
            mermaid_script += f'class {class_name} {{\n'
            
            #mermaid_script += '    +constructor()\n'
            #mermaid_script += '    \n'
            #mermaid_script += f'    {members_and_methods}\n'
            
            #for member in members_and_methods:
            mermaid_script += f'    {class_info["members_and_methods"]}\n'
            
            mermaid_script += '}\n'
        

    return mermaid_script

def write_mermaid_file(relationships, output_file, class_info):
    
    # for relationship in relationships:
    #     class_name1 = format_class_name(relationship[0])
    #     class_name2 = format_class_name(relationship[1])
    
    # TODO: Append suffix number to output_file if it exists already 
    # TODO: If output_file exists, try to parse it and append new relationships to it

    # TODO: If output_file exists, delete it and generate a new one
    if os.path.exists(output_file):
        
        # Get the suffix number from files with the same name
        output_file = output_file.replace('.txt', '')
        output_file = output_file.replace('.md', '')
        output_file = output_file.replace('.mmd', '')
        
        suffix = 1
        
        while os.path.exists(f'{output_file}{suffix}.txt') or os.path.exists(f'{output_file}{suffix}.md') or os.path.exists(f'{output_file}{suffix}.mmd'):
            suffix += 1
        
        output_file = f'{output_file}{suffix}.mmd'
        
        print(f'Output file {output_file} already exists. A new file will be created with the suffix {suffix}.')
        
        #os.remove(output_file)
        
        #with open(output_file, 'r', encoding='utf-8') as file:
            #mermaid_script = file.read()
    #else:
        #mermaid_script = ''
    
    mermaid_script = generate_mermaid_script(relationships, class_info)

    with open(output_file, "w", encoding='utf-8') as f:
        f.write(mermaid_script)

    print(f"Mermaid script has been generated as {output_file}")

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

    relations_per_file = 20

    for i in range(0, len(all_relationships), relations_per_file):
        relationships_chunk = all_relationships[i:i+relations_per_file]
        common_relationship = find_most_common_relationship(relationships_chunk)
        output_file = os.path.join(output_dir, f"{common_relationship}.mmd")
        write_mermaid_file(relationships_chunk, output_file, class_info)

    print("Mermaid scripts have been generated in the mermaid_output directory.")

if __name__ == "__main__":
    main()