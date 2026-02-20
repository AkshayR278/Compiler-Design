# Quick Start Guide

## Building and Running

### Prerequisites
- Install Rust from [rustup.rs](https://rustup.rs/)
- After installing, **close and reopen** your terminal (or VS Code) so `cargo` is in PATH

---

## Testing on Windows

### Option 1: Run from terminal (PowerShell or CMD)

1. **Open a terminal** in the project folder:
   - In VS Code: **Terminal → New Terminal** (or `` Ctrl+` ``)
   - Or: open **PowerShell** or **Command Prompt**, then:
     ```powershell
     cd "C:\Users\aksha\Documents\Studies\Clg\Year 3\SEM 6\Projects\Compiler-Design\Lexical Analyzer"
     ```

2. **Build** (first time only):
   ```powershell
   cargo build --release
   ```

3. **Run the lexer** on an example file. Output appears in the same terminal:
   ```powershell
   cargo run --release -- examples/example1.mcpp
   ```
   Or using the compiled `.exe`:
   ```powershell
   .\target\release\mcpp-lexer.exe examples/example1.mcpp
   ```

4. **What you’ll see:**
   - **Token stream** and **symbol table** printed in the terminal
   - A **JSON file** created next to your source: `examples/example1_tokens.json`

### Option 2: Double-click script (no terminal know-how needed)

1. In the project folder, double-click **`run-lexer.bat`**.
2. It runs the lexer on `examples/example1.mcpp` and **pauses** so you can read the output.
3. Press any key to close the window.

### Option 3: Run on your own file

```powershell
cargo run --release -- "path\to\your\file.mcpp"
```

Example:
```powershell
cargo run --release -- "C:\Users\aksha\myprogram.mcpp"
```

---

### Where is the output?

| Output | Where it appears |
|--------|-------------------|
| Token stream | In the terminal (scroll to see all) |
| Symbol table | In the terminal, right after the token stream |
| JSON tokens | File: `examples\<name>_tokens.json` (same folder as the `.mcpp` file you passed) |

To **save terminal output** to a file on Windows:
```powershell
cargo run --release -- examples/example1.mcpp | Out-File -FilePath output.txt
```
Then open `output.txt` in the project folder.

---

## Building and Running (all platforms)

### Build
```bash
cargo build --release
```

### Run
```bash
# Run on example file
cargo run --release examples/example1.mcpp

# Windows: use .exe
.\target\release\mcpp-lexer.exe examples/example1.mcpp

# Linux/Mac: use no extension
./target/release/mcpp-lexer examples/example1.mcpp
```

## Example Usage

### Input File: `examples/example1.mcpp`
```cpp
// Example 1: Basic variable declarations
#include <iostream>

int main() {
    int x = 10;
    int y = 20;
    return 0;
}
```

### Expected Output

**Token Stream:**
```
=== TOKEN STREAM ===
<Include, #include, 2, 1>
<LeftBracket, <, 2, 10>
<Identifier, iostream, 2, 11>
<RightBracket, >, 2, 19>
<Int, int, 4, 1>
<Identifier, main, 4, 5>
<LeftParen, (, 4, 9>
<RightParen, ), 4, 10>
<LeftBrace, {, 4, 12>
<Int, int, 5, 5>
<Identifier, x, 5, 9>
<Assign, =, 5, 11>
<IntegerLiteral, 10, 5, 13>
<Semicolon, ;, 5, 15>
<Int, int, 6, 5>
<Identifier, y, 6, 9>
<Assign, =, 6, 11>
<IntegerLiteral, 20, 6, 13>
<Semicolon, ;, 6, 15>
<Return, return, 7, 5>
<IntegerLiteral, 0, 7, 12>
<Semicolon, ;, 7, 13>
<RightBrace, }, 8, 1>
<EOF, EOF, 8, 2>
```

**Symbol Table:**
```
=== SYMBOL TABLE ===
Name            Type         Data Type    Scope      Line    
----------------------------------------------------------------------
main            variable     int          global     4       
x               variable     int          global     5       
y               variable     int          global     6       
----------------------------------------------------------------------
Total symbols: 3
```

**JSON Output:** Saved to `example1_tokens.json`

## Testing Different Examples

```bash
# Test control flow
cargo run --release examples/example2.mcpp

# Test functions and operators
cargo run --release examples/example3.mcpp

# Test complex program
cargo run --release examples/example4.mcpp
```

## Error Handling

If the lexer encounters an invalid character, it will report:

```
Lexical Error: Invalid character '@' at line 5, column 12
```

The lexer stops immediately upon encountering an error.
