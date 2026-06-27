import streamlit as st
import os
import json
from utils import get_supabase_client, db_set
import time
import re

def reorder_files(file_paths, chore_filename):
    import shutil
    # Rename to temporary names first to avoid conflicts
    temp_names = []
    for idx, path in enumerate(file_paths):
        dir_name = os.path.dirname(path)
        ext = os.path.splitext(path)[1]
        temp_name = os.path.join(dir_name, f"temp_reorder_{idx}{ext}")
        try:
            os.rename(path, temp_name)
            temp_names.append(temp_name)
        except:
            pass
            
    # Rename from temp to final names with a new timestamp
    timestamp = int(time.time())
    for idx, temp_path in enumerate(temp_names):
        dir_name = os.path.dirname(temp_path)
        ext = os.path.splitext(temp_path)[1]
        new_name = os.path.join(dir_name, f"{chore_filename}_{timestamp}_{idx}{ext}")
        try:
            os.rename(temp_path, new_name)
        except:
            pass

# --- Helpers for extracting OneDrive image URLs from step text ---
# Pattern matches: ([📷 Image Guide](URL)) or ([📷 Guide](URL)) etc.
IMAGE_LINK_PATTERN = re.compile(
    r'\(\[📷[^\]]*\]\((https?://[^\)]+)\)\)'
)

def extract_image_urls(step_text):
    """Extract all OneDrive image URLs from a step's markdown text."""
    return IMAGE_LINK_PATTERN.findall(step_text)

def clean_step_text(step_text):
    """Remove inline image link markdown from step text for cleaner checklist display."""
    # Remove the full ([📷 ...](URL)) patterns
    cleaned = IMAGE_LINK_PATTERN.sub('', step_text)
    # Clean up leftover whitespace/punctuation artifacts
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)    # collapse multiple spaces
    cleaned = re.sub(r'\s+,', ',', cleaned)        # fix " ," → ","
    cleaned = re.sub(r'\s+\.', '.', cleaned)       # fix " ." → "."
    cleaned = re.sub(r',\s*\.', '.', cleaned)      # fix ",." → "."
    return cleaned.strip()

def is_chore_file(filename, chore_filename):
    """
    Checks if a filename corresponds exactly to the chore_filename prefix,
    accounting for timestamps and indexes (format: chore_filename_timestamp_idx.ext).
    """
    name, ext = os.path.splitext(filename)
    parts = name.split("_")
    if len(parts) >= 3:
        # Check if the last two parts are digits (timestamp and index)
        if parts[-2].isdigit() and parts[-1].isdigit():
            file_chore = "_".join(parts[:-2])
            return file_chore == chore_filename
    return name == chore_filename

def make_direct_image_url(url):
    """
    Converts a SharePoint sharing link to a direct file access/download link
    that can be embedded inside an st.image tag.
    """
    if "sharepoint.com" in url:
        if "download=1" not in url:
            if "?" in url:
                return url + "&download=1"
            else:
                return url + "?download=1"
    return url

# Page Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">📖 House Chore Instruction Guide</h1>
    <p class="guide-subtitle">Clear standards make a happy home! Follow these instructions to perform chores effectively.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# List of default chores for lookup
chores_list = st.session_state.chores_list

# Pre-selection logic (checks URL query parameters first, then session state backup)
default_index = 0
query_chore = st.query_params.get("chore", None)
if query_chore and query_chore in chores_list:
    default_index = chores_list.index(query_chore)
    # Clear the query parameter so the selectbox is not locked on subsequent runs
    if "chore" in st.query_params:
        del st.query_params["chore"]
elif 'selected_chore_guide' in st.session_state and st.session_state.selected_chore_guide in chores_list:
    default_index = chores_list.index(st.session_state.selected_chore_guide)
    del st.session_state.selected_chore_guide

# Chore Selection
selected_chore = st.selectbox(
    "🔍 Select a Chore to view detailed instructions:",
    options=chores_list,
    index=default_index
)

# Reset expander open state if the chore changes
if "last_selected_chore" not in st.session_state or st.session_state.last_selected_chore != selected_chore:
    st.session_state.last_selected_chore = selected_chore
    st.session_state.keep_editor_open = False

# Reload instructions from JSON file on page load to pick up manual text edits instantly
INSTRUCTIONS_FILE = "instructions.json"
if os.path.exists(INSTRUCTIONS_FILE) and os.path.getsize(INSTRUCTIONS_FILE) > 0:
    try:
        with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
            st.session_state.chore_details = json.load(f)
    except:
        pass

# Ensure any new chores added in the Roster edit also have empty instruction placeholders
for chore_name in st.session_state.chores_list:
    if chore_name not in st.session_state.chore_details:
        st.session_state.chore_details[chore_name] = {
            "tools": ["General cleaning supplies"],
            "steps": ["No instructions written yet. Click 'Edit Chore Details & Photos' below to write guidelines."],
            "onedrive_url": ""
        }

