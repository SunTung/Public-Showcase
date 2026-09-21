#!/usr/bin/env python3
"""
Independent direct verifier for a RESTRICTED K6,D=3 model.

Scope (important):
  * simple K6: one edge per unordered vertex pair;
  * each such edge has one fixed ordered pair of endpoint colours;
  * after choosing three pairwise-edge-disjoint monochromatic witness matchings,
    the 9 witness edges have fixed monochromatic endpoint colours 0,1,2;
  * the remaining 6 edges each have two endpoint-colour variables in {0,1,2};
  * a support is the 9 forced witness edges plus any subset of the 6 free edges.

The program does NOT encode or solve the unrestricted Krenn-Gu model with multiple
endpoint-colour edge types per vertex pair. It verifies only the restricted model above.

Method: brute-force all 3^12 endpoint-colour assignments for each symmetry-reduced
support type and directly count inherited-vertex-colouring (IVC) buckets. No symbolic
UNSAT/DSU machinery from the companion certificate verifier is used.
"""
from itertools import combinations, permutations, product
from collections import Counter

V = tuple(range(6))
E = tuple((i,j) for i in V for j in V if i < j)


def gen_pms(vertices):
    vertices = tuple(vertices)
    if not vertices:
        return [()]
    a = vertices[0]
    out = []
    for k in range(1, len(vertices)):
        b = vertices[k]
        rest = vertices[1:k] + vertices[k+1:]
        for tail in gen_pms(rest):
            out.append(tuple(sorted(((min(a,b), max(a,b)),) + tail)))
    return sorted(set(out))

PM = gen_pms(V)
PM_INDEX = {m:i for i,m in enumerate(PM)}
PM_EDGES = [frozenset(m) for m in PM]
assert len(PM) == 15


def canon_edge(a,b):
    return (a,b) if a < b else (b,a)


def permute_matching(m, p):
    return tuple(sorted(canon_edge(p[a], p[b]) for a,b in m))


def bipartite_union(triple):
    adj = {v:set() for v in V}
    for mi in triple:
        for a,b in PM[mi]:
            adj[a].add(b); adj[b].add(a)
    colour = {}
    for s in V:
        if s in colour:
            continue
        colour[s] = 0
        q = [s]
        for u in q:
            for w in adj[u]:
                if w in colour:
                    if colour[w] == colour[u]:
                        return False
                else:
                    colour[w] = 1-colour[u]
                    q.append(w)
    return True


DISJOINT_TRIPLES = [
    t for t in combinations(range(15),3)
    if all(PM_EDGES[a].isdisjoint(PM_EDGES[b]) for a,b in combinations(t,2))
]
assert len(DISJOINT_TRIPLES) == 80
assert sum(bipartite_union(t) for t in DISJOINT_TRIPLES) == 20
assert sum(not bipartite_union(t) for t in DISJOINT_TRIPLES) == 60
PRISM = next(t for t in DISJOINT_TRIPLES if not bipartite_union(t))
K33   = next(t for t in DISJOINT_TRIPLES if bipartite_union(t))


def support_orbit_reps(witness):
    forced = set().union(*(PM_EDGES[i] for i in witness))
    free = tuple(sorted(set(E)-forced))
    witness_set = set(witness)

    # Vertex permutations stabilizing the UNLABELLED set of the 3 witnesses.
    actions = []
    for p in permutations(V):
        image = {PM_INDEX[permute_matching(PM[i], p)] for i in witness}
        if image == witness_set:
            action = tuple(free.index(canon_edge(p[a],p[b])) for a,b in free)
            actions.append(action)

    def move(mask, action):
        y = 0
        for i,j in enumerate(action):
            if (mask >> i) & 1:
                y |= 1 << j
        return y

    unseen = set(range(64))
    reps = []
    while unseen:
        x = min(unseen)
        orb = {move(x,g) for g in actions}
        reps.append(x)
        unseen -= orb
    return forced, free, len(actions), tuple(reps)


def assignment_has_no_mixed_singleton(witness, forced, free, mask, digits):
    # Endpoint colours for every present edge.
    ec = {}
    for c,mi in enumerate(witness):
        for a,b in PM[mi]:
            ec[(a,b,a)] = c
            ec[(a,b,b)] = c
    for k,(a,b) in enumerate(free):
        if (mask >> k) & 1:
            ec[(a,b,a)] = digits[2*k]
            ec[(a,b,b)] = digits[2*k+1]

    support = set(forced)
    for k,e in enumerate(free):
        if (mask >> k) & 1:
            support.add(e)

    buckets = Counter()
    for m,edges in zip(PM,PM_EDGES):
        if not edges.issubset(support):
            continue
        ivc = [None]*6
        for a,b in m:
            ivc[a] = ec[(a,b,a)]
            ivc[b] = ec[(a,b,b)]
        buckets[tuple(ivc)] += 1

    for ivc,n in buckets.items():
        mono = all(x == ivc[0] for x in ivc)
        if (not mono) and n == 1:
            return False
    return True


def verify_geometry(name, witness):
    forced, free, stab, reps = support_orbit_reps(witness)
    rows = []
    total_assignments_checked = 0

    # For absent free edges, their endpoint colours are irrelevant. Enumerating all 12
    # digits would duplicate work. Enumerate only endpoints of present free edges.
    # This is still a direct exhaustive verifier of every semantically distinct colouring.
    for mask in reps:
        present = [k for k in range(6) if (mask >> k) & 1]
        slots = [2*k+s for k in present for s in (0,1)]
        nchecked = 0
        witness_found = None
        for vals in product(range(3), repeat=len(slots)):
            digits = [0]*12
            for s,v in zip(slots, vals):
                digits[s] = v
            nchecked += 1
            if assignment_has_no_mixed_singleton(witness, forced, free, mask, digits):
                witness_found = tuple(digits)
                break
        total_assignments_checked += nchecked
        assert witness_found is None, (name, mask, witness_found)
        rows.append((mask, nchecked, "UNSAT"))

    return {
        "name": name,
        "witness": witness,
        "stabilizer": stab,
        "support_orbits": len(reps),
        "reps": reps,
        "rows": rows,
        "assignments_checked": total_assignments_checked,
    }


def main():
    print("MODEL = restricted fixed-endpoint-colour simple K6")
    print("PM =", len(PM))
    print("pairwise-disjoint witness triples = 80 = 60 prism + 20 K3,3")
    grand_orbits = 0
    grand_checks = 0
    for name,w in (("prism",PRISM),("K3,3",K33)):
        r = verify_geometry(name,w)
        grand_orbits += r["support_orbits"]
        grand_checks += r["assignments_checked"]
        print(f"\n{name}: witness={r['witness']} stabilizer={r['stabilizer']} support_orbits={r['support_orbits']}")
        print("support reps =", r["reps"])
        for row in r["rows"]:
            print(row)
        print("semantic endpoint assignments checked =", r["assignments_checked"])
    assert grand_orbits == 23
    print("\nPASS: all 23 support-orbit representatives are UNSAT by direct IVC-bucket enumeration.")
    print("total semantic endpoint assignments checked =", grand_checks)

if __name__ == "__main__":
    main()
