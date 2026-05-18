#!/usr/bin/env python3
"""
extract_slr.py — LLM-assisted data extraction for SLR NeSy (v3)
=================================================================
Pipeline: PDF → structural pre-processing → Claude API → JSON → Excel + CSV

v3 (DEC-028): descriptive-only system prompt (I4 gating removed),
              D2/D6/D7 controlled vocabularies added to PROMPT_A5,
              `role` and `i4_strict_assessment` fields removed,
              `block_mapping.csv` v3 with `status` column → retired entries
              skipped by default (override with --include-retired).

Usage:
    python extract_slr.py                       # Sequential, included only
    python extract_slr.py --batch               # Batch API (-50% cost)
    python extract_slr.py --test 3              # Calibrate on 3 articles
    python extract_slr.py --article name        # Single article by filename
    python extract_slr.py --resume              # Resume from checkpoints
    python extract_slr.py --include-retired     # Also process retired PS (audit)
    python extract_slr.py --include-standby     # Also process standby PS (default: yes)

Requires: pip install anthropic pypdf openpyxl pandas tqdm
Author: C. Lambert-Tremblay — UQO 2026
"""

import json, os, re, sys, time, argparse, logging
from pathlib import Path
from datetime import datetime
import anthropic, pandas as pd
from pypdf import PdfReader
from tqdm import tqdm

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

MODEL = "claude-opus-4-6"
MAX_TOKENS = 4096
MAX_RETRIES = 3
RETRY_BASE_DELAY = 5  # seconds, doubles each retry

# Paths — adjust to your local setup
BASE_DIR = Path(r"C:\Users\ConstanceLambert\Université du Québec en Outaouais\Projet de mémoire - NeSy Harmonisation Sémantique - General\Maitrise\SLR_thesis\data\fulltext")
PRIMARY_DIR = BASE_DIR / "Extraction"
SURVEY_DIR = BASE_DIR / "Surveys"
OUTPUT_DIR = BASE_DIR.parent / "extraction_output"

log = logging.getLogger("extract_slr")
log.setLevel(logging.INFO)
_log_ready = False

def init_logging():
    global _log_ready
    if _log_ready: return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    for h in [logging.FileHandler(OUTPUT_DIR / "extraction.log", encoding="utf-8"),
              logging.StreamHandler()]:
        h.setFormatter(fmt); log.addHandler(h)
    _log_ready = True


# ═══════════════════════════════════════════════════════════════
# SYSTEM PROMPT — descriptive only (DEC-028)
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = r"""You are an expert research assistant in neuro-symbolic AI (NeSy).
You assist a researcher (M.Sc. Computer Science, UQO) conducting a systematic literature
review on explainable semantic matching of heterogeneous indicators via NeSy approaches.

ALL extracted values MUST be in English.

YOUR ROLE IS DESCRIPTIVE, NOT DECISIONAL.

The 29 active primary studies in this corpus have all been validated as in-scope at
the inclusion stages (Tri #2 quality assessment + Tri #3 full-text audit). Two of them
(SMoG, PRASE) are documented standby cases with rebuttals on file. Do NOT re-judge
admissibility, do NOT emit exclusion verdicts, do NOT use labels like "Non-NeSy baseline".
Your task is to describe what the article does.

REFERENCE FRAMEWORKS (for descriptive labelling only):

- Kautz (2022) taxonomy of NeSy integration:
  * Type 1 (Symbolic Neuro): symbolic guides / constrains the neural
  * Type 2 (Neuro Symbolic): neural feeds the symbolic
  * Type 3 (Hybrid / Joint): bidirectional or joint integration

- Research questions of the SLR:
  * RQ1: NeSy architectures for heterogeneous semantic matching
  * RQ2: Explainability and interactive validation (HITL)
  * RQ3: Application contexts (multilingualism, M&E)

EXTRACTION QUALITY REQUIREMENTS:
- FACTUAL: do not invent. Missing information -> "Not specified".
- PRECISE: exact model names, dataset names, numeric metric values.
- CONCISE: short sentences.
- DESCRIPTIVE: report what the article says, do not editorialise.

STRUCTURAL MARKERS IN THE INPUT:
The article text contains [SECTION_LABEL] markers to help you locate information:
- NeSy architecture -> [METHODOLOGY] / [APPROACH]
- Metrics & results -> [RESULTS] / [EXPERIMENTS]
- Datasets -> [EXPERIMENTS] / [DATASETS]
- Limitations -> [DISCUSSION] / [CONCLUSION] / [LIMITATIONS]
- Contribution -> [ABSTRACT] / [INTRODUCTION] / [CONCLUSION]
"""

# ═══════════════════════════════════════════════════════════════
# EXTRACTION PROMPTS
# ═══════════════════════════════════════════════════════════════

