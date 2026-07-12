import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# ---------- SECURITY: Safe symbol whitelist for parse_expr ----------
# Only allow known mathematical symbols/functions. This blocks __import__, eval, exec, open, etc.
_SAFE_NAMES = {
    'x': sp.Symbol('x'), 'y': sp.Symbol('y'), 'z': sp.Symbol('z'),
    'pi': sp.pi, 'e': sp.E, 'E': sp.E, 'I': sp.I, 'oo': sp.oo,
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'sec': sp.sec, 'csc': sp.csc, 'cot': sp.cot,
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
    'sqrt': sp.sqrt, 'cbrt': sp.cbrt, 'root': sp.root,
    'log': sp.log, 'ln': sp.log, 'exp': sp.exp,
    'Abs': sp.Abs, 'abs': sp.Abs,
    'sign': sp.sign, 'floor': sp.floor, 'ceiling': sp.ceiling,
    'factorial': sp.factorial,
    'gamma': sp.gamma, 'beta': sp.beta,
    'diff': sp.diff, 'integrate': sp.integrate,
    'Sum': sp.Sum, 'Product': sp.Product,
    'Rational': sp.Rational, 'Float': sp.Float, 'Integer': sp.Integer,
    'theta': sp.Symbol('theta'), 'alpha': sp.Symbol('alpha'),
    'beta_sym': sp.Symbol('beta'), 'phi': sp.Symbol('phi'),
}

# Dangerous patterns that must NEVER reach the parser
_DANGEROUS_PATTERNS = re.compile(
    r'__\w+__|\bimport\b|\beval\b|\bexec\b|\bcompile\b|\bopen\b'
    r'|\bgetattr\b|\bsetattr\b|\bdelattr\b|\bglobals\b|\blocals\b'
    r'|\bos\b|\bsys\b|\bsubprocess\b|\bshutil\b|\bpathlib\b'
    r'|\bbreakpoint\b|\b__builtins__\b',
    re.IGNORECASE
)

MAX_EXPR_LENGTH = 500  # Prevent DoS via absurdly long expressions

def safe_parse(expression_str: str) -> sp.Expr:
    """Parse a math expression string with security restrictions."""
    if len(expression_str) > MAX_EXPR_LENGTH:
        raise ValueError(f"Expression too long ({len(expression_str)} chars). Max is {MAX_EXPR_LENGTH}.")
    if _DANGEROUS_PATTERNS.search(expression_str):
        raise ValueError("Expression contains forbidden keywords. Only mathematical expressions are allowed.")
    transformations = standard_transformations + (implicit_multiplication_application,)
    return parse_expr(expression_str, local_dict=_SAFE_NAMES, transformations=transformations)

