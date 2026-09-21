**Proof.** Equation (3) expresses $A(a^6)$ as a finite sum of perfect-matching monomials equal to one. If every monomial in that sum were zero, the sum would be zero. Hence at least one contributing monomial is nonzero. $\square$

### Lemma 2 (Pairwise edge-disjoint monochromatic witnesses)

Any nonzero monochromatic witness for one colour is edge-disjoint from every monochromatic witness for a different colour. In particular, $M_0,M_1,M_2$ are pairwise edge-disjoint.

**Proof.** Suppose $M_a$ and $M_b$, with $a\neq b$, shared a primitive edge $e_{ij}$. Since $M_a$ induces $a^6$, the fixed endpoint-colour pair of $e_{ij}$ must be $(a,a)$. Since $M_b$ induces $b^6$, the same primitive edge must have endpoint-colour pair $(b,b)$. A primitive edge in the restricted model has only one fixed endpoint-colour pair, a contradiction. $\square$

### Corollary 3 (Nine-edge nonzero backbone)

The union

$$
W=M_0\cup M_1\cup M_2
$$

contains nine distinct primitive edges, and every edge of $W$ has nonzero weight.

**Proof.** Each perfect matching has three edges and the three witnesses are pairwise edge-disjoint, so $|W|=9$. Since each witness monomial is a product of three complex weights and is nonzero, every edge weight appearing in a witness is nonzero. $\square$

Since $K_6$ has fifteen primitive edges, exactly six edges lie outside $W$. Every candidate nonzero-edge support therefore has the form

$$
E^{\times}=W\cup T,
\qquad
T\subseteq E(K_6)\backslash W. \qquad (7)
$$

Thus, once a witness triple is selected, there are only

$$
2^6=64 \qquad (8)
$$

raw zero/nonzero choices for the six optional edges.

## 4. Witness-union geometry

### Proposition 4 (Eighty witness triples and two union geometries)

$K_6$ has exactly $80$ unordered triples of pairwise edge-disjoint perfect matchings. The union of any such triple is isomorphic to exactly one of two connected cubic graphs on six vertices: the triangular prism or $K_{3,3}$. Exactly $60$ triples have triangular-prism union and $20$ have $K_{3,3}$ union.

**Proof.** $K_6$ has $15$ perfect matchings. For a fixed perfect matching $M_1$, exactly $8$ of the remaining perfect matchings are edge-disjoint from $M_1$. If $M_1$ and $M_2$ are edge-disjoint, then $M_1\cup M_2$ is a $6$-cycle. Exactly $4$ perfect matchings are edge-disjoint from both. Hence the number of ordered pairwise-edge-disjoint triples is

$$
15\cdot8\cdot4=480,
$$

so the number of unordered triples is $480/3!=80$.

The union of three pairwise edge-disjoint perfect matchings is a simple $3$-regular graph on six vertices. It is connected because a component of a simple cubic graph has at least four vertices, so two components cannot fit on six vertices. The connected cubic graphs on six vertices are the triangular prism and $K_{3,3}$.

There are $10$ unordered bipartitions of six labelled vertices into two parts of size three, hence $10$ labelled copies of $K_{3,3}$. Each $K_{3,3}$ has exactly two unordered $1$-factorizations into three perfect matchings. Therefore $10\cdot2=20$ witness triples have $K_{3,3}$ union, and the remaining $80-20=60$ have triangular-prism union. $\square$

This proposition removes the witness-union classification from the computational burden. Computation begins only after the nine-edge backbone and the two witness geometries have been established.

## 5. Finite support reduction

Fix one representative witness triple for each of the two geometries. The nine witness edges are forced nonzero and the six complementary primitive edges are optional. The $64$ raw supports are acted on by the stabilizer of the unordered witness set under vertex permutations.

For the triangular-prism representative, the stabilizer has order $12$ and the $64$ supports reduce to $13$ orbits. For the $K_{3,3}$ representative, the stabilizer has order $36$ and the $64$ supports reduce to $10$ orbits. Hence the entire remaining support domain consists of

$$
13+10=23 \qquad (9)
$$

support-orbit representatives.

The canonical support masks used by the verifiers are

$$
\begin{aligned}
\text{prism: }&0,1,3,5,6,7,15,19,23,25,27,31,63,\\
K_{3,3}:\;&0,1,3,5,7,15,28,29,31,63.
\end{aligned} \qquad (10)
$$

Both verification programs reconstruct the fifteen perfect matchings, the eighty pairwise-edge-disjoint witness triples, the $60+20$ geometry split, the witness-set stabilizers, and the same $13+10$ support-orbit decomposition from the public model definition.

## 6. Structural route: mixed-fiber singleton forcing

### Lemma 5 (A mixed singleton is immediately impossible)

If $c$ is mixed and $|F_c|=1$, then the target system (3)-(4) cannot be satisfied.

**Proof.** Let $F_c=\{M^\star\}$. Every matching inducing $c$ other than $M^\star$ has zero monomial. Therefore

$$
A(c)=z(M^\star). \qquad (11)
$$

Because $M^\star\in\mathcal M^{\times}$,

$$
z(M^\star)\neq0, \qquad (12)
$$

so $A(c)\neq0$, contradicting the mixed target equation $A(c)=0$. $\square$

The key universal statement is therefore purely finite and combinatorial: can the six optional edges and their fixed endpoint colours be chosen so that every mixed nonzero fiber has cardinality either zero or at least two?

### Theorem 6 (Mixed-fiber singleton obstruction; computer-assisted)

In the restricted fixed-endpoint-colour simple-graph $K_6,D=3$ model, suppose the three monochromatic amplitudes satisfy (3). Choose, for each monochromatic colour, any perfect matching contributing a nonzero monomial to that amplitude. For every nonzero-edge support and fixed endpoint-colour assignment compatible with those witnesses, there exists a mixed colouring $c$ with

$$
|F_c|=1. \qquad (13)
$$

**Computational proof.** By Lemmas 1-2 and Corollary 3, every hypothetical solution supplies a pairwise-edge-disjoint witness triple, a nine-edge nonzero backbone, one of the two geometries of Proposition 4, and one of the $23$ support-orbit representatives of Section 5.

For every support representative, the direct verifier enumerates every semantically distinct endpoint-colour assignment on the optional edges that are present. Absent optional edges have no semantic endpoint colours and are not redundantly enumerated. For each assignment, the verifier constructs every surviving perfect matching, computes its inherited vertex colouring, groups surviving perfect matchings into fibers, and asks whether all mixed fibers avoid cardinality one.
