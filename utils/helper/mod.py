from typed import name

def _is_local(obj):
    return name(obj).startswith('_')

def _is_global(obj):
    return not _is_local(obj)
