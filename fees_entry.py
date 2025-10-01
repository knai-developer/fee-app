# [file name]: fees_entry.py
# [file content begin]
# type:ignore
import streamlit as st
from datetime import datetime
from database import generate_student_id, save_to_csv, load_data, load_student_fees, get_student_fee_amount
from utils import format_currency, get_academic_year, check_annual_admission_paid, get_unpaid_months


def fees_entry_page():
    """Fees entry page"""
   
    st.header("➕ Enter Fee Details")
     
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    PAYMENT_METHODS = ["Cash", "Bank Transfer", "Cheque", "Online Payment", "Other"]
    
    # Initialize session state variables if they don't exist
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'available_months' not in st.session_state:
        st.session_state.available_months = []
    if 'current_student_id' not in st.session_state:
        st.session_state.current_student_id = None
    if 'last_saved_records' not in st.session_state:
        st.session_state.last_saved_records = None
    if 'last_student_name' not in st.session_state:
        st.session_state.last_student_name = ""
    if 'last_class_category' not in st.session_state:
        st.session_state.last_class_category = None
    if 'last_class_section' not in st.session_state:
        st.session_state.last_class_section = ""
    if 'current_fee_type' not in st.session_state:
        st.session_state.current_fee_type = "Monthly Fee"
    if 'current_total_amount' not in st.session_state:
        st.session_state.current_total_amount = 0
    if 'previous_fee_type' not in st.session_state:
        st.session_state.previous_fee_type = "Monthly Fee"
    if 'previous_month_selection' not in st.session_state:
        st.session_state.previous_month_selection = "Select a month"
    
    # Create the form
    with st.form(key=f"fee_form_{st.session_state.form_key}", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input(
                "Student Name*", 
                placeholder="Full name", 
                value=st.session_state.last_student_name,
                key=f"student_name_{st.session_state.form_key}"
            )
        with col2:
            class_category = st.selectbox(
                "Class Category*", 
                CLASS_CATEGORIES, 
                index=CLASS_CATEGORIES.index(st.session_state.last_class_category) if st.session_state.last_class_category in CLASS_CATEGORIES else 0,
                key=f"class_category_{st.session_state.form_key}"
            )
            class_section = st.text_input(
                "Class Section", 
                placeholder="A, B, etc. (if applicable)", 
                value=st.session_state.last_class_section,
                key=f"class_section_{st.session_state.form_key}"
            )
        
        # Add a button to update student data
        update_btn = st.form_submit_button("🔍 Check Student Records")
        
        if update_btn:
            update_student_data(student_name, class_category)
            st.rerun()
        
        student_id = st.session_state.current_student_id
        
        # Show student records if student_id is available
        if student_id:
            display_student_records(student_id)
        
        payment_date = st.date_input("Payment Date", value=datetime.now(), 
                                   key=f"payment_date_{st.session_state.form_key}")
        academic_year = get_academic_year(payment_date)
        
        fee_type = st.radio("Select Fee Type*", 
                          ["Monthly Fee", "Annual Charges", "Admission Fee"],
                          horizontal=True,
                          key=f"fee_type_{st.session_state.form_key}")
        
        # Check if fee type changed and update calculation
        current_fee_type = st.session_state.get(f"fee_type_{st.session_state.form_key}", "Monthly Fee")
        if current_fee_type != st.session_state.previous_fee_type:
            update_fee_calculation(student_id, academic_year)
            st.session_state.previous_fee_type = current_fee_type
        
        selected_months = []
        monthly_fee = 0
        annual_charges = 0
        admission_fee = 0
        
        # Load student fees data
        fees_data = load_student_fees()
        
        # Show appropriate fee input based on selected fee type
        if fee_type == "Monthly Fee":
            monthly_fee, selected_months = handle_monthly_fee(
                student_id, fees_data, academic_year
            )
        
        elif fee_type == "Annual Charges":
            annual_charges, selected_months = handle_annual_charges(
                student_id, academic_year, fees_data
            )
        
        elif fee_type == "Admission Fee":
            admission_fee, selected_months = handle_admission_fee(
                student_id, academic_year, fees_data
            )
        
        # Calculate total amount dynamically
        total_amount = calculate_total_amount(fee_type, monthly_fee, annual_charges, admission_fee, selected_months)
        
        # Update session state with current total amount
        st.session_state.current_total_amount = total_amount
        
        col3, col4 = st.columns(2)
        with col3:
            st.text_input(
                "Total Amount",
                value=format_currency(total_amount),
                disabled=True,
                key=f"total_amount_{st.session_state.form_key}"
            )
            
            payment_method = st.selectbox(
                "Payment Method*",
                PAYMENT_METHODS,
                key=f"payment_method_{st.session_state.form_key}"
            )
        with col4:
            # Show received amount as display only (user cannot change)
            st.text_input(
                "Received Amount*",
                value=format_currency(total_amount),
                disabled=True,
                key=f"received_amount_display_{st.session_state.form_key}"
            )
            
            # Hidden field for actual received amount (will use total_amount)
            received_amount = total_amount
            
            signature = st.text_input(
                "Received By (Signature)*",
                placeholder="Your name",
                key=f"signature_{st.session_state.form_key}"
            )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Save Fee Record")
        with col_btn2:
            refresh = st.form_submit_button("🔄 Refresh Form")
        
        if refresh:
            refresh_form()
            st.rerun()
        
        if submitted:
            # Check payment status before submission
            annual_paid, admission_paid = check_annual_admission_paid(student_id, academic_year)
            
            handle_form_submission(
                student_name, class_category, class_section, student_id,
                signature, fee_type, selected_months, monthly_fee,
                annual_charges, admission_fee, received_amount,
                payment_method, payment_date, academic_year,
                annual_paid, admission_paid
            )
 
    # Check for success message and show it
    if 'success_message' in st.session_state and st.session_state.success_message:
        st.success(st.session_state.success_message)
        # Clear the success message
        st.session_state.success_message = None
    
    # Check for balloons and show them
    if 'show_balloons' in st.session_state and st.session_state.show_balloons:
        st.balloons()
        # Clear the balloons flag
        st.session_state.show_balloons = False

def update_fee_calculation(student_id, academic_year):
    """Update fee calculation when fee type changes"""
    current_fee_type = st.session_state.get(f"fee_type_{st.session_state.form_key}", "Monthly Fee")
    st.session_state.current_fee_type = current_fee_type
    
    # Recalculate total amount
    fees_data = load_student_fees()
    
    if current_fee_type == "Monthly Fee":
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        available_months = st.session_state.available_months
        selected_month = st.session_state.get(f"month_select_{st.session_state.form_key}", "Select a month")
        
        if selected_month != "Select a month" and available_months:
            st.session_state.current_total_amount = monthly_fee
        else:
            st.session_state.current_total_amount = 0
    
    elif current_fee_type == "Annual Charges":
        annual_paid, _ = check_annual_admission_paid(student_id, academic_year)
        if not annual_paid:
            st.session_state.current_total_amount = get_student_fee_amount(student_id, "annual")
        else:
            st.session_state.current_total_amount = 0
    
    elif current_fee_type == "Admission Fee":
        _, admission_paid = check_annual_admission_paid(student_id, academic_year)
        if not admission_paid:
            st.session_state.current_total_amount = get_student_fee_amount(student_id, "admission")
        else:
            st.session_state.current_total_amount = 0

def calculate_total_amount(fee_type, monthly_fee, annual_charges, admission_fee, selected_months):
    """Calculate total amount based on fee type and selections"""
    if fee_type == "Monthly Fee":
        return monthly_fee * len(selected_months)
    elif fee_type == "Annual Charges":
        return annual_charges
    elif fee_type == "Admission Fee":
        return admission_fee
    return 0

def update_student_data(student_name, class_category):
    """Update session state with student data when name or class changes"""
    if student_name and class_category:
        student_id = generate_student_id(student_name, class_category)
        st.session_state.current_student_id = student_id
        st.session_state.available_months = get_unpaid_months(student_id)
        
        # Reset fee calculation when student changes
        st.session_state.current_total_amount = 0
        st.session_state.previous_fee_type = "Monthly Fee"
        st.session_state.previous_month_selection = "Select a month"
    else:
        st.session_state.current_student_id = None
        st.session_state.available_months = []
        st.session_state.current_total_amount = 0

def display_student_records(student_id):
    """Display student payment history"""
    st.subheader("📋 Student Payment History")
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if not student_records.empty:
        # Display all records for the student
        display_df = student_records[[
            "Student Name", "Month", "Monthly Fee", "Annual Charges", 
            "Admission Fee", "Received Amount", "Payment Method", "Date", "Academic Year"
        ]].sort_values("Date", ascending=False)
        
        st.dataframe(
            display_df.style.format({
                "Monthly Fee": format_currency,
                "Annual Charges": format_currency,
                "Admission Fee": format_currency,
                "Received Amount": format_currency
            }),
            use_container_width=True
        )
        
        # Calculate totals
        total_monthly = student_records["Monthly Fee"].sum()
        total_annual = student_records["Annual Charges"].sum()
        total_admission = student_records["Admission Fee"].sum()
        total_received = student_records["Received Amount"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Monthly", format_currency(total_monthly))
        col2.metric("Total Annual", format_currency(total_annual))
        col3.metric("Total Admission", format_currency(total_admission))
        col4.metric("Total Received", format_currency(total_received))
        
        # Show payment status
        st.subheader("Payment Status")
        payment_date = st.session_state.get(f"payment_date_{st.session_state.form_key}", datetime.now())
        academic_year = get_academic_year(payment_date)
        
        annual_paid, admission_paid = check_annual_admission_paid(student_id, academic_year)
        unpaid_months = st.session_state.available_months
        
        col_paid, col_unpaid = st.columns(2)
        
        with col_paid:
            st.markdown("#### ✅ Paid Months")
            paid_months = student_records[student_records['Monthly Fee'] > 0]['Month'].unique()
            if len(paid_months) > 0:
                for month in sorted(paid_months):
                    amount = student_records[student_records['Month'] == month]['Monthly Fee'].iloc[0]
                    st.markdown(f"- {month}: {format_currency(amount)}")
            else:
                st.markdown("No months paid yet")
        
        with col_unpaid:
            st.markdown("#### ❌ Unpaid Months")
            if len(unpaid_months) > 0:
                for month in unpaid_months:
                    st.markdown(f"- {month}")
            else:
                st.markdown("All months paid")
        
        st.markdown("---")
        st.markdown(f"**Annual Fees Paid**: {'✅ Yes' if annual_paid else '❌ No'}")
        st.markdown(f"**Admission Fee Paid**: {'✅ Yes' if admission_paid else '❌ No'}")
        
        # Show current fee settings
        st.subheader("💰 Current Fee Settings")
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        annual_fee = get_student_fee_amount(student_id, "annual")
        admission_fee = get_student_fee_amount(student_id, "admission")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly Fee", format_currency(monthly_fee))
        col2.metric("Annual Charges", format_currency(annual_fee))
        col3.metric("Admission Fee", format_currency(admission_fee))
        
    else:
        st.info("No fee records found for this student.")
        unpaid_months = st.session_state.available_months
        
        st.markdown("#### ❌ Unpaid Months")
        if len(unpaid_months) > 0:
            for month in unpaid_months:
                st.markdown(f"- {month}")
        else:
            st.markdown("All months paid")
        
        # Show current fee settings for new students too
        st.subheader("💰 Current Fee Settings")
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        annual_fee = get_student_fee_amount(student_id, "annual")
        admission_fee = get_student_fee_amount(student_id, "admission")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly Fee", format_currency(monthly_fee))
        col2.metric("Annual Charges", format_currency(annual_fee))
        col3.metric("Admission Fee", format_currency(admission_fee))

def handle_monthly_fee(student_id, fees_data, academic_year):
    """Handle monthly fee input with dynamic fees"""
    monthly_fee = 0
    selected_months = []
    
    if not student_id:
        st.warning("Please enter Student Name and select Class Category.")
    elif not st.session_state.available_months:
        st.error("All months have been paid for this student!")
    else:
        # Get monthly fee from database (dynamic)
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        
        st.text_input(
            "Monthly Fee Amount per Month*",
            value=format_currency(monthly_fee),
            disabled=True,
            key=f"monthly_fee_{st.session_state.form_key}"
        )
        
        # Show fee source information
        if student_id in fees_data:
            st.success(f"✅ Admin set monthly fee: {format_currency(monthly_fee)}")
        else:
            st.info(f"ℹ️ Using default monthly fee: {format_currency(monthly_fee)}")
        
        # Month selection as dropdown
        selected_month = st.selectbox(
            "Select Month*",
            ["Select a month"] + st.session_state.available_months,
            key=f"month_select_{st.session_state.form_key}"
        )
        
        # Check if month selection changed and update calculation
        current_month_selection = st.session_state.get(f"month_select_{st.session_state.form_key}", "Select a month")
        if current_month_selection != st.session_state.previous_month_selection:
            if current_month_selection != "Select a month":
                st.session_state.current_total_amount = monthly_fee
            else:
                st.session_state.current_total_amount = 0
            st.session_state.previous_month_selection = current_month_selection
        
        if selected_month != "Select a month":
            selected_months = [selected_month]
            st.markdown(f"**Selected Month**: {selected_month}")
            st.markdown(f"**Amount to Pay**: {format_currency(monthly_fee)}")
        else:
            st.markdown("**Selected Month**: None")
    
    return monthly_fee, selected_months

def handle_annual_charges(student_id, academic_year, fees_data):
    """Handle annual charges input with dynamic fees"""
    annual_charges = 0
    selected_months = []
    
    if student_id:
        annual_paid, _ = check_annual_admission_paid(student_id, academic_year)
        if annual_paid:
            st.error("Annual charges have already been paid for this academic year!")
            st.session_state.current_total_amount = 0
        else:
            selected_months = ["ANNUAL"]
            # Get annual charges from database (dynamic)
            annual_charges = get_student_fee_amount(student_id, "annual")
            
            st.text_input(
                "Annual Charges Amount*",
                value=format_currency(annual_charges),
                disabled=True,
                key=f"annual_charges_{st.session_state.form_key}"
            )
            
            # Show fee source information
            if student_id in fees_data:
                st.success(f"✅ Admin set annual charges: {format_currency(annual_charges)}")
            else:
                st.info(f"ℹ️ Using default annual charges: {format_currency(annual_charges)}")
            
            # Auto-set total amount
            st.session_state.current_total_amount = annual_charges
    else:
        st.warning("Please enter Student Name and select Class Category.")
    
    return annual_charges, selected_months

def handle_admission_fee(student_id, academic_year, fees_data):
    """Handle admission fee input with dynamic fees"""
    admission_fee = 0
    selected_months = []
    
    if student_id:
        _, admission_paid = check_annual_admission_paid(student_id, academic_year)
        if admission_paid:
            st.error("Admission fee has already been paid for this academic year!")
            st.session_state.current_total_amount = 0
        else:
            selected_months = ["ADMISSION"]
            # Get admission fee from database (dynamic)
            admission_fee = get_student_fee_amount(student_id, "admission")
            
            st.text_input(
                "Admission Fee Amount*",
                value=format_currency(admission_fee),
                disabled=True,
                key=f"admission_fee_{st.session_state.form_key}"
            )
            
            # Show fee source information
            if student_id in fees_data:
                st.success(f"✅ Admin set admission fee: {format_currency(admission_fee)}")
            else:
                st.info(f"ℹ️ Using default admission fee: {format_currency(admission_fee)}")
            
            # Auto-set total amount
            st.session_state.current_total_amount = admission_fee
    else:
        st.warning("Please enter Student Name and select Class Category.")
    
    return admission_fee, selected_months

def refresh_form():
    """Refresh the form"""
    st.session_state.form_key += 1
    st.session_state.last_student_name = ""
    st.session_state.last_class_category = None
    st.session_state.last_class_section = ""
    st.session_state.current_student_id = None
    st.session_state.available_months = []
    st.session_state.current_fee_type = "Monthly Fee"
    st.session_state.current_total_amount = 0
    st.session_state.previous_fee_type = "Monthly Fee"
    st.session_state.previous_month_selection = "Select a month"

def handle_form_submission(
    student_name, class_category, class_section, student_id,
    signature, fee_type, selected_months, monthly_fee,
    annual_charges, admission_fee, received_amount,
    payment_method, payment_date, academic_year,
    annual_paid, admission_paid
):
    """Handle form submission"""
    if not student_name or not class_category or not signature:
        st.error("Please fill all required fields (*)")
        return False
    elif not student_id:
        st.error("Please enter Student Name and select Class Category.")
        return False
    elif fee_type == "Monthly Fee" and not selected_months:
        st.error("Please select a month for Monthly Fee payment.")
        return False
    elif fee_type == "Annual Charges" and annual_paid:
        st.error("Annual charges have already been paid for this academic year!")
        return False
    elif fee_type == "Admission Fee" and admission_paid:
        st.error("Admission fee has already been paid for this academic year!")
        return False
    else:
        fee_records = []
        
        # Always use the calculated total amount as received amount
        calculated_received_amount = st.session_state.current_total_amount
        
        if fee_type in ["Annual Charges", "Admission Fee"]:
            fee_data = {
                "ID": student_id,
                "Student Name": student_name,
                "Class Category": class_category,
                "Class Section": class_section,
                "Month": selected_months[0],
                "Monthly Fee": 0,
                "Annual Charges": annual_charges,
                "Admission Fee": admission_fee,
                "Received Amount": calculated_received_amount,  # Use calculated amount
                "Payment Method": payment_method,
                "Date": payment_date.strftime("%Y-%m-%d"),
                "Signature": signature,
                "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Academic Year": academic_year
            }
            fee_records.append(fee_data)
        
        elif fee_type == "Monthly Fee":
            for month in selected_months:
                fee_data = {
                    "ID": student_id,
                    "Student Name": student_name,
                    "Class Category": class_category,
                    "Class Section": class_section,
                    "Month": month,
                    "Monthly Fee": monthly_fee,
                    "Annual Charges": 0,
                    "Admission Fee": 0,
                    "Received Amount": calculated_received_amount,  # Use calculated amount
                    "Payment Method": payment_method,
                    "Date": payment_date.strftime("%Y-%m-%d"),
                    "Signature": signature,
                    "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Academic Year": academic_year
                }
                fee_records.append(fee_data)
        
        if save_to_csv(fee_records):
            # Store the success message in session state to display after rerun
            st.session_state.success_message = "✅ Fee record(s) saved successfully!"
            st.session_state.show_balloons = True
            
            # Update session state
            st.session_state.last_student_name = student_name
            st.session_state.last_class_category = class_category
            st.session_state.last_class_section = class_section or ""
            st.session_state.form_key += 1
            st.session_state.available_months = get_unpaid_months(student_id)
            st.session_state.last_saved_records = fee_records
            st.session_state.current_total_amount = 0
            st.session_state.previous_fee_type = "Monthly Fee"
            st.session_state.previous_month_selection = "Select a month"
            
            # Rerun to refresh the form
            st.rerun()
        else:
            st.error("Failed to save fee records. Please try again.")
            return False
    
    return True
# [file content end]