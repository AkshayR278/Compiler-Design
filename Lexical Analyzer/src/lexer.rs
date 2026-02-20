use regex::Regex;
use serde::{Deserialize, Serialize};

/// Token types for MCPP language
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum TokenType {
    // Keywords
    Int,
    Float,
    Char,
    Bool,
    String,
    If,
    Else,
    While,
    For,
    Return,
    
    // Preprocessor
    Include,
    Define,
    
    // Operators
    Plus,           // +
    Minus,          // -
    Multiply,       // *
    Divide,         // /
    Modulo,         // %
    Assign,         // =
    Equal,          // ==
    NotEqual,       // !=
    LessThan,       // <
    GreaterThan,    // >
    LessEqual,      // <=
    GreaterEqual,   // >=
    LogicalAnd,     // &&
    LogicalOr,      // ||
    Increment,       // ++
    Decrement,      // --
    
    // Delimiters
    Semicolon,      // ;
    Comma,          // ,
    LeftParen,      // (
    RightParen,     // )
    LeftBrace,      // {
    RightBrace,     // }
    LeftBracket,    // [
    RightBracket,   // ]
    
    // Literals
    IntegerLiteral,
    FloatLiteral,
    CharLiteral,
    StringLiteral,
    BoolLiteral,
    
    // Identifiers
    Identifier,
    
    // Special
    Comment,
    EOF,
}

/// Token representation with position information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Token {
    pub token_type: TokenType,
    pub lexeme: String,
    pub line: usize,
    pub column: usize,
}

impl Token {
    pub fn new(token_type: TokenType, lexeme: String, line: usize, column: usize) -> Self {
        Token {
            token_type,
            lexeme,
            line,
            column,
        }
    }
    
    /// Format token as compiler-style output: <TOKEN_TYPE, LEXEME, LINE, COLUMN>
    pub fn to_compiler_format(&self) -> String {
        format!("<{:?}, {}, {}, {}>", self.token_type, self.lexeme, self.line, self.column)
    }
}

/// Symbol entry in the symbol table
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Symbol {
    pub name: String,
    pub symbol_type: String,  // "variable", "function"
    pub data_type: String,     // "int", "float", "char", "bool", "string", "function"
    pub scope: String,         // "global", "local"
    pub line: usize,
}

/// Symbol table for tracking identifiers
#[derive(Debug, Clone)]
pub struct SymbolTable {
    symbols: Vec<Symbol>,
    current_scope: String,
}

impl SymbolTable {
    pub fn new() -> Self {
        SymbolTable {
            symbols: Vec::new(),
            current_scope: "global".to_string(),
        }
    }
    
    /// Add a symbol to the table
    pub fn add_symbol(&mut self, name: String, symbol_type: String, data_type: String, line: usize) {
        let scope = self.current_scope.clone();
        let symbol = Symbol {
            name,
            symbol_type,
            data_type,
            scope,
            line,
        };
        self.symbols.push(symbol);
    }
    
    /// Set the current scope (for future symbols)
    pub fn set_scope(&mut self, scope: String) {
        self.current_scope = scope;
    }
    
    /// Get all symbols
    pub fn get_symbols(&self) -> &Vec<Symbol> {
        &self.symbols
    }
    
    /// Print symbol table in formatted output
    pub fn print(&self) {
        println!("\n=== SYMBOL TABLE ===");
        println!("{:<15} {:<12} {:<12} {:<10} {:<8}", "Name", "Type", "Data Type", "Scope", "Line");
        println!("{}", "-".repeat(70));
        for symbol in &self.symbols {
            println!("{:<15} {:<12} {:<12} {:<10} {:<8}", 
                symbol.name, 
                symbol.symbol_type, 
                symbol.data_type, 
                symbol.scope, 
                symbol.line
            );
        }
        println!("{}", "-".repeat(70));
        println!("Total symbols: {}", self.symbols.len());
    }
}

/// Lexical analyzer for MCPP language
pub struct Lexer {
    source: String,
    position: usize,
    line: usize,
    column: usize,
    tokens: Vec<Token>,
    symbol_table: SymbolTable,
    patterns: Vec<(TokenType, Regex)>,
    last_type_keyword: Option<String>,  // Track last seen type keyword for symbol table
}

impl Lexer {
    /// Create a new lexer instance
    pub fn new(source: String) -> Self {
        let mut lexer = Lexer {
            source,
            position: 0,
            line: 1,
            column: 1,
            tokens: Vec::new(),
            symbol_table: SymbolTable::new(),
            patterns: Vec::new(),
            last_type_keyword: None,
        };
        lexer.initialize_patterns();
        lexer
    }
    
