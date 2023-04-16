import os
import re
import subprocess
from class_info import ClassInfo, get_package_name, get_class_name
from plantuml import PlantUML
project_path = "C:\Apps\The-Prophecy-of-Hank\HandyHank\Assets\HandyHank\Scripts\Runtime" #input("Enter the project path: ")

def unity_format(code):
    res = code\
.replace(" --> MonoBehaviour", "").replace(" --> SerializedMonoBehaviour", "")\
.replace(" --> ScriptableObject", "").replace(" --> SerializedScriptableObject", "")\
.replace(" --> IDisposable", "")\
.replace(" --> Singleton", "")
    
    # # remove lines where there is only one word (e.g. "Hank")
    res = re.sub(r'(?m)^\s*\w+\s*$', '', res)
    # trim lines
    res = re.sub(r'(?m)^\s+', '', res)
    return res

def generate_plantuml_image(plantuml_code, output_path):
    plantuml_instance = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    temp_file = 'temp_plantuml.txt'
    with open(temp_file, 'w') as f:
        f.write(plantuml_code)
    try:
        plantuml_instance.processes_file(temp_file, output_path)
    except subprocess.CalledProcessError as e:
        print(f"Error generating PlantUML image: {e}")
    os.remove(temp_file)
    
def generate_plantuml_diagram_chunks(cs_files):
    class_diagram = ["@startuml"]
    packages = {}

    for cs_file in cs_files:
        using_statements, class_inheritance = parse_relationships(cs_file)
        class_name = os.path.splitext(os.path.basename(cs_file))[0]
        package_name = os.path.dirname(cs_file).replace(project_path, '').strip(os.sep)
        package_name = package_name.replace(os.sep, '_')  # Replace path separators with underscores
        if package_name not in packages:
            packages[package_name] = []
        packages[package_name].append(class_name)
    for package_name, classes in packages.items():
        class_diagram.append(f"namespace {package_name} {{")
        for class_name in classes:
            class_diagram.append(f"  class {class_name}")
        class_diagram.append("}")

    class_diagram.append("@enduml")
    return "\n".join(class_diagram)


def generate_mermaid_diagram_group(cs_files, group_name):
    class_diagram = ["classDiagram"]
    packages = {}
    relationships = {}

    for cs_file in cs_files:
        using_statements, class_inheritance = parse_relationships(cs_file)
        class_name = os.path.splitext(os.path.basename(cs_file))[0]
        package_name = os.path.dirname(cs_file).replace(project_path, '').strip(os.sep)
        package_name = package_name.replace(os.sep, '_')  # Replace path separators with underscores
        if package_name not in packages:
            packages[package_name] = []
        packages[package_name].append(class_name)
        relationships[class_name] = class_inheritance
    related_classes = set([group_name])
    to_process = [group_name]

    while to_process:
        current_class = to_process.pop()
        for related_class in relationships.get(current_class, []):
            if related_class not in related_classes:
                related_classes.add(related_class)
                to_process.append(related_class)
    for package_name, classes in packages.items():
        for class_name in classes:
            if class_name in related_classes:
                class_diagram.append(f"class {class_name}")
                for inheritance in relationships[class_name]:
                    class_diagram.append(f"{class_name} *-- {inheritance}")

    return "\n".join(class_diagram)

from collections import namedtuple, defaultdict

def get_package_name(cs_file, project_path):
    return os.path.dirname(os.path.relpath(cs_file, project_path)).replace(os.sep, '_')

def get_class_name(cs_file):
    return os.path.splitext(os.path.basename(cs_file))[0]

def generate_mermaid_diagram_chunks(cs_files, project_path):
    class_diagram = ["flowchart RL"]
    packages = defaultdict(list)
    class_info_dict = {}

    for cs_file in cs_files:
        class_info_dict[cs_file] = ClassInfo(*parse_relationships(cs_file))
        class_name = get_class_name(cs_file)
        package_name = get_package_name(cs_file, project_path)
        packages[package_name].append(class_name)
    
    # Generate class nodes
    # Apply: a --> b --> c
    for cs_file in cs_files:
        class_name = get_class_name(cs_file)
        for inheritance in class_info_dict[cs_file].class_inheritance:
            class_diagram.append(f"{class_name} --> {inheritance}")
    
    # for cs_file in cs_files:
    #     class_name = get_class_name(cs_file)
    #     #[class_diagram.append(f"{class_name} -.-> {relationship}") for relationship in class_info_dict[cs_file].using_statements if "Runtime" in relationship]
    #     for relationship in class_info_dict[cs_file].using_statements:
    #        if "Runtime" in relationship:
    #            class_diagram.append(f"{class_name} -.-> {relationship}")
               
    class_diagram = [unity_format(line) for line in class_diagram]
    
    #Generate package nodes
    #Apply: a --> b --> c
    for package_name, classes in packages.items():
        if len(classes) <= 1:
            continue
        class_diagram.append(f"subgraph {package_name}")
        for class_name in classes:
            class_diagram.append(f"  {class_name}")
        class_diagram.append("end")
    
    return "\n".join(class_diagram)

def generate_mermaid_diagram(cs_files):
    class_diagram = ["classDiagram"]

    for cs_file in cs_files:
        using_statements, class_inheritance = parse_relationships(cs_file)
        class_name = os.path.splitext(os.path.basename(cs_file))[0]
        class_diagram.append(f"class {class_name}")
        for inheritance in class_inheritance:
            class_diagram.append(f"{class_name} *-- {inheritance}")

    return "\n".join(class_diagram)

def find_cs_files(path):
    cs_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.cs'):
                cs_files.append(os.path.join(root, file))
    return cs_files

def parse_relationships(cs_file):
    with open(cs_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    using_statements = re.findall(r'using (\w+(?:\.\w+)*);', content)
    class_inheritance = re.findall(r'class \w+\s*:\s*(\w+)', content)
    
    return using_statements, class_inheritance

def print_relationships(cs_files):
    for cs_file in cs_files:
        using_statements, class_inheritance = parse_relationships(cs_file)
        print(f"File: {cs_file}")
        if using_statements:
            print("  Using statements:")
            for statement in using_statements:
                print(f"    {statement}")
                
        if class_inheritance:
            print("  Inheritance:")
            for inheritance in class_inheritance:
                print(f"    Inherits from {inheritance}")
                
        print()


cs_files = find_cs_files(project_path)

mermaid_diagram = generate_mermaid_diagram_chunks(cs_files, project_path)
mermaid_diagram = re.sub(r'(?m)^\s+', '', mermaid_diagram)

import pyperclip

pyperclip.copy(mermaid_diagram)

print("Mermaid diagram copied to clipboard!")
