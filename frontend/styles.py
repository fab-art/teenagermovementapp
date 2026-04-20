import streamlit as st

def apply_styles():
    """Apply custom CSS styles to the Streamlit app."""
    
    custom_css = """
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --success-color: #16a34a;
        --warning-color: #ca8a04;
        --danger-color: #dc2626;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Hide default Streamlit header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom card styling */
    .metric-card {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 4px solid var(--primary-color);
    }
    
    .metric-card.success {
        border-left-color: var(--success-color);
    }
    
    .metric-card.warning {
        border-left-color: var(--warning-color);
    }
    
    .metric-card.danger {
        border-left-color: var(--danger-color);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--background-color);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    
    /* Success message */
    .stAlert {
        border-radius: 6px;
    }
    
    /* Page title */
    h1, h2, h3 {
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Metric display */
    [data-testid="stMetricValue"] {
        color: var(--primary-color);
    }
    
    /* Table headers */
    thead th {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Navigation menu items */
    .nav-item {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .nav-item:hover {
        background-color: #e0e7ff;
    }
    
    .nav-item.active {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-badge.pending {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-badge.completed {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-badge.cancelled {
        background-color: #fee2e2;
        color: #991b1b;
    }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)


def get_color_scheme():
    """Return the color scheme dictionary for consistent theming."""
    return {
        'primary': '#2563eb',
        'secondary': '#1e40af',
        'success': '#16a34a',
        'warning': '#ca8a04',
        'danger': '#dc2626',
        'background': '#f8fafc',
        'card': '#ffffff',
        'text_primary': '#1e293b',
        'text_secondary': '#64748b'
    }
