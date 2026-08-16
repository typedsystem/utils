from typed import service, action, Str, Bool, Tuple, List, Term
from utils.mods.number.types import Nat
from utils.mods.path.types import Path
from utils.mods.path.err import (
    PathErr, ExistsErr,
    FileErr, DirErr,
    MountErr, SymlinkErr,
    CompressedErr
)

@service(err=PathErr)
class path:
    @action
    def __join__(trm, *paths: Tuple(Path)) -> 'path':
        import os
        _paths = [str(path) for path in paths ]
        return action.term(os.path.join(str(trm), *_paths), ...)

    @action
    def __split__(trm) -> List(Str):
        return str(trm).split('/')

    @action
    def cwd(trm) -> 'path':
        """
        : kind is action
        : args
        :  - trm: Path
        :  - return: Path
        : desc: Returns the current working directory
        """
        import os
        return action.term(os.path.abspath(os.path.curdir), ...)

    @action
    def here(trm) -> 'path':
        """
        Returns the current file directory

        : typeof(here) is Action
        : args(here)   is (trm: Path, return: Path)
        """
        import inspect
        import os
        caller_frame = inspect.stack()[3]
        caller_filepath = caller_frame.filename
        return action.term(os.path.dirname(os.path.abspath(caller_filepath)), ...)

    @action
    def absof(trm) -> 'path':
        """
        :: args:
        ::  - trm: Path
        ::  - return: Path
        :: desc: Returns the absolute version of a given path
        """
        import os
        return action.term(os.path.abspath(str(trm)), ...)

    @action
    def baseof(trm) -> Str:
        """
        :: args:
        ::  - trm: Path
        ::  - return: Str
        :: desc: Returns the basename of a given path
        """
        import os
        from typed import Str
        return action.term(os.path.basename(str(trm)), Str)

    @action
    def mimeof(trm) -> Str:
        """
        :: args:
        ::  - trm: Path
        ::  - return: Str
        :: desc: Returns the mimetype of a given path
        """
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(trm))
        mime_ = mime_type or "application/octet-stream"
        return action.term(mime_, Str)

    @action
    def encof(trm) -> Str:
        """
        :: args:

        Returns the encoding of a given path
        """
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(trm))
        mime_ = mime_type or "application/octet-stream"
        return action.term(mime_, Str)

    @action
    def fileof(trm) -> Str:
        """
        Returns the filename of a given path
        """
        import os
        from typed import Str
        return action.term(os.path.basename(str(trm)).split('.')[0], Str)

    @action
    def extof(trm) -> Str:
        """
        Returns the extension of a given path
        """
        import os
        from typed import Str
        return action.term(os.path.basename(str(trm)).split('.')[-1], Str)

    @action
    def parent(trm, level: Nat=1) -> 'path':
        import os
        for _ in range(max(0, level)):
            path_ = str(trm)
            parent_path = os.path.dirname(os.path.abspath(path_))
            if parent_path == path_:
                break

            path_ = parent_path

        if not path_:
            path_ = '/'

        return action.term(path_, ...)

    @action
    def mkdir(trm, target):
        import os

        trm_str = str(trm)
        if not os.path.isdir(trm_str):
            raise NotADirectoryError(f"Base path is not a directory: {trm_str}")

        target_path = os.path.join(trm_str, str(target))
        os.makedirs(
            target_path,
            exist_ok=True
        )

        return action.term(target_path, ...)

    @action
    def touch(trm, target):
        import os
        trm_str = str(trm)
        if not os.path.isdir(trm_str):
            raise PathErr(
                message="Path is not a directory",
                path=trm_str
            )

        target_path = os.path.join(trm_str, str(target))
        target_parent = os.path.dirname(target_path)

        if target_parent and not os.path.exists(target_parent):
            os.makedirs(
                target_parent,
                exist_ok=True
            )

        with open(target_path, 'a'):
            os.utime(
                target_path,
                None
            )

        return action.term(target_path, ...)

    @action
    def tempdir(trm: Term):
        import tempfile, os
        temp_dir = tempfile.mkdtemp()
        os.makedirs(
            temp_dir,
            exist_ok=True
        )
        return action.term(temp_dir, ...)

    @action
    def tempfile(trm: Term, prefix: Str='', extension: Str=''):
        import tempfile, os
        temp_file = tempfile.mktemp(prefix=prefix, suffix=f'.{extension}')
        with open(temp_file, 'a'):
            os.utime(temp_file, None)
        return action.term(temp_file, ...)

    @action
    def ls(trm: Term, pattern: Str=None, exclude=None):
        import os
        import fnmatch

        trm_str = str(trm)

        def _match(p, pat_list):
            if not pat_list:
                return False
            base = os.path.basename(p)
            patterns = [pat_list] if isinstance(pat_list, str) else pat_list
            for pat in patterns:
                if base == pat or p == pat or fnmatch.fnmatch(base, pat) or fnmatch.fnmatch(p, pat):
                    return True
            return False

        results = []

        if pattern is not None:
            for root, dirs, files in os.walk(trm_str):
                for name in dirs + files:
                    full_path = os.path.join(root, name)
                    if _match(full_path, pattern) and not _match(full_path, exclude):
                        results.append(action.term(os.path.abspath(full_path), ...))
        else:
            if os.path.isdir(trm_str):
                for name in os.listdir(trm_str):
                    full_path = os.path.join(trm_str, name)
                    if not _match(full_path, exclude):
                        results.append(action.term(os.path.abspath(full_path), ...))

        return results

    @action
    def find(
        trm: Term,
        pattern: Str="",
        kind: Str="",
        min_depth: Nat=1,
        max_depth: Nat=1,
        reverse: bool=False,
    ):
        import os
        import re

        categorized_results = {"symlink": [], "mount": [], "dir": [], "file": []}

        if kind:
            if kind not in categorized_results:
                raise PathErr(
                    message="Invalid path kind",
                    received=kind,
                    expected=f"{tuple(categorized_results.keys())}",
                )

        compiled_pattern = re.compile(pattern) if pattern else None
        target_directory = os.path.abspath(str(trm))

        def categorize_path(full_path: str):
            item_name = os.path.basename(full_path)
            if not pattern or compiled_pattern.search(item_name):
                if os.path.islink(full_path):
                    categorized_results["symlink"].append(full_path)
                elif os.path.ismount(full_path):
                    categorized_results["mount"].append(full_path)
                elif os.path.isdir(full_path):
                    categorized_results["dir"].append(full_path)
                elif os.path.isfile(full_path):
                    categorized_results["file"].append(full_path)

        if reverse:
            curr_dir = target_directory
            depth = 1

            while curr_dir:
                if max_depth != 0 and depth > max_depth:
                    break

                parent_dir = os.path.dirname(curr_dir)

                if parent_dir == curr_dir:
                    break

                if min_depth == 0 or depth >= min_depth:
                    categorize_path(parent_dir)

                    try:
                        for item in os.listdir(parent_dir):
                            full_path = os.path.join(parent_dir, item)
                            if full_path != curr_dir:
                                categorize_path(full_path)
                    except PermissionError:
                        pass

                curr_dir = parent_dir
                depth += 1

        else:
            initial_depth = len(target_directory.split(os.sep))

            for root, dirs, files in os.walk(target_directory):
                current_depth = len(root.split(os.sep)) - initial_depth + 1

                if min_depth != 0 and current_depth < min_depth:
                    continue
                if max_depth != 0 and current_depth > max_depth:
                    continue

                for item in dirs + files:
                    full_path = os.path.join(root, item)
                    categorize_path(full_path)

        if kind:
            return [action.term(p, trm.__type__) for p in categorized_results[kind]]

        return {
            key: [action.term(p, trm.__type__) for p in paths]
            for key, paths in categorized_results.items()
        }

    @action
    def cp(trm, pattern=None, target="", exclude=None):
        import os
        import shutil
        import fnmatch

        trm_str = str(trm)
        target_str = str(target)

        def _match(p, pat_list):
            if not pat_list:
                return False
            base = os.path.basename(p)
            patterns = [pat_list] if isinstance(pat_list, str) else pat_list
            for pat in patterns:
                if base == pat or p == pat or fnmatch.fnmatch(base, pat) or fnmatch.fnmatch(p, pat):
                    return True
            return False

        if pattern is not None:
            for root, dirs, files in os.walk(trm_str):
                for filename in files:
                    src_path = os.path.join(root, filename)
                    if not _match(src_path, pattern):
                        continue
                    if _match(src_path, exclude):
                        continue

                    rel_path = os.path.relpath(src_path, trm_str)
                    target_path = os.path.join(target_str, rel_path)
                    target_parent = os.path.dirname(target_path)

                    if target_parent and not os.path.exists(target_parent):
                        os.makedirs(target_parent, exist_ok=True)

                    shutil.copy2(src_path, target_path)
            return action.term(None, ...)

        if _match(trm_str, exclude):
            return action.term(None, ...)

        if os.path.isfile(trm_str):
            if os.path.exists(target_str) and os.path.isdir(target_str):
                final_target = os.path.join(target_str, os.path.basename(trm_str))
            else:
                final_target = target_str
                target_parent = os.path.dirname(final_target)
                if target_parent and not os.path.exists(target_parent):
                    os.makedirs(target_parent, exist_ok=True)

            shutil.copy2(trm_str, final_target)
            return action.term(None, ...)

        if os.path.isdir(trm_str):
            if os.path.exists(target_str):
                if os.path.isdir(target_str):
                    final_target = os.path.join(target_str, os.path.basename(trm_str))
                    if not exclude:
                        shutil.copytree(trm_str, final_target)
                    else:
                        for root, dirs, files in os.walk(trm_str):
                            rel_root = os.path.relpath(root, trm_str)
                            tgt_root = os.path.join(final_target, rel_root)
                            if not os.path.exists(tgt_root):
                                os.makedirs(tgt_root, exist_ok=True)
                            for f in files:
                                src_f = os.path.join(root, f)
                                if not _match(src_f, exclude):
                                    shutil.copy2(
                                        src_f,
                                        os.path.join(tgt_root, f)
                                    )
                else:
                    raise NotADirectoryError(f"Destination is not a dir: {target_str}")
            else:
                if not exclude:
                    shutil.copytree(trm_str, target_str)
                else:
                    for root, dirs, files in os.walk(trm_str):
                        rel_root = os.path.relpath(root, trm_str)
                        tgt_root = os.path.join(target_str, rel_root)
                        if not os.path.exists(tgt_root):
                            os.makedirs(tgt_root, exist_ok=True)
                        for f in files:
                            src_f = os.path.join(root, f)
                            if not _match(src_f, exclude):
                                shutil.copy2(
                                    src_f,
                                    os.path.join(tgt_root, f)
                                )
            return action.term(trm, ...)

        raise ValueError(f"Unsupported source type: {trm_str}")

    @action
    def rm(trm, remove=None, exclude=None):
        import os
        import shutil
        import fnmatch

        trm_str = str(trm)
        if not os.path.exists(trm_str):
            return action.term(None, ...)

        def _match(p, pat_list):
            if not pat_list:
                return False
            base = os.path.basename(p)
            patterns = [pat_list] if isinstance(pat_list, str) else pat_list
            for pat in patterns:
                if base == pat or p == pat or fnmatch.fnmatch(base, pat) or fnmatch.fnmatch(p, pat):
                    return True
            return False

        if remove is None and not exclude:
            if os.path.isdir(trm_str):
                shutil.rmtree(trm_str)
            else:
                os.remove(trm_str)
            return action.term(None, ...)

        if os.path.isdir(trm_str):
            for root, dirs, files in os.walk(trm_str, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if remove and not _match(file_path, remove):
                        continue
                    if _match(file_path, exclude):
                        continue
                    os.remove(file_path)

                for name in dirs:
                    dir_path = os.path.join(root, name)
                    if remove and not _match(dir_path, remove):
                        continue
                    if _match(dir_path, exclude):
                        continue
                    try:
                        os.rmdir(dir_path)
                    except OSError:
                        pass

            if not remove and not _match(trm_str, exclude):
                try:
                    os.rmdir(trm_str)
                except OSError:
                    pass
        else:
            if (not remove or _match(trm_str, remove)) and not _match(trm_str, exclude):
                os.remove(trm_str)

        return action.term(trm, ...)

    @action
    def chmod(trm, mode):
        import os

        os.chmod(trm, mode)
        if os.path.isdir(trm):
            for root, dirs, files in os.walk(trm):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    os.chmod(dir_path, mode)
                for f in files:
                    file_path = os.path.join(root, f)
                    os.chmod(file_path, mode)

        return action.term(trm, ...)

    @action
    def chown(trm, user=None, group=None):
        import os
        from pwd import getpwnam
        from grp import getgrnam

        uid = -1
        gid = -1

        if user is not None:
            if isinstance(user, str):
                try:
                    uid = getpwnam(user).pw_uid
                except KeyError:
                    raise ValueError(f"User '{user}' not found.")
            elif isinstance(user, int):
                uid = user
            else:
                raise TypeError("User must be a string (username) or an int (UID).")

        if group is not None:
            if isinstance(group, str):
                try:
                    gid = getgrnam(group).gr_gid
                except KeyError:
                    raise ValueError(f"Group '{group}' not found.")
            elif isinstance(group, int):
                gid = group
            else:
                raise TypeError("Group must be a string (group name) or an int (GID).")

        os.chown(trm, uid, gid)

        if os.path.isdir(trm):
            for root, dirs, files in os.walk(trm):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    os.chown(
                        dir_path,
                        uid,
                        gid
                    )
                for f in files:
                    file_path = os.path.join(root, f)
                    os.chown(
                        file_path,
                        uid,
                        gid
                    )

        return action.term(trm, ...)

    @action
    def sync(trm, target='', delete=False):
        import os
        import filecmp
        import shutil
        from pathlib import Path as Path_

        source_path = Path_(trm)
        destination_path = Path_(target)

        if source_path.is_file():
            if delete:
                if destination_path.exists():
                    os.remove(destination_path)
            shutil.copy2(
                trm,
                target
            )

        def sync_dirs(src, dest):
            for source, _, files in os.walk(src):
                target_dir = source.replace(str(src), str(dest), 1)
                Path_(target_dir).mkdir(
                    parents=True,
                    exist_ok=True
                )
                for file_ in files:
                    src_file = os.path.join(source, file_)
                    dst_file = os.path.join(target_dir, file_)
                    if not os.path.exists(dst_file) or not filecmp.cmp(src_file, dst_file, shallow=False):
                        shutil.copy2(
                            src_file,
                            dst_file
                        )

        if os.path.isdir(trm):
            destination_path.mkdir(
                parents=True,
                exist_ok=True
            )
            sync_dirs(
                source_path,
                destination_path
            )

            if delete:
                for target_dir, _, files in os.walk(destination_path):
                    source_dir = target_dir.replace(str(destination_path), str(source_path), 1)
                    if not os.path.exists(source_dir):
                        shutil.rmtree(target_dir)
                    else:
                        for file_ in files:
                            dst_file = os.path.join(target_dir, file_)
                            src_file = os.path.join(source_dir, file_)
                            if not os.path.exists(src_file):
                                os.remove(dst_file)

        return action.term(
            None,
            ...
        )

@service(err=ExistsErr)
class exists(path):
    @action
    def compress(trm, pattern: Str=None, target: Path="") -> 'exists':
        import os
        import zipfile
        import tarfile
        import fnmatch
        import mimetypes
        from utils.mods.checker import require

        trm_str = str(trm)
        target_str = str(target)
        require.path.exists(trm_str)

        def is_match(p):
            if not pattern or pattern == "*":
                return True
            rel_p = os.path.relpath(
                p,
                trm_str
            )
            base = os.path.basename(p)
            return fnmatch.fnmatch(rel_p, pattern) or fnmatch.fnmatch(base, pattern) or fnmatch.fnmatch(p, pattern)

        mime_type, encoding = mimetypes.guess_type(target_str)

        if mime_type == "application/zip":
            with zipfile.ZipFile(target_str, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(trm_str):
                    for root, dirs, files in os.walk(trm_str):
                        for file_name in files:
                            filepath = os.path.join(
                                root,
                                file_name
                            )
                            if is_match(filepath):
                                arcname = os.path.relpath(
                                    filepath,
                                    start=trm_str
                                )
                                zipf.write(
                                    filepath,
                                    arcname=arcname
                                )
                        for dir_name in dirs:
                            dirpath = os.path.join(
                                root,
                                dir_name
                            )
                            if is_match(dirpath):
                                arcname = os.path.relpath(
                                    dirpath,
                                    start=trm_str
                                )
                                zipf.write(
                                    dirpath,
                                    arcname + os.sep
                                )
                elif os.path.isfile(trm_str):
                    if is_match(trm_str):
                        zipf.write(
                            trm_str,
                            arcname=os.path.basename(trm_str)
                        )
                else:
                    raise ValueError(f"Input path not found or not a file/directory: {trm_str}")

        elif mime_type == "application/x-tar" or encoding in ("gzip", "bzip2", "xz", "compress") or mime_type in ("application/gzip", "application/x-bzip2", "application/x-xz"):
            mode = "w"
            if encoding == "gzip" or mime_type == "application/gzip":
                mode = "w:gz"
            elif encoding == "bzip2" or mime_type == "application/x-bzip2":
                mode = "w:bz2"
            elif encoding == "xz" or mime_type == "application/x-xz":
                mode = "w:xz"

            with tarfile.open(target_str, mode) as tar:
                if os.path.isdir(trm_str):
                    for root, dirs, files in os.walk(trm_str):
                        for file_name in files:
                            filepath = os.path.join(
                                root,
                                file_name
                            )
                            if is_match(filepath):
                                arcname = os.path.relpath(
                                    filepath,
                                    trm_str
                                )
                                tar.add(
                                    filepath,
                                    arcname=arcname
                                )
                        for dir_name in dirs:
                            dirpath = os.path.join(
                                root,
                                dir_name
                            )
                            if is_match(dirpath):
                                arcname = os.path.relpath(
                                    dirpath,
                                    trm_str
                                )
                                tar.add(
                                    dirpath,
                                    arcname=arcname
                                )
                elif os.path.isfile(trm_str):
                    if is_match(trm_str):
                        tar.add(
                            trm_str,
                            arcname=os.path.basename(trm_str)
                        )
                else:
                    raise ValueError(f"Input path not found or not a file/directory: {trm_str}")
        else:
            raise ValueError(f"Unsupported compression format for output path: {target_str}")

        return action.term(
            target_str,
            ...
        )

    @action
    def decompress(trm, pattern=None, target="") -> 'exists':
        import os
        import zipfile
        import tarfile
        import fnmatch
        import mimetypes
        from utils.mods.checker import path_require

        trm_str = str(trm)
        path_require.iscompressed(trm_str)

        target_str = str(target)
        if not os.path.isabs(target_str):
            target_str = os.path.join(
                os.path.dirname(os.path.abspath(trm_str)),
                target_str
            )

        if not os.path.exists(target_str):
            os.makedirs(
                target_str,
                exist_ok=True
            )

        def is_match(p):
            if not pattern or pattern == "*":
                return True
            return fnmatch.fnmatch(p, pattern) or fnmatch.fnmatch(os.path.basename(p), pattern)

        mime_type = path_require.mimeof(trm_str)
        _, encoding = mimetypes.guess_type(trm_str)

        if mime_type == "application/zip":
            with zipfile.ZipFile(trm_str, 'r') as zipf:
                if not pattern or pattern == "*":
                    zipf.extractall(path=target_str)
                else:
                    members = [m for m in zipf.namelist() if is_match(m)]
                    zipf.extractall(
                        path=target_str,
                        members=members
                    )
        elif mime_type == "application/x-tar" or encoding in ("gzip", "bzip2", "xz", "compress") or mime_type in ("application/gzip", "application/x-bzip2", "application/x-xz"):
            mode = "r"
            if encoding == "gzip" or mime_type == "application/gzip":
                mode = "r:gz"
            elif encoding == "bzip2" or mime_type == "application/x-bzip2":
                mode = "r:bz2"
            elif encoding == "xz" or mime_type == "application/x-xz":
                mode = "r:xz"

            with tarfile.open(trm_str, mode) as tar:
                if not pattern or pattern == "*":
                    tar.extractall(path=target_str)
                else:
                    members = [m for m in tar.getmembers() if is_match(m.name)]
                    tar.extractall(
                        path=target_str,
                        members=members
                    )
        else:
            raise ValueError(f"Unsupported extraction format for input path: {trm_str}")

        return action.term(target_str, ...)

@service(err=FileErr)
class dir(exists): pass

@service(err=DirErr)
class file(exists):
    @action
    def read(trm) -> Str:
        from utils.mods.checker import require
        require.path.isfile(trm)
        with open(str(trm), 'r') as f:
            return action.term(f.read(), Str)

    @action
    def linesof(trm) -> List(Str):
        from utils.mods.checker import require
        require.path.isfile(trm)
        with open(str(trm), 'r') as f:
            return action.term(f.readlines(), List(Str))

    @action
    def write(trm: Term, content: Str='', append: Bool=False) -> 'file':
        from utils.mods.checker import require
        require.path.isfile(trm)
        mode = 'a' if append else 'w'
        with open(str(trm), mode) as f:
            f.write(content)
            return action.term(f, ...)

@service(err=MountErr)
class mount(path): pass

@service(err=SymlinkErr)
class symlink(path): pass

@service(err=CompressedErr)
class compressed(path): pass
