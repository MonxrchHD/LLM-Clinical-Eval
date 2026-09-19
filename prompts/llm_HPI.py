from call_API import call_claude, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from case_input import get_case_input


def build_hpi(case_text):
    prompt = f"""Format a clinical case to present to another attending physician viewing the case. Below is raw case information collected field-by-field from a clinician.

Rewrite this as a single, flowing paragraph — the way a resident would present a patient to their attending, or one attending would hand off a patient to another. Do not use headers, bullet points, or section labels. Integrate the chief complaint, history, and relevant findings into one continuous clinical narrative, in the order a physician would naturally present them (chief complaint and identifying information first, then history, then pertinent findings).

Strict rules:

Use only the information explicitly provided below. Do not add, infer, assume, or interpret anything not explicitly stated.
If a field was reported as "none," "not applicable," "not available," or similar, state it exactly as reported (e.g., "no known drug allergies," "no current medications") — do not rephrase this as though something was omitted, not yet done, or not yet performed.
Do not introduce any topic, section, or finding that was not present in the raw input below (for example, do not mention physical exam findings if none were provided).
Do not add clinical commentary, assessment, differential diagnosis, or recommendations — only reorganize and rephrase what is given into a coherent narrative.

Raw case information:
{case_text}

Provide only the final one-paragraph presentation, with no preamble, headers, or explanation."""

    return prompt


if __name__ == "__main__":
    case_text = get_case_input()
    summary = call_claude(build_hpi(case_text), model=DEFAULT_MODEL,  max_tokens=DEFAULT_MAX_TOKENS)
    print(summary)