# Fetch details for the selected chore
details = st.session_state.chore_details.get(selected_chore, {
    "tools": ["General cleaning supplies"],
    "steps": [
        "Sweep and clear the area.",
        "Wipe surfaces with appropriate cleaning agent.",
        "Dispose of waste and tidy tools."
    ]
})

# Display Chore Overview Layout
st.markdown(f"## {selected_chore}")

st.markdown(f"🛠️ **Tools & Supplies Required:** {', '.join(details['tools'])}")
st.markdown("---")

col_title, col_btn = st.columns([5, 1])
with col_title:
    st.caption("Cross off the tasks below as you complete them:")
with col_btn:
    if st.button("🔄 Reset Checklist", key=f"reset_{selected_chore}", use_container_width=True):
        for i in range(len(details["steps"])):
            st.session_state[f"step_{selected_chore}_{i}"] = False
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
for step_num, step in enumerate(details["steps"]):
    checkbox_key = f"step_{selected_chore}_{step_num}"
    if checkbox_key not in st.session_state:
        st.session_state[checkbox_key] = False
    # Display the raw step text containing the OneDrive/SharePoint markdown link
    st.checkbox(f"**Step {step_num + 1}:** {step}", key=checkbox_key)

st.markdown("---")

# Keep expander open on rerun if an action was performed
keep_open = False
if st.session_state.get("keep_editor_open", False):
    keep_open = True

# Reset keep_editor_open flag for next runs (so they can collapse it manually if they want)
st.session_state.keep_editor_open = False

