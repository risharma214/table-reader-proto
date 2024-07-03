import streamlit as st
from streamlit import session_state as ss
import streamlit_authenticator as stauth
import pandas as pd
from supabase import create_client, Client
from st_login_form import login_form
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

def create_folder(folder_name):
  """Create a folder and prints the folder ID
  Returns : Folder Id
  """
  creds, _ = google.auth.default()

  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, fields="id").execute()
    print(f'Folder ID: "{file.get("id")}".')
    return file.get("id")

  except HttpError as error:
    print(f"An error occurred: {error}")
    return None

def create_folder_in_folder(folder_name, parent_folder_id):
  """Create a folder and prints the folder ID
  Returns : Folder Id
  """
  creds, _ = google.auth.default()

  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)
    file_metadata = {
        "name": folder_name,
        "parent": [parent_folder_id], 
        "mimeType": "application/vnd.google-apps.folder",
    }

    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, fields="id").execute()
    print(f'Folder ID: "{file.get("id")}".')
    return file.get("id")

  except HttpError as error:
    print(f"An error occurred: {error}")
    return None

def check_folder_exists(service, parent_folder_id, folder_name):
  """Checks if a folder exists in a given parent folder.

  Args:
    service: The authorized Google Drive API service.
    parent_folder_id: The ID of the parent folder.
    folder_name: The name of the folder to check.

  Returns:
    True if the folder exists, False otherwise.
  """
  query = f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
  results = service.files().list(q=query, fields='files(id)').execute()
  return len(results.get('files', [])) > 0


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

client = login_form()

# Example query to fetch usernames
response = supabase.table("users").select("username").execute()

# Base directory where folders will be created
base_directory = '102hqOG363E-LM0bKUoQY9RjJkYyOwk4w'

data=response.data
username_list = []

st.write(data[0]["username"])
for i in range(len(data)):
    username_holder = data[i]["username"]
    username_list.append(username_holder)

creds, _ = google.auth.default()
service = build('drive', 'v3', credentials=creds)

for username in username_list:
    
    # Check if the folder already exists
    if check_folder_exists(service, base_directory, username):
        print(f"Folder already exists for user '{username}' at: {base_directory}")
    else:
        try:
            create_folder_in_folder(username, base_directory)
            print(f"Folder created for user '{username}' at: {base_directory}")
        except OSError as e:
            print(f"Failed to create directory for user '{username}': {e}")

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
        st.switch_page("pages/Initial_Page.py")
    else:
        st.success("Welcome guest")
        st.switch_page("pages/Initial_Page.py")
else:
    st.error("Not authenticated")