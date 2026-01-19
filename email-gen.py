import streamlit as st
import pandas as pd
from io import BytesIO

# -------------------------
# 🏫 SCHOOL → PROGRAMME MAPPING
# -------------------------
school_programmes = {
    "sonam": ["Nursing", "Midwifery", "Public Health Nursing"],
    "sop": ["Pharmacy", "Pharmacology"],
    "sbbs": ["Biomedical Science", "Medical Laboratory"],
    "som": ["Medicine", "Physician Assistant"],
    "sph": ["Public Health", "Health Promotion", "Disease Control", "Nutrition"],
    "sahs": ["Diagnostic Imaging", "Dietetics", "Medical Laboratory Sciences", "Orthotics and Prosthetics", "Physiotherapy"],
    "ssem": ["Sports Psychology &Rehabilitation", "Sports Nutrition"]
}

# -------------------------
# 🔍 Detect School from Programme
# -------------------------
def get_school_from_programme(programme):
    for school, progs in school_programmes.items():
        if any(prog.lower() in str(programme).lower() for prog in progs):
            return school
    return "unknown"

# -------------------------
# ✉️ Email Generation Logic
# -------------------------
def generate_email(first, middle, last, dept, year, student_type):
    first_letter = first[0].lower()
    middle_letter = middle[0].lower() if pd.notna(middle) and middle.strip() else ''
    lastname = last.lower().replace(' ', '')
    
    suffix = ""
    if student_type.lower() == "sandwich":
        suffix = f"{str(year)[-2:]}sw"
    
    email = f"{first_letter}{middle_letter}{lastname}{suffix}@{dept.lower()}.uhas.edu.gh"
    return email

# -------------------------
# 🎨 STREAMLIT APP
# -------------------------
st.set_page_config(page_title="UHAS Email Generator", page_icon="📧", layout="wide")
st.title("📧 UHAS Student Email Generator")
st.write("Upload student data and automatically generate institutional emails for **Regular** or **Sandwich** students.")

# -------------------------
# DROPDOWN INPUTS
# -------------------------
col1, col2 = st.columns(2)
with col1:
    student_type = st.selectbox("Select Student Type", ["Regular", "Sandwich"])
with col2:
    admission_year = st.selectbox("Select Admission Year", [2025, 2026])

# -------------------------
# FILE UPLOAD
# -------------------------
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("### Preview of Uploaded File")
        st.dataframe(df.head())

        # Normalize column names
        df.columns = [c.strip().title() for c in df.columns]

        # Detect Programme column
        programme_col = next((c for c in df.columns if "programme" in c.lower()), None)
        if not programme_col:
            st.error("⚠️ Could not detect 'Programme' column.")
            st.stop()

        # Handle names
        if "Fullname" in df.columns or "Name" in df.columns:
            name_col = "Fullname" if "Fullname" in df.columns else "Name"
            df[['Firstname', 'Middlename', 'Lastname']] = df[name_col].str.split(' ', n=2, expand=True)
        elif not {'Firstname', 'Lastname'}.issubset(df.columns):
            st.error("⚠️ File must have either 'Fullname' or 'Firstname' and 'Lastname' columns.")
            st.stop()

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

        # -------------------------
# 📤 CREATE FINAL OUTPUT FORMAT
# -------------------------
        output_df = pd.DataFrame({
    "Username": df["Email"],
    "First name": df["Firstname"],
    "Last name": df["Lastname"],
    "Display name": df["Firstname"] + " " + df["Lastname"],
    "Job title": "Student",
    "Department": df["Department"],
    "Office number": "",
    "Office phone": "",
    "Mobile phone": ["Mobile phone"],
    "Fax": "",
    "Alternate email address": df["Email"],
    "Address": "",
    "City": "Ho",
    "State or province": "Volta",
    "ZIP or postal code": "",
    "Country or region": "Ghana"
})

# -------------------------
# 📥 DOWNLOAD EXCEL
# -------------------------
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

# Footer
# st.markdown("---")
# st.caption("Developed by DELALI • UHAS Email Generator © 2026")
