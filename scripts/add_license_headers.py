import os

LICENSE_HEADER = """# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""

JS_LICENSE_HEADER = """/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"""

def add_header(file_path, header):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "Copyright (c) 2024" in content:
        print(f"Skipping {file_path} - Header already present")
        return

    # Handle shebangs
    if content.startswith("#!"):
        lines = content.splitlines(keepends=True)
        new_content = lines[0] + header + "".join(lines[1:])
    else:
        new_content = header + content

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {file_path}")

def main():
    root_dir = "."
    skip_dirs = ["node_modules", "venv", ".git", "__pycache__", ".next", "dist", "build", ".gemini", "artifacts"]
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.endswith(".py"):
                add_header(file_path, LICENSE_HEADER)
            elif file.endswith((".ts", ".tsx", ".js", ".jsx")):
                # Skip config files that might break with comments at top or are auto-generated
                if "json" in file: continue
                add_header(file_path, JS_LICENSE_HEADER)

if __name__ == "__main__":
    main()
