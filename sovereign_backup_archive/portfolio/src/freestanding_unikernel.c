/* Freestanding Unikernel Entry Point (No OS/libc dependencies) */
typedef unsigned long size_t;

void kernel_main(void) {
    volatile unsigned short *vga_buffer = (volatile unsigned short *)0xB8000;
    const char *msg = "SOVEREIGN UNIKERNEL BOOTED";
    for (int i = 0; msg[i] != '\0'; i++) {
        vga_buffer[i] = (0x0A << 8) | msg[i]; // Bright Green text
    }
    while (1) {
        __asm__ __volatile__("hlt");
    }
}
