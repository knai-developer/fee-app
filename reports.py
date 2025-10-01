# [file name]: reports.py
# [file content begin]
#type:ignore
import streamlit as st
import pandas as pd
from database import load_data
from utils import format_currency, style_row

def reports_page(selected_menu):
    """Reports page for viewing records"""
    if selected_menu == "View All Records":
        view_all_records()
    elif selected_menu == "Paid & Unpaid Students Record":
        paid_unpaid_records()
    elif selected_menu == "Student Yearly Report":
        student_yearly_report()

def view_all_records():
    """View all fee records"""
    st.header("👀 View All Fee Records")
    
    df = load_data()
    if df.empty:
        st.info("No fee records found")
    else:
        CLASS_CATEGORIES = [
            "Nursery", "KGI", "KGII", 
            "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
            "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
        ]
        
        tabs = st.tabs(["All Records"] + CLASS_CATEGORIES)
        
        with tabs[0]:
            st.subheader("All Fee Records")
            
            st.markdown("## Select a record to edit or delete:")
            
            edit_index = st.selectbox(
                "Select Record",
                options=df.index,
                format_func=lambda x: f"{df.loc[x, 'Student Name']} - {df.loc[x, 'Class Category']} - {df.loc[x, 'Month']}"
            )
            
            with st.form("edit_form"):
                record = df.loc[edit_index]
                
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input("Student Name", value=record['Student Name'])
                    edit_class = st.selectbox("Class Category", CLASS_CATEGORIES, 
                                            index=CLASS_CATEGORIES.index(record['Class Category']))
                    edit_section = st.text_input("Class Section", value=record['Class Section'])
                    edit_month = st.selectbox("Month", [
                        "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                        "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH",
                        "ANNUAL", "ADMISSION"
                    ], index=[
                        "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                        "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH",
                        "ANNUAL", "ADMISSION"
                    ].index(record['Month']))
                with col2:
                    edit_monthly_fee = st.number_input("Monthly Fee", value=float(record['Monthly Fee'] or 0))
                    edit_annual_charges = st.number_input("Annual Charges", value=float(record['Annual Charges'] or 0))
                    edit_admission_fee = st.number_input("Admission Fee", value=float(record['Admission Fee'] or 0))
                    edit_received = st.number_input("Received Amount", value=float(record['Received Amount'] or 0))
                    edit_payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Cheque", "Online Payment", "Other"], 
                                                     index=["Cash", "Bank Transfer", "Cheque", "Online Payment", "Other"].index(record['Payment Method'] if pd.notna(record['Payment Method']) else "Cash"))
                
                try:
                    edit_date_value = pd.to_datetime(record['Date'])
                except:
                    edit_date_value = pd.to_datetime('today')
                
                edit_date = st.date_input("Payment Date", value=edit_date_value)
                edit_signature = st.text_input("Received By (Signature)", value=record['Signature'])
                edit_academic_year = st.text_input("Academic Year", 
                                                 value=record['Academic Year'] if pd.notna(record['Academic Year']) else f"{edit_date.year}-{edit_date.year+1}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    update_btn = st.form_submit_button("🔄 Update Record")
                with col2:
                    delete_btn = st.form_submit_button("🗑️ Delete Record")
                
                if update_btn:
                    from database import update_data
                    df.loc[edit_index, 'Student Name'] = edit_name
                    df.loc[edit_index, 'Class Category'] = edit_class
                    df.loc[edit_index, 'Class Section'] = edit_section
                    df.loc[edit_index, 'Month'] = edit_month
                    df.loc[edit_index, 'Monthly Fee'] = edit_monthly_fee
                    df.loc[edit_index, 'Annual Charges'] = edit_annual_charges
                    df.loc[edit_index, 'Admission Fee'] = edit_admission_fee
                    df.loc[edit_index, 'Received Amount'] = edit_received
                    df.loc[edit_index, 'Payment Method'] = edit_payment_method
                    df.loc[edit_index, 'Date'] = edit_date.strftime('%d-%m-%Y')
                    df.loc[edit_index, 'Signature'] = edit_signature
                    df.loc[edit_index, 'Academic Year'] = edit_academic_year
                    df.loc[edit_index, 'Entry Timestamp'] = pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')
                    
                    if update_data(df):
                        st.success("✅ Record updated successfully!")
                        st.rerun()
                
                if delete_btn:
                    from database import update_data
                    df = df.drop(index=edit_index)
                    if update_data(df):
                        st.success("✅ Record deleted successfully!")
                        st.rerun()
        
            st.dataframe(
                df.style.apply(style_row, axis=1).format({
                    'Monthly Fee': format_currency,
                    'Annual Charges': format_currency,
                    'Admission Fee': format_currency,
                    'Received Amount': format_currency
                }),
                use_container_width=True
            )
        
        for i, category in enumerate(CLASS_CATEGORIES, start=1):
            with tabs[i]:
                st.subheader(f"{category} Records")
                class_df = df[df["Class Category"] == category]
                
                if not class_df.empty:
                    st.dataframe(
                        class_df.style.apply(style_row, axis=1).format({
                            'Monthly Fee': format_currency,
                            'Annual Charges': format_currency,
                            'Admission Fee': format_currency,
                            'Received Amount': format_currency
                        }),
                        use_container_width=True
                    )
                    
                    st.subheader("Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Students", class_df['Student Name'].nunique())
                    with col2:
                        st.metric("Total Received", format_currency(class_df['Received Amount'].sum()))
                    with col3:
                        unpaid = class_df[class_df['Monthly Fee'] == 0]['Student Name'].nunique()
                        st.metric("Unpaid Students", unpaid, delta_color="inverse")
                    
                    st.markdown("Monthly Collection:")
                    monthly_summary = class_df.groupby('Month')['Received Amount'].sum().reset_index()
                    st.bar_chart(monthly_summary.set_index('Month'))
        
        st.divider()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All Records as CSV",
            data=csv,
            file_name="all_fee_records.csv",
            mime="text/csv"
        )

