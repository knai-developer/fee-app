# [file name]: main.py
# [file content begin]
##uv run streamlit run main.py
#type:ignore
import streamlit as st
from auth import check_authentication, logout, login_page
from home import home_page
from fees_entry import fees_entry_page
from reports import reports_page
from admin import admin_page
from utils import hide_streamlit_elements, navbar_component, navbar_collapsible_component
from database import initialize_files

def main():
    # Initialize files and hide elements
    initialize_files()
    hide_streamlit_elements()
    
    # Initialize session state if it doesn't exist
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication status
    is_authenticated = check_authentication()
    
    # If not authenticated, show home page or login page
    if not is_authenticated:
        if st.session_state.show_login:
            login_page()
        else:
            home_page()
        return
    
    # If authenticated, show main app with navbar
    st.set_page_config(page_title="School Fees Management", layout="wide")
    
    # Define navigation options based on user role
    if st.session_state.is_admin:
        menu_options = [
            "Enter Fees", "View All Records", "Paid & Unpaid Students Record", 
            "Student Yearly Report", "User Management", "Set Student Fees"
        ]
    else:
        menu_options = ["Enter Fees"]
    
    # Display navbar and get selected menu
    # selected_menu = navbar_component(menu_options)
    selected_menu = navbar_collapsible_component(menu_options)
    
    # Route to appropriate page based on navbar selection
    if selected_menu == "Enter Fees":
        fees_entry_page()
    elif selected_menu in ["View All Records", "Paid & Unpaid Students Record", "Student Yearly Report"]:
        reports_page(selected_menu)
    elif selected_menu in ["User Management", "Set Student Fees"]:
        admin_page(selected_menu)

if __name__ == "__main__":
    main()
# [file content end]