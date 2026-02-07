import unittest
from pathlib import Path
from synapse.parser import CodeParser

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = CodeParser()

    def test_python_parsing(self):
        content = "def hello():\n    print('world')\nhello()"
        temp_file = Path("test_py.py")
        temp_file.write_text(content)
        try:
            result = self.parser.parse_file(temp_file)
            self.assertIn("hello", result["definitions"])
            self.assertIn("print", result["calls"])
            self.assertIn("hello", result["calls"])
        finally:
            temp_file.unlink()

    def test_js_parsing(self):
        content = "function greet() { console.log('hi'); }\ngreet();"
        temp_file = Path("test_js.js")
        temp_file.write_text(content)
        try:
            result = self.parser.parse_file(temp_file)
            self.assertIn("greet", result["definitions"])
            self.assertIn("greet", result["calls"])
        finally:
            temp_file.unlink()

if __name__ == "__main__":
    unittest.main()