# Page Configuration
st.set_page_config(
    page_title="AS.Dev's Desmos Clone",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism CSS Inject
st.markdown("""
<style>
    /* Styling Streamlit app background and default fonts */
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #0d131f 100%);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Sleek container for parameters and status */
    .card-panel {
        background: rgba(31, 41, 55, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    
    /* Virtual Keyboard Keys - Styled as Glass Buttons with Calculator Padding */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 6px !important;
        padding: 12px 6px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease-in-out !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        min-height: 48px !important;
    }
    
    /* Calculator Grid layout adjustments to reduce blank gaps and pack them tightly */
    .stTabs [data-testid="column"] {
        padding: 1px !important;
        margin: 0px !important;
    }
    .stTabs [data-testid="stHorizontalBlock"] {
        gap: 2px !important;
        margin-bottom: 2px !important;
    }
    div.stButton {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Hover and Focus effect for buttons */
    div.stButton > button:hover {
        background: rgba(59, 130, 246, 0.25) !important;
        border-color: rgba(59, 130, 246, 0.6) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 12px -3px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Click / Active effect */
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Custom Styling for the Formula Text Input Box */
    div.stTextInput > div > div > input {
        background-color: rgba(17, 24, 39, 0.8) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        font-size: 20px !important;
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.3) !important;
    }
    
    div.stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4) !important;
    }

    /* Style the sidebar panel */
    section[data-testid="stSidebar"] {
        background-color: #0c111d !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Tabs Navigation styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: rgba(17, 24, 39, 0.5) !important;
        padding: 6px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 36px !important;
        background-color: transparent !important;
        border-radius: 6px !important;
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 0px 14px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #f8fafc !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Style container with borders (st.container(border=True)) to look like glass cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.35) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }

    /* Force all columns in a row to stretch to the tallest sibling's height */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        flex: 1 !important;
    }
    
    /* Interactive Button Transitions & Hover Animations */
    button {
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    button:hover {
        transform: translateY(-2px) scale(1.03) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25) !important;
        filter: brightness(1.2) !important;
    }
    button:active {
        transform: translateY(1px) scale(0.98) !important;
    }

    /* Animated gradient keyframes for header */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.15); }
        50% { box-shadow: 0 0 30px rgba(99, 102, 241, 0.3); }
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>
    function colorizeButtons() {
        try {
            const doc = window.parent.document;
            const buttons = doc.querySelectorAll("button");
            buttons.forEach(btn => {
                if (btn.dataset.colored) return;
                const txt = btn.innerText || "";
                if (txt.includes("Space")) {
                    btn.style.cssText += "background: rgba(59, 130, 246, 0.15) !important; border-color: rgba(59, 130, 246, 0.5) !important; color: #60a5fa !important;";
                    btn.dataset.colored = "space";
                } else if (txt.includes("Del") || txt.includes("Clear") || txt.includes("🗑")) {
                    btn.style.cssText += "background: rgba(239, 68, 68, 0.18) !important; border: 1.5px solid rgba(239, 68, 68, 0.6) !important; color: #f87171 !important; text-shadow: 0 0 8px rgba(239, 68, 68, 0.3) !important;";
                    btn.dataset.colored = "delete";
                } else if (txt.includes("Add Function")) {
                    btn.style.cssText += "background: rgba(16, 185, 129, 0.18) !important; border: 1.5px solid rgba(16, 185, 129, 0.6) !important; color: #34d399 !important; text-shadow: 0 0 8px rgba(16, 185, 129, 0.3) !important; font-weight: 600 !important;";
                    btn.dataset.colored = "add";
                }
            });
        } catch(e) {}
    }
    setInterval(colorizeButtons, 400);
</script>
""", unsafe_allow_html=True)

# Secondary component-based colorizer as fallback (runs in parent frame via streamlit.components)
import streamlit.components.v1 as components
components.html("""
<script>
function applyColors() {
    const doc = window.parent.document;
    const buttons = doc.querySelectorAll('button');
    buttons.forEach(btn => {
        const txt = btn.textContent || '';
        if (txt.includes('Add Function')) {
            btn.style.setProperty('background', 'rgba(16,185,129,0.18)', 'important');
            btn.style.setProperty('border', '1.5px solid rgba(16,185,129,0.6)', 'important');
            btn.style.setProperty('color', '#34d399', 'important');
            btn.style.setProperty('text-shadow', '0 0 8px rgba(16,185,129,0.3)', 'important');
            btn.style.setProperty('font-weight', '600', 'important');
        } else if (txt.includes('Del') || txt.includes('Clear') || txt.includes('🗑')) {
            btn.style.setProperty('background', 'rgba(239,68,68,0.18)', 'important');
            btn.style.setProperty('border', '1.5px solid rgba(239,68,68,0.6)', 'important');
            btn.style.setProperty('color', '#f87171', 'important');
            btn.style.setProperty('text-shadow', '0 0 8px rgba(239,68,68,0.3)', 'important');
        } else if (txt.includes('Space')) {
            btn.style.setProperty('background', 'rgba(59,130,246,0.15)', 'important');
            btn.style.setProperty('border-color', 'rgba(59,130,246,0.5)', 'important');
            btn.style.setProperty('color', '#60a5fa', 'important');
        }
    });
}
setInterval(applyColors, 500);
applyColors();
</script>
""", height=0)

# Key mappings for Desmos-like button labels to sympy code
key_mappings = {
    "⬜²": "**2",
    "x⬜": "**",
    "√⬜": "sqrt(",
    "⬜√⬜": "root(",
    "⬜/⬜": "/",
    "log⬜": "log(",
    "π": "pi",
    "θ": "theta",
    "∞": "oo",
    "∫": "integrate(",
    "d/dx": "diff(",
    "≥": ">=",
    "≤": "<=",
    "·": "*",
    "÷": "/",
    "x°": "*pi/180",
    "(⬜)": "(",
    "|⬜|": "abs(",
    "f ∘ g": "*",
    "f(x)": "f(x)",
    "ln": "log(",
    "e⬜": "exp(",
    "(⬜)'": "diff(",
    "∂/∂x": "diff(",
    "∫_⬜^⬜": "integrate(",
    "lim": "limit(",
    "∑": "Sum(",
    "sin": "sin(",
    "cos": "cos(",
    "tan": "tan(",
    "cot": "cot(",
    "csc": "csc(",
    "sec": "sec(",
    "→": "->",
    "←": "<-",
    "≠": "!=",
    "∈": " in ",
    "∉": " not in ",
}

greek_mappings = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa",
    "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "π": "pi",
    "ρ": "rho", "σ": "sigma", "τ": "tau", "υ": "upsilon", "φ": "phi",
    "χ": "chi", "ψ": "psi", "ω": "omega",
    "Α": "Alpha", "Β": "Beta", "Γ": "Gamma", "Δ": "Delta", "Ε": "Epsilon",
    "Ζ": "Zeta", "Η": "Eta", "Θ": "Theta", "Ι": "Iota", "Κ": "Kappa",
    "Λ": "Lambda", "Μ": "Mu", "Ν": "Nu", "Ξ": "Xi", "Π": "Pi",
    "Ρ": "Rho", "Σ": "Sigma", "Τ": "Tau", "Υ": "Upsilon", "Φ": "Phi",
    "Χ": "Chi", "Ψ": "Psi", "Ω": "Omega"
}

