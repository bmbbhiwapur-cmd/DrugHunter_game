"""
Drug Hunter — Case data
Developed by Sarang Dhote, Shivaji Science College, Nagpur
Pure data file — no imports, no dependencies.
"""

CASES = [
    {
        "id": 1, "title": "The Painful Truth",
        "disease": "Pain & Inflammation (Rheumatoid Arthritis)",
        "difficulty": "⭐⭐ Beginner",
        "patient": {
            "name": "Mrs. Sharma", "age": 58, "gender": "Female",
            "condition": "Chronic rheumatoid arthritis — joint pain, swelling, redness",
            "history": "Took ibuprofen for 3 years → hospitalized with stomach bleeding",
        },
        "stage1_question": "Which enzyme produces prostaglandins that cause inflammation?",
        "stage1_options": [
            {"text": "Lipoxygenase (LOX)", "correct": False,
             "feedback": "LOX makes leukotrienes, not prostaglandins."},
            {"text": "Cyclooxygenase-2 (COX-2)", "correct": True,
             "feedback": "Correct! COX-2 makes prostaglandins during inflammation. COX-1 protects the stomach."},
            {"text": "Phospholipase A2", "correct": False,
             "feedback": "PLA2 releases arachidonic acid but doesn't make prostaglandins directly."},
            {"text": "Acetylcholinesterase", "correct": False,
             "feedback": "Wrong system — that enzyme breaks down acetylcholine."},
        ],
        "target_protein": "COX-2", "target_pdb": "3LN1",
        "pocket_regions": [
            {"name": "Surface loop (outside pocket)", "correct": False,
             "feedback": "Too far from the catalytic site."},
            {"name": "Hydrophobic pocket near Val523", "correct": True,
             "feedback": "Correct! Val523 in COX-2 vs Ile523 in COX-1 is the key selectivity difference."},
            {"name": "Membrane-binding domain", "correct": False,
             "feedback": "That anchors COX-2 to the membrane — not the drug binding site."},
            {"name": "Dimer interface", "correct": False,
             "feedback": "Where two subunits meet, not where drugs bind."},
        ],
        "candidates": [
            {"name": "Celecoxib",      "desc": "Selective COX-2 inhibitor",            "smiles": "CC1=CC=C(C=C1)C2=CC(=NN2C3=CC=C(C=C3)S(=O)(=O)N)C(F)(F)F", "kind": "best"},
            {"name": "Aspirin",        "desc": "Old non-selective NSAID",              "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",                                     "kind": "weak"},
            {"name": "Ibuprofen",      "desc": "Non-selective NSAID",                  "smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",                               "kind": "weak"},
            {"name": "Diphenhydramine","desc": "Decoy — antihistamine",                "smiles": "CN(C)CCOC(C1=CC=CC=C1)C2=CC=CC=C2",                            "kind": "decoy"},
            {"name": "Rofecoxib",      "desc": "COX-2 selective (withdrawn 2004)",     "smiles": "CS(=O)(=O)C1=CC=C(C=C1)C2=C(C(=O)OC2)C3=CC=CC=C3",            "kind": "alt"},
            {"name": "Glucose",        "desc": "Decoy — sugar",                        "smiles": "C(C1C(C(C(C(O1)O)O)O)O)O",                                    "kind": "decoy"},
        ],
        "off_target": "COX-1", "off_target_pdb": "3KK6",
        "selectivity_data": {
            "Celecoxib": {"pass": True,  "msg": "Excellent selectivity — fits large COX-2 pocket, blocked by Ile523 in COX-1."},
            "Rofecoxib": {"pass": True,  "msg": "Selective — but cardiac risk led to market withdrawal in 2004."},
        },
        "admet": {
            "Celecoxib": {"MW": 381, "LogP": 3.5, "HBD": 1, "HBA": 7, "RotBonds": 4, "pass": True,  "warning": None},
            "Rofecoxib": {"MW": 314, "LogP": 2.7, "HBD": 0, "HBA": 4, "RotBonds": 2, "pass": True,  "warning": "⚠️ FDA withdrew Vioxx in 2004 — 40% increased heart attack risk."},
        },
        "ending": "Mrs. Sharma's joints feel great and her stomach is fine. Selective inhibition solved her problem.",
    },
    {
        "id": 2, "title": "Pressure Mounting",
        "disease": "Hypertension", "difficulty": "⭐⭐ Beginner",
        "patient": {
            "name": "Mr. Patel", "age": 62, "gender": "Male",
            "condition": "Persistent high blood pressure (160/100 mmHg)",
            "history": "Lifestyle changes failed. Needs pharmacological treatment.",
        },
        "stage1_question": "Which enzyme converts angiotensin I → angiotensin II (vasoconstrictor)?",
        "stage1_options": [
            {"text": "Renin", "correct": False, "feedback": "Renin acts earlier — converts angiotensinogen to angiotensin I."},
            {"text": "Angiotensin Converting Enzyme (ACE)", "correct": True, "feedback": "Correct! ACE converts angiotensin I → angiotensin II, constricting vessels."},
            {"text": "Aldosterone Synthase", "correct": False, "feedback": "Aldosterone synthase acts downstream of angiotensin II."},
            {"text": "Bradykininase", "correct": False, "feedback": "Bradykininase is another name for ACE — use the standard term."},
        ],
        "target_protein": "ACE", "target_pdb": "1O86",
        "pocket_regions": [
            {"name": "N-terminal helix",          "correct": False, "feedback": "Far from the active site."},
            {"name": "Zinc-binding catalytic site","correct": True,  "feedback": "Correct! ACE is a zinc metallopeptidase — drugs chelate the Zn²⁺."},
            {"name": "Membrane anchor region",     "correct": False, "feedback": "Anchors ACE to the cell surface."},
            {"name": "Glycosylation surface",      "correct": False, "feedback": "Just sugar decoration on the protein."},
        ],
        "candidates": [
            {"name": "Captopril",    "desc": "First ACE inhibitor",         "smiles": "CC(CS)C(=O)N1CCCC1C(=O)O",                                                   "kind": "best"},
            {"name": "Lisinopril",   "desc": "Modern ACE inhibitor",        "smiles": "NCCCCC(NC(CCc1ccccc1)C(=O)O)C(=O)N1CCCC1C(=O)O",                           "kind": "alt"},
            {"name": "Paracetamol",  "desc": "Decoy — painkiller",          "smiles": "CC(=O)Nc1ccc(O)cc1",                                                         "kind": "decoy"},
            {"name": "Aspirin",      "desc": "Decoy — anti-inflammatory",   "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",                                                   "kind": "decoy"},
            {"name": "Caffeine",     "desc": "Decoy — stimulant",           "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",                                              "kind": "decoy"},
            {"name": "Enalaprilat",  "desc": "Active form of enalapril",    "smiles": "CCOC(=O)C(CCc1ccccc1)NC(C)C(=O)N1CCCC1C(=O)O",                            "kind": "weak"},
        ],
        "off_target": "ACE2", "off_target_pdb": "1R42",
        "selectivity_data": {
            "Captopril":  {"pass": True, "msg": "Good selectivity. May cause dry cough via bradykinin buildup."},
            "Lisinopril": {"pass": True, "msg": "Excellent selectivity over ACE2."},
        },
        "admet": {
            "Captopril":  {"MW": 217, "LogP": 0.3,  "HBD": 2, "HBA": 4, "RotBonds": 4,  "pass": True,  "warning": None},
            "Lisinopril": {"MW": 405, "LogP": -1.2, "HBD": 5, "HBA": 8, "RotBonds": 12, "pass": False, "warning": "⚠️ Violates Lipinski rules but works via active transport."},
        },
        "ending": "Mr. Patel's BP drops to 130/85. Back to morning walks with his grandchildren.",
    },
    {
        "id": 3, "title": "The Forgetting Mind",
        "disease": "Alzheimer's Disease", "difficulty": "⭐⭐⭐ Intermediate",
        "patient": {
            "name": "Mr. Singh", "age": 72, "gender": "Male",
            "condition": "Progressive memory loss, confusion, difficulty recognizing family",
            "history": "Worsening for 2 years. Brain imaging shows cortical thinning.",
        },
        "stage1_question": "Acetylcholine is low in Alzheimer's. Which enzyme breaks it down?",
        "stage1_options": [
            {"text": "Choline acetyltransferase (ChAT)", "correct": False, "feedback": "ChAT MAKES acetylcholine — inhibiting it worsens disease."},
            {"text": "Acetylcholinesterase (AChE)",       "correct": True,  "feedback": "Correct! AChE breaks down acetylcholine. Inhibiting it boosts levels."},
            {"text": "Monoamine oxidase (MAO)",           "correct": False, "feedback": "MAO breaks down dopamine/serotonin, not acetylcholine."},
            {"text": "COMT",                              "correct": False, "feedback": "COMT breaks down catecholamines, not acetylcholine."},
        ],
        "target_protein": "AChE", "target_pdb": "4EY7",
        "pocket_regions": [
            {"name": "Peripheral anionic site (PAS)", "correct": False, "feedback": "PAS is at the gorge entrance. Catalytic site is deeper."},
            {"name": "Catalytic triad at gorge bottom","correct": True,  "feedback": "Correct! AChE has a deep gorge with Ser-His-Glu triad at the bottom."},
            {"name": "Surface helix",                  "correct": False, "feedback": "Wrong location."},
            {"name": "Dimerization interface",         "correct": False, "feedback": "Where subunits meet — not the active site."},
        ],
        "candidates": [
            {"name": "Donepezil",    "desc": "Selective AChE inhibitor (Aricept)", "smiles": "COc1cc2c(cc1OC)CC(CC1CCN(Cc3ccccc3)CC1)C2=O",  "kind": "best"},
            {"name": "Galantamine",  "desc": "Natural alkaloid AChE inhibitor",    "smiles": "COC1=CC=C2CN3CCC4=CC(=C(OC5=C4C2=C1OC53)O)OC", "kind": "alt"},
            {"name": "Rivastigmine", "desc": "Dual AChE/BuChE inhibitor",          "smiles": "CCN(C)C(=O)Oc1cccc(C(C)N(C)C)c1",               "kind": "weak"},
            {"name": "Memantine",    "desc": "Decoy — NMDA antagonist",            "smiles": "CC12CC3CC(C1)(CC(C2)C3)N",                       "kind": "decoy"},
            {"name": "Aspirin",      "desc": "Decoy — NSAID",                      "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",                      "kind": "decoy"},
            {"name": "Vitamin C",    "desc": "Decoy — antioxidant",                "smiles": "C(C(C1C(=C(C(=O)O1)O)O)O)O",                    "kind": "decoy"},
        ],
        "off_target": "BuChE", "off_target_pdb": "1P0I",
        "selectivity_data": {
            "Donepezil":   {"pass": True, "msg": "Highly selective for AChE — minimal peripheral side effects."},
            "Galantamine": {"pass": True, "msg": "Reasonable selectivity. Also activates nicotinic receptors."},
        },
        "admet": {
            "Donepezil":   {"MW": 379, "LogP": 4.3, "HBD": 0, "HBA": 4, "RotBonds": 6, "pass": True, "warning": "Crosses blood-brain barrier well (LogP 4.3) — essential for CNS drugs."},
            "Galantamine": {"MW": 287, "LogP": 1.1, "HBD": 1, "HBA": 4, "RotBonds": 1, "pass": True, "warning": None},
        },
        "ending": "Mr. Singh's family reports he's more responsive. He recognized his granddaughter's birthday.",
    },
    {
        "id": 4, "title": "The Mosquito's Curse",
        "disease": "Malaria", "difficulty": "⭐⭐⭐⭐ Advanced",
        "patient": {
            "name": "Ms. Banerjee", "age": 28, "gender": "Female",
            "condition": "Cyclical fever, chills, anemia after travel to tropical region",
            "history": "Blood smear confirms P. falciparum. Chloroquine-resistant.",
        },
        "stage1_question": "Which enzyme is the classic target for antifolate antimalarials?",
        "stage1_options": [
            {"text": "Dihydrofolate reductase (DHFR)", "correct": True,  "feedback": "Correct! Pf-DHFR is essential for parasite DNA synthesis. Selective inhibitors spare human DHFR."},
            {"text": "Thymidylate synthase",           "correct": False, "feedback": "Important but DHFR is the primary validated target."},
            {"text": "Heme polymerase",                "correct": False, "feedback": "That's the chloroquine target — patient is resistant."},
            {"text": "Cytochrome bc1",                 "correct": False, "feedback": "Valid (atovaquone) but DHFR is more selective here."},
        ],
        "target_protein": "Pf-DHFR", "target_pdb": "3QGT",
        "pocket_regions": [
            {"name": "NADPH binding site",             "correct": False, "feedback": "Adjacent to substrate pocket but not the drug target."},
            {"name": "Folate substrate binding pocket","correct": True,  "feedback": "Correct! Antifolates compete here. Key residue: Phe58 (vs Ile in human DHFR)."},
            {"name": "Hinge region",                   "correct": False, "feedback": "Moves during catalysis but isn't a drug binding site."},
            {"name": "Dimerization domain",            "correct": False, "feedback": "Pf-DHFR is a single chain with thymidylate synthase."},
        ],
        "candidates": [
            {"name": "Pyrimethamine","desc": "Classic antifolate antimalarial",      "smiles": "CCc1nc(N)nc(N)c1-c1ccc(Cl)cc1",              "kind": "best"},
            {"name": "Cycloguanil",  "desc": "Active metabolite of proguanil",       "smiles": "CC1(C)N=C(N)N=C(N)N1c1ccc(Cl)cc1",          "kind": "alt"},
            {"name": "Trimethoprim", "desc": "Bacterial DHFR inhibitor — weaker",    "smiles": "COc1cc(Cc2cnc(N)nc2N)cc(OC)c1OC",           "kind": "weak"},
            {"name": "Paracetamol",  "desc": "Decoy — fever reducer only",           "smiles": "CC(=O)Nc1ccc(O)cc1",                         "kind": "decoy"},
            {"name": "Quinine",      "desc": "Decoy — different mechanism",          "smiles": "COc1ccc2nccc([C@@H](O)[C@H]3CC[C@@H](C=C)CN3)c2c1", "kind": "decoy"},
            {"name": "Aspirin",      "desc": "Decoy — NSAID",                        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",                   "kind": "decoy"},
        ],
        "off_target": "Human DHFR", "off_target_pdb": "1U72",
        "selectivity_data": {
            "Pyrimethamine": {"pass": True, "msg": "Excellent selectivity! Exploits Phe58 in Pf-DHFR vs Ile in human DHFR."},
            "Cycloguanil":   {"pass": True, "msg": "Good selectivity. Watch for resistance mutations."},
        },
        "admet": {
            "Pyrimethamine": {"MW": 248, "LogP": 2.7, "HBD": 2, "HBA": 3, "RotBonds": 2, "pass": True, "warning": "Long-term use causes folate deficiency — co-administer folinic acid."},
            "Cycloguanil":   {"MW": 251, "LogP": 1.9, "HBD": 3, "HBA": 4, "RotBonds": 2, "pass": True, "warning": None},
        },
        "ending": "Ms. Banerjee's fever resolves in 48 hours. Parasitemia clears. Discharged with folate supplement.",
    },
    {
        "id": 5, "title": "Breathless in the City",
        "disease": "Asthma", "difficulty": "⭐⭐ Beginner",
        "patient": {
            "name": "Master Rohan", "age": 14, "gender": "Male",
            "condition": "Acute asthma attack — wheezing, shortness of breath",
            "history": "Triggered by exercise and dust. Needs fast bronchodilator.",
        },
        "stage1_question": "Which receptor, when activated, relaxes airway smooth muscle?",
        "stage1_options": [
            {"text": "β1-adrenergic receptor", "correct": False, "feedback": "β1 is in the heart — causes tachycardia."},
            {"text": "β2-adrenergic receptor", "correct": True,  "feedback": "Correct! β2 on airway smooth muscle causes bronchodilation."},
            {"text": "α1-adrenergic receptor", "correct": False, "feedback": "α1 causes vasoconstriction — wrong target."},
            {"text": "Muscarinic M3 receptor", "correct": False, "feedback": "M3 causes bronchoconstriction — the opposite!"},
        ],
        "target_protein": "β2-adrenergic receptor", "target_pdb": "2RH1",
        "pocket_regions": [
            {"name": "Orthosteric pocket in TM bundle","correct": True,  "feedback": "Correct! Agonists bind in the orthosteric site within the 7-TM bundle."},
            {"name": "Extracellular loop ECL2",        "correct": False, "feedback": "ECL2 caps the pocket but isn't the binding site."},
            {"name": "Intracellular G-protein site",   "correct": False, "feedback": "G-proteins bind here, not drugs."},
            {"name": "Membrane lipid surface",         "correct": False, "feedback": "Lipid contact surface — not a drug site."},
        ],
        "candidates": [
            {"name": "Salbutamol",   "desc": "Short-acting β2 agonist (Albuterol)", "smiles": "CC(C)(C)NCC(O)c1ccc(O)c(CO)c1",                    "kind": "best"},
            {"name": "Salmeterol",   "desc": "Long-acting β2 agonist",              "smiles": "OCc1cc(C(O)CNCCCCCCOCCCCc2ccccc2)ccc1O",           "kind": "alt"},
            {"name": "Epinephrine",  "desc": "Non-selective adrenergic agonist",    "smiles": "CNCC(O)c1ccc(O)c(O)c1",                             "kind": "weak"},
            {"name": "Propranolol",  "desc": "Decoy — β-blocker (worsens asthma!)", "smiles": "CC(C)NCC(O)COc1cccc2ccccc12",                       "kind": "decoy"},
            {"name": "Aspirin",      "desc": "Decoy — can trigger asthma",          "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",                          "kind": "decoy"},
            {"name": "Caffeine",     "desc": "Decoy — mild stimulant",              "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",                     "kind": "decoy"},
        ],
        "off_target": "β1-adrenergic receptor", "off_target_pdb": "7BVQ",
        "selectivity_data": {
            "Salbutamol": {"pass": True, "msg": "Good β2 selectivity — minimal cardiac effects at therapeutic dose."},
            "Salmeterol": {"pass": True, "msg": "Highly selective. Long lipophilic tail anchors for prolonged action."},
        },
        "admet": {
            "Salbutamol": {"MW": 239, "LogP": 0.3, "HBD": 4, "HBA": 4, "RotBonds": 5,  "pass": True,  "warning": None},
            "Salmeterol": {"MW": 415, "LogP": 3.9, "HBD": 4, "HBA": 5, "RotBonds": 15, "pass": False, "warning": "⚠️ Exceeds rotatable bond limit — but inhaled delivery bypasses bioavailability issues."},
        },
        "ending": "Rohan's wheezing resolves within minutes. Prescribed a rescue inhaler.",
    },
]

# Remaining 15 cases use same structure — add them here
# See full cases.py in the repository for all 20 cases
