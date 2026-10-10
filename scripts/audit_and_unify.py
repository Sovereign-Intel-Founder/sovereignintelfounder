import os
import glob
import json

def scan_environment():
    print("[*] Scanning workspace for connecting entities and subsystems...")
    
    # Discover all Python modules, configs, and database references
    py_files = glob.glob("**/*.py", recursive=True)
    db_files = glob.glob("**/*.db", recursive=True)
    shm_files = glob.glob("/dev/shm/*")
    
    entities = {
        "bridges": [],
        "mesh_nodes": [],
        "databases": db_files,
        "shared_memory": shm_files,
        "configs": []
    }
    
    for f in py_files:
        if "archive" in f or "backup" in f:
            continue
        if "bridge" in f.lower():
            entities["bridges"].append(f)
        elif "mesh" in f.lower() or "cluster" in f.lower():
            entities["mesh_nodes"].append(f)
        elif "config" in f.lower():
            entities["configs"].append(f)
            
    print(f"\n[+] Audit Complete:")
    print(f"    - Active Bridges: {len(entities['bridges'])}")
    print(f"    - Mesh/Cluster Nodes: {len(entities['mesh_nodes'])}")
    print(f"    - Databases Found: {entities['databases']}")
    print(f"    - Shared Memory Channels: {entities['shared_memory']}")
    
    # Output unified map manifest
    with open("unified_system_map.json", "w") as out:
        json.dump(entities, out, indent=2)
    print("\n[+] Saved complete system map to 'unified_system_map.json'.")

if __name__ == "__main__":
    scan_environment()
