# A Mixed-Fiber Singleton Obstruction and Exact Computer-Assisted Certificate for a Restricted Fixed-Endpoint-Colour $K_6,D=3$ Perfect-Matching Model

**Submission manuscript — version 1.1 — 21 September 2026**

**Public showcase copy:** author and correspondence metadata are intentionally omitted from this display copy.  
**Affiliation:** Independent Researcher, Taiwan

**Keywords:** perfect matching; inherited vertex colouring; complex edge weights; computer-assisted proof; finite obstruction; Krenn-Gu problem

**MSC (suggested):** 05C70, 05C15

## Abstract

We study a restricted fixed-endpoint-colour simple-graph $K_6,D=3$ perfect-matching model. Every unordered vertex pair supports exactly one primitive edge; each primitive edge carries one fixed ordered pair of endpoint colours and one complex weight. The target amplitudes are one for the three monochromatic inherited vertex colourings and zero for every mixed inherited vertex colouring.

We prove nonexistence by combining a human-readable structural reduction with two materially different exact finite verifiers. Nonzero monochromatic amplitudes force three nonzero monochromatic perfect-matching witnesses. Because primitive edges have fixed endpoint colours, witnesses for distinct monochromatic colours are pairwise edge-disjoint and force a nine-edge nonzero backbone. Their union has exactly two possible geometries, the triangular prism and $K_{3,3}$. The six remaining primitive edges give $64$ raw supports per witness geometry, which reduce under witness-set symmetries to $13+10=23$ support orbits.

The first verifier directly enumerates inherited-colouring fibers for every semantically distinct endpoint-colour assignment on the surviving optional edges and checks $1,217,855$ assignments in total. It proves that every support orbit forces a mixed inherited-colouring fiber containing exactly one nonzero perfect-matching monomial. The second verifier uses exact endpoint-colour equality constraints and finds an UNSAT core of size at most three surviving perfect matchings for every one of the $23$ support orbits. A mixed singleton fiber has no nonzero cancellation partner, so its amplitude cannot vanish, independently of complex phase. Hence the restricted target system is impossible.

The theorem applies only to the stated fixed-endpoint-colour simple-graph model. It is strictly narrower than the unrestricted Krenn-Gu problem, in which multiple endpoint-colour edge types may occur on the same vertex pair, and it does not resolve the general Krenn-Gu conjecture. Its contribution is a compact structural obstruction and a small, reproducible certificate for this restricted calibration model.

## 1. Introduction

Inherited vertex colourings of perfect matchings provide a graph-theoretic formulation of interference constraints arising in quantum-optical state generation. In the formulation of Krenn, Gu, and Soltész, an edge has a colour at each endpoint and a complex weight. A perfect matching induces a colouring of all vertices, and the amplitude of an inherited vertex colouring is the sum of the monomials contributed by all perfect matchings that induce it [1].

The unrestricted problem permits an undirected graph that need not be simple. In particular, different endpoint-colour edge types may occur between the same pair of vertices. The present work deliberately studies a smaller calibration model: the underlying graph is the simple graph $K_6$, there is exactly one primitive edge for each unordered vertex pair, and each primitive edge has one fixed ordered endpoint-colour pair from three colours. This restriction is essential in the witness-disjointness argument below and is retained in every theorem.

The purpose of this paper is twofold. First, we give a complete finite nonexistence certificate for this restricted model. Second, we isolate the common structural mechanism behind all finite contradictions: a **mixed nonzero singleton fiber** of the inherited-colouring map. Once such a fiber exists, the associated mixed amplitude consists of exactly one nonzero monomial and cannot be canceled by any complex phase choice.

The proof has three layers. The analytic layer derives nonzero monochromatic witnesses, their pairwise edge-disjointness, and a nine-edge nonzero backbone. A short combinatorial layer classifies the possible witness unions. The remaining universal finite statement is then checked by two exact programs that use different contradiction mechanisms: direct inherited-colouring bucket enumeration and symbolic equality/UNSAT-core certification.

A public Lean-checked artifact released in 2026 establishes the stronger unrestricted $(6,3)$ nonexistence theorem over the full coloured-edge model [4]. The result proved here is therefore not a new parameter-range theorem. Its intended contribution is instead explanatory compression: within the stated restricted model, the contradiction can be expressed as a short support-and-fiber mechanism and verified by a small finite certificate that can be rerun directly.

## 2. Restricted model and notation

Let

$$
V=\{1,2,3,4,5,6\},\qquad G=K_6.
$$

For every unordered vertex pair $\{i,j\}$ with $i<j$, there is exactly one primitive edge $e_{ij}$. The edge has one fixed ordered pair of endpoint colours

$$
\bigl(\kappa_{ij}(i),\kappa_{ij}(j)\bigr)\in\{0,1,2\}^2
$$

and one complex weight $w_{ij}\in\mathbb C$.

A perfect matching $M$ of $K_6$ consists of three pairwise vertex-disjoint primitive edges covering all six vertices. Its monomial is

$$
z(M)=\prod_{e\in M}w_e. \qquad (1)
$$

The fixed endpoint colours induce a vertex colouring

$$
\Phi(M)\in\{0,1,2\}^6.
$$

For any vertex colouring $c\in\{0,1,2\}^6$, define the amplitude

$$
A(c)=\sum_{M:\,\Phi(M)=c}z(M). \qquad (2)
$$

The restricted target system requires

$$
A(0^6)=A(1^6)=A(2^6)=1, \qquad (3)
$$

and

$$
A(c)=0\qquad\text{for every non-monochromatic }c. \qquad (4)
$$

Define the set of nonzero perfect matchings

$$
\mathcal M^{\times}=\{M:z(M)\neq0\}, \qquad (5)
$$

and, for each colouring $c$, the nonzero inherited-colouring fiber

$$
F_c=\{M\in\mathcal M^{\times}:\Phi(M)=c\}. \qquad (6)
$$

A mixed colouring $c$ with $|F_c|=1$ is called a **mixed nonzero singleton fiber**.

## 3. Analytic witness reduction

### Lemma 1 (Nonzero monochromatic witnesses)

For every colour $a\in\{0,1,2\}$, there exists a perfect matching $M_a$ such that

$$
\Phi(M_a)=a^6,
\qquad
z(M_a)\neq0.
$$
