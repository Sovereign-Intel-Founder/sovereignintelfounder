# Kinetic Capsule PoC

**Classification:** KINETIC PROOF-CARRYING COMPUTATION — LOCAL IN-PROCESS FEASIBILITY PROTOTYPE

## Overview
Demonstrates single-process state migration and checkpoint verification using canonical JSON serialization, SHA-256 state commitments, and Ed25519 cryptographic signatures.

## Scope & Limitations
- Carries explicit serialized application state only.
- Does NOT migrate arbitrary process memory or live call stacks.
- Does NOT self-replicate, scan network hosts, or execute wallet/payment logic.
- Uses local authorized cells only. Not production infrastructure.

## Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Execution Instructions
\`\`\`bash
python3 kinetic_capsule_poc/demo.py
\`\`\`
