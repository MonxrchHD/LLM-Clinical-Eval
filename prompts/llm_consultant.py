def build_consultant_prompt(case_text):
    prompt = f"""You are my clinical consultant. I am a clinician evaluating a patient case. Using the provided patient case and current, generally accepted clinical guidelines relevant to the presenting condition, provide definitive clinical recommendations with patient-specific rationale.

If clinically important information is missing, state what information is needed and explain how it would affect your recommendation. If a topic is not applicable to the case, state that it is not applicable and briefly explain why.

You will be assessed on clinical accuracy, prioritization, guideline-concordant reasoning, dosing/titration appropriateness (if applicable), safety, and feasibility. Do not include links. Do not use bold, italics, underlining, emojis, highlighting, or tables. Format your response using an alphanumerical outline with the following progression: I, A, 1, a, i.

I. Clinical decision-making and chief complaint prioritization
A. State the chief complaint clearly and using appropriate clinical terminology.
B. Prioritize the chief complaint and provide rationale supported by the case findings.
C. Determine whether this case primarily calls for optimization of an existing plan or intensification/initiation of treatment, and justify that choice.
D. Identify any missing information needed to make a safe, complete clinical decision.
E. Provide clear clinical reasoning connecting the patient's presentation and findings to your decisions.

II. Comorbidity recognition and treatment selection
A. Identify relevant comorbidities from the case and assess their clinical significance.
B. Select treatment(s) that address the chief complaint while accounting for identified comorbidities.
C. Address optimization of any existing treatments/medications the patient is already on.
D. Ground your recommendations in relevant clinical guidelines.

III. Treatment execution (dosing/titration, if applicable)
A. Provide starting dose(s) for any newly recommended treatment, or state that none is needed.
B. Provide titration schedule and interval, if relevant.
C. State whether existing treatments should be continued, increased, decreased, discontinued, or switched.
D. Address renal/hepatic or other relevant dose adjustments.

IV. Patient safety and monitoring
A. Identify contraindications, or state what information is needed to assess them.
B. Identify relevant adverse effects, warnings, and drug/treatment interactions.
C. Develop a monitoring plan, including relevant baseline and follow-up labs or assessments.

V. Communication and documentation
A. Document the clinical reasoning and rationale behind your recommendations.
B. Describe how you would communicate this plan to the patient, including risks, benefits, and alternatives.

VI. Follow-up and continuity of care
A. Provide a specific follow-up plan, including timeframe.
B. Address coordination with other healthcare providers involved in the patient's care, if relevant.

Here is the the case for you to evaluate:
{case_text}
"""
    return prompt

if __name__ == "__main__":
    case_text = """Chief complaint: Progressive shortness of breath and leg swelling over the past 10 days.

History of present illness: 67-year-old presents with worsening dyspnea on exertion, now occurring after walking less than one block, plus orthopnea (sleeping on 3 pillows) and bilateral lower extremity swelling. Reports a 6 lb weight gain over the past week. Denies chest pain, fever, or cough.

PMH: Heart failure with reduced ejection fraction (EF 35%, diagnosed 2 years ago), hypertension, atrial fibrillation.

PSH: Coronary artery bypass graft (CABG) 5 years ago.

Current medications: Lisinopril 20mg daily, metoprolol succinate 50mg daily, furosemide 20mg daily, apixaban 5mg twice daily, atorvastatin 40mg daily.

Allergies: NKDA.

Labs (today): Sodium 133 mEq/L, potassium 4.2 mEq/L, creatinine 1.3 mg/dL (baseline 1.0 mg/dL), BNP 1450 pg/mL (baseline ~300 pg/mL), unremarkable CBC.

Vitals: BP 128/78, HR 88 (irregularly irregular), RR 20, SpO2 94% on room air, weight up 6 lb from last visit."""
    result = build_consultant_prompt(case_text)
    print(result)