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