def paid_unpaid_records():
    """Paid and unpaid students records"""
    st.header("✅ Paid & ❌ Unpaid Students Record")
    df = load_data()
    
    if df.empty:
        st.info("No fee records found")
    else:
        all_students = df[['ID', 'Student Name', 'Class Category']].drop_duplicates()
        
        MONTHS = [
            "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
            "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"
        ]
        
        all_combinations = pd.DataFrame([
            (student['ID'], student['Student Name'], student['Class Category'], month)
            for _, student in all_students.iterrows()
            for month in MONTHS
        ], columns=['ID', "Student Name", "Class Category", "Month"])
        
        payment_records = df[["ID", "Month", "Monthly Fee", "Received Amount"]]
        merged = pd.merge(all_combinations, payment_records, on=["ID", "Month"], how="left")
        
        from database import load_student_fees
        fees_data = load_student_fees()
        
        def get_student_fee(student_id):
            if student_id in fees_data:
                return fees_data[student_id]["monthly_fee"]
            student_payments = df[(df['ID'] == student_id) & (df['Monthly Fee'] > 0)]
            if not student_payments.empty:
                return student_payments['Monthly Fee'].iloc[-1]
            return 2000
            
        merged['Estimated Monthly Fee'] = merged['ID'].apply(get_student_fee)
            
        merged['Status'] = merged['Monthly Fee'].apply(
            lambda x: "Paid" if pd.notna(x) and x > 0 else "Unpaid"
        )
        merged['Outstanding'] = merged.apply(
            lambda row: 0 if row['Status'] == "Paid" else row['Estimated Monthly Fee'],
            axis=1
        )
            
        tabs = st.tabs(MONTHS)
            
        for i, month in enumerate(MONTHS):
            with tabs[i]:
                month_data = merged[merged['Month'] == month].copy()
                    
                if not month_data.empty:
                    total_students = len(month_data)
                    paid_students = len(month_data[month_data["Status"] == "Paid"])
                    unpaid_students = total_students - paid_students
                    total_outstanding = month_data[month_data["Status"] == "Unpaid"]["Outstanding"].sum()
                        
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Students", total_students)
                    with col2:
                        st.metric("Paid Students", paid_students)
                    with col3:
                        st.metric("Unpaid Students", unpaid_students, 
                                delta=f"Rs. {int(total_outstanding):,}" if total_outstanding > 0 else "Rs. 0")
                        
                    def color_status(val):
                        color = "green" if val == "Paid" else "red"
                        return f"color: {color}"
                        
                    display_df = month_data[[
                        "Student Name", "Class Category", "Estimated Monthly Fee", 
                        "Received Amount", "Outstanding", "Status"
                    ]]
                    display_df = display_df.rename(columns={
                        "Estimated Monthly Fee": "Monthly Fee",
                        "Received Amount": "Amount Paid",
                        "Outstanding": "Balance Due"
                    })
                        
                    st.dataframe(
                        display_df.style.format({
                            "Monthly Fee": format_currency,
                            "Amount Paid": format_currency,
                            "Balance Due": format_currency
                        }).applymap(color_status, subset=["Status"]),
                        use_container_width=True
                    )
                            
                    csv = display_df.to_csv(index=False).encode("utf-8")
                                                    
                st.subheader("Overall Payment Status")
                student_summary = merged.groupby(["ID", "Student Name", "Class Category"]).agg({
                    "Status": lambda x: (x == "Unpaid").sum(),
                    "Outstanding": "sum"
                }).reset_index()
                student_summary.columns = [
                    "ID", "Student Name", "Class Category", "Unpaid Months", "Total Outstanding"
                ]
        
                st.dataframe(
                    student_summary.style.format({
                        "Total Outstanding": format_currency
                    }),
                    use_container_width=True
                )
                        
                csv = student_summary.to_csv(index=False).encode("utf-8")

