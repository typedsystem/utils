from typed import service, action, Str
from typed.meta import TYPE
from utils.mods.path.types import Path
from utils.mods.path.err import (
    PathErr, ExistsErr,
    FileErr, DirErr,
    MountErr, SymlinkErr
)

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

        return action.term(
            None,
            ...
        )

    @action
    def touch(trm, target):
        import os

        trm_str = str(trm)
        if not os.path.isdir(trm_str):
            raise NotADirectoryError(f"Base path is not a directory: {trm_str}")

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

        return action.term(
            None,
            ...
        )

    @action
    def ls(trm, pattern=None, exclude=None):
        import os
        import fnmatch

        trm_str = str(trm)

        def is_match(p, pat_list):
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
                    if is_match(full_path, pattern) and not is_match(full_path, exclude):
                        results.append(full_path)
        else:
            if os.path.isdir(trm_str):
                for name in os.listdir(trm_str):
                    full_path = os.path.join(trm_str, name)
                    if not is_match(full_path, exclude):
                        results.append(full_path)

        return results

    @action
    def cp(trm, pattern=None, target="", exclude=None):
        import os
        import shutil
        import fnmatch

        trm_str = str(trm)
        target_str = str(target)

        def is_match(p, pat_list):
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
                    if not is_match(src_path, pattern):
                        continue
                    if is_match(src_path, exclude):
                        continue

                    rel_path = os.path.relpath(src_path, trm_str)
                    target_path = os.path.join(target_str, rel_path)
                    target_parent = os.path.dirname(target_path)

                    if target_parent and not os.path.exists(target_parent):
                        os.makedirs(target_parent, exist_ok=True)

                    shutil.copy2(src_path, target_path)
            return action.term(None, ...)

        if is_match(trm_str, exclude):
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
                                if not is_match(src_f, exclude):
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
                            if not is_match(src_f, exclude):
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

        def is_match(p, pat_list):
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
                    if remove and not is_match(file_path, remove):
                        continue
                    if is_match(file_path, exclude):
                        continue
                    os.remove(file_path)

                for name in dirs:
                    dir_path = os.path.join(root, name)
                    if remove and not is_match(dir_path, remove):
                        continue
                    if is_match(dir_path, exclude):
                        continue
                    try:
                        os.rmdir(dir_path)
                    except OSError:
                        pass

            if not remove and not is_match(trm_str, exclude):
                try:
                    os.rmdir(trm_str)
                except OSError:
                    pass
        else:
            if (not remove or is_match(trm_str, remove)) and not is_match(trm_str, exclude):
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

@service(err=ExistsErr)
class exists(path): pass

@service(err=FileErr)
class dir(path): pass

@service(err=DirErr)
class file(path): pass

@service(err=MountErr)
class mount(path): pass

@service(err=SymlinkErr)
class symlink(path): pass
