from functools import cache
import time

from memobene import get_random_local_scores


@cache
def best_parents(v,S_v):
    
    def gen_scores():
        yield (local_scores[v][S_v], S_v)
        for w in range(N):
            if S_v & (1<<w):
                S_v_w = S_v & ~(1<<w)
                bps_score, bps = best_parents(v,S_v_w)
                yield (local_scores[v][bps], S_v_w)

    return max(gen_scores())

@cache
def best_sink(S : int):
    if not S:
        return 0, None
    
    def gen_sink_scores():
        for v in range(N):
            if S & (1<<v):
                S_v = S & ~(1<<v)
                p_score, bps = best_parents(v,S_v)
                (n_score, next_sink) = best_sink(S_v)
                score = p_score + n_score
                yield  (score, v)
    
    return max(gen_sink_scores())

def best_net(S):
    for i in range(N):
        score, sink = best_sink(S)
        S = S & ~ (1<<sink)
        bps_score, bps = best_parents(sink, S)
        yield (sink, bps, bps_score)


if __name__ == '__main__':
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
    local_scores0 = get_random_local_scores(N, args.seed)

    S = (1<<N) - 1
    local_scores = [[0.0]*(2**N)  for v in range(N)]
    for v in local_scores0:
        for ss, ls in local_scores0[v].items():
            local_scores[v][set2bitset(ss)] = ls 

    start_time = time.time()
    pss = best_net(S)
    total_score = 0.0
    for v,ps,s in pss:
        total_score += s
        print(v, ps, s)

    print(total_score, f'{time.time() - start_time:.2}s')
