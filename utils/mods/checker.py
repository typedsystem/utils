from utils.mods.number.checker import number_check, number_require
from utils.mods.path.checker import path_check, path_require
from utils.mods.shell.checker import shell_check, shell_require

class check:
    number = number_check
    path   = path_check
    shell  = shell_check

class require:
    number = number_require
    path   = path_require
    shell  = shell_require
