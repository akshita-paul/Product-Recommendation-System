import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import models
import time

# ---------------------------------------------------------------------------
# Page configuration & custom premium styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🔮 Product Recommendation System",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Define style variables based on current theme state
if st.session_state.theme == "dark":
    theme_vars = """
        --bg-gradient: linear-gradient(135deg, #090615 0%, #110c24 50%, #05030d 100%);
        --sidebar-bg: rgba(7, 4, 18, 0.85);
        --card-bg: rgba(20, 15, 38, 0.45);
        --card-border: 1px solid rgba(255, 255, 255, 0.08);
        --card-hover-border: 1px solid rgba(168, 85, 247, 0.4);
        --text-primary: #ffffff;
        --text-secondary: #a3a1c2;
        --text-muted: #6b698a;
        --accent-purple: #a855f7;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --glass-blur: blur(12px);
        --shadow-main: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        --shadow-glow: 0 0 15px rgba(168, 85, 247, 0.15);
    """
else:
    theme_vars = """
        --bg-gradient: linear-gradient(135deg, #f2f4fc 0%, #e2e6f3 50%, #d5daf0 100%);
        --sidebar-bg: rgba(255, 255, 255, 0.75);
        --card-bg: rgba(255, 255, 255, 0.6);
        --card-border: 1px solid rgba(255, 255, 255, 0.4);
        --card-hover-border: 1px solid rgba(124, 58, 237, 0.4);
        --text-primary: #151226;
        --text-secondary: #585573;
        --text-muted: #918fa8;
        --accent-purple: #7c3aed;
        --accent-blue: #2563eb;
        --accent-cyan: #0891b2;
        --accent-green: #059669;
        --accent-red: #dc2626;
        --glass-blur: blur(16px);
        --shadow-main: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
        --shadow-glow: 0 0 15px rgba(124, 58, 237, 0.1);
    """

