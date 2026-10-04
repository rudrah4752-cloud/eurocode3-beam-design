import math
import pandas as pd
import streamlit as st

# ==========================================
# PAGE CONFIGURATION & HEADER
# ==========================================
st.set_page_config(
    page_title="Eurocode 3 Steel Beam Design Tool",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏗️ Eurocode 3 Steel Beam Analysis & Design Tool")
st.caption(
    "Final Year Research Project — Structural Steel Beam Verification according to BS EN 1993"
)

st.info(
    "💡 **Instructions:** Adjust the design inputs in the left sidebar to analyze different beam configurations. Review the tabs below for detailed design checks."
)

# ==========================================
# 1. SIDEBAR INPUTS
# ==========================================
# Beam Configuration
st.sidebar.header("1. Beam Configuration")
beam_type = st.sidebar.radio(
    "Select Beam Support Condition:", ["Restrained Beam", "Unrestrained Beam"]
)

# Loading Type Selection
st.sidebar.header("2. Span & Applied Loads")
loading_type = st.sidebar.selectbox(
    "Select Loading Type",
    [
        "1. FULL UDL",
        "2. PARTIAL UDL",
        "3. POINT LOAD",
        "4. TRIANGULAR",
        "5. INVERTED TRIANGULAR",
        "6. TRAPEZOIDAL",
        "7. UDL + POINT LOAD",
    ],
)

# Load & Span Variables
L = st.sidebar.number_input(
    "Span Length, L (m):", min_value=0.5, max_value=30.0, value=8.0, step=0.5
)
Gk = st.sidebar.number_input(
    "UDL Dead Load, Gk (kN/m):", min_value=0.0, value=25.0, step=1.0
)
Qk = st.sidebar.number_input(
    "UDL Live Load, Qk (kN/m):", min_value=0.0, value=35.0, step=1.0
)

PL_Gk = st.sidebar.number_input(
    "Point Load Dead, PL Gk (kN):", min_value=0.0, value=0.0, step=1.0
)
PL_Qk = st.sidebar.number_input(
    "Point Load Live, PL Qk (kN):", min_value=0.0, value=0.0, step=1.0
)

# Steel Section Properties
st.sidebar.header("3. Steel Section Properties")
fy = st.sidebar.selectbox(
    "Steel Grade / Yield Strength, fy (MPa):", [275, 355, 460], index=1
)
h = st.sidebar.number_input(
    "Total Depth, h (mm):", min_value=10.0, value=607.6, step=1.0
)
b = st.sidebar.number_input(
    "Flange Width, b (mm):", min_value=10.0, value=228.2, step=1.0
)
tw = st.sidebar.number_input(
    "Web Thickness, tw (mm):", min_value=1.0, value=11.1, step=0.1
)
tf = st.sidebar.number_input(
    "Flange Thickness, tf (mm):", min_value=1.0, value=17.3, step=0.1
)
r = st.sidebar.number_input(
    "Root Radius, r (mm):", min_value=0.0, value=12.7, step=0.1
)
A = st.sidebar.number_input(
    "Cross-sectional Area, A (cm²):", min_value=1.0, value=144.0, step=1.0
)
Wpl = st.sidebar.number_input(
    "Plastic Section Modulus, Wpl,y (cm³):",
    min_value=1.0,
    value=1450.0,
    step=10.0,
)
Iz = st.sidebar.number_input(
    "Second Moment of Area, Iz (cm4):",
    min_value=1.0,
    value=3390.0,
    step=10.0,
)

# Unrestrained Parameters
if beam_type == "Unrestrained Beam":
    st.sidebar.header("4. Buckling / LTB Parameters")
    Lcr = st.sidebar.number_input(
        "Unrestrained Length, Lcr (mm):",
        min_value=100.0,
        value=4000.0,
        step=100.0,
    )
    IT = st.sidebar.number_input(
        "Torsional Constant, IT (cm4):",
        min_value=1.0,
        value=170000.0,
        step=10000.0,
    )
    Iw = st.sidebar.number_input(
        "Warping Constant, Iw (dm6):", min_value=0.0, value=1.2, step=0.1
    )

# ==========================================
# 2. DYNAMIC ACTION COMPUTATIONS (Ved & Med)
# ==========================================
w_ed = 1.35 * Gk + 1.5 * Qk
P_ed = 1.35 * PL_Gk + 1.5 * PL_Qk

if "1. FULL UDL" in loading_type:
    Ved = (w_ed * L) / 2
    Med = (w_ed * (L**2)) / 8
elif "2. PARTIAL UDL" in loading_type:
    a = 4.0  # Loaded length (m)
    Ved = (w_ed * a) / 2
    Med = (w_ed * a / 8) * (2 * L - a)
elif "3. POINT LOAD" in loading_type:
    Ved = P_ed / 2
    Med = (P_ed * L) / 4
elif "4. TRIANGULAR" in loading_type:
    Ved = (w_ed * L) / 4
    Med = (w_ed * (L**2)) / (12 * (3**0.5))
elif "5. INVERTED TRIANGULAR" in loading_type:
    Ved = (w_ed * L) / 4
    Med = (w_ed * (L**2)) / 12
elif "6. TRAPEZOIDAL" in loading_type:
    a = 3.0  # Flat top length (m)
    Ved = (w_ed * (L + a)) / 4
    Med = (w_ed / 24) * (3 * (L**2) - 4 * (a**2))
elif "7. UDL + POINT LOAD" in loading_type:
    Ved = ((w_ed * L) / 2) + (P_ed / 2)
    Med = ((w_ed * (L**2)) / 8) + ((P_ed * L) / 4)

# Dynamic Display Summary
st.subheader("1. Design Actions Summary")
col_v, col_m = st.columns(2)
col_v.metric("Design Shear Force (V_ed)", f"{Ved:.2f} kN")
col_m.metric("Design Bending Moment (M_ed)", f"{Med:.2f} kNm")

# ==========================================
# 3. EUROCODE 3 DESIGN VERIFICATIONS
# ==========================================
# Shear Resistance Check
st.subheader("2. Shear Resistance Check")
Av = (A * 100 - 2 * b * tf + (tw + 2 * r) * tf)
Vpl_Rd = (Av * (fy / (3**0.5))) / 1000  # kN
shear_check = Ved <= Vpl_Rd

col_s1, col_s2 = st.columns(2)
col_s1.write(f"Shear Area ($A_v$): **{Av:.2f} mm²**")
col_s1.write(f"Plastic Shear Resistance ($V_{{pl,Rd}}$): **{Vpl_Rd:.2f} kN**")

if shear_check:
    col_s2.success("✅ PASS: Shear Resistance is Adequate")
else:
    col_s2.error("❌ FAIL: Shear Resistance Exceeded")

# Bending Resistance Check
st.subheader("3. Moment Resistance Check")
Mc_Rd = (Wpl * 1000 * fy) / 10**6  # kNm
bending_check = Med <= Mc_Rd

col_b1, col_b2 = st.columns(2)
col_b1.write(f"Plastic Moment Resistance ($M_{{c,Rd}}$): **{Mc_Rd:.2f} kNm**")

if bending_check:
    col_b2.success("✅ PASS: Moment Resistance is Adequate")
else:
    col_b2.error("❌ FAIL: Moment Resistance Exceeded")

# Lateral Torsional Buckling (LTB) Check for Unrestrained Beams
if beam_type == "Unrestrained Beam":
    st.subheader("4. Lateral-Torsional Buckling (LTB) Check")
    C1 = 1.00
    E_Nmm = 210000
    G_Nmm = 81000

    Iz_mm = Iz * 10000
    IT_mm = IT * 10000
    Iw_mm = Iw * 10**12

    term1 = (C1 * (math.pi**2) * E_Nmm * Iz_mm) / (Lcr**2)
    term2 = math.sqrt((Iw_mm / Iz_mm) + (((Lcr**2) * G_Nmm * IT_mm) / ((math.pi**2) * E_Nmm * Iz_mm)))
    Mcr = (term1 * term2) / 10**6

    lambda_LT = math.sqrt((Wpl * 1000 * fy) / (Mcr * 10**6))
    hb_ratio = h / b
    buckling_curve = "a" if hb_ratio <= 2 else "b"
    alpha_LT = 0.21 if buckling_curve == "a" else 0.34

    phi_LT = 0.5 * (1 + alpha_LT * (lambda_LT - 0.2) + (lambda_LT**2))
    chi_LT = 1 / (phi_LT + math.sqrt(phi_LT**2 - lambda_LT**2))
    if chi_LT > 1.0:
        chi_LT = 1.0

    Mb_Rd = round((chi_LT * Wpl * 1000 * fy / 1.0) / 10**6, 2)
    ltb_check = Med <= Mb_Rd

    col_l1, col_l2 = st.columns(2)
    col_l1.write(f"Elastic Critical Moment ($M_{{cr}}$): **{Mcr:.2f} kNm**")
    col_l1.write(fr"Slenderness ($\lambda_{{LT}}$): **{lambda_LT:.3f}**")
    col_l1.write(fr"Reduction Factor ($\chi_{{LT}}$): **{chi_LT:.3f}**")

    col_l2.metric("Buckling Moment Resistance (M_b,Rd)", f"{Mb_Rd:.2f} kNm")
    if ltb_check:
        col_l2.success("✅ PASS: LTB Resistance is Adequate")
    else:
        col_l2.error("❌ FAIL: LTB Resistance Exceeded")

# Overall Verification Summary
st.subheader("5. Overall Design Summary")
if beam_type == "Restrained Beam":
    all_passed = shear_check and bending_check
else:
    all_passed = shear_check and bending_check and ltb_check

if all_passed:
    st.success("🎉 ALL CHECKS PASSED: The selected steel beam section is STRUCTURALLY ADEQUATE.")
else:
    st.error("⚠️ CHECKS FAILED: Please select a larger section or reduce span/loading.")