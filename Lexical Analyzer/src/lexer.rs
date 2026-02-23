use regex::Regex;
use serde::{Deserialize, Serialize};

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
    
    pub fn to_compiler_format(&self) -> String {
        format!("<{:?}, {}, {}, {}>", self.token_type, self.lexeme, self.line, self.column)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Symbol {
    pub name: String,
    pub symbol_type: String,
    pub data_type: String,   
    pub scope: String,        
    pub line: usize,
}

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
    
    #[allow(dead_code)]
    pub fn set_scope(&mut self, scope: String) {
        self.current_scope = scope;
    }
    
    #[allow(dead_code)]
    pub fn get_symbols(&self) -> &Vec<Symbol> {
        &self.symbols
    }
    
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

pub struct Lexer {
    source: String,
    position: usize,
    line: usize,
    column: usize,
    tokens: Vec<Token>,
    symbol_table: SymbolTable,
    patterns: Vec<(TokenType, Regex)>,
    last_type_keyword: Option<String>,
}

impl Lexer {
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
    

    fn initialize_patterns(&mut self) {
        self.patterns.push((
            TokenType::Comment,
            Regex::new(r"(?s)/\*.*?\*/").unwrap()
        ));
        
        self.patterns.push((
            TokenType::Comment,
            Regex::new(r"//.*").unwrap()
        ));
        
        self.patterns.push((
            TokenType::StringLiteral,
            Regex::new(r#""([^"\\]|\\.)*""#).unwrap()
        ));
        
        self.patterns.push((
            TokenType::CharLiteral,
            Regex::new(r"'([^'\\]|\\.)'").unwrap()
        ));
        
        self.patterns.push((
            TokenType::FloatLiteral,
            Regex::new(r"\d+\.\d+([eE][+-]?\d+)?").unwrap()
        ));
        
        self.patterns.push((
            TokenType::IntegerLiteral,
            Regex::new(r"\d+").unwrap()
        ));
        
        self.patterns.push((
            TokenType::BoolLiteral,
            Regex::new(r"\b(true|false)\b").unwrap()
        ));
        
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
        
        self.patterns.push((
            TokenType::Include,
            Regex::new(r"#include\b").unwrap()
        ));
        self.patterns.push((
            TokenType::Define,
            Regex::new(r"#define\b").unwrap()
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
        
        self.patterns.push((
            TokenType::Identifier,
            Regex::new(r"[a-zA-Z_][a-zA-Z0-9_]*").unwrap()
        ));
    }
    
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
    
    pub fn tokenize(&mut self) -> Result<(), String> {
        while self.position < self.source.len() {
            self.skip_whitespace();
            
            if self.position >= self.source.len() {
                break;
            }
            
            let mut matched = false;
            let start_line = self.line;
            let start_col = self.column;
            
            for (token_type, pattern) in &self.patterns {
                let remaining = &self.source[self.position..];
                
                if let Some(mat) = pattern.find(remaining) {
                    if mat.start() == 0 {
                        let lexeme = mat.as_str().to_string();
                        
                        if *token_type == TokenType::Comment {
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
                        
                        let mut final_token_type = token_type.clone();
                        
                        if let Some(data_type) = self.get_data_type(token_type) {
                            self.last_type_keyword = Some(data_type);
                        }
                        
                        if *token_type == TokenType::Identifier {
                            if let Some(keyword_type) = self.check_keyword(&lexeme) {
                                match keyword_type {
                                    TokenType::If | TokenType::Else | TokenType::While | 
                                    TokenType::For | TokenType::Return => {
                                        self.last_type_keyword = None;
                                    }
                                    _ => {}
                                }
                                final_token_type = keyword_type;
                            } else {
                                let data_type = self.last_type_keyword.clone().unwrap_or_else(|| "unknown".to_string());
                                

                                let symbol_type = "variable".to_string();
                                
                                self.symbol_table.add_symbol(
                                    lexeme.clone(),
                                    symbol_type,
                                    data_type,
                                    start_line,
                                );
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
                let ch = self.source.chars().nth(self.position).unwrap();
                return Err(format!(
                    "Lexical Error: Invalid character '{}' at line {}, column {}",
                    ch, self.line, self.column
                ));
            }
        }
        
        self.tokens.push(Token::new(
            TokenType::EOF,
            "EOF".to_string(),
            self.line,
            self.column,
        ));
        
        Ok(())
    }
    
    pub fn get_tokens(&self) -> &Vec<Token> {
        &self.tokens
    }
    
    pub fn get_symbol_table(&self) -> &SymbolTable {
        &self.symbol_table
    }
    
    pub fn print_token_stream(&self) {
        println!("\n=== TOKEN STREAM ===");
        for token in &self.tokens {
            println!("{}", token.to_compiler_format());
        }
    }
    
    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(&self.tokens).unwrap()
    }
}
