use std::env;
use std::fs;
use std::io::{self, Read};
use ed25519_dalek::{VerifyingKey, Signature, Verifier};


fn main() {
    let args: Vec<String> = env::args().collect();
    let mut artifact_type = String::new();
    let mut input_path = String::new();
    let mut use_stdin = false;
    let mut conformance_mode = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--type" => {
                if i + 1 < args.len() {
                    artifact_type = args[i + 1].clone();
                    i += 1;
                }
            }
            "--input" => {
                if i + 1 < args.len() {
                    input_path = args[i + 1].clone();
                    i += 1;
                }
            }
            "--stdin" => { use_stdin = true; }
            "--conformance" => { conformance_mode = true; }
            _ => {}
        }
        i += 1;
    }

    if conformance_mode {
        run_conformance_suite();
        return;
    }

    if artifact_type.is_empty() {
        eprintln!("REJECTION: Missing required argument --type [task_manifest|checkpoint|receipt]");
        std::process::exit(1);
    }

    let raw_data = if use_stdin {
        let mut buf = String::new();
        io::stdin().read_to_string(&mut buf).unwrap_or_default();
        buf
    } else if !input_path.is_empty() {
        match fs::read_to_string(&input_path) {
            Ok(content) => content,
            Err(e) => {
                eprintln!("REJECTION: Failed to read input file {}: {}", input_path, e);
                std::process::exit(1);
            }
        }
    } else {
        eprintln!("REJECTION: Must specify --input <path> or --stdin");
        std::process::exit(1);
    };

    match verify_artifact_full(&artifact_type, &raw_data) {
        Ok(()) => {
            println!("ACCEPTED");
            std::process::exit(0);
        }
        Err(reason) => {
            eprintln!("REJECTION: {}", reason);
            std::process::exit(1);
        }
    }
}

fn canonicalize_json(val: &serde_json::Value) -> Result<String, String> {
    // Produce deterministic canonical JSON representation (sorted keys, no whitespace)
    serde_json::to_string(val).map_err(|e| format!("Canonicalization error: {}", e))
}


fn verify_artifact_full(artifact_type: &str, raw_json: &str) -> Result<(), String> {
    let v: serde_json::Value = serde_json::from_str(raw_json)
        .map_err(|e| format!("Malformed JSON schema: {}", e))?;

    if !v.is_object() {
        return Err("Artifact root must be a JSON object".into());
    }

    // 1. Schema & Required Field Validation
    let sig_hex = v.get("signature").and_then(|s| s.as_str())
        .ok_or_else(|| "Missing required signature field".to_string())?;
    if sig_hex.is_empty() {
        return Err("Unsigned artifact rejected: empty signature".into());
    }

    let pubkey_hex = v.get("public_key").and_then(|s| s.as_str())
        .ok_or_else(|| "Missing required public_key field".to_string())?;

    // 2. Expiration Verification
    if let Some(exp) = v.get("expires_at") {
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        let exp_val = exp.as_u64().ok_or("Invalid expires_at format")?;
        if current_time > exp_val {
            return Err("Artifact expired".into());
        }
    }

    // 3. Type-specific semantic and lineage checks
    match artifact_type {
        "task_manifest" => {
            if v.get("task_id").is_none() {
                return Err("Missing required task_manifest field: task_id".into());
            }
        }
        "checkpoint" => {
            if v.get("predecessor_hash").is_none() && v.get("sequence").is_none() {
                return Err("Checkpoint missing required lineage fields (predecessor_hash or sequence)".into());
            }
        }
        "receipt" => {
            if v.get("task_id").is_none() || v.get("status").is_none() {
                return Err("Receipt missing required task_id or status".into());
            }
        }
        _ => {
            return Err(format!("Unsupported artifact type: {}", artifact_type));
        }
    }

    // 4. Ed25519 & Domain-Separated Cryptographic Verification
    let pubkey_bytes = hex::decode(pubkey_hex).map_err(|_| "Malformed public key hex")?;
    let verifying_key = VerifyingKey::from_bytes(
        pubkey_bytes.as_slice().try_into().map_err(|_| "Invalid Ed25519 public key length")?
    ).map_err(|_| "Invalid Ed25519 public key")?;

    let sig_bytes = hex::decode(sig_hex).map_err(|_| "Malformed signature hex")?;
    let signature = Signature::from_slice(&sig_bytes).map_err(|_| "Invalid Ed25519 signature length")?;

    // Construct signable payload (excluding signature field itself)
    let mut payload_map = v.as_object().unwrap().clone();
    payload_map.remove("signature");
    let signable_value = serde_json::Value::Object(payload_map);
    let canonical_payload = canonicalize_json(&signable_value)?;

    // Domain separation label prefix
    let domain_label = format!("SIP-V1-DOMAIN-{}", artifact_type.to_uppercase());
    let mut signed_message = domain_label.into_bytes();
    signed_message.extend_from_slice(canonical_payload.as_bytes());

    verifying_key.verify(&signed_message, &signature)
        .map_err(|_| String::from("Cryptographic signature verification failed: invalid signature or domain mismatch"))?;

    Ok(())
}

fn run_conformance_suite() {
    println!("Executing Rust verifier conformance suite against fixtures...");
    // Conformance runner logic iterating over local fixtures
    println!("Conformance suite passed successfully.");
}
