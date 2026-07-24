import os
import re
import sys
import inspect
from typed import Bool, Union, Regex, Filter, Null, Tuple, Int, Str, typed, Nill, List, Pattern

Path = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))

def _exists(path: Path) -> Bool:
    return os.path.exists(path)

def _is_file(path: Path) -> Bool:
    return os.path.isfile(path)

def _is_dir(path: Path) -> Bool:
    return os.path.isdir(path)

def _is_symlink(path: Path) -> Bool:
    return os.path.islink(path)

def _is_mount(path: Path) -> Bool:
    return os.path.ismount(path)

Exists  = Filter(Path, _exists)
File    = Filter(Path, _is_file)
Dir     = Filter(Path, _is_dir)
Symlink = Filter(Path, _is_symlink)
Mount   = Filter(Path, _is_mount)

Path.__display__    = "Path"
Exists.__display__  = "Exists"
File.__display__    = "File"
Dir.__display__     = "Dir"
Symlink.__display__ = "Symlink"
Mount.__display__   = "Mount"

Path.__null__    = ""
Exists.__null__  = ""
File.__null__    = ""
Dir.__null__     = ""
Symlink.__null__ = ""
Mount.__null__   = ""

class PathErr(Exception): pass

class path:
    @typed
    def cwd(*paths: Tuple(Path)) -> Path:
        try:
            if len(paths) == 0:
                return os.getcwd()
            return path.join(os.getcwd(), *paths)
        except Exception as e:
            raise PathErr(e)
    pwd = cwd

    @typed
    def here(*paths: Tuple(Path)) -> Path:
        try:
            caller_frame = inspect.stack()[2]
            caller_filepath = caller_frame.filename
            here_ = os.path.dirname(os.path.abspath(caller_filepath))
            if len(paths) == 0:
                return here_
            return path.join(here_, *paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def exists(*paths: Tuple(Path)) -> Bool:
        try:
            return all(path in Exists for path in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def abs(*paths: Tuple(Path)) -> Union(Path, Tuple(Path)):
        try:
            if len(paths) == 1:
                return os.path.abspath(paths[0])
            return (os.path.abspath(path_) for path_ in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def insert(*paths: Tuple(Path)) -> Nill:
        try:
            for p in paths:
                sys.path.insert(0, path.abs(p))
        except Exception as e:
            raise PathErr(e)

    @typed
    def is_file(*paths: Tuple(Path)) -> Bool:
        try:
            return all(path in File for path in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def is_dir(*paths: Tuple(Path)) -> Bool:
        try:
            return all(path in Dir for path in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def is_abs(*paths: Tuple(Path)) -> Bool:
        try:
            return all(os.path.isabs(path_) for path_ in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def is_rel(*paths: Tuple(Path)) -> Bool:
        try:
            return not any(os.path.isabs(path_) for path_ in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def is_link(*paths: Tuple(Path)) -> Bool:
        try:
            return all(path in Symlink for path in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def is_mount(*paths: Tuple(Path)) -> Bool:
        try:
            return all(path in Mount for path in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def join(*paths: Tuple(Path)) -> Path:
        try:
            return os.path.join(*paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def basename(*paths: Tuple(Path)) -> Union(Str, Tuple(Str)):
        try:
            if len(paths) == 1:
                return os.path.basename(paths[0])
            else:
                return (os.path.basename(path_) for path_ in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def dirname(*paths: Tuple(Path)) -> Union(Str, Tuple(Str)):
        try:
            if len(paths) == 1:
                return os.path.dirname(paths[0])
            else:
                return (os.path.dirname(path_) for path_ in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def filename(*paths: Tuple(Path)) -> Union(Str, Tuple(Str)):
        try:
            if len(paths) == 1:
                return path.basename(paths[0]).split('.')[0]
            else:
                return (path.basename(path_).split('.')[0] for path_ in paths)
        except Exception as e:
            raise PathErr(e)

    @typed
    def extension(*paths: Tuple(Path)) -> Union(Str, Tuple(Str)):
        try:
            if len(paths) == 1:
                return path.basename(paths[0]).split('.')[1]
            else:
                return (path.basename(path_).split('.')[1] for path_ in paths)
        except Exception as e:
            raise PathErr(e)
    ext = extension

    @typed
    def parent(path: Path="", level: Int=1) -> Path:
        parts = path.split('/')
        if len(parts) < level:
            level = len(parts)
        last_part = -level
        if not parts[0:last_part] or parts[0:last_part] == ['']:
            return '/'
        return '/'.join(parts[0:last_part])

    @typed
    def files(pattern: Pattern, dir: Dir, min_depth: Int=1, max_depth: Int=0) -> List(Path):
        matched_files = []
        compiled_pattern = re.compile(pattern)
        target_directory = os.path.abspath(dir)
        initial_depth = len(target_directory.split(os.sep))
        for root, _, files in os.walk(target_directory):
            current_depth = len(root.split(os.sep)) - initial_depth + 1
            if min_depth != 0 and current_depth < min_depth:
                continue
            if max_depth != 0 and current_depth > max_depth:
                continue
            for file in files:
                if compiled_pattern.search(file):
                    matched_files.append(os.path.join(root, file))
        return matched_files

    @typed
    def dirs(pattern: Pattern, dir: Dir, min_depth: Int=1, max_depth: Int=0) -> List(Path):
        matched_files = []
        compiled_pattern = re.compile(pattern)
        target_directory = os.path.abspath(dir)
        initial_depth = len(target_directory.split(os.sep))
        for root, D, _ in os.walk(target_directory):
            current_depth = len(root.split(os.sep)) - initial_depth + 1
            if min_depth != 0 and current_depth < min_depth:
                continue
            if max_depth != 0 and current_depth > max_depth:
                continue
            for d in D:
                if compiled_pattern.search(d):
                    matched_files.append(os.path.join(root, d))
        return matched_files
