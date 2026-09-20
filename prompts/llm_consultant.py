from call_API import call_claude, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from prompts.llm_HPI import build_hpi
from case_input import get_case_input, build_case_text

def build_consultant_prompt(case_text):
    prompt = f"""Using the provided patient case and current, generally accepted clinical guidelines relevant to the presenting condition, provide definitive clinical recommendations with patient-specific rationale.

If clinically important information is missing, state what information is needed and explain how it would affect your recommendation. If a topic is not applicable to the case, state that it is not applicable and briefly explain why.

You will be assessed on clinical accuracy, prioritization, guideline-concordant reasoning, dosing/titration appropriateness (if applicable), safety, and feasibility. Do not include links. Do not use bold, italics, underlining, emojis, highlighting, or tables. Format your response using an alphanumerical outline with the following progression: I, A, 1, a, i.
Be concise. For each lettered/numbered item, provide your determination and the key supporting rationale in 1–3 sentences — do not restate general textbook background, enumerate exhaustive differentials, or explain concepts not specific to this patient. Prioritize depth only on the items most clinically significant to this case; brief acknowledgment is sufficient for items of lower relevance.

End your treatment with a line starting with exactly SUMMARY: followed by a brief clinical summary about 3-4 sentences long to present to another attending physician also reviewing the case. For example, your response should end with a line like: SUMMARY: <your clinical summary here>

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

Here is the case for you to evaluate:
{case_text}
"""
    return prompt


def get_consultant_response(raw_case):
    case_text = call_claude(build_hpi(raw_case), model = DEFAULT_MODEL,  max_tokens = DEFAULT_MAX_TOKENS)
    response = call_claude(build_consultant_prompt(case_text), model = DEFAULT_MODEL,  max_tokens = DEFAULT_MAX_TOKENS)
    plan, summary = response.split("SUMMARY:")
    return plan, case_text, summary

if __name__ == "__main__":
    info = get_case_input()
    raw = build_case_text(info)
    plan, case_text, summary = get_consultant_response(raw)
    print(plan)
    print(summary)