.code16
.global apic_trampoline_start
.global apic_trampoline_end

apic_trampoline_start:
    cli
    cld

    # Load temporary GDT for 32-bit transition
    lgdt [gdt32_ptr - apic_trampoline_start + 0x8000]

    # Enable Protected Mode in CR0
    mov %cr0, %eax
    or $1, %eax
    mov %eax, %cr0

    # Far jump into 32-bit protected mode segment
    ljmp $0x08, $protected_mode_entry

.code32
protected_mode_entry:
    # Setup data segment selectors
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss

    # Read Local APIC ID register to calculate unique per-core stack offset
    # Local APIC ID register is mapped at base 0xFEE00020 (bits 24-31)
    mov $0xFEE00020, %esi
    mov (%esi), %ebx
    shr $24, %ebx                  # EBX = Core APIC ID (0 to 127)

    # Base stack pointer: 0x90000 + (APIC_ID * 0x4000) (16KB per core stack)
    mov $0x90000, %esp
    mov %ebx, %ecx
    shl $14, %ecx                  # Multiply APIC ID by 16384 (0x4000)
    add %ecx, %esp

    # Enable Physical Address Extension (PAE) in CR4
    mov %cr4, %eax
    or $0x20, %eax
    mov %eax, %cr4

    # Load PML4 Page Table base address into CR3 (Assuming 0x100000)
    mov $0x100000, %eax
    mov %eax, %cr3

    # Enable Long Mode in EFER MSR (Model Specific Register 0xC0000080)
    mov $0xC0000080, %ecx
    rdmsr
    or $0x0100, %eax               # Set LME (Long Mode Enable) bit
    wrmsr

    # Enable Paging in CR0 to activate 64-bit Long Mode
    mov %cr0, %eax
    or $0x80000000, %eax
    mov %eax, %cr0

    # Far jump into 64-bit long mode C entry point (address 0x200000)
    ljmp $0x08, $long_mode_entry

.code64
long_mode_entry:
    # Clear data segments for 64-bit execution
    xor %ax, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss

    # Jump straight to sovereign C multi-core handler
    mov $sovereign_core_main, %rax
    call *%rax

hang_loop:
    cli
    hlt
    jmp hang_loop

# 32-bit GDT Data Structure
.align 8
gdt32:
    .quad 0x0000000000000000       # Null descriptor
    .quad 0x00cf9a000000ffff       # 32-bit flat code segment (Ring 0)
    .quad 0x00cf92000000ffff       # 32-bit flat data segment (Ring 0)
gdt32_ptr:
    .word (gdt32_ptr - gdt32 - 1)
    .long 0x8000 + (gdt32 - apic_trampoline_start)

apic_trampoline_end:
