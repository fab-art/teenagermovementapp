import json
import re

def parse_guidelines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by ATC Classes (A, B, C...)
    sections = re.split(r'\n([A-V])\. ', content)

    drug_master = []
    guidelines = []

    # sections[0] is intro
    for i in range(1, len(sections), 2):
        class_letter = sections[i]
        class_body = sections[i+1]

        # Extract subclasses (e.g. A01, A02)
        subclasses = re.split(r'\n([A-V]\d{2}[A-Z]?) ', class_body)

        for j in range(1, len(subclasses), 2):
            subclass_code = subclasses[j]
            subclass_body = subclasses[j+1]

            # Extract sections
            patho = re.search(r'■ PATHOPHYSIOLOGY & DISEASE MECHANISM(.*?)(?=■|$)', subclass_body, re.S)
            pharmacology = re.search(r'■ PHARMACOLOGICAL PRINCIPLES(.*?)(?=■|$)', subclass_body, re.S)
            dispensing = re.search(r'■ CLINICAL DISPENSING GUIDANCE(.*?)(?=■|$)', subclass_body, re.S)
            medicines_table = re.search(r'■ REIMBURSABLE MEDICINES IN THIS SUBCLASS(.*?)(?=$)', subclass_body, re.S)

            subclass_title = subclass_body.split('\n')[0].strip()

            guideline = {
                "atc_code": subclass_code,
                "title": subclass_title,
                "pathophysiology": patho.group(1).strip() if patho else "",
                "pharmacology": pharmacology.group(1).strip() if pharmacology else "",
                "dispensing_guidance": dispensing.group(1).strip() if dispensing else ""
            }
            guidelines.append(guideline)

            if medicines_table:
                table_text = medicines_table.group(1).strip()
                lines = table_text.split('\n')
                for line in lines:
                    if '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            generic = parts[0].strip()
                            brand = parts[1].strip()
                            strength_form = parts[2].strip()

                            # Filter out header
                            if generic == "Generic Name (INN)":
                                continue

                            drug_master.append({
                                "id": f"{subclass_code}-{len(drug_master)}",
                                "generic_name": generic,
                                "brand_name": brand,
                                "strength_form": strength_form,
                                "atc_code": subclass_code,
                                "therapeutic_class": subclass_title,
                                "rhia_covered": True
                            })

    return drug_master, guidelines

if __name__ == "__main__":
    drugs, guides = parse_guidelines('scripts/guideline_source.txt')

    with open('frontend/src/data/drug_master.json', 'w') as f:
        json.dump(drugs, f, indent=2)

    with open('frontend/src/data/guidelines.json', 'w') as f:
        json.dump(guides, f, indent=2)

    print(f"Parsed {len(drugs)} drugs and {len(guides)} guidelines.")
