@echo off
REM Build and run the TornBot Rust project
cargo build --release
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
cargo run --release