# Callback helpers for virtual keyboard operations
def append_text(val):
    to_append = val
    if val in key_mappings:
        to_append = key_mappings[val]
    elif val in greek_mappings:
        to_append = greek_mappings[val]
        
    active_key = f"func_val_{st.session_state.active_input_idx}"
    if active_key in st.session_state:
        st.session_state[active_key] += to_append

def backspace():
    active_key = f"func_val_{st.session_state.active_input_idx}"
    if active_key in st.session_state and len(st.session_state[active_key]) > 0:
        st.session_state[active_key] = st.session_state[active_key][:-1]

def clear_text():
    active_key = f"func_val_{st.session_state.active_input_idx}"
    if active_key in st.session_state:
        st.session_state[active_key] = ""

# Auto-focus callback: when user types in a field, keyboard targets it
def set_focus(idx):
    st.session_state.active_input_idx = idx

# Callback for dimension mode change
def on_mode_change():
    new_mode = st.session_state.dimension_mode_select
    if new_mode == "Single Variable":
        st.session_state.function_inputs = ["x**2 - 2*x"]
    else:
        st.session_state.function_inputs = ["sin(x) * cos(y)"]
    st.session_state.active_input_idx = 0
    # Clear old keys
    for k in list(st.session_state.keys()):
        if k.startswith("func_val_"):
            del st.session_state[k]

# Initialize Default States
if 'function_inputs' not in st.session_state:
    st.session_state.function_inputs = ["x**2 - 2*x"]
if 'active_input_idx' not in st.session_state:
    st.session_state.active_input_idx = 0

