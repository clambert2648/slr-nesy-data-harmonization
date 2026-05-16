# Glossary — NeSy & KG Alignment

*SLR companion glossary — Constance Lambert-Tremblay — UQO 2026*

Stable reference for terms encountered during A.5/A.6 extraction. Primary anchor: Cotovio et al. (2023). Updated as new concepts emerge from the corpus.

---

## Formal logic & ontology foundations

### Signature — Sig(O)
The vocabulary of an ontology: the set of all entity names declared in O. Formally the disjoint union of four sets — N_C (named concepts/classes), N_R (named object properties), N_D (data properties), and N_I (named individuals).
*Source: Cotovio §2.1*

### Axiom
A formal statement asserted as true in an ontology, expressed in the syntax of its underlying description logic. Axioms collectively define what is necessarily entailed by the ontology.
*Source: Cotovio §2.1*

### Satisfiability
A concept C is satisfiable in ontology O if there exists at least one possible interpretation in which C has non-empty extension. Unsatisfiable concepts (C ⊑ ⊥) cannot have any instance without contradicting O.
*Source: Cotovio §2.1.1*

### Coherence
Property of an ontology where every named concept is satisfiable. An incoherent ontology contains at least one unsatisfiable concept; reasoning over it produces meaningless answers.
*Source: Cotovio §2.1.1*

