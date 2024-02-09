import json
from utils import *

ARRAY_DEL = ","
CSV_SEPARATOR = ","
PRETTY_PRINT_JSON = True

contacts = []
field_set = set([])

with open("all.vcf", "r") as file:
    contacts = toObj(file)


# extract all the fields
for contact in contacts:
    field_set |= set(contact.keys())

field_set = sorted(field_set)


# got through all contacts and generate csv

# header
contactsCSV = ""
for field in field_set:
    contactsCSV += f'"{field}"{CSV_SEPARATOR}'
contactsCSV = contactsCSV[:-1] + "\n"

# data
for contact in contacts:
    for field in field_set:
        if field in contact:
            entry = contact[field]
            if isinstance(entry, list):
                entry = ARRAY_DEL.join(entry)
            contactsCSV += '"' + entry.replace('"', "'") + '"'
        contactsCSV += CSV_SEPARATOR
    # trim last comma and add new line
    contactsCSV = contactsCSV[:-1] + "\n"

# write to file
with open("new.csv", "w") as f2:
    f2.write(contactsCSV)
    f2.close()

# write to file
with open("new.json", "w") as f2:
    if PRETTY_PRINT_JSON:
        json.dump(contacts, f2, ensure_ascii=False, indent=2)
    else:
        json.dump(contacts, f2, ensure_ascii=False)
    f2.close()
