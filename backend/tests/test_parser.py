from pathlib import Path

from app.parser.python_parser import PythonParser


def create_temp_file(tmp_path, content):
    file_path = tmp_path / "sample.py"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_function_detection(tmp_path):
    code = """
def add(a, b):
    return a + b
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert result.status == "ok"
    assert len(result.functions) == 1
    assert result.functions[0].name == "add"


def test_function_parameters(tmp_path):
    code = """
def add(a, b):
    return a + b
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert result.functions[0].parameters == ["a", "b"]


def test_function_calls(tmp_path):
    code = """
def process():
    validate()
    save()
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert "validate" in result.calls
    assert "save" in result.calls

    assert "validate" in result.functions[0].calls
    assert "save" in result.functions[0].calls


def test_class_and_inheritance(tmp_path):
    code = """
class PaymentService(BaseService):
    pass
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert len(result.classes) == 1

    class_info = result.classes[0]

    assert class_info.name == "PaymentService"
    assert class_info.bases == ["BaseService"]


def test_class_methods(tmp_path):
    code = """
class PaymentService:
    def validate(self, payment):
        return True

    def save(self, payment):
        return True
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert len(result.classes) == 1

    class_info = result.classes[0]

    assert len(class_info.methods) == 2

    assert class_info.methods[0].name == "validate"
    assert class_info.methods[1].name == "save"


def test_import_detection(tmp_path):
    code = """
import os
from pathlib import Path
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert "os" in result.imports
    assert "pathlib.Path" in result.imports


def test_invalid_python_file(tmp_path):
    code = """
def broken(
"""

    file_path = create_temp_file(tmp_path, code)

    parser = PythonParser()
    result = parser.parse_file(str(file_path))

    assert result.status == "error"
    assert result.error is not None