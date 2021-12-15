import subprocess


class Terminal:
    def execute(self, cmd: str):
        s = subprocess.getstatusoutput(cmd)

    def execute_with_result(self, cmd: str) -> tuple:
        s = subprocess.getstatusoutput(cmd)
        return s
