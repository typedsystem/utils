import os
import tarfile
import zipfile
from typed import typed, Str, Nill, List
from utils.mods.path import Path, File

class FileErr(Exception): pass

class file:
    @typed
    def read(filepath: File='') -> Str:
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception as e:
            raise FileErr(e)

    @typed
    def write(filepath: Path='', content: Str='') -> Nill:
        try:
            with open(filepath, 'w') as f:
                f.write(content)
        except Exception as e:
            raise FileErr(e)

    @typed
    def append(filepath: File='', content: Str='') -> Nill:
        try:
            with open(filepath, 'a') as f:
                f.write(content)
        except Exception as e:
            raise FileErr(e)

    @typed
    def get_lines(filepath: File='') -> List(Str):
        try:
            with open(filepath, 'r') as f:
                return f.readlines()
        except Exception as e:
            raise FileErr(e)

    @typed
    def get_stripped_lines(filepath: File='') -> List(Str):
        try:
            with open(filepath, 'r') as f:
                return [line.strip() for line in f.readlines()]
        except Exception as e:
            raise FileErr(e)

    @typed
    def zip(input_path: Path, output_path: Path) -> Nill:
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(input_path):
                    for root, dirs, files in os.walk(input_path):
                        for file_name in files:
                            filepath = os.path.join(root, file_name)
                            arcname = os.path.relpath(filepath, start=input_path)
                            zipf.write(filepath, arcname=arcname)
                        for dir_name in dirs:
                            dirpath = os.path.join(root, dir_name)
                            arcname = os.path.relpath(dirpath, start=input_path)
                            zipf.write(dirpath, arcname + os.sep)
                elif os.path.isfile(input_path):
                    zipf.write(input_path, arcname=os.path.basename(input_path))
                else:
                    raise FileErr(f"Input path not found or not a file/directory: {input_path}")
        except Exception as e:
            raise FileErr(e)

    @typed
    def unzip(input_path: File, output_dir: Path) -> Nill:
        try:
            with zipfile.ZipFile(input_path, 'r') as zipf:
                zipf.extractall(path=output_dir)
        except Exception as e:
            raise FileErr(e)

    @typed
    def tar(input_path: Path, output_path: Path) -> Nill:
        try:
            with tarfile.open(output_path, "w:gz") as tar:
                if os.path.isdir(input_path):
                    for root, dirs, files in os.walk(input_path):
                        for file_name in files:
                            filepath = os.path.join(root, file_name)
                            arcname = os.path.relpath(filepath, input_path)
                            tar.add(filepath, arcname=arcname)
                        for dir_name in dirs:
                            dirpath = os.path.join(root, dir_name)
                            arcname = os.path.relpath(dirpath, input_path)
                            tar.add(dirpath, arcname=arcname)
                elif os.path.isfile(input_path):
                    tar.add(input_path, arcname=os.path.basename(input_path))
                else:
                    raise FileErr(f"Input path not found or not a file/directory: {input_path}")
        except Exception as e:
            raise FileErr(e)

    @typed
    def untar(input_path: File, output_dir: Path) -> Nill:
        try:
            with tarfile.open(input_path, 'r:gz') as tar:
                tar.extractall(path=output_dir)
        except Exception as e:
            raise FileErr(e)
