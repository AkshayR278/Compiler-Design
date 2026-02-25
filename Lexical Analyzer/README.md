# MCPP Lexical Analyzer

This is a lexical analyzer implementation for a simplified subset of cpp called **MCPP (Mini C++)** . This project is meant to demonstrate the first phase of compiler construction: lexical analysis, to convert a input program into a stream of tokens.

## Table of Contents

1. [Overview](#overview)
2. [Language Specification](#language-specification)
3. [Architecture](#architecture)
4. [Tokenization Algorithm](#tokenization-algorithm)
5. [Symbol Table Design](#symbol-table-design)
6. [Usage](#usage)
7. [Example Output](#example-output)
8. [Implementation Details](#implementation-details)

## Overview

The MCPP Lexical Analyzer is implemented in Rust and provides:

- **Regex-based tokenization** of MCPP source code
- **Position tracking** (line and column numbers) for each token
- **Error detection** with precise error reporting
- **Symbol table** for identifier tracking
- **Dual output formats**: compiler-style token stream and JSON visualization
- **Modular design** suitable for integration into a larger compiler front-end

## Language Specification

### MCPP Token Classes

#### 1. Keywords
- **Data types**: `int`, `float`, `char`, `bool`, `string`
- **Control flow**: `if`, `else`, `while`, `for`, `return`

#### 2. Preprocessor Directives
- `#include`, `#define` (not processed)

#### 3. Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Assignment**: `=`
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical**: `&&`, `||`
- **Increment/Decrement**: `++`, `--`

#### 4. Delimiters
- `;`, `,`, `(`, `)`, `{`, `}`, `[`, `]`

#### 5. Literals
- **Integer**: `123`, `456`
- **Float**: `3.14`, `2.5e10`
- **Character**: `'a'`, `'Z'`
- **String**: `"Hello, World!"`
- **Boolean**: `true`, `false`

#### 6. Comments
- **Single-line**: `// comment`
- **Multi-line**: `/* comment */`

#### 7. Identifiers
- Pattern: `[a-zA-Z_][a-zA-Z0-9_]*`
- Examples: `variable`, `myFunction`, `_temp`, `count123`

### Lexical Rules

1. **Whitespace**: Spaces, tabs, and newlines are ignored (except for position tracking)
2. **Comments**: Removed during tokenization, not included in token stream
3. **Longest match**: Multi-character operators (`==`, `++`) are matched before single-character ones (`=`, `+`)
4. **Keywords vs Identifiers**: Keywords are matched before general identifier pattern
5. **Case sensitivity**: MCPP is case-sensitive

### Component Responsibilities

1. **TokenType**: Enumeration of all possible token types in MCPP
2. **Token**: Represents a single token with type, lexeme, and position
3. **SymbolTable**: Maintains a table of identifiers with metadata
4. **Lexer**: Core tokenization engine with pattern matching

### Pattern Matching Strategy

The lexer uses **ordered pattern matching** where patterns are tried in a specific order:

1. **Comments** (multi-line, then single-line) - removed from stream
2. **String/Character literals** - prevent false matches
3. **Numeric literals** (float before integer)
4. **Multi-character operators** (before single-character)
5. **Single-character operators**
6. **Delimiters**
7. **Keywords** (before identifiers)
8. **Identifiers** (last, as fallback)

This ordering ensures:
- Longer patterns are matched before shorter ones (`==` before `=`)
- Keywords are recognized before being treated as identifiers
- Comments are removed before other processing

### Position Tracking

The lexer maintains:
- **Line number**: Incremented on `\n` characters
- **Column number**: Incremented for each character, reset to 1 on newline
- **Position**: Absolute character offset in source string

Position is tracked character-by-character to handle:
- Multi-byte characters correctly
- Escape sequences in strings
- Comments spanning multiple lines

## Symbol Table Design

The symbol table tracks identifiers encountered during lexical analysis:

### Symbol Entry Structure

```rust
struct Symbol {
    name: String,        // Identifier name
    symbol_type: String, // "variable" or "function"
    data_type: String,   // "int", "float", "char", "bool", "string", "unknown"
    scope: String,       // "global" or "local"
    line: usize,         // First occurrence line number
}
```

### Type Inference Strategy

During lexical analysis, the lexer performs **limited type inference**:

1. **Type keywords**: When a type keyword (`int`, `float`, etc.) is encountered, it's stored
2. **Identifier following type**: The next identifier uses the stored type
3. **Function detection**: Identifiers followed by `(` are marked as functions
4. **Unknown types**: Identifiers without preceding type keywords are marked as "unknown"

### Scope Tracking

Currently, the lexer uses a simplified scope model:
- **Global scope**: Default scope for all identifiers
- **Local scope**: Can be set manually (for future parsing integration)

In a complete compiler, scope would be determined during parsing by tracking `{` and `}` delimiters.


### Output Files

The lexer generates:
1. **Console output**: Token stream and symbol table
2. **JSON file**: `{filename}_tokens.json` with all tokens in JSON format

## Example Output

### Input (`examples/example1.mcpp`)

```cpp
// Example 1: Basic variable declarations
#include <iostream>

int main() {
    int x = 10;
    int y = 20;
    return 0;
}
```

### Token Stream Output

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

### Symbol Table Output

```
=== SYMBOL TABLE ===
Name            Type         Data Type    Scope      Line    
----------------------------------------------------------------------
main            function     int          global     4       
x               variable     int          global     5       
y               variable     int          global     6       
----------------------------------------------------------------------
Total symbols: 3
```

### JSON Output (`example1_tokens.json`)

```json
[
  {
    "token_type": "Include",
    "lexeme": "#include",
    "line": 2,
    "column": 1
  },
  {
    "token_type": "LeftBracket",
    "lexeme": "<",
    "line": 2,
    "column": 10
  },
  ...
]
```

## Implementation Details

### Error Handling

The lexer stops immediately upon encountering an invalid character:

```
Lexical Error: Invalid character '@' at line 5, column 12
```

## Author

Created as part of Compiler Design coursework - Year 3, Semester 6 By Akshay 353. 