PROMPT_A5 = r"""Extract data from this primary study according to form A.5 (v3).
Respond ONLY with valid JSON, no surrounding text. ALL values MUST be in English.

The schema combines (a) the historical A.5 narrative fields and (b) three controlled
vocabularies (D2, D6, D7) from the coding grid v2 (DEC-027). The remaining grid
dimensions (D1, D3, D4, D5) are NOT extracted here — they are coded by the researcher
at reading time on the paper form.

Exact schema:

{
  "id": "PS-XXX",
  "reference": {"authors": "", "year": 2024, "title": "", "source": ""},
  "section_1_architecture": {
    "nesy_type_kautz": "Type 1 | Type 2 | Type 3 | Not applicable",
    "neural_component": "model, embeddings, pre-training details",
    "symbolic_component": "KG, rules, ontology, constraints",
    "knowledge_representation": "OWL/DL | RDF/RDFS | Rules/Horn | None | Other: ...",
    "symbolic_inference_evidence": "where exactly the symbolic component operates at inference time (e.g. filters candidate pairs, constrains the loss, applies reasoner on outputs, generates explanations). Describe the pipeline phase, do NOT issue a PASS/FAIL verdict."
  },
  "section_2_integration": {
    "mode": "Sequential pipeline | Joint/end-to-end | Symbolic constraints | Other: ...",
    "component_interaction": "describe the flow between neural and symbolic components"
  },
  "section_3_task_evaluation": {
    "task": ["Schema matching", "Entity resolution", "Ontology alignment", "Entity alignment (inter-KG)", "Data harmonization", "Record linkage", "Semantic annotation", "Other: ..."],
    "datasets": [{"name": "", "size": "", "domain": ""}],
    "metrics_best_result": "F1 = 0.923 on Dataset X",
    "best_baseline": {"name": "", "score": "", "gap_delta": "+X.X pp", "type": "Neural | Symbolic | NeSy"},
    "ablation_study": true
  },
  "section_4_explainability": {
    "D6_hitl_explainability": "None | Trace | Interactive | Native explainability",
    "explainability_mechanism": "narrative description of the mechanism, or N/A",
    "explainability_evaluation": "how the explainability is evaluated (user study, ablation, none), or N/A",
    "hitl_details": "if HITL present: feedback mechanism, human cost, labels, iterations, time — or N/A"
  },
  "section_5_context_D7": {
    "domain": "biomedical | industrial | M&E / development | agricultural | general | other: ...",
    "multilingual": false,
    "n_languages": 1,
    "dataset_scale": "small (<5k entities) | medium (5k–50k) | large (>50k) | variable",
    "heterogeneity_type": ["Terminological", "Structural", "Linguistic", "Measurement", "Not specified"]
  },
  "section_6_knowledge_source_D2": {
    "D2_knowledge_source_type": "Lexical-taxonomic | Domain ontology-KG | Pre-trained neural | Hybrid",
    "specific_sources": "specific resources cited (WordNet, UMLS, DBpedia, BioBERT, ...)"
  },
  "section_7_reproducibility": {
    "code_available": false, "code_url": "N/A", "open_data": false, "frameworks_libraries": ""
  },
  "section_8_synthesis": {
    "main_contribution": "1 sentence",
    "limitations_reported": "as reported by the authors",
    "relevance_to_thesis": ["Reusable pipeline architecture", "Transferable embedding component", "KG/ontology component", "HITL mechanism", "Multilingual case", "Reusable benchmark", "Explainability mechanism", "M&E/dev context", "Evaluation metric/protocol", "NeSy taxonomy/classification"],
    "free_notes": ""
  }
}

CONTROLLED VOCABULARIES (DEC-027 grid v2):

D2 — Knowledge source type:
  * Lexical-taxonomic     — dictionaries, thesauri (WordNet, BabelNet, translation lexicons)
  * Domain ontology-KG    — UMLS, FMA, DBpedia, Wikidata, domain KG (incl. SPARQL endpoints)
  * Pre-trained neural    — BERT, BioBERT, fastText, sentence encoders, external LLM
  * Hybrid                — explicit combination of at least two of the above

D6 — HITL / explainability (RQ2):
  * None                  — no explanation, no human in the loop
  * Trace                 — reasoning chains, attention weights, or scores available but not interactive
  * Interactive           — human validation integrated in the algorithmic loop
  * Native explainability — explanation is an explicit design goal of the system

D7 — Application context (RQ3):
  * dataset_scale: small <5k entities | medium 5k–50k | large >50k | variable
  * multilingual: true only if the system handles ≥2 languages in matching (not just text in one language)

CRITICAL REMINDERS:
- "task": array — an article may cover multiple tasks.
- "relevance_to_thesis": select ALL applicable categories.
- "symbolic_inference_evidence": describe WHERE the symbolic component operates at inference, do NOT classify the article as PASS/FAIL on I4.
- Missing information -> "Not specified" (string) or null (boolean).
"""

PROMPT_A6 = r"""Extract data from this literature review / survey according to form A.6.
Respond ONLY with valid JSON, no surrounding text. ALL values MUST be in English.

{
  "id": "SV-XXX",
  "reference": {"authors": "", "year": 2024, "title": "", "source": ""},
  "section_1_scope": {
    "survey_type": "Mapping study | Systematic review | Narrative review | Benchmark/state of the art",
    "rq_covered": ["RQ1", "RQ2", "RQ3", "General NeSy framework"],
    "period_covered": "", "n_articles_analysed": 0,
    "role_for_thesis": "Reference taxonomy | Theoretical framing | Contextual"
  },
  "section_2_taxonomy": {
    "key_categories": "classification schema proposed by the authors",
    "adoption_for_thesis": "Adopt as-is | Adapt | Reject",
    "adoption_rationale": "rationale if Adapt or Reject, else N/A"
  },
  "section_3_findings_by_rq": {
    "rq1_architectures": "dominant NeSy architectures identified",
    "rq2_explainability_hitl": "explainability / HITL mechanisms mentioned",
    "rq3_domains_languages": "domains, languages, application contexts"
  },
  "section_4_gaps_trends": {
    "gaps_identified": "", "future_directions": "",
    "link_to_thesis_gap": "relevance to M&E harmonization, NeSy, HITL, multilingual"
  },
  "section_5_synthesis": {
    "main_contribution_to_thesis": "2-3 sentences max"
  }
}

CRITICAL REMINDERS:
- Be factual. If the survey does not cover an RQ, write "Not covered".
- "key_categories": describe the schema as proposed by the authors, not your own interpretation.
- "link_to_thesis_gap": evaluate relevance specifically to ex-post M&E indicator harmonization + NeSy + HITL + multilingual.
"""

