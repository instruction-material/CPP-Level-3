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
    compiler=os.environ.get('CXX','g++');targets=['command_sim_starter','command_sim_solution','state_review_starter','state_review_solution']
    with tempfile.TemporaryDirectory(prefix='cppi6-builds-native-') as tmp:
        area=Path(tmp)
        for name in ['CPPI6-Saveable-Command-Simulation','CPPI6-Enum-vs-Polymorphic-State-Review']:
            for role in ['starter','solution']:
                folder=area/(name+'-'+role);shutil.copytree(ROOT/name/role,folder)
                for sanitized in [False,True]:
                    run(['make','clean'],folder)
                    flags=' '.join(FLAGS+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'] if sanitized else []))
                    run(['make','CXX='+compiler,'CXXFLAGS='+flags,'main'],folder,timeout=120)
                    expected=1 if name.endswith('State-Review') and role=='starter' else 0
                    out,err=run([folder/'main'],folder,expected=expected,stdin='show\n')
                    if name.endswith('Simulation'):
                        if role=='starter':assert out=='' and 'Unfinished command parser' in err
                        else:assert out.startswith('phase ready position entry moves 0\n') and err==''
                    elif role=='starter':assert out=='' and 'Unfinished state factory' in err
                    else:assert out=='enum ready poly ready\nlifetime balanced true\n' and err==''
        build=area/'cmake'
        run(['cmake','-S',ROOT,'-B',build,'-DCMAKE_CXX_COMPILER='+compiler],area,timeout=120)
        run(['cmake','--build',build,'--target',*targets,'--parallel','2'],area,timeout=240)
        for target in targets:
            expected=1 if target=='state_review_starter' else 0
            out,err=run([build/target],area,expected=expected,stdin='show\n')
            if target=='command_sim_starter':assert out=='' and 'Unfinished command parser' in err
            elif target=='command_sim_solution':assert out.startswith('phase ready position entry moves 0\n') and err==''
            elif target=='state_review_starter':assert out=='' and 'Unfinished state factory' in err
            else:assert out=='enum ready poly ready\nlifetime balanced true\n' and err==''
    print(json.dumps({'event':'verified-cppi6-builds','makePacks':4,'makeOrdinaryAndSanitized':True,'cmakeTargets':4,'explicitUnfinishedTasks':True}),flush=True)
if __name__=='__main__':main()
