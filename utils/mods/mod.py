import importlib
import importlib.util
import sys
import ast
from typed import typed, Any, Maybe, List, Str, Bool, Dict, Union, name, Nill
from utils.mods.json_ import Entry

class ModErr(Exception): pass

class mod:
    @typed
    def exists(module: Entry) -> Bool:
        """
        Checks if some given module entry exists.
        """
        try:
            importlib.import_module(module)
            return True
        except:
            return False

    @typed
    def get(obj: Maybe(Union(Str), List(Str))=None, module: Maybe(Entry)=None) -> Any:
        try:
            if module is None:
                if obj not in Str:
                    raise TypeError(
                        "Single-argument form get(mod) requires 'module' to be a string"
                    )
                module = obj
                obj = '.'

            module = importlib.import_module(module)

            if obj is None or obj == '.':
                return module

            if obj == '*':
                names = getattr(module, "__all__", None)
                if names is None:
                    names = [name for name in dir(module) if not name.startswith('_')]
                return {name: getattr(module, name) for name in names}

            if obj in Str:
                return getattr(module, obj, None)

            if obj in List(Str):
                return [getattr(module, name, None) for name in obj]
        except Exception as e:
            raise ModErr(e)

    @typed
    def has(obj: Any, module: Entry) -> Bool:
        return hasattr(mod.get(module), obj)

    @typed
    def locals(module: Entry) -> Dict:
        try:
            return {name: mod.get(name, module) for name in dir(mod.get(module)) if mod._is_local(name)}
        except Exception as e:
            raise ModErr(e)

    @typed
    def globals(module: Entry) -> Dict:
        try:
            return {name: mod.get(name, module) for name in dir(mod.get(module)) if mod._is_global(name)}
        except Exception as e:
            raise ModErr(e)

    @typed
    def imports(module: Entry) -> Union(Dict(Str), Dict(Dict(Str))):
        try:
            if not mod.exists(module):
                raise ModErr(f"The given module '{module}' does not exists.")
            spec = importlib.util.find_spec(module)
            if not spec or not spec.origin or not spec.origin.endswith('.py'):
                raise ImportError(f"Cannot find source for module {module}")

            with open(spec.origin, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=spec.origin)

            imports = []

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ImportFrom) and node.module != "__future__":
                    for alias in node.names:
                        if alias.asname:
                            imports.append((node.lineno, {node.module: {alias.name: alias.asname}}))
                        else:
                            imports.append((node.lineno, {node.module: alias.name}))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.asname:
                            imports.append((node.lineno, {alias.name: {'': alias.asname}}))
                        else:
                            imports.append((node.lineno, {alias.name: ''}))
            return tuple(import_dict for _, import_dict in sorted(imports, key=lambda x: x[0]))
        except Exception as e:
            raise ModErr(e)

    @typed
    def import_all(module: Entry) -> Nill:
        caller_globals = sys._getframe(2).f_globals

        mod = importlib.import_module(module)
        spec = importlib.util.find_spec(module)
        if not spec or not spec.origin or not spec.origin.endswith('.py'):
            raise ImportError(f"Cannot find source for module {module}")
        with open(spec.origin, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=spec.origin)

        defined_names = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined_names.add(node.name)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_names.add(target.id)
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        defined_names.add(node.target.id)
        for name in defined_names:
            if name in mod.__dict__:
                caller_globals[name] = mod.__dict__[name]