### Consistency Principle
Constraint that an aligned KG (KG_M = KG ∪ KG' ∪ M) must not introduce unsatisfiable concepts that did not exist in either source ontology alone. Violations indicate flawed mappings or incompatibilities between source ontologies.
*Source: Cotovio §2.1.1*

### Deductive difference — diff_Σ(KG, KG')
The set of axioms over signature Σ = Sig(KG) ∪ Sig(KG') that hold in KG' but not in KG. Quantifies the new entailments introduced by alignment.
*Source: Cotovio §2.1.1*

### Description Logic (DL)
Family of formal logics designed for representing and reasoning over structured knowledge. Provides decidable fragments of first-order logic with well-defined complexity.
*Source: general*

### OWL profiles (EL, EL++, DL-Lite, SROIQ)
Sub-languages of OWL DL with different expressivity-vs-tractability tradeoffs. EL is lightweight (efficient reasoning over hierarchies); EL++ adds property hierarchies and nominals; DL-Lite is optimized for query answering over large data; SROIQ is the full OWL 2 DL fragment.
*Source: general / corpus context*

---

## Semantic Web stack

### RDF (Resource Description Framework)
W3C data model representing information as triples ⟨subject, predicate, object⟩. The atomic structure of all Semantic Web data; aggregating triples produces a directed labeled graph.
*Source: general*

### RDFS (RDF Schema)
Lightweight vocabulary on top of RDF for declaring classes, properties, sub-class/sub-property hierarchies, domain and range constraints. Sufficient for taxonomies; insufficient for formal reasoning beyond hierarchy.
*Source: general*

### OWL (Web Ontology Language)
W3C standard for ontologies layered on RDFS, adding equivalence, disjointness, restrictions, cardinality constraints, transitive/symmetric/functional properties, and class expressions. Supports formal Description Logic reasoning.
*Source: general*

### SPARQL
W3C query language for RDF data. Pattern-based: queries describe sub-graphs to match, with filters, optional patterns, and aggregations.
*Source: general*

### Knowledge Graph (KG)
A structured, graph-based representation of knowledge in a domain — entities as nodes, relationships as labeled edges, often grounded in an OWL ontology. Industry-popularized term (Google, 2012); functionally overlaps with Semantic Web ontologies but is technology-agnostic (RDF or property graphs).
*Source: Cotovio §1, general*

### Parsing
Transforming a linear character string (e.g. an OWL file, a SPARQL query) into a structured data representation (tree, graph, object) according to grammatical rules. The bridge between specifications and operational code.
*Source: general*

---

## Knowledge graph alignment pipeline

### KG Alignment (KGA)
Task of automatically identifying semantically equivalent or related entities, relationships, and attributes across two or more knowledge graphs. Output is a set of mappings establishing correspondences between signatures.
*Source: Cotovio §1*

### Mapping ⟨e₁, e₂, r, c⟩
A single correspondence in an alignment: e₁ ∈ Sig(KG₁), e₂ ∈ Sig(KG₂), r is a semantic relation (≡, ⊑, ⊒), c ∈ [0,1] is a confidence score.
*Source: Cotovio §2.1*

### Alignment M
The set of all mappings produced between two KGs. K^M denotes M after the repair phase has filtered incoherent mappings.
*Source: Cotovio §2.1*

### Candidate Generation Function G
First stage of alignment: G takes an entity from KG₁ and proposes a set of candidate entities from KG₂ that may correspond to it, using labels, descriptions, types, or relational structure. Recall-oriented (errs toward false positives).
*Source: Cotovio §2.1.2*

### Filter Function F
Second stage of alignment: evaluates candidate mappings produced by G, eliminates those with low confidence or violating cardinality/coherence constraints. May also repair mappings by mitigating logical inconsistencies.
*Source: Cotovio §2.1.2*

### Mapping Repair
Process of removing or correcting mappings whose collective effect violates the consistency principle. Typically performed post-hoc using Description Logic reasoners (Pellet, HermiT, ELK).
*Source: Cotovio §2.1.1, §4.1*

### Blocking
Pre-processing step in entity resolution and KGA that reduces the comparison space by grouping likely-similar entities together, avoiding the quadratic cost of comparing all pairs.
*Source: Obraczka & Rahm 2025 (corpus)*

### Reference Alignment
A manually curated, gold-standard alignment used for training (supervised setting) or evaluation (unsupervised setting) of KGA systems. Source of ground truth for precision/recall/F1 metrics.
*Source: Cotovio §2.1.3*

### OAEI (Ontology Alignment Evaluation Initiative)
Annual community benchmark for KGA systems, with multiple tracks (Anatomy, Conference, Largebio, Bio-ML, etc.) providing reference alignments. The de facto evaluation standard for the field.
*Source: Cotovio §2.2*

### Functionality (of a relation)
Degree to which a relation r tends to map a head entity to a unique tail entity. Formally:

> fun(r) = |{h | ∃t : r(h, t)}| / |{(h, t) | r(h, t)}|, with fun(r) ∈ [0, 1].

fun(r) = 1 iff r is strictly functional (e.g., hasCapital generally assigns one capital per country). Exploited by PARIS and FLORA to propagate alignments: if h ≡ h' and r, r' are both functional with r(h, t) and r'(h', t'), then t ≡ t' is licensed.
*Source: Peng et al. 2025 (FLORA, §3); originally Suchanek et al. 2011 (PARIS)*

### Local functionality
Head-specific variant: fun(r, h) = 1 / |{t | r(h, t)}|, equal to 1 iff r maps h to a unique tail. Required to handle relations that are globally functional but admit local exceptions — e.g., hasCapital is non-functional for South Africa (Pretoria, Bloemfontein, Cape Town). FLORA uses both global and local functionality jointly: global functionality avoids spurious matches under KG incompleteness, local functionality avoids missing exceptions.
*Source: Peng et al. 2025 (FLORA, §3)*

### Functionality of a relation list
Extension of functionality to a list R = (r₁, …, rₙ) of relations applied to a list H = (h₁, …, hₙ) of head entities sharing a common tail t:

> fun(R) = |{H | ∃t, R(H, t)}| / |{(H, t) | R(H, t)}|.

Captures combinatorial functionality: BirthDateOf and FamilyNameOf are each non-functional, but the pair is — few people share both a birth date and a family name. This is the structural generalization that lets FLORA go beyond PARIS's single-relation propagation and align entities through multi-fact structural evidence.
*Source: Peng et al. 2025 (FLORA, §5.1)*

---

## Optimization & decision frameworks

### Hard vs Soft Constraint
A hard constraint is binary: any violation invalidates the entire alignment (consist returns 0). A soft constraint penalizes violations on a continuous scale (softconsist applies a logistic function over the count of incoherences). Soft constraints are differentiable; hard constraints are not — a fundamental requirement for neural training.
*Source: Cotovio §2.1.2, §4.3*

### Assumption of Correctness vs Uncertainty
Two philosophical stances when optimizing alignment under coherence pressure. Correctness: the source ontologies are perfect, so any incoherent mapping is wrong. Uncertainty: ontologies may be incomplete or erroneous, so high-confidence mappings can override coherence violations.
*Source: Cotovio §2.1.2*

### Heuristic
A practical rule or learned procedure that produces good-enough answers efficiently, without guaranteeing optimality. Used wherever theoretically optimal solutions are intractable. NeSy systems often replace hand-crafted heuristics with learned ones.
*Source: Cotovio §4.2*

### Adversarial Training (for KGA)
Training framework where a generator G (proposing mappings) and a discriminator D (evaluating coherence) are trained jointly in opposition. G learns to produce globally coherent alignments rather than locally good mappings post-hoc filtered. Internalizes repair into mapping. Requires soft consistency (LTN/LNN as D) for differentiability.
*Source: Cotovio §4.1, §4.3*

### GAN (Generative Adversarial Network)
Training framework where two neural networks compete: a generator G produces candidates and a discriminator D judges them, both improving through opposition until G's outputs are indistinguishable from the target distribution.
*Source: Goodfellow 2014, general*

---

## Symbolic, subsymbolic & neuro-symbolic

### Symbolic AI
Approach to AI based on explicit, human-readable knowledge representation (formal logic, rules, ontologies) and symbol manipulation. Strengths: interpretability, formal deduction. Weaknesses: brittleness, expert-effort to encode, difficulty with continuous domains.
*Source: Cotovio §3*

### Subsymbolic AI
Approach to AI based on distributed numerical representations (embeddings, neural activations) rather than discrete named symbols. Knowledge is positional in vector space, not pointable on any single value. Synonymous in practice with neural/connectionist methods.
*Source: Cotovio §3*

### Deduction
Reasoning from general rules to particular conclusions. If premises are true and the inference is valid, the conclusion is guaranteed true. Native to symbolic systems (DL reasoners, OWL inference).
*Source: Cotovio §1, general*

### Induction
Reasoning from particular examples to general patterns. Conclusion is never guaranteed; it is probabilized by the quantity and representativeness of examples. Native to subsymbolic systems (neural networks learn by induction over datasets).
*Source: Cotovio §3, general*

### Abduction
Inference to the best explanation: from an observation, infer the most plausible hypothesis that would explain it. Neither guaranteed (deduction) nor purely statistical (induction). Often implicit in explainability mechanisms.
*Source: general*

### Neuro-Symbolic AI (NeSy)
AI subfield aiming to integrate symbolic reasoning (knowledge representation, logical inference) with subsymbolic learning (deep learning, embeddings) to leverage complementary strengths. Sometimes called Neurosymbolic AI or NSai.
*Source: Cotovio §1, §3*

### Kautz's NeSy Taxonomy (Type I–VI)
Six levels of symbolic-subsymbolic integration. Type I: standard DL with symbolic I/O. Type II: loosely-coupled hybrid (e.g. AlphaGo). Type III: neural model + symbolic reasoner cooperating on complementary tasks. Type IV: neural net trained with symbolic constraints. Type V: tightly-coupled with logic-as-regularizer (LTN, LNN approach). Type VI: full integration of symbolic engine inside neural network — currently aspirational.
*Source: Cotovio §3.1; Kautz 2022*

### Tightly vs Loosely Coupled NeSy
Loosely coupled: symbolic and subsymbolic components operate in sequence, exchanging discrete inputs/outputs (e.g. BERT generates candidates, then OWL reasoner repairs). Tightly coupled: components are integrated within a single architecture, with continuous information flow (LTN, LNN, fuzzy NeSy).
*Source: Cotovio §3.1*

### Logic Tensor Networks (LTN)
Tightly-coupled NeSy framework combining deep neural networks with first-order fuzzy logic. Embeds elements of a formal language into vector space, enabling logical formulas to be evaluated as continuous functions and integrated with neural training.
*Source: Cotovio §3.1; Badreddine et al. 2022*

### Logical Neural Networks (LNN)
Tightly-coupled NeSy framework establishing a one-to-one correspondence between neurons and logical formulas. Each neuron's activation function approximates a logical operator. Inherently interpretable; current implementations limited by scalability.
*Source: Cotovio §3.1; Riegel et al. 2020*

### Fuzzy Logic
Multi-valued logic where truth values are real numbers in [0,1] rather than binary. Operators (T-norms for AND, T-conorms for OR) generalize classical logic. Underlies LTN and FLORA (corpus); makes logical reasoning differentiable.
*Source: general; Peng et al. 2025 (FLORA, §4)*

### Fuzzy Inference System (FIS)
Rule-based reasoning system that combines fuzzy operators to compute outputs from inputs expressed as membership degrees in [0, 1]. In its Mamdani-style form, rules read "p₁ is P₁ ∧ ... ∧ pₙ is Pₙ ⇒ c is C", with three stages: (i) fuzzification — mapping crisp inputs to membership values via a fuzzy set's membership function µ; (ii) aggregation — combining premises into a firing strength via an aggregation function ϕ (often a T-norm); (iii) defuzzification — collapsing the output fuzzy set into a scalar value. FLORA uses an FIS to integrate heterogeneous signals (lexical similarity, structural similarity, relation functionality) in a single principled framework that yields interpretable explanations of alignments.
*Source: Peng et al. 2025 (FLORA, §4); Sabri 2013; Mamdani-style*

### Simple Positive FIS
Restricted form of FIS introduced in FLORA: all membership functions reduce to identity, no negation is allowed, and defuzzification uses the First-of-Maxima (FoM) method. A rule has the form P₁ ∧ ... ∧ Pₙ →[ϕ] C, where each Pᵢ has a known value in [0, 1] and C is an output variable. A solution is the smallest assignment of output variables such that every rule is satisfied (output ≥ firing strength). The simplification enables a clean fixed-point semantics needed for KGA.
*Source: Peng et al. 2025 (FLORA, §4, Def. 1)*

### Recursive FIS
A Simple Positive FIS in which output variables may also appear as premises (cyclic dependencies allowed) — the form required by FLORA, because entity alignment and relation alignment mutually depend on each other. Solved by fixed-point iteration (Algorithm 1 of FLORA): initialize outputs to 0, then for each rule update its output variable to the max of its current value and the rule's firing strength, until convergence. By the Knaster–Tarski fixed-point theorem, the iteration provably converges to the least fixed point provided every aggregation function is continuous and non-decreasing.
*Source: Peng et al. 2025 (FLORA, §4, Def. 2 + Thm. 1)*

---

## Embedding & neural architectures for KGA

### Embedding
Dense vector representation of an entity, concept, word, or graph element in a continuous space. Geometric proximity in the embedding space is intended to reflect semantic similarity.
*Source: general*

### TransE
Translation-based KG embedding model: relations are translations in vector space (h + r ≈ t for triples ⟨h, r, t⟩). Foundational for many KGA approaches.
*Source: Bordes et al. 2013, corpus context*

### Graph Neural Network (GNN)
Neural architecture operating directly on graph-structured data, propagating information between nodes via their connectivity. GCN, GAT (Graph Attention) are common variants used in KGA for capturing structural patterns.
*Source: general*

### BERTMap-style Approaches
Family of KGA systems leveraging pre-trained language models (BERT) for semantic similarity, fine-tuned on ontology textual content. Strong on textual/lexical matching but require formal post-processing (mapping repair) for logical coherence.
*Source: He et al. 2021 (rank 286)*

---

## Explainability for KGA

### Post-hoc Explanation
Explanation generated after a model has produced a decision, by analyzing the decision externally. The model itself remains a black box; explanation is an added layer.
*Source: Cotovio §4.5*

### Intrinsic Explanation
Explanation arising from the model's architecture itself: the decision mechanism IS the explanation. Faithfulness is guaranteed by construction. Property of tightly-coupled NeSy systems (LTN, LNN, FLORA).
*Source: Cotovio §4.5*

### Concept Induction
Post-hoc method: given a model decision, find a formal concept (DL class expression) from a background ontology that best correlates with the activation pattern. Output: a named formal concept the user can read and validate. Answers "what kind of thing is this?"
*Source: Cotovio §4.5; Sarker, Geng, Dalal*

### Path-based Explanation
Post-hoc method: justify a decision by exhibiting a sequence of edges (a chain of relations) in the KG connecting the entities involved. Output: a graph path the user can trace step by step. Answers "how is this connected?"
*Source: Cotovio §4.5; Xiong, Zhu*

### Faithfulness (of an explanation)
Property of an explanation that accurately reflects the actual computation performed by the model. Post-hoc explanations risk unfaithfulness (the explanation rationalizes rather than describes); intrinsic NeSy explanations are faithful by construction.
*Source: general / Cotovio §4.5*

---

## Human-in-the-loop (HITL) & validation

### Human-in-the-Loop (HITL)
Architectural pattern where human input is integrated at runtime into an automated system, typically for validation, correction, or learning from feedback. Central to RQ2: HITL converts explainability from a property into a workflow.
*Source: Cotovio §4.4; thesis RQ2*

### Human-in-the-Loop Reinforcement Learning (HLRL)
RL framework where reward signals are derived from human preferences rather than from a fixed reward function. Underpins RLHF in modern LLMs; identified by Cotovio as a candidate for KGA mapping validation.
*Source: Cotovio §4.4*

### Mapping Validation
Expert review of automatically generated mappings, accepting or rejecting them based on domain knowledge. Bottleneck of current KGA pipelines; key motivation for tools that surface explanations alongside mappings.
*Source: general / corpus context*

---

*SLR NeSy — Glossary v1 (EN) — C. Lambert-Tremblay — UQO 2026*
