import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="HR Analytics Dashboard", page_icon="👥", layout="wide")
st.title("👥 HR Analytics Dashboard")
st.caption("Explore employee headcount, departments, salaries, tenure, and attrition.")

uploaded = st.file_uploader("Upload HR CSV (optional)", type=["csv"])
default_path = "hr_data.csv"

try:
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_csv(default_path)
except FileNotFoundError:
    st.error("hr_data.csv was not found. Upload a CSV file to continue.")
    st.stop()

df.columns = df.columns.astype(str).str.strip()
required = ["EmployeeID", "Name", "Gender", "Age", "Department", "JobTitle", "City", "MonthlySalaryPKR", "YearsAtCompany", "Status"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

df["MonthlySalaryPKR"] = pd.to_numeric(df["MonthlySalaryPKR"], errors="coerce")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["YearsAtCompany"] = pd.to_numeric(df["YearsAtCompany"], errors="coerce")

with st.sidebar:
    st.header("Filters")
    departments = st.multiselect("Department", sorted(df["Department"].dropna().unique()), default=sorted(df["Department"].dropna().unique()))
    statuses = st.multiselect("Employee status", sorted(df["Status"].dropna().unique()), default=sorted(df["Status"].dropna().unique()))
    genders = st.multiselect("Gender", sorted(df["Gender"].dropna().unique()), default=sorted(df["Gender"].dropna().unique()))

filtered = df[
    df["Department"].isin(departments) &
    df["Status"].isin(statuses) &
    df["Gender"].isin(genders)
].copy()

if filtered.empty:
    st.warning("No employees match these filters.")
    st.stop()

headcount = len(filtered)
active_count = int((filtered["Status"].str.lower() == "active").sum())
resigned_count = int((filtered["Status"].str.lower() == "resigned").sum())
avg_salary = filtered["MonthlySalaryPKR"].mean()
avg_age = filtered["Age"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Employees", f"{headcount:,}")
c2.metric("Active Employees", f"{active_count:,}")
c3.metric("Average Monthly Salary", f"PKR {avg_salary:,.0f}" if pd.notna(avg_salary) else "N/A")
c4.metric("Average Age", f"{avg_age:.1f}" if pd.notna(avg_age) else "N/A")

left, right = st.columns(2)
with left:
    dept = filtered.groupby("Department", as_index=False).size().rename(columns={"size":"Employees"})
    st.plotly_chart(px.bar(dept, x="Department", y="Employees", title="Employees by Department", text_auto=True), use_container_width=True)
with right:
    gender = filtered.groupby("Gender", as_index=False).size().rename(columns={"size":"Employees"})
    st.plotly_chart(px.pie(gender, names="Gender", values="Employees", hole=0.45, title="Gender Distribution"), use_container_width=True)

left, right = st.columns(2)
with left:
    salary = filtered.groupby("Department", as_index=False)["MonthlySalaryPKR"].mean()
    st.plotly_chart(px.bar(salary, x="Department", y="MonthlySalaryPKR", title="Average Salary by Department", labels={"MonthlySalaryPKR":"Average monthly salary (PKR)"}), use_container_width=True)
with right:
    status = filtered.groupby("Status", as_index=False).size().rename(columns={"size":"Employees"})
    st.plotly_chart(px.bar(status, x="Status", y="Employees", title="Employee Status"), use_container_width=True)

st.subheader("Employee details")
st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button("Download filtered employee data", filtered.to_csv(index=False).encode("utf-8"), "filtered_hr_data.csv", "text/csv")
st.caption("This package uses fictional sample employee data. Replace it with authorized data before using it for real reporting.")
