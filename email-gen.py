import streamlit as st
import pandas as pd
from io import BytesIO
import re

#name parser (fixes ALL your errors)
def parse_name(raw_name):
    if not raw_name or not str(raw_name).strip():
        return "", "", ""

    name = str(raw_name).replace(",", "").strip()
    parts = name.split()

    if len(parts) == 1:
        return parts[0].title(), "", parts[0].title()

    first = parts[0].title()
    last = parts[-1].title()
    middle = " ".join(parts[1:-1]).title() if len(parts) > 2 else ""

    return first, middle, last

# GROUP MAP
COURSE_GROUPS = {
    "B42029": {
        "gid": 500,
        "courses": [
            "BACHELOR OF DIAGNOSTIC IMAGING (RADIOGRAPHY)",
            "BACHELOR OF DIETETICS",
            "BACHELOR OF HEALTH SERVICES ADMINISTRATION",
            "BACHELOR OF MIDWIFERY",
            "BACHELOR OF NURSING",
            "BACHELOR OF ORTHOTICS AND PROSTHETICS",
            "BACHELOR OF PHYSIOTHERAPY",
            "BACHELOR OF PUBLIC HEALTH (DISEASE CONTROL)",
            "BACHELOR OF PUBLIC HEALTH (HEALTH INFORMATION)",
            "BACHELOR OF PUBLIC HEALTH (NUTRITION)",
            "BACHELOR OF PUBLIC HEALTH NURSING",
            "BACHELOR OF SPEECH, LANGUAGE AND HEARING SCIENCES",
            "BACHELOR OF SPORTS AND EXERCISE MEDICAL SCIENCES",
            "BSc. BIOCHEMISTRY AND MOLECULAR BIOLOGY",
            "DOCTOR OF PHILOSOPHY (BIOMEDICAL SCIENCES)",
            "DOCTOR OF PHILOSOPHY (PHARMACOGNOSY)",
            "PHD IN MEDICAL LABORATORY SCIENCES (CLINICAL MICROBIOLOGY)",
            "PHD IN MEDICAL LABORATORY SCIENCES (HISTOPATHOLOGY/CYTOPATHOLOGY)"
        ]
    },

    "B62031": {
        "gid": 501,
        "courses": [
            "BACHELOR OF DENTAL SURGERY",
            "BACHELOR OF MEDICINE, BACHELOR OF SURGERY",
        ]
    },

    "D62031": {
        "gid": 502,
        "courses": [
            "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (CLINICAL)",
            "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (COUNSELLING)",
            "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (NEUROPSYCHOLOGY)",
            "DOCTOR OF MEDICAL LABORATORY SCIENCES",
            "DOCTOR OF PHARMACY"
        ]
    },

    "M22028": {
        "gid": 503,
        "courses": [
            "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (CLINICAL TOP-UP)",
            "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (NEUROPSYCHOLOGY TOP-UP)",
            "DOCTOR OF MEDICAL LABORATORY (SANDWICH)",
            "DOCTOR OF MEDICAL LABORATORY SCIENCES (TOP UP)",
            "DOCTOR OF PHILOSOPHY (PUBLIC HEALTH)",
            "MASTER OF PHILOSOPHY (APPLIED EPIDEMIOLOGY)",
            "MASTER OF PHILOSOPHY (BIOMEDICAL SCIENCES)",
            "MASTER OF PHILOSOPHY (NURSING STUDIES)",
            "MASTER OF PHILOSOPHY (PHARMACOLOGY)",
            "MASTER OF PHILOSOPHY (MIDWIFERY)",
            "MASTER OF PHILOSOPHY (PHARMACOGNOSY)",
            "MASTER OF PHILOSOPHY (PHARMACEUTICAL CHEMISTRY)",
            "MASTER OF PHILOSOPHY (PHARMACOLOGY)",
            "MASTER OF PHILOSOPHY (BIOMEDICAL SCIENCES)",
            "MASTER OF SCIENCE (BIOMEDICAL SCIENCES)",
            "MASTER PHILOSOPHY (MIDWIFERY)",
            "MASTER PHILOSOPHY (PHARMACOGNOSY)"
        ]
    },

    "M12027": {
        "gid": 504,
        "courses": [
            "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY AND DISEASE CONTROL )",
            "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY AND DISEASE CONTROL) WEEKEND OPTION",
            "MASTER OF PUBLIC HEALTH (FAMILY AND REPRODUCTIVE HEALTH)",
            "MASTER OF PUBLIC HEALTH (FAMILY AND REPRODUCTIVE HEALTH) WEEKEND OPTION",
            "MASTER OF PUBLIC HEALTH (GENERAL)",
            "MASTER OF PUBLIC HEALTH (GENERAL) WEEKEND OPTION",
            "MASTER OF PUBLIC HEALTH (HEALTH PROMOTION) WEEKEND OPTION"
        ]
    }
}