# ═══════════════════════════════════════════════════════════════
# STRUCTURAL PRE-PROCESSING
# ═══════════════════════════════════════════════════════════════

SECTION_PATTERNS = [
    (r"^abstract$", "ABSTRACT"),
    (r"^[0-9.]*\s*introduction", "INTRODUCTION"),
    (r"^[0-9.]*\s*(background|related\s+work|literature\s+review|preliminaries)", "BACKGROUND"),
    (r"^[0-9.]*\s*(method(ology)?|proposed\s+(method|approach|framework|system|model)|our\s+(approach|method)|approach|framework)", "METHODOLOGY"),
    (r"^[0-9.]*\s*(experiment(s|al)?|evaluation|results|empirical)", "RESULTS"),
    (r"^[0-9.]*\s*discussion", "DISCUSSION"),
    (r"^[0-9.]*\s*(conclusion|future\s+work)", "CONCLUSION"),
    (r"^[0-9.]*\s*(limitation|threats?\s+to)", "LIMITATIONS"),
    (r"^[0-9.]*\s*(dataset|benchmark|corpus)", "DATASETS"),
    (r"^[0-9.]*\s*ablation", "ABLATION"),
    (r"^[0-9.]*\s*(implementation|training\s+(detail|setup))", "IMPLEMENTATION"),
]

HEADING_RE = re.compile(
    r"^("
    r"(?:[0-9]+(?:\.[0-9]+)*\.?\s+[A-Z])"
    r"|(?:(?:I{1,3}|IV|VI{0,3}|IX|X{0,3})\.?\s+[A-Z])"
    r"|(?:ABSTRACT|INTRODUCTION|CONCLUSION|REFERENCES|ACKNOWLEDGMENT)"
    r")", re.MULTILINE
)


def detect_sections(text):
    sections = []
    for m in HEADING_RE.finditer(text):
        ls = text.rfind("\n", 0, m.start()) + 1
        le = text.find("\n", m.start())
        if le == -1: le = len(text)
        heading = text[ls:le].strip()
        if len(heading) > 120 or re.match(r"^[0-9.\s]+$", heading):
            continue
        sections.append((heading, ls, le))
    return sections


def classify_heading(heading):
    clean = re.sub(r"^[0-9IVXLC]+[.\s]*", "", heading).strip()
    for pattern, label in SECTION_PATTERNS:
        if re.search(pattern, clean, re.IGNORECASE):
            return label
    return "OTHER"


def add_structural_markers(text):
    """Insert [SECTION_LABEL] markers before detected headings."""
    sections = detect_sections(text)
    if not sections:
        return text
    parts, prev = [], 0
    n_markers = 0
    for heading, start, end in sections:
        label = classify_heading(heading)
        parts.append(text[prev:start])
        parts.append(f"\n[{label}]\n")
        n_markers += 1
        prev = start
    parts.append(text[prev:])
    log.info(f"    {n_markers} structural markers inserted")
    return "".join(parts)


# ═══════════════════════════════════════════════════════════════
# PDF EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_text_from_pdf(pdf_path, max_pages=50):
    try:
        reader = PdfReader(str(pdf_path))
        text = "\n\n".join(p.extract_text() or "" for p in reader.pages[:max_pages])
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        text = "\n".join(lines)
        if len(text) > 180_000:
            text = text[:180_000] + "\n[... TRUNCATED ...]"
            log.warning(f"  Truncated {pdf_path.name}")
        text = add_structural_markers(text)
        return text
    except Exception as e:
        log.error(f"  Failed to read {pdf_path.name}: {e}")
        return ""


def list_pdfs(directory):
    if not directory.exists():
        log.error(f"Directory not found: {directory}")
        return []
    pdfs = sorted(directory.glob("*.pdf"))
    log.info(f"Found {len(pdfs)} PDFs in {directory}")
    return pdfs


# ═══════════════════════════════════════════════════════════════
# STATUS FILTERING (DEC-028)
# ═══════════════════════════════════════════════════════════════




def load_status_index():
    """Build a lookup table {filename: status} from block_mapping.csv (v3.1).

    The mapping CSV has a `filename` column populated with the exact PDF name on disk
    (e.g. '1889_Peng_2025.pdf'). We key the status index by that filename for exact
    matching — no fuzzy author+year heuristic.

    Fallback: if a row has an empty `filename`, we keep a secondary index keyed by
    `{type}_{first_author_token}_{year}` for backward compatibility.

    Returns: (status_by_filename: dict, status_by_authoryear: dict)
    """
    path = _find_block_mapping_path()
    if path is None:
        log.warning("block_mapping.csv not found — status filtering disabled")
        return {}, {}

    df = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False)
    status_by_fn, status_by_ay = {}, {}
    for _, row in df.iterrows():
        status = str(row.get("status", "included")).lower().strip() or "included"
        fn = str(row.get("filename", "")).strip()
        if fn:
            status_by_fn[fn] = status
        else:
            # legacy fallback
            ref = str(row.get("short_ref", ""))
            rtype = str(row.get("type", "")).upper()
            tokens = re.findall(r"[A-Za-z]+", ref)
            years = re.findall(r"\b(20[0-9]{2})\b", ref)
            if tokens and years:
                status_by_ay[f"{rtype}_{tokens[0].lower()}_{years[0]}"] = status

    counts = {s: sum(1 for v in status_by_fn.values() if v == s)
              for s in ("included", "standby", "retired")}
    log.info(f"Status index loaded: {len(status_by_fn)} by filename "
             f"({counts['included']} included, {counts['standby']} standby, "
             f"{counts['retired']} retired){' + '+str(len(status_by_ay))+' fallback' if status_by_ay else ''}")
    return status_by_fn, status_by_ay


