# Submodules & External References

## Overview

The Sovereign Intelligence Protocol (SIP) repository maintains a reference to the `sovereign-intelligence` submodule directory. 

## Current Repository State

* **Git Link Type:** Incomplete / Orphaned Gitlink (`160000` entry at commit `4bad840...`).
* **Configuration:** No `.gitmodules` mapping is currently present in the root of the public repository.
* **Parent Repository Independence:** The core SIP repository (specifications, atomic SPSC ring buffers, and native tick-to-trade benchmarks) is independently structured and does not strictly require the unmapped submodule for baseline protocol review or local verification.

## Handling & Recommendations

* Do not attempt automatic recursive submodule initialization unless a valid public URL is mapped in `.gitmodules`.
* Core native benchmarks and protocol schemas reside directly within the main repository paths.
