from typed import service, action

@service
class cmd:
    @action
    def has(cmd: Str) -> Bool:
        return shutil.which(str(cmd)) is not None

    @action
    def run(
        cmd: Union(Str, List, Tuple, File), 
        cwd: Maybe(Path)=None, 
        envs: Union(List(Env), Dict(Str, keys=Env))={},
        terminate: Bool=True, 
        **kargs: Dict) -> Tuple:
        try:
            if not cmd in Union(List, Tuple):
                if cmd in File:
                    cmd_list = file.read(cmd)
                else:
                    cmd_list = shlex.split(str(cmd))
            else:
                cmd_list = [str(x) for x in cmd]

            env = os.environ.copy()
            if envs in List:
                for env_var in envs:
                    if env_var in os.environ:
                        env[env_var] = os.environ[env_var]
            if envs in Dict:
                env.update(envs)

            if terminate:
                process = subprocess.run(
                    cmd_list,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    env=env,
                    check=False
                )
                return process.returncode, process.stderr, process.stdout
            else:
                try:
                    process = subprocess.Popen(
                        cmd_list,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        env=env
                    )
                    for line in process.stdout:
                        print(line, end='')
                    process.wait()
                    return None, None
                except Exception as e:
                    print(f"Error in Popen: {e}", file=sys.stderr)
                    return str(e), None
        except Exception as e:
            raise CmdErr(e)

    @action
    def sleep(seconds: Pos=1) -> Nill:
        import time
        return time.sleep(seconds)

    @action
    def exit(code: Nat=0) -> Nill:
        import sys
        return sys.exit(code)
