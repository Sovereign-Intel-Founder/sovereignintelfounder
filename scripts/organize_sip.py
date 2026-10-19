#!/usr/bin/env python3
"""
Sovereign Intelligence Protocol (SIP) - Repository Organization Tool
Version: 1.0.1
Authoritative tool for idempotent dry-run planning and approved archival curation.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "1.0.1"

def run_git(args, cwd=None):
    res = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def get_sha256(path):
    sha256_hash = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def verify_clean_working_tree():
    rc, out, _ = run_git(["status", "--porcelain"])
    if rc != 0:
        return False, "Failed to check git status."
    return len(out) == 0, out

def main():
    parser = argparse.ArgumentParser(
        description="Idempotent SIP Repository Organization and Curation Tool"
    )
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run in dry-run mode (default)")
    parser.add_argument("--apply", action="store_true", help="Apply approved changes from manifest")
    parser.add_argument("--manifest", type=str, help="Path to approved manifest JSON")
    parser.add_argument("--archive", type=str, help="Absolute path to secure archive vault")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow running with uncommitted changes")
    parser.add_argument("--version", action="version", version=f"%(prog)s {TOOL_VERSION}")

    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    # 1. Locate Git root
    rc, root_out, _ = run_git(["rev-parse", "--show-toplevel"])
    if rc != 0 or not root_out:
        print("ERROR: Must be run from inside a SIP Git repository.", file=sys.stderr)
        sys.exit(1)
    repo_root = Path(root_out).resolve()
    os.chdir(repo_root)

    # 2. Verify git status
    clean, status_out = verify_clean_working_tree()
    if not clean and not args.allow_dirty:
        print("ERROR: Working tree is not clean. Commit/stash changes or pass --allow-dirty.", file=sys.stderr)
        sys.exit(1)

    # Git metadata
    _, origin_url, _ = run_git(["config", "--get", "remote.origin.url"])
    _, branch, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    _, commit, _ = run_git(["rev-parse", "HEAD"])

    # Tracked files inventory
    tracked_files = [x for x in run_git(["ls-files"])[1].splitlines() if x.strip()]

    # 3. Secure archive validation
    archive_path_str = args.archive
    if not archive_path_str and args.dry_run:
        possible_defaults = [
            os.environ.get("SIP_SECURE_ARCHIVE"),
            str(repo_root.parent / "secure_archive"),
            os.path.expanduser("~/secure_archive")
        ]
        for p in possible_defaults:
            if p and os.path.exists(p):
                archive_path_str = p
                break

    if not archive_path_str:
        print("ERROR: No secure archive path provided via --archive or discovered safely. Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    archive_path = Path(archive_path_str).resolve()
    
    # Check if archive is outside repo
    try:
        archive_path.relative_to(repo_root)
        inside_repo = True
    except ValueError:
        inside_repo = False

    if args.dry_run:
        if not archive_path.exists():
            print(f"ERROR: Archive path {archive_path} does not exist.", file=sys.stderr)
            sys.exit(1)

        print("=== SIP REPOSITORY ORGANIZATION: DRY-RUN MODE ===")
        print(f"Repository Root: {repo_root}")
        print(f"Current Branch: {branch} ({commit[:7]})")
        print(f"Secure Archive: {archive_path} (Outside Repo: {not inside_repo})")

        candidates = []
        human_decisions = []
        manifest_records = []
        total_bytes = 0

        for f in tracked_files:
            p = repo_root / f
            size = p.stat().st_size if p.exists() else 0
            total_bytes += size

            if f == "core/=":
                sha = get_sha256(p)
                candidates.append(f)
                manifest_records.append({
                    "source": f,
                    "archive": str(archive_path / f),
                    "sha256": sha or "",
                    "classification": "malformed",
                    "reason": "Malformed zero-byte shell redirection artifact",
                    "references": [],
                    "public_claim_dependency": "none",
                    "approved": False
                })
            elif f.endswith("ledger.lock") or f in {"core/lane_id", "core/main"}:
                human_decisions.append(f)

        plan_json = {
            "version": TOOL_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit": commit,
            "branch": branch,
            "archive_path": str(archive_path),
            "archive_outside_repo": not inside_repo,
            "tracked_file_count": len(tracked_files),
            "total_bytes": total_bytes,
            "candidates": manifest_records,
            "human_decisions": human_decisions
        }

        json_path = Path("/tmp/sip-organization-plan.json")
        json_path.write_text(json.dumps(plan_json, indent=2), encoding="utf-8")

        md_lines = [
            "# Sovereign Intelligence Protocol: Organization & Curation Plan",
            "",
            f"- **Timestamp UTC**: `{plan_json['timestamp']}`",
            f"- **Commit**: `{commit}`",
            f"- **Branch**: `{branch}`",
            f"- **Archive Path**: `{archive_path}` (Outside Repo: `{not inside_repo}`)",
            f"- **Total Tracked Files**: `{len(tracked_files)}`",
            f"- **Total Tracked Size**: `{total_bytes} bytes`",
            "",
            "## Proposed Archive Candidates",
            ""
        ]

        if manifest_records:
            for rec in manifest_records:
                md_lines.extend([
                    f"### `{rec['source']}`",
                    f"- **Archive Destination**: `{rec['archive']}`",
                    f"- **SHA-256**: `{rec['sha256']}`",
                    f"- **Classification**: `{rec['classification']}`",
                    f"- **Reason**: `{rec['reason']}`",
                    f"- **Approved**: `{rec['approved']}`",
                    ""
                ])
        else:
            md_lines.append("None.")

        md_path = Path("/tmp/sip-organization-plan.md")
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

        print(f"\nGenerated Dry-Run Plan JSON: {json_path}")
        print(f"Generated Dry-Run Plan Markdown: {md_path}")
        print(f"Archive Candidates Found: {len(manifest_records)}")
        print("\nReview the generated plan and supply an approved manifest with --apply.")

    elif args.apply:
        if not args.manifest:
            print("ERROR: --apply mode requires --manifest /path/to/manifest.json", file=sys.stderr)
            sys.exit(1)

        manifest_file = Path(args.manifest)
        if not manifest_file.exists():
            print(f"ERROR: Manifest file not found at {manifest_file}", file=sys.stderr)
            sys.exit(1)

        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"ERROR: Failed to parse manifest JSON: {e}", file=sys.stderr)
            sys.exit(1)

        manifest_commit = manifest_data.get("commit")
        if manifest_commit != commit:
            print(f"ERROR: Manifest commit ({manifest_commit}) does not match current HEAD ({commit}). Aborting apply.", file=sys.stderr)
            sys.exit(1)

        manifest_archive_path_str = manifest_data.get("archive_path") or args.archive
        if not manifest_archive_path_str:
            print("ERROR: Manifest missing archive_path and no --archive provided.", file=sys.stderr)
            sys.exit(1)
        
        man_archive_path = Path(manifest_archive_path_str).resolve()
        if not man_archive_path.is_absolute():
            print("ERROR: Archive path must be absolute.", file=sys.stderr)
            sys.exit(1)
        
        try:
            man_archive_path.relative_to(repo_root)
            print("ERROR: Archive path must be outside the repository.", file=sys.stderr)
            sys.exit(1)
        except ValueError:
            pass

        candidates = manifest_data.get("candidates", [])
        if not candidates:
            print("ERROR: No candidates found in manifest.", file=sys.stderr)
            sys.exit(1)

        for rec in candidates:
            if not rec.get("approved", False):
                print(f"ERROR: Manifest contains unapproved record for '{rec.get('source')}'. All records must have approved=true.", file=sys.stderr)
                sys.exit(1)

        if not man_archive_path.exists():
            try:
                man_archive_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"ERROR: Could not create archive directory {man_archive_path}: {e}", file=sys.stderr)
                sys.exit(1)

        print("=== SIP REPOSITORY ORGANIZATION: APPLY MODE ===")
        
        moved_count = 0
        already_archived_count = 0
        applied_records = []

        for record in candidates:
            src_rel = record["source"]
            src_path = repo_root / src_rel
            dest_path = Path(record["archive"])

            if not src_path.exists():
                print(f"WARNING: Source file {src_rel} no longer exists. Skipping.")
                continue

            current_sha = get_sha256(src_path)
            if current_sha != record["sha256"]:
                print(f"ERROR: SHA-256 mismatch for {src_rel}. Expected {record['sha256']}, got {current_sha}. Aborting apply.", file=sys.stderr)
                sys.exit(1)

            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if dest_path.exists():
                dest_sha = get_sha256(dest_path)
                if dest_sha != current_sha:
                    print(f"ERROR: Destination collision with different content at {dest_path}. Aborting.", file=sys.stderr)
                    sys.exit(1)
                else:
                    print(f"Destination already exists with identical content/hash: {dest_path}. Treating as already archived.")
                    already_archived_count += 1
                    applied_records.append({
                        "source": src_rel,
                        "archive": str(dest_path),
                        "sha256": current_sha,
                        "status": "already_archived"
                    })
            else:
                shutil.move(str(src_path), str(dest_path))
                moved_count += 1
                applied_records.append({
                    "source": src_rel,
                    "archive": str(dest_path),
                    "sha256": current_sha,
                    "status": "moved"
                })

        archive_manifest = {
            "tool_version": TOOL_VERSION,
            "original_commit": commit,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "records": applied_records
        }
        archive_manifest_path = man_archive_path / "sip_archive_manifest.json"
        archive_manifest_path.write_text(json.dumps(archive_manifest, indent=2), encoding="utf-8")

        print(f"\nSuccessfully processed {moved_count} moved, {already_archived_count} pre-existing archive records.")
        print(f"Archive manifest written to: {archive_manifest_path}")
        print("\nNOTE: Reference updates require a separate reviewed step. No automated reference rewriting was performed.")

        print("\n" + "="*60)
        print("POST-APPLY VALIDATION & MANUAL PUBLICATION GUIDANCE")
        print("="*60)
        print("To validate and stage manually, run:")
        print("  git status --short --branch")
        print("  git diff --check")
        print("  git diff --stat")
        print("  git add <exact approved files only>")
        print("  git commit -m \"chore: curate active SIP public tree\"")
        print("  git push origin main")
        print("============================================================")

if __name__ == "__main__":
    main()