def filename_status(pdf_path, status_by_fn, status_by_ay, article_type):
    """Status lookup. Exact filename match first, fallback to author+year.

    Returns 'included' / 'standby' / 'retired' / 'unknown'.
    """
    if not status_by_fn and not status_by_ay:
        return "included"

    # 1. exact filename match
    if pdf_path.name in status_by_fn:
        return status_by_fn[pdf_path.name]

    # 2. fallback fuzzy match (only if CSV had empty filenames)
    if status_by_ay:
        stem = pdf_path.stem.lower()
        tokens = re.findall(r"[a-z]+", stem)
        years = re.findall(r"\b(20[0-9]{2})\b", stem)
        if tokens and years:
            for tok in tokens[:3]:
                if tok in ("et", "al", "and", "the", "bt", "sv"):
                    continue
                key = f"{article_type}_{tok}_{years[0]}"
                if key in status_by_ay:
                    return status_by_ay[key]
    return "unknown"


def filter_pdfs_by_status(pdfs, status_by_fn, status_by_ay, article_type,
                          include_retired=False, include_standby=True):
    """Partition pdfs by status. Returns (kept, skipped_dict)."""
    kept, skipped = [], {"retired": [], "standby": [], "unknown": []}
    for p in pdfs:
        st = filename_status(p, status_by_fn, status_by_ay, article_type)
        if st == "retired" and not include_retired:
            skipped["retired"].append(p.name)
        elif st == "standby" and not include_standby:
            skipped["standby"].append(p.name)
        elif st == "unknown":
            kept.append(p)
            skipped["unknown"].append(p.name)
        else:
            kept.append(p)
    if skipped["retired"]:
        log.info(f"  Skipped {len(skipped['retired'])} retired {article_type}: "
                 f"{', '.join(skipped['retired'][:3])}{'...' if len(skipped['retired'])>3 else ''}")
    if skipped["standby"]:
        log.info(f"  Skipped {len(skipped['standby'])} standby {article_type}")
    if skipped["unknown"]:
        log.warning(f"  {len(skipped['unknown'])} {article_type} with unknown status (processed anyway)")
    return kept, skipped


# ═══════════════════════════════════════════════════════════════
# JSON PARSING — robust
# ═══════════════════════════════════════════════════════════════

def parse_llm_json(raw):
    text = raw.strip()
    if text.startswith("```"):
        nl = text.find("\n")
        text = text[nl+1:] if nl != -1 else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    for attempt_text in [text, re.sub(r",\s*([}\]])", r"\1", text)]:
        try:
            return json.loads(attempt_text)
        except json.JSONDecodeError:
            pass

    bs, be = text.find("{"), text.rfind("}")
    if bs != -1 and be > bs:
        block = text[bs:be+1]
        for t in [block, re.sub(r",\s*([}\]])", r"\1", block)]:
            try:
                return json.loads(t)
            except json.JSONDecodeError:
                pass
    return None


# ═══════════════════════════════════════════════════════════════
# CLAUDE API — with retry + exponential backoff
# ═══════════════════════════════════════════════════════════════

def call_claude(client, article_text, prompt, article_id):
    user_msg = f"{prompt}\n\n--- ARTICLE FULL TEXT (with structural markers) ---\n\n{article_text}"
    raw_text = ""
    response = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS,
                system=[{"type": "text", "text": SYSTEM_PROMPT,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user_msg}]
            )
            raw_text = response.content[0].text.strip()
            break
        except anthropic.RateLimitError:
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            log.warning(f"  Rate limit {article_id}, retry {attempt}/{MAX_RETRIES} in {delay}s")
            time.sleep(delay)
        except anthropic.APIError as e:
            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                log.warning(f"  API error {article_id}: {e}, retry in {delay}s")
                time.sleep(delay)
            else:
                log.error(f"  API error {article_id} after {MAX_RETRIES} attempts: {e}")
                return None

    if not raw_text:
        return None

    data = parse_llm_json(raw_text)
    if data is None:
        log.error(f"  JSON parse error for {article_id}")
        debug_path = OUTPUT_DIR / "debug" / f"{article_id}_raw.txt"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(raw_text, encoding="utf-8")
        return None

    # Force the id field to match the runtime sequential id (the LLM tends to
    # hallucinate the placeholder PS-XXX based on prompt context). We preserve
    # the LLM-emitted value in _meta.llm_emitted_id for audit purposes.
    llm_emitted_id = data.get("id", "")
    if llm_emitted_id and llm_emitted_id != article_id:
        log.info(f"  {article_id}: LLM emitted id='{llm_emitted_id}' overridden -> '{article_id}'")
    data["id"] = article_id

    data["_meta"] = {
        "model": response.model,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_read": getattr(response.usage, "cache_read_input_tokens", 0),
        "cache_creation": getattr(response.usage, "cache_creation_input_tokens", 0),
        "extracted_at": datetime.now().isoformat(),
        "source_file": article_id,
        "llm_emitted_id": llm_emitted_id,
    }
    return data


