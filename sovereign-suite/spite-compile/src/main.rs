use std::fs;
use std::io;
use std::env;
use goblin::elf::Elf;

const TRAP_PAYLOAD: &[u8] = &[0xCC, 0x90, 0xEB, 0xFE]; // INT3, NOP, JMP SELF

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: spite-compile <path/to/binary>");
        std::process::exit(1);
    }

    let path = &args[1];
    let buffer = fs::read(path)?;

    // Rigorous structural ELF parsing
    let elf = Elf::parse(&buffer).map_err(|e| {
        io::Error::new(io::ErrorKind::InvalidData, format!("Invalid ELF structure: {}", e))
    })?;

    println!("[SpiteCompile] Rigorous ELF inspection passed. Entry point: {:#x}", elf.entry);

    let mut modified = buffer.clone();
    let mut target_offset = 0;

    // Locate the executable segment (.text boundary) for safe insertion
    for ph in &elf.program_headers {
        if ph.p_type == goblin::elf::program_header::PT_LOAD && (ph.p_flags & goblin::elf::program_header::PF_X) != 0 {
            target_offset = (ph.p_offset + ph.p_filesz) as usize;
            break;
        }
    }

    if target_offset > 0 && target_offset < modified.len() {
        println!("[SpiteCompile] Injecting disassembler trap sequence into executable segment at {:#x}", target_offset);
        modified.splice(target_offset..target_offset, TRAP_PAYLOAD.iter().cloned());
    } else {
        eprintln!("[!] Error: Could not resolve safe executable segment boundary.");
        std::process::exit(1);
    }

    let armored_path = format!("{}.armored", path);
    fs::write(&armored_path, &modified)?;

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&armored_path, fs::Permissions::from_mode(0o755))?;
    }

    println!("[SpiteCompile] Hardened armoring complete. Output written to: {}", armored_path);
    Ok(())
}
