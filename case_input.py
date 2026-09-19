def get_case_input():
    case = {}
    fields = {
        "Chief Complaint: ": "What is the chief complaint?",
        "PMH: ": "What is the patient's PMH?",
        "PSH: ": "What is the patient's PSH?",
        "Current Medications: ": "What are the patient's current medications?",
        "Pertinent clinical findings: ": "What was seen on clinical examination?",
        "Allergies: ": "What are the patient's allergies?",
        "Labs: ": "What are the patient's labs?",
        "Vitals: ": "What are the patient's vitals?",
    }

    for field, question in fields.items():
        info = input(question + " ")
        case[field] = info
    return case

def build_case_text(case):
    case_text = ""
    for field, response in case.items():
        case_text += f"{field}\n{response}\n"

    return case_text

    