# ═══════════════════════════════════════════════════════════════
# BATCH API
# ═══════════════════════════════════════════════════════════════

def prepare_batch_requests(pdfs, prompt, prefix):
    reqs = []
    for i, pdf in enumerate(pdfs, 1):
        text = extract_text_from_pdf(pdf)
        if not text: continue
        reqs.append({
            "custom_id": f"{prefix}-{i:03d}",
            "params": {
                "model": MODEL, "max_tokens": MAX_TOKENS,
                "system": [{"type": "text", "text": SYSTEM_PROMPT}],
                "messages": [{"role": "user",
                    "content": f"{prompt}\n\n--- ARTICLE FULL TEXT (with structural markers) ---\n\n{text}"}]
            }
        })
    return reqs

def submit_batch(client, requests, label):
    jsonl_path = OUTPUT_DIR / f"batch_{label}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in requests: f.write(json.dumps(r) + "\n")
    batch = client.messages.batches.create(requests=requests)
    log.info(f"Batch submitted: {batch.id} ({len(requests)} requests)")
    return batch.id

def poll_batch(client, batch_id, interval=60, id_map=None):
    """Poll a batch until ended and parse results.

    id_map: optional dict {custom_id: pdf_filename} so we can populate _meta.source_file
            (the batch API does not echo the filename — only custom_id).
    """
    id_map = id_map or {}
    while True:
        b = client.messages.batches.retrieve(batch_id)
        log.info(f"  Batch {batch_id}: {b.processing_status}")
        if b.processing_status == "ended": break
        time.sleep(interval)
    results = []
    for r in client.messages.batches.results(batch_id):
        if r.result.type == "succeeded":
            msg = r.result.message
            data = parse_llm_json(msg.content[0].text.strip())
            if data:
                # Force id to match the runtime custom_id (LLM tends to hallucinate it)
                llm_emitted_id = data.get("id", "")
                if llm_emitted_id and llm_emitted_id != r.custom_id:
                    log.info(f"  {r.custom_id}: LLM emitted id='{llm_emitted_id}' overridden")
                data["id"] = r.custom_id

                # Preserve tokens + source_file in _meta (parity with sequential mode)
                usage = getattr(msg, "usage", None)
                data["_meta"] = {
                    "model": MODEL,
                    "batch_id": batch_id,
                    "custom_id": r.custom_id,
                    "extracted_at": datetime.now().isoformat(),
                    "llm_emitted_id": llm_emitted_id,
                    "source_file": id_map.get(r.custom_id, ""),
                    "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
                    "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
                    "cache_read": getattr(usage, "cache_read_input_tokens", 0) if usage else 0,
                    "cache_creation": getattr(usage, "cache_creation_input_tokens", 0) if usage else 0,
                }
                results.append(data)
        else:
            log.error(f"  Failed: {r.custom_id}")
    return results


# ═══════════════════════════════════════════════════════════════
# CHECKPOINTS — crash recovery
# ═══════════════════════════════════════════════════════════════

def save_checkpoint(aid, data):
    d = OUTPUT_DIR / "checkpoints"; d.mkdir(parents=True, exist_ok=True)
    (d / f"{aid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_checkpoints(prefix):
    d = OUTPUT_DIR / "checkpoints"
    if not d.exists(): return {}
    out = {}
    for p in d.glob(f"{prefix}-*.json"):
        try: out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return out


# ═══════════════════════════════════════════════════════════════
# ID MAPPING — traceability
# ═══════════════════════════════════════════════════════════════

def build_id_map(pdfs, prefix):
    pairs = [(f"{prefix}-{i:03d}", p) for i, p in enumerate(pdfs, 1)]
    mp = OUTPUT_DIR / f"id_map_{prefix}.csv"
    with open(mp, "w", encoding="utf-8") as f:
        f.write("id,filename\n")
        for aid, p in pairs: f.write(f"{aid},{p.name}\n")
    log.info(f"ID mapping: {mp}")
    return pairs


# ═══════════════════════════════════════════════════════════════
# THEMATIC BLOCK MAPPING
# ═══════════════════════════════════════════════════════════════

BLOCK_MAPPING_FILE = OUTPUT_DIR / "block_mapping.csv"
# Path(__file__) works reliably at module top-level (always defined when running as a script).
BLOCK_MAPPING_ALT = Path(__file__).parent / "block_mapping.csv"


def _find_block_mapping_path():
    """Return the first existing block_mapping.csv path, or None if not found.

    Searches in this order:
      1. OUTPUT_DIR / block_mapping.csv  (preferred, next to extraction outputs)
      2. Same directory as the script itself  (convenient for dev)
      3. Current working directory  (last-resort fallback)

    This helper avoids the `"__file__" in dir()` pattern, which silently fails
    inside function scopes (dir() returns local names there).
    """
    candidates = [
        BLOCK_MAPPING_FILE,
        BLOCK_MAPPING_ALT,
        Path.cwd() / "block_mapping.csv",
    ]
    for p in candidates:
        if p and p.exists():
            return p
    return None


def load_block_mapping():
    """Load block_mapping.csv → two dicts: by filename (exact) and by author_year (fallback).

    Primary key: `filename` column (CSV v3.1, populated for all 56 entries).
    Fallback key: `{type}_{first_author}_{year}` derived from short_ref.

    Returns: (mapping_by_filename, mapping_by_authoryear)
    Each value is a dict with block / block_label / list_order / rank / status.
    """
    path = _find_block_mapping_path()
    if path is None:
        log.warning("block_mapping.csv not found — thematic columns will be empty")
        return {}, {}

    df = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False)
    by_fn, by_ay = {}, {}
    for _, row in df.iterrows():
        record = {
            "block": row.get("block", ""),
            "block_label": row.get("block_label", ""),
            "list_order": row.get("list_order", ""),
            "rank": row.get("rank", ""),
            "status": row.get("status", "included"),
        }
        fn = str(row.get("filename", "")).strip()
        if fn:
            by_fn[fn] = record

        # Fallback index, always built so it can rescue malformed source_file values
        ref = str(row.get("short_ref", ""))
        rtype = str(row.get("type", "")).upper()
        tokens = re.findall(r"[A-Za-z]+", ref)
        years = re.findall(r"\b(20[0-9]{2})\b", ref)
        if tokens and years:
            by_ay[f"{rtype}_{tokens[0].lower()}_{years[0]}"] = record

    log.info(f"Block mapping loaded: {len(by_fn)} by filename + {len(by_ay)} by author+year from {path}")
    return by_fn, by_ay


