// TornBot.rs - Rust port of TornBot.py core logic
// Dependencies: serde_json, ini, rand, reqwest, rusqlite

// Version = 0.4.2

// <!-- "Imports" ----->
use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};
use ini::Ini;
use rand::seq::SliceRandom;
use rand::thread_rng;
use reqwest;
use rusqlite::{params, Connection};
use rusqlite::ToSql;
use serde_json::Value;
use chrono::Local;
use tokio::time::{sleep, Duration};

// $struct : Defines a Data Container that has no functions
struct TornBot {
    data: Value,
    config: Ini,
    keys: Vec<String>,
    config_path: PathBuf,
    db_path: String,
    usage_tracker: HashMap<String, (u64, u32)>, // key -> (last_sec, count_in_sec)
}

// $impl: Implement Method (like python class, and uses self calls)
// & self = Cannot Modify, Cannot take Ownership
// & mut self = Can Modify, Cannot take Ownership
// mut self = Can Modify, Can Take Ownership
impl TornBot {
    fn new(data_path: &str, config_path: &str, db_path: &str) -> Result<Self, Box<dyn Error>> {
        let data_str = fs::read_to_string(data_path)?;
        let data: Value = serde_json::from_str(&data_str)?;
        let config = Ini::load_from_file(config_path)?;
        let mut keys = Vec::new();
        for (sec, prop) in &config {
            for (k, v) in prop.iter() {
                if v.parse::<i64>().is_ok() {
                    keys.push(k.to_string());
                }
            }
        }
        Ok(TornBot {
            data,
            config,
            keys,
            config_path: PathBuf::from(config_path),
            db_path: db_path.to_string(),
            usage_tracker: HashMap::new(),
        })
    }

    fn get_random_key(&self) -> Result<&str, &'static str> {
        if self.keys.is_empty() {
            Err("No Keys Available")
        } else {
            Ok(self.keys.choose(&mut thread_rng()).unwrap())
        }
    }

    fn increment_key_count(&mut self, key: &str) -> Result<(), Box<dyn Error>> {
        // Enforce 50 uses/sec per key
        let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
        let entry = self.usage_tracker.entry(key.to_string()).or_insert((now, 0));
        if entry.0 == now {
            if entry.1 >= 50 {
                return Err(format!("Key '{}' exceeded 50 uses per second", key).into());
            }
            entry.1 += 1;
        } else {
            entry.0 = now;
            entry.1 = 1;
        }
        // Update keys.db used column
        let conn = Connection::open(&self.db_path)?;
        let updated = conn.execute(
            "UPDATE key_counts SET used = used + 1 WHERE key = ?1",
            params![key],
        )?;
        if updated == 0 {
            return Err(format!("Key '{}' not found in database.", key).into());
        }
        Ok(())
    }

    // Example HTTP call (GET)
    async fn call_api(&mut self, url: &str) -> Result<Value, Box<dyn Error>> {
        let apikey = self.get_random_key()?;
        let client = reqwest::Client::new();
        let resp = client.get(url)
            .header("accept", "application/json")
            .header("Authorization", format!("ApiKey {}", apikey))
            .send()
            .await?;
        if !resp.status().is_success() {
            return Err(format!("HTTP Error: {}", resp.status()).into());
        }
        let json: Value = resp.json().await?;
        self.increment_key_count(apikey)?;
        Ok(json)
    }
}

fn read_keys_from_cfg(cfg_path: &str) -> Result<Vec<String>, Box<dyn Error>> {
    let config = Ini::load_from_file(cfg_path)?;
    let mut keys = Vec::new();
    for (_sec, prop) in &config {
        for (k, v) in prop.iter() {
            // Only add if value is not 'None' and key is not 'None'
            if k != "None" && v != "None" {
                keys.push(k.to_string());
            }
        }
    }
    Ok(keys)
}

