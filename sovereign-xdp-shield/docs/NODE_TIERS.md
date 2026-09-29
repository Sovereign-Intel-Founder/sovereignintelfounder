# Sovereign Intelligence Protocol - Node Tiers

To maximize network resilience and accessibility, the protocol supports three distinct deployment tiers:

1. **Tier 1: Core Bare-Metal Anchor (`deploy_core.sh`)**
   - **Target:** High-performance enterprise hardware (e.g., 128-Core EPYC in Ashburn, VA).
   - **Mode:** Native XDP driver-level packet filtering and zero-copy ingestion.
2. **Tier 2: Standard Cloud VPS Node (`deploy_vps.sh`)**
   - **Target:** Standard virtual private servers (2GB to 4GB RAM).
   - **Mode:** Generic SKB fallback mode for multi-tenant virtualized network interfaces.
3. **Tier 3: Edge & Dev Node (`deploy_edge.sh`)**
   - **Target:** Local development laptops or lightweight edge devices.
   - **Mode:** Simulation and lightweight telemetry streaming for local testing.