# group a student belongs to
def detect_group(programme):
    prog_norm = normalize_program(programme)

    for group_code, info in COURSE_GROUPS.items():
        for keyword in info["courses"]:
            keyword_norm = normalize_program(keyword)
            if keyword_norm and keyword_norm in prog_norm:
                return group_code

    # fallback: check for key words within programme
    if "DOCTOR" in prog_norm or "PHD" in prog_norm:
        return "D62031"
    if "MASTER" in prog_norm or "MSc" in prog_norm:
        return "M22028"
    if "BACHELOR" in prog_norm or "BSC" in prog_norm:
        # cannot decide between B4/B6, leave for determine_group
        return None

    return None  # unmatched programmes


# 🏫 SCHOOL → PROGRAMME MAPP
if "school_programmes" not in st.session_state:
    st.session_state.school_programmes = {
    "sonam": ["BACHELOR OF MIDWIFERY", "BACHELOR OF NURSING", "BACHELOR OF PUBLIC HEALTH NURSING", "BACHELOR OF HEALTH SERVICES ADMINISTRATION", "MASTER OF PHILOSOPHY (NURSING STUDIES)", "MASTER PHILOSOPHY (MIDWIFERY)", "BSCMIDS", "BSCNUSDW", "BPHNUS", "BSCMITSW", "BSCNUTSW", "BPHNUTSW"],
    "sop": ["DOCTOR OF PHARMACY", "DOCTOR OF PHILOSOPHY (PHARMACOGNOSY)", "MASTER OF PHILOSOPHY (PHARMACEUTICAL CHEMISTRY)", "MASTER OF PHILOSOPHY (PHARMACOLOGY)", "MASTER PHILOSOPHY (PHARMACOGNOSY)", "DOCTOR OF PHILOSOPHY (PHARMACOLOGY)"],
    "sbbs": ["BSc. BIOCHEMISTRY AND MOLECULAR BIOLOGY", "DOCTOR OF PHILOSOPHY (BIOMEDICAL SCIENCES)", "MASTER OF PHILOSOPHY (BIOMEDICAL SCIENCES)"],
    "som": ["BACHELOR OF DENTAL SURGERY", "BACHELOR OF MEDICINE, BACHELOR OF SURGERY", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (CLINICAL TOP-UP)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (CLINICAL)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (COUNSELLING)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (NEUROPSYCHOLOGY TOP-UP)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (NEUROPSYCHOLOGY)"],
    "sph": ["BACHELOR OF PUBLIC HEALTH (HEALTH PROMOTION)", "BACHELOR OF PUBLIC HEALTH (HEALTH INFORMATION)", "BACHELOR OF PUBLIC HEALTH (DISEASE CONTROL)", "BACHELOR OF PUBLIC HEALTH (NUTRITION)", "DOCTOR OF PHILOSOPHY (PUBLIC HEALTH)", "MASTER OF PHILOSOPHY (APPLIED EPIDEMIOLOGY)", "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY AND DISEASE CONTROL )", "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY AND DISEASE CONTROL) WEEKEND OPTION", "MASTER OF PUBLIC HEALTH (FAMILY AND REPRODUCTIVE HEALTH)", "MASTER OF PUBLIC HEALTH (FAMILY AND REPRODUCTIVE HEALTH) WEEKEND OPTION", "MASTER OF PUBLIC HEALTH (GENERAL)", "MASTER OF PUBLIC HEALTH (GENERAL) WEEKEND OPTION", "MASTER OF PUBLIC HEALTH (HEALTH PROMOTION) WEEKEND OPTION"],
    "sahs": ["BACHELOR OF DIAGNOSTIC IMAGING (RADIOGRAPHY)", "BACHELOR OF DIETETICS", "BACHELOR OF SPEECH, LANGUAGE AND HEARING SCIENCES", "BACHELOR OF ORTHOTICS AND PROSTHETICS", "BACHELOR OF PHYSIOTHERAPY", "DOCTOR OF MEDICAL LABORATORY (SANDWICH)", "DOCTOR OF MEDICAL LABORATORY SCIENCES", "DOCTOR OF MEDICAL LABORATORY SCIENCES (TOP UP)", "Master of Philosophy in Medical Laboratory Sciences (Chemical Pathology)", "Master of Philosophy in Medical Laboratory Sciences (Haematology)", "Master of Philosophy in Medical Laboratory Sciences (Histopathology/Cytopathology)", "Master of Philosophy in Medical Laboratory Sciences (Immunology/Vaccinology)", "MASTER OF SCIENCE (BIOMEDICAL SCIENCES)", "PhD in Medical Laboratory Sciences (Clinical Microbiology)", "Phd in medical laboratory sciences (Histopathology/Cytopathology)", "BPSISW", "BPHEHSW", "BPHMHSW", "BPHHPSW", "BPHDCSW", "BPHNSW"],
    "ssem": ["BACHELOR OF SPORTS AND EXERCISE MEDICAL SCIENCES", "Sports Nutrition"]
}
school_programmes = st.session_state.school_programmes 


# 🔍 Detect School from Programme

def normalize_program(programme):
    if not programme or not str(programme).strip():
        return ""
    cleaned = str(programme).upper().strip()
    cleaned = re.sub(r"[^A-Z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def get_school_from_programme(programme):
    prog_norm = normalize_program(programme)
    if not prog_norm:
        return "unknown"

    for school, progs in school_programmes.items():
        for mapped_prog in progs:
            mapped_norm = normalize_program(mapped_prog)

            # exact/contains match
            if mapped_norm and (mapped_norm in prog_norm or prog_norm in mapped_norm):
                return school

            # fuzzy token overlap (helps abbreviations/spelling variations)
            mapped_tokens = set(mapped_norm.split())
            prog_tokens = set(prog_norm.split())
            if mapped_tokens and prog_tokens:
                overlap = mapped_tokens.intersection(prog_tokens)
                if len(overlap) / max(len(mapped_tokens), 1) >= 0.7:
                    return school

    return "unknown"


# Group codes and GID mappings (base GIDs by program type)
GID_MAPPING = {
    "B4": 500,  # 4-year bachelors
    "B6": 501,  # 6-year bachelors
    "D6": 502,  # Doctorate
    "M2": 503,  # 2-year masters
    "M1": 504,  # 1-year masters
}

def get_gid_from_group(group_code):
    """Extract GID from group code based on program type prefix."""
    for prefix, gid in GID_MAPPING.items():
        if group_code.startswith(prefix):
            return gid
    return 500  # Default to bachelors if unrecognized

#Determine group code automatically
def determine_group(programme, admission_year):
    prog = programme.lower()

    # Doctorate
    if any(x in prog for x in ["doctor", "phd"]):
        return "D62031"

    # Masters
    if "master" in prog:
        return "M22028"  # default 2-year
        # if you later detect 1-year → return "M1027"

    # Bachelors (default 4 years)
    grad_year = admission_year + 3
    return f"B4{grad_year}"


# ✉️ Email Generation Logic
def generate_email(first, middle, last, dept, year, student_type, level):
    # Handle empty strings
    if not first or not first.strip():
        first = ""
    if not last or not last.strip():
        last = ""
    
    username = ""
    
    # Add first initial
    if first:
        username += first[0].lower()
    
    # Add all middle initials
    if middle and middle.strip():
        for word in middle.split():
            if word:
                username += word[0].lower()
    
    # Add full last name
    if last:
        username += last.lower().replace(" ", "")

    suffix = str(year)[-2:]
    if student_type.lower() == "sandwich":
        suffix += "sw"

    if level > 400:
        suffix += "pg"       

    return f"{username}{suffix}@{dept.lower()}.uhas.edu.gh"


# LDAP row generator
def generate_ldif_block(row, index_number, group_code):
    email = row["Email"]
    full_name = f"{row['Lastname']} {row['Firstname']} {row['Middlename']}".replace("  ", " ").strip().upper()

    # Prefer the specific GID from COURSE_GROUPS, but fall back to a prefix-based mapping
    if group_code in COURSE_GROUPS:
        gid = COURSE_GROUPS[group_code]["gid"]
    else:
        gid = get_gid_from_group(group_code)

    return f"""
dn: uid={email},ou={group_code},ou=students,dc=uhas,dc=edu,dc=gh
cn: {full_name}
displayName: {full_name}
gecos: {group_code}
gidNumber: {gid}
givenName: {full_name}
homeDirectory: /home/users/{email}
loginShell: /bin/bash
mail: {email}
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: posixAccount
objectClass: shadowAccount
objectClass: top
shadowLastChange: 17366
sn: {row['Lastname'].upper()}
uid: {email}
uidNumber: {index_number}
userPassword: UHAS{index_number}
""".strip()


# 🎨 STREAMLIT APP
st.set_page_config(page_title="UHAS Email Generator", page_icon="📧", layout="wide")
st.title("📧 UHAS Student Email Generator")
st.write("Upload student data and automatically generate institutional emails for **Regular** or **Sandwich** students.")

# DROPDOWN INPUTS
col1, col2 = st.columns(2)
with col1:
    student_type = st.selectbox("Select Student Type", ["Regular", "Sandwich"])
with col2:
    admission_year = st.selectbox("Select Admission Year", [2025, 2026])

# FILE UPLOAD
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Check file extension and read accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.write("### Preview of Uploaded File")
        st.dataframe(df.head())


        # Normalize column names
        df.columns = [c.strip().title() for c in df.columns]

        # Detect Name Column
        name_col = next(
            (c for c in df.columns if "name" in c.lower()),
            None
        )

        if not name_col:
            st.error("⚠️ Could not detect a Name/Fullname column.")
            st.stop()


        # Detect Programme column
        programme_col = next(
            (c for c in df.columns if "program" in c.lower() or "program offered" in c.lower()),
            None
        )

        if not programme_col:
            st.error("⚠️ Could not detect Program column.")
            st.stop()

        # Name split
        def split_name(fullname):
            # Check if name has comma (format: LASTNAME, FIRSTNAME MIDDLENAME)
            if "," in str(fullname):
                parts = str(fullname).split(",")
                last_name = parts[0].strip().title()
                # Everything after comma is first and middle names
                remaining = parts[1].strip() if len(parts) > 1 else ""
                remaining_parts = remaining.split()
                
                if len(remaining_parts) == 0:
                    return "", "", last_name
                elif len(remaining_parts) == 1:
                    return remaining_parts[0].title(), "", last_name
                else:
                    return (
                        remaining_parts[0].title(),
                        " ".join(remaining_parts[1:]).title(),
                        last_name
                    )
            
            # No comma - use original logic
            clean = (
                str(fullname)
                .replace("  ", "")
                .strip()
            )

            parts = clean.split()

            if len(parts) == 1:
                return parts[0].title(), "", ""
            elif len(parts) == 2:
                return parts[0].title(), "", parts[1].title()
            else:
                return (
                    parts[0].title(),
                    " ".join(parts[1:-1]).title(),
                    parts[-1].title()
                )


        # Detect Phone Column
        phone_col = next(   
            (c for c in df.columns if "phone" in c.lower() or "mobile" in c.lower()),
            None
        )

        # Detect Student No Column
        index_col = next(   
            (c for c in df.columns if "student" in c.lower() or "index" in c.lower() or "form" in c.lower()),
            None
        )

        # Detect Level Column
        level_col = next(
            (c for c in df.columns if "level" in c.lower()),
            None
        )

        # Apply name split function
        name_column = next(
    (c for c in df.columns if "name" in c.lower()),
    None
        )

        if not name_column:
            st.error("Name column not found.")
            st.stop()

        df[["Firstname", "Middlename", "Lastname"]] = df[name_column].apply(
    lambda x: pd.Series(parse_name(x))
)


        # Determine department
        df["Department"] = df[programme_col].apply(get_school_from_programme)

        # Generate emails
        df["Email"] = df.apply(lambda row: generate_email(
            str(row["Lastname"]),
            str(row["Middlename"]) if pd.notna(row["Middlename"]) else "",
            str(row["Firstname"]),
            str(row["Department"]),
            admission_year,
            student_type,
            int(row[level_col]) if level_col and pd.notna(row[level_col]) else 0
        ), axis=1)

        # generate LDIF blocks and separate them by COURSE_GROUPS
        ldif_blocks = []
        # initialize per-group containers (plus an 'unknown' bucket)
        ldif_files = {k: [] for k in COURSE_GROUPS.keys()}
        ldif_files.setdefault("unknown", [])

        for _, row in df.iterrows():
            index_number = str(row[index_col]).strip() if index_col and pd.notna(row[index_col]) else "N/A"
            # Create uid_number without "UHAS" prefix
            uid_number = index_number
            if uid_number.startswith("UHAS"):
                uid_number = uid_number[4:]

            programme_value = str(row[programme_col]) if pd.notna(row[programme_col]) else ""

            # Try to detect exact group from COURSE_GROUPS; fall back to determine_group-derived mapping
            detected = detect_group(programme_value)
            if detected:
                group_code = detected
            else:
                derived = determine_group(programme_value, admission_year)
                if derived.startswith("B4"):
                    group_code = "B42029"
                elif derived.startswith("B6"):
                    group_code = "B62031"
                elif derived.startswith("D6"):
                    group_code = "D62031"
                elif derived.startswith("M2"):
                    group_code = "M22028"
                elif derived.startswith("M1"):
                    group_code = "M12027"
                else:
                    group_code = "unknown"

            block = generate_ldif_block(row, uid_number, group_code)

            if group_code in ldif_files:
                ldif_files[group_code].append(block)
            else:
                ldif_files.setdefault("unknown", []).append(block)

            ldif_blocks.append(block)

       
        # Preview output
        st.success("✅ Emails generated successfully!")
        st.dataframe(df[["Lastname", "Middlename", "Firstname", "Department", "Email"]].head())

    
    # 📤 CREATE FINAL OUTPUT FORMAT
        output_df = pd.DataFrame({
        "Username": df["Email"],
        "First name": df["Lastname"],
        "Last name": df["Firstname"],
        "Display name": df["Firstname"] + " " + df["Middlename"].fillna("") + " " + df["Lastname"],
        "Job title": "Student",
        "DEPARTMENT": df["Department"].fillna("").astype(str).str.upper(),
        "Office number": "",
        "Office phone": "",
        "Mobile phone": df[phone_col].fillna("") if phone_col else "",
        "Index Number": df[index_col].fillna("") if index_col else "",
        "Alternate email address": df["Email"],
        "Address": "",
        "City": "Ho",
        "State or province": "Volta",
        "ZIP or postal code": "",
        "Country or region": "Ghana"
    })

# 📥 DOWNLOAD EXCEL
        output = BytesIO()
        output_df.to_excel(output, index=False)
        output.seek(0)

        st.write("### Preview of Generated Import File")
        st.dataframe(output_df.head())


        st.download_button(
            label="📥 Download Excel with Emails",
            data=output,
            file_name=f"UHAS_{student_type}_{admission_year}_emails.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

         # Combined LDIF for download
        ldif_output = "\n\n".join(ldif_blocks)

        # Provide per-group LDIF downloads
        st.write("### LDIF files by group")
        for group_code, blocks in ldif_files.items():
            if not blocks:
                continue
            content = "\n\n".join(blocks)
            st.download_button(
                label=f"📥 Download {group_code}.ldif",
                data=content,
                file_name=f"{group_code}.ldif",
                mime="text/plain"
            )

        #st.download_button(
        #    label="📥 Download LDIF File for all students",
        #    data=ldif_output,
        #    file_name="uhas_students.ldif",
        #    mime="text/plain"
        #)

    except Exception as e:
        st.error(f"❌ Error: {e}")
