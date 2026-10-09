# Kinetic Capsule PoC V2

**Classification:** KINETIC PROOF-CARRYING COMPUTATION — LOCAL PROCESS-BOUNDARY RESEARCH PROTOTYPE

## Overview
Demonstrates process-boundary separation between Cell A and Cell B, where Cell A terminates completely after step 500, and Cell B spawns independently to resume execution through step 1,000 using Ed25519-signed checkpoints and receipt lineage checks.

## Scope & Limitations
- Carries explicit serialized application state only.
- Does NOT migrate process memory or live call stacks.
- Local processes only; no remote process execution or networking.

## Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Execution Instructions
\`\`\`bash
python3 kinetic_capsule_poc_v2/demo_controller.py
\`\`\`
