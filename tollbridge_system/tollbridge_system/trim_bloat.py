import os
import re

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    removed_count = 0
    
    # Patterns matching pasted markdown documentation spam
    markdown_link_pattern = re.compile(r'^\s*#?\s*\[.*?\]\(https?://.*?\)')
    markdown_header_pattern = re.compile(r'^\s*#{1,6}\s+[A-Z].*')
    
    for line in lines:
        # Filter out lines that look like accidental markdown paste artifacts
        if markdown_link_pattern.match(line) or (markdown_header_pattern.match(line) and not line.strip().startswith('#')):
            removed_count += 1
            continue
        cleaned_lines.append(line)
        
    if removed_count > 0:
        bak_path = filepath + '.bak'
        with open(bak_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        print(f"[CLEANED] {os.path.basename(filepath)}: Removed {removed_count} lines of doc spam (Backup: {os.path.basename(bak_path)})")
    else:
        print(f"[OK] {os.path.basename(filepath)}: No markdown spam detected.")

target_dir = "/home/joshua445/tollbridge_system"
for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith('.py') and file != 'trim_bloat.py':
            clean_file(os.path.join(root, file))
