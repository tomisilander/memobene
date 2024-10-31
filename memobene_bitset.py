from collections import namedtuple
from memobene import get_random_local_scores

Memos =  namedtuple('Memo', 'sink sink_score bps bps_score')

def best_parents(v,S_v, memos:Memos):
    """Return best parents for v in candidate set S_v.
       They are either S_v or best parents in some of its
       smallest proper subsets.
    """
    
    if memos.bps[v][S_v] != -1:
        return (memos.bps_score[v][S_v], memos.bps[v][S_v])
    
    def gen_scores():
        yield (local_scores[v][S_v], S_v)
        for w in range(N):
            if S_v & (1<<w): # if w in S_v
                S_v_w = S_v & ~(1<<w) # take it out
                bps_score, bps = best_parents(v, S_v_w, memos)
                yield (local_scores[v][bps], S_v_w)

    best_res = max(gen_scores())
    memos.bps_score[v][S_v], memos.bps[v][S_v] = best_res
    return best_res

def best_sink(S : int, memos:Memos):
    if not S:
        return 0, -1
    
    if memos.sink[S] != -1:
        return (memos.sink_score[S], memos.sink[S])

    def gen_sink_scores():
        for v in range(N):
            if S & (1<<v):
                S_v = S & ~(1<<v)
                p_score, bps = best_parents(v,S_v, memos)
                (n_score, next_sink) = best_sink(S_v, memos)
                score = p_score + n_score
                yield  (score, v)
    
    best_res = max(gen_sink_scores())
    memos.sink_score[S], memos.sink[S] = best_res
    return best_res

def best_net(N, memos:Memos):
    nof_sets = 1<<N
    S = nof_sets - 1
    
    for i in range(N):
        if memos.sink[S] == -1:
            _score, sink = best_sink(S, memos)
        else:
            sink  = memos.sink[S]
        S = S & ~ (1<<sink)
        bps_score, bps = best_parents(sink, S, memos)
        yield (sink, bps, bps_score)


if __name__ == '__main__':
    import time
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('nof_vars', type=int)
    parser.add_argument('seed', type=int)
    args = parser.parse_args()
    
    def set2bitset(S):
        bs = 0
        for i in S:
            bs += (1<<i)
        return bs

    N = args.nof_vars
    nof_sets = 1<<N

    local_scores0 = get_random_local_scores(N, args.seed)
    local_scores = [[0.0]*nof_sets  for v in range(N)]
    for v in local_scores0:
        for ss, ls in local_scores0[v].items():
            local_scores[v][set2bitset(ss)] = ls 

    memos = Memos(sink = [-1] * nof_sets,
                  sink_score = [0.0] * nof_sets, 
                  bps = [[-1] * nof_sets for v in range(N)],
                  bps_score = [[0.0] * nof_sets for v in range(N)]
    )

    start_time = time.time()
    pss = best_net(N, memos)
    total_score = 0.0
    for v,ps,s in pss:
        total_score += s
        print(v, bin(ps), s)

    print(total_score, f'{time.time() - start_time:.2}s')
