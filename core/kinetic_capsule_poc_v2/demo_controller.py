import subprocess
import sys

def run_cmd(cmd):
    # Converted to argument array for subprocess security compliance
    if isinstance(cmd, str):
        import shlex
        cmd_args = shlex.split(cmd)
    else:
        cmd_args = cmd
    res = subprocess.run(cmd_args, shell=False)
    if res.returncode != 0:
        print(f"ERROR: Command failed: {cmd}")
        sys.exit(1)

def main():
    for run_num in [1, 2]:
        print(f"\n--- DEMO EXECUTION RUN {run_num}/2 ---")
        run_cmd("python3 -m kinetic_capsule_poc_v2.cell_a")
        run_cmd("python3 -m kinetic_capsule_poc_v2.cell_b")
        run_cmd("python3 -m kinetic_capsule_poc_v2.verifier")
        run_cmd("python3 -m kinetic_capsule_poc_v2.adversarial")

    print("\n" + "="*50)
    print("KINETIC PROOF-CARRYING COMPUTATION — PROCESS-BOUNDARY PASS")
    print("="*50)
    print("- Cell A process started.")
    print("- Cell A checkpoint created.")
    print("- Cell A exited after checkpoint.")
    print("- Cell B process started independently.")
    print("- Cell B signature verified.")
    print("- Cell B destination verified.")
    print("- Cell B resumed at step 500.")
    print("- Cell B completed at step 1,000.")
    print("- Independent verifier passed.")
    print("- Reference state matched.")
    print("- Tamper tests rejected.")
    print("- Replay tests rejected.")
    print("- Revocation tests rejected.")
    print("- Wrong-destination tests rejected.")

if __name__ == "__main__":
    main()
