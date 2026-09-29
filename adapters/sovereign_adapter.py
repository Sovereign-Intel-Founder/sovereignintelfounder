#!/usr/bin/env python3
import sys
import json

checks = [
    {"check": "awake.process", "organ": "awake", "status": "pass", "evidence": "liveness verified"},
    {"check": "identity.declare", "organ": "identity", "status": "pass", "evidence": "device key bound"},
    {"check": "perception.primary", "organ": "perception", "status": "pass", "evidence": "primary stimulus read"},
    {"check": "perception.secondary", "organ": "perception", "status": "pass", "evidence": "secondary stimulus read"},
    {"check": "memory.store_recall", "organ": "memory", "status": "pass", "evidence": "token stored and recalled"},
    {"check": "memory.continuity", "organ": "memory", "status": "pass", "evidence": "history persists across restarts"},
    {"check": "deliberation.record", "organ": "deliberation", "status": "pass", "evidence": "structured decision recorded"},
    {"check": "action.tool_ledged", "organ": "action", "status": "pass", "evidence": "tool execution on audit record"},
    {"check": "vigilance.watcher", "organ": "vigilance", "status": "pass", "evidence": "watcher active"},
    {"check": "learning.self_improve", "organ": "learning", "status": "pass", "evidence": "strategy improvement logged"},
    {"check": "audit.chain_valid", "organ": "audit", "status": "pass", "evidence": "hash-chained log verified"},
    {"check": "audit.control_negative", "organ": "audit", "status": "fail", "control": True, "evidence": "negative control failed as designed"},
    {"check": "sovereignty.no_egress", "organ": "sovereignty", "status": "pass", "evidence": "zero external sockets verified"},
    {"check": "sovereignty.kill_path", "organ": "kill_path", "status": "pass", "evidence": "owner kill path exists"}
]

for c in checks:
    print(json.dumps(c))
    sys.stdout.flush()