def enrich_with_blocks(df, block_maps, article_type="PS"):
    """Add block / block_label / list_order / status columns.

    block_maps is the tuple (by_filename, by_authoryear) returned by load_block_mapping().
    Match by source_file (filename) first, fallback to first_author+year.
    """
    by_fn, by_ay = block_maps if isinstance(block_maps, tuple) else (block_maps, {})

    if (not by_fn and not by_ay) or df.empty:
        for col in ["block", "block_label", "list_order", "status"]:
            df[col] = ""
        return df

    blocks, labels, orders, statuses = [], [], [], []
    for _, row in df.iterrows():
        source_file = str(row.get("source_file", "")).strip()
        match = by_fn.get(source_file, {})
        if not match:
            authors = str(row.get("authors", ""))
            year = str(row.get("year", ""))
            first_author = re.findall(r"[A-Za-z]+", authors)
            key = f"{article_type}_{first_author[0].lower()}_{year}" if first_author and year else ""
            match = by_ay.get(key, {})
        blocks.append(match.get("block", ""))
        labels.append(match.get("block_label", ""))
        orders.append(match.get("list_order", ""))
        statuses.append(match.get("status", ""))

    df.insert(2, "block", blocks)
    df.insert(3, "block_label", labels)
    df.insert(4, "list_order", orders)
    df.insert(5, "status", statuses)
    matched = sum(1 for b in blocks if b)
    log.info(f"  Block enrichment ({article_type}): {matched}/{len(df)} matched")
    return df


# ═══════════════════════════════════════════════════════════════
# FLATTEN → DataFrame  (v3 schema: D2/D6/D7, no role/i4_strict)
# ═══════════════════════════════════════════════════════════════

def _jl(val):
    return "; ".join(val) if isinstance(val, list) else str(val) if val else ""

def flatten_a5(records):
    rows = []
    for r in (r for r in records if r):
        ref  = r.get("reference", {})
        s1   = r.get("section_1_architecture", {})
        s2   = r.get("section_2_integration", {})
        s3   = r.get("section_3_task_evaluation", {})
        s4   = r.get("section_4_explainability", {})
        s5   = r.get("section_5_context_D7", {})
        s6   = r.get("section_6_knowledge_source_D2", {})
        s7   = r.get("section_7_reproducibility", {})
        s8   = r.get("section_8_synthesis", {})
        meta = r.get("_meta", {})
        bl   = s3.get("best_baseline", {}) or {}
        rows.append({
            "id": r.get("id", ""), "source_file": meta.get("source_file", ""),
            "authors": ref.get("authors", ""), "year": ref.get("year", ""),
            "title": ref.get("title", ""), "source": ref.get("source", ""),
            # Architecture
            "nesy_type_kautz": s1.get("nesy_type_kautz", ""),
            "neural_component": s1.get("neural_component", ""),
            "symbolic_component": s1.get("symbolic_component", ""),
            "knowledge_representation": s1.get("knowledge_representation", ""),
            "symbolic_inference_evidence": s1.get("symbolic_inference_evidence", ""),
            # Integration
            "integration_mode": s2.get("mode", ""),
            "component_interaction": s2.get("component_interaction", ""),
            # Task / eval
            "task": _jl(s3.get("task")),
            "datasets": json.dumps(s3.get("datasets", []), ensure_ascii=False),
            "metrics_best_result": s3.get("metrics_best_result", ""),
            "baseline_name": bl.get("name", ""), "baseline_score": bl.get("score", ""),
            "baseline_gap": bl.get("gap_delta", ""), "baseline_type": bl.get("type", ""),
            "ablation_study": s3.get("ablation_study", ""),
            # D6 explainability
            "D6_hitl_explainability": s4.get("D6_hitl_explainability", ""),
            "explainability_mechanism": s4.get("explainability_mechanism", ""),
            "explainability_evaluation": s4.get("explainability_evaluation", ""),
            "hitl_details": s4.get("hitl_details", ""),
            # D7 context
            "D7_domain": s5.get("domain", ""),
            "D7_multilingual": s5.get("multilingual", ""),
            "D7_n_languages": s5.get("n_languages", ""),
            "D7_dataset_scale": s5.get("dataset_scale", ""),
            "heterogeneity_type": _jl(s5.get("heterogeneity_type")),
            # D2 knowledge source
            "D2_knowledge_source_type": s6.get("D2_knowledge_source_type", ""),
            "specific_sources": s6.get("specific_sources", ""),
            # Reproducibility
            "code_available": s7.get("code_available", ""),
            "code_url": s7.get("code_url", ""),
            "open_data": s7.get("open_data", ""),
            "frameworks_libraries": s7.get("frameworks_libraries", ""),
            # Synthesis
            "main_contribution": s8.get("main_contribution", ""),
            "limitations_reported": s8.get("limitations_reported", ""),
            "relevance_to_thesis": _jl(s8.get("relevance_to_thesis")),
            "free_notes": s8.get("free_notes", ""),
            # Validation columns (filled at reading time)
            "validation_status": "", "notes_revision": "",
            # Reading-time columns for D1, D3, D4, D5 (left empty, coded on paper)
            "D1_manual": "", "D3_manual": "", "D4_manual": "", "D5_manual": "",
            # API meta
            "input_tokens": meta.get("input_tokens", ""),
            "output_tokens": meta.get("output_tokens", ""),
            "extracted_at": meta.get("extracted_at", ""),
        })
    return pd.DataFrame(rows)

