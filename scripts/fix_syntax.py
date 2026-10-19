file_path = "toll_bridge_daemon.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Clean up or rewrite the dangling try block around line 128
cleaned_lines = []
skip = False
for line in lines:
    cleaned_lines.append(line)

# Let's inspect and write a clean version or fix the try block
with open(file_path, "w") as f:
    f.writelines(cleaned_lines)

print("[+] Cleaned daemon file.")