    /// Initialize regex patterns for tokenization
    /// Order matters: more specific patterns should come first
    fn initialize_patterns(&mut self) {
        // Multi-line comment (must come before single-line comment)
        self.patterns.push((
            TokenType::Comment,
            Regex::new(r"(?s)/\*.*?\*/").unwrap()
        ));
        
        // Single-line comment
        self.patterns.push((
            TokenType::Comment,
            Regex::new(r"//.*").unwrap()
        ));
        
        // String literals (with escape sequences)
        self.patterns.push((
            TokenType::StringLiteral,
            Regex::new(r#""([^"\\]|\\.)*""#).unwrap()
        ));
        
        // Character literals
        self.patterns.push((
            TokenType::CharLiteral,
            Regex::new(r"'([^'\\]|\\.)'").unwrap()
        ));
        
        // Float literals (must come before integer literals)
        self.patterns.push((
            TokenType::FloatLiteral,
            Regex::new(r"\d+\.\d+([eE][+-]?\d+)?").unwrap()
        ));
        
        // Integer literals
        self.patterns.push((
            TokenType::IntegerLiteral,
            Regex::new(r"\d+").unwrap()
        ));
        
        // Bool literals
        self.patterns.push((
            TokenType::BoolLiteral,
            Regex::new(r"\b(true|false)\b").unwrap()
        ));
        
        // Multi-character operators (must come before single-character)
        self.patterns.push((
            TokenType::LogicalAnd,
            Regex::new(r"&&").unwrap()
        ));
        self.patterns.push((
            TokenType::LogicalOr,
            Regex::new(r"\|\|").unwrap()
        ));
        self.patterns.push((
            TokenType::Equal,
            Regex::new(r"==").unwrap()
        ));
        self.patterns.push((
            TokenType::NotEqual,
            Regex::new(r"!=").unwrap()
        ));
        self.patterns.push((
            TokenType::LessEqual,
            Regex::new(r"<=").unwrap()
        ));
        self.patterns.push((
            TokenType::GreaterEqual,
            Regex::new(r">=").unwrap()
        ));
        self.patterns.push((
            TokenType::Increment,
            Regex::new(r"\+\+").unwrap()
        ));
        self.patterns.push((
            TokenType::Decrement,
            Regex::new(r"--").unwrap()
        ));
        
        // Single-character operators
        self.patterns.push((
            TokenType::Plus,
            Regex::new(r"\+").unwrap()
        ));
        self.patterns.push((
            TokenType::Minus,
            Regex::new(r"-").unwrap()
        ));
        self.patterns.push((
            TokenType::Multiply,
            Regex::new(r"\*").unwrap()
        ));
        self.patterns.push((
            TokenType::Divide,
            Regex::new(r"/").unwrap()
        ));
        self.patterns.push((
            TokenType::Modulo,
            Regex::new(r"%").unwrap()
        ));
        self.patterns.push((
            TokenType::Assign,
            Regex::new(r"=").unwrap()
        ));
        self.patterns.push((
            TokenType::LessThan,
            Regex::new(r"<").unwrap()
        ));
        self.patterns.push((
            TokenType::GreaterThan,
            Regex::new(r">").unwrap()
        ));
        
        // Delimiters
        self.patterns.push((
            TokenType::Semicolon,
            Regex::new(r";").unwrap()
        ));
        self.patterns.push((
            TokenType::Comma,
            Regex::new(r",").unwrap()
        ));
        self.patterns.push((
            TokenType::LeftParen,
            Regex::new(r"\(").unwrap()
        ));
        self.patterns.push((
            TokenType::RightParen,
            Regex::new(r"\)").unwrap()
        ));
        self.patterns.push((
            TokenType::LeftBrace,
            Regex::new(r"\{").unwrap()
        ));
        self.patterns.push((
            TokenType::RightBrace,
            Regex::new(r"\}").unwrap()
        ));
        self.patterns.push((
            TokenType::LeftBracket,
            Regex::new(r"\[").unwrap()
        ));
        self.patterns.push((
            TokenType::RightBracket,
            Regex::new(r"\]").unwrap()
        ));
        
        // Keywords (must come before identifiers)
        self.patterns.push((
            TokenType::Include,
            Regex::new(r"\b#include\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Define,
            Regex::new(r"\b#define\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Int,
            Regex::new(r"\bint\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Float,
            Regex::new(r"\bfloat\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Char,
            Regex::new(r"\bchar\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Bool,
            Regex::new(r"\bbool\b").unwrap()
        ));
        self.patterns.push((
            TokenType::String,
            Regex::new(r"\bstring\b").unwrap()
        ));
        self.patterns.push((
            TokenType::If,
            Regex::new(r"\bif\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Else,
            Regex::new(r"\belse\b").unwrap()
        ));
        self.patterns.push((
            TokenType::While,
            Regex::new(r"\bwhile\b").unwrap()
        ));
        self.patterns.push((
            TokenType::For,
            Regex::new(r"\bfor\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Return,
            Regex::new(r"\breturn\b").unwrap()
        ));
        
        // Identifiers (must come last)
        self.patterns.push((
            TokenType::Identifier,
            Regex::new(r"[a-zA-Z_][a-zA-Z0-9_]*").unwrap()
        ));
    }
    
    /// Skip whitespace and update position
    fn skip_whitespace(&mut self) {
        while self.position < self.source.len() {
            let ch = self.source.chars().nth(self.position).unwrap();
            if ch == '\n' {
                self.line += 1;
                self.column = 1;
                self.position += 1;
            } else if ch.is_whitespace() {
                self.column += 1;
                self.position += 1;
            } else {
                break;
            }
        }
    }
    
    /// Check if a keyword matches and return the appropriate token type
    fn check_keyword(&self, lexeme: &str) -> Option<TokenType> {
        match lexeme {
            "int" => Some(TokenType::Int),
            "float" => Some(TokenType::Float),
            "char" => Some(TokenType::Char),
            "bool" => Some(TokenType::Bool),
            "string" => Some(TokenType::String),
            "if" => Some(TokenType::If),
            "else" => Some(TokenType::Else),
            "while" => Some(TokenType::While),
            "for" => Some(TokenType::For),
            "return" => Some(TokenType::Return),
            "#include" => Some(TokenType::Include),
            "#define" => Some(TokenType::Define),
            _ => None,
        }
    }
    
    /// Determine data type from token type
    fn get_data_type(&self, token_type: &TokenType) -> Option<String> {
        match token_type {
            TokenType::Int => Some("int".to_string()),
            TokenType::Float => Some("float".to_string()),
            TokenType::Char => Some("char".to_string()),
            TokenType::Bool => Some("bool".to_string()),
            TokenType::String => Some("string".to_string()),
            _ => None,
        }
    }
    
    /// Tokenize the source code
    pub fn tokenize(&mut self) -> Result<(), String> {
        while self.position < self.source.len() {
            self.skip_whitespace();
            
            if self.position >= self.source.len() {
                break;
            }
            
            let mut matched = false;
            let start_pos = self.position;
            let start_line = self.line;
            let start_col = self.column;
            
            // Try to match each pattern
            for (token_type, pattern) in &self.patterns {
                // Create a substring from current position
                let remaining = &self.source[self.position..];
                
                if let Some(mat) = pattern.find(remaining) {
                    // Check if match starts at position 0 (beginning of remaining string)
                    if mat.start() == 0 {
                        let lexeme = mat.as_str().to_string();
                        
                        // Skip comments (don't add them to token stream)
                        if *token_type == TokenType::Comment {
                            // Update position and column
                            for ch in lexeme.chars() {
                                if ch == '\n' {
                                    self.line += 1;
                                    self.column = 1;
                                } else {
                                    self.column += 1;
                                }
                                self.position += 1;
                            }
                            matched = true;
                            break;
                        }
                        
                        // Create token
                        let mut final_token_type = token_type.clone();
                        
                        // Check if it's a type keyword (store for next identifier)
                        if let Some(data_type) = self.get_data_type(token_type) {
                            self.last_type_keyword = Some(data_type);
                        }
                        
                        // Check if identifier is actually a keyword
                        if *token_type == TokenType::Identifier {
                            if let Some(keyword_type) = self.check_keyword(&lexeme) {
                                final_token_type = keyword_type;
                                // Reset type keyword if it was a control keyword
                                match keyword_type {
                                    TokenType::If | TokenType::Else | TokenType::While | 
                                    TokenType::For | TokenType::Return => {
                                        self.last_type_keyword = None;
                                    }
                                    _ => {}
                                }
                            } else {
                                // Add identifier to symbol table
                                // Use last seen type keyword if available
                                let data_type = self.last_type_keyword.clone().unwrap_or_else(|| "unknown".to_string());
                                
                                // Note: Function detection requires parsing (checking if identifier
                                // is followed by '('). For lexical analysis, we mark all as variables.
                                // A parser would determine if it's actually a function.
                                let symbol_type = "variable".to_string();
                                
                                self.symbol_table.add_symbol(
                                    lexeme.clone(),
                                    symbol_type,
                                    data_type,
                                    start_line,
                                );
                                // Reset after using
                                self.last_type_keyword = None;
                            }
                        }
                        
                        let token = Token::new(
                            final_token_type,
                            lexeme.clone(),
                            start_line,
                            start_col,
                        );
                        
                        self.tokens.push(token);
                        
                        // Update position
                        for ch in lexeme.chars() {
                            if ch == '\n' {
                                self.line += 1;
                                self.column = 1;
                            } else {
                                self.column += 1;
                            }
                            self.position += 1;
                        }
                        
                        matched = true;
                        break;
                    }
                }
            }
            
            if !matched {
                // Invalid token found
                let ch = self.source.chars().nth(self.position).unwrap();
                return Err(format!(
                    "Lexical Error: Invalid character '{}' at line {}, column {}",
                    ch, self.line, self.column
                ));
            }
        }
        
        // Add EOF token
        self.tokens.push(Token::new(
            TokenType::EOF,
            "EOF".to_string(),
            self.line,
            self.column,
        ));
        
        Ok(())
    }
    
    /// Get all tokens
    pub fn get_tokens(&self) -> &Vec<Token> {
        &self.tokens
    }
    
    /// Get symbol table
    pub fn get_symbol_table(&self) -> &SymbolTable {
        &self.symbol_table
    }
    
    /// Print token stream in compiler format
    pub fn print_token_stream(&self) {
        println!("\n=== TOKEN STREAM ===");
        for token in &self.tokens {
            println!("{}", token.to_compiler_format());
        }
    }
    
    /// Generate JSON output
    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(&self.tokens).unwrap()
    }
}
