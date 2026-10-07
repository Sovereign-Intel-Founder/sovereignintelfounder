use std::net::SocketAddr;
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main()-> Result<(), Box<dyn std::error::Error>> {
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    let listener = TcpListener::bind(addr).await?;
    println!("Sovereign Intelligence Protocol toll bridge active on port 8080...");

    loop {
        let (mut socket, remote_addr) = listener.accept().await?;
        println!("Incoming agent connection from: {}", remote_addr);

        tokio::spawn(async move {
            let mut buf = [0; 1024];
            match socket.read(&mut buf).await {
                Ok(n) if n > 0 => {
                    let response = "HTTP/1.1 402 Payment Required\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Payment required via Sovereign Intelligence Protocol mesh.\"}\r\n";
                    let _ = socket.write_all(response.as_bytes()).await;
                }
                _ => {}
            }
        });
    }
}
