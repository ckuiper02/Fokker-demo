import streamlit as st

# ==========================================
# --- CONFIGURATION SECTION ---
# ==========================================

# 1. Global Defaults for Substeps (unless specific overrides are needed)
#    Formula: (Base + (Per_Sample * Sample_Count)) * Complexity_Multiplier
SUBSTEP_CONFIG = {
    "base_hours": 0.0,          # Usually 0 setup for a specific substep execution
    "hours_per_sample": 0.5,    # Time taken per unit
    "complexity_multipliers": { # Multiplier applied to the total calculation
        "Easy": 1.0,
        "Medium": 1.25,
        "High": 1.5
    }
}

# 2. Definition of Substep Lists
EXECUTION_SUBSTEPS = [
    "Thermal Cycling/Thermal Shock", "Vibration", "Fluid Susceptibility",
    "Salt Fog", "Seal Integrity", "Discontinuity Monitoring System"
]

ATP_SUBSTEPS = [
    "Visual Inspection", "Partial Discharge", "Insulation Resistance",
    "Dielectric Withstanding Voltage", "Electrical Bonding Resistance", "Tear Down Inspection"
]

# 3. MASTER CONFIGURATION: The "Recipe" for every step
#    You can now tune how each step behaves individually.
#    - 'base': Fixed hours (Project Management, Setup)
#    - 'per_sample': Hours added for every sample (Testing, Inspection)
#    - 'multipliers': Dictionary for {Easy, Medium, High} impact
#    - 'substeps': List of substeps or None

# A helper to keep the dict clean. Default multipliers are 1.0 (no effect).
DEFAULT_MULTS = {"Easy": 1.0, "Medium": 1.0, "High": 1.0}
# A helper for steps heavily affected by complexity (e.g. 20% increase for med, 50% for high)
COMPLEX_MULTS = {"Easy": 1.0, "Medium": 1.2, "High": 1.5}

PROJECT_STEPS = {
    "Conformity Delegation": {
        "base": 2.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "Creation of UUT": {
        "base": 2.0, "per_sample": 1.0, "multipliers": COMPLEX_MULTS, "substeps": None
    },
    "Creation of Test Plan": {
        "base": 4.0, "per_sample": 0.0, "multipliers": COMPLEX_MULTS, "substeps": None
    },
    "Test Facility Selection": {
        "base": 2.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "NDA": {
        "base": 1.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "Subcontract": {
        "base": 2.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "TRR 1": {
        "base": 3.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "UUT Conformity": {
        "base": 1.0, "per_sample": 0.5, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "Pre-ATP": {
        "base": 1.0, "per_sample": 0.0, "multipliers": COMPLEX_MULTS, "substeps": ATP_SUBSTEPS
    },
    "Test Set-up": {
        "base": 4.0, "per_sample": 0.0, "multipliers": COMPLEX_MULTS, "substeps": None
    },
    "TRR 2": {
        "base": 2.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "Test Execution": {
        # High impact from samples and complexity here
        "base": 2.0, "per_sample": 0.0, "multipliers": COMPLEX_MULTS, "substeps": EXECUTION_SUBSTEPS
    },
    "Post-ATP": {
        "base": 1.0, "per_sample": 0.0, "multipliers": COMPLEX_MULTS, "substeps": ATP_SUBSTEPS
    },
    "Test Reporting": {
        "base": 4.0, "per_sample": 1.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
    "Archiving": {
        "base": 1.0, "per_sample": 0.0, "multipliers": DEFAULT_MULTS, "substeps": None
    },
}

# ==========================================
# --- HELPER FUNCTION ---
# ==========================================

def calculate_hours(config, num_samples, complexity):
    """Calculates hours for a single item based on configuration."""
    base = config.get("base", config.get("base_hours", 0))
    per_sample = config.get("per_sample", config.get("hours_per_sample", 0))
    multipliers = config.get("multipliers", config.get("complexity_multipliers", DEFAULT_MULTS))
    
    # Formula: (Fixed Time + (Time per sample * N samples)) * Complexity Factor
    raw_hours = base + (per_sample * num_samples)
    final_hours = raw_hours * multipliers[complexity]
    return final_hours

# ==========================================
# --- MAIN APP UI ---
# ==========================================

st.title("⏱️ Advanced Test Estimator")

# --- GLOBAL INPUTS ---
st.sidebar.header("Project Parameters")
st.sidebar.markdown("These settings influence calculations for steps sensitive to volume and difficulty.")

num_samples = st.sidebar.number_input("Number of Samples (UUTs)", min_value=1, value=1, step=1)
complexity = st.sidebar.selectbox("Sample Complexity", options=["Easy", "Medium", "High"])

st.sidebar.divider()
st.sidebar.info(f"**Current Settings:**\n\nSamples: {num_samples}\n\nComplexity: {complexity}")

# --- MAIN LIST ---
st.subheader("Select Process Steps")

total_hours = 0.0

# Iterate through steps
for step_name, config in PROJECT_STEPS.items():
    
    # Calculate what this step would cost if selected (for display purposes)
    estimated_step_cost = calculate_hours(config, num_samples, complexity)
    
    col_check, col_info = st.columns([3, 1])
    
    with col_check:
        is_selected = st.checkbox(f"**{step_name}**", key=step_name)
        
        # Logic if selected
        if is_selected:
            total_hours += estimated_step_cost
            
            # --- SUBSTEP LOGIC ---
            if config["substeps"]:
                selected_subs = st.multiselect(
                    f"Select {step_name} activities:",
                    options=config["substeps"],
                    key=f"{step_name}_sub"
                )
                
                # Calculate substep cost using the SUBSTEP_CONFIG defaults
                # (You could also make specific configs for specific substeps if needed)
                for sub in selected_subs:
                    sub_cost = calculate_hours(SUBSTEP_CONFIG, num_samples, complexity)
                    total_hours += sub_cost
                    estimated_step_cost += sub_cost # Add to local display var
                    
    # Display the dynamic cost of this step (live update based on sidebar)
    with col_info:
        if is_selected:
            st.caption(f"{estimated_step_cost:.1f} hrs")

# ==========================================
# --- RESULTS ---
# ==========================================

st.divider()
st.subheader("Estimation Result")

# Display breakdown
c1, c2, c3 = st.columns(3)
c1.metric("Samples", num_samples)
c2.metric("Complexity", complexity)
c3.metric("Total Hours", f"{total_hours:.2f}", delta_color="normal")

# Visual bar for context
if total_hours > 0:
    st.progress(min(total_hours / 200, 1.0)) # Assuming 200 is a 'big' project