import streamlit as st
import os
import json
import time

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
elif 'selected_chore_guide' in st.session_state and st.session_state.selected_chore_guide in chores_list:
    default_index = chores_list.index(st.session_state.selected_chore_guide)
    del st.session_state.selected_chore_guide

# Chore Selection
selected_chore = st.selectbox(
    "🔍 Select a Chore to view detailed instructions:",
    options=chores_list,
    index=default_index
)

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
            "steps": ["No instructions written yet. Open and edit 'instructions.json' to write guidelines."],
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

# Main Content Layout: Instructions (Left) vs Photo/Image (Right)
content_col1, content_col2 = st.columns([3, 2])

with content_col1:
    col_title, col_btn = st.columns([3, 2])
    with col_title:
        st.markdown("### 📝 Cleaning Checklist")
    with col_btn:
        if st.button("🔄 Reset Checklist", key=f"reset_{selected_chore}", use_container_width=True):
            for i in range(len(details["steps"])):
                st.session_state[f"step_{selected_chore}_{i}"] = False
            st.rerun()
    
    st.caption("Cross off the tasks below as you complete them:")
    for step_num, step in enumerate(details["steps"]):
        checkbox_key = f"step_{selected_chore}_{step_num}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False
        st.checkbox(f"**Step {step_num + 1}:** {step}", key=checkbox_key)

with content_col2:
    st.markdown("### 📷 Visual Guide")
    
    # Image Loading Logic: Scan for all matching files starting with the chore name
    # Strip parenthetical notes to find the base chore filename for matching assets
    base_chore = selected_chore.split("(")[0].strip()
    chore_filename = base_chore.lower().replace(" ", "_")
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    found_images = []
    
    if os.path.exists("assets"):
        for file in os.listdir("assets"):
            name, ext = os.path.splitext(file)
            # Match files starting with the chore name (e.g., staircase, staircase_2, staircase_close_up)
            if name.startswith(chore_filename) and ext.lower() in valid_extensions:
                found_images.append(os.path.join("assets", file))
                
    # Sort images to keep them ordered (e.g., staircase_1 before staircase_2)
    found_images.sort()
    
    if len(found_images) == 1:
        # Display single image directly
        st.image(found_images[0], caption=f"Visual guide for {selected_chore}", use_container_width=True)
    elif len(found_images) > 1:
        # Display multiple images using sub-tabs
        tabs = st.tabs([f"📷 Photo {i+1}" for i in range(len(found_images))])
        for i, img_path in enumerate(found_images):
            with tabs[i]:
                st.image(img_path, caption=f"Photo {i+1} of {len(found_images)}: {selected_chore}", use_container_width=True)
    else:
        # Fallback if no images found
        st.markdown(f"""
        <div class="fallback-image-box">
            <span style="font-size: 3rem; display: block; margin-bottom: 10px;">📷</span>
            <span style="font-weight: 600; color: #7f8c8d; font-size: 1.1rem;">Instruction photo coming soon!</span>
            <p style="font-size: 0.85rem; color: #95a5a6; margin-top: 5px; margin-bottom: 0;">
                A photo showing the clean standard for "{selected_chore}" will be uploaded soon.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
st.markdown("---")

# Edit Chore Details & Photos Expander
with st.expander("✏️ Edit Chore Details & Photos", expanded=False):
    st.markdown(f"### Update Guide for **{selected_chore}**")
    
    # 1. Edit Tools
    current_tools_str = ", ".join(details.get("tools", []))
    edited_tools = st.text_input("Required Tools & Supplies (comma-separated):", value=current_tools_str)
    
    # 2. Edit Steps
    current_steps_str = "\n".join(details.get("steps", []))
    edited_steps = st.text_area("Cleaning Steps (one step per line):", value=current_steps_str, height=200)
    
    # 3. Existing Photos Management
    st.markdown("#### 📷 Manage Photos")
    if found_images:
        st.write("Click 'Delete' next to any photo you want to remove:")
        for img_path in found_images:
            img_filename = os.path.basename(img_path)
            col_img, col_del = st.columns([4, 1])
            with col_img:
                st.caption(f"File: {img_filename}")
            with col_del:
                if st.button("🗑️ Delete", key=f"del_{img_filename}"):
                    try:
                        os.remove(img_path)
                        st.success(f"Deleted {img_filename}!")
                        # Force reload details and images
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete {img_filename}: {e}")
    else:
        st.info("No photos uploaded for this chore yet.")
        
    # 4. Upload New Photos (dynamically keyed to clear the uploader widget after a successful save)
    base_chore = selected_chore.split("(")[0].strip()
    chore_key = base_chore.lower().replace(" ", "_")
    uploader_ver_key = f"uploader_ver_{chore_key}"
    if uploader_ver_key not in st.session_state:
        st.session_state[uploader_ver_key] = 0
        
    uploader_key = f"uploader_{chore_key}_{st.session_state[uploader_ver_key]}"
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
        
        # Save instructions to JSON file
        st.session_state.chore_details[selected_chore] = {
            "tools": tools_list,
            "steps": steps_list
        }
        
        try:
            with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.chore_details, f, ensure_ascii=False, indent=2)
            st.success("Successfully updated details in instructions.json!")
        except Exception as e:
            st.error(f"Failed to save instructions: {e}")
            
        # Process and save uploaded files with duplicate checks (MD5 hashes)
        if uploaded_files:
            import hashlib
            
            # Create assets directory if it doesn't exist
            if not os.path.exists("assets"):
                os.makedirs("assets")
            
            # Retrieve MD5 hashes of already uploaded files for this chore
            existing_hashes = set()
            for img_path in found_images:
                try:
                    with open(img_path, "rb") as f:
                        existing_hashes.add(hashlib.md5(f.read()).hexdigest())
                except:
                    pass
            
            batch_hashes = set()
            base_chore = selected_chore.split("(")[0].strip()
            chore_filename = base_chore.lower().replace(" ", "_")
            messages = []
            
            for idx, uploaded_file in enumerate(uploaded_files):
                file_bytes = uploaded_file.getvalue()
                file_hash = hashlib.md5(file_bytes).hexdigest()
                
                if file_hash in existing_hashes:
                    messages.append(("warning", f"⚠️ Skipped duplicate: '{uploaded_file.name}' has already been uploaded for this chore."))
                    continue
                if file_hash in batch_hashes:
                    messages.append(("warning", f"⚠️ Skipped batch duplicate: '{uploaded_file.name}' was uploaded multiple times in this batch."))
                    continue
                
                batch_hashes.add(file_hash)
                ext = os.path.splitext(uploaded_file.name)[1].lower()
                timestamp = int(time.time())
                new_filename = f"{chore_filename}_{timestamp}_{idx}{ext}"
                save_path = os.path.join("assets", new_filename)
                
                try:
                    with open(save_path, "wb") as f:
                        f.write(file_bytes)
                    messages.append(("success", f"✅ Saved {new_filename} to assets!"))
                    existing_hashes.add(file_hash)
                except Exception as e:
                    messages.append(("error", f"❌ Failed to save {new_filename}: {e}"))
            
            # Render all messages and pause briefly so user can see them before rerun
            for msg_type, text in messages:
                if msg_type == "success":
                    st.success(text)
                elif msg_type == "warning":
                    st.warning(text)
                else:
                    st.error(text)
            
            if messages:
                st.session_state[uploader_ver_key] += 1
                time.sleep(2.0)
                    
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


