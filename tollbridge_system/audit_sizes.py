import os
import glob

path = "/home/joshua445/tollbridge_system"
files = glob.glob(os.path.join(path, "**/*.py"), recursive=True)

print(f"{'FILE':<30} | {'LINES':<10}")
print("-" * 45)

file_stats = []
for f in files:
    if 'master_architect' in f or 'trim_bloat' in f or 'audit_sizes' in f:
        continue
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as file_obj:
            line_count = sum(1 for _ in file_obj)
        file_stats.append((os.path.basename(f), line_count))
    except Exception as e:
        file_stats.append((os.path.basename(f), str(e)))

for name, lines in sorted(file_stats, key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True):
    print(f"{name:<30} | {lines}")
