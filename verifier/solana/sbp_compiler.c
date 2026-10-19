// SBP Compiler and Execution Harness Integration
int main() {
    printf("[*] Compiling Sovereign Bytecode (SBP) Binary Image...\n");

    Program sovereign_prog;
    sovereign_prog.length = 0;

    // Emitting low-level SBP bytecode instructions directly:
    // 1. R[1] = 42 (Initialization constant)
    sovereign_prog.code[sovereign_prog.length++] = (Instruction){OP_LOADI, 1, 0, 0, 42};
    // 2. R[2] = 100 (Iteration multiplier)
    sovereign_prog.code[sovereign_prog.length++] = (Instruction){OP_LOADI, 2, 0, 0, 100};
    // 3. R[0] = R[1] + R[2]
    sovereign_prog.code[sovereign_prog.length++] = (Instruction){OP_ADD, 0, 1, 2};
    // 4. Stream transaction buffer pulse
    sovereign_prog.code[sovereign_prog.length++] = (Instruction){OP_STREAM, 0, 0, 0, 0};
    // 5. Halt execution frame
    sovereign_prog.code[sovereign_prog.length++] = (Instruction){OP_HALT, 0, 0, 0, 0};

    printf("[+] Program compiled successfully. Instructions emitted: %d\n", sovereign_prog.length);
    printf("[*] Launching 64-Thread SBP Runtime on EPYC Topology...\n");

    pthread_t threads[THREADS];
    VMContext contexts[THREADS];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < THREADS; i++) {
        contexts[i].thread_id = i;
        contexts[i].prog = &sovereign_prog;
        contexts[i].accumulated_checksum = 0;
        pthread_create(&threads[i], NULL, sbp_vm_worker, &contexts[i]);
    }

    int64_t total_checksum = 0;
    for (int i = 0; i < THREADS; i++) {
        pthread_join(threads[i], NULL);
        total_checksum += contexts[i].accumulated_checksum;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    long total_ops = (long)THREADS * CYCLES_PER_WORKER * sovereign_prog.length;

    printf("\n[+] ==========================================\n");
    printf("[+] SBP VIRTUAL MACHINE EXECUTION COMPLETE\n");
    printf("[+] Global Checksum Verification: %ld\n", total_checksum);
    printf("[+] Total Instructions Processed: %ld\n", total_ops);
    printf("[+] Duration: %.4f seconds\n", elapsed);
    printf("[+] SBP Bytecode Throughput: %.2f million inst/sec\n", (total_ops / elapsed) / 1e6);
    printf("[+] ==========================================\n");

    return 0;
}
