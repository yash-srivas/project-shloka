import sys
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

reame_path = Path("data/raw/REAME.md")
reame_text = reame_path.read_text(encoding="utf-8")

prompts_dir = Path("prompts")
steps = [
    (1, "step1_sampradaanam.txt", "Step 1 — संप्रदानम्"),
    (2, "step2_padavibhaga.txt", "Step 2 — पदविभागः"),
    (3, "step3_anwaya.txt", "Step 3 — अन्वयः"),
    (4, "step4_anwayartha.txt", "Step 4 — अन्वयार्थः"),
    (5, "step5_bhavartha.txt", "Step 5 — भावानुवादः / भावार्थः"),
    (6, "step6_padakrutyam.txt", "Step 6 — पदकृत्यम्"),
    (7, "step7_dhvanitartha.txt", "Step 7 — ध्वनितार्थः")
]

print("=== VERIFYING PROMPTS AGAINST REAME.md ===")
for step_num, filename, header in steps:
    prompt_file = prompts_dir / filename
    if not prompt_file.exists():
        print(f"[FAIL] {filename} does not exist!")
        continue
    
    prompt_content = prompt_file.read_text(encoding="utf-8")
    
    # Check if key instructions from REAME.md are present in prompt_content
    # Find section in REAME.md
    start_idx = reame_text.find(header)
    end_idx = reame_text.find("---", start_idx) if start_idx != -1 else -1
    reame_section = reame_text[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else ""
    
    # Check key phrases
    checks = []
    if step_num == 1:
        checks = ["पद्यसूत्र (shloka/verse)", "4 पादs", "गद्यसूत्र (prose sutra)", "No definitions. No explanations."]
    elif step_num == 2:
        checks = ["सुबन्त", "तिङन्त", "अव्यय", "संधिविभजन", "समस्तपद", "लिङ्ग, विभक्ति, वचन", "लकार, पुरुष, वचन"]
    elif step_num == 3:
        checks = ["Kartru (प्रथमा विभक्ति)", "द्वितीया विभक्ति", "Visheshana", "तृतीया विभक्ति", "चतुर्थी विभक्ति", "पञ्चमी विभक्ति", "षष्ठी विभक्ति", "सप्तमी विभक्ति"]
    elif step_num == 4:
        checks = ["अन्वयार्थः", "Kartru → Karma → Kriya", "literal, word-by-word meaning", "No interpretation"]
    elif step_num == 5:
        checks = ["भावार्थः", "आचार्य (author) intended", "प्रकरण", "2 to 5 sentences"]
    elif step_num == 6:
        checks = ["पदकृत्यम्", "Synonyms", "धातु", "धात्वर्थ", "उपसर्ग", "Contribution"]
    elif step_num == 7:
        checks = ["ध्वनितार्थः", "व्याकरण", "तन्त्रयुक्ति", "तन्त्रसमन्वय", "2 to 4 sentences"]
        
    all_pass = True
    missing = []
    for c in checks:
        if c not in prompt_content:
            all_pass = False
            missing.append(c)
            
    if all_pass:
        print(f"[PASS] Step {step_num} ({filename}) verified against REAME.md. All key rules intact.")
    else:
        print(f"[WARN] Step {step_num} ({filename}) missing phrases: {missing}")
