import streamlit as st
import pandas as pd
from io import BytesIO

# 🏫 SCHOOL → PROGRAMME MAPPING
school_programmes = {
    "sonam": ["Nursing", "Midwifery", "Public Health Nursing"],
    "sop": ["Pharmacy", "Pharmacology"],
    "sbbs": ["Biomedical Science", "Medical Laboratory"],
    "som": ["Medicine", "Physician Assistant"],
    "sph": ["Public Health", "Health Promotion", "Disease Control", "Nutrition"],
    "sahs": ["Diagnostic Imaging", "Dietetics", "Medical Laboratory Sciences", "Orthotics and Prosthetics", "Physiotherapy"],
    "ssem": ["Sports Psychology &Rehabilitation", "Sports Nutrition"]
}

# 🔍 Detect School from Programme
def get_school_from_programme(programme):
    for school, progs in school_programmes.items():
        if any(prog.lower() in str(programme).lower() for prog in progs):
            return school
    return "unknown"

# ✉️ Email Generation Logic
def generate_email(first, middle, last, dept, year, student_type):
    username = first[0].lower()
    if middle and middle.strip():
        username += middle[0].lower()
    username += last.lower().replace(" ", "")

    suffix = str(year)[-2:]
    if student_type.lower() == "sandwich":
        suffix += "sw"

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
            (c for c in df.columns if "programme" in c.lower() or "program offered" in c.lower()),
            None
        )

        if not programme_col:
            st.error("⚠️ Could not detect Programme column.")
            st.stop()

        # Name split
        def split_name(fullname):
            parts = str(fullname).strip().split()
            if len(parts) == 1:
                return parts[0], "", ""
            elif len(parts) == 2:
                return parts[0], "", parts[1]
            else:
                return parts[0], " ".join(parts[1:-1]), parts[-1]

        df[["Firstname", "Middlename", "Lastname"]] = df[name_col].apply(
            lambda x: pd.Series(split_name(x))
        )


        # Detect Phone Column
        phone_col = next(   
            (c for c in df.columns if "phone" in c.lower() or "mobile" in c.lower()),
            None
        )

        # Determine department
        df["Department"] = df[programme_col].apply(get_school_from_programme)

        # Generate emails
        df["Email"] = df.apply(lambda row: generate_email(
            str(row["Firstname"]),
            str(row["Middlename"]) if pd.notna(row["Middlename"]) else "",
            str(row["Lastname"]),
            str(row["Department"]),
            admission_year,
            student_type
        ), axis=1)

        # Preview output
        st.success("✅ Emails generated successfully!")
        st.dataframe(df[["Firstname", "Middlename", "Lastname", "Department", "Email"]].head())

    
    # 📤 CREATE FINAL OUTPUT FORMAT
        output_df = pd.DataFrame({
    "Username": df["Email"],
    "First name": df["Firstname"],
    "Last name": df["Lastname"],
    "Display name": df["Firstname"] + " " + df["Lastname"],
    "Job title": "Student",
    "Department": df["Department"],
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

