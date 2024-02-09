import re
import quopri
from aliases import ALIASES
import array


FIELD_RE = r"[a-zA-Z0-9;=\-]+:"
IGNORED_FIELDS = ["VERSION", "N", "PHOTO;ENCODING=BASE64;JPEG"]
XC = "X-ANDROID-CUSTOM"
REMOVE_PH_DASH = True

def decode_strs(field, value):
    """Decodes strings

    Args:
        field (str): field name
        value (str): value

    Returns:
        [str, str]: decoded string along with modified field name
    """
    separate = field.split(";ENCODING=")
    if len(separate) > 1:
        txt = value
        if separate[1] == "QUOTED-PRINTABLE":
            value = quopri.decodestring(value.replace("==", "=")).decode("utf-8")
        field = separate[0]
    return [field, value]


def extract_field_data(value):
    field_data = "Custom Attribute"
    field_name = value
    # X-ANDROID-FIELDs
    if "vnd.android.cursor.item/" in value:
        value = value[24:]
        [field_name, field_data, field_attr] = value.split(";")[:3]
        if field_name in ALIASES[XC]:
            alias_data = ALIASES[XC][field_name]
            if isinstance(alias_data, str):
                field_name = alias_data
            else:
                field_data = f"{field_data} ({alias_data[field_attr]})"
    return [field_name, field_data]


def fmt_number(num):
    return num.replace("-", "") if REMOVE_PH_DASH else num


def format_tel(contact):
    tel_nums = {}
    tels = [f for f in dict.keys(contact) if "TEL;" in f]
    for t in tels:
        prefix = t[4:].capitalize()
        fname = f"Phone{f': {prefix}' if prefix != 'Cell' else ''}"
        if isinstance(contact[t], list):
            c = 0
            for num in contact[t]:
                num_name = f"{fname}{f' {c}' if c > 0 else ''}"
                contact[num_name] = fmt_number(num)
                c += 1
        else:
            contact[fname] = fmt_number(contact[t])
        del contact[t]

# preprocess fields (ie replace by aliases)
def preprocess_fields(contact):
    c2 = {}
    for field in contact.copy():
        if field in IGNORED_FIELDS:
            continue

        [f, d] = decode_strs(field, contact[field])
        c2[f] = d
        subfields = field.split(";")
        f0 = subfields[0]
        fp = f
        if f0 in ALIASES:
            alias = ALIASES[f0]
            val = c2[f]
            if isinstance(alias, str):
                c2[alias] = val
                fp = alias
            else:
                [ex_field, data] = extract_field_data(val)
                c2[ex_field] = data
                fp = ex_field
            del c2[f]

    # format phone numbers
    format_tel(c2)
    return c2


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
        value = line[len(f) :].replace(":", "")
        if f == "BEGIN":
            field = ""
        elif f == "END":
            field = ""
            contact = preprocess_fields(contact)
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
