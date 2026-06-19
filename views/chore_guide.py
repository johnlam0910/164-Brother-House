import streamlit as st
import os
import json
import time
import pandas as pd
import re

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

# If OneDrive URL is set, display a premium-looking CTA link button
onedrive_url = details.get("onedrive_url", "")
if onedrive_url:
    st.markdown(f"""
    <div style="background-color: #e8f5e9; border-left: 5px solid #2e5a44; padding: 12px 18px; border-radius: 8px; margin-top: 10px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">🎬</span>
            <span style="font-weight: 600; color: #2e5a44;">OneDrive Video & Document Guide is available for this task!</span>
        </div>
        <a href="{onedrive_url}" target="_blank" style="background-color: #2e5a44; color: white !important; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: background-color 0.2s;">View Guide ↗</a>
    </div>
    """, unsafe_allow_html=True)

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
    chore_filename = selected_chore.lower().replace(" ", "_")
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
    
    # 2.5. Edit OneDrive URL
    current_onedrive_url = details.get("onedrive_url", "")
    edited_onedrive_url = st.text_input("OneDrive Guide URL (video or document link):", value=current_onedrive_url)
    
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
    chore_key = selected_chore.lower().replace(" ", "_")
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
            "steps": steps_list,
            "onedrive_url": edited_onedrive_url.strip()
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
            chore_filename = selected_chore.lower().replace(" ", "_")
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

