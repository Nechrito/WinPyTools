import os
import sys
import re
from pathlib import Path

def parse_csharp_code(file_path):
    relationships = []

    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    pattern = r'\bclass\b\s+(\w+)\s*:\s*(\w+)'
    matches = re.findall(pattern, code, re.MULTILINE)

    for match in matches:
        relationships.append((match[0], match[1]))

    return relationships

def generate_mermaid_script(relationships, subdir):
    mermaid_script = '''classDiagram
'''
    blacklist = {"SerializedScriptableObject", "ScriptableObject", "MonoBehaviour", "Object", "Component", "IDisposable"}

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

    output_path = Path(f'mermaid_output/{subdir}')
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "output.mmd", "w", encoding='utf-8') as output_file:
        output_file.write(mermaid_script)

    return len(relationships)

def main():
    if len(sys.argv) < 2:
        print("Usage: python unity_code_analyzer.py <directory_with_csharp_files>")
        exit(1)

    directory = sys.argv[1]

    script_count = 0
    reference_count = 0
    unique_classes = set()

    for root, dirs, files in os.walk(directory):
        subdir = os.path.relpath(root, directory)
        relationships = []

        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                relationships.extend(parse_csharp_code(file_path))
                script_count += 1

        if relationships:
            reference_count += generate_mermaid_script(relationships, subdir)
            unique_classes.update([relationship[1] for relationship in relationships])

    print("Mermaid scripts have been generated in mermaid_output directory.")
    print(f"Statistics:")
    print(f"  - Script count: {script_count}")
    print(f"  - Reference count: {reference_count}")
    print(f"  - Unique classes referenced: {len(unique_classes)}")

if __name__ == "__main__":
    main()
