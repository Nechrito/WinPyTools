import os
import subprocess
from plantuml import PlantUML

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
    
def generate_plantuml_diagram_chunks(cs_files, project_path: str):
    chart = ["@startuml"]
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
        chart.append(f"namespace {package_name} {{")
        for class_name in classes:
            chart.append(f"  class {class_name}")
        chart.append("}")

    chart.append("@enduml")
    return "\n".join(chart)

def parse_relationships(cs_file):
    with open(cs_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    using_statements = re.findall(r'using (\w+(?:\.\w+)*);', content)
    class_inheritance = re.findall(r'class \w+\s*:\s*(\w+)', content)
    
    return using_statements, class_inheritance