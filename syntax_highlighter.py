import re


class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_syntax_highlighting()
    
    def setup_syntax_highlighting(self):
        """Setup syntax highlighting tags and definitions"""
        # C/SourceMod syntax highlighting colors
        self.syntax_colors = {
            'keyword': '#569cd6',      # Blue for keywords
            'string': '#ce9178',       # Orange for strings
            'comment': '#6a9955',      # Green for comments
            'number': '#b5cea8',       # Light green for numbers
            'preprocessor': '#c586c0', # Purple for preprocessor
            'function': '#dcdcaa',     # Yellow for functions
            'type': '#4ec9b0',         # Cyan for types
        }
        
        # C/SourceMod keywords
        self.keywords = [
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
            'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
            'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while',
            'public', 'stock', 'native', 'forward', 'new', 'decl', 'funcenum', 'functag',
            'Action', 'Plugin', 'Handle', 'bool', 'true', 'false', 'null', 'INVALID_HANDLE'
        ]
        
        # Configure tags
        for tag, color in self.syntax_colors.items():
            self.text_widget.tag_configure(tag, foreground=color)
    
    def highlight_syntax(self):
        """Apply C/SourceMod syntax highlighting"""
        # Clear existing tags
        for tag in self.syntax_colors.keys():
            self.text_widget.tag_remove(tag, "1.0", "end")
        
        content = self.text_widget.get("1.0", "end-1c")
        
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add("keyword", start, end)
        
        # Highlight strings
        string_pattern = r'"[^"]*"'
        for match in re.finditer(string_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("string", start, end)
        
        # Highlight single-line comments
        comment_pattern = r'//.*$'
        for match in re.finditer(comment_pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start, end)
        
        # Highlight multi-line comments
        multiline_comment_pattern = r'/\*.*?\*/'
        for match in re.finditer(multiline_comment_pattern, content, re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start, end)
        
        # Highlight numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("number", start, end)
        
        # Highlight preprocessor directives
        preprocessor_pattern = r'#\w+'
        for match in re.finditer(preprocessor_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("preprocessor", start, end)
        
        # Highlight function names
        function_pattern = r'\b\w+(?=\s*\()'
        for match in re.finditer(function_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("function", start, end)