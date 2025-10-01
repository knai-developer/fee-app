# [file name]: utils.py
# [file content begin]
#type:ignore
import streamlit as st
import pandas as pd
from datetime import datetime
from database import load_data
from auth import logout  # Add this import

def hide_streamlit_elements():
    """Hide only the GitHub icon while keeping deploy button"""
    st.markdown("""
    <style>
    /* Hide only the GitHub icon specifically */
    div[data-testid="stToolbar"] > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) {
        display: none !important;
    }
    
    /* Alternative selector for GitHub icon */
    button[title="View app source on GitHub"] {
        display: none !important;
    }
    
    /* Hide GitHub fork button */
    .stActionButton:has([title*="GitHub"]) {
        display: none !important;
    }
    
    /* More specific GitHub icon hiding */
    div[data-testid="stToolbar"] button[kind="header"]:first-child {
        display: none !important;
    }
    
    /* Hide the GitHub icon in the toolbar */
    .stApp > header button:first-child {
        display: none !important;
    }
    
    /* Keep deploy button visible but hide GitHub */
    div[data-testid="stToolbar"] > div > div > div:first-child {
        display: none !important;
    }
    
    /* Alternative approach - hide by icon content */
    button[aria-label*="GitHub"] {
        display: none !important;
    }
    
    /* Custom navbar styling */
    .navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: none;
        backdrop-filter: blur(10px);
        position: sticky;
        top: 10px;
        z-index: 1000;
    }
    .navbar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        max-width: 1200px;
        margin: 0 auto;
    }
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        text-decoration: none;
    }
    .navbar-brand-icon {
        font-size: 1.8rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    .navbar-menu {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    .nav-btn {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        cursor: pointer;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    .nav-btn:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
    }
    .nav-btn.active {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    .nav-btn.active::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    .nav-btn.active:hover::before {
        left: 100%;
    }
    .navbar-user-info {
        display: flex;
        align-items: center;
        gap: 15px;
        color: white;
        font-size: 0.85rem;
        flex-wrap: wrap;
    }
    .user-badge {
        margin-bottom:10px;
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 3px 10px rgba(0, 184, 148, 0.3);
    }
    .trial-badge {
        background: linear-gradient(135deg, #fdcb6e, #e17055);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 3px 10px rgba(253, 203, 110, 0.3);
    }
    .logout-btn {
        background: linear-gradient(135deg, #e17055, #d63031);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3);
    }
    .logout-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
        background: linear-gradient(135deg, #d63031, #c23616);
    }
    .nav-divider {
        width: 2px;
        height: 30px;
        background: rgba(255, 255, 255, 0.3);
        margin: 0 10px;
    }
    @media (max-width: 768px) {
        .navbar {
            padding: 0.8rem 1rem;
        }
        .navbar-container {
            flex-direction: column;
            gap: 1rem;
        }
        .navbar-menu {
            justify-content: center;
            gap: 5px;
        }
        .navbar-user-info {
            justify-content: center;
            text-align: center;
            gap: 10px;
        }
        .nav-btn {
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
        }
    }
    
    /* Floating animation for brand */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    .navbar-brand {
        animation: float 4s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def navbar_component(menu_options):
    """Create a beautiful top navigation bar component"""
    
    # Initialize selected menu in session state if not exists
    if 'selected_nav_menu' not in st.session_state:
        st.session_state.selected_nav_menu = menu_options[0]
    
    # Create navbar container
    with st.container():
        st.markdown("""
        <div class="navbar">
            <div class="navbar-container">
                <div class="navbar-brand">
                    <span class="navbar-brand-icon">🏫</span>
                    British School Karachi
                </div>
                
        """, unsafe_allow_html=True)
        
        # Create navigation buttons
        for option in menu_options:
            is_active = st.session_state.selected_nav_menu == option
            active_class = "active" if is_active else ""
            
            # Get appropriate icon for each menu item
            icon_map = {
                "Enter Fees": "💰",
                "View All Records": "👀", 
                "Paid & Unpaid Students Record": "✅",
                "Student Yearly Report": "📊",
                "User Management": "👥",
                "Set Student Fees": "💸"
            }
            icon = icon_map.get(option, "📄")
            
            if st.button(f"{icon} {option}", key=f"nav_{option}", 
                       use_container_width=False,
                       help=f"Go to {option}"):
                st.session_state.selected_nav_menu = option
                st.rerun()
        
        st.markdown("""
                </div>
                
                <div class="navbar-user-info">
        """, unsafe_allow_html=True)
        
        # User info
        user_type = "Admin" if st.session_state.is_admin else "User"
        st.markdown(f'<div class="user-badge">👤 {user_type}: {st.session_state.current_user}</div>', 
                   unsafe_allow_html=True)
        
        # Trial info
        if st.session_state.trial_remaining:
            st.markdown(f'<div class="trial-badge">⏰ {st.session_state.trial_remaining}</div>', 
                       unsafe_allow_html=True)
        
        # Divider
        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", key="navbar_logout", use_container_width=False):
            logout()  # This will now work with the import
            st.rerun()
        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return st.session_state.selected_nav_menu

def format_currency(val):
    """Format currency with Pakistani Rupees symbol and thousand separators"""
    try:
        return f"Rs. {int(val):,}" if not pd.isna(val) and val != 0 else "Rs. 0"
    except:
        return "Rs. 0"

def style_row(row):
    """Apply styling to DataFrame rows based on payment status"""
    today = datetime.now()
    is_between_1st_and_10th = 1 <= today.day <= 10
    styles = [''] * len(row)
    
    if is_between_1st_and_10th:
        if row['Monthly Fee'] == 0:
            styles[0] = 'color: red'
        else:
            styles[0] = 'color: green'
    return styles

def get_academic_year(date):
    """Determine academic year based on date"""
    year = date.year
    if date.month >= 4:  # Academic year starts in April
        return f"{year}-{year+1}"
    return f"{year-1}-{year}"

def check_annual_admission_paid(student_id, academic_year):
    """Check if annual charges or admission fee have been paid for the academic year"""
    df = load_data()
    if df.empty:
        return False, False
    
    student_records = df[(df['ID'] == student_id) & (df['Academic Year'] == academic_year)]
    annual_paid = student_records['Annual Charges'].sum() > 0
    admission_paid = student_records['Admission Fee'].sum() > 0
    
    return annual_paid, admission_paid

def get_unpaid_months(student_id):
    """Get list of unpaid months for a specific student"""
    df = load_data()
    all_months = [
        "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
        "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"
    ]
    
    if df.empty or student_id is None:
        return all_months
    
    paid_months = df[(df['ID'] == student_id) & (df['Monthly Fee'] > 0)]['Month'].unique().tolist()
    
    unpaid_months = [month for month in all_months if month not in paid_months]
    
    return unpaid_months
# [file content end]
def get_student_fee_amount(student_id, fee_type):
    """Get specific fee amount for a student from database"""
    from database import load_student_fees
    
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