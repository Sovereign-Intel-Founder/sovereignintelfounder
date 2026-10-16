#include <efi.h>
#include <efilib.h>

EFI_STATUS
EFIAPI
efi_main (EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    InitializeLib(ImageHandle, SystemTable);
    Print(L"\r\n========================================\r\n");
    Print(L"   SOVEREIGN FIRMWARE BOOT SUCCESSFUL!  \r\n");
    Print(L"========================================\r\n\r\n");
    return EFI_SUCCESS;
}
