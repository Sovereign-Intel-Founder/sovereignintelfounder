import os

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    removed_count = 0
    
    for line in lines:
        # Strip out lines containing documentation links or markdown link syntax
        if 'tiangolo.com' in line or '](' in line or '[FastAPI docs' in line:
            removed_count += 1
            continue
        cleaned_lines.append(line)
        
    if removed_count > 0:
        bak_path = filepath + '.bak'
        with open(bak_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        print(f"[CLEANED] {os.path.basename(filepath)}: Removed {removed_count} lines of doc spam")
    else:
        print(f"[OK] {os.path.basename(filepath)}: No doc spam detected.")

target_dir = "/home/joshua445/tollbridge_system"
for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith('.py') and not file.startswith('trim_bloat'):
            clean_file(os.path.join(root, file))
