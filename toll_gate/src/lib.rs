use rusqlite::{Connection, Result};
use std::collections::HashMap;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::Arc;
use parking_lot::RwLock;

const FREE_TIER_LIMIT: u32 = 8;

#[derive(Debug, PartialEq, Eq)]
pub enum RoutingDecision {
    AllowFree,
    Trigger402PaymentRequired { toll_address: &'static str, min_toll_amount: u64 },
}

pub struct SessionTracker {
    request_count: AtomicU32,
}

impl SessionTracker {
    #[inline(always)]
    pub fn new() -> Self {
        Self {
            request_count: AtomicU32::new(0),
        }
    }

    #[inline(always)]
    pub fn evaluate(&self) -> RoutingDecision {
        let current = self.request_count.fetch_add(1, Ordering::Relaxed);
        if current < FREE_TIER_LIMIT {
            RoutingDecision::AllowFree
        } else {
            RoutingDecision::Trigger402PaymentRequired {
                toll_address: "So11111111111111111111111111111111111111112",
                min_toll_amount: 1000,
            }
        }
    }

    #[inline(always)]
    pub fn reset(&self) {
        self.request_count.store(0, Ordering::Relaxed);
    }
}

pub struct GatewayRouter {
    sessions: Arc<RwLock<HashMap<[u8; 32], Arc<SessionTracker>>>>,
}

impl GatewayRouter {
    pub fn new() -> Self {
        Self {
            sessions: Arc::new(RwLock::new(HashMap::with_capacity(1024))),
        }
    }

    #[inline]
        pub fn route_request(&self, client_id: [u8; 32]) -> RoutingDecision {
        let client_hex: String = client_id.iter().map(|b| format!("{:02x}", b)).collect();

        if check_client_deposit(&client_hex) {
            return RoutingDecision::AllowFree;
        }

        let mut sessions = self.sessions.write();
        let tracker = sessions
            .entry(client_id)
            .or_insert_with(|| Arc::new(SessionTracker::new()))
            .clone();

        tracker.evaluate()
    }
}

fn check_client_deposit(client_id_hex: &str) -> bool {
    let env_path = std::env::var("SOVEREIGN_DB_PATH").unwrap_or_else(|_| "sovereign_intel.db".to_string());
    let paths = [env_path.as_str(), "sovereign_intel.db"];
    for path in paths {
        if let Ok(conn) = Connection::open(path) {
            let mut stmt = match conn.prepare("SELECT SUM(amount_lamports) FROM processed_deposits WHERE client_id = ?1") {
                Ok(s) => s,
                Err(_) => continue,
            };
            let total: Result<Option<i64>, _> = stmt.query_row([client_id_hex], |row| row.get(0));
            if let Ok(Some(lamports)) = total {
                if lamports > 0 {
                    return true;
                }
            }
        }
    }
    false
}


#[cfg(test)]
mod tests {

    #[test]
    fn test_funded_client_bypass() {
        let router = GatewayRouter::new();
        // Matching hex string formatted client ID
        let mut client_id = [0u8; 32];
        for i in 0..32 { client_id[i] = 1; }

        // Should pass past 8 requests without 402 challenge
        for _i in 0..12 {
            let decision = router.route_request(client_id);
            assert_eq!(decision, RoutingDecision::AllowFree);
        }
    }

    use super::*;

    #[test]
    fn test_toll_gate_flow() {
        let router = GatewayRouter::new();
        let client_id = [2u8; 32];

        for _i in 0..8 {
            let decision = router.route_request(client_id);
            assert_eq!(decision, RoutingDecision::AllowFree);
        }

        let decision = router.route_request(client_id);
        match decision {
            RoutingDecision::Trigger402PaymentRequired { .. } => {},
            _ => panic!("Expected 402 payment required on 9th request"),
        }
    }
}
