import os
import re
import subprocess
import networkx as nx
import community as community_louvain
from collections import defaultdict
from matplotlib import pyplot as plt
import matplotlib

project_path = r"C:\Apps\The-Prophecy-of-Hank\HandyHank\Assets\HandyHank\Scripts\Runtime"

def parse_relationships(cs_file):
    with open(cs_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    using_statements = re.findall(r'using (\w+(?:\.\w+)*);', content)
    class_inheritance = re.findall(r'class \w+\s*:\s*(\w+)', content)
    
    return using_statements, class_inheritance

def find_cs_files(path):
    cs_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.cs'):
                cs_files.append(os.path.join(root, file))
    return cs_files
def suggest_folder_structure(cs_files):
    # Create a directed graph to represent dependencies between classes
    dependency_graph = nx.DiGraph()

    for cs_file in cs_files:
        using_statements, class_inheritance = parse_relationships(cs_file)
        
        class_name = os.path.splitext(os.path.basename(cs_file))[0]

        dependency_graph.add_node(class_name)
        
        # for inheritance in class_inheritance:
        #     dependency_graph.add_edge(class_name, inheritance)
            
        for using_statement in using_statements:
            dependency_graph.add_edge(class_name, using_statement)

    G = dependency_graph.to_undirected()
    
    # Detect communities in the graph using the Louvain method
    partition = community_louvain.best_partition(G)
    
    # Draw the graph
    pos = nx.spring_layout(G)
    
    # Color the nodes according to their partition
    #cmap = cm.get_cmap('viridis', max(partition.values()) + 1)  # Deprecated method
    cmap = matplotlib.colormaps.get_cmap('viridis')  # Recommended method
    nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=40,
                        cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.show()

    # Create a dictionary to store the suggested folder structure
    folder_structure = defaultdict(list)

    for class_name, folder_id in partition.items():
        folder_structure[folder_id].append(class_name)

    return folder_structure


def generate_mermaid_diagram_group(cs_files, group_name):
    chart = ["classDiagram"]
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
                chart.append(f"class {class_name}")
                for inheritance in relationships[class_name]:
                    chart.append(f"{class_name} *-- {inheritance}")

    return "\n".join(chart)


def get_package_name(cs_file, project_path):
    return os.path.dirname(os.path.relpath(cs_file, project_path)).replace(os.sep, '_')

def get_class_name(cs_file):
    return os.path.splitext(os.path.basename(cs_file))[0]

from collections import defaultdict

def generate_mermaid_diagram_chunks(cs_files, project_path):
    # TODO: Figure out which of flowchart or classDiagram to use, can multiple be used?
    chart = ["flowchart RL"]
    packages = defaultdict(list)
    class_info_dict = {}

    # Retrieves all classes and their relationships
    for cs_file in cs_files:
        class_info_dict[cs_file] = ClassInfo(*parse_relationships(cs_file))
        class_name = get_class_name(cs_file)
        package_name = get_package_name(cs_file, project_path)
        packages[package_name].append(class_name)
    
    # Generates dependency nodes from inheritance
    for cs_file in cs_files:
        class_name = get_class_name(cs_file)
        for inheritance in class_info_dict[cs_file].class_inheritance:
            chart.append(f"{class_name} --> {inheritance}")
    
    # Generates, a lot of, dependency nodes based on "using" statements. mermaid.live doesn't like this.
    # for cs_file in cs_files:
    #     class_name = get_class_name(cs_file)
    #     #[chart.append(f"{class_name} -.-> {relationship}") for relationship in class_info_dict[cs_file].using_statements if "Runtime" in relationship]
    #     for relationship in class_info_dict[cs_file].using_statements:
    #        if "Runtime" in relationship:
    #            chart.append(f"{class_name} -.-> {relationship}")
               
    chart = [unity_format(line) for line in chart]
    
    # Apply: a --> b --> c --> a OR a --> b & b --> c & c --> a
    for package_name, classes in packages.items():
        if len(classes) <= 1:
            continue
        chart.append(f"subgraph {package_name}")
        for class_name in classes:
            chart.append(f"  {class_name}")
        chart.append("end")
    
    return "\n".join(chart)

def generate_mermaid_diagram(cs_files):
    chart = ["classDiagram"]

    for cs_file in cs_files:
        using_statements, class_inheritance = parse_relationships(cs_file)
        class_name = os.path.splitext(os.path.basename(cs_file))[0]
        chart.append(f"class {class_name}")
        for inheritance in class_inheritance:
            chart.append(f"{class_name} *-- {inheritance}")

    return "\n".join(chart)

def parse_relationships(cs_file):
    with open(cs_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    using_statements = re.findall(r'using (\w+(?:\.\w+)*);', content)
    class_inheritance = re.findall(r'class \w+\s*:\s*(\w+)', content)
    
    return using_statements, class_inheritance

def find_cs_files(path):
    cs_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.cs'):
                cs_files.append(os.path.join(root, file))
    return cs_files

def unity_format(code):
    # These are the classes that Unity adds to every class, and we don't want to see them in the diagram
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


# Find all .cs files in the project path
cs_files = find_cs_files(project_path)

# Call the function to suggest an improved folder structure
suggested_folders = suggest_folder_structure(cs_files)

# Print the suggested folder structure
for folder_id, classes in suggested_folders.items():
    print(f"Folder {folder_id}: {', '.join(classes)}")
    
print(generate_mermaid_diagram_group(cs_files, "."))


# TODO: Suggest, after analyzing .cs files, an improved folder structure for the project based on the dependencies between classes