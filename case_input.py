

def get_case_input():
    case_text = ""
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
        case_text += f"{field}{info}\n"

    return case_text


if __name__ == "__main__":
    case_text = get_case_input()
    print("\n===Assembled Case Text===\n")
    print(case_text)
