# Glossary & Engineering Terminology

- **SPSC (Single-Producer Single-Consumer):** A lock-free ring buffer queue pattern optimized for exactly one thread writing and one thread reading, eliminating cross-core lock contention.
- **Lock-free:** A concurrency property ensuring that shared resource access guarantees progress for at least one thread across execution steps, avoiding blocking mutexes.
- **Atomic operation:** An operation that executes as a single, indivisible unit of work visible instantaneously to other execution threads.
- **Backpressure:** The mechanism used when incoming work exceeds processing capacity. The system may block producers, reject work, drop work, or apply another explicitly documented policy.
- **Queue capacity:** The bounded maximum number of items a buffer can hold before load-shedding or blocking triggers.
- **Upstream dependency:** An external service, socket, or feed providing input data to the ingestion pipeline.
- **Failure domain:** The structural boundary within which a system fault or exception is contained, preventing cascading failures across unrelated subsystems.
- **Loopback:** A network interface (`127.0.0.1`) restricted entirely to the local host, preventing external network exposure.
- **Authentication:** The cryptographic or credential-based verification of an actor's identity.
- **Authorization:** The verification of whether an authenticated actor has permissions to execute a specific action.
- **Shell injection:** A vulnerability where untrusted input is passed directly to a system shell interpreter, allowing arbitrary command execution.
- **Simulation:** A local operational state utilizing synthetic or locally generated inputs rather than live external effects.
- **Settlement:** A finalized state transition recording a transaction outcome. In this project, settlement is simulation-only.
- **Throughput:** The number of completed operations per unit of time under a defined workload. Must be interpreted alongside latency and error telemetry.
- **Latency (p50/p95/p99):** The time duration between event ingestion and processing completion at the 50th, 95th, and 99th percentile distributions.
