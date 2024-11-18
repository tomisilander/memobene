from itertools import chain, combinations
from functools import cache
from random import random, seed as set_seed

def powerset(S):
    return chain.from_iterable(combinations(S, r) for r in range(len(S)+1))

def get_random_local_scores(N, seed):
    set_seed(seed)
    S = frozenset(range(N))
    return {v: {ss:random() for ss in map(frozenset, powerset(S-{v}))} for v in S}
    
@cache
def best_parents(v,S_v):
    """Finds best parents for v in in S_v"""
    def gen_scores():
        yield (local_scores[v][S_v], S_v)
        for w in S_v:
            yield best_parents(v,S_v - {w})
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

def best_net(S):
    for i in range(N):
        score, sink = best_sink(S)
        S = S - {sink}
        bps_score, bps = best_parents(sink, S)
        yield (sink, bps, bps_score)

if __name__ == '__main__':
    import time
    from argparse import ArgumentParser
    from local_scores_io import read_local_scores

    parser = ArgumentParser()
    parser.add_argument('nof_vars', type=int)
    parser.add_argument('seed', type=int)
    parser.add_argument('--resdir')
    args = parser.parse_args()
    
    N = args.nof_vars
    S = frozenset(range(N))
    if args.resdir:
        local_scores = read_local_scores(args.resdir, args.nof_vars)
    else:
        local_scores = get_random_local_scores(N, args.seed)

    start_time = time.time()
    pss = best_net(S)
    total_score = 0.0
    for v,ps,s in pss:
        total_score += s
        print(v, ps, s)
    print(total_score, f'{time.time() - start_time:.2}s')
