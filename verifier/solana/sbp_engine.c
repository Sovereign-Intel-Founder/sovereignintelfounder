#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <sched.h>

#define MAX_REGISTERS 16
#define MAX_INSTRUCTIONS 256
#define THREADS 64
#define CYCLES_PER_WORKER 100000

// SBP Instruction Set Architecture (ISA) Opcodes
typedef enum {
    OP_NOP = 0,
    OP_LOADI = 1,  // Load immediate value into register: R[A] = imm
    OP_ADD   = 2,  // Add registers: R[A] = R[B] + R[C]
    OP_XOR   = 3,  // Bitwise mixer/hasher: R[A] = R[B] ^ R[C]
    OP_STREAM= 4,  // Simulate zero-copy ring frame dispatch
    OP_HALT  = 255
} OpCode;

typedef struct {
    uint8_t op;
    uint8_t a;
    uint8_t b;
    uint8_t c;
    int64_t imm;
} Instruction;

typedef struct {
    Instruction code[MAX_INSTRUCTIONS];
    int length;
} Program;

typedef struct {
    int thread_id;
    Program* prog;
    int64_t accumulated_checksum;
} VMContext;

void* sbp_vm_worker(void* arg) {
    VMContext* ctx = (VMContext*)arg;

    // Pin execution thread strictly to EPYC hardware core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(ctx->thread_id % 128, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    int64_t checksum = 0;

    for (int cycle = 0; cycle < CYCLES_PER_WORKER; cycle++) {
        int64_t registers[MAX_REGISTERS] = {0};
        
        for (int ip = 0; ip < ctx->prog->length; ip++) {
            Instruction* inst = &ctx->prog->code[ip];
            switch (inst->op) {
                case OP_LOADI:
                    registers[inst->a] = inst->imm;
                    break;
                case OP_ADD:
                    registers[inst->a] = registers[inst->b] + registers[inst->c];
                    break;
                case OP_XOR:
                    registers[inst->a] = registers[inst->b] ^ registers[inst->c];
                    break;
                case OP_STREAM:
                    // Zero-copy ring transmission simulation pulse
                    registers[inst->a] += 1;
                    break;
                case OP_HALT:
                case OP_NOP:
                default:
                    break;
            }
        }
        checksum += registers[0];
    }

    ctx->accumulated_checksum = checksum;
    pthread_exit(NULL);
}

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
