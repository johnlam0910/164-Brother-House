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

# Main Content: Mobile-friendly tabbed layout (📝 Checklist | 📷 Image Guide)
# Pre-extract all OneDrive image URLs from step text for the Image Guide tab
step_image_map = {}  # {step_num: [url, ...]}
for step_num, step in enumerate(details["steps"]):
    urls = extract_image_urls(step)
    if urls:
        step_image_map[step_num] = urls

# Compute chore filename for asset lookup (used in editor upload naming)
base_chore = selected_chore.split("(")[0].strip()
clean_base = "".join(c for c in base_chore if c.isalnum() or c.isspace() or c == "_")
chore_filename = clean_base.lower().strip().replace(" ", "_")

col_checklist, col_images = st.columns([3, 2])

with col_checklist:
    col_title, col_btn = st.columns([3, 2])
    with col_title:
        st.caption("Cross off the tasks below as you complete them:")
    with col_btn:
        if st.button("🔄 Reset", key=f"reset_{selected_chore}", use_container_width=True):
            for i in range(len(details["steps"])):
                st.session_state[f"step_{selected_chore}_{i}"] = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    for step_num, step in enumerate(details["steps"]):
        checkbox_key = f"step_{selected_chore}_{step_num}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False
        # Do not clean inline image links, display the raw step text with its OneDrive links
        st.checkbox(f"**Step {step_num + 1}:** {step}", key=checkbox_key)