# Deep Purple / Light Glass Theme CSS (Sourced from style.css with dynamic theme variables)
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        __THEME_VARIABLES__
        --border-radius-lg: 18px;
        --border-radius-md: 12px;
        --border-radius-sm: 8px;
        --font-heading: 'Plus Jakarta Sans', sans-serif;
        --font-body: 'Outfit', sans-serif;
    }
    
    /* Background overrides */
    .stApp {
        background: var(--bg-gradient) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
    }
    
    /* Remove white decoration strip at the top of Streamlit */
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Hide top header background completely to remove the strip */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        height: 0px !important;
        display: none !important;
    }
    
    /* Adjust top padding of the main block */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* Hide the radio bullet markers in sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    /* Style the radio labels as a list of menu items in sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 14px 18px !important;
        margin-bottom: 8px !important;
        border-radius: var(--border-radius-md) !important;
        color: var(--text-secondary) !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        font-family: var(--font-body) !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        cursor: pointer !important;
        box-shadow: none !important;
        position: relative !important;
    }
    
    /* Inject FontAwesome icons using pseudo-elements with FontAwesome font-family */
    section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
        font-family: "Font Awesome 6 Free" !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        display: inline-block !important;
        transition: transform 0.2s !important;
    }
    
    /* Hover icon animation */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before {
        transform: translateX(2px) !important;
    }
    
    /* Map options to FontAwesome unicodes */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-of-type(1)::before {
        content: "\\f015" !important; /* fa-house-chimney */
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-of-type(2)::before {
        content: "\\e2ca" !important; /* fa-wand-magic-sparkles */
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-of-type(3)::before {
        content: "\\f0cb" !important; /* fa-table-list */
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-of-type(4)::before {
        content: "\\f201" !important; /* fa-chart-line */
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-of-type(5)::before {
        content: "\\f05a" !important; /* fa-circle-info */
    }
    
    /* Hover state in sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border-color: var(--accent-purple) !important;
    }
    /* Active/Selected state in sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.18) 0%, rgba(59, 131, 246, 0.18) 100%) !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        color: var(--accent-purple) !important;
        box-shadow: var(--shadow-glow) !important;
    }
    
    /* Style the radio labels on main content area as algorithm grid cards */
    div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] *) div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 12px !important;
    }
    div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] *) div[role="radiogroup"] label {
        background: var(--card-bg) !important;
        border: var(--card-border) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 16px !important;
        text-align: center !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        color: var(--text-secondary) !important;
        width: 100% !important;
        white-space: pre-line !important;
        line-height: 1.4 !important;
        font-size: 13px !important;
    }
    div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] *) div[role="radiogroup"] label:hover {
        background: var(--card-bg) !important;
        border-color: var(--accent-purple) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] *) div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(59, 131, 246, 0.15) 100%) !important;
        border-color: var(--accent-purple) !important;
        box-shadow: var(--shadow-glow) !important;
        color: var(--accent-purple) !important;
    }
    div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] *) div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    
    /* Sidebar Overrides */
    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        backdrop-filter: var(--glass-blur) !important;
        -webkit-backdrop-filter: var(--glass-blur) !important;
        border-right: var(--card-border) !important;
    }
    
    /* Header/Status styles */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 32px;
    }
    .dashboard-title {
        font-family: var(--font-heading) !important;
        font-size: 32px !important;
        background: linear-gradient(to right, var(--text-primary), var(--accent-purple)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 700 !important;
        margin: 0;
    }
    .dashboard-subtitle {
        color: var(--text-secondary) !important;
        font-size: 15px !important;
        margin-top: 4px !important;
    }
    
    /* Status Badge */
    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: var(--card-bg);
        border: var(--card-border);
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 500;
        color: var(--text-primary);
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--accent-green);
        box-shadow: 0 0 10px var(--accent-green);
        display: inline-block;
        animation: pulse-animation 2s infinite;
    }
    
    @keyframes pulse-animation {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    /* Card Styles */
    .premium-card {
        background: var(--card-bg) !important;
        backdrop-filter: var(--glass-blur) !important;
        -webkit-backdrop-filter: var(--glass-blur) !important;
        border: var(--card-border) !important;
        border-radius: var(--border-radius-lg) !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: var(--shadow-main) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .premium-card:hover {
        border-color: var(--accent-purple) !important;
        box-shadow: var(--shadow-glow) !important;
    }
    .premium-card-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
        border-left: 3px solid var(--accent-purple);
        padding-left: 10px;
    }
    
    /* Metrics Row */
    .stat-container {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: var(--border-radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    .stat-icon.purple {
        background: rgba(168, 85, 247, 0.15);
        color: var(--accent-purple);
        border: 1px solid rgba(168, 85, 247, 0.25);
    }
    .stat-icon.blue {
        background: rgba(59, 130, 246, 0.15);
        color: var(--accent-blue);
        border: 1px solid rgba(59, 130, 246, 0.25);
    }
    .stat-icon.green {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .stat-value {
        font-size: 24px;
        font-weight: 800;
        color: var(--text-primary);
        margin: 2px 0;
    }
    .stat-label {
        font-size: 13px;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Sidebar Navigation Menu */
    .menu-logo-container {
        padding: 1.5rem 1rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .menu-logo-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
        border-radius: var(--border-radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
    }
    .menu-logo-text {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
    }
    .menu-logo-text span {
        color: var(--accent-purple);
    }
    .menu-logo-sub {
        font-size: 11px;
        color: var(--text-muted);
        font-weight: 500;
    }
    
    /* Product list items/cards */
    .product-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--card-bg) !important;
        border: var(--card-border) !important;
        padding: 16px !important;
        border-radius: var(--border-radius-md) !important;
        margin-bottom: 12px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .product-row:hover {
        border-color: var(--accent-purple) !important;
        transform: translateX(4px) !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        background-color: transparent;
        border: none;
        color: var(--text-secondary);
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-purple) !important;
        border-bottom-color: var(--accent-purple) !important;
        font-weight: 600;
    }
    
    /* Buttons override */
    div.stButton > button {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-blue) 100%) !important;
        color: #fff !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3) !important;
        border: none !important;
        border-radius: var(--border-radius-md) !important;
        padding: 12px 24px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.45) !important;
        color: #fff !important;
    }
    
    .algo-quick-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .algo-quick-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--card-bg);
        border: var(--card-border);
        padding: 16px;
        border-radius: var(--border-radius-md);
        margin-bottom: 12px;
    }
    .algo-meta h5 {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 2px;
        color: var(--text-primary);
    }
    .algo-meta p {
        font-size: 11px;
        color: var(--text-secondary);
        margin: 0;
    }
    .badge {
        font-size: 11px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
        white-space: nowrap;
    }
    .badge-accuracy {
        background: rgba(168, 85, 247, 0.15);
        color: var(--accent-purple);
        border: 1px solid rgba(168, 85, 247, 0.25);
    }
    
    .kpi-box {
        background: var(--card-bg) !important;
        border: var(--card-border) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 20px 16px !important;
        text-align: center !important;
        transition: transform 0.2s !important;
    }
    .kpi-box:hover {
        transform: translateY(-2px) !important;
        border-color: var(--accent-purple) !important;
    }
    .kpi-title {
        font-size: 11px !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
        display: block !important;
        margin-bottom: 6px !important;
    }
    .kpi-box h2 {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: var(--accent-purple) !important;
        margin-bottom: 4px !important;
        margin-top: 0 !important;
    }
    .kpi-box p {
        font-size: 10px !important;
        color: var(--text-muted) !important;
        line-height: 1.3 !important;
        margin: 0 !important;
    }
    
    /* Table Styling */
    .table-wrapper {
        overflow-x: auto;
        margin-top: 20px;
    }
    .comparison-table {
        width: 100% !important;
        border-collapse: collapse !important;
        text-align: left !important;
        font-size: 14px !important;
        color: var(--text-primary) !important;
    }
    .comparison-table th, 
    .comparison-table td {
        padding: 16px 24px !important;
        border-bottom: var(--card-border) !important;
    }
    .comparison-table th {
        background: var(--card-bg) !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    .comparison-table tbody tr {
        transition: background 0.2s !important;
    }
    .comparison-table tbody tr:hover {
        background: var(--card-bg) !important;
    }
    .comparison-table tbody tr.best-row {
        background: rgba(168, 85, 247, 0.1) !important;
    }
    .comparison-table tbody tr.best-row td:first-child {
        border-left: 4px solid var(--accent-purple) !important;
        padding-left: 20px !important;
    }
    .comparison-table tbody tr.best-row td {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    .comparison-table tbody tr.best-row td:first-child::after {
        content: '★ Best' !important;
        font-size: 9px !important;
        background: var(--accent-purple) !important;
        color: #fff !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        margin-left: 8px !important;
        font-weight: 600 !important;
        vertical-align: middle !important;
        display: inline-block !important;
    }

    /* Sidebar Footer & Theme Toggle styling */
    .sidebar-footer {
        border-top: var(--card-border) !important;
        padding-top: 20px !important;
        margin-top: 5rem !important;
    }
    
    .theme-toggle-container {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin-bottom: 20px !important;
        padding: 0 6px !important;
    }
    
    .theme-label {
        font-size: 13px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    
    /* Switch Styles */
    .switch {
        position: relative !important;
        display: inline-block !important;
        width: 40px !important;
        height: 22px !important;
    }
    
    .switch input {
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    .slider {
        position: absolute !important;
        cursor: pointer !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background-color: var(--text-muted) !important;
        transition: .3s !important;
    }
    
    .slider:before {
        position: absolute !important;
        content: "" !important;
        height: 16px !important;
        width: 16px !important;
        left: 3px !important;
        bottom: 3px !important;
        background-color: white !important;
        transition: .3s !important;
    }
    
    .switch input:checked + .slider {
        background-color: var(--accent-purple) !important;
    }
    
    .switch input:checked + .slider:before {
        transform: translateX(18px) !important;
    }
    
    .slider.round {
        border-radius: 34px !important;
    }
    
    .slider.round:before {
        border-radius: 50% !important;
    }
    
    /* User Profile */
    .user-profile {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    
    .avatar {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: var(--accent-purple) !important;
        font-size: 18px !important;
    }
    
    .profile-info h4 {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
    }
    
    .profile-info p {
        font-size: 11px !important;
        color: var(--text-muted) !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    /* Footer styling */
    .footer-section {
        border-top: var(--card-border);
        padding-top: 20px;
        margin-top: 40px;
        text-align: center;
        color: var(--text-muted);
        font-size: 12px;
    }
    .footer-section a {
        color: var(--accent-purple);
        text-decoration: none;
    }
    .footer-section a:hover {
        text-decoration: underline;
    }
    /* Result cards used in recommendation outputs */
    .result-card {
        background: var(--card-bg);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: var(--card-border);
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateX(4px);
        border-color: var(--accent-purple);
    }
    .result-card-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-primary);
    }
    .result-card-cat {
        font-size: 0.75rem;
        color: var(--accent-purple);
    }
    .result-card-meta {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.2rem;
    }
    .prediction-box {
        background: var(--card-bg);
        padding: 1.2rem;
        border-radius: 12px;
        border: var(--card-border);
        text-align: center;
        margin-bottom: 1rem;
    }
    .prediction-label {
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    .prediction-score {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }
    .welcome-desc {
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .stat-desc {
        font-size: 11px;
        color: var(--text-muted);
    }

    /* Streamlit native widget overrides for light theme */
    .stTextInput input,
    .stNumberInput input {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border: var(--card-border) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border: var(--card-border) !important;
    }
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
        background: var(--sidebar-bg) !important;
        color: var(--text-primary) !important;
    }
    .stSlider [data-testid="stTickBar"],
    .stSlider label {
        color: var(--text-secondary) !important;
    }
    /* Spinner, info, success, warning, error boxes */
    div[data-testid="stAlert"] {
        background: var(--card-bg) !important;
        border: var(--card-border) !important;
        color: var(--text-primary) !important;
    }
    .stDataFrame, .stTable {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
    }
    /* Toggle label text */
    .stToggle label {
        color: var(--text-secondary) !important;
    }
    /* Altair/Vega chart background fix */
    .vega-embed .marks {
        fill: var(--text-primary) !important;
    }

</style>
""".replace("__THEME_VARIABLES__", theme_vars), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------------
df = models._load_dataset()
total_products_count = len(df)

# ---------------------------------------------------------------------------
# Sidebar Panel: RecEngine.ai Logo & Navigation
# ---------------------------------------------------------------------------
if "nav" not in st.session_state:
    st.session_state.nav = "Home"

options = ["Home", "Product Recs", "Algorithm Comparison", "Analytics", "About Project"]
nav_index = options.index(st.session_state.nav) if st.session_state.nav in options else 0

with st.sidebar:
    st.markdown("""
    <div class="menu-logo-container">
        <div class="menu-logo-icon">
            <i class="fa-solid fa-brain-circuit logo-icon" style="color: white; font-size: 20px;"></i>
        </div>
        <div>
            <div class="menu-logo-text">RecEngine<span>.ai</span></div>
            <div class="menu-logo-sub">Machine Learning Dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(" ")
    
    # Custom Radio button style navigation
    nav_selection = st.radio(
        "Navigation Menu",
        options,
        index=nav_index,
        label_visibility="collapsed"
    )
    st.session_state.nav = nav_selection
    
    st.markdown("""
    <div class="sidebar-footer" style="border-top: var(--card-border); padding-top: 15px; margin-top: 2rem; margin-bottom: 5px;">
        <div class="theme-toggle-container" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
            <span class="theme-label"><i class="fa-solid fa-moon"></i> Dark Mode</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    dark_mode = st.toggle("Dark Mode Toggle", value=(st.session_state.theme == "dark"), label_visibility="collapsed")
    new_theme = "dark" if dark_mode else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
        
    st.markdown("""
    <div class="sidebar-footer" style="padding-top: 5px;">
        <div class="user-profile">
            <div class="avatar"><i class="fa-solid fa-user-tie"></i></div>
            <div class="profile-info">
                <h4>ML Engineer</h4>
                <p>Administrator</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Helper function to render status header
def render_header(title, subtitle):
    st.markdown(f"""
    <div class="dashboard-header">
        <div>
            <div class="dashboard-title">{title}</div>
            <div class="dashboard-subtitle">{subtitle}</div>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span>
            Models Loaded
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page 1: Home
# ---------------------------------------------------------------------------
if nav_selection == "Home":
    render_header("Product Recommendation System", "Get product recommendations using Machine Learning algorithms")
    
    # Welcome Card
    st.markdown("""
    <div class="premium-card" style="padding-bottom: 1.2rem;">
        <div class="premium-card-title">Welcome to the Product Recommendation Console</div>
        <div class="welcome-desc">
            Test machine learning classification and content-based filtering models using 42,000+ Amazon electronic 
            and device sales records. Predict recommendation statuses or extract similar products instantly.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Launch Recommendation Console →"):
        st.session_state.nav = "Product Recs"
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="premium-card">
            <div class="stat-container">
                <div class="stat-icon purple"><i class="fa-solid fa-database"></i></div>
                <div class="stat-details">
                    <span class="stat-label">Total Products</span>
                    <h3 class="stat-value">{total_products_count:,}</h3>
                    <span class="stat-desc">Cleaned Amazon dataset records</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="premium-card">
            <div class="stat-container">
                <div class="stat-icon blue"><i class="fa-solid fa-cube"></i></div>
                <div class="stat-details">
                    <span class="stat-label">Available Algorithms</span>
                    <h3 class="stat-value">6</h3>
                    <span class="stat-desc">5 Classifiers + 1 NLP Engine</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="premium-card">
            <div class="stat-container">
                <div class="stat-icon green"><i class="fa-solid fa-circle-check"></i></div>
                <div class="stat-details">
                    <span class="stat-label">Best Model Accuracy</span>
                    <h3 class="stat-value">79.36%</h3>
                    <span class="stat-desc">SVC with TF-IDF text features</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Quick Info & Dataset Composition
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""
        <div class="premium-card">
            <div class="premium-card-title">Algorithm Quick Info</div>
            <div class="algo-quick-list">
                <div class="algo-quick-item">
                    <div class="algo-meta">
                        <h5>Random Forest Classifier</h5>
                        <p>Ensemble of TF-IDF text trees. Best balance of accuracy and recall on product metadata.</p>
                    </div>
                    <span class="badge badge-accuracy">79.20% Acc</span>
                </div>
                <div class="algo-quick-item">
                    <div class="algo-meta">
                        <h5>Support Vector Machine (SVC)</h5>
                        <p>Draws optimal boundaries in TF-IDF text vector space. Highest precision classifier.</p>
                    </div>
                    <span class="badge badge-accuracy">79.36% Acc</span>
                </div>
                <div class="algo-quick-item">
                    <div class="algo-meta">
                        <h5>KNN Classifier</h5>
                        <p>Finds the K nearest TF-IDF neighbors and votes on the recommendation label.</p>
                    </div>
                    <span class="badge badge-accuracy">78.40% Acc</span>
                </div>
                <div class="algo-quick-item">
                    <div class="algo-meta">
                        <h5>Logistic Regression</h5>
                        <p>Linear classifier over TF-IDF text features. Fast and highly interpretable baseline.</p>
                    </div>
                    <span class="badge badge-accuracy">77.87% Acc</span>
                </div>
                <div class="algo-quick-item">
                    <div class="algo-meta">
                        <h5>Decision Tree</h5>
                        <p>Tree-based splits on TF-IDF text features. Explainable and transparent classifier.</p>
                    </div>
                    <span class="badge badge-accuracy">72.13% Acc</span>
                </div>
                <div class="algo-quick-item">
                    <div class="algo-meta">
                        <h5>NLP Content Recommendation</h5>
                        <p>Extracts features using TF-IDF and uses Cosine Similarity to find similar items based on metadata.</p>
                    </div>
                    <span class="badge badge-accuracy">79.36% Acc</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="premium-card" style="height: 100%;">
            <div class="premium-card-title">Dataset Composition</div>
        """, unsafe_allow_html=True)
        # Category composition chart
        cat_counts = df['product_category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        chart = alt.Chart(cat_counts.head(5)).mark_bar(color='#a855f7', cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('Category:N', sort='-y', axis=alt.Axis(labelAngle=-25, labelColor='#b0aec4')),
            y=alt.Y('Count:Q', axis=alt.Axis(labelColor='#b0aec4')),
            tooltip=['Category', 'Count']
        ).properties(height=200, background='transparent').configure_view(strokeOpacity=0)
        st.altair_chart(chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page 2: Product Recs (Recommendation Console)
# ---------------------------------------------------------------------------
elif nav_selection == "Product Recs":
    render_header("Recommendation Engine Console", "Run predictions and search similar products using trained ML models")
    
    # Grid columns
    col_input, col_model = st.columns([1.6, 1])
    
    with col_input:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">📝 Product Features Input</div>', unsafe_allow_html=True)
        
        # Select existing product
        product_list = models.get_all_product_titles()
        selected_prod = st.selectbox(
            "SELECT EXISTING PRODUCT (OPTIONAL - WILL AUTOPOPULATE VALUES)",
            ["Select a product..."] + product_list,
            index=0
        )
        
        # Autofill values
        default_title = ""
        default_cat_idx = 0
        default_reviews = 1500
        default_monthly = 600
        default_original = 129.99
        default_discounted = 99.99
        default_discount_pct = 23.0
        default_best_seller = "No Badge"
        default_sponsored = "Organic"
        default_coupon = "No Coupon"
        default_rating = 4.5
        
        categories = models.get_all_categories()
        
        if selected_prod != "Select a product...":
            matching_rows = df[df['product_title'] == selected_prod]
            if not matching_rows.empty:
                row = matching_rows.iloc[0]
                default_title = str(row['product_title'])
                
                cat_str = str(row['product_category'])
                if cat_str in categories:
                    default_cat_idx = categories.index(cat_str)
                
                default_reviews = int(row.get('total_reviews', 0))
                default_monthly = int(row.get('purchased_last_month', 0))
                default_original = float(row.get('original_price', 0.0))
                default_discounted = float(row.get('discounted_price', 0.0))
                default_discount_pct = float(row.get('discount_percentage', 0.0))
                default_best_seller = str(row.get('is_best_seller', 'No Badge'))
                default_sponsored = str(row.get('is_sponsored', 'Organic'))
                default_coupon = str(row.get('has_coupon', 'No Coupon'))
                default_rating = float(row.get('product_rating', 4.5))
        
        # Input Form
        prod_title = st.text_input("Product Title / Description:", value=default_title, placeholder="Enter keywords or description...")
        
        c1, c2 = st.columns(2)
        with c1:
            category_selection = st.selectbox("Category:", categories, index=default_cat_idx)
            rating = st.slider("Rating (1.0 - 5.0):", 1.0, 5.0, default_rating, step=0.1)
        with c2:
            brand = st.text_input("Brand (Optional):", value="Generic")
            sales_last_month = st.number_input("Sales Last Month:", min_value=0, value=default_monthly)
            
        c3, c4, c5 = st.columns(3)
        with c3:
            orig_price = st.number_input("Original Price ($):", min_value=0.0, value=default_original)
        with c4:
            disc_price = st.number_input("Discounted Price ($):", min_value=0.0, value=default_discounted)
        with c5:
            disc_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=default_discount_pct)
            
        c6, c7, c8 = st.columns(3)
        with c6:
            tot_reviews = st.number_input("Total Reviews:", min_value=0, value=default_reviews)
        with c7:
            best_seller_status = st.selectbox("Best Seller Status:", ["No Badge", "Best Seller"], index=0 if default_best_seller == "No Badge" else 1)
        with c8:
            sponsored_status = st.selectbox("Sponsored Status:", ["Organic", "Sponsored"], index=0 if default_sponsored == "Organic" else 1)
            
        coupon_avail = st.selectbox("Coupon Availability:", ["No Coupon", "Save 10% with coupon", "Save 15% with coupon", "Save $20.00 with coupon"], index=0 if "No" in default_coupon else 1)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_model:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">⚙️ Select Algorithm</div>', unsafe_allow_html=True)
        
        model_choice_display = st.radio(
            "Model list:",
            [
                "🌲 Random Forest\nEnsemble bagging model",
                "🎯 SVC\nOptimal kernel boundary",
                "🌿 Decision Tree\nInterpretable node splits",
                "👥 KNN\nInstance-based neighbors",
                "✍️ Logistic Regression\nFast baseline classifier",
                "🌐 NLP Content Recommendation\nTF-IDF similarity engine"
            ],
            label_visibility="collapsed"
        )
        
        # Clean mapping to backend keys
        model_choice_mapping = {
            "🌲 Random Forest\nEnsemble bagging model": "Random Forest",
            "🎯 SVC\nOptimal kernel boundary": "SVC",
            "🌿 Decision Tree\nInterpretable node splits": "Decision Tree",
            "👥 KNN\nInstance-based neighbors": "KNN",
            "✍️ Logistic Regression\nFast baseline classifier": "Logistic Regression",
            "🌐 NLP Content Recommendation\nTF-IDF similarity engine": "NLP-based Recommendation"
        }
        model_choice = model_choice_mapping[model_choice_display]
        
        st.write(" ")
        recommend_clicked = st.button("Recommend Product")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Output card
        st.markdown('<div class="premium-card" style="min-height: 250px;">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">📋 Recommendation Output</div>', unsafe_allow_html=True)
        
        if recommend_clicked:
            if model_choice == "NLP-based Recommendation":
                query_text = prod_title if prod_title.strip() else selected_prod
                if query_text == "Select a product..." or not query_text.strip():
                    st.warning("Please select a product or enter keywords in the Title first.")
                else:
                    with st.spinner("Searching similarity matrix..."):
                        if query_text in product_list:
                            results = models.recommend_products_nlp(query_text, top_n=5)
                        else:
                            results = models.search_products_nlp(query_text, top_n=5)
                            
                        if results.empty:
                            st.info("No close matches found.")
                        else:
                            st.success("Similarity recommendations generated successfully!")
                            for idx, row in results.iterrows():
                                st.markdown(f"""
                                <div class="result-card">
                                    <div class="result-card-title">{row['product_title']}</div>
                                    <div class="result-card-cat">{row['product_category']} • Match: {row['match_score']}%</div>
                                    <div class="result-card-meta">⭐ {row['product_rating']} | Price: ${row['discounted_price']:.2f}</div>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                with st.spinner("Processing specifications..."):
                    # Classify using the pre-trained cached model
                    try:
                        label, confidence, metrics = models.predict_recommendation_status(
                            total_reviews=tot_reviews,
                            purchased_last_month=sales_last_month,
                            discounted_price=disc_price,
                            original_price=orig_price,
                            is_best_seller=best_seller_status,
                            is_sponsored=sponsored_status,
                            has_coupon=coupon_avail,
                            product_category=category_selection,
                            discount_percentage=disc_pct,
                            algorithm=model_choice,
                            product_title=prod_title if prod_title.strip() else selected_prod
                        )
                        
                        st.success("Recommendation status predicted successfully!")
                        
                        conf_str = f"Confidence Level: {confidence}%" if confidence is not None else f"Model Accuracy: {metrics['Accuracy']}%"
                        st.markdown(f"""
                        <div class="prediction-box">
                            <div class="prediction-label">CLASSIFIER PREDICTION ({model_choice})</div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: {'#10b981' if label == 'Recommended' else '#ef4444'}; margin: 0.4rem 0;">{label}</div>
                            <div class="prediction-score">{conf_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("### Top Products in Category")
                        same_cat = df[df['product_category'] == category_selection]
                        same_cat = same_cat.sort_values(by='product_rating', ascending=False).head(3)
                        
                        for idx, row in same_cat.iterrows():
                            st.markdown(f"""
                            <div class="result-card">
                                <div class="result-card-title">{row['product_title']}</div>
                                <div class="result-card-cat">{row['product_category']}</div>
                                <div class="result-card-meta">⭐ {row['product_rating']} | Price: ${row['discounted_price']:.2f}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error executing recommendation: {e}")
                        st.warning("Please make sure to run train_models.py to pre-train and cache your models.")
        else:
            st.info("Fill out specifications and press 'Recommend Product' to output matches.")
            
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page 3: Algorithm Comparison
# ---------------------------------------------------------------------------
elif nav_selection == "Algorithm Comparison":
    render_header("Model Comparison Matrix", "Compare metrics like Accuracy, Precision, Recall, and training execution times")
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="premium-card-title">Comparison Matrix (Pre-loaded from models.ipynb)</div>', unsafe_allow_html=True)
    st.write("Performance details gathered from model runs against the testing dataset (20% split). The best model is highlighted.")
    
    metrics_df = models.get_all_model_metrics()
    
    # Find best model
    best_idx = metrics_df['Accuracy'].idxmax()
    
    # Generate rows
    rows_html = ""
    for i, row in metrics_df.iterrows():
        is_best = (i == best_idx)
        row_class = ' class="best-row"' if is_best else ''
        rows_html += f"<tr{row_class}><td>{row['Model']}</td><td>{row['Accuracy']:.2f}%</td><td>{row['Precision']:.2f}%</td><td>{row['Recall']:.2f}%</td><td>{row['F1 Score']:.2f}%</td><td>{row['Training Time']}</td></tr>"
        
    table_html = f"<div class='table-wrapper'><table class='comparison-table'><thead><tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>Training Time</th></tr></thead><tbody>{rows_html}</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page 4: Analytics
# ---------------------------------------------------------------------------
elif nav_selection == "Analytics":
    render_header("Performance & Insights Analytics", "Visualize and dissect classifier outputs using graphs")
    
    c1, c2 = st.columns(2)
    metrics_df = models.get_all_model_metrics()
    
    with c1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">Model Accuracy Comparison</div>', unsafe_allow_html=True)
        chart = alt.Chart(metrics_df).mark_bar(color='#8b5cf6', cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('Model:N', axis=alt.Axis(labelAngle=0, labelColor='#b0aec4')),
            y=alt.Y('Accuracy:Q', scale=alt.Scale(domain=[40, 100]), axis=alt.Axis(labelColor='#b0aec4')),
            tooltip=['Model', 'Accuracy']
        ).properties(height=250).configure_view(strokeOpacity=0)
        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">Classifier F1-Score Trend</div>', unsafe_allow_html=True)
        chart_f1 = alt.Chart(metrics_df).mark_line(point=True, color='#3b82f6').encode(
            x=alt.X('Model:N', axis=alt.Axis(labelColor='#b0aec4')),
            y=alt.Y('F1 Score:Q', scale=alt.Scale(domain=[40, 100]), axis=alt.Axis(labelColor='#b0aec4')),
            tooltip=['Model', 'F1 Score']
        ).properties(height=250).configure_view(strokeOpacity=0)
        st.altair_chart(chart_f1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Evaluation KPI selector
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="premium-card-title">Model Evaluation Details</div>', unsafe_allow_html=True)
    st.write("Select an algorithm to view its individual KPI cards in detail.")
    
    selected_model = st.selectbox("Select Model:", metrics_df['Model'].tolist())
    model_row = metrics_df[metrics_df['Model'] == selected_model].iloc[0]
    
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-box">
            <span class="kpi-title">Accuracy</span>
            <h2>{model_row['Accuracy']:.2f}%</h2>
            <p>Fraction of correct predictions</p>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-box">
            <span class="kpi-title">Precision</span>
            <h2>{model_row['Precision']:.2f}%</h2>
            <p>Ability to avoid false positives</p>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-box">
            <span class="kpi-title">Recall</span>
            <h2>{model_row['Recall']:.2f}%</h2>
            <p>Ability to find all positive samples</p>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="kpi-box">
            <span class="kpi-title">F1 Score</span>
            <h2>{model_row['F1 Score']:.2f}%</h2>
            <p>Weighted harmonic mean of metrics</p>
        </div>
        """, unsafe_allow_html=True)
    with kpi5:
        st.markdown(f"""
        <div class="kpi-box">
            <span class="kpi-title">Training Time</span>
            <h2>{model_row['Training Time']}</h2>
            <p>CPU Execution time in seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page 5: About Project
# ---------------------------------------------------------------------------
elif nav_selection == "About Project":
    render_header("About Project", "System metadata, specifications, and pipeline overview")
    
    st.markdown("""
    <div class="premium-card">
        <div class="premium-card-title">Recommendation Engine Pipeline Overview</div>
        <div style="color: #b0aec4; line-height: 1.6;">
            This system provides recommendation outcomes based on two different machine learning pipelines:
            <ol style="margin-top: 0.5rem; padding-left: 1.2rem;">
                <li><strong>Dynamic TF-IDF Vectorizer</strong>: Maps vocabulary and computes cosine similarities across electronic titles and specifications on-the-fly.</li>
                <li><strong>ML Classification Classifiers</strong>: Converts raw ratings to binary classes (Recommended / Not Recommended) and fits 5 separate classifiers to determine customer recommendation probability based on numerical product stats.</li>
            </ol>
            All training is handled dynamically, with models stored in compressed joblib formats for fast load times and minimal deployment footprint.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Premium Footer Section
# ---------------------------------------------------------------------------
st.markdown("""
<div class="footer-section">
    <p>🔮 Product Recommendation System v1.0.0 | Developer Admin Console</p>
    <p>Powered by Streamlit & Scikit-Learn | <a href="#" target="_blank"><i class="fa-brands fa-github"></i> GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
