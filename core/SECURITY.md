# Security Policy

## Trust Boundaries & Hardening Controls
- Local Sandbox Execution: Runtime components operate strictly within local loopback (127.0.0.1) network boundaries.
- Input Validation & Backpressure: Bounded ring buffers and telemetry parsers enforce strict capacity limits and backpressure shedding.
- Memory Safety & Sanitization: Core C routines are validated under AddressSanitizer (ASan) and UndefinedBehaviorSanitizer (UBSan).
- Architecture Cleanup: Unauthenticated remote command-execution prototypes have been purged from the active release path.

## Reporting a Vulnerability
If you discover a security flaw or memory safety issue, please open an issue or discussion within the repository.
