import pandas as pd, os, shutil, time

def safe_move(src, dst):
    """Copy then delete, with retry for OneDrive locks."""
    shutil.copy2(src, dst)
    for attempt in range(3):
        try:
            os.remove(src)
            return True
        except PermissionError:
            time.sleep(1)
    print("    WARN: copied but could not delete source: %s" % src)
    return False

inc = pd.read_csv('data/processed/articles_inclus.csv', keep_default_na=False)
snow = pd.read_csv('data/processed/snowballing.csv', keep_default_na=False)
corpus = pd.read_csv('data/processed/corpus_scored.csv', keep_default_na=False)

base = 'data/fulltext'
src_s1 = os.path.join(base, 'Screening_1_included')
src_snow = os.path.join(base, 'Snowballing')
dst_extraction = os.path.join(base, 'Extraction')
dst_i4 = os.path.join(base, 'Screening_2_I4_strict')
dst_exclu = os.path.join(base, 'Screening_2_excluded')
dst_surveys = os.path.join(base, 'Surveys')

os.makedirs(dst_extraction, exist_ok=True)
os.makedirs(dst_i4, exist_ok=True)
os.makedirs(dst_exclu, exist_ok=True)

# Build lookup: rank -> (qa_pass, is_I4) from articles_inclus (corpus only)
rank_info = {}
for _, r in inc.iterrows():
    try:
        rank = int(r['rank'])
    except (ValueError, TypeError):
        continue
    qa = r['qa_pass']
    notes_q2 = str(r.get('qa_notes_q2', ''))
    is_i4 = 'I4' in notes_q2.upper()
    rank_info[rank] = (qa, is_i4)

# Build lookup for corpus_scored (for orphan PDFs)
corpus_decision = dict(zip(corpus['rank'].astype(int), corpus['decision']))

# Build lookup: snowballing id -> tri2 (normalize: BT01 -> BT-01)
snow_tri2 = {}
for _, r in snow.iterrows():
    sid = r['id']  # e.g. BT-01
    snow_tri2[sid] = r['tri2']
    # Also store without hyphen: BT01
    snow_tri2[sid.replace('-', '')] = r['tri2']

# --- CORPUS PDFs (Screening_1_included) ---
s1_files = [f for f in os.listdir(src_s1) if f.endswith('.pdf')]
print("PDFs remaining in Screening_1_included: %d" % len(s1_files))

moved = {'Extraction': 0, 'I4_strict': 0, 'Exclu': 0, 'Surveys': 0}
orphans = []

for f in s1_files:
    rank_str = f.split('_')[0]
    try:
        rank = int(rank_str)
    except ValueError:
        orphans.append(f)
        continue
    
    info = rank_info.get(rank)
    if info:
        qa, is_i4 = info
        if qa == 'oui':
            safe_move(os.path.join(src_s1, f), os.path.join(dst_extraction, f))
            moved['Extraction'] += 1
        elif is_i4:
            safe_move(os.path.join(src_s1, f), os.path.join(dst_i4, f))
            moved['I4_strict'] += 1
        else:
            safe_move(os.path.join(src_s1, f), os.path.join(dst_exclu, f))
            moved['Exclu'] += 1
    else:
        # Orphan: check corpus_scored
        dec = corpus_decision.get(rank, '?')
        if dec == 'survey':
            safe_move(os.path.join(src_s1, f), os.path.join(dst_surveys, f))
            moved['Surveys'] += 1
            print("  Survey orphan -> Surveys: %s" % f)
        else:
            orphans.append("%s (decision=%s)" % (f, dec))

print("  -> Extraction: %d" % moved['Extraction'])
print("  -> I4 strict:  %d" % moved['I4_strict'])
print("  -> Exclu Tri2:  %d" % moved['Exclu'])
print("  -> Surveys:     %d" % moved['Surveys'])
if orphans:
    print("  Orphans left in Screening_1_included (Tri 1 exclu):")
    for o in orphans:
        print("    " + o)

# --- SNOWBALLING PDFs ---
snow_files = [f for f in os.listdir(src_snow) if f.endswith('.pdf')]
print("\nPDFs in Snowballing: %d" % len(snow_files))

sm = {'Extraction': 0, 'I4_strict': 0, 'Exclu': 0}
kept = []

for f in snow_files:
    sid = f.split('_')[0]  # BT01, SV01
    tri2 = snow_tri2.get(sid, '')
    
    if tri2 == 'inclus':
        safe_move(os.path.join(src_snow, f), os.path.join(dst_extraction, f))
        sm['Extraction'] += 1
    elif 'I4' in tri2.upper():
        safe_move(os.path.join(src_snow, f), os.path.join(dst_i4, f))
        sm['I4_strict'] += 1
    elif tri2.startswith('exclu'):
        safe_move(os.path.join(src_snow, f), os.path.join(dst_exclu, f))
        sm['Exclu'] += 1
    else:
        kept.append("%s (tri2='%s')" % (f, tri2))

print("  -> Extraction: %d" % sm['Extraction'])
print("  -> I4 strict:  %d" % sm['I4_strict'])
print("  -> Exclu:      %d" % sm['Exclu'])
if kept:
    print("  Kept in Snowballing (tri1 exclu or pas de PDF tri2):")
    for s in kept:
        print("    " + s)

# --- SUMMARY ---
print("\n=== FINAL SUMMARY ===")
print("Extraction:            %d" % (moved['Extraction'] + sm['Extraction']))
print("Screening_2_I4_strict: %d" % (moved['I4_strict'] + sm['I4_strict']))
print("Screening_2_excluded:  %d" % (moved['Exclu'] + sm['Exclu']))
print("Surveys (added):       %d" % moved['Surveys'])

# I4 strict
i4 = non_pass[non_pass['qa_notes_q2'].str.contains('I4', case=False, na=False)]
print(f"I4 strict failed: {len(i4)}")

# Non-I4 (real tri2 failures)
non_i4 = non_pass[~non_pass['qa_notes_q2'].str.contains('I4', case=False, na=False)]
print(f"Non-I4 tri2 exclusions: {len(non_i4)}")

# Sample
print("\nSample non_pass:")
for _, r in non_pass.head(5).iterrows():
    rank = r['rank']
    total = r['qa_total']
    notes = str(r['qa_notes_q2'])[:80]
    print(f"  rank={rank} total={total} notes={notes}")

# Also check snowballing exclu
sn = pd.read_csv('data/processed/snowballing.csv', keep_default_na=False)
sn_exclu_tri1 = sn[sn['tri1'].str.startswith('exclu')]
sn_exclu_tri2 = sn[(sn['tri2'].str.startswith('exclu')) & (sn['tri2'] != '')]
print(f"\nSnowballing exclu tri1: {len(sn_exclu_tri1)}")
print(f"Snowballing exclu tri2: {len(sn_exclu_tri2)}")
print("SN tri2 values:", sn_exclu_tri2['tri2'].value_counts().to_dict())
