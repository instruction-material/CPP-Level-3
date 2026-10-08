"""Verify real CPPI4 behavior, source roles and bounded failures."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI4-Ownership-Rewrite-Reflection"
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi4-ownership-source")
BASE_FLAGS = ["-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wsign-conversion", "-Werror", "-g", "-O0"]

def execute(command, cwd, expected=0, timeout=60):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    fields = {"parentTaskId":TASK,"cwd":str(cwd),"command":list(map(str,command)),
              "pid":child.pid,"parentPid":os.getpid(),"timeoutSeconds":timeout}
    def event(kind, **extra):
        print(json.dumps({"event":kind,"time":datetime.now(timezone.utc).isoformat(),**fields,**extra}),flush=True)
    event("start")
    try:
        output,error=child.communicate(timeout=timeout)
    except BaseException:
        os.killpg(child.pid,signal.SIGTERM)
        try: child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL)
            child.wait()
        event("child-process-group-cleanup",exitCode=child.returncode)
        raise
    event("end",exitCode=child.returncode)
    assert child.returncode==expected,(command,child.returncode,output,error)
    assert b"AddressSanitizer" not in error and b"runtime error:" not in error,error
    return output,error

def expected_reference(values):
    row=" ".join(map(str,values))+" "
    return ("Manual array: "+row+"\nManual responsibility: delete[] must run exactly once.\n\n"
            +"Vector: "+row+"\nVector responsibility: the vector cleans up its own storage.\n\n"
            +"unique_ptr array: "+row+"\nunique_ptr responsibility: ownership is still explicit, but cleanup is automatic.\n").encode()

def main():
    compiler=os.environ.get("CXX","c++")
    reference=(PACK/"solution/ownership-reference.cpp").read_text()
    manual=(PACK/"starter/manual-ownership.cpp").read_text()
    assert reference[:reference.index("void vectorDemo()")] == manual[:manual.index("int main()")]
    with tempfile.TemporaryDirectory(prefix="cppi4-ownership-native-") as directory:
        cwd=Path(directory)
        (cwd/"ownership-reference.cpp").write_text(reference)
        (cwd/"ownership-probe.cpp").write_bytes((ROOT/"ownership-output-probe.cpp").read_bytes())
        for standard in [17,20]:
            for sanitized in [False,True]:
                flags=[f"-std=c++{standard}",*BASE_FLAGS]
                if sanitized: flags += ["-fsanitize=address,undefined","-fno-sanitize-recover=all","-fno-omit-frame-pointer","-fno-pie","-no-pie"]
                for section,document in [("starter","NOTES.md"),("solution","WORKED.md")]:
                    execute([compiler,*flags,str(PACK/section/"main.cpp"),"-o","printer"],cwd)
                    assert execute(["./printer"],cwd)==((PACK/section/document).read_bytes(),b"")
                    assert execute(["./printer","extra"],cwd,2)==(b"",b"Usage: main\n")
                for changed,values in [(False,[84,91,76,88]),(True,[0,60,100,59])]:
                    text=reference.replace("{84, 91, 76, 88}","{0, 60, 100, 59}") if changed else reference
                    assert text.count("{0, 60, 100, 59}") == (3 if changed else 0)
                    (cwd/"normal-reference.cpp").write_text(text)
                    execute([compiler,*flags,"normal-reference.cpp","-o","reference"],cwd)
                    assert execute(["./reference"],cwd)==(expected_reference(values),b"")
                    text=manual.replace("{84, 91, 76, 88}","{0, 60, 100, 59}") if changed else manual
                    (cwd/"manual.cpp").write_text(text)
                    execute([compiler,*flags,"manual.cpp","-o","manual"],cwd)
                    expected=expected_reference(values).split(b"\n\n",1)[0]+b"\n"
                    assert execute(["./manual"],cwd)==(expected,b"")
                execute([compiler,*flags,"ownership-probe.cpp","-o","probe"],cwd)
                assert execute(["./probe"],cwd)==(b"Three real partial-output exceptions observed.\n",b"")
    print(json.dumps({"event":"verified-ownership-worksheet","standards":[17,20],"ordinaryAndSanitized":True,"exactPrinters":2,"changedScores":[0,60,100,59],"realPartialOutputExceptions":3}))

if __name__=="__main__": main()
