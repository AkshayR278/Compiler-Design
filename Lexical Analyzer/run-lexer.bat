@echo off
REM MCPP Lexer - Windows run script
REM Double-click to run the lexer on example1.mcpp and see output

cd /d "%~dp0"

echo Checking for Rust...
where cargo >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Rust/cargo not found. Install from https://rustup.rs/
    echo Then close and reopen this window and run again.
    pause
    exit /b 1
)

echo Building (if needed)...
cargo build --release 2>nul
if %ERRORLEVEL% neq 0 (
    cargo build --release
    if %ERRORLEVEL% neq 0 (
        echo Build failed.
        pause
        exit /b 1
    )
)

echo.
echo ========== Running MCPP Lexer on examples/example1.mcpp ==========
echo.

cargo run --release -- examples/example1.mcpp

echo.
echo ========== Done. JSON saved to examples/example1_tokens.json ==========
echo.
pause
