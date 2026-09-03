import ast
from pathlib import Path

from app.models.code_entities import (
    ClassInfo,
    CodeFile,
    FunctionInfo,
)


class PythonParser(ast.NodeVisitor):

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.calls = []

        self.current_function = None
        self.current_class = None

    def parse_file(self, file_path: str) -> CodeFile:
        """
        Parse one Python file and return a CodeFile object.
        """

        self.functions = []
        self.classes = []
        self.imports = []
        self.calls = []
        self.current_function = None
        self.current_class = None

        path = Path(file_path)

        try:
            code = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(
                code,
                filename=str(path)
            )

            self.visit(tree)

            return CodeFile(
                path=str(path),
                imports=self.imports,
                classes=self.classes,
                functions=self.functions,
                calls=self.calls,
                status="ok",
                error=None,
            )

        except (
            SyntaxError,
            UnicodeDecodeError,
            OSError
        ) as error:

            return CodeFile(
                path=str(path),
                imports=[],
                classes=[],
                functions=[],
                calls=[],
                status="error",
                error=str(error),
            )

    def visit_FunctionDef(self, node):

        parameters = [
            argument.arg
            for argument in node.args.args
        ]

        function = FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno,
            parameters=parameters,
            calls=[],
        )

        if self.current_class is not None:

            self.current_class.methods.append(
                function
            )

        else:

            self.functions.append(
                function
            )

        previous_function = self.current_function

        self.current_function = function

        self.generic_visit(node)

        self.current_function = previous_function

    def visit_AsyncFunctionDef(self, node):

        parameters = [
            argument.arg
            for argument in node.args.args
        ]

        function = FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno,
            parameters=parameters,
            calls=[],
        )

        if self.current_class is not None:

            self.current_class.methods.append(
                function
            )

        else:

            self.functions.append(
                function
            )

        previous_function = self.current_function

        self.current_function = function

        self.generic_visit(node)

        self.current_function = previous_function

    def visit_ClassDef(self, node):

        bases = []

        for base in node.bases:

            if isinstance(base, ast.Name):

                bases.append(base.id)

            elif isinstance(base, ast.Attribute):

                base_name = self.get_attribute_name(
                    base
                )

                if base_name:
                    bases.append(base_name)

        class_info = ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno,
            bases=bases,
            methods=[],
        )

        self.classes.append(
            class_info
        )

        previous_class = self.current_class

        self.current_class = class_info

        self.generic_visit(node)

        self.current_class = previous_class

    def visit_Import(self, node):

        for alias in node.names:

            self.imports.append(
                alias.name
            )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):

        module = node.module or ""

        for alias in node.names:

            if module:

                import_name = (
                    f"{module}.{alias.name}"
                )

            else:

                import_name = alias.name

            self.imports.append(
                import_name
            )

        self.generic_visit(node)

    def visit_Call(self, node):

        call_name = self.get_call_name(
            node
        )

        if call_name:

            self.calls.append(
                call_name
            )

            if self.current_function is not None:

                self.current_function.calls.append(
                    call_name
                )

        self.generic_visit(node)

    def get_call_name(self, node):

        if isinstance(node.func, ast.Name):

            return node.func.id

        if isinstance(node.func, ast.Attribute):

            return self.get_attribute_name(
                node.func
            )

        return None

    def get_attribute_name(self, node):

        if isinstance(node, ast.Name):

            return node.id

        if isinstance(node, ast.Attribute):

            parent = self.get_attribute_name(
                node.value
            )

            if parent:

                return f"{parent}.{node.attr}"

            return node.attr

        return None