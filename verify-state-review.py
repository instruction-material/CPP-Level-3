"""Check rover behavior against independent phase, graph and serialization models."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI6-Enum-vs-Polymorphic-State-Review"
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi6-state-review-source")
SOURCES = ["main.cpp", "state_review.cpp"]
HEADERS = ["state_review.h"]
FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Werror", "-g", "-O0"]



def run(command, cwd, expected=0, stdin=None, timeout=45, stdout_stream=None):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE if stdout_stream is None else stdout_stream, stderr=subprocess.PIPE, text=True)
    fields = {"parentTaskId": TASK, "cwd": str(cwd), "command": [str(c) for c in command],
              "pid": child.pid, "parentPid": os.getpid(), "timeoutSeconds": timeout}

    def record(event, **extra):
        print(json.dumps({"event": event, "time": datetime.now(timezone.utc).isoformat(),
                          **fields, **extra}), flush=True)

    record("start")
    try:
        out, err = child.communicate(input=stdin, timeout=timeout)
    except BaseException:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        record("child-process-group-cleanup", exitCode=child.returncode)
        raise
    record("end", exitCode=child.returncode)
    assert child.returncode == expected, (command, child.returncode, out, err)
    return out, err




import itertools
import re
HARNESS = r"""
#include "state_review.h"
#include <cassert>
#include <type_traits>
using namespace statecourse;
int main() {
    static_assert(std::is_abstract_v<State> && std::has_virtual_destructor_v<State>);
    static_assert(!std::is_copy_constructible_v<State>);
    const Phase phases[] = {Phase::Ready, Phase::Running, Phase::Paused, Phase::Finished};
    const Event events[] = {Event::Start, Event::Pause, Event::Resume, Event::Finish};
    const int table[4][4] = {{1,-1,-1,-1},{-1,2,-1,3},{-1,-1,1,3},{-1,-1,-1,-1}};
    for (std::size_t p = 0; p < 4; ++p) for (std::size_t e = 0; e < 4; ++e) {
        auto actual = makeState(phases[p]);
        const auto before = actual.get();
        auto simple = enumNext(phases[p], events[e]);
        auto dynamic = actual->next(events[e]);
        const bool expected = table[p][e] >= 0;
        assert(simple.has_value() == expected && dynamic.has_value() == expected);
        if (expected) { assert(*simple == phases[static_cast<std::size_t>(table[p][e])]); assert(dynamic == simple); }
        assert(actual.get() == before && actual->phase() == phases[p]);
    }
    assert(Lifetime::created == 16 && Lifetime::destroyed == 16);
    {
        Machine machine;
        assert(!machine.apply(Event::Pause) && machine.phase() == Phase::Ready);
        const auto before = Lifetime::created;
        assert(machine.apply(Event::Start) && machine.phase() == Phase::Running);
        assert(Lifetime::created == before + 1);
        assert(machine.apply(Event::Pause) && machine.apply(Event::Finish));
        const auto ended = Lifetime::created;
        assert(machine.phase() == Phase::Finished && !machine.apply(Event::Finish));
        assert(Lifetime::created == ended);
    }
    assert(Lifetime::created == Lifetime::destroyed);
}
"""


def completed(destination):
    shutil.copytree(PACK / "starter", destination)
    learner=(destination/'state_review.cpp').read_text();reference=(PACK/'solution'/'state_review.cpp').read_text()
    pattern=r"(\s*// BEGIN TASK (\w+)\n)[\s\S]*?(\s*// END TASK \2\n)"
    bodies={m[2]:m[0] for m in re.finditer(pattern,reference)};assert len(bodies)==3
    learner=re.sub(pattern,lambda m:bodies[m[2]],learner);assert learner==reference
    (destination/'state_review.cpp').write_text(learner)


def oracle(events):
    table={('ready','start'):'running',('running','pause'):'paused',('paused','resume'):'running',
           ('running','finish'):'finished',('paused','finish'):'finished'}
    phase='ready';lines=[]
    for event in events:
        next_phase=table.get((phase,event))
        if next_phase:phase=next_phase
        lines.append(f"{event} {'accepted' if next_phase else 'rejected'} enum {phase} poly {phase}")
    return '\n'.join(lines+['lifetime balanced true'])+'\n'


def main():
    compiler=os.environ.get('CXX','g++');counts=[]
    with tempfile.TemporaryDirectory(prefix='cppi6-state-native-') as tmp:
        area=Path(tmp);complete=area/'completed';completed(complete)
        harness=area/'harness.cpp';harness.write_text(HARNESS)
        sequences=list(itertools.product(['start','pause','resume','finish'],repeat=4))
        for sanitized in [False,True]:
            extra=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'] if sanitized else []
            for label,source in [('starter',PACK/'starter'),('completed',complete),('reference',PACK/'solution')]:
                folder=area/(label+('-sanitized' if sanitized else '-ordinary'));folder.mkdir();app=folder/'state-review'
                run([compiler,*FLAGS,*extra,*(source/name for name in SOURCES),'-o',app],folder,timeout=120)
                if label=='starter':
                    out,err=run([app],folder,expected=1,stdin='start\n');assert out=='' and err=='Failed: Unfinished state factory.\n';continue
                probe=folder/'probe';run([compiler,*FLAGS,*extra,'-I',source,harness,source/'state_review.cpp','-o',probe],folder,timeout=120);run([probe],folder)
                out,err=run([app],folder,stdin='');assert out=='lifetime balanced true\n' and err==''
                out,err=run([app,'extra'],folder,expected=2);assert out=='' and err=='Usage: state-review\n'
                for sequence in sequences:
                    out,err=run([app],folder,stdin='\n'.join(sequence)+'\nquit\nstart\n');assert out==oracle(sequence) and err==''
                out,err=run([app],folder,stdin='show\nunknown\n'+'x'*25+'\nshow\nquit\n');assert out=='enum ready poly ready\nenum ready poly ready\nlifetime balanced true\n' and err.count('Rejected:')==2
                if Path('/dev/full').exists():
                    with open('/dev/full','wb') as sink:out,err=run([app],folder,expected=1,stdin='start\n',stdout_stream=sink)
                    assert out is None and 'Could not write' in err
                counts.append(len(sequences))
    assert counts==[256]*4
    print(json.dumps({'event':'verified-state-review','programVariants':6,'completedLearnerEqualsReference':True,
                      'independentPhasePairs':16,'independentEventSequencesPerProgram':256,'virtualDestruction':True,
                      'actualLifetimeCounters':True,'ordinaryAndSanitized':True}),flush=True)

if __name__=='__main__':main()
