#!/usr/bin/env python3
"""
Exact symbolic certificate verifier for a RESTRICTED K6,D=3 model.

Scope (important):
  * simple K6: one edge per unordered vertex pair;
  * each edge has one fixed ordered pair of endpoint colours;
  * three nonzero monochromatic witness matchings therefore use pairwise-disjoint
    primitive edges;
  * witness edges are forced nonzero and the remaining six primitive edges may
    independently be present or absent.

This is NOT a verifier for the unrestricted Krenn-Gu model that permits distinct
endpoint-colour edge types on the same vertex pair.

The certificate uses only perfect matchings, support survival and exact endpoint-
colour equality constraints. No floating point or numerical weight optimisation is used.
"""
from itertools import combinations, permutations, product

V=range(6)
E=[(i,j) for i in V for j in V if i<j]
EI={e:i for i,e in enumerate(E)}

def pms(vs):
    vs=tuple(vs)
    if not vs: return [()]
    a=vs[0]; out=[]
    for k in range(1,len(vs)):
        b=vs[k]; rest=vs[1:k]+vs[k+1:]
        for m in pms(rest):
            out.append(tuple(sorted(((min(a,b),max(a,b)),)+m)))
    return sorted(set(out))

PM=pms(V)
IDX={m:i for i,m in enumerate(PM)}
EM=[frozenset(m) for m in PM]
assert len(PM)==15

def bipartite_union(t):
    adj=[set() for _ in V]
    for i in t:
        for a,b in PM[i]:
            adj[a].add(b); adj[b].add(a)
    col={}
    for s in V:
        if s in col: continue
        col[s]=0; q=[s]
        for u in q:
            for w in adj[u]:
                if w in col and col[w]==col[u]: return False
                if w not in col:
                    col[w]=1-col[u]; q.append(w)
    return True

TRIPLES=[t for t in combinations(range(15),3)
         if all(EM[a].isdisjoint(EM[b]) for a,b in combinations(t,2))]
assert len(TRIPLES)==80
PRISM=next(t for t in TRIPLES if not bipartite_union(t))
K33=next(t for t in TRIPLES if bipartite_union(t))
assert sum(not bipartite_union(t) for t in TRIPLES)==60
assert sum(bipartite_union(t) for t in TRIPLES)==20

def ce(a,b): return (a,b) if a<b else (b,a)
def ppm(m,p): return tuple(sorted(ce(p[a],p[b]) for a,b in m))

def support_orbits(rep):
    W=set().union(*(EM[i] for i in rep))
    F=sorted(set(E)-W)
    G=[]
    R=set(rep)
    for p in permutations(V):
        images={IDX[ppm(PM[i],p)] for i in rep}
        if images==R:
            G.append(tuple(F.index(ce(p[a],p[b])) for a,b in F))
    def act(mask,g):
        z=0
        for i,j in enumerate(g):
            if mask>>i&1: z|=1<<j
        return z
    unseen=set(range(64)); orbits=[]
    while unseen:
        x=min(unseen)
        o={act(x,g) for g in G}
        orbits.append(sorted(o)); unseen-=o
    return W,F,G,orbits

class DSU:
    def __init__(self):
        self.p=list(range(15))
        self.c=[None]*12+[0,1,2]
    def find(self,x):
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]
            x=self.p[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b: return True
        ca,cb=self.c[a],self.c[b]
        if ca is not None and cb is not None and ca!=cb: return False
        self.p[b]=a
        self.c[a]=ca if ca is not None else cb
        return True

def consistent(eqs):
    d=DSU()
    return all(d.union(a,b) for a,b in eqs)

def verify(rep):
    W,F,G,ORBS=support_orbits(rep)

    edge_colour={}
    for c,mi in enumerate(rep):
        for e in PM[mi]: edge_colour[e]=c

    slot={}
    for i,e in enumerate(F):
        for side,v in enumerate(e): slot[(e,v)]=2*i+side

    expr=[]
    for m in PM:
        row=[None]*6
        for e in m:
            for v in e:
                row[v]=12+edge_colour[e] if e in edge_colour else slot[(e,v)]
        expr.append(row)

    def alternatives(mi,alive):
        ans=[]
        for c in range(3):
            ans.append(tuple((x,12+c) for x in expr[mi]))
        for mj in alive:
            if mj!=mi:
                ans.append(tuple(zip(expr[mi],expr[mj])))
        return [a for a in ans if consistent(a)]

    cert=[]
    for orb in ORBS:
        mask=min(orb)
        T={F[i] for i in range(6) if mask>>i&1}
        S=W|T
        alive=[i for i,m in enumerate(EM) if set(m)<=S]
        ALT={i:alternatives(i,alive) for i in alive}
        core=None; checked=None; counts=None
        for size in (1,2,3):
            for K in combinations(alive,size):
                n=1
                for i in K: n*=len(ALT[i])
                sat=False
                for choice in product(*(ALT[i] for i in K)):
                    eqs=[e for block in choice for e in block]
                    if consistent(eqs):
                        sat=True; break
                if not sat:
                    core=K; checked=n
                    counts=tuple(len(ALT[i]) for i in K)
                    break
            if core is not None: break
        assert core is not None
        cert.append((mask,core,counts,checked))
    return len(G),len(ORBS),cert

def main():
    print("MODEL = restricted fixed-endpoint-colour simple K6")
    print("PM =",len(PM))
    print("disjoint witness triples =",len(TRIPLES), "= 60 prism + 20 K3,3")
    total=0
    for name,rep in (("prism",PRISM),("K3,3",K33)):
        g,n,cert=verify(rep); total+=n
        print("\n",name,"witness",rep,"stabilizer",g,"support orbits",n)
        for row in cert: print(row)
        print("maximum minimum core size =",max(len(x[1]) for x in cert))
    assert total==23
    print("\nPASS: restricted model: 23/23 support-orbit representatives have an exact UNSAT core of size <= 3.")

if __name__=="__main__":
    main()
