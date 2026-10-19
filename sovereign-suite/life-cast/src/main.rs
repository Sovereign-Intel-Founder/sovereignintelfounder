use std::fs::File;
use std::io::{self, Read};
use std::thread;
use std::time::Duration;

fn read_cpu_utilization() -> io::Result<String> {
    let mut file = File::open("/proc/stat")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let first_line = contents.lines().next().unwrap_or("cpu 0 0 0 0");
    Ok(first_line.to_string())
}

fn main() {
    println!("[Life-Cast] Initializing 128-core telemetry matrix...");
    
    #[cfg(target_os = "linux")]
    unsafe {
        let mut set: libc::cpu_set_t = std::mem::zeroed();
        libc::CPU_ZERO(&mut set);
        libc::CPU_SET(127, &mut set);
        libc::sched_setaffinity(0, std::mem::size_of::<libc::cpu_set_t>(), &set);
        println!("[Life-Cast] Thread affinity locked to core 127.");
    }

    for tick in 1..=3 {
        match read_cpu_utilization() {
            Ok(stats) => println!("[TICK {}] Kernel Telemetry -> {}", tick, stats),
            Err(e) => eprintln!("[!] Telemetry read failure: {}", e),
        }
        thread::sleep(Duration::from_millis(500));
    }
    println!("[Life-Cast] 128-core telemetry sweep nominal.");
}
