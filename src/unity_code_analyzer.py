import os
import shutil
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import *

from sklearn.cluster import KMeans

def find_optimal_clusters(matrix):
    max_clusters = min(1, len(matrix))
    sum_of_squared_distances = []

    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(matrix)
        sum_of_squared_distances.append(kmeans.inertia_)
    optimal_k = sum_of_squared_distances.index(min(sum_of_squared_distances)) + 1

    return optimal_k

def group_classes_by_cluster(class_info, clustering_labels):
    grouped_classes = defaultdict(list)
    for class_name, cluster_label in zip(class_info.keys(), clustering_labels):
        grouped_classes[cluster_label].append(class_name)

    return grouped_classes

def find_most_common_relationship(relationships):
    relationship_counts = defaultdict(int)
    
    for relationship in relationships:
        relationship_counts[relationship[1]] += 1

    return max(relationship_counts, key=relationship_counts.get)

def class_info_to_plantuml(class_info):
    plantuml_code = "classDiagram\n"

    for class_name, info in class_info.items():
        base_class_name = info.get('base', '')
        members = info.get('members', [])
        methods = info.get('methods', [])

        if base_class_name:
            plantuml_code += f"{class_name} --|> {base_class_name}\n"
        plantuml_code += f'class {class_name} {{\n'
        plantuml_code += f"    \n"
        
        for member in members:
            access, _, member_type, member_name = member
            plantuml_code += f"  {access.strip()} {member_type} {member_name}\n"

        for method in methods:
            access, _, return_type, method_name = method
            plantuml_code += f"  {access.strip()} {return_type} {method_name}()\n"

        plantuml_code += "}\n"

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
    mermaid_code = '''classDiagram\ndirection BT\n'''
    
    for class_name, info in class_info.items():
        base_class_name = info.get('base', '')
        members = info.get('members', [])
        methods = info.get('methods', [])

        if base_class_name:
            mermaid_code += f"{class_name} <|-- {base_class_name}\n"
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

    return mermaid_code.replace('\n\n', '\n').replace('"', "")

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
        
        if len(cluster_relationships) > 0:
            relationship_counts = Counter(cluster_relationships)
            top_relationship = relationship_counts.most_common(1)[0][0]
            output_file = os.path.join(output_dir, f"{top_relationship[0]}_{top_relationship[1]}.mmd")

        cluster_class_info = {class_name: class_info[class_name] for class_name in class_names}
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

    return ("\n".join(mermaid_script)).replace('\n\n', '\n').replace('"', "")

def write_mermaid_script_to_file(mermaid_script: str, output_file: str) -> None:
    mermaid_script = mermaid_script.replace('\n\n', '\n').replace('"', "")
    if os.path.exists(output_file):
        with open(output_file, "a") as f:
            f.write(mermaid_script)
            return
    with open(output_file, "w") as f:
        f.write(mermaid_script)


def generate_mermaid_script(relationships, subdir):
    mermaid_script = '''classDiagram
'''
    blacklist = {} #{"SerializedScriptableObject", "ScriptableObject", "MonoBehaviour", "Object", "Component", "IDisposable"}

    for relationship in relationships:
        if relationship[0] in blacklist or relationship[1] in blacklist:
            continue

        class_name1 = relationship[0] \
        .replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("SerializedScriptableObject", "ScriptableObject") \
        .replace("SerializedMonoBehaviour", "MonoBehaviour") \
        .replace("ScriptableObjectSingleton", "ScriptableObject") \
        .replace("GlobalConfigCollection", "ScriptableObject")

        class_name2 = relationship[1] \
        .replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("SerializedScriptableObject", "ScriptableObject") \
        .replace("SerializedMonoBehaviour", "MonoBehaviour") \
        .replace("ScriptableObjectSingleton", "ScriptableObject") \
        .replace("GlobalConfigCollection", "ScriptableObject")

        mermaid_script += f'"{class_name1}" --> "{class_name2}"\n'

    mermaid_script = mermaid_script.replace('\n\n', '\n').replace('"', "")

    output_path = Path(f'mermaid/{subdir}')
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "output.mmd", "w", encoding='utf-8') as output_file:
        output_file.write(mermaid_script)

    return len(relationships)

def get_class_info_from_file(file_path: str) -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
    class_info = defaultdict(dict)
    relationships = []

    with open(file_path, 'r') as f:
        for line in f:
            if 'class' in line:
                class_name = line.split()[1]
                class_info[class_name]['members'] = []
                class_info[class_name]['file'] = file_path

            if 'relationship' in line:
                relationship = line.replace('relationship', '').strip().split()
                relationships.append(relationship)

            if 'public' in line or 'private' in line or 'protected' in line:
                member = line.strip().split()
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
                member = [m for m in member if m]
                member = ' '.join(member)
    return class_info, relationships
import os
import re
from collections import defaultdict, Counter

