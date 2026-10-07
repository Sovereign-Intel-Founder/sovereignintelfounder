---------------- MODULE formal_lockfree_spec ----------------
EXTENDS Naturals, Sequences, TLC

CONSTANTS Threads, MaxVal
VARIABLES head, tail, memory

Init == 
    /\ head = 1
    /\ tail = 1
    /\ memory = [i \in 1..10 |-> 0]

Push(t) == 
    /\ tail <= 10
    /\ memory' = [memory EXCEPT ![tail] = t]
    /\ tail' = tail + 1
    /\ UNCHANGED head

Next == \E t \in 1..MaxVal : Push(t)

Spec == Init /\ [][Next]_<<head, tail, memory>>
=============================================================
