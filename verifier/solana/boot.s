.code32
.set MULTIBOOT2_HEADER_MAGIC, 0xe85250d6
.set ARCHITECTURE_I386,        0
.set HEADER_LENGTH,           (header_end - header_start)
.set CHECKSUM,                (-(MULTIBOOT2_HEADER_MAGIC + ARCHITECTURE_I386 + HEADER_LENGTH))

.section .multiboot_header
header_start:
    .long MULTIBOOT2_HEADER_MAGIC
    .long ARCHITECTURE_I386
    .long HEADER_LENGTH
    .long CHECKSUM

    /* Multiboot2 End Tag */
    .word 0
    .word 0
    .long 8
header_end:

.section .text
.global start
start:
    cli
    mov $stack_top, %esp

    /* Store Multiboot pointer */
    push %ebx

    /* Check for Long Mode support, initialize paging, and transition to 64-bit */
    call kernel_early_setup

    /* Jump into Sovereign Ring 0 C Main */
    call sovereign_ring0_main

.hang:
    cli
    hlt
    jmp .hang

.section .bss
.align 16
stack_bottom:
    .skip 16384 /* 16KB Boot Stack */
stack_top:
