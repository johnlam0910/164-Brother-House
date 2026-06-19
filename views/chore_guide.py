import streamlit as st
import os
import json
import time

# Page Header
st.markdown("<h1 style='text-align: center; color: #2e5a44;'>📖 House Chore Instruction Guide</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555; font-size: 1.1rem;'>Clear standards make a happy home! Follow these instructions to perform chores effectively.</p>", unsafe_allow_html=True)
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
    st.markdown("### 📝 Cleaning Instructions")
    for step_num, step in enumerate(details["steps"], 1):
        st.markdown(f"{step_num}. {step}")

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
    
    # Re-index all matching images sequentially to clean up gaps and normalize names
    normalized = False
    for idx, img_path in enumerate(found_images):
        dirname, filename = os.path.split(img_path)
        ext = os.path.splitext(filename)[1].lower()
        
        clean_name = filename
        if "_pos_" in filename:
            parts = filename.split("_pos_")
            if len(parts) > 1 and "_" in parts[1]:
                clean_name = parts[1].split("_", 1)[1]
        else:
            clean_name = filename.replace(chore_filename + "_", "").replace(chore_filename, "")
            if clean_name.startswith("_"):
                clean_name = clean_name[1:]
        
        clean_name = os.path.splitext(clean_name)[0]
        expected_filename = f"{chore_filename}_pos_{idx:02d}_{clean_name}{ext}"
        
        if filename != expected_filename:
            new_path = os.path.join(dirname, expected_filename)
            try:
                os.rename(img_path, new_path)
                found_images[idx] = new_path
                normalized = True
            except:
                pass
                
    if normalized:
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
    
    # 3. Existing Photos Management & Reordering
    st.markdown("#### 📷 Manage Photos & Order")
    if found_images:
        st.write("You can reorder photos using the Move Up/Down buttons, or click Delete to remove them:")
        for idx, img_path in enumerate(found_images):
            img_filename = os.path.basename(img_path)
            
            # Clean filename for display (remove position prefix)
            display_name = img_filename
            pos_tag = f"_pos_{idx:02d}_"
            if pos_tag in img_filename:
                display_name = img_filename.split(pos_tag)[1]
                
            col_img, col_up, col_down, col_del = st.columns([5, 1, 1, 1])
            with col_img:
                st.caption(f"**Photo {idx+1}:** {display_name}")
            with col_up:
                if st.button("🔼", key=f"up_{img_filename}", disabled=(idx == 0)):
                    prev_path = found_images[idx - 1]
                    prev_filename = os.path.basename(prev_path)
                    
                    temp_path = img_path + ".tmp"
                    os.rename(img_path, temp_path)
                    
                    prev_new_filename = prev_filename.replace(f"_pos_{(idx-1):02d}_", f"_pos_{idx:02d}_")
                    prev_new_path = os.path.join(os.path.dirname(prev_path), prev_new_filename)
                    os.rename(prev_path, prev_new_path)
                    
                    curr_new_filename = img_filename.replace(f"_pos_{idx:02d}_", f"_pos_{(idx-1):02d}_")
                    curr_new_path = os.path.join(os.path.dirname(img_path), curr_new_filename)
                    os.rename(temp_path, curr_new_path)
                    
                    st.success("Reordered!")
                    st.rerun()
            with col_down:
                if st.button("🔽", key=f"down_{img_filename}", disabled=(idx == len(found_images) - 1)):
                    next_path = found_images[idx + 1]
                    next_filename = os.path.basename(next_path)
                    
                    temp_path = img_path + ".tmp"
                    os.rename(img_path, temp_path)
                    
                    next_new_filename = next_filename.replace(f"_pos_{(idx+1):02d}_", f"_pos_{idx:02d}_")
                    next_new_path = os.path.join(os.path.dirname(next_path), next_new_filename)
                    os.rename(next_path, next_new_path)
                    
                    curr_new_filename = img_filename.replace(f"_pos_{idx:02d}_", f"_pos_{(idx+1):02d}_")
                    curr_new_path = os.path.join(os.path.dirname(img_path), curr_new_filename)
                    os.rename(temp_path, curr_new_path)
                    
                    st.success("Reordered!")
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{img_filename}"):
                    try:
                        os.remove(img_path)
                        st.success("Deleted photo!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete: {e}")
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
                new_pos = len(found_images) + idx
                new_filename = f"{chore_filename}_pos_{new_pos:02d}_{timestamp}{ext}"
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
<div style="background-color: #f4f7f5; border-left: 5px solid #2e5a44; padding: 20px; border-radius: 8px; margin-top: 10px; box-shadow: 0 2px 6px rgba(46, 90, 68, 0.05);">
    <h4 style="margin-top: 0; color: #2e5a44; font-weight: 600; font-size: 1.15rem;">🏠 Home Reminder for the Brothers:</h4>
    <p style="color: #444; margin-bottom: 15px; font-size: 1.05rem; line-height: 1.5;">
        Let’s stay on top of our cleaning schedule and look after our shared space together. If you see something that needs attention outside of the roster, please step in and help out.
    </p>
    <p style="font-style: italic; color: #2e5a44; font-weight: 600; margin: 0; font-size: 1rem;">
        "Share with the Lord’s people who are in need. Practice hospitality." (Romans 12:13)
    </p>
</div>
""", unsafe_allow_html=True)


