# --- START OF DIAGNOSTIC app.py ---

import streamlit as st
import os

st.title("File System Diagnostic Tool")

st.header("1. Current Working Directory")
cwd = os.getcwd()
st.write(f"The script is running from: `{cwd}`")

st.header("2. Contents of the Current Directory")
st.write("Files and folders found here:")
try:
    dir_contents = os.listdir(cwd)
    st.code('\n'.join(dir_contents))
except Exception as e:
    st.error(f"Could not list directory contents: {e}")

st.header("3. Contents of the Parent Directory (One level up)")
try:
    parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))
    st.write(f"The parent directory is: `{parent_dir}`")
    st.write("Files and folders found here:")
    parent_contents = os.listdir(parent_dir)
    st.code('\n'.join(parent_contents))
except Exception as e:
    st.error(f"Could not check parent directory: {e}")

st.header("4. Checking for `assets/corporate.png`")
# Test the path we think should work
test_path_1 = "assets/corporate.png"
if os.path.exists(test_path_1):
    st.success(f"✅ Found the image at the simple relative path: `{test_path_1}`")
else:
    st.error(f"❌ Could NOT find the image at the simple relative path: `{test_path_1}`")

# Test another common path structure on Streamlit Cloud
test_path_2 = f"{cwd}/assets/corporate.png"
if os.path.exists(test_path_2):
    st.success(f"✅ Found the image at the full constructed path: `{test_path_2}`")
else:
    st.error(f"❌ Could NOT find the image at the full constructed path: `{test_path_2}`")

# Another test
test_path_3 = f"{parent_dir}/assets/corporate.png"
if os.path.exists(test_path_3):
    st.success(f"✅ Found the image in the PARENT directory: `{test_path_3}`")
else:
    st.error(f"❌ Could NOT find the image in the PARENT directory: `{test_path_3}`")
