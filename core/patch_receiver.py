path = "sip-remote-handoff/receiver.py"
with open(path, "r") as f:
    content = f.read()

# Replace relative import cleanly
target = "from .envelope import compute_artifact_sha256, verify_envelope_signature"
replacement = """try:
    from .envelope import compute_artifact_sha256, verify_envelope_signature
except ImportError:
    from envelope import compute_artifact_sha256, verify_envelope_signature"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(path, "w") as f:
        f.write(content)
    print("Successfully patched imports in receiver.py")
else:
    print("Target import string not found verbatim.")
