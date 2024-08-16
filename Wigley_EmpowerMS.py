import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration for better aesthetics
st.set_page_config(page_title="EmpowerMS: Risk Reduction Tool", layout="wide")

# Title and description
st.title("EmpowerMS: Risk Reduction Tool for Black Persons with MS")
st.markdown("""
This tool is designed to help Black persons with multiple sclerosis (BpwMS) understand their risk of disease progression and how lifestyle changes, such as smoking cessation, can significantly reduce that risk. 
By empowering you with this knowledge, we hope to support you in making informed decisions about your health.
""")

# Sidebar for user inputs
st.sidebar.header("Input Parameters")

# Coefficients from the logistic regression model (log-odds)
log_odds_coefficients = {
    "Intercept": 0.488,
    "BpwMS": 4.8613,
    "Current Smoker": 16.8601,
    "BpwMS * Current Smoker": -18.5033,
    "Pack-Years": 0.1531,
    "BpwMS * Pack-Years": -0.496,
    "Age at Baseline": 0.0056,
    "Sex (Male)": -2.2452,
    "Follow-up Interval": 0.3507
}

# Function to calculate the risk and contributions
def calculate_risk(inputs):
    log_odds = log_odds_coefficients["Intercept"]
    
    for key in inputs:
        log_odds += log_odds_coefficients[key] * inputs[key]
    
    odds = np.exp(log_odds)
    probability = odds / (1 + odds)
    risk_of_worsening = 1 - probability
    return risk_of_worsening

# Function to calculate the benefit of smoking cessation
def calculate_smoking_cessation_benefit(inputs):
    # Current risk
    current_risk = calculate_risk(inputs)
    
    # Risk if the individual quits smoking
    inputs_no_smoking = inputs.copy()
    inputs_no_smoking["Current Smoker"] = 0
    inputs_no_smoking["BpwMS * Current Smoker"] = 0
    risk_no_smoking = calculate_risk(inputs_no_smoking)
    
    # Relative risk reduction
    relative_risk_reduction = (current_risk - risk_no_smoking) / current_risk
    return relative_risk_reduction * 100, current_risk * 100, risk_no_smoking * 100

# Collecting user inputs
bpwms = st.sidebar.selectbox("BpwMS", options=[1, 0], format_func=lambda x: "Yes" if x == 1 else "No", index=0)
current_smoker = st.sidebar.selectbox("Current Smoker", options=[1, 0], format_func=lambda x: "Yes" if x == 1 else "No", index=0)
pack_years = st.sidebar.number_input("Pack-Years", min_value=0.0, step=0.1, value=2.5)
age_at_baseline = st.sidebar.number_input("Age at Baseline", min_value=0, step=1, value=30)
sex_male = st.sidebar.selectbox("Sex", options=[0, 1], format_func=lambda x: "Male" if x == 1 else "Female")
follow_up_interval = st.sidebar.number_input("Follow-up Interval", min_value=0.0, step=0.1, value=1.0)

# Calculating interaction terms
bpwms_current_smoker = bpwms * current_smoker
bpwms_pack_years = bpwms * pack_years

# Preparing inputs for calculation
inputs = {
    "BpwMS": bpwms,
    "Current Smoker": current_smoker,
    "BpwMS * Current Smoker": bpwms_current_smoker,
    "Pack-Years": pack_years,
    "BpwMS * Pack-Years": bpwms_pack_years,
    "Age at Baseline": age_at_baseline,
    "Sex (Male)": sex_male,
    "Follow-up Interval": follow_up_interval
}

# Check if the user is not BpwMS or not a Current Smoker
if bpwms == 0 or current_smoker == 0:
    st.warning("This calculator is specifically designed for Black persons with multiple sclerosis (BpwMS) who are current smokers. The results may not be accurate for individuals who do not belong to this population.")
else:
    # Button to perform calculation
    if st.sidebar.button("Calculate Risk and Benefits"):
        # Calculating risk and smoking cessation benefit
        relative_risk_reduction, current_risk, risk_no_smoking = calculate_smoking_cessation_benefit(inputs)
        
        st.subheader(f"Current Risk of Worsening: {current_risk:.2f}%")
        st.subheader(f"Risk of Worsening if Quit Smoking: {risk_no_smoking:.2f}%")
        st.subheader(f"Relative Risk Reduction from Smoking Cessation: {relative_risk_reduction:.2f}%")
        
        # Plotting the relative risk reduction as a pie chart
        fig, ax = plt.subplots(figsize=(6, 6))
        labels = ['Remaining Risk After Quitting', 'Risk Reduction']
        sizes = [100 - relative_risk_reduction, relative_risk_reduction]
        colors = ['orange', 'lightgreen']
        explode = (0, 0.1)  # Explode the risk reduction slice
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title('Relative Risk Reduction from Smoking Cessation')
        st.pyplot(fig)