def flatten_a6(records):
    rows = []
    for r in (r for r in records if r):
        ref, s1, s2 = r.get("reference",{}), r.get("section_1_scope",{}), r.get("section_2_taxonomy",{})
        s3, s4, s5 = r.get("section_3_findings_by_rq",{}), r.get("section_4_gaps_trends",{}), r.get("section_5_synthesis",{})
        meta = r.get("_meta",{})
        rows.append({
            "id": r.get("id",""), "source_file": meta.get("source_file",""),
            "authors": ref.get("authors",""), "year": ref.get("year",""),
            "title": ref.get("title",""), "source": ref.get("source",""),
            "survey_type": s1.get("survey_type",""),
            "rq_covered": _jl(s1.get("rq_covered")),
            "period_covered": s1.get("period_covered",""),
            "n_articles_analysed": s1.get("n_articles_analysed",""),
            "role_for_thesis": s1.get("role_for_thesis",""),
            "key_categories": s2.get("key_categories",""),
            "adoption_for_thesis": s2.get("adoption_for_thesis",""),
            "adoption_rationale": s2.get("adoption_rationale",""),
            "rq1_architectures": s3.get("rq1_architectures",""),
            "rq2_explainability_hitl": s3.get("rq2_explainability_hitl",""),
            "rq3_domains_languages": s3.get("rq3_domains_languages",""),
            "gaps_identified": s4.get("gaps_identified",""),
            "future_directions": s4.get("future_directions",""),
            "link_to_thesis_gap": s4.get("link_to_thesis_gap",""),
            "main_contribution_to_thesis": s5.get("main_contribution_to_thesis",""),
            "validation_status": "", "notes_revision": "",
            "extracted_at": meta.get("extracted_at",""),
        })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════
# SAVE OUTPUTS
# ═══════════════════════════════════════════════════════════════