# Edit Chore Details Expander
with st.expander("✏️ Edit Chore Details", expanded=keep_open):
    st.markdown(f"### Update Guide for **{selected_chore}**")
    
    # Display save or upload results from the previous rerun
    if "save_success_msg" in st.session_state:
        st.success(st.session_state.save_success_msg)
        del st.session_state.save_success_msg
    if "upload_results" in st.session_state:
        for result in st.session_state.upload_results:
            if "✅" in result:
                st.success(result)
            elif "⚠️" in result:
                st.warning(result)
            else:
                st.error(result)
        del st.session_state.upload_results

    # 1. Edit Tools
    current_tools_str = ", ".join(details.get("tools", []))
    edited_tools = st.text_input("Required Tools & Supplies (comma-separated):", value=current_tools_str)
    
    # 2. Edit Steps
    current_steps_str = "\n".join(details.get("steps", []))
    edited_steps = st.text_area("Cleaning Steps (one step per line):", value=current_steps_str, height=200)
    
    # 3. Save Button
    if st.button("💾 Save Chore Details", type="primary", use_container_width=True):
        # Update details in dict
        tools_list = [t.strip() for t in edited_tools.split(",") if t.strip()]
        steps_list = [s.strip() for s in edited_steps.split("\n") if s.strip()]
        
        # Save instructions to JSON file (preserving onedrive_url and uploaded_photos if they existed)
        old_details = st.session_state.chore_details.get(selected_chore, {})
        st.session_state.chore_details[selected_chore] = {
            "tools": tools_list,
            "steps": steps_list,
            "onedrive_url": old_details.get("onedrive_url", ""),
            "uploaded_photos": old_details.get("uploaded_photos", [])
        }
        
        # Save to database and local file
        supabase_client = get_supabase_client()
        if supabase_client is not None:
            db_set("chore_details", st.session_state.chore_details)
            
        try:
            with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
            st.session_state.save_success_msg = "💾 Chore details updated successfully!"
            st.session_state.keep_editor_open = True
        except Exception as e:
            st.error(f"Failed to save instructions: {e}")
            
        st.rerun()

    # 6. Default Baseline Manager
    st.markdown("---")
    st.markdown("#### 💾 Default Baseline Manager")
    st.caption("Save your custom guidelines and photos as the default baseline, or revert to it if you make mistakes.")
    
    col_set, col_rev = st.columns(2)
    DEFAULT_JSON = "instructions_default.json"
    
    with col_set:
        if st.button("💾 Set Current as Default", help="Save the current instructions and photos for this chore as the default baseline.", use_container_width=True):
            import shutil
            
            # 1. Update instructions_default.json
            default_details = {}
            if os.path.exists(DEFAULT_JSON) and os.path.getsize(DEFAULT_JSON) > 0:
                try:
                    with open(DEFAULT_JSON, "r", encoding="utf-8") as f:
                        default_details = json.load(f)
                except:
                    pass
            
            default_details[selected_chore] = st.session_state.chore_details.get(selected_chore, {
                "tools": [],
                "steps": []
            })
            
            try:
                with open(DEFAULT_JSON, "w", encoding="utf-8") as f:
                    json.dump(default_details, f, ensure_ascii=False, indent=2)
                st.session_state.save_success_msg = "✅ Instructions set as default baseline!"
                st.session_state.keep_editor_open = True
            except Exception as e:
                st.error(f"❌ Failed to save default instructions: {e}")
                
            # 2. Copy current photos to assets_default/
            if not os.path.exists("assets_default"):
                os.makedirs("assets_default")
                
            # Remove old default photos for this chore
            for file in os.listdir("assets_default"):
                if is_chore_file(file, chore_filename):
                    try:
                        os.remove(os.path.join("assets_default", file))
                    except:
                        pass
                        
            # Copy active photos
            copied_count = 0
            if os.path.exists("assets"):
                for file in os.listdir("assets"):
                    if is_chore_file(file, chore_filename):
                        try:
                            shutil.copy(os.path.join("assets", file), os.path.join("assets_default", file))
                            copied_count += 1
                        except:
                            pass
            if copied_count > 0:
                st.session_state.save_success_msg += f" (Copied {copied_count} photos to default baseline)"
            
            st.rerun()
            
    with col_rev:
        if st.button("⏪ Revert to Default", help="Restore the saved default instructions and photos for this chore.", use_container_width=True):
            import shutil
            
            # 1. Restore instructions from instructions_default.json
            reverted = False
            if os.path.exists(DEFAULT_JSON) and os.path.getsize(DEFAULT_JSON) > 0:
                try:
                    with open(DEFAULT_JSON, "r", encoding="utf-8") as f:
                        default_details = json.load(f)
                    if selected_chore in default_details:
                        st.session_state.chore_details[selected_chore] = default_details[selected_chore]
                        reverted = True
                except:
                    pass
            
            if reverted:
                try:
                    with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
                    st.session_state.save_success_msg = "✅ Reverted instructions to default baseline!"
                    st.session_state.keep_editor_open = True
                except Exception as e:
                    st.error(f"❌ Failed to restore instructions: {e}")
                    reverted = False
            else:
                st.warning("⚠️ No saved default baseline found for this chore!")
                
            if reverted:
                # 2. Restore photos from assets_default/
                # Delete active photos
                if os.path.exists("assets"):
                    for file in os.listdir("assets"):
                        if is_chore_file(file, chore_filename):
                            try:
                                os.remove(os.path.join("assets", file))
                            except:
                                pass
                                
                # Copy back from assets_default/
                restored_count = 0
                if os.path.exists("assets_default"):
                    for file in os.listdir("assets_default"):
                        if is_chore_file(file, chore_filename):
                            try:
                                if not os.path.exists("assets"):
                                    os.makedirs("assets")
                                shutil.copy(os.path.join("assets_default", file), os.path.join("assets", file))
                                restored_count += 1
                            except:
                                pass
                if restored_count > 0:
                    st.session_state.save_success_msg += f" (Restored {restored_count} photos from default baseline)"
                
                st.rerun()

    # 6. Inactive & Backup Guides (for renames, deletions, and combinations)
    inactive_chores = [c for c in st.session_state.chore_details.keys() if c not in chores_list]
    if inactive_chores:
        st.markdown("---")
        st.markdown("#### 📦 Inactive & Backup Guides")
        st.caption("These guides exist in your database but their chores were deleted or renamed. You can migrate their instructions to active chores or delete them permanently.")
        
        for inactive in inactive_chores:
            col_in, col_to, col_act = st.columns([2, 3, 1])
            with col_in:
                st.markdown(f"**{inactive}**")
                st.caption(f"{len(st.session_state.chore_details[inactive].get('steps', []))} steps")
            with col_to:
                target_chore = st.selectbox(
                    "Migrate to:", 
                    chores_list, 
                    key=f"migrate_to_{inactive}",
                    index=0
                )
            with col_act:
                if st.button("💾 Copy", key=f"btn_migrate_{inactive}", help=f"Copy instructions from {inactive} to {target_chore}"):
                    # Copy details
                    st.session_state.chore_details[target_chore] = st.session_state.chore_details[inactive].copy()
                    
                    # Save to database and local file
                    if get_supabase_client() is not None:
                        db_set("chore_details", st.session_state.chore_details)
                    with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
                        
                    st.session_state.save_success_msg = f"✅ Successfully copied guide from '{inactive}' to '{target_chore}'!"
                    st.session_state.keep_editor_open = True
                    st.rerun()
            
            # Allow permanent deletion
            col_del_label, col_del_btn = st.columns([5, 1])
            with col_del_btn:
                if st.button("🗑️ Delete Backup", key=f"btn_del_inactive_{inactive}", help=f"Permanently delete backup guide for {inactive}"):
                    del st.session_state.chore_details[inactive]
                    
                    # Save to database and local file
                    if get_supabase_client() is not None:
                        db_set("chore_details", st.session_state.chore_details)
                    with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
                        
                    st.session_state.save_success_msg = f"🗑️ Permanently deleted backup guide for '{inactive}'!"
                    st.session_state.keep_editor_open = True
                    st.rerun()
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
st.markdown("---")
# Home Reminder alert box
st.markdown("""
<div class="reminder-card">
    <h4 class="reminder-title">🏠 Home Reminder for the Brothers:</h4>
    <p class="reminder-text">
        Let’s stay on top of our cleaning schedule and look after our shared space together. If you see something that needs attention outside of the roster, please step in and help out.
    </p>
    <p class="reminder-quote">
        "Share with the Lord’s people who are in need. Practice hospitality." (Romans 12:13)
    </p>
</div>
""", unsafe_allow_html=True)


