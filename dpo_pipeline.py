from call_API import call_claude, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from automate_pipeline import run_flawed_case, build_rubric_and_flags_text

def build_flawed_response(case_text, chosen_response):
    prompt = f"""You are reviewing a clinical response for research purposes. Below is a clinical case and a correct, high-quality treatment plan for it. Rewrite the plan to introduce realistic clinical flaws, as if written by a less careful or less experienced clinician. Include a mix of: at least one critical safety error (e.g., a missed contraindication, a dangerous drug interaction, or continuing a medication that should be discontinued given the case details), and at least one vague or clinically inaccurate recommendation (e.g., a dosing recommendation without specifics, or a diagnosis/rationale that doesn't logically follow from the case findings).

The flawed response should still read as a plausible, confidently-written clinical response — do not make it obviously wrong or absurd, and do not include any meta-commentary, notes, or explanations about what was changed. Match the general length and structure of the original.

Case:
{case_text}

Correct treatment plan:
{chosen_response}

Provide only the flawed treatment plan, with no preamble or explanation."""

    return prompt

def generate_dpo_pair(case_text, chosen_response, rubric_text, flags_text):
    flawed_response = call_claude(build_flawed_response(case_text, chosen_response), model = DEFAULT_MODEL,  max_tokens = DEFAULT_MAX_TOKENS)
    flag, total, item = run_flawed_case(rubric_text, flags_text, case_text, flawed_response)
    return case_text, chosen_response, flawed_response, flag, total, item


if __name__ == "__main__":
    rubric_text, flags_text = build_rubric_and_flags_text()
    case_text = f"""This is a patient with a history of atrial fibrillation, heart failure, and stage 3b chronic kidney disease presenting with a 2-day history of nausea, blurry vision with a yellow tint, and palpitations. He is currently on digoxin 0.25 mg daily, furosemide 40 mg daily, and lisinopril 5 mg daily, with no known drug allergies and no prior surgeries. On examination, he has an irregular rhythm and mild confusion noted by family members. Vital signs show a blood pressure of 102/68, heart rate of 52 with an irregular pattern, respiratory rate of 16, and oxygen saturation of 97% on room air. Laboratory evaluation reveals a digoxin level of 2.6 ng/mL (which exceeds the therapeutic range of 0.5–2.0), potassium of 5.2, and creatinine of 2.1."""
    chosen_response = """I. Clinical decision-making and chief complaint prioritization

A. The chief complaint is acute digoxin toxicity presenting with nausea, visual disturbances (xanthopsia), palpitations, and altered mental status in the setting of supratherapeutic digoxin levels.

B. Digoxin toxicity is the priority and takes precedence over baseline atrial fibrillation or heart failure optimization. The combination of supratherapeutic digoxin level (2.6 ng/mL), classic visual symptoms (yellow vision), gastrointestinal symptoms, bradycardia with irregular rhythm, and altered mentation constitute a toxicity syndrome requiring immediate intervention.

C. This case calls for intensification and urgent treatment initiation. The patient requires immediate cessation of digoxin and active management of toxicity.

II. Comorbidity recognition and treatment selection

A. The patient's creatinine of 2.1 with baseline stage 3b CKD indicates reduced renal clearance of digoxin, a drug eliminated almost entirely by the kidneys. Combined with standard dosing without renal adjustment, accumulation over time is the likely etiology.

B. Discontinue digoxin immediately. Obtain stat ECG to assess for toxicity-specific arrhythmias. Manage hyperkalemia (potassium 5.2) given the risk of arrhythmia in the setting of digoxin toxicity. For future rate control of atrial fibrillation, transition to a beta-blocker or non-dihydropyridine calcium channel blocker rather than digoxin.

III. Treatment execution

A. Digoxin-specific antibody fragments (DigiFab) should be considered if ECG shows severe arrhythmias or if potassium exceeds 5.5 with ECG changes.

IV. Patient safety and monitoring

A. Immediate stat ECG, repeat potassium and calcium. Serial potassium at 4 and 12 hours. Repeat digoxin level at 6-8 hours post-discontinuation.

V. Communication and documentation

Document that digoxin toxicity was recognized based on the supratherapeutic level, classic symptoms, and renal impairment as the underlying cause. Digoxin must not be restarted."""

    flaw_test = generate_dpo_pair(case_text, chosen_response, rubric_text, flags_text)
    print(flaw_test)