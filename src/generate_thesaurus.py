# generate_thesaurus.py
# Génère le fichier thésaurus VOSviewer à partir des mots-clés réels du corpus
# Format : terme_original <TAB> terme_canonique

thesaurus = {

    # ── NEURO-SYMBOLIQUE (toutes variantes → terme canonique) ─────────────────
    'neuro-symbolic':                           'neuro-symbolic ai',
    'neuro-symbolic approach':                  'neuro-symbolic ai',
    'neuro-symbolic artificial intelligence':   'neuro-symbolic ai',
    'neuro-symbolic computing':                 'neuro-symbolic ai',
    'neuro-symbolic integration':               'neuro-symbolic ai',
    'neuro-symbolic intelligence':              'neuro-symbolic ai',
    'neuro-symbolic learning':                  'neuro-symbolic ai',
    'neuro-symbolic models':                    'neuro-symbolic ai',
    'neuro-symbolic reasoning':                 'neuro-symbolic ai',
    'neuro-symbolic systems':                   'neuro-symbolic ai',
    'neural symbolic reasoning':                'neuro-symbolic ai',
    'neural-symbolic':                          'neuro-symbolic ai',
    'neural-symbolic computing':                'neuro-symbolic ai',
    'neural-symbolic integration':              'neuro-symbolic ai',
    'neural-symbolic learning':                 'neuro-symbolic ai',
    'neural-symbolic learning and reasoning':   'neuro-symbolic ai',
    'neural-symbolic reasoning':                'neuro-symbolic ai',
    'neural-symbolic system':                   'neuro-symbolic ai',
    'neurosymbolic':                            'neuro-symbolic ai',
    'neurosymbolic ai':                         'neuro-symbolic ai',
    'neurosymbolic integration':                'neuro-symbolic ai',
    'neurosymbolic learning':                   'neuro-symbolic ai',
    'neurosymbolic reasoning':                  'neuro-symbolic ai',

    # ── KNOWLEDGE GRAPH ───────────────────────────────────────────────────────
    'knowledge graphs':                         'knowledge graph',
    'knowledge graph (kg)':                     'knowledge graph',
    'knowledge graphs (kg)':                    'knowledge graph',
    'knowledge graphs (kgs)':                   'knowledge graph',

    # ── KNOWLEDGE GRAPH EMBEDDING ─────────────────────────────────────────────
    'knowledge graph embeddings':               'knowledge graph embedding',

    # ── LARGE LANGUAGE MODELS ─────────────────────────────────────────────────
    'large language model':                     'large language models',
    'large language model (llm)':               'large language models',
    'large language models (llms)':             'large language models',
    'large language model agent':               'large language models',
    'llm':                                      'large language models',
    'llms':                                     'large language models',
    'language models':                          'large language models',

    # ── EXPLAINABLE AI ────────────────────────────────────────────────────────
    'explainable ai (xai)':                     'explainable ai',
    'explainable artificial intelligence':      'explainable ai',
    'explainable artificial intelligence (xai)':'explainable ai',
    'explainability':                           'explainable ai',
    'xai':                                      'explainable ai',

    # ── ONTOLOGY ──────────────────────────────────────────────────────────────
    'ontologies':                               'ontology',

    # ── GRAPH NEURAL NETWORKS ─────────────────────────────────────────────────
    'graph neural network':                     'graph neural networks',
    'graph neural networks (gnn)':              'graph neural networks',
    'graph neural networks (gnns)':             'graph neural networks',
    'gnn':                                      'graph neural networks',

    # ── GRAPH CONVOLUTIONAL NETWORK ───────────────────────────────────────────
    'graph convolutional networks':             'graph convolutional network',
    'graph convolutional neural network':       'graph convolutional network',
    'graph convolutional neural networks':      'graph convolutional network',
    'graph convolution network':                'graph convolutional network',

    # ── GRAPH ATTENTION NETWORK ───────────────────────────────────────────────
    'graph attention network (gat)':            'graph attention network',

    # ── GRAPH EMBEDDING ───────────────────────────────────────────────────────
    'graph embeddings':                         'graph embedding',

    # ── NLP ───────────────────────────────────────────────────────────────────
    'natural language processing (nlp)':        'natural language processing',
    'nlp':                                      'natural language processing',

    # ── DEEP LEARNING ─────────────────────────────────────────────────────────
    'deep neural network':                      'deep learning',
    'deep neural networks':                     'deep learning',

    # ── TRANSFORMER ───────────────────────────────────────────────────────────
    'transformer models':                       'transformer',
    'transformer model':                        'transformer',
    'transformer architecture':                 'transformer',
    'transformers':                             'transformer',

    # ── RETRIEVAL-AUGMENTED GENERATION ────────────────────────────────────────
    'retrieval augmented generation':           'retrieval-augmented generation',
    'retrieval-augmented generation (rag)':     'retrieval-augmented generation',
    'retrieval-enhanced generation':            'retrieval-augmented generation',
    'rag':                                      'retrieval-augmented generation',

    # ── RECOMMENDER SYSTEMS ───────────────────────────────────────────────────
    'recommender system':                       'recommender systems',
    'recommendation system':                    'recommender systems',
    'recommendation systems':                   'recommender systems',

    # ── CONVOLUTIONAL NEURAL NETWORK ──────────────────────────────────────────
    'convolutional neural network (cnn)':       'convolutional neural network',
    'convolutional neural networks':            'convolutional neural network',
    'cnn':                                      'convolutional neural network',

    # ── MULTIMODAL ────────────────────────────────────────────────────────────
    'multi-modal':                              'multimodal',
    'multi-modal data':                         'multimodal',
    'multi-modal fusion':                       'multimodal fusion',
    'multi-modal knowledge graph':              'multimodal knowledge graph',
    'multi-modal entity alignment':             'multimodal entity alignment',
    'multi-modal learning':                     'multimodal learning',

    # ── DATA HARMONIZATION ────────────────────────────────────────────────────
    'data harmonisation':                       'data harmonization',

    # ── ELECTRONIC HEALTH RECORDS ─────────────────────────────────────────────
    'electronic health record':                 'electronic health records',
    'ehr':                                      'electronic health records',

    # ── ARTIFICIAL INTELLIGENCE ───────────────────────────────────────────────
    'ai':                                       'artificial intelligence',

    # ── EMBEDDING ─────────────────────────────────────────────────────────────
    'embeddings':                               'embedding',

    # ── WORD EMBEDDING ────────────────────────────────────────────────────────
    'word embeddings':                          'word embedding',

    # ── DESCRIPTION LOGICS ────────────────────────────────────────────────────
    'description logic':                        'description logics',

    # ── DIGITAL TWIN ──────────────────────────────────────────────────────────
    'digital twins':                            'digital twin',

    # ── MULTI-AGENT SYSTEMS ───────────────────────────────────────────────────
    'multi-agent system':                       'multi-agent systems',

    # ── GENERATIVE AI ─────────────────────────────────────────────────────────
    'generative artificial intelligence':       'generative ai',

    # ── LSTM ──────────────────────────────────────────────────────────────────
    'long short-term memory':                   'lstm',
    'long short term memory (lstm)':            'lstm',

    # ── TRUSTWORTHY AI ────────────────────────────────────────────────────────
    'trustworthy artificial intelligence':      'trustworthy ai',

    # ── HYBRID AI ─────────────────────────────────────────────────────────────
    'hybrid artificial intelligence':           'hybrid ai',

    # ── PRE-TRAINED LANGUAGE MODEL ────────────────────────────────────────────
    'pre-trained language models':              'pre-trained language model',
    'pretrained language model':                'pre-trained language model',

    # ── CONTEXT AWARENESS ─────────────────────────────────────────────────────
    'context-awareness':                        'context awareness',

    # ── BIM ───────────────────────────────────────────────────────────────────
    'building information modelling (bim)':     'bim',

    # ── E-COMMERCE ────────────────────────────────────────────────────────────
    'ecommerce':                                'e-commerce',

    # ── HUMAN-IN-THE-LOOP ─────────────────────────────────────────────────────
    'human-in-the-loop (hitl)':                 'human-in-the-loop',

    # ── BERT ──────────────────────────────────────────────────────────────────
    'sentence-bert':                            'bert',

    # ── KNOWLEDGE BASE ────────────────────────────────────────────────────────
    'knowledge base embedding':                 'knowledge graph embedding',

    # ── SEMANTIC WEB ──────────────────────────────────────────────────────────
    'semantic web technologies':                'semantic web',
    'semantic web integration':                 'semantic web',

    # ── NAMED ENTITY RECOGNITION ──────────────────────────────────────────────
    'named entity recognition (ner)':           'named entity recognition',

    # ── QUESTION ANSWERING ────────────────────────────────────────────────────
    'question answering system':                'question answering',
    'question-answering system':                'question answering',

    # ── SYMBOLIC AI ───────────────────────────────────────────────────────────
    'symbolic ai':                              'symbolic ai',   # déjà canonique

    # ── KNOWLEDGE REPRESENTATION ──────────────────────────────────────────────
    'knowledge representation and reasoning':   'knowledge representation',

    # ── ONTOLOGY MATCHING ─────────────────────────────────────────────────────
    'complex ontology matching':                'ontology matching',
    'biomedical ontology matching':             'ontology matching',
    'complex ontology alignment':               'ontology alignment',

}

# ── Écriture du fichier ────────────────────────────────────────────────────────
output_path = 'results/tables/vosviewer_thesaurus.txt'

import os
os.makedirs('results/tables', exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('label\treplace by\n')   # ← en-tête obligatoire VOSviewer
    for original, canonical in sorted(thesaurus.items()):
        f.write(f'{original}\t{canonical}\n')

print(f"✓ Thésaurus généré : {len(thesaurus)} règles de normalisation")
print(f"  Fichier : {output_path}")
print()

# Résumé par groupe
groups = {
    'Neuro-symbolique': [k for k in thesaurus if 'neuro' in k or 'neural-sym' in k or 'neurosym' in k],
    'Knowledge graph':  [k for k in thesaurus if 'knowledge graph' in k and 'embedding' not in k],
    'LLM':              [k for k in thesaurus if 'language model' in k or k in ('llm','llms')],
    'Explainable AI':   [k for k in thesaurus if 'explain' in k or k == 'xai'],
    'GNN':              [k for k in thesaurus if 'graph neural' in k or k == 'gnn'],
}
print("── Groupes principaux ──")
for grp, keys in groups.items():
    print(f"  {grp:<20} : {len(keys)} variantes normalisées")
