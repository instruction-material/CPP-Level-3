# Worked state comparison

The four-by-four table in the worksheet has five accepted pairs. `Ready` accepts
only start; `Running` accepts pause and finish; `Paused` accepts resume and finish;
`Finished` accepts none. The reference enum table and each actual derived type
implement these same entries independently.

In the worked show/pause/start/pause/resume/finish/finish trace, five State objects
are created: the initial Ready plus Running, Paused, Running and Finished. Four
old states are destroyed during replacements, and the final Finished is destroyed
when Machine leaves scope. Both illegal pause-from-ready and finish-from-finished
leave the same object alive. The actual driver reports balanced lifetime after
that scope; it does not merely print a fixed claim.

For `start`, `pause`, `finish`, four objects are created and destroyed: Ready,
Running, Paused and Finished. Pause-to-finish is legal and requires no intermediate
Running. The factory returns owning pointers to actual derived types, and the
virtual destructor reaches their destructors. A candidate allocation happens
before swap, so a throwing allocation retains the prior Machine state.

For this bounded, closed four-phase table, keep the enum in the core rover. Its
state is already composed into Snapshot with graph, position and movement count.
The command interface remains polymorphic because commands supply distinct
operations. Introducing State objects becomes a separate architectural choice
when phase behavior grows, not a prerequisite for command dispatch.
