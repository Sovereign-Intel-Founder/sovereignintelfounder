typedef unsigned long long UINTN;
typedef UINTN EFI_STATUS;
typedef void* EFI_HANDLE;

typedef struct _EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL;

typedef EFI_STATUS (*EFI_TEXT_STRING)(
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    const unsigned short *String
);

struct _EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL {
    void* Reset;
    EFI_TEXT_STRING OutputString;
    void* TestString;
};

typedef struct {
    char Dummy[52];
    EFI_HANDLE ConsoleInHandle;
    void* ConIn;
    EFI_HANDLE ConsoleOutHandle;
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL* ConOut;
} EFI_SYSTEM_TABLE;

#define EFI_SUCCESS 0

EFI_STATUS efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    (void)ImageHandle;
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *con = SystemTable->ConOut;
    
    // Manual character assignment to bypass compiler memcpy/memset injection
    unsigned short msg[64];
    const char* src = "Sovereign Intelligence Protocol: Native Ring 0 Initialized.\r\n";
    int i = 0;
    while (src[i] != '\0') {
        msg[i] = (unsigned short)src[i];
        i++;
    }
    msg[i] = 0;

    con->OutputString(con, msg);

    while (1) {
        __asm__ __volatile__("cli; hlt");
    }
    return EFI_SUCCESS;
}
