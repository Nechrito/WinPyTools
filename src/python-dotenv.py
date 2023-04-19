import os
import re
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

directory = "src"

# Dictionary to store new environment variables
new_env_vars = {}

# Function to replace absolute paths with environment variable reference
def replace_abs_path(match):
    abs_path = match.group()
    if abs_path.startswith("http://") or abs_path.startswith("https://"):
        return abs_path
    env_var_name = "PROJECT_PATH"
    new_env_vars[env_var_name] = abs_path
    return f'os.getenv("{env_var_name}")'

# Regex pattern to match absolute paths
path_pattern = re.compile(r'(?<=r")(?:[a-zA-Z]:)?[\\/](?:[a-zA-Z0-9\s_@\-^!#$%&+={}\[\]]+[\\/]?)+')

# Iterate through all files in the directory
for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(".py"):
            
            if "dotenv" in file:
                continue
            
            #print(f"Path: {file}")
            
            file_path = os.path.join(root, file)
            
            print(f"File: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace absolute paths with environment variable references
            new_content = path_pattern.sub(replace_abs_path, content)
            
            # Add imports if necessary
            if new_content != content:
                if "from dotenv import load_dotenv" not in content:
                    new_content = "from dotenv import load_dotenv\n" + new_content
                if "from pathlib import Path" not in content:
                    new_content = "from pathlib import Path\n" + new_content
                if "load_dotenv()" not in content:
                    new_content = "load_dotenv()\n" + new_content
                    
                print(f'Added imports to {file_path} and replaced absolute paths with environment variables for {len(new_env_vars)} paths')
            
                #print(new_content)
                
                # Save the modified content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

# Save the environment variables to the .env file
with open(".env", "a", encoding="utf-8") as f:
   for key, value in new_env_vars.items():
        print(f"{key}={value}\n")
#         #f.write(f"{key}={value}\n")
