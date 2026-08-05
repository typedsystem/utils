from typed import service, action, Str
from typed.meta import TYPE
from utils.mods.path.types import Path
from utils.mods.err import PathErr

@service(err=PathErr)
class path:
    @action
    def cwd(trm):
        import os
        return action.term(os.path.curdir(), ...)

    @action
    def here(trm):
        import inspect
        import os
        caller_frame = inspect.stack()[3]
        caller_filepath = caller_frame.filename
        return action.term(os.path.dirname(os.path.abspath(caller_filepath)), ...)

    @action
    def absof(trm):
        import os
        return action.term(os.path.abspath(str(trm)), ...)

    @action
    def baseof(trm):
        import os
        from typed import Str
        return action.term(os.path.basename(trm), Str)

    @action
    def parentof(trm, level: int = 1):
        import os
        for _ in range(max(0, level)):
            path_ = trm
            parent_path = os.path.dirname(path_)
            if parent_path == path_:
                break

            path_ = parent_path

        if not path_:
            path_ = '/'

        return action.term(path, ...)

    @action
    def fileof(trm):
        import os
        from typed import Str
        return action.term(os.path.basename(trm).split('.')[0], Str)

    @action
    def extof(trm):
        import os
        from typed import Str
        return action.term(os.path.basename(str(trm)).split('.')[-1], Str)

    @action
    def join(trm, *paths):
        import os
        return action.term(os.path.join(trm, *paths), ...)

    @action
    def find(trm, pattern: Str="", kind=TYPE, min_depth: int=1, max_depth: int=0):
        import os
        from utils.mods.path.types import PathKinds
        if kind not in PathKinds:
            from typed import prop
            raise PathErr(
                message="Invalid path kind",
                received=prop.nameof(kind),
                expected=f"term of {prop.nameof(PathKinds)}"
            )

        import re, os
        compiled_pattern = re.compile(pattern) if pattern else None
        target_directory = os.path.abspath(str(trm))
        initial_depth = len(target_directory.split(os.sep))

        categorized_results = {
            "symlink": [],
            "mount": [],
            "dir": [],
            "file": []
        }

        target_type = type.capitalize() if type else None

        for root, dirs, files in os.walk(target_directory):
            current_depth = len(root.split(os.sep)) - initial_depth + 1

            if min_depth != 0 and current_depth < min_depth:
                continue
            if max_depth != 0 and current_depth > max_depth:
                continue

            for item in dirs + files:
                if not pattern or compiled_pattern.search(item):
                    full_path = os.path.join(root, item)

                    if os.path.islink(full_path):
                        categorized_results["symlink"].append(full_path)
                    elif os.path.ismount(full_path):
                        categorized_results["mount"].append(full_path)
                    elif os.path.isdir(full_path):
                        categorized_results["dir"].append(full_path)
                    elif os.path.isfile(full_path):
                        categorized_results["file"].append(full_path)

        from typed import term

        if target_type:
            if target_type not in categorized_results:
                valid_types = ", ".join(categorized_results.keys())
                raise ValueError(f"Invalid type '{type}'. Valid options are: {valid_types}")

            return [term(p, trm.__type__) for p in categorized_results[target_type]]

        return {
            key: [term(p, trm.__type__) for p in paths] 
            for key, paths in categorized_results.items()
        }

    @action
    def read(trm) -> str:
        with open(trm, 'r') as f:
            return f.read()

    @action
    def write(trm, content: Str='', append: bool=False):
        with open(trm, 'w') as f:
            f.write(content)
            return f

    @action
    def compress(trm, source: Path, target: Path):
        import os, zipfile, tarfile
        out_str = str(target).lower()

        if out_str.endswith('.zip'):
            with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(source):
                    for root, dirs, files in os.walk(source):
                        for file_name in files:
                            filepath = os.path.join(root, file_name)
                            arcname = os.path.relpath(filepath, start=source)
                            zipf.write(filepath, arcname=arcname)
                        for dir_name in dirs:
                            dirpath = os.path.join(root, dir_name)
                            arcname = os.path.relpath(dirpath, start=source)
                            zipf.write(dirpath, arcname + os.sep)
                elif os.path.isfile(source):
                    zipf.write(source, arcname=os.path.basename(source))
                else:
                    raise PathErr(f"Input path not found or not a file/directory: {source}")

        elif out_str.endswith(('.tar', '.tar.gz', '.tgz')):
            mode = "w:gz" if out_str.endswith(('.gz', '.tgz')) else "w"
            with tarfile.open(target, mode) as tar:
                if os.path.isdir(source):
                    for root, dirs, files in os.walk(source):
                        for file_name in files:
                            filepath = os.path.join(root, file_name)
                            arcname = os.path.relpath(filepath, source)
                            tar.add(filepath, arcname=arcname)
                        for dir_name in dirs:
                            dirpath = os.path.join(root, dir_name)
                            arcname = os.path.relpath(dirpath, source)
                            tar.add(dirpath, arcname=arcname)
                elif os.path.isfile(source):
                    tar.add(source, arcname=os.path.basename(source))
                else:
                    raise PathErr(f"Input path not found or not a file/directory: {source}")
        else:
            raise PathErr(f"Unsupported compression format for output path: {target}")
        return action.term(target, ...)

    @action
    def decompress(trm, source: Path, target: Path):
        import zipfile, tarfile
        in_str = str(source).lower()

        if in_str.endswith('.zip'):
            with zipfile.ZipFile(source, 'r') as zipf:
                zipf.extractall(path=target)
        elif in_str.endswith(('.tar', '.tar.gz', '.tgz')):
            mode = 'r:gz' if in_str.endswith(('.gz', '.tgz')) else 'r'
            with tarfile.open(source, mode) as tar:
                tar.extractall(path=target)
        else:
            raise PathErr(f"Unsupported extraction format for input path: {source}")

        return action.term(target, ...)

@service(err=PathErr)
class exists(path): pass

@service(err=PathErr)
class dir(path): pass

@service(err=PathErr)
class file(path): pass

@service(err=PathErr)
class mount(path): pass

@service(err=PathErr)
class symlink(path): pass
