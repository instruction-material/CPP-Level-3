from pathlib import Path
import importlib.util
import json
import os
import re
import shutil
import tempfile
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rover_check", ROOT / "verify-rover-simulation.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
run = checks.run
FLAGS = checks.FLAGS

def main():
    compiler=os.environ.get('CXX','g++')
    pack=ROOT/'CPPI6-Saveable-Command-Simulation'
    dispatch=re.findall(r'```cpp\n([\s\S]*?)```',(pack/'DISPATCH-LESSON.md').read_text());pathway=re.findall(r'```cpp\n([\s\S]*?)```',(pack/'PATHWAYS-LESSON.md').read_text())
    assert len(dispatch)==len(pathway)==1
    dispatch=dispatch[0];pathway=pathway[0]
    cases=[('dispatch',dispatch,'move 1\nread 1\nmove 3\nread 3\ndestroyed 4\n',0,''),
           ('dispatch',dispatch.replace('<Move>(1, destroyed)','<Move>(3, destroyed)').replace('<Move>(2, destroyed)','<Move>(4, destroyed)'), 'move 3\nread 3\nmove 7\nread 7\ndestroyed 4\n',0,''),
           ('dispatch',dispatch.replace('<Move>(1, destroyed)','<Move>(11, destroyed)'),'',1,'Rejected: Move outside the lesson bounds.\n'),
           ('pathway',pathway,'found true\nentry -> archive -> dock\nentered 3\n',0,''),
           ('pathway',pathway.replace('{"archive", {"dock"}}','{"archive", {"entry"}}'),'found true\nentry -> lab -> dock\nentered 4\n',0,''),
           ('pathway',pathway.replace('{"archive", {"dock"}}','{"archive", {}}').replace('{"lab", {"dock"}}','{"lab", {}}'),'found false\n\nentered 3\n',0,'')]
    with tempfile.TemporaryDirectory(prefix='cppi6-lessons-native-') as tmp:
        folder=Path(tmp)
        for sanitized in [False,True]:
            extra=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'] if sanitized else []
            for i,(label,source,expected,status,stderr) in enumerate(cases):
                f=folder/f'lesson-{i}.cpp';f.write_text(source);exe=folder/f'lesson-{i}'
                run([compiler,*FLAGS,*extra,f,'-o',exe],folder,timeout=120)
                out,err=run([exe],folder,expected=status);assert out==expected and err==stderr
                out,err=run([exe,'extra'],folder,expected=2);assert out=='' and err==f'Usage: {label}-lesson\n'
    print(json.dumps({'event':'verified-cppi6-lessons','fullPrograms':2,'programCases':6,'changedDispatchAndGraph':True,'actualInvalidMove':True,'ordinaryAndSanitized':True}),flush=True)
if __name__=='__main__':main()
