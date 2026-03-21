"""Build snowballing.csv from survey and included-article backward snowballing."""
import pandas as pd

rows = []

# ===== SURVEY SNOWBALLING (23 articles) =====
sv = [
    dict(id="SV-01", tier=1, year=2021, authors="Chen, Jiménez-Ruiz, Horrocks, Antonyrajah",
         title="Augmenting Ontology Alignment by Semantic Embedding and Distant Supervision",
         doi="10.1007/978-3-030-77385-4_23", source_surveys="Cotovio_2023",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-02", tier=1, year=2020, authors="Sun, Wang, Hu, Chen, Dai, Zhang, Qu",
         title="Knowledge Graph Alignment Network with Gated Multi-Hop Neighborhood Aggregation",
         doi="10.1609/aaai.v34i01.5354", source_surveys="Cotovio_2023",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-03", tier=1, year=2021, authors="Trojahn, Vieira, Schmidt, Pease",
         title="Foundational Ontologies Meet Ontology Matching: A Survey",
         doi="10.3233/sw-210447", source_surveys="Portisch_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-04", tier=1, year=2020, authors="Riegel, Gray, Luus, Khan, Makondo, Akhalwaya, Qian, Fagin, Barahona, Sharma, Ikbal, Karanam, Neelam, Likhyani, Srivastava",
         title="Logical Neural Networks",
         doi="10.48550/arxiv.2006.13155", source_surveys="Cotovio_2023",
         in_corpus="oui", corpus_rank="132; 389", corpus_decision="exclude", priority=""),
    dict(id="SV-05", tier=1, year=2021, authors="Zhang, Chen, Zhang, Ke, Ding",
         title="Neural, Symbolic and Neural-Symbolic Reasoning on Knowledge Graphs",
         doi="10.1016/j.aiopen.2021.03.001", source_surveys="Cheng_2024",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-06", tier=1, year=2022, authors="Kaoudi, Martinez Lorenzo, Markl",
         title="Towards Loosely-Coupling Knowledge Graph Embeddings and Ontology-based Reasoning",
         doi="", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-07", tier=1, year=2021, authors="Jain, Tran, Gad-Elrab, Stepanova",
         title="Improving Knowledge Graph Embeddings with Ontological Reasoning",
         doi="10.1007/978-3-030-88361-4_24", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-08", tier=1, year=2021, authors="Cheng, Yang, Zhang, Sun",
         title="UniKER: A Unified Framework for Combining Embedding and Definite Horn Rule Reasoning for Knowledge Graph Inference",
         doi="10.18653/v1/2021.emnlp-main.769", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-09", tier=1, year=2022, authors="Cheng, Liu, Wang, Sun",
         title="RLogic: Recursive Logical Rule Learning from Knowledge Graphs",
         doi="10.1145/3534678.3539421", source_surveys="Cheng_2024",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-10", tier=1, year=2023, authors="Cheng, Ahmed, Sun",
         title="Neural Compositional Rule Learning for Knowledge Graph Reasoning",
         doi="10.48550/arxiv.2303.03581", source_surveys="Cheng_2024",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-11", tier=1, year=2020, authors="Iyer, Agarwal, Kumar",
         title="VeeAlign: A Supervised Deep Learning Approach to Ontology Alignment",
         doi="", source_surveys="Portisch_2025",
         in_corpus="oui", corpus_rank="591; 604", corpus_decision="exclude", priority=""),
    dict(id="SV-12", tier=1, year=2019, authors="Qu, Tang",
         title="Probabilistic Logic Neural Networks for Reasoning",
         doi="", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-13", tier=1, year=2022, authors="Boschin, Jain, Keretchashvili, Suchanek",
         title="Combining Embeddings and Rules for Fact Prediction",
         doi="10.4230/OASIcs.AIB.2022.4", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-14", tier=1, year=2020, authors="Minervini, Riedel, Stenetorp, Grefenstette",
         title="Learning Reasoning Strategies in End-to-End Differentiable Proving",
         doi="10.3233/faia210359", source_surveys="Cheng_2024",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-15", tier=2, year=2023, authors="d'Avila Garcez, Lamb",
         title="Neurosymbolic AI: The 3rd Wave",
         doi="10.1007/s10462-023-10448-w", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-16", tier=2, year=2020, authors="De Raedt, Dumančić, Manhaeve, Marra",
         title="From Statistical Relational to Neuro-Symbolic Artificial Intelligence",
         doi="10.24963/ijcai.2020/688", source_surveys="Zhang_2024",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-17", tier=2, year=2017, authors="Besold, d'Avila Garcez, Bader, Bowman",
         title="Neural-Symbolic Learning and Reasoning: A Survey and Interpretation",
         doi="10.48550/arxiv.1711.03902", source_surveys="Breit_2023",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-18", tier=2, year=2020, authors="Hitzler, Bianchi, Ebrahimi, Sarker",
         title="Neural-Symbolic Integration and the Semantic Web",
         doi="10.3233/sw-190368", source_surveys="Breit_2023",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-19", tier=2, year=2021, authors="Sarker, Zhou, Eberhart, Hitzler",
         title="Neuro-Symbolic Artificial Intelligence: Current Trends",
         doi="10.3233/AIC-210084", source_surveys="Breit_2023",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-20", tier=2, year=2022, authors="Hitzler, Eberhart, Ebrahimi, Sarker",
         title="Neuro-Symbolic Approaches in Artificial Intelligence",
         doi="10.1093/nsr/nwac035", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-21", tier=2, year=2016, authors="Serafini, d'Avila Garcez",
         title="Logic Tensor Networks: Deep Learning and Logical Reasoning from Data and Knowledge",
         doi="10.48550/arxiv.1606.04422", source_surveys="Zhang_2024",
         in_corpus="oui", corpus_rank="412; 1063", corpus_decision="exclude", priority=""),
    dict(id="SV-22", tier=2, year=2020, authors="Lamb, Garcez, Gori, Prates",
         title="Graph Neural Networks Meet Neural-Symbolic Computing: A Survey and Perspective",
         doi="10.24963/ijcai.2020/670", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="SV-23", tier=2, year=2020, authors="Cropper, Dumančić, Muggleton",
         title="Turning 30: New Ideas in Inductive Logic Programming",
         doi="10.24963/ijcai.2020/673", source_surveys="DeLong_2025",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
]

# ===== BACKWARD SNOWBALLING FROM INCLUDED ARTICLES (27 articles) =====
bt = [
    dict(id="BT-01", tier=1, year=2021, authors="Chen, Hu, Jiménez-Ruiz, Horrocks",
         title="OWL2Vec*: Embedding of OWL Ontologies",
         doi="", source_articles="286, 665",
         in_corpus="oui", corpus_rank="143", corpus_decision="include",
         priority="haute — cité par 3 articles inclus, OWL axioms + embeddings"),
    dict(id="BT-02", tier=1, year=2021, authors="Racharak T.",
         title="Concept Similarity in DL ELH with Pretrained Word Embedding",
         doi="", source_articles="169, 211",
         in_corpus="non", corpus_rank="", corpus_decision="",
         priority="haute — article parent de 169 et 211"),
    dict(id="BT-03", tier=1, year=2021, authors="Qi, Zhang, Chen et al.",
         title="Unsupervised KG Alignment by Probabilistic Reasoning and Semantic Embedding",
         doi="", source_articles="330, 1889, 58",
         in_corpus="non", corpus_rank="", corpus_decision="",
         priority="haute — cité par 3 articles inclus, raisonnement probabiliste + embeddings"),
    dict(id="BT-04", tier=1, year=2021, authors="Chen, Jiménez-Ruiz, Horrocks, Antonyrajah",
         title="Augmenting Ontology Alignment by Semantic Embedding and Distant Supervision",
         doi="10.1007/978-3-030-77385-4_23", source_articles="286",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-05", tier=1, year=2022, authors="Kaoudi, Martinez Lorenzo, Markl",
         title="Towards Loosely-Coupling KG Embeddings and Ontology-based Reasoning",
         doi="", source_articles="7 (survey DeLong_2025)",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-06", tier=1, year=2022, authors="Ji Q., Li W. et al.",
         title="Embedding-Based Approach to Repairing OWL Ontologies",
         doi="", source_articles="673",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-07", tier=1, year=2023, authors="Zhu, Liu, Yao et al.",
         title="TGR: Neural-Symbolic Ontological Reasoner for Domain Knowledge Graphs",
         doi="", source_articles="673",
         in_corpus="oui", corpus_rank="127", corpus_decision="exclude",
         priority="haute — raisonneur ontologique NeSy"),
    dict(id="BT-08", tier=1, year=2023, authors="Chen, He, Jiménez-Ruiz et al.",
         title="Contextual Semantic Embeddings for Ontology Subsumption Prediction",
         doi="", source_articles="665",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-09", tier=1, year=2023, authors="He, Chen, Jiménez-Ruiz et al.",
         title="Language Model Analysis for Ontology Subsumption Inference",
         doi="", source_articles="665",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-10", tier=1, year=2023, authors="Jackermeier, Chen, Horrocks",
         title="Box²EL: Concept and Role Box Embeddings for the Description Logic EL++",
         doi="", source_articles="665",
         in_corpus="non", corpus_rank="", corpus_decision="",
         priority="haute — DL EL++ + embeddings géométriques"),
    dict(id="BT-11", tier=1, year=2023, authors="Li W., Ji Q. et al.",
         title="Graph-Based Interactive Mapping Revision in DL-Lite",
         doi="", source_articles="673",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-12", tier=1, year=2023, authors="Li Y., Lambrix P.",
         title="Repairing EL Ontologies Using Weakening and Completing",
         doi="", source_articles="673",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-13", tier=1, year=2022, authors="He, Chen et al.",
         title="ML-Friendly Biomedical Datasets for Equivalence and Subsumption Ontology Matching",
         doi="", source_articles="665",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-14", tier=1, year=2022, authors="Mao X. et al.",
         title="LightEA: Scalable, Interpretable Entity Alignment via Label Propagation",
         doi="", source_articles="58",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-15", tier=1, year=2023, authors="Cheng K. et al.",
         title="Neural Compositional Rule Learning for Knowledge Graph Reasoning",
         doi="10.48550/arxiv.2303.03581", source_articles="58",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-16", tier=1, year=2024, authors="Xu C. et al.",
         title="NALA: Effective and Interpretable Entity Alignment",
         doi="", source_articles="1889",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-17", tier=2, year=2021, authors="Zhang J., Chen B. et al.",
         title="Neural, Symbolic and Neural-Symbolic Reasoning on Knowledge Graphs",
         doi="10.1016/j.aiopen.2021.03.001", source_articles="121",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-18", tier=2, year=2021, authors="van Bekkum M. et al.",
         title="Modular Design Patterns for Hybrid Learning and Reasoning Systems",
         doi="", source_articles="121",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-19", tier=2, year=2022, authors="Hitzler P. et al.",
         title="Neuro-Symbolic Approaches in Artificial Intelligence",
         doi="10.1093/nsr/nwac035", source_articles="200",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-20", tier=2, year=2021, authors="Sarker M.K., Zhou, Eberhart, Hitzler",
         title="Neuro-Symbolic Artificial Intelligence: Current Trends",
         doi="10.3233/AIC-210084", source_articles="200",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-21", tier=2, year=2022, authors="Wang W., Yang Y., Wu F.",
         title="Survey on Neuro-Symbolic Computing",
         doi="", source_articles="1170",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-22", tier=2, year=2023, authors="Sheth A., Roy K., Gaur M.",
         title="Neurosymbolic AI — Why, What, and How",
         doi="", source_articles="200",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-23", tier=2, year=2023, authors="DeLong L.N. et al.",
         title="Neuro-Symbolic AI for Reasoning on Graph Structures: A Survey",
         doi="", source_articles="121",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-24", tier=2, year=2023, authors="Ciravegna G. et al.",
         title="Logic Explained Networks",
         doi="", source_articles="211",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-25", tier=2, year=2024, authors="Portisch J. et al.",
         title="Background Knowledge in Ontology Matching: A Survey",
         doi="", source_articles="474",
         in_corpus="oui", corpus_rank="56", corpus_decision="survey", priority=""),
    dict(id="BT-26", tier=2, year=2023, authors="Zhapa-Camacho F. et al.",
         title="mOWL: Python Library for Machine Learning with Biomedical Ontologies",
         doi="", source_articles="665",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
    dict(id="BT-27", tier=2, year=2025, authors="Mileo A.",
         title="Towards a Neuro-Symbolic Cycle for Human-Centered Explainability",
         doi="", source_articles="200",
         in_corpus="non", corpus_rank="", corpus_decision="", priority=""),
]

# Build unified DataFrame
cols = ["id", "snowball_type", "tier", "year", "authors", "title", "doi",
        "source_surveys", "source_articles", "in_corpus", "corpus_rank",
        "corpus_decision", "priority", "decision_snowball"]

all_rows = []
for r in sv:
    r["snowball_type"] = "survey"
    r["source_articles"] = ""
    r["priority"] = r.get("priority", "")
    r["decision_snowball"] = ""
    all_rows.append(r)
for r in bt:
    r["snowball_type"] = "backtracking"
    r["source_surveys"] = ""
    r["decision_snowball"] = ""
    all_rows.append(r)

df = pd.DataFrame(all_rows, columns=cols)

# Mark duplicates between SV and BT
# SV-01/BT-04: Augmenting Ontology Alignment (Chen 2021)
# SV-06/BT-05: Loosely-Coupling (Kaoudi 2022)
# SV-10/BT-15: Neural Compositional Rule Learning (Cheng 2023)
# SV-05/BT-17: Neural, Symbolic and NeSy Reasoning on KGs (Zhang 2021)
# SV-19/BT-20: Neuro-Symbolic AI Current Trends (Sarker 2021)
# SV-20/BT-19: Neuro-Symbolic Approaches in AI (Hitzler 2022)

# Add a note column for duplicates
df["notes"] = ""
dupes = {
    "BT-04": "= SV-01",
    "BT-05": "= SV-06",
    "BT-15": "= SV-10",
    "BT-17": "= SV-05",
    "BT-19": "= SV-20",
    "BT-20": "= SV-19",
}
for k, v in dupes.items():
    df.loc[df["id"] == k, "notes"] = v

# Also note the SV side
dupes_sv = {
    "SV-01": "= BT-04",
    "SV-06": "= BT-05",
    "SV-10": "= BT-15",
    "SV-05": "= BT-17",
    "SV-19": "= BT-20",
    "SV-20": "= BT-19",
}
for k, v in dupes_sv.items():
    df.loc[df["id"] == k, "notes"] = v

df.to_csv("data/processed/snowballing.csv", index=False, encoding="utf-8-sig")
print(f"Total: {len(df)} lignes")
print(f"  Survey: {(df['snowball_type']=='survey').sum()}")
print(f"  Backtracking: {(df['snowball_type']=='backtracking').sum()}")
print(f"  Tier 1: {(df['tier']==1).sum()}")
print(f"  Tier 2: {(df['tier']==2).sum()}")
print(f"  Déjà dans corpus: {(df['in_corpus']=='oui').sum()}")
print(f"  Doublons cross-type: {(df['notes']!='').sum()}")
unique = len(df) - (df['notes'].str.startswith('= SV')).sum()
print(f"  Articles uniques: {unique}")
