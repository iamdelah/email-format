import streamlit as st
import pandas as pd
from io import BytesIO

# -------------------------
# EMAIL GENERATION LOGIC
# -------------------------
def generate_email(first, middle, last, dept, year, student_type):
    first_letter = first[0].lower()
    middle_letter = middle[0].lower() if pd.notna(middle) and middle.strip() else ''
    lastname = last.lower().replace(' ', '')

    # Add suffix for Sandwich students
    suffix = ""
    if student_type.lower() == "sandwich":
        suffix = f"{str(year)[-2:]}sw"

    email = f"{first_letter}{middle_letter}{lastname}{suffix}@{dept.lower()}.uhas.edu.gh"
    return email


# -------------------------
# 🔍 DETECT SCHOOL FROM PROGRAMME
# -------------------------
def get_school_from_programme(programme, mapping):
    for school, progs in mapping.items():
        if any(prog.lower() in str(programme).lower() for prog in progs):
            return school
    return "unknown"


# -------------------------
# 🎨 STREAMLIT APP UI
# -------------------------
st.set_page_config(page_title="UHAS Email Generator", page_icon="📧", layout="wide")
st.title("UHAS Student Email Generator")
st.write("Generate institutional emails for **Regular** and **Sandwich** students automatically.")



# -------------------------
# 🎓 MAIN FORM - USER INPUTS
# -------------------------
col1, col2 = st.columns(2)
with col1:
    student_type = st.selectbox("Select Student Type", ["Regular", "Sandwich"])
with col2:
    admission_year = st.selectbox("Select Admission Year", [2024, 2025])

uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "csv"])

# -------------------------
# 🧩 PROCESS UPLOADED FILE
# -------------------------
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
            st.error("⚠️ Could not detect 'Programme' column in your file.")
            st.stop()

        # Handle names
        if "Fullname" in df.columns or "Name" in df.columns:
            name_col = "Fullname" if "Fullname" in df.columns else "Name"
            df[['Firstname', 'Middlename', 'Lastname']] = df[name_col].str.split(' ', n=2, expand=True)
        elif not {'Firstname', 'Lastname'}.issubset(df.columns):
            st.error("⚠️ File must have either 'Fullname' or 'Firstname' and 'Lastname' columns.")
            st.stop()

        # Determine department (school)
        df["Department"] = df[programme_col].apply(lambda x: get_school_from_programme(x, st.session_state.school_mapping))

        # Generate emails
        df["Email"] = df.apply(lambda row: generate_email(
            str(row["Firstname"]),
            str(row["Middlename"]) if pd.notna(row["Middlename"]) else "",
            str(row["Lastname"]),
            str(row["Department"]),
            admission_year,
            student_type
        ), axis=1)

        # Show result
        st.success("✅ Emails generated successfully!")
        st.dataframe(df[["Firstname", "Middlename", "Lastname", "Department", "Email"]].head())

        # Export to Excel
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Download Excel with Emails",
            data=output,
            file_name=f"UHAS_{student_type}_{admission_year}_emails.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")

# -------------------------
# 📜 FOOTER
# -------------------------
#st.markdown("---")
#st.caption("Developed by SEMABIA DELALI • UHAS Email Generator Pro © 2025")
