# Kinetic Capsule Conformance

**Classification:** KINETIC PROOF-CARRYING COMPUTATION — INDEPENDENT-IMPLEMENTATION VERIFICATION

## Overview
Provides a standalone Python verifier that evaluates static test fixtures and adversarial mutation matrices. Includes semantic adversarial testing against artifacts validly signed by an authorized key.

## Scope & Limitations
- Independently implemented Python verifier.
- This is NOT cross-language verification. Rust or WebAssembly verifier implementations are designated as future work.
- Demonstrates that signatures alone do not prove computation correctness; independent state, commitment, and lineage checks are strictly required.

## Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Execution Instructions
\`\`\`bash
python3 kinetic_capsule_conformance/generate_fixtures.py
python3 kinetic_capsule_conformance/independent_verifier.py kinetic_capsule_conformance/fixtures
python3 kinetic_capsule_conformance/semantic_audit.py
\`\`\`
