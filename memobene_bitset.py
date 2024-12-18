from collections import namedtuple
from math import inf
from memobene import get_random_local_scores

# To compact memo range of parent sets can be reduced to never include v

def parset2varset(v:int, pset:int) -> int:
  singleton = 1<<v
  mask      = singleton - 1
  low       = pset &  mask
  high      = pset & ~mask
  return (high<<1) | low

def varset2parset(v:int, vset:int):
  # assumes v not set
  singleton = 1<<v
  mask      = singleton - 1
  low       = vset &  mask
  high      = vset & ~mask
  return (high>>1) | low

Memos =  namedtuple('Memo', 'sink net_score bps bps_score local_scores')

def fill_best_parents_memos(memos:Memos):
    """Record best parent set for each variable and candidate parent set (!) PS_v.
       It is either PS_v or best parents in some of its
       smallest proper subsets. 
    """
    N = len(memos.local_scores)
    for v, (score_memo, parent_memo, ls_v) in enumerate(zip(memos.bps_score, memos.bps, memos.local_scores)):
        for PS_v in range(len(score_memo)):
            S_v = parset2varset(v, PS_v)    
            score_memo[PS_v]  = ls_v[PS_v]
            parent_memo[PS_v] = PS_v
            for w in range(N):
                if S_v & (1<<w): # if w in S_v
                    vset = S_v & ~(1<<w)
                    PS_v_w = varset2parset(v, vset) # take it out
                    # PS_v_w = ((vset & ~((1<<v)-1)) >> 1) | (vset & ((1<<v)-1))
                    if score_memo[PS_v_w] > score_memo[PS_v]:
                        score_memo[PS_v] = score_memo[PS_v_w]
                        parent_memo[PS_v] = parent_memo[PS_v_w]


def best_parents(v, PS_v, memos:Memos):
    """Return best parent set for each variable in candidate parent set (!) PS_v.
       It is either PS_v or best parents in some of its
       smallest proper subsets.
    """

    # print('PS_v', v, PS_v, bin(PS_v))
    if memos.bps[v][PS_v] != -1:
        return (memos.bps_score[v][PS_v], memos.bps[v][PS_v])

    S_v = parset2varset(v, PS_v)    

    N = len(memos.local_scores)
    best_res = (memos.local_scores[v][PS_v], PS_v)
    for w in range(N):
        if S_v & (1<<w): # if w in S_v
            PS_v_w = varset2parset(v, S_v & ~(1<<w)) # take it out
            best_res = max(best_res, best_parents(v, PS_v_w, memos))

    memos.bps_score[v][PS_v], memos.bps[v][PS_v] = best_res
    # print('set bps', v, bin(S_v), best_res[0], bin(parset2varset(v, best_res[1])))
    return best_res

def best_sink(S : int, memos:Memos):
    """ Find a best sink for network for variables in S.
        It is the node v with score that equals
        the score of v's parents in S-{v} + score of best net for S-{v} 
    """
    if not S:
        return 0, -1
    
    if memos.sink[S] != -1:
        return (memos.net_score[S], memos.sink[S])

    N = len(memos.local_scores)
    best_res = (-inf, 0)
    for v in range(N):
        if S & (1<<v):
            bps_score_memo = memos.bps_score[v]
            S_v = S & ~(1<<v)
            # p_score, _bps = best_parents(v, varset2parset(v, S_v), memos)
            bps_score = bps_score_memo[varset2parset(v, S_v)]
            (subnet_score, _next_sink) = best_sink(S_v, memos)
            score = bps_score + subnet_score
            best_res = max(best_res, (score, v))
    
    memos.net_score[S], memos.sink[S] = best_res
    return best_res

def best_net(N, memos:Memos):
    nof_sets = 1<<N
    S = nof_sets - 1

    net = [None] * N    
    for i in range(N):
        if memos.sink[S] == -1:
            _score, sink = best_sink(S, memos)
        else:
            sink  = memos.sink[S]
        S = S & ~ (1<<sink)
        # bps_score, bps = best_parents(sink, varset2parset(sink, S), memos)
        bps_score = memos.bps_score[sink][varset2parset(sink, S)]
        bps       = memos.bps[sink][varset2parset(sink, S)]
        net[i] = (sink, parset2varset(sink, bps), bps_score)

    return net

def main(args):
    def set2bitset(S):
        bs = 0
        for i in S:
            bs += (1<<i)
        return bs

    N = args.nof_vars
    nof_sets = 1<<N

    if args.resdir:
        local_scores0 = read_local_scores(args.resdir, args.nof_vars)
    else:
        local_scores0 = get_random_local_scores(N, args.seed)
    local_scores = [[0.0]*(nof_sets//2)  for v in range(N)]
    for v in local_scores0:
        for ss, ls in local_scores0[v].items():
            local_scores[v][varset2parset(v, set2bitset(ss))] = ls 

    # There are 2x2 tables for memoizing
    # For each set, a best sink and the score of the best network if you use that sink
    # For each variable and a set S_v (not containing v), best parents for v in S_v and the score of those parents
    memos = Memos(sink = [-1] * nof_sets,
                  net_score = [0.0] * nof_sets, 
                  bps = [[-1] * (nof_sets//2) for v in range(N)],
                  bps_score = [[0.0] * (nof_sets//2) for v in range(N)],
                  local_scores = local_scores
    )

    start_time = time.perf_counter()
    fill_best_parents_memos(memos)
    pss = best_net(N, memos)
    total_score = 0.0
    for v,ps,s in pss:
        total_score += s
        print(v, bin(ps), s)

    print(total_score, f'{time.perf_counter() - start_time:.2}s')

if __name__ == '__main__':
    import time
    from argparse import ArgumentParser
    from local_scores_io import read_local_scores

    parser = ArgumentParser()
    parser.add_argument('nof_vars', type=int)
    parser.add_argument('seed', type=int)
    parser.add_argument('--resdir')
    args = parser.parse_args()
    main(args)    
