# https://mermaid.js.org/syntax/classDiagram.html
        


import os
import shutil
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import *

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def create_relationship_matrix(class_info, relationships):
    class_indices = {class_name: index for index, class_name in enumerate(class_info.keys())}
    
    matrix_size = len(class_info)
    matrix = np.zeros((matrix_size, matrix_size), dtype=int)

    for class1, class2 in relationships:
        if class1 in class_indices and class2 in class_indices:
            idx1, idx2 = class_indices[class1], class_indices[class2]
            matrix[idx1, idx2] = 1
            matrix[idx2, idx1] = 1

    return matrix



from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def find_optimal_clusters(matrix):
    # Try different values of K
    max_clusters = min(20, len(matrix))
    sum_of_squared_distances = []

    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(matrix)
        sum_of_squared_distances.append(kmeans.inertia_)

    # Plot the elbow curve
    # plt.plot(range(1, max_clusters + 1), sum_of_squared_distances, "bx-")
    # plt.xlabel("Number of Clusters (K)")
    # plt.ylabel("Sum of Squared Distances")
    # plt.title("Elbow Method for Optimal K")
    # plt.show()

    # Find the elbow point
    # You can use a more advanced elbow detection method if necessary
    optimal_k = sum_of_squared_distances.index(min(sum_of_squared_distances)) + 1

    return optimal_k

def group_classes_by_cluster(class_info, clustering_labels):
    grouped_classes = defaultdict(list)
    
    # Iterate through class_info keys (class names) and clustering_labels
    for class_name, cluster_label in zip(class_info.keys(), clustering_labels):
        grouped_classes[cluster_label].append(class_name)

    return grouped_classes

def find_most_common_relationship(relationships):
    relationship_counts = defaultdict(int)
    
    for relationship in relationships:
        relationship_counts[relationship[1]] += 1

    return max(relationship_counts, key=relationship_counts.get)

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

def access_modifier_to_plantuml(access_modifier):
    if "public" in access_modifier:
        return '+'
    
    if "private" in access_modifier:
        return '-'
    
    if "protected" in access_modifier:
        return '#'
    
    return ''
    
def unpack_to_mermaid_code(class_info):
    mermaid_code = '''classDiagram\n  direction RL\n'''
    
    """
classDiagram
    classA --|> classB : Inheritance
    classC --* classD : Composition
    classE --o classF : Aggregation
    classG --> classH : Association
    classI -- classJ : Link(Solid)
    classK ..> classL : Dependency
    classM ..|> classN : Realization
    classO .. classP : Link(Dashed)
    """

    for class_name, info in class_info.items():
        base_class_name = info.get('base', '')
        members = info.get('members', [])
        methods = info.get('methods', [])

        if base_class_name:
            mermaid_code += f"{class_name} <|-- {base_class_name}\n"

        #mermaid_code += f"class {class_name} {{\n"
        mermaid_code += f"class {class_name}\n"

        has_members = len(members) > 0
        has_methods = len(methods) > 0
        has_members_and_methods = has_members and has_methods

        if not has_members_and_methods:
            mermaid_code += f"    \n"    

        for member in members:
            access, _, member_type, member_name = member
            mermaid_code += f"{class_name} : {access_modifier_to_plantuml(access.strip())} {member_type} {member_name}\n"

        for method in methods:
            access, _, return_type, method_name = method
            mermaid_code += f"{class_name} : {access_modifier_to_plantuml(access.strip())} {return_type} {method_name}()\n"

        mermaid_code += "\n"
        # mermaid_code += "}\n"

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
        
        members_and_methods = re.findall(r'([+\-#])(\w+\s+\w+(?:\(.*?\))?)', match[2])

        for member in members:
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

    return relationships, class_info

def write_relationships_to_files(grouped_classes, relationships, output_dir, class_info):
    for cluster_label, class_names in grouped_classes.items():
        cluster_relationships = [r for r in relationships if r[0] in class_names and r[1] in class_names]

        output_file = os.path.join(output_dir, f"cluster_{cluster_label}.mmd")

        cluster_class_info = {class_name: class_info[class_name] for class_name in class_names}

        # Write the class definitions and relationships for each cluster
        mermaid_script = unpack_to_mermaid_code(cluster_class_info)

        for relationship in cluster_relationships:
            mermaid_script += f"{relationship[0]} <|-- {relationship[1]}\n"

        with open(output_file, "w") as f:
            f.write(mermaid_script)

    print("Relationship files have been generated in the output directory.")


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

def write_mermaid_file(relationships: List[Tuple[str, str]], output_file: str, class_info: Dict[str, str]) -> None:
    mermaid_script = get_mermaid_script(relationships)
    write_mermaid_script_to_file(mermaid_script, output_file)

def get_mermaid_script(relationships: List[Tuple[str, str]]) -> str:
    mermaid_script = []
    mermaid_script.append("classDiagram")

    for rel in relationships:
        base_class = rel[0]
        derived_class = rel[1]

        base_class = base_class.replace(".", "_")
        derived_class = derived_class.replace(".", "_")

        mermaid_script.append(f"{derived_class} --|> {base_class}")

    return "\n".join(mermaid_script)

def write_mermaid_script_to_file(mermaid_script: str, output_file: str) -> None:
    
    # If it exists, append to the file
    if os.path.exists(output_file):
        with open(output_file, "a") as f:
            f.write(mermaid_script)
            return

    # Otherwise, create the file
    
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

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create a relationship matrix
    relationship_matrix = create_relationship_matrix(class_info, all_relationships)
    
    # Find the optimal number of clusters using K-means algorithm
    optimal_clusters = find_optimal_clusters(relationship_matrix)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=optimal_clusters)
    clustering_labels = kmeans.fit_predict(relationship_matrix)

    # Group the classes based on the clustering result
    grouped_classes = group_classes_by_cluster(class_info, clustering_labels)

    # Write relationships to files
    write_relationships_to_files(grouped_classes, all_relationships, output_dir, class_info)

if __name__ == "__main__":
    main()