fn sync_keys_with_db(db_path: &str, keys: &[String]) -> Result<(), Box<dyn Error>> {
    let conn = Connection::open(db_path)?;
    // Ensure table exists
    conn.execute(
        "CREATE TABLE IF NOT EXISTS key_counts (
            key TEXT PRIMARY KEY,
            sec INTEGER DEFAULT 0,
            min INTEGER DEFAULT 0,
            used INTEGER DEFAULT 0
        );",
        [],
    )?;
    for key in keys {
        let mut stmt = conn.prepare("SELECT 1 FROM key_counts WHERE key = ?1 LIMIT 1")?;
        let exists = stmt.exists(params![key])?;
        if !exists {
            conn.execute(
                "INSERT INTO key_counts (key) VALUES (?1)",
                params![key],
            )?;
        }
    }
    Ok(())
}

struct PointsMarketStats {
    timestamp: String,
    volume: i64,
    small_orders: i64,
    medium_orders: i64,
    large_orders: i64,
    whale_orders: i64,
    high: i64,
    low: i64,
    marketcap: i64,
    avg_price: f64,
}

impl PointsMarketStats {
    fn insert_into_db(&self, db_path: &str) -> Result<(), Box<dyn Error>> {
        let conn = Connection::open(db_path)?;
        conn.execute(
            "CREATE TABLE IF NOT EXISTS points_market (
                timestamp TEXT PRIMARY KEY,
                volume INTEGER,
                small_orders INTEGER,
                medium_orders INTEGER,
                large_orders INTEGER,
                whale_orders INTEGER,
                high INTEGER,
                low INTEGER,
                marketcap INTEGER,
                avg_price REAL
            );",
            [],
        )?;
        conn.execute(
            "INSERT INTO points_market (timestamp, volume, small_orders, medium_orders, large_orders, whale_orders, high, low, marketcap, avg_price)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            [
                &self.timestamp as &dyn ToSql,
                &self.volume,
                &self.small_orders,
                &self.medium_orders,
                &self.large_orders,
                &self.whale_orders,
                &self.high,
                &self.low,
                &self.marketcap,
                &self.avg_price,
            ],
        )?;
        Ok(())
    }
}

async fn poll_points_market(bot: &mut TornBot, db_path: &str) -> Result<(), Box<dyn Error>> {
    loop {
        let url = "https://api.torn.com/market/?selections=pointsmarket";
        let apikey = bot.get_random_key()?;
        let full_url = format!("{}&key={}", url, apikey);
        let resp = reqwest::get(&full_url).await?;
        let json: Value = resp.json().await?;
        let pointsmarket = &json["pointsmarket"];
        if !pointsmarket.is_object() {
            eprintln!("No pointsmarket data");
            sleep(Duration::from_secs(1)).await;
            continue;
        }
        let mut volume = 0i64;
        let mut small = 0i64;
        let mut medium = 0i64;
        let mut large = 0i64;
        let mut whale = 0i64;
        let mut high = i64::MIN;
        let mut low = i64::MAX;
        let mut marketcap = 0i64;
        for (_k, v) in pointsmarket.as_object().unwrap() {
            let cost = v["cost"].as_i64().unwrap_or(0);
            let quantity = v["quantity"].as_i64().unwrap_or(0);
            let total_cost = v["total_cost"].as_i64().unwrap_or(0);
            volume += quantity;
            marketcap += total_cost;
            if cost > high { high = cost; }
            if cost < low { low = cost; }
            match quantity {
                0..=999 => {},
                1000..=2499 => medium += 1,
                2500..=4999 => large += 1,
                5000..=i64::MAX => whale += 1,
                _ => {},
            }
            if quantity < 1000 { small += 1; }
        }
        let avg_price = if volume > 0 { marketcap as f64 / volume as f64 } else { 0.0 };
        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f").to_string();
        let stats = PointsMarketStats {
            timestamp,
            volume,
            small_orders: small,
            medium_orders: medium,
            large_orders: large,
            whale_orders: whale,
            high,
            low,
            marketcap,
            avg_price,
        };
        stats.insert_into_db(db_path)?;
        sleep(Duration::from_secs(1)).await;
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Example paths (adjust as needed)
    let data_path = "../data/dat.json";
    let config_path = "../data/bot.cfg";
    let cfg_path = "keys.cfg";
    let db_path = "keys.db";
    let points_db = "points.db";
    let keys = read_keys_from_cfg(cfg_path)?;
    sync_keys_with_db(db_path, &keys)?;
    let mut bot = TornBot::new(data_path, config_path, db_path)?;
    poll_points_market(&mut bot, points_db).await?;
    Ok(())
}
