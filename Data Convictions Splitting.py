import re
import fasttext

model = fasttext.load_model("C:/Users/293740/Desktop/New folder/lid.176.bin")

def french(input):
    predictions = model.predict(input, k=1)
    language = predictions[0][0].replace('__label__', '')
    return (language)

def separate_text(input_text):
    lowercase_txt = input_text.lower()
    lines = lowercase_txt.split('\n')
    sections = []
    #current_section = []

    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        if french(line) == 'fr':  # Skip French text
            continue

        else:
            sections.append(line)

    return sections


def data_seperator(lst):
    medical_procedure_list = []
    medical_date_list = []
    conviction_list = []

    previous_entry = None

    for line in lst:
        if re.match(r'^[a-zA-Z\s]+$', line):
            medical_procedure_list.append(line)
        # elif re.match(r'^[a-zA-Z\s] + [\'\"]+$', line):
        #     medical_procedure_list.append(line)
        elif re.match(r'^\d{2}/\d{2}/\d{2} [a-zA-Z\s._-]+$', line):
            conviction_list.append(line)
            previous_entry = line
            continue
        elif re.match(r'^[a-zA-Z\s]+ \d{4}/\d{2}/\d{2}$', line) and 'offence date' not in line:
            medical_date_list.append(line)
       
        elif previous_entry != None:
            if re.match(r'^\d{2}/\d{2}/\d{2} [a-zA-Z\s._-]+$', previous_entry) and 'offence date' in line:
                conviction_list[-1] += ' ' + line
                previous_entry = None
           
    return medical_procedure_list, medical_date_list, conviction_list

text = """REQUIRES CORRECTIVE LENSES"
VERRES CORRECTEURS REQUIS
20/03/09 DISOBEY LEGAL SIGN
OFFENCE DATE 2020/02/20
INOBSERVATION D'UN PANNEAU OFFICIEL
DATE DE L'INFRACTION 2020/02/20
20/03/09 FAIL TO HAVE INSURANCE CARD - C.A.I.A.
OFFENCE DATE 2020/02/20
DEFAUT D'AVOIR UNE CARTE D'ASSURANCE - L.A.A.O.
DATE DE L'INFRACTION 2020/02/20
MEDICAL DUE DATE 2020/09/03"""

input_text = text.replace('"','')

sections = separate_text(input_text)
print(sections)

result = data_seperator(sections)

medical_procedure_list, medical_date_list, conviction_list = result

print("Medical Procedure List:", medical_procedure_list)
print("Medical Date List:", medical_date_list)
print("Conviction List:", conviction_list)