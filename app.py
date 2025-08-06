import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os, json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import plotly.graph_objs as go
from analytics import plot_active_customers, plot_total_sales

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

import pandas as pd
import streamlit as st



def insert_into_clients_table(cols_list):
    try:
        response = supabase.table("clients").insert({
            "contact_no": cols_list[0],
            "created_at": cols_list[1].isoformat(),
            "client_name": cols_list[2],
            "client_form_link": cols_list[3],       
            "client_response_sheet_link": cols_list[4],
            "Business_Name": cols_list[5],
            "Business_Address": cols_list[6],
            "email_id": cols_list[7],
            "password": cols_list[8]
        }).execute()

        # Try to print or log the whole response
        # st.write("Insert response:", response)

        # Check if data exists in response
        if hasattr(response, 'data') and response.data:
            st.success("Client registered successfully.")
        else:
            st.warning("Insert did not return any data. Check your input or Supabase rules.")
    except Exception as e:
        st.error(f"Insert failed due to: {e}")

def get_client_details(email):
    response = supabase.table("clients").select("*").eq("email_id", email).single().execute()
    return response 

def sign_up(email, password,cols_list=None):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        user = response.user
        if user:
            
            insert_into_clients_table(cols_list)
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response.user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")

def main_app(user_email):
    st.title("🎉 Welcome Page")
    st.success(f"Welcome, {user_email}! 👋")

    client_info = get_client_details(user_email)
    if client_info:
        sheet_url = client_info.data["client_response_sheet_link"]
        df = load_google_sheet(sheet_url)
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        st.title("Google Sheet Data Viewer")
        st.dataframe(df)

# df = ... (your DataFrame loading code)
        plot_active_customers(df, contact_col='customer_mobile_number', timestamp_col='timestamp')
        plot_total_sales(df, sales_col='total_sales', timestamp_col='timestamp')
        st.info(f"Your client data: {client_info.data}")
    else:
        st.warning("Client details not found.")

    if st.button("Logout"):
        sign_out()

def auth_screen():
    st.title("🔐 Streamlit & Supabase Auth App")
    client_name = st.text_input("Client Name", placeholder="Enter your name")
    client_form_link = st.text_input("Client Form Link", placeholder="Enter the form link")
    client_response_sheet_link = st.text_input("Client Response Sheet Link", placeholder="Enter the response sheet link")
    Business_Name = st.text_input("Business Name", placeholder="Enter your business name")
    street = st.text_input("Street")
    city = st.text_input("City")
    state = st.text_input("State")
    pincode = st.text_input("Pincode")
    country = st.text_input("Country", value="India")
    address = {
        "street": street,
        "city": city,
        "state": state,
        "pincode": pincode,
        "country": country
    }
    Business_Address = address
    option = st.selectbox("Choose an action:", ["Login", "Sign Up"])
    contact = int(st.number_input("Contact Number"))
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    current_timestamp = datetime.now()
    
    cols_list = [contact,current_timestamp,client_name,client_form_link,client_response_sheet_link,Business_Name,Business_Address,email,password]
    if option == "Sign Up" and st.button("Register"):
        user = sign_up(email, password,cols_list=cols_list)
        if user:
            st.success("Registration successful. Please log in.")

    if option == "Login" and st.button("Login"):
        user = sign_in(email, password)
        if user:
            st.session_state.user_email = user.email
            st.success(f"Welcome back, {email}!")
            st.rerun()
            
            
def load_google_sheet(sheet_url):
    # Convert Google Sheets view URL to CSV export URL
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0]
    csv_url = sheet_url.replace("/edit", "") + "/export?format=csv"
    
    try:
        df = pd.read_csv(csv_url)
        st.success("Data loaded successfully from Google Sheet.")
        return df
    except Exception as e:
        st.error(f"Failed to load sheet: {e}")
        return None

# Session check
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email:
    main_app(st.session_state.user_email)
else:
    auth_screen()
