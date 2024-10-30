from itertools import chain, combinations
from functools import cache
import time

from random import random, seed 



def powerset(S):
    return chain.from_iterable(combinations(S, r) for r in range(len(S)+1))

def get_local_scores(N):
    S = frozenset(range(N))
    return {v: {frozenset(ss):random() for ss in powerset(S-{v})} for v in S}
    
N = 14
S = frozenset(range(N))
seed(666)
local_scores = get_local_scores(N)

@cache
def best_parents(v,S_v):
    
    def gen_scores():
        yield (local_scores[v][S_v], S_v)
        for w in S_v:
            S_v_w = S_v - {w}
            _bps_score, bps = best_parents(v,S_v_w)
            yield (local_scores[v][bps], S_v_w)

    return max(gen_scores())

@cache
def best_sink(S:frozenset):
    
    if not S:
        return 0, None
    
    def gen_sink_scores():
        for v in S:
            S_v = S - {v}
            p_score, bps = best_parents(v,S_v)
            (n_score, _next_sink) = best_sink(S_v)
            score = p_score + n_score
            yield  (score, v)
    
    return max(gen_sink_scores())

def parents(S):
    for i in range(N):
        score, sink = best_sink(S)
        S = S - {sink}
        bps_score, bps = best_parents(sink, S)
        yield (sink, bps, bps_score)

start_time = time.time()
# ps = sorted(list(parents(S)))
ps = parents(S)
total_score = 0.0
for v,ps, s in ps:
    total_score += s
    print(v, ps, s)

print(total_score, f'{time.time() - start_time:.2}s')
