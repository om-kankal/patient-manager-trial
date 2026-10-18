import streamlit as st
import requests

# FastAPI Backend URL
BASE_URL = "http://127.0.0.1:8000"

# Page Configuration
st.set_page_config(
    page_title="Patient Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Neumorphic CSS Styling
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #e0e5ec;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #4a5568;
    }
    
    /* Neumorphic Card Styling */
    .neumorphic-card {
        background: #e0e5ec;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 9px 9px 16px #a3b1c6, -9px -9px 16px #ffffff;
        margin-bottom: 25px;
    }
    
    .neumorphic-inset {
        background: #e0e5ec;
        padding: 15px;
        border-radius: 12px;
        box-shadow: inset 4px 4px 8px #a3b1c6, inset -4px -4px 8px #ffffff;
        margin-bottom: 15px;
    }

    /* Headers */
    h1, h2, h3 {
        color: #2d3748;
        font-weight: 700;
    }

    /* Buttons */
    .stButton>button {
        background: #e0e5ec;
        color: #2d3748;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 6px 6px 12px #a3b1c6, -6px -6px 12px #ffffff;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        box-shadow: inset 3px 3px 6px #a3b1c6, inset -3px -3px 6px #ffffff;
        color: #1a202c;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        background: #e0e5ec !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: inset 3px 3px 6px #a3b1c6, inset -3px -3px 6px #ffffff !important;
        color: #2d3748 !important;
        padding: 10px !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: #e0e5ec;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 6px 6px 12px #a3b1c6, -6px -6px 12px #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("## 🏥 Navigation")
nav_option = st.sidebar.radio("Go to", ["Dashboard / View Patients", "Add New Patient", "Update Patient", "Delete Patient", "System Health"])

st.sidebar.markdown("---")
# Health Check Status in Sidebar
try:
    health_res = requests.get(f"{BASE_URL}/health", timeout=2)
    if health_res.status_code == 200:
        h_data = health_res.json()
        st.sidebar.success(f"Backend Status: **{h_data.get('status')}** (v{h_data.get('version')})")
    else:
        st.sidebar.error("Backend error.")
except Exception:
    st.sidebar.error("⚠️ Backend is offline or unreachable.")

# --- 1. DASHBOARD & VIEW PATIENTS ---
if nav_option == "Dashboard / View Patients":
    st.markdown("<h1>Patient Records Dashboard</h1>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{BASE_URL}/patients")
        if response.status_code == 200:
            patients = response.json()
            if not patients:
                st.info("No patient records found in the database.")
            else:
                # Metrics Row
                total_patients = len(patients)
                avg_age = sum([p.get('age', 0) for p in patients.values()]) / total_patients if total_patients > 0 else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Total Patients", value=total_patients)
                with col2:
                    st.metric(label="Average Age", value=f"{avg_age:.1f} yrs")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display Patients in Neumorphic Cards
                for pid, details in patients.items():
                    with st.container():
                        st.markdown(f"""
                        <div class="neumorphic-card">
                            <h3>👤 {details.get('name')} <span style="font-size: 0.7em; color: #718096;">(ID: {pid})</span></h3>
                            <hr style="border: 0; border-top: 1px solid rgba(163,177,198,0.5);">
                            <p><b>City:</b> {details.get('city')} | <b>Gender:</b> {details.get('gender')} | <b>Age:</b> {details.get('age')}</p>
                            <p><b>Height:</b> {details.get('height')} m | <b>Weight:</b> {details.get('weight')} kg</p>
                            <p><b>BMI:</b> {details.get('BMI')} &nbsp;|&nbsp; <b>Verdict:</b> <span style="color: {'#e53e3e' if details.get('verdict') != 'Normal' else '#38a169'}; font-weight: bold;">{details.get('verdict')}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.error("Failed to fetch patient data from backend.")
    except Exception as e:
        st.error(f"Could not connect to FastAPI server: {e}")

# --- 2. ADD NEW PATIENT ---
elif nav_option == "Add New Patient":
    st.markdown("<h1>Add New Patient</h1>", unsafe_allow_html=True)
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            patient_id = st.text_input("Patient ID*", placeholder="e.g., P001")
            name = st.text_input("Full Name*", placeholder="e.g., John Doe")
            city = st.text_input("City*", placeholder="e.g., New York")
            gender = st.selectbox("Gender*", ['Male', 'Female', 'Other'])
        with col2:
            age = st.number_input("Age*", min_value=1, max_value=120, value=25)
            height = st.number_input("Height (meters)*", min_value=0.1, max_value=3.0, value=1.75, step=0.01)
            weight = st.number_input("Weight (kg)*", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
        
        submitted = st.form_submit_button("Create Patient")
        if submitted:
            if not patient_id or not name or not city:
                st.warning("Please fill out all required text fields.")
            else:
                payload = {
                    "id": patient_id,
                    "name": name,
                    "city": city,
                    "age": int(age),
                    "height": float(height),
                    "weight": float(weight),
                    "gender": gender
                }
                try:
                    res = requests.post(f"{BASE_URL}/create", json=payload)
                    if res.status_code == 200:
                        st.success(res.json().get("messege", "Patient added successfully!"))
                    else:
                        st.error(res.json().get("detail", "Error creating patient."))
                except Exception as e:
                    st.error(f"Connection error: {e}")

# --- 3. UPDATE PATIENT ---
elif nav_option == "Update Patient":
    st.markdown("<h1>Update Patient Record</h1>", unsafe_allow_html=True)
    
    # Fetch patient list to let user select
    try:
        res = requests.get(f"{BASE_URL}/patients")
        if res.status_code == 200:
            patients = res.json()
            if not patients:
                st.info("No patients available to update.")
            else:
                selected_id = st.selectbox("Select Patient ID to Edit", list(patients.keys()))
                current_data = patients[selected_id]
                
                st.markdown(f"**Current Details for {current_data.get('name')}:**")
                
                with st.form("update_patient_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Name", value=current_data.get('name'))
                        city = st.text_input("City", value=current_data.get('city'))
                        gender_options = ['Male', 'Female', 'Other']
                        curr_gender = current_data.get('gender')
                        gender_idx = gender_options.index(curr_gender) if curr_gender in gender_options else 0
                        gender = st.selectbox("Gender", gender_options, index=gender_idx)
                    with col2:
                        age = st.number_input("Age", min_value=1, max_value=120, value=int(current_data.get('age', 25)))
                        height = st.number_input("Height (meters)", min_value=0.1, max_value=3.0, value=float(current_data.get('height', 1.7)), step=0.01)
                        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=float(current_data.get('weight', 70.0)), step=0.1)
                    
                    update_submitted = st.form_submit_button("Update Patient")
                    if update_submitted:
                        update_payload = {
                            "name": name,
                            "city": city,
                            "age": int(age),
                            "height": float(height),
                            "weight": float(weight),
                            "gender": gender
                        }
                        try:
                            put_res = requests.put(f"{BASE_URL}/edit/{selected_id}", json=update_payload)
                            if put_res.status_code == 200:
                                st.success(put_res.json().get("messege", "Data updated successfully"))
                            else:
                                st.error(put_res.json().get("detail", "Failed to update patient."))
                        except Exception as e:
                            st.error(f"Connection error: {e}")
        else:
            st.error("Could not retrieve patient records.")
    except Exception as e:
        st.error(f"Connection error: {e}")

# --- 4. DELETE PATIENT ---

elif nav_option == "Delete Patient":
    st.markdown("<h1>Delete Patient Record</h1>", unsafe_allow_html=True)
    
    if "delete_success_msg" in st.session_state:
        st.success(st.session_state["delete_success_msg"])
        del st.session_state["delete_success_msg"]

    try:
        res = requests.get(f"{BASE_URL}/patients")
        if res.status_code == 200:
            patients = res.json()
            if not patients:
                st.info("No patients available to delete.")
            else:
                patient_to_delete = st.selectbox("Select Patient ID to Delete", list(patients.keys()))
                p_info = patients[patient_to_delete]
                
                st.warning(f"You are about to delete **{p_info.get('name')}** (ID: `{patient_to_delete}`). This action cannot be undone.")
                
                if st.button("Confirm & Delete"):
                    del_res = requests.delete(f"{BASE_URL}/delete_one/{patient_to_delete}")
                    
                    if del_res.status_code == 200:
                        st.session_state["delete_success_msg"] = del_res.json().get("messege", "Patient successfully deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete patient.")
        else:
            st.error("Could not load patient data.")
    except Exception as e:
        st.error(f"Connection error: {e}")

# --- 5. SYSTEM HEALTH ---
elif nav_option == "System Health":
    st.markdown("<h1>System Diagnostics</h1>", unsafe_allow_html=True)
    
    try:
        root_res = requests.get(f"{BASE_URL}/")
        about_res = requests.get(f"{BASE_URL}/about")
        health_res = requests.get(f"{BASE_URL}/health")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="neumorphic-card">
                <h3>Root Endpoint</h3>
                <p><b>Response:</b><br>{root_res.json() if root_res.status_code == 200 else 'Error'}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="neumorphic-card">
                <h3>About Endpoint</h3>
                <p><b>Response:</b><br>{about_res.json() if about_res.status_code == 200 else 'Error'}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="neumorphic-card">
                <h3>Health Check</h3>
                <p><b>Response:</b><br>{health_res.json() if health_res.status_code == 200 else 'Error'}</p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Backend is not running. Please start FastAPI first using `uvicorn main:app --reload`. Details: {e}")