# #type:ignore
# import pandas as pd
# import numpy as np
# import json
# import os
# from datetime import datetime
# from hashlib import md5

# def initialize_files():
#     """Initialize all required files"""
#     initialize_csv()
#     initialize_user_db()
#     initialize_student_fees()

# def initialize_user_db():
#     """Initialize the user database if it doesn't exist"""
#     if not os.path.exists("users.json"):
#         with open("users.json", 'w') as f:
#             json.dump({}, f)

# def initialize_student_fees():
#     """Initialize the student fees JSON file if it doesn't exist"""
#     if not os.path.exists("student_fees.json"):
#         with open("student_fees.json", 'w') as f:
#             json.dump({}, f)

# def initialize_csv():
#     """Initialize the CSV file with proper columns if it doesn't exist"""
#     if not os.path.exists("fees_data.csv"):
#         columns = [
#             "ID", "Student Name", "Class Category", "Class Section", "Month", 
#             "Monthly Fee", "Annual Charges", "Admission Fee", 
#             "Received Amount", "Payment Method", "Date", "Signature", 
#             "Entry Timestamp", "Academic Year"
#         ]
#         pd.DataFrame(columns=columns).to_csv("fees_data.csv", index=False)

# def generate_student_id(student_name, class_category):
#     """Generate a unique 8-character ID based on student name and class"""
#     unique_str = f"{student_name}_{class_category}".encode('utf-8')
#     return md5(unique_str).hexdigest()[:8].upper()

# def save_to_csv(data):
#     """Save data to CSV with proper validation"""
#     try:
#         if os.path.exists("fees_data.csv"):
#             df = pd.read_csv("fees_data.csv")
#         else:
#             df = pd.DataFrame(columns=data[0].keys())
        
#         new_df = pd.DataFrame(data)
#         df = pd.concat([df, new_df], ignore_index=True)
        
#         df.to_csv("fees_data.csv", index=False)
#         return True
#     except Exception as e:
#         st.error(f"Error saving data: {str(e)}")
#         return False

# def load_data():
#     """Load data from CSV with robust error handling"""
#     if not os.path.exists("fees_data.csv"):
#         return pd.DataFrame()
    
#     try:
#         df = pd.read_csv("fees_data.csv")
        
#         expected_columns = [
#             "ID", "Student Name", "Class Category", "Class Section", "Month", 
#             "Monthly Fee", "Annual Charges", "Admission Fee", 
#             "Received Amount", "Payment Method", "Date", "Signature", 
#             "Entry Timestamp", "Academic Year"
#         ]
        
#         for col in expected_columns:
#             if col not in df.columns:
#                 df[col] = np.nan
        
#         try:
#             df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')
#         except:
#             pass
        
#         try:
#             df['Entry Timestamp'] = pd.to_datetime(df['Entry Timestamp']).dt.strftime('%d-%m-%Y %H:%M')
#         except:
#             pass
        
#         return df.dropna(how='all')
    
#     except Exception as e:
#         st.error(f"Error loading data: {str(e)}")
#         return pd.DataFrame()

# def update_data(updated_df):
#     """Update the CSV file with the modified DataFrame"""
#     try:
#         updated_df.to_csv("fees_data.csv", index=False)
#         return True
#     except Exception as e:
#         st.error(f"Error updating data: {str(e)}")
#         return False

# def load_student_fees():
#     """Load student-specific fees from JSON file"""
#     try:
#         if os.path.exists("student_fees.json"):
#             with open("student_fees.json", 'r') as f:
#                 return json.load(f)
#         return {}
#     except Exception as e:
#         st.error(f"Error loading student fees: {str(e)}")
#         return {}

# def save_student_fees(fees_data):
#     """Save student-specific fees to JSON file"""
#     try:
#         with open("student_fees.json", 'w') as f:
#             json.dump(fees_data, f, indent=4)
#         return True
#     except Exception as e:
#         st.error(f"Error saving student fees: {str(e)}")
#         return False



# [file name]: database.py
# [file content begin]
#type:ignore
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from hashlib import md5
import streamlit as st

def initialize_files():
    """Initialize all required files"""
    initialize_csv()
    initialize_user_db()
    initialize_student_fees()

