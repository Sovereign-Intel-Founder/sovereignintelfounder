import os
import glob

# Find init_keys.py location
matches = glob.glob('**/init_keys.py', recursive=True)
if not matches:
    print("Error: Could not find init_keys.py anywhere in the workspace.")
    exit(1)

init_path = matches[0]
print(f"Found init_keys.py at: {init_path}")

# Read existing Makefile
if not os.path.exists('Makefile'):
    print("Error: Makefile not found in current directory.")
    exit(1)

with open('Makefile', 'r') as f:
    content = f.read()

# Generate proper audit rule
new_audit_rule = f"audit:\n\tPYTHONPATH=$(PWD) python3 {init_path}\n"

# Replace or append audit rule
if "audit:" in content:
    lines = content.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if line.startswith('audit:'):
            skip = True
            new_lines.append(new_audit_rule.strip())
            continue
        if skip and (line.startswith('\t') or line.startswith('    ')):
            continue
        skip = False
        new_lines.append(line)
    content = '\n'.join(new_lines)
else:
    content += f"\n{new_audit_rule}"

with open('Makefile', 'w') as f:
    f.write(content)

print("Makefile updated successfully with correct PYTHONPATH and path.")