# Import from Excel Expander
with st.expander("📥 Import Chores & Instructions from Excel", expanded=False):
    st.markdown("### 📊 Import Chores from Spreadsheet")
    st.write("Upload an Excel file containing your chores, tools, cleaning steps, and OneDrive URLs to load them automatically into the guide.")
    
    uploaded_excel = st.file_uploader(
        "Upload Excel File:", 
        type=["xlsx", "xls"], 
        key="excel_uploader"
    )
    
    if uploaded_excel is not None:
        try:
            # Load sheet names first
            xls = pd.ExcelFile(uploaded_excel)
            sheet_name = st.selectbox("Select Sheet to read:", options=xls.sheet_names, key="excel_sheet_select")
            
            # Read selected sheet
            df = pd.read_excel(uploaded_excel, sheet_name=sheet_name)
            
            if df.empty:
                st.warning("The selected sheet is empty. Please check your Excel file.")
            else:
                st.markdown("#### 🔍 Excel Preview")
                st.dataframe(df.head(5), use_container_width=True)
                
                st.markdown("#### 🗺️ Column Mapping")
                st.write("Match columns from your Excel file to the app's fields:")
                
                columns = list(df.columns)
                
                # Try to auto-detect defaults based on common patterns
                def get_default_col(options, patterns):
                    for p in patterns:
                        for opt in options:
                            if p.lower() in str(opt).lower():
                                return options.index(opt)
                    return 0
                
                chore_col = st.selectbox(
                    "🔑 Chore Name / Task Name Column:", 
                    options=columns,
                    index=get_default_col(columns, ["chore", "task", "job", "name", "title"])
                )
                
                tools_col = st.selectbox(
                    "🛠️ Required Tools Column (Optional):", 
                    options=["-- None / Skip --"] + columns,
                    index=get_default_col(["-- None / Skip --"] + columns, ["tool", "supply", "equipment", "material"])
                )
                
                steps_col = st.selectbox(
                    "📝 Instructions / Cleaning Steps Column:", 
                    options=columns,
                    index=get_default_col(columns, ["step", "instruction", "how", "guideline", "description", "content"])
                )
                
                url_col = st.selectbox(
                    "🎬 OneDrive URL Column (Optional):", 
                    options=["-- None / Skip --"] + columns,
                    index=get_default_col(["-- None / Skip --"] + columns, ["onedrive", "url", "link", "video", "folder"])
                )
                
                st.markdown("#### ⚙️ Import Options")
                
                sync_chores = st.checkbox(
                    "➕ Automatically add new chores to House Roster (chores.txt)", 
                    value=True,
                    help="If your Excel has chores that are not yet in the system, check this to automatically register them so they can be assigned in the Roster Generator."
                )
                
                import_mode = st.radio(
                    "🔄 Import Mode:",
                    options=["Merge & Update (Update matching chores, keep others)", "Overwrite All (Delete existing instructions, load only from Excel)"],
                    index=0
                )
                
                # Confirm Button
                if st.button("🚀 Confirm & Import Data", type="primary", use_container_width=True):
                    # Process the spreadsheet data
                    imported_count = 0
                    new_chores_added = []
                    
                    # Target instructions dict
                    target_details = {} if "Overwrite" in import_mode else st.session_state.chore_details.copy()
                    
                    # Convert to string to avoid NaNs crashing things, fillna with empty string
                    df_clean = df.copy()
                    for col in [chore_col, steps_col]:
                        df_clean[col] = df_clean[col].fillna("").astype(str)
                    
                    if tools_col != "-- None / Skip --":
                        df_clean[tools_col] = df_clean[tools_col].fillna("").astype(str)
                    if url_col != "-- None / Skip --":
                        df_clean[url_col] = df_clean[url_col].fillna("").astype(str)
                        
                    for _, row in df_clean.iterrows():
                        chore_name = row[chore_col].strip()
                        if not chore_name:
                            continue
                            
                        # Parse steps
                        raw_steps = row[steps_col].strip()
                        # Split by newlines or numbers/bullets (1. or - or *)
                        steps_list = []
                        if raw_steps:
                            # Split into lines
                            lines = [line.strip() for line in raw_steps.split("\n") if line.strip()]
                            for line in lines:
                                # Clean up leading numbering/bullets like "1. ", "2) ", "- ", "* "
                                cleaned_line = re.sub(r'^(?:\d+[\.\)]|[-*•])\s*', '', line).strip()
                                if cleaned_line:
                                    steps_list.append(cleaned_line)
                        if not steps_list:
                            steps_list = ["No steps written in spreadsheet."]
                            
                        # Parse tools
                        tools_list = ["General cleaning supplies"]
                        if tools_col != "-- None / Skip --":
                            raw_tools = row[tools_col].strip()
                            if raw_tools:
                                # Split by comma or semicolon or newline
                                split_tools = re.split(r'[,;\n]', raw_tools)
                                tools_list = [t.strip() for t in split_tools if t.strip()]
                        
                        # Parse OneDrive URL
                        onedrive_val = ""
                        if url_col != "-- None / Skip --":
                            onedrive_val = row[url_col].strip()
                            
                        target_details[chore_name] = {
                            "tools": tools_list,
                            "steps": steps_list,
                            "onedrive_url": onedrive_val
                        }
                        imported_count += 1
                        
                        # If sync_chores is selected, track if this is a new chore
                        if sync_chores and chore_name not in st.session_state.chores_list:
                            new_chores_added.append(chore_name)
                    
                    # Update session state
                    st.session_state.chore_details = target_details
                    
                    # Save instructions to instructions.json
                    try:
                        with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
                            json.dump(target_details, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        st.error(f"Failed to save imported instructions to file: {e}")
                        
                    # Sync to chores list if new ones were added
                    if new_chores_added:
                        updated_chores = st.session_state.chores_list.copy()
                        for nc in new_chores_added:
                            if nc not in updated_chores:
                                updated_chores.append(nc)
                                
                        st.session_state.chores_list = updated_chores
                        try:
                            with open("chores.txt", "w", encoding="utf-8") as f:
                                f.write("\n".join(updated_chores))
                        except Exception as e:
                            st.error(f"Failed to update chores.txt: {e}")
                            
                    st.success(f"🎉 Successfully imported {imported_count} chores from sheet '{sheet_name}'!")
                    if new_chores_added:
                        st.info(f"➕ Registered {len(new_chores_added)} new chores to House Roster: {', '.join(new_chores_added)}")
                    
                    # Delay slightly for the user to see the success message, then rerun
                    time.sleep(1.5)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error parsing Excel file: {e}")

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


