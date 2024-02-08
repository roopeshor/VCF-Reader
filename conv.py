import array
import re
import json
import quopri

ARRAY_DEL = ','
FIELD_RE = r"[a-zA-Z0-9;=\-]+:"
CSV_SEPARATOR = ','
IGNORED_FIELDS = ["VERSION", "PHOTO;ENCODING=BASE64;JPEG"]

contacts = []
field_set = set([])

# convert vcf to array of contacts object

def toObj(f):
	field = ""
	contact = {}
	contacts = []
	for i, ln in enumerate(f):
		line = ln.strip()
		f = re.search(FIELD_RE, line)

		# remove last column
		if f:
			f = f.group()[:-1]
		else:
			f = ""
		
		# start from : remove that colon if it exists
		value = line[len(f):].replace(":","")
		if f == "BEGIN":
			field = ""
		elif f == "END":
			field = ""
			contacts += [contact]
			contact = {}
		elif f == "" and field != "":
			# no field names are present appears to
			# be continuation of previous field, like note/photo
			if isinstance(contact[field], array.array):
				contact[field] += [value]
			else:
				contact[field] += value
		else:
			# new field
			field = f
			if field in contact:
				if isinstance(contact[field], list):
					contact[field] += [value]
				else:
					contact[field] = [value, contact[field]]
			else:
				contact[field] = value
	return contacts

with open('all.vcf', 'r') as file:
	contacts = toObj(file)


for contact in contacts:
	# extract all the fields
	field_set |= set(contact.keys())
	for ign in IGNORED_FIELDS:
	# remove ignored fields
		if ign in contact:
			del contact[ign]

field_set = sorted(field_set)

# convert encoding to proepr ones
for contact in contacts:
	for field in contact:
		separate = field.split("ENCODING=")
		if len(separate) > 1:
			txt = contact[field]
			if separate[1] == "QUOTED-PRINTABLE":
				contact[field] = quopri.decodestring(contact[field].replace("==", "=")).decode('utf-8')


# got through all contacts and generate csv
contactsCSV = ""
for field in field_set:
	contactsCSV += field + CSV_SEPARATOR
contactsCSV = contactsCSV[:-1] + '\n'

for contact in contacts:
	for field in field_set:
		if field in contact:
			entry = contact[field]
			if isinstance(entry, list):
				entry = ARRAY_DEL.join(entry)
			contactsCSV += '"' + entry.replace('"', "'") + '"'
		contactsCSV += CSV_SEPARATOR
	# trim last comma and add new line
	contactsCSV = contactsCSV[:-1] + '\n'

# write to file
with open('new.csv', 'w') as f2:
	f2.write(contactsCSV)
	f2.close()

# write to file
with open('new.json', 'w') as f2:
	json.dump(contacts, f2, ensure_ascii=False)
	f2.close()
