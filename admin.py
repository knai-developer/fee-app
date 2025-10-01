# [file name]: admin.py
# [file content begin]
#type:ignore
import streamlit as st
import json
import pandas as pd
from auth import create_user, format_trial_remaining
from database import load_student_fees, save_student_fees, generate_student_id, check_fee_setting_exists, get_all_students_with_fees

def admin_page(selected_menu):
    """Admin functions page"""
    if selected_menu == "User Management":
        user_management()
    elif selected_menu == "Set Student Fees":
        set_student_fees()

def user_management():
    """Admin interface for user management"""
    st.header("👥 User Management")
    
    with st.expander("➕ Create New User"):
        with st.form("create_user_form"):
            new_username = st.text_input("New Username*")
            new_email = st.text_input("Gmail Address*", placeholder="yourname@gmail.com", help="Only Gmail addresses are allowed.")
            new_password = st.text_input("New Password*", type="password", key="new_pass")
            confirm_password = st.text_input("Confirm Password*", type="password", key="confirm_pass")
            is_admin = st.checkbox("Admin User")
            show_password = st.checkbox("Show Password")
            
            if show_password:
                st.text(f"Password will be: {new_password if new_password else '[not set]'}")
            
            submit = st.form_submit_button("Create User")
            
            if submit:
                if not new_username or not new_password or not new_email:
                    st.error("Username, password, and Gmail address are required!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, message = create_user(new_username, new_password, new_email, is_admin)
                    if success:
                        st.success(message)
                        st.info(f"User '{new_username}' created with email: {new_email}, Trial: 1-month trial started")
                    else:
                        st.error(message)

    with st.expander("👀 View All Users"):
        try:
            with open("users.json", 'r') as f:
                users = json.load(f)
                
            user_data = []
            for username, details in users.items():
                trial_remaining = "N/A"
                if details.get('trial_end'):
                    from datetime import datetime
                    trial_end = datetime.strptime(details['trial_end'], "%Y-%m-%d %H:%M:%S")
                    remaining = trial_end - datetime.now()
                    trial_remaining = format_trial_remaining(remaining) if remaining.total_seconds() > 0 else "Expired"
                
                user_data.append({
                    "Username": username,
                    "Email": details.get('email', 'N/A'),
                    "Admin": "Yes" if details.get('is_admin', False) else "No",
                    "Created At": details.get('created_at', "Unknown"),
                    "Trial Remaining": trial_remaining
                })
            
            user_df = pd.DataFrame(user_data)
            st.dataframe(user_df)
            
            st.subheader("Delete User")
            if not user_df.empty:
                user_to_delete = st.selectbox(
                    "Select User to Delete",
                    user_df['Username'].tolist(),
                    key="delete_user_select"
                )
                
                if st.button("🗑️ Delete User", key="delete_user_btn"):
                    if user_to_delete == st.session_state.current_user:
                        st.error("You cannot delete your own account!")
                    else:
                        try:
                            with open("users.json", 'r') as f:
                                users = json.load(f)
                            
                            if user_to_delete in users:
                                del users[user_to_delete]
                                
                                with open("users.json", 'w') as f:
                                    json.dump(users, f)
                                
                                st.success(f"User '{user_to_delete}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error("User not found!")
                        except Exception as e:
                            st.error(f"Error deleting user: {str(e)}")

        except Exception as e:
            st.error(f"Error loading users: {str(e)}")

    with st.expander("🔑 Reset Password"):
        try:
            with open("users.json", 'r') as f:
                users = json.load(f)
            
            users_list = list(users.keys())
            selected_user = st.selectbox("Select User", users_list, key="reset_user_select")
            
            with st.form("reset_password_form"):
                new_password = st.text_input("New Password*", type="password", key="reset_pass")
                confirm_password = st.text_input("Confirm Password*", type="password", key="reset_confirm")
                show_password = st.checkbox("Show New Password")
                
                if show_password:
                    st.text(f"New password will be: {new_password if new_password else '[not set]'}")
                
                reset_btn = st.form_submit_button("Reset Password")
                
                if reset_btn:
                    if not new_password:
                        st.error("Password cannot be empty!")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        from auth import hash_password
                        users[selected_user]['password'] = hash_password(new_password)
                        with open("users.json", 'w') as f:
                            json.dump(users, f)
                        st.success(f"Password for {selected_user} reset successfully!")
                        st.info(f"New password: {new_password}")
        except Exception as e:
            st.error(f"Error resetting password: {str(e)}")

def set_student_fees():
    """Admin interface to set fees for individual students"""
    st.header("💸 Set Student Fees")
    
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    with st.expander("➕ Set Fees for a Student"):
        with st.form("set_fees_form"):
            col1, col2 = st.columns(2)
            with col1:
                student_name = st.text_input("Student Name*", placeholder="Full name")
            with col2:
                class_category = st.selectbox("Class Category*", CLASS_CATEGORIES)
            
            # Dynamic fee inputs
            monthly_fee = st.number_input("Monthly Fee*", min_value=0, value=2000, step=100,
                                         help="This amount will be shown when entering monthly fees")
            annual_charges = st.number_input("Annual Charges*", min_value=0, value=2000, step=100,
                                           help="This amount will be shown when entering annual charges")
            admission_fee = st.number_input("Admission Fee*", min_value=0, value=1000, step=100,
                                          help="This amount will be shown when entering admission fee")
            
            submit = st.form_submit_button("💾 Save Fee Settings")
            
            if submit:
                if not student_name or not class_category:
                    st.error("Please fill all required fields (*)")
                else:
                    student_id = generate_student_id(student_name, class_category)
                    fees_data = load_student_fees()
                    
                    # Check if fee setting already exists
                    fee_exists = check_fee_setting_exists(student_name, class_category)
                    
                    fees_data[student_id] = {
                        "student_name": student_name,
                        "class_category": class_category,
                        "monthly_fee": monthly_fee,
                        "annual_charges": annual_charges,
                        "admission_fee": admission_fee,
                        "updated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    if save_student_fees(fees_data):
                        if fee_exists:
                            st.success(f"✅ Fee settings updated for {student_name} ({class_category})")
                        else:
                            st.success(f"✅ Fee settings saved for {student_name} ({class_category})")
                        st.info(f"""
                        **Fee Summary:**
                        - Monthly Fee: Rs. {monthly_fee:,}
                        - Annual Charges: Rs. {annual_charges:,}
                        - Admission Fee: Rs. {admission_fee:,}
                        """)
                        st.rerun()
                    else:
                        st.error("❌ Failed to save fee settings")

    with st.expander("👀 View All Student Fees"):
        fees_data = load_student_fees()
        if not fees_data:
            st.info("No student fees settings found")
        else:
            from utils import format_currency
            fee_records = [
                {
                    "Student ID": student_id,
                    "Student Name": details["student_name"],
                    "Class": details["class_category"],
                    "Monthly Fee": format_currency(details["monthly_fee"]),
                    "Annual Charges": format_currency(details["annual_charges"]),
                    "Admission Fee": format_currency(details["admission_fee"]),
                    "Updated At": details["updated_at"]
                }
                for student_id, details in fees_data.items()
            ]
            fee_df = pd.DataFrame(fee_records)
            st.dataframe(fee_df, use_container_width=True)
            
            # Download option
            csv = fee_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Student Fees as CSV",
                data=csv,
                file_name="student_fees.csv",
                mime="text/csv"
            )
            
            st.subheader("Edit/Delete Fee Settings")
            if not fee_df.empty:
                student_to_edit = st.selectbox(
                    "Select Student to Edit/Delete",
                    fee_df["Student ID"].tolist(),
                    format_func=lambda x: f"{fees_data[x]['student_name']} - {fees_data[x]['class_category']}",
                    key="edit_fee_select"
                )
                
                with st.form("edit_fees_form"):
                    student_details = fees_data[student_to_edit]
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Student Name*", value=student_details["student_name"])
                    with col2:
                        edit_class = st.selectbox("Class Category*", CLASS_CATEGORIES, 
                                                 index=CLASS_CATEGORIES.index(student_details["class_category"]))
                    
                    edit_monthly_fee = st.number_input("Monthly Fee*", min_value=0, 
                                                      value=int(student_details["monthly_fee"]), step=100)
                    edit_annual_charges = st.number_input("Annual Charges*", min_value=0, 
                                                         value=int(student_details["annual_charges"]), step=100)
                    edit_admission_fee = st.number_input("Admission Fee*", min_value=0, 
                                                        value=int(student_details["admission_fee"]), step=100)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_btn = st.form_submit_button("🔄 Update Fees")
                    with col2:
                        delete_btn = st.form_submit_button("🗑️ Delete Fees")
                    
                    if update_btn:
                        if not edit_name or not edit_class:
                            st.error("Please fill all required fields (*)")
                        else:
                            new_student_id = generate_student_id(edit_name, edit_class)
                            fees_data = load_student_fees()
                            
                            if new_student_id != student_to_edit:
                                fees_data.pop(student_to_edit, None)
                            
                            fees_data[new_student_id] = {
                                "student_name": edit_name,
                                "class_category": edit_class,
                                "monthly_fee": edit_monthly_fee,
                                "annual_charges": edit_annual_charges,
                                "admission_fee": edit_admission_fee,
                                "updated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            if save_student_fees(fees_data):
                                st.success(f"✅ Fee settings updated for {edit_name} ({edit_class})")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update fee settings")
                    
                    if delete_btn:
                        fees_data = load_student_fees()
                        if student_to_edit in fees_data:
                            del fees_data[student_to_edit]
                            if save_student_fees(fees_data):
                                st.success("✅ Fee settings deleted successfully")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete fee settings")
# [file content end]