def student_yearly_report():
    """Student yearly report"""
    st.header("📊 Student Yearly Fee Report")
    
    df = load_data()
    if df.empty:
        st.info("No fee records found")
    else:
        all_classes = sorted(df["Class Category"].unique())
        selected_class = st.selectbox("Select Class", all_classes, key="class_selector")
        
        class_students = sorted(df[df["Class Category"] == selected_class]["Student Name"].unique())
        
        if not class_students:
            st.warning(f"No students found in {selected_class}")
        else:
            selected_student = st.selectbox("Select Student", class_students, key="student_selector")
            
            student_data = df[(df["Student Name"] == selected_student) & 
                            (df["Class Category"] == selected_class)]
            
            if student_data.empty:
                st.warning(f"No records found for {selected_student} in {selected_class}")
            else:
                st.subheader(f"Yearly Report for {selected_student}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Class**: {selected_class}")
                with col2:
                    section = student_data.iloc[0]["Class Section"] if "Class Section" in student_data.columns else "N/A"
                    st.markdown(f"**Section**: {section if pd.notna(section) else 'N/A'}")
                
                st.subheader("Fee Summary")
                
                total_monthly_fee = student_data["Monthly Fee"].sum()
                annual_charges = student_data["Annual Charges"].sum()
                admission_fee = student_data["Admission Fee"].sum()
                total_received = student_data["Received Amount"].sum()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Monthly Fee", format_currency(total_monthly_fee))
                with col2:
                    st.metric("Annual Charges", format_currency(annual_charges))
                with col3:
                    st.metric("Admission Fee", format_currency(admission_fee))
                with col4:
                    st.metric("Total Received", format_currency(total_received))
                
                st.subheader("Monthly Fee Details")
                
                all_months = [
                    "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                    "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"
                ]
                
                monthly_report = pd.DataFrame({"Month": all_months})
                monthly_data = student_data.groupby("Month").agg({
                    "Monthly Fee": "sum",
                    "Received Amount": "sum"
                }).reset_index()
                
                monthly_report = monthly_report.merge(monthly_data, on="Month", how="left").fillna(0)
                monthly_report["Status"] = monthly_report.apply(
                    lambda row: "Paid" if row["Monthly Fee"] > 0 else "Unpaid",
                    axis=1
                )
                
                def color_unpaid(val):
                    if val == "Unpaid":
                        return "color: red"
                    return ""
                
                st.dataframe(
                    monthly_report.style
                    .applymap(color_unpaid, subset=["Status"])
                    .format({
                        "Monthly Fee": format_currency,
                        "Received Amount": format_currency
                    }),
                    use_container_width=True
                )
                
                st.subheader("Payment Trends")
                st.line_chart(monthly_report.set_index("Month")[["Monthly Fee", "Received Amount"]])
                
                st.divider()
                csv = monthly_report.to_csv(index=False).encode("utf-8")
# [file content end]