def get_bottom_directory(path):
    
    if not os.path.isdir(path):
        return None
    
    if not os.listdir(path):
        return path
    
    return get_bottom_directory(os.path.join(path, os.listdir(path)[0]))

def count_class_occurrences(file_path, class_name):
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    return code.count(class_name)

def analyze_relationships(directory):
    relationships = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".cs"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as file:
                    code = file.read()

                pattern = r'\bclass\b\s+(\w+)\s*:\s*(\w+)'
                matches = re.findall(pattern, code, re.MULTILINE)

                relationships.extend(matches)

    return relationships

from collections import defaultdict, Counter

def parse(file_path):
    local_relationships = []

    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    pattern = r'\bclass\b\s+(\w+)\s*:\s*(\w+)'
    matches = re.findall(pattern, code, re.MULTILINE)

    for match in matches:
        local_relationships.append((match[0], match[1]))
    return local_relationships

def count_references(file_path, class_name):
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    return code.count(class_name)

def print_most_referenced_classes(class_references):
    class_counts = Counter(class_references.values())
    class_counts_list = class_counts.most_common()

    print(f"MOST REFERENCED CLASSES")
    for class_name, count in class_counts_list[:20]:
        print(f"  - {class_name} ({count})")

def print_relationships(directory):
    relationships = []
    dependencies = []
    script_count = 0
    mermaid_script = "classDiagram\n"
    
    all_relationships = []
    class_info = defaultdict(dict)
    
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                rel, file_class_info = parse_csharp_code(file_path)
                all_relationships.extend(rel)
                class_info.update(file_class_info)
                #class_info.update(file_class_info)
                
    class_references = defaultdict(int)
    for root, dirs, files in os.walk(directory):
       for file in files:
           if file.endswith('.cs'):
               file_path = os.path.join(root, file)
               
               relationships, s = parse_csharp_code(file_path)
               
               for class_name in s:
                   class_references[class_name] += count_references(file_path, class_name)
    #print(class_references)
    
    # for rel in all_relationships:
    #     for r in rel:
    #         a, b = r
    #         mermaid_script += f"{a} --> {b}\n"
    
    print(mermaid_script)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                relationships.extend(parse(file_path))
                script_count += 1
                dependencies.append(parse_csharp_code(file_path)[0])
    
    grouped_relationships = defaultdict(list)
    for relationship in relationships:
        derived_class, base_class = relationship
        if base_class != 'MonoBehaviour' and base_class != 'ScriptableObject' and base_class != 'OdinEditorWindow' and not "Serializ" in base_class and not "Singleton" in base_class and not "Editor" in base_class and not "Attribute" in base_class and not "Drawer" in base_class:
            grouped_relationships[base_class].append(derived_class)
    
    for base_class, derived_classes in grouped_relationships.items():
        derived_classes = list(set(derived_classes))
        derived_classes.sort()
        
        if len(derived_classes) == 1:
            mermaid_script += f"{base_class} --|> {derived_classes[0]}\n"
        else:
            for derived_class in derived_classes:
                mermaid_script += f"{base_class} --> {derived_class}\n"
    
    mermaid_script = mermaid_script \
    .replace(" --> Serialized", "").replace(" --|> Serialized", "") \
    .replace(" --> Singleton", "").replace(" --|> Singleton", "") \
    .replace(" --> MonoBehaviour", "").replace(" --|> MonoBehaviour", "") \
    .replace(" --> ScriptableObject", "").replace(" --|> ScriptableObject", "") \
    
    print_most_referenced_relationships(grouped_relationships)
    
    #print_most_referenced_classes([x for x in class_references.items() if x[1] > 0], class_info)
    
    print_stats(script_count, len(grouped_relationships))
    
    with open('mermaid_script.mmd', 'w', encoding='utf-8') as file:
        file.write(mermaid_script)
    
def print_stats(script_count, relationship_count):
    print(f"STATS")
    print(f"  - Script count: {script_count}")
    print(f"  - Unique classes referenced: {relationship_count}\n")

def print_most_referenced_classes(class_counts_list, class_info):
    print("MOST REFERENCED CLASSES")
    for base_class, count in class_counts_list[:12]:
        print(f"  - {base_class} ({count}) by {class_info[base_class]}")

def print_most_referenced_relationships(grouped_relationships):
    print("MOST REFERENCED RELATIONSHIPS")
    sorted_relationships = sorted(grouped_relationships.items(), key=lambda x: len(x[1]), reverse=True)
    for base_class, derived_classes in sorted_relationships[:12]:
        count = len(derived_classes)
        print(f"  - {str(derived_classes[0])} : {base_class} ({count} candidates)") # ({((1 / count)*100):.1f}%)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python unity_code_analyzer.py <directory_with_csharp_files>")
        exit(1)

    directory = sys.argv[1]
    
    print_relationships(directory=directory)

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

    
if __name__ == "__main__":
    main()