# Header UI — Premium Animated Gradient Card
st.markdown("""
<div style="position: relative; overflow: hidden;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(147, 51, 234, 0.15) 50%, rgba(236, 72, 153, 0.10) 100%);
            background-size: 200% 200%;
            animation: gradientShift 8s ease infinite;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 32px 36px;
            border-radius: 20px;
            margin-bottom: 28px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);">
    <!-- Decorative floating particles -->
    <div style="position: absolute; top: 12px; right: 40px; width: 8px; height: 8px; background: rgba(96, 165, 250, 0.5); border-radius: 50%; animation: float 3s ease-in-out infinite;"></div>
    <div style="position: absolute; top: 30px; right: 80px; width: 5px; height: 5px; background: rgba(192, 132, 252, 0.4); border-radius: 50%; animation: float 4s ease-in-out infinite 0.5s;"></div>
    <div style="position: absolute; bottom: 18px; right: 60px; width: 6px; height: 6px; background: rgba(52, 211, 153, 0.4); border-radius: 50%; animation: float 3.5s ease-in-out infinite 1s;"></div>

    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
        <span style="font-size: 2.2rem; animation: float 3s ease-in-out infinite;">📐</span>
        <h1 style="margin: 0; font-size: 2.4rem;
                    background: linear-gradient(135deg, #60a5fa 0%, #c084fc 40%, #f472b6 70%, #34d399 100%);
                    background-size: 200% auto;
                    animation: gradientShift 6s linear infinite;
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    font-weight: 800; letter-spacing: -0.5px;">
            AS.Dev's Desmos Clone
        </h1>
    </div>
    <p style="margin: 0 0 16px 0; color: #b0bec5; font-size: 1.05rem; line-height: 1.6; max-width: 800px;">
        An advanced mathematical modeling playground — graph single‑variable functions in 2D or multivariable functions in 3D,
        run real‑time calculus analyses, and adjust extra variables on the fly.
    </p>
    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
        <span style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); color: #60a5fa; padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">📈 2D & 3D Plotting</span>
        <span style="background: rgba(147, 51, 234, 0.15); border: 1px solid rgba(147, 51, 234, 0.3); color: #c084fc; padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">∫ Calculus Engine</span>
        <span style="background: rgba(236, 72, 153, 0.15); border: 1px solid rgba(236, 72, 153, 0.3); color: #f472b6; padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">⌨️ Virtual Keyboard</span>
        <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">🎨 Custom Colors</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.markdown("## ⚙️ Configuration")

# 1. Dimension Mode
mode = st.sidebar.selectbox(
    "Plotting Dimension",
    ["Single Variable", "Multivariable"],
    key="dimension_mode_select",
    on_change=on_mode_change
)

st.sidebar.markdown("---")

# Domain and Grid Configuration
st.sidebar.markdown("### 🌐 Domain & Resolution")

if mode == "Single Variable":
    x_min, x_max = st.sidebar.slider(
        "x Domain",
        min_value=-100.0,
        max_value=100.0,
        value=(-10.0, 10.0),
        step=1.0,
        key="x_domain_2d"
    )
    if x_min >= x_max:
        st.sidebar.error("Error: Min domain must be less than Max domain.")
        st.stop()
        
    resolution = st.sidebar.slider(
        "Plot Resolution (Points)",
        min_value=100,
        max_value=2000,
        value=600,
        step=50,
        key="res_2d"
    )
else: # Multivariable
    x_min, x_max = st.sidebar.slider(
        "x Domain",
        min_value=-50.0,
        max_value=50.0,
        value=(-5.0, 5.0),
        step=1.0,
        key="x_domain_3d"
    )
    y_min, y_max = st.sidebar.slider(
        "y Domain",
        min_value=-50.0,
        max_value=50.0,
        value=(-5.0, 5.0),
        step=1.0,
        key="y_domain_3d"
    )
    if x_min >= x_max or y_min >= y_max:
        st.sidebar.error("Error: Min domains must be less than Max domains.")
        st.stop()
        
    resolution = st.sidebar.slider(
        "Mesh Density (N x N)",
        min_value=20,
        max_value=150,
        value=60,
        step=5,
        key="res_3d"
    )

st.sidebar.markdown("---")

# 3D Visual Customizations
if mode == "Multivariable":
    st.sidebar.markdown("### 🎨 3D Rendering Styles")
    colormap = st.sidebar.selectbox(
        "Surface Colormap",
        ["viridis", "plasma", "magma", "coolwarm", "inferno", "cividis", "Spectral", "ocean"],
        index=0
    )
    surf_style = st.sidebar.selectbox(
        "Render Mode",
        ["Solid Surface", "Wireframe", "Contours Only"],
        index=0
    )
    st.sidebar.markdown("#### 🔄 View Angle")
    elev_angle = st.sidebar.slider("Elevation View Angle", 0, 90, 30, 5)
    azim_angle = st.sidebar.slider("Azimuth Rotation Angle", 0, 360, 45, 5)
    st.sidebar.markdown("---")

# Create callback helper for inline row deletion
def delete_row_callback(idx):
    if len(st.session_state.function_inputs) > 1:
        st.session_state.function_inputs.pop(idx)
        # Shift values down to prevent losing text inputs
        num_fields = len(st.session_state.function_inputs) + 1
        for k in range(idx, num_fields - 1):
            next_key = f"func_val_{k+1}"
            curr_key = f"func_val_{k}"
            if next_key in st.session_state:
                st.session_state[curr_key] = st.session_state[next_key]
        last_key = f"func_val_{num_fields-1}"
        if last_key in st.session_state:
            del st.session_state[last_key]
        # Adjust keyboard focus selection
        if st.session_state.active_input_idx >= len(st.session_state.function_inputs):
            st.session_state.active_input_idx = len(st.session_state.function_inputs) - 1
        st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

# Draw the dynamic list of function input fields with inline color picker and individual delete button
graph_colors = []
default_colors = ['#06b6d4', '#a855f7', '#eab308', '#ec4899', '#3b82f6', '#14b8a6', '#ef4444', '#10b981', '#f97316']

for i in range(len(st.session_state.function_inputs)):
    state_key = f"func_val_{i}"
    if state_key not in st.session_state:
        st.session_state[state_key] = st.session_state.function_inputs[i]

    is_focused = (st.session_state.active_input_idx == i)
    # Visual indicator for the currently focused function
    focus_dot = "🔹 " if is_focused else ""
    label_text = f"{focus_dot}f{chr(8321 + i)}(x)" if mode == "Single Variable" else f"{focus_dot}f{chr(8321 + i)}(x, y)"

    col_input_field, col_color_field, col_delete_field = st.columns([6, 0.7, 0.7])
    with col_input_field:
        st.text_input(
            label_text,
            key=state_key,
            on_change=set_focus,
            args=(i,)
        )
    with col_color_field:
        default_color = default_colors[i % len(default_colors)]
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        chosen_color = st.color_picker(
            f"Color {i+1}",
            value=default_color,
            key=f"color_pick_{i}",
            label_visibility="collapsed"
        )
        graph_colors.append(chosen_color)
    with col_delete_field:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        is_disabled = (len(st.session_state.function_inputs) <= 1)
        st.button(
            "🗑",
            key=f"del_row_{i}",
            on_click=delete_row_callback,
            args=(i,),
            disabled=is_disabled,
            use_container_width=True,
            help=f"Delete function {i+1}"
        )

# Dynamic Controls — Add function field (keyboard auto-targets last edited field)
if st.button("➕ Add Function Field", use_container_width=True):
    new_idx = len(st.session_state.function_inputs)
    st.session_state.function_inputs.append("x" if mode == "Single Variable" else "x*y")
    st.session_state.active_input_idx = new_idx  # auto-focus the newly added field
    st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

# Control row directly above the keyboard tabs
st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
c_space, c_back, c_clear = st.columns([2, 1, 1])
with c_space:
    st.button("␣ Space", key="ctrl_space", on_click=append_text, args=(" ",), use_container_width=True)
with c_back:
    st.button("⌫ Del", key="ctrl_back", on_click=backspace, use_container_width=True)
with c_clear:
    st.button("🗑️ Clear", key="ctrl_clear", on_click=clear_text, use_container_width=True)

# ----------------- VIRTUAL KEYBOARD TABS -----------------
basic_keys = [
    ["⬜²", "x⬜", "√⬜", "⬜√⬜", "⬜/⬜", "log⬜", "π", "θ", "∞", "∫", "d/dx"],
    ["≥", "≤", "·", "÷", "x°", "(⬜)", "|⬜|", "f ∘ g", "f(x)", "ln", "e⬜"],
    ["(⬜)'", "∂/∂x", "∫_⬜^⬜", "lim", "∑", "sin", "cos", "tan", "cot", "csc", "sec"]
]

greek_lower_keys = [
    ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ"],
    ["ι", "κ", "λ", "μ", "ν", "ξ", "π", "ρ"],
    ["σ", "τ", "υ", "φ", "χ", "ψ", "ω"]
]

greek_upper_keys = [
    ["Α", "Β", "Γ", "Δ", "Ε", "Ζ", "Η", "Θ"],
    ["Ι", "Κ", "Λ", "Μ", "Ν", "Ξ", "Π", "Ρ"],
    ["Σ", "Τ", "Υ", "Φ", "Χ", "Ψ", "Ω"]
]

trig_keys_new = [
    ["sin", "cos", "tan", "sec", "csc", "cot"],
    ["asin", "acos", "atan", "asec", "acsc", "acot"],
    ["sinh", "cosh", "tanh", "asinh", "acosh", "atanh"]
]

relations_keys = [
    ["<", ">", "≤", "≥", "=", "≠"],
    ["→", "←", "↑", "↓", "↔", "⇒"],
    ["+", "-", "*", "/", "^", "%"]
]

sets_logic_keys = [
    ["∈", "∉", "⊂", "⊃", "⊆", "⊇"],
    ["∩", "∪", "\\", "∅", "𝕌", "ℙ"],
    ["∀", "∃", "∄", "∧", "∨", "¬"]
]

calculus_keys = [
    ["∑", "∏", "∫", "∬", "∭", "∮"],
    ["d/dx", "∂/∂x", "∇", "Δ", "lim", "∞"],
    ["diff(", "integrate(", "limit(", "series(", "solve("]
]

subscripts_keys = [
    ["x_1", "x_2", "y_1", "y_2", "z_1", "z_2"],
    ["pi", "e", "I", "h", "G", "c"],
    ["k_B", "N_A", "mu_0", "epsilon_0", "sigma"]
]

numeric_pad_keys = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "+", "^"]
]

keyboard_tabs = st.tabs([
    "Basic", 
    "αβγ", 
    "ABΓ", 
    "sin cos", 
    "≥ ÷ →", 
    "x ∈ ℂ ∀", 
    "∑ ∫ ∏", 
    "H₂O", 
    "🖩"
])

with keyboard_tabs[0]:
    for row_idx, row in enumerate(basic_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_basic_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[1]:
    for row_idx, row in enumerate(greek_lower_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_glower_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[2]:
    for row_idx, row in enumerate(greek_upper_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_gupper_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[3]:
    for row_idx, row in enumerate(trig_keys_new):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_trig_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[4]:
    for row_idx, row in enumerate(relations_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_rel_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[5]:
    for row_idx, row in enumerate(sets_logic_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_sets_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[6]:
    for row_idx, row in enumerate(calculus_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_calc_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[7]:
    for row_idx, row in enumerate(subscripts_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_sub_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

with keyboard_tabs[8]:
    for row_idx, row in enumerate(numeric_pad_keys):
        cols = st.columns(len(row))
        for col_idx, key in enumerate(row):
            cols[col_idx].button(key, key=f"kb_num_{row_idx}_{col_idx}", on_click=append_text, args=(key,), use_container_width=True)

# ----------------- PARSING MATH ENGINE -----------------
# Synchronize function inputs from dynamic list and build expressions
exprs = []
for idx in range(len(st.session_state.function_inputs)):
    state_key = f"func_val_{idx}"
    if state_key in st.session_state:
        st.session_state.function_inputs[idx] = st.session_state[state_key]
        
    f_str_clean = st.session_state.function_inputs[idx].strip()
    if not f_str_clean:
        continue
        
    processed_str = f_str_clean.replace('^', '**').replace('ln(', 'log(')
    try:
        expr = safe_parse(processed_str)
        exprs.append(expr)
    except ValueError as val_err:
        st.error(f"⚠️ **Security Block in Function {idx+1}**: {val_err}")
        st.stop()
    except Exception as parse_err:
        st.error(f"❌ **Parser Error in Function {idx+1} ('{f_str_clean}')**: Could not interpret. Ensure parentheses are balanced and operators are valid. Details: `{parse_err}`")
        st.stop()

if not exprs:
    st.info("💡 Graphing is idle. Start by defining a function field above!")
    st.stop()

# Extract Variables and Bind Parameters dynamically
free_syms = set()
for expr in exprs:
    free_syms.update(expr.free_symbols)

x_sym = sp.Symbol('x')
y_sym = sp.Symbol('y')

# Identify parameter variables (any free variables that are NOT the plotting variables)
if mode == "Single Variable":
    param_syms = [s for s in free_syms if s.name != 'x']
else:
    param_syms = [s for s in free_syms if s.name not in ('x', 'y')]

# Bind Sidebar Sliders for parameters dynamically
params_values = {}
if param_syms:
    st.sidebar.markdown("### ⚙️ Parameter Configuration")
    st.sidebar.caption("Fine-tune variables in your formula:")
    for sym in sorted(param_syms, key=lambda s: s.name):
        params_values[sym] = st.sidebar.slider(
            label=f"Parameter {sym.name}",
            min_value=-10.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key=f"slider_{sym.name}"
        )

# ----------------- 2D SINGLE VARIABLE PLOTTING -----------------
if mode == "Single Variable":
    # Selection for Calculus Reference if multiple functions are present
    if len(exprs) > 1:
        st.markdown("### 📊 Calculus Analysis Target")
        selected_index = st.selectbox(
            "Select Function for Calculus & Symbolic Reference:",
            options=range(len(exprs)),
            format_func=lambda idx: f"f{chr(8320+idx+1)}(x) = {sp.pretty(exprs[idx], use_unicode=True)}"
        )
    else:
        selected_index = 0

    active_eval_expr = exprs[selected_index].subs(params_values)

    # Calculate Calculus elements
    deriv_expr = sp.diff(active_eval_expr, x_sym)
    
    try:
        integ_expr = sp.integrate(active_eval_expr, x_sym)
    except Exception:
        integ_expr = None

    # Calculus Details Panels
    st.markdown("### 📊 Calculus & Symbolic Reference")
    
    col_deriv_opt, col_integ_opt = st.columns(2)
    n = selected_index + 1
    with col_deriv_opt:
        plot_deriv = st.checkbox(f"Overlay Derivative: f\u2032{chr(8320+n)}(x)", value=False, key="check_deriv")
    with col_integ_opt:
        # Only allow overlay if we got a closed-form integral
        has_closed_integral = integ_expr is not None and not integ_expr.has(sp.Integral)
        plot_integ = st.checkbox(f"Overlay Integral: \u222Bf{chr(8320+n)}(x)dx", value=False, key="check_integ", disabled=not has_closed_integral)
        if not has_closed_integral:
            st.caption("(Disabled: Analytical integration has no simple closed form)")

    col_ref_f, col_ref_df, col_ref_int = st.columns(3)
    with col_ref_f:
        with st.container(border=True):
            latex_repr = sp.latex(active_eval_expr)
            st.latex(rf"\textrm{{Original }} f_{{{n}}}(x)")
            st.latex(rf"f_{{{n}}}(x) = {latex_repr}")

    with col_ref_df:
        with st.container(border=True):
            deriv_repr = sp.latex(deriv_expr)
            st.latex(rf"\textrm{{Derivative }} f'_{{{n}}}(x)")
            st.latex(rf"f'_{{{n}}}(x) = {deriv_repr}")

    with col_ref_int:
        with st.container(border=True):
            st.latex(rf"\textrm{{Integral of }} f_{{{n}}}(x)")
            if has_closed_integral:
                integ_repr = sp.latex(integ_expr)
                st.latex(rf"\int f_{{{n}}}(x)\, dx = {integ_repr}")
            else:
                st.info("No closed-form integral found.")

    # Graph Evaluation
    x_vals = np.linspace(x_min, x_max, resolution)
    
    # 2D Plotter
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Dark Theming styles for Matplotlib
    fig.patch.set_facecolor('#0d131f')
    ax.set_facecolor('#111827')
    
    # Colors for main functions
    colors = ['#06b6d4', '#a855f7', '#eab308', '#ec4899', '#3b82f6', '#14b8a6']

    # Evaluate and Plot all main functions
    for idx, expr in enumerate(exprs):
        try:
            curr_eval_expr = expr.subs(params_values)
            f_func = sp.lambdify(x_sym, curr_eval_expr, modules=['numpy'])
            y_vals = f_func(x_vals)
            if isinstance(y_vals, (int, float)):
                y_vals = np.full_like(x_vals, y_vals)
                
            lbl = f"$f_{{{idx+1}}}(x) = {sp.latex(curr_eval_expr)}$"
            ax.plot(x_vals, y_vals, label=lbl, color=graph_colors[idx % len(graph_colors)], linewidth=2.5)
        except Exception as e:
            st.error(f"Error evaluating f{chr(8320+idx+1)}(x) curve: {e}")
        
    # Derivative Overlay Evaluation
    if plot_deriv:
        try:
            df_func = sp.lambdify(x_sym, deriv_expr, modules=['numpy'])
            dy_vals = df_func(x_vals)
            if isinstance(dy_vals, (int, float)):
                dy_vals = np.full_like(x_vals, dy_vals)
                
            ax.plot(x_vals, dy_vals, label=f"$f'_{{{selected_index+1}}}(x)$", color='#ef4444', linewidth=2.0, linestyle='--')
        except Exception as e:
            st.warning(f"Could not render derivative: {e}")
            
    # Integral Overlay Evaluation
    if plot_integ and has_closed_integral:
        try:
            int_func = sp.lambdify(x_sym, integ_expr, modules=['numpy'])
            iy_vals = int_func(x_vals)
            if isinstance(iy_vals, (int, float)):
                iy_vals = np.full_like(x_vals, iy_vals)
                
            ax.plot(x_vals, iy_vals, label=f"$\\int f_{{{selected_index+1}}}(x)\\, dx$", color='#10b981', linewidth=2.0, linestyle='-.')
        except Exception as e:
            st.warning(f"Could not render integral: {e}")
            
    # Style Axes & Grid lines
    ax.grid(True, color='#374151', linestyle=':', linewidth=0.8)
    ax.axhline(0, color='#4b5563', linewidth=1.2)
    ax.axvline(0, color='#4b5563', linewidth=1.2)
    
    # Text colors
    ax.tick_params(colors='#94a3b8', labelsize=10)
    ax.xaxis.label.set_color('#cbd5e1')
    ax.yaxis.label.set_color('#cbd5e1')
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.legend(facecolor='#1f2937', edgecolor='#374151', labelcolor='#cbd5e1', loc='best', framealpha=0.9)
    
    # Display in Streamlit
    st.markdown("### 📉 2D Function Visualizer")
    st.pyplot(fig, use_container_width=True)

# ----------------- 3D MULTIVARIABLE PLOTTING -----------------
else:
    # Selection for Calculus Reference if multiple functions are present
    if len(exprs) > 1:
        st.markdown("### 📊 Partial Derivatives Target")
        selected_index_3d = st.selectbox(
            "Select Function for Partial Derivatives Reference:",
            options=range(len(exprs)),
            format_func=lambda idx: f"f{chr(8320+idx+1)}(x, y) = {sp.pretty(exprs[idx], use_unicode=True)}"
        )
    else:
        selected_index_3d = 0

    active_eval_expr_3d = exprs[selected_index_3d].subs(params_values)

    # Calculus Elements (Partial Derivatives)
    deriv_x = sp.diff(active_eval_expr_3d, x_sym)
    deriv_y = sp.diff(active_eval_expr_3d, y_sym)

    m = selected_index_3d + 1
    st.markdown("### 📊 Partial Derivatives Reference")
    col_ref_dx, col_ref_dy = st.columns(2)

    with col_ref_dx:
        with st.container(border=True):
            deriv_x_repr = sp.latex(deriv_x)
            st.latex(rf"\textrm{{Partial w.r.t. }} x")
            st.latex(rf"\frac{{\partial f_{{{m}}}}}{{\partial x}} = {deriv_x_repr}")

    with col_ref_dy:
        with st.container(border=True):
            deriv_y_repr = sp.latex(deriv_y)
            st.latex(rf"\textrm{{Partial w.r.t. }} y")
            st.latex(rf"\frac{{\partial f_{{{m}}}}}{{\partial y}} = {deriv_y_repr}")

    st.markdown("### 🗳️ Select Surface to Graph")
    plot_surface_choice = st.selectbox(
        "Choose rendering surface:",
        ["All Main Functions f(x, y)", "Partial Derivative w.r.t x (df/dx) of chosen function", "Partial Derivative w.r.t y (df/dy) of chosen function"]
    )
    
    # Calculate active expression for 3D plot based on choice
    if "All Main Functions" in plot_surface_choice:
        active_expr = None
        label_expr = ", ".join([f"f_{idx+1}(x,y)" for idx in range(len(exprs))])
    elif "w.r.t x" in plot_surface_choice:
        active_expr = deriv_x
        label_expr = f"z = \\frac{{\\partial f_{{{selected_index_3d+1}}}}}{{\\partial x}}"
    else:
        active_expr = deriv_y
        label_expr = f"z = \\frac{{\\partial f_{{{selected_index_3d+1}}}}}{{\\partial y}}"

    # Evaluate 3D Arrays
    x_array = np.linspace(x_min, x_max, resolution)
    y_array = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(x_array, y_array)

    # Create 3D Plot
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Dark colors setup matching app design
    fig.patch.set_facecolor('#0d131f')
    ax.set_facecolor('#0d131f')

    # Text, Grid, and Axis colors
    ax.tick_params(colors='#94a3b8', labelsize=9)
    ax.xaxis.label.set_color('#cbd5e1')
    ax.yaxis.label.set_color('#cbd5e1')
    ax.zaxis.label.set_color('#cbd5e1')
    
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_zlabel('z', fontsize=11)

    # Sleek dark semi-transparent panes
    ax.xaxis.set_pane_color((0.08, 0.11, 0.18, 0.6))
    ax.yaxis.set_pane_color((0.08, 0.11, 0.18, 0.6))
    ax.zaxis.set_pane_color((0.08, 0.11, 0.18, 0.6))

    # Grid style
    ax.grid(True, color='#374151', linestyle=':', linewidth=0.5)

    # Set View
    ax.view_init(elev=elev_angle, azim=azim_angle)

    # Render Plot Surface
    try:
        from matplotlib.colors import LinearSegmentedColormap
        
        # Helper to generate beautiful custom colormaps fading from dark background to chosen color
        def create_custom_cmap(hex_color):
            try:
                return LinearSegmentedColormap.from_list("custom_cmap", ["#0d131f", hex_color])
            except Exception:
                return "viridis"
        
        if active_expr is None:
            # Render all main functions
            for idx, expr in enumerate(exprs):
                curr_eval_expr = expr.subs(params_values)
                f_func_3d = sp.lambdify((x_sym, y_sym), curr_eval_expr, modules=['numpy'])
                Z = f_func_3d(X, Y)
                if isinstance(Z, (int, float)):
                    Z = np.full_like(X, Z)
                
                # Create glowing hologram colormap using chosen hex color from color picker
                hex_color = graph_colors[idx % len(graph_colors)]
                cmap = create_custom_cmap(hex_color)
                alpha_val = 0.6 if len(exprs) > 1 else 0.9
                
                if surf_style == "Solid Surface":
                    surf = ax.plot_surface(X, Y, Z, cmap=cmap, edgecolor='none', alpha=alpha_val)
                    if idx == 0:
                        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
                        cbar.ax.yaxis.set_tick_params(color='#94a3b8')
                        plt.setp(cbar.ax.get_yticklabels(), color='#cbd5e1')
                        cbar.outline.set_edgecolor('#374151')
                elif surf_style == "Wireframe":
                    stride = max(1, resolution // 20)
                    ax.plot_wireframe(X, Y, Z, cmap=cmap, rstride=stride, rcount=30, ccount=30, linewidth=0.8, alpha=alpha_val)
                else: # Contours Only
                    ax.contour3D(X, Y, Z, 40, cmap=cmap, alpha=alpha_val)
            
            st.markdown(f"### 🏔️ 3D Surface Visualizer: {label_expr}")
        else:
            # Render single chosen partial derivative
            f_func_3d = sp.lambdify((x_sym, y_sym), active_expr, modules=['numpy'])
            Z = f_func_3d(X, Y)
            if isinstance(Z, (int, float)):
                Z = np.full_like(X, Z)
                
            if surf_style == "Solid Surface":
                surf = ax.plot_surface(X, Y, Z, cmap=colormap, edgecolor='none', alpha=0.9)
                cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
                cbar.ax.yaxis.set_tick_params(color='#94a3b8')
                plt.setp(cbar.ax.get_yticklabels(), color='#cbd5e1')
                cbar.outline.set_edgecolor('#374151')
            elif surf_style == "Wireframe":
                stride = max(1, resolution // 20)
                ax.plot_wireframe(X, Y, Z, cmap=colormap, rstride=stride, rcount=30, ccount=30, linewidth=0.8)
            else: # Contours Only
                ax.contour3D(X, Y, Z, 40, cmap=colormap)
            
            st.markdown(f"### 🏔️ 3D Surface Visualizer: ${label_expr}$")
            
        st.pyplot(fig, use_container_width=True)
        
    except Exception as plot_err:
        st.error(f"Error rendering the 3D surface: {plot_err}")

# ----------------- FOOTER SECTION -----------------
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 28px 36px;
            margin-top: 24px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            text-align: center;">
    <p style="margin: 0 0 6px 0; font-size: 1.1rem; font-weight: 600;
              background: linear-gradient(135deg, #60a5fa, #c084fc);
              -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Built with 🤍 by AS.Dev
    </p>
    <p style="margin: 0 0 16px 0; color: #64748b; font-size: 0.85rem;">
        Powered by Streamlit · SymPy · Matplotlib · NumPy
    </p>
    <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
        <a href="https://as-developerportfolio.web.app/" target="_blank"
           style="display: inline-flex; align-items: center; gap: 8px;
                  background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.3);
                  color: #60a5fa; padding: 10px 22px; border-radius: 12px;
                  text-decoration: none; font-size: 0.9rem; font-weight: 500;
                  transition: all 0.25s ease;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            Portfolio
        </a>
        <a href="https://github.com/AS-Developer-17/Desmos-Clone" target="_blank"
           style="display: inline-flex; align-items: center; gap: 8px;
                  background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12);
                  color: #e2e8f0; padding: 10px 22px; border-radius: 12px;
                  text-decoration: none; font-size: 0.9rem; font-weight: 500;
                  transition: all 0.25s ease;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            GitHub Repo
        </a>
    </div>
    <p style="margin: 16px 0 0 0; color: #475569; font-size: 0.75rem;">
        © 2025 AS.Dev — All rights reserved
    </p>
</div>
""", unsafe_allow_html=True)