def initialize_user_db():
    """Initialize the user database if it doesn't exist"""
    if not os.path.exists("users.json"):
        with open("users.json", 'w') as f:
            json.dump({}, f)

def initialize_student_fees():
    """Initialize the student fees JSON file if it doesn't exist"""
    if not os.path.exists("student_fees.json"):
        with open("student_fees.json", 'w') as f:
            json.dump({}, f)

def initialize_csv():
    """Initialize the CSV file with proper columns if it doesn't exist"""
    if not os.path.exists("fees_data.csv"):
        columns = [
            "ID", "Student Name", "Class Category", "Class Section", "Month", 
            "Monthly Fee", "Annual Charges", "Admission Fee", 
            "Received Amount", "Payment Method", "Date", "Signature", 
            "Entry Timestamp", "Academic Year"
        ]
        pd.DataFrame(columns=columns).to_csv("fees_data.csv", index=False)

def generate_student_id(student_name, class_category):
    """Generate a unique 8-character ID based on student name and class"""
    unique_str = f"{student_name}_{class_category}".encode('utf-8')
    return md5(unique_str).hexdigest()[:8].upper()

def save_to_csv(data):
    """Save data to CSV with proper validation"""
    try:
        if os.path.exists("fees_data.csv"):
            df = pd.read_csv("fees_data.csv")
        else:
            df = pd.DataFrame(columns=data[0].keys())
        
        new_df = pd.DataFrame(data)
        df = pd.concat([df, new_df], ignore_index=True)
        
        df.to_csv("fees_data.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def load_data():
    """Load data from CSV with robust error handling"""
    if not os.path.exists("fees_data.csv"):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv("fees_data.csv")
        
        expected_columns = [
            "ID", "Student Name", "Class Category", "Class Section", "Month", 
            "Monthly Fee", "Annual Charges", "Admission Fee", 
            "Received Amount", "Payment Method", "Date", "Signature", 
            "Entry Timestamp", "Academic Year"
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = np.nan
        
        try:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')
        except:
            pass
        
        try:
            df['Entry Timestamp'] = pd.to_datetime(df['Entry Timestamp']).dt.strftime('%d-%m-%Y %H:%M')
        except:
            pass
        
        return df.dropna(how='all')
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def update_data(updated_df):
    """Update the CSV file with the modified DataFrame"""
    try:
        updated_df.to_csv("fees_data.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")
        return False

def load_student_fees():
    """Load student-specific fees from JSON file"""
    try:
        if os.path.exists("student_fees.json"):
            with open("student_fees.json", 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading student fees: {str(e)}")
        return {}

def save_student_fees(fees_data):
    """Save student-specific fees to JSON file"""
    try:
        with open("student_fees.json", 'w') as f:
            json.dump(fees_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving student fees: {str(e)}")
        return False

def get_student_fee_amount(student_id, fee_type):
    """Get specific fee amount for a student - dynamic fees system"""
    fees_data = load_student_fees()
    
    if student_id in fees_data:
        fee_mapping = {
            "monthly": "monthly_fee",
            "annual": "annual_charges", 
            "admission": "admission_fee"
        }
        
        if fee_type in fee_mapping:
            fee_key = fee_mapping[fee_type]
            return fees_data[student_id].get(fee_key, 0)
    
    # Default fees if not set by admin
    default_fees = {
        "monthly": 2000,
        "annual": 2000,
        "admission": 1000
    }
    return default_fees.get(fee_type, 0)

def get_student_fee_details(student_id):
    """Get all fee details for a student"""
    fees_data = load_student_fees()
    
    if student_id in fees_data:
        return fees_data[student_id]
    
    # Return default fees if not set
    return {
        "monthly_fee": 2000,
        "annual_charges": 2000,
        "admission_fee": 1000,
        "student_name": "Not Set",
        "class_category": "Not Set"
    }

def check_fee_setting_exists(student_name, class_category):
    """Check if fee setting already exists for a student"""
    student_id = generate_student_id(student_name, class_category)
    fees_data = load_student_fees()
    return student_id in fees_data

def get_all_students_with_fees():
    """Get all students who have custom fee settings"""
    fees_data = load_student_fees()
    return fees_data
# [file content end]