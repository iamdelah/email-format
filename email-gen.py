import streamlit as st
import pandas as pd
from io import BytesIO

# 🏫 SCHOOL → PROGRAMME MAPP
if "school_programmes" not in st.session_state:
    st.session_state.school_programmes = {
    "sonam": ["BACHELOR OF MIDWIFERY", "BACHELOR OF NURSING", "BACHELOR OF PUBLIC HEALTH NURSING", "BACHELOR OF HEALTH SERVICES ADMINISTRATION", "MASTER OF PHILOSOPHY (NURSING STUDIES)", "MASTER PHILOSOPHY (MIDWIFERY)"],
    "sop": ["DOCTOR OF PHARMACY", "DOCTOR OF PHILOSOPHY (PHARMACOGNOSY)", "MASTER OF PHILOSOPHY (PHARMACEUTICAL CHEMISTRY)", "MASTER OF PHILOSOPHY (PHARMACOLOGY)", "MASTER PHILOSOPHY (PHARMACOGNOSY)", "DOCTOR OF PHILOSOPHY (PHARMACOLOGY)"],
    "sbbs": ["BSc. BIOCHEMISTRY AND MOLECULAR BIOLOGY", "DOCTOR OF PHILOSOPHY (BIOMEDICAL SCIENCES)", "MASTER OF PHILOSOPHY (BIOMEDICAL SCIENCES)"],
    "som": ["BACHELOR OF DENTAL SURGERY", "BACHELOR OF MEDICINE, BACHELOR OF SURGERY", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (CLINICAL TOP-UP)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (CLINICAL)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (COUNSELLING)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (NEUROPSYCHOLOGY TOP-UP)", "COMBINED BACHELOR AND MASTER OF SCIENCE IN PSYCHOLOGY (NEUROPSYCHOLOGY)"],
    "sph": ["BACHELOR OF PUBLIC HEALTH (HEALTH PROMOTION)", "BACHELOR OF PUBLIC HEALTH (HEALTH INFORMATION)", "BACHELOR OF PUBLIC HEALTH (DISEASE CONTROL)", "BACHELOR OF PUBLIC HEALTH (NUTRITION)", "DOCTOR OF PHILOSOPHY (PUBLIC HEALTH)", "MASTER OF PHILOSOPHY (APPLIED EPIDEMIOLOGY)", "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY AND DISEASE CONTROL )", "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY AND DISEASE CONTROL) WEEKEND OPTION", "MASTER OF PUBLIC HEALTH (FAMILY AND REPRODUCTIVE HEALTH)", "MASTER OF PUBLIC HEALTH (FAMILY AND REPRODUCTIVE HEALTH) WEEKEND OPTION", "MASTER OF PUBLIC HEALTH (GENERAL)", "MASTER OF PUBLIC HEALTH (GENERAL) WEEKEND OPTION", "MASTER OF PUBLIC HEALTH (HEALTH PROMOTION) WEEKEND OPTION"],
    "sahs": ["BACHELOR OF DIAGNOSTIC IMAGING (RADIOGRAPHY)", "BACHELOR OF DIETETICS", "BACHELOR OF SPEECH, LANGUAGE AND HEARING SCIENCES", "BACHELOR OF ORTHOTICS AND PROSTHETICS", "BACHELOR OF PHYSIOTHERAPY", "DOCTOR OF MEDICAL LABORATORY (SANDWICH)", "DOCTOR OF MEDICAL LABORATORY SCIENCES", "DOCTOR OF MEDICAL LABORATORY SCIENCES (TOP UP)", "Master of Philosophy in Medical Laboratory Sciences (Chemical Pathology)", "Master of Philosophy in Medical Laboratory Sciences (Haematology)", "Master of Philosophy in Medical Laboratory Sciences (Histopathology/Cytopathology)", "Master of Philosophy in Medical Laboratory Sciences (Immunology/Vaccinology)", "MASTER OF SCIENCE (BIOMEDICAL SCIENCES)", "PhD in Medical Laboratory Sciences (Clinical Microbiology)", "Phd in medical laboratory sciences (Histopathology/Cytopathology)"],
    "ssem": ["BACHELOR OF SPORTS AND EXERCISE MEDICAL SCIENCES", "Sports Nutrition"]
}
school_programmes = st.session_state.school_programmes 

# 🧭 SIDEBAR - MAPPING EDITOR
st.sidebar.header("🏫 School – Programme Mapping")

# Display existing mapping (read-only)
for school, programmes in st.session_state.school_programmes.items():
    st.sidebar.markdown(
        f"**{school.upper()}**: {', '.join(programmes)}"
    )

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add Programme to School")

school_to_add = st.sidebar.selectbox(
    "Select School",
    list(st.session_state.school_programmes.keys())
)

new_programme = st.sidebar.text_input("New Programme Name")

if st.sidebar.button("Add Programme"):
    if new_programme:
        existing = st.session_state.school_programmes[school_to_add]
        if new_programme not in existing:
            existing.append(new_programme)
            st.sidebar.success("Programme added successfully!")
        else:
            st.sidebar.warning("Programme already exists.")

st.sidebar.markdown("---")
st.sidebar.subheader("🏫 Add New School")

new_school = st.sidebar.text_input("New School Code (e.g. sohs)")
new_school_programme = st.sidebar.text_input("Initial Programme")

if st.sidebar.button("Add School"):
    if new_school:
        if new_school.lower() not in st.session_state.school_programmes:
            st.session_state.school_programmes[new_school.lower()] = (
                [new_school_programme] if new_school_programme else []
            )
            st.sidebar.success("New school added!")
        else:
            st.sidebar.warning("School already exists.")


# 🔍 Detect School from Programme
def get_school_from_programme(programme):
    for school, progs in school_programmes.items():
        if any(prog.lower() in str(programme).lower() for prog in progs):
            return school
    return "unknown"

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
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
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

        # Apply name split function
        df[["Lastname", "Middlename", "Firstname"]] = df[name_col].apply(
            lambda x: pd.Series(split_name(x))
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
            int(row["Level"])
        ), axis=1)
        

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
    "Mobile phone": df[phone_col] if phone_col else "",
    "Fax": "",
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
    label="📥 Download Excel (Import Format)",
    data=output,
    file_name=f"UHAS_{student_type}_{admission_year}_emails.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


        st.download_button(
            label="📥 Download Excel with Emails",
            data=output,
            file_name=f"UHAS_{student_type}_{admission_year}_emails.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")

