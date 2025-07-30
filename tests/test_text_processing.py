import pytest
from app.utils.text_processing import (
    clean_text,
    extract_code_blocks,
    is_code_like,
    split_into_sentences,
    extract_keywords
)


class TestTextProcessing:
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  Hello   world!  \n\n  This   is   a   test.  "
        clean = clean_text(dirty_text)
        assert clean == "Hello world! This is a test."
    
    def test_extract_code_blocks(self):
        """Test code block extraction"""
        text = """
        Here is some text.
        
        ```python
        def hello():
            print("Hello world")
        ```
        
        More text here.
        
        ```javascript
        function test() {
            console.log("test");
        }
        ```
        """
        
        code_blocks = extract_code_blocks(text)
        assert len(code_blocks) == 2
        assert "def hello():" in code_blocks[0]
        assert "function test()" in code_blocks[1]
    
    def test_is_code_like(self):
        """Test code detection"""
        # Should be detected as code
        assert is_code_like("def hello(): return 'world'")
        assert is_code_like("class Test: pass")
        assert is_code_like("import os")
        assert is_code_like("for i in range(10):")
        
        # Should not be detected as code
        assert not is_code_like("This is a normal sentence.")
        assert not is_code_like("Hello world!")
    
    def test_split_into_sentences(self):
        """Test sentence splitting"""
        text = "Hello world. This is a test. How are you?"
        sentences = split_into_sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "Hello world"
        assert sentences[1] == "This is a test"
        assert sentences[2] == "How are you"
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "Python es un lenguaje de programación muy popular para el desarrollo web y la inteligencia artificial."
        keywords = extract_keywords(text, max_keywords=5)
        
        # Should extract meaningful keywords
        assert "python" in keywords
        assert "lenguaje" in keywords
        assert "programación" in keywords
        
        # Should not include stop words
        assert "es" not in keywords
        assert "un" not in keywords
        assert "de" not in keywords 