def save_outputs(df_a5, df_a6, raw_a5, raw_a6):
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    block_maps = load_block_mapping()
    df_a5 = enrich_with_blocks(df_a5, block_maps, "PS")
    df_a6 = enrich_with_blocks(df_a6, block_maps, "SV")

    jd = OUTPUT_DIR / "json"; jd.mkdir(parents=True, exist_ok=True)
    for name, data in [("a5", raw_a5), ("a6", raw_a6)]:
        (jd / f"{name}_raw_{ts}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    cd = OUTPUT_DIR / "csv"; cd.mkdir(parents=True, exist_ok=True)
    if not df_a5.empty:
        df_a5.to_csv(cd / f"extraction_A5_{ts}.csv", index=False, encoding="utf-8-sig")
    if not df_a6.empty:
        df_a6.to_csv(cd / f"extraction_A6_{ts}.csv", index=False, encoding="utf-8-sig")

    xp = OUTPUT_DIR / f"extraction_SLR_{ts}.xlsx"
    with pd.ExcelWriter(xp, engine="openpyxl") as w:
        if not df_a5.empty: df_a5.to_excel(w, sheet_name="A5_Primary_Studies", index=False)
        if not df_a6.empty: df_a6.to_excel(w, sheet_name="A6_Surveys", index=False)
        pd.DataFrame({"Metric": ["A.5 count", "A.6 count", "Model", "Date", "Version", "Pre-processing", "DEC ref"],
            "Value":  [len(df_a5), len(df_a6), MODEL, ts, "v3.0",
                       "Section markers (regex) + status filter",
                       "DEC-026 / DEC-027 / DEC-028"]
        }).to_excel(w, sheet_name="Summary", index=False)

    log.info(f"Saved: {xp}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="LLM-assisted SLR extraction v3 (DEC-028)")
    ap.add_argument("--batch", action="store_true", help="Batch API (-50%%)")
    ap.add_argument("--test", type=int, default=0, help="Test on N articles")
    ap.add_argument("--article", type=str, help="Single article by filename")
    ap.add_argument("--surveys-only", action="store_true")
    ap.add_argument("--primary-only", action="store_true")
    ap.add_argument("--resume", action="store_true", help="Skip already-extracted articles")
    ap.add_argument("--include-retired", action="store_true",
                    help="Also process PS marked 'retired' in block_mapping (audit mode)")
    ap.add_argument("--exclude-standby", action="store_true",
                    help="Skip the 2 standby PS (SMoG, PRASE). Default: included.")
    ap.add_argument("--poll-interval", type=int, default=60)
    args = ap.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    init_logging()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("Set ANTHROPIC_API_KEY first.  PowerShell: $env:ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load status index for filtering (DEC-028)
    status_by_fn, status_by_ay = load_status_index()

    primary_pdfs = [] if args.surveys_only else list_pdfs(PRIMARY_DIR)
    survey_pdfs  = [] if args.primary_only else list_pdfs(SURVEY_DIR)

    # Apply status filtering BEFORE everything else
    if primary_pdfs:
        primary_pdfs, _ = filter_pdfs_by_status(
            primary_pdfs, status_by_fn, status_by_ay, "PS",
            include_retired=args.include_retired,
            include_standby=not args.exclude_standby,
        )
    # Surveys: all included (no retired SV)
    if survey_pdfs:
        survey_pdfs, _ = filter_pdfs_by_status(
            survey_pdfs, status_by_fn, status_by_ay, "SV",
            include_retired=args.include_retired, include_standby=True,
        )

    if args.article:
        target = args.article.replace(".pdf", "").lower()
        match = [p for p in primary_pdfs + survey_pdfs if target in p.stem.lower()]
        if not match:
            log.error(f"No PDF matching '{args.article}' (or it is filtered out by status)")
            sys.exit(1)
        pdf = match[0]
        is_pri = pdf in primary_pdfs
        primary_pdfs = [pdf] if is_pri else []
        survey_pdfs  = [pdf] if not is_pri else []

    if args.test > 0:
        primary_pdfs = primary_pdfs[:args.test]
        survey_pdfs  = survey_pdfs[:args.test]

    total = len(primary_pdfs) + len(survey_pdfs)
    log.info(f"Plan: {len(primary_pdfs)} primary (A.5) + {len(survey_pdfs)} surveys (A.6) = {total}")
    if total == 0:
        log.error("No PDFs to process. Check paths and status filter.")
        sys.exit(1)

    pp = build_id_map(primary_pdfs, "PS") if primary_pdfs else []
    sp = build_id_map(survey_pdfs, "SV") if survey_pdfs else []

    if not args.batch:
        ex_ps = load_checkpoints("PS") if args.resume else {}
        ex_sv = load_checkpoints("SV") if args.resume else {}
        if args.resume:
            log.info(f"Resume: {len(ex_ps)} PS + {len(ex_sv)} SV checkpoints")

        res_a5 = list(ex_ps.values()) if args.resume else []
        res_a6 = list(ex_sv.values()) if args.resume else []

        if pp:
            log.info("-- Extracting primary studies (A.5) --")
            for aid, pdf in tqdm(pp, desc="A.5"):
                if args.resume and aid in ex_ps:
                    log.info(f"  {aid}: SKIPPED (checkpoint)"); continue
                log.info(f"  {aid}: {pdf.name}")
                text = extract_text_from_pdf(pdf)
                if not text: continue
                result = call_claude(client, text, PROMPT_A5, aid)
                if result:
                    result["_meta"]["source_file"] = pdf.name
                    res_a5.append(result); save_checkpoint(aid, result)
                time.sleep(1)

        if sp:
            log.info("-- Extracting surveys (A.6) --")
            for aid, pdf in tqdm(sp, desc="A.6"):
                if args.resume and aid in ex_sv:
                    log.info(f"  {aid}: SKIPPED (checkpoint)"); continue
                log.info(f"  {aid}: {pdf.name}")
                text = extract_text_from_pdf(pdf)
                if not text: continue
                result = call_claude(client, text, PROMPT_A6, aid)
                if result:
                    result["_meta"]["source_file"] = pdf.name
                    res_a6.append(result); save_checkpoint(aid, result)
                time.sleep(1)
    else:
        res_a5, res_a6 = [], []
        if primary_pdfs:
            reqs = prepare_batch_requests(primary_pdfs, PROMPT_A5, "PS")
            bid = submit_batch(client, reqs, "A5_primary")
            id_map_ps = {aid: pdf.name for aid, pdf in pp}
            res_a5 = poll_batch(client, bid, args.poll_interval, id_map=id_map_ps)
        if survey_pdfs:
            reqs = prepare_batch_requests(survey_pdfs, PROMPT_A6, "SV")
            bid = submit_batch(client, reqs, "A6_surveys")
            id_map_sv = {aid: pdf.name for aid, pdf in sp}
            res_a6 = poll_batch(client, bid, args.poll_interval, id_map=id_map_sv)

    df_a5, df_a6 = flatten_a5(res_a5), flatten_a6(res_a6)
    log.info(f"Extracted: {len(df_a5)} primary, {len(df_a6)} surveys")
    save_outputs(df_a5, df_a6, res_a5, res_a6)

    ti = sum(r.get("_meta",{}).get("input_tokens",0) for r in res_a5+res_a6)
    to = sum(r.get("_meta",{}).get("output_tokens",0) for r in res_a5+res_a6)
    tc = sum(r.get("_meta",{}).get("cache_read",0) for r in res_a5+res_a6)
    log.info(f"-- Cost: input={ti:,} output={to:,} cache={tc:,} "
             f"~${ti/1e6*5 + to/1e6*25:.2f} (savings ~${tc/1e6*4.5:.2f}) --")


if __name__ == "__main__":
    main()