with col_images:
    # Show cloud-uploaded photos (from database details)
    cloud_photos = details.get("uploaded_photos", [])
    if cloud_photos:
        st.markdown("##### ☁️ Cloud Uploaded Photos")
        for idx, img_url in enumerate(cloud_photos):
            st.image(img_url, caption=f"Cloud Photo {idx + 1} of {len(cloud_photos)}", use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        # Fallback if no images at all
        st.markdown(f"""
        <div class="fallback-image-box">
            <span style="font-size: 3rem; display: block; margin-bottom: 10px;">📷</span>
            <span style="font-weight: 600; color: #7f8c8d; font-size: 1.1rem;">No cloud images uploaded yet</span>
            <p style="font-size: 0.85rem; color: #95a5a6; margin-top: 5px; margin-bottom: 0;">
                Photos for "{selected_chore}" can be uploaded in the edit section below.
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 4. Upload Key and Expander State determination
base_chore = selected_chore.split("(")[0].strip()
clean_base = "".join(c for c in base_chore if c.isalnum() or c.isspace() or c == "_")
chore_key = clean_base.lower().strip().replace(" ", "_")
uploader_ver_key = f"uploader_ver_{chore_key}"
if uploader_ver_key not in st.session_state:
    st.session_state[uploader_ver_key] = 0

uploader_key = f"uploader_{chore_key}_{st.session_state[uploader_ver_key]}"

# Keep expander open on rerun if there are pending files or if an action was performed
keep_open = False
if uploader_key in st.session_state and st.session_state[uploader_key]:
    keep_open = True
if st.session_state.get("keep_editor_open", False):
    keep_open = True

# Reset keep_editor_open flag for next runs (so they can collapse it manually if they want)
st.session_state.keep_editor_open = False

# Edit Chore Details & Photos Expander
with st.expander("✏️ Edit Chore Details & Photos", expanded=keep_open):
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
    
    # 3. Existing Photos Management
    st.markdown("#### 📷 Manage Cloud Photos")
    
    # Manage cloud photos
    cloud_photos = details.get("uploaded_photos", [])
    if cloud_photos:
        st.caption("Manage cloud guide photos (🗑️ to delete):")
        for idx, img_url in enumerate(cloud_photos):
            col_img, col_del = st.columns([6, 1])
            with col_img:
                st.caption(f"Cloud Photo {idx+1}: {img_url.split('/')[-1]}")
            with col_del:
                if st.button("🗑️", key=f"del_cloud_{idx}", help="Delete cloud photo"):
                    # Remove from list
                    updated_photos = cloud_photos.copy()
                    deleted_url = updated_photos.pop(idx)
                    st.session_state.chore_details[selected_chore]["uploaded_photos"] = updated_photos
                    
                    # Try to delete from Supabase storage bucket
                    try:
                        filename_to_delete = deleted_url.split("/")[-1]
                        supabase_client = get_supabase_client()
                        if supabase_client:
                            supabase_client.storage.from_("chore-guides").remove([filename_to_delete])
                    except:
                        pass
                        
                    # Save to database and local file
                    if get_supabase_client() is not None:
                        db_set("chore_details", st.session_state.chore_details)
                    with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
                        
                    st.session_state.save_success_msg = "🗑️ Deleted cloud photo!"
                    st.session_state.keep_editor_open = True
                    st.rerun()
    else:
        st.info("No cloud photos uploaded for this chore yet.")
        
    # 4. Upload New Photos
    uploaded_files = st.file_uploader(
        "Upload new photo(s) for this chore:", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True,
        key=uploader_key
    )
    
    # 5. Save Button
    if st.button("💾 Save Chore Details", type="primary", use_container_width=True):
        # Update details in dict
        tools_list = [t.strip() for t in edited_tools.split(",") if t.strip()]
        steps_list = [s.strip() for s in edited_steps.split("\n") if s.strip()]
        
        # Save instructions to JSON file (preserving onedrive_url if it existed)
        old_details = st.session_state.chore_details.get(selected_chore, {})
        
        supabase_client = get_supabase_client()
        uploaded_photo_urls = []
        messages = []
        
        # Process and save uploaded files with duplicate checks (MD5 hashes)
        if uploaded_files:
            import hashlib
            
            # 1. Cloud Upload Mode
            if supabase_client is not None:
                for idx, uploaded_file in enumerate(uploaded_files):
                    file_bytes = uploaded_file.getvalue()
                    ext = os.path.splitext(uploaded_file.name)[1].lower()
                    timestamp = int(time.time())
                    mime_type = "image/jpeg"
                    if ext == ".png":
                        mime_type = "image/png"
                    elif ext == ".webp":
                        mime_type = "image/webp"
                    
                    cloud_filename = f"{chore_filename}_{timestamp}_{idx}{ext}"
                    try:
                        # Upload to 'chore-guides' bucket
                        res = supabase_client.storage.from_("chore-guides").upload(
                            path=cloud_filename,
                            file=file_bytes,
                            file_options={"content-type": mime_type}
                        )
                        public_url = supabase_client.storage.from_("chore-guides").get_public_url(cloud_filename)
                        uploaded_photo_urls.append(public_url)
                        messages.append(f"✅ Uploaded '{uploaded_file.name}' to cloud storage!")
                    except Exception as e:
                        messages.append(f"❌ Cloud upload failed for '{uploaded_file.name}': {e}")
                        
            # 2. Local Fallback/Write Mode
            else:
                if not os.path.exists("assets"):
                    os.makedirs("assets")
                
                valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
                found_images = []
                for file in os.listdir("assets"):
                    name, ext = os.path.splitext(file)
                    if is_chore_file(file, chore_filename) and ext.lower() in valid_extensions:
                        found_images.append(os.path.join("assets", file))
                
                existing_hashes = set()
                for img_path in found_images:
                    try:
                        with open(img_path, "rb") as f:
                            existing_hashes.add(hashlib.md5(f.read()).hexdigest())
                    except:
                        pass
                
                batch_hashes = set()
                for idx, uploaded_file in enumerate(uploaded_files):
                    file_bytes = uploaded_file.getvalue()
                    file_hash = hashlib.md5(file_bytes).hexdigest()
                    
                    if file_hash in existing_hashes or file_hash in batch_hashes:
                        messages.append(f"⚠️ Skipped duplicate: '{uploaded_file.name}'")
                        continue
                    
                    batch_hashes.add(file_hash)
                    ext = os.path.splitext(uploaded_file.name)[1].lower()
                    timestamp = int(time.time())
                    new_filename = f"{chore_filename}_{timestamp}_{idx}{ext}"
                    save_path = os.path.join("assets", new_filename)
                    
                    try:
                        with open(save_path, "wb") as f:
                            f.write(file_bytes)
                        messages.append(f"✅ Saved {new_filename} to local assets!")
                    except Exception as e:
                        messages.append(f"❌ Local save failed for {new_filename}: {e}")
        
        # Extend current list of uploaded photos with the new ones
        current_uploaded_photos = old_details.get("uploaded_photos", [])
        current_uploaded_photos.extend(uploaded_photo_urls)
        
        st.session_state.chore_details[selected_chore] = {
            "tools": tools_list,
            "steps": steps_list,
            "onedrive_url": old_details.get("onedrive_url", ""),
            "uploaded_photos": current_uploaded_photos
        }
        
        # Save to database and local file
        if supabase_client is not None:
            db_set("chore_details", st.session_state.chore_details)
            
        try:
            with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
            st.session_state.save_success_msg = "💾 Chore details updated successfully!"
            st.session_state.keep_editor_open = True
        except Exception as e:
            st.error(f"Failed to save instructions: {e}")
            
        if messages:
            st.session_state.upload_results = messages
            st.session_state[uploader_ver_key] += 1
            st.session_state.keep_editor_open = True
            
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


