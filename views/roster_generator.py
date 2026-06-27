import streamlit as st
import random
import pandas as pd
import os
import json
from utils import get_supabase_client, db_set
import urllib.parse

DEFAULT_BROTHERS = [
    "John", "David", "Michael", "James", 
    "Andrew", "Robert", "William", "Joseph", "Daniel"
]

DEFAULT_CHORES = [
    "Staircase (Sweep Second & Third Floor)", "Back Yard", "Front Yard",
    "Dining Table + (Mop Second & Third Floor)", "Mop Floor", "Toilet",
    "Inside Kitchen", "Sweep Floor", "Outside Kitchen"
]


# Bible Verses Collection
BIBLE_VERSES = [
    {
        "reference": "Hebrews 10:24",
        "text": "And let us consider how we may spur one another on toward love and good deeds."
    },
    {
        "reference": "Galatians 6:2",
        "text": "Carry each other’s burdens, and in this way you will fulfill the law of Christ."
    },
    {
        "reference": "Hebrews 13:16",
        "text": "And do not forget to do good and to share with others, for with such sacrifices God is pleased."
    },
    {
        "reference": "1 John 3:17-18",
        "text": "If anyone has material possessions and sees a brother or sister in need but has no pity on them, how can the love of God be in that person? Dear children, let us not love with words or speech but with actions and in truth."
    },
    {
        "reference": "Psalm 133:1",
        "text": "How good and pleasant it is when God’s people live together in unity!"
    },
    {
        "reference": "Colossians 3:23",
        "text": "Whatever you do, work at it with all your heart, as working for the Lord, not for human masters."
    }
]

# Initialize verse in session state if not present or malformed
if ('selected_verse' not in st.session_state 
        or not isinstance(st.session_state.selected_verse, dict) 
        or 'text' not in st.session_state.selected_verse 
        or 'reference' not in st.session_state.selected_verse):
    st.session_state.selected_verse = random.choice(BIBLE_VERSES)

# Page Title & Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🏠 Brother House Roster Guide</h1>
    <p class="main-subtitle">✨ HOUSE OF JESUS LOVER ✨</p>
</div>
""", unsafe_allow_html=True)

# Display Random Bible Verse Card
verse = st.session_state.selected_verse
st.markdown(f"""
<div class="bible-verse-card">
    <p class="bible-verse-text">
        "{verse['text']}"
    </p>
    <p class="bible-verse-ref">
        — {verse['reference']}
    </p>
</div>
""", unsafe_allow_html=True)

# Render success messages across reruns
if "success_msg" in st.session_state:
    st.success(st.session_state.success_msg)
    del st.session_state.success_msg

# Navigation row for changing the verse manually
vc_col1, vc_col2 = st.columns([8, 2])
with vc_col2:
    if st.button("🔄 Next Bible Verse", key="next_verse_btn", use_container_width=True):
        st.session_state.selected_verse = random.choice(BIBLE_VERSES)
        st.rerun()

st.markdown("---")

# Expandable section for editing list of brothers and chores
with st.expander("🛠️ Edit Names & Tasks", expanded=False):
    st.markdown("Modify the lists below to add, remove, or change the house members and chores.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brothers_text = st.text_area(
            "Brothers (one per line)", 
            value="\n".join(st.session_state.brothers_list), 
            height=250,
            help="Enter the names of the brothers in the house, one name per line."
        )
        
    with col2:
        chores_text = st.text_area(
            "Chores (one per line)", 
            value="\n".join(st.session_state.chores_list), 
            height=250,
            help="Enter the list of chores, one chore per line."
        )
    
    # Add App URL field collapsed inside Advanced Settings sub-expander
    st.markdown("---")
    with st.expander("⚙️ Advanced Settings (Website URL)", expanded=False):
        st.markdown("🌐 **Website URL Configuration (for WhatsApp links)**")
        app_url_input = st.text_input(
            "Live Deployed Website URL", 
            value=st.session_state.get("app_url", ""),
            placeholder="https://164-brothers-house.streamlit.app",
            help="Paste your live Streamlit website link here. When you copy the roster for WhatsApp, it will automatically append a direct link to the Chore Guide!"
        )
        # Warn if URL is localhost (won't work from other devices)
        if app_url_input and ("localhost" in app_url_input or "127.0.0.1" in app_url_input):
            st.warning(
                "⚠️ **localhost links won't work on other devices!** "
                "Please deploy your app (e.g., to Streamlit Cloud) and enter the live URL here. "
                "For example: `https://164-brothers-house.streamlit.app`"
            )
            
    # Save/Revert buttons in double columns
    st.markdown("<br>", unsafe_allow_html=True)
    col_save, col_revert = st.columns([1, 1])
    
    with col_save:
        save_btn = st.button("💾 Save Changes & Update Lists", use_container_width=True)
    with col_revert:
        revert_btn = st.button("⏪ Revert to Default Lists", help="Restore the default list of brothers and chores.", use_container_width=True)
        
    if save_btn:
        new_brothers = [line.strip() for line in brothers_text.split("\n") if line.strip()]
        new_chores = [line.strip() for line in chores_text.split("\n") if line.strip()]
        
        if not new_brothers:
            st.error("Validation Error: Please enter at least one Brother name.")
        elif not new_chores:
            st.error("Validation Error: Please enter at least one Chore.")
        else:
            st.session_state.brothers_list = new_brothers
            st.session_state.chores_list = new_chores
            st.session_state.app_url = app_url_input.strip()
            
            # Clean up active roster: remove deleted chores, and remove deleted brothers from assignees
            if 'roster' in st.session_state and st.session_state.roster:
                cleaned_roster = {}
                for chore, assignees in st.session_state.roster.items():
                    if chore in new_chores:
                        cleaned_assignees = [a for a in assignees if a in new_brothers]
                        if cleaned_assignees:
                            cleaned_roster[chore] = cleaned_assignees
                st.session_state.roster = cleaned_roster
                
                # Filter off_duty list as well
                st.session_state.off_duty = [b for b in st.session_state.off_duty if b in new_brothers]
                
                # Save cleaned roster to file
                try:
                    roster_data = {
                        "roster": st.session_state.roster,
                        "off_duty": st.session_state.off_duty
                    }
                    with open("roster.json", "w", encoding="utf-8") as f:
                        json.dump(roster_data, f, ensure_ascii=False, indent=2)
                except:
                    pass
            
            # Save to Supabase if connected
            if get_supabase_client() is not None:
                db_set("brothers_list", new_brothers)
                db_set("chores_list", new_chores)
                db_set("config", {"app_url": st.session_state.app_url})
                if 'roster' in st.session_state and st.session_state.roster:
                    db_set("roster", {
                        "roster": st.session_state.roster,
                        "off_duty": st.session_state.off_duty
                    })

            # Save to text files for persistence
            with open("brothers.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(new_brothers))
            with open("chores.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(new_chores))
            
            # Save config.json
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump({"app_url": st.session_state.app_url}, f, ensure_ascii=False, indent=2)
                
            st.session_state.success_msg = "House roster lists and website config updated successfully!"
            st.rerun()

    if revert_btn:
        st.session_state.brothers_list = DEFAULT_BROTHERS.copy()
        st.session_state.chores_list = DEFAULT_CHORES.copy()
        
        # Save to Supabase if connected
        if get_supabase_client() is not None:
            db_set("brothers_list", DEFAULT_BROTHERS)
            db_set("chores_list", DEFAULT_CHORES)
            
        # Save to local text files for persistence
        with open("brothers.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_BROTHERS))
        with open("chores.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_CHORES))
            
        st.session_state.success_msg = "⏪ Successfully reverted brothers and chores lists to defaults!"
        st.rerun()



# Roster count mismatch warning (prominent check for mobile viewports where sidebar is collapsed)
n_brothers = len(st.session_state.brothers_list)
n_chores = len(st.session_state.chores_list)
if n_brothers != n_chores:
    st.warning(
        f"⚠️ **Roster Count Mismatch:** You have **{n_brothers}** brothers and **{n_chores}** chores. "
        f"Generating the roster will assign some brothers multiple chores or put them on the off-duty rest list. "
        f"You can adjust these in the 'Edit Names & Tasks' section above."
    )

# Layout for Generation Action
st.markdown("<h3 style='color: #2e5a44;'>🎲 Roster Generation</h3>", unsafe_allow_html=True)
gen_col1, gen_col2 = st.columns([3, 1])

with gen_col1:
    st.markdown("Click the button to assign the brothers to their house duties. The roster is saved and will remain the same as you use the app.")

with gen_col2:
    generate_btn = st.button("🎲 Generate Roster", type="primary", use_container_width=True)

if generate_btn:
    brothers = st.session_state.brothers_list.copy()
    chores = st.session_state.chores_list.copy()
    
    if not brothers or not chores:
        st.error("Cannot generate roster: Brothers or Chores list is empty!")
    else:
        # Shuffle brothers to make the pairing random
        random.shuffle(brothers)
        
        new_roster = {}
        off_duty = []
        
        # Handle matching logic based on counts
        if len(brothers) == len(chores):
            # Perfect 1-to-1 match
            for chore, brother in zip(chores, brothers):
                new_roster[chore] = [brother]
        elif len(brothers) < len(chores):
            # Fewer brothers than chores: some brothers do multiple chores
            for idx, chore in enumerate(chores):
                assigned_brother = brothers[idx % len(brothers)]
                if chore in new_roster:
                    new_roster[chore].append(assigned_brother)
                else:
                    new_roster[chore] = [assigned_brother]
        else:
            # More brothers than chores: some brothers are off duty
            assigned_brothers = brothers[:len(chores)]
            off_duty = brothers[len(chores):]
            for chore, brother in zip(chores, assigned_brothers):
                new_roster[chore] = [brother]
                
        st.session_state.roster = new_roster
        st.session_state.off_duty = off_duty
        
        # Save roster to JSON file and Supabase for persistence
        roster_data = {
            "roster": new_roster,
            "off_duty": off_duty
        }
        if get_supabase_client() is not None:
            db_set("roster", roster_data)
        with open("roster.json", "w", encoding="utf-8") as f:
            json.dump(roster_data, f, ensure_ascii=False, indent=2)
    
        # Automatically select a new Bible verse to go with the new roster
        st.session_state.selected_verse = random.choice(BIBLE_VERSES)
        st.session_state.success_msg = "✨ New chore roster generated successfully!"
        st.rerun()

# Roster Display Section
st.markdown("---")
st.markdown("<h2 style='color: #2e5a44;'>📅 Current Roster Assignments</h2>", unsafe_allow_html=True)

if not st.session_state.roster:
    st.info("No active roster found. Click 'Generate Roster' above to assign tasks!")
else:
    # Display Roster in a beautiful grid
    roster_items = list(st.session_state.roster.items())
    
    # Display Roster in a beautiful responsive grid of compact cards (prevents long vertical scrolling on mobile)
    grid_html = ["<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px;'>"]
    
    for chore, assignees in roster_items:
        # Defensive check for single-string assignees (backward compatibility)
        if isinstance(assignees, str):
            assignees = [assignees]
        encoded_chore = urllib.parse.quote(chore)
        grid_html.append(f"""<div class="compact-card">
<div class="compact-card-title">{chore}</div>
<div class="compact-card-subtitle">Assigned to:</div>
<div class="compact-card-assignee">{', '.join(assignees)}</div>
<div style="margin-top: 4px;">
<span class="compact-card-link">📖 View Guide</span>
</div>
<a href="/chore_guide?chore={encoded_chore}" target="_self" class="compact-card-overlay-link"></a>
</div>""")
        
    grid_html.append("</div>")
    st.markdown("".join(grid_html), unsafe_allow_html=True)

    # Show off duty brothers if any
    if st.session_state.off_duty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2e5a44;'>💤 Off Duty / Rest List</h3>", unsafe_allow_html=True)
        off_duty_names = ", ".join(st.session_state.off_duty)
        st.markdown(f"""
        <div style="background-color: #e8f0fe; border-left: 5px solid #1a73e8; padding: 15px; border-radius: 8px;">
            <p style="margin: 0; font-size: 1.1rem; color: #1557b0;">
                <strong>Resting this cycle:</strong> {off_duty_names} — Enjoy your time off!
            </p>
        </div>
        """, unsafe_allow_html=True)

    # WhatsApp Copy Box
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📱 Copy for WhatsApp / Group Chat", expanded=True):
        st.markdown("Click the copy icon on the top-right of the text block below to copy and paste directly into WhatsApp:")
        verse = st.session_state.selected_verse
        
        # Determine base URL for chore guide deep links
        raw_app_url = st.session_state.get("app_url", "")
        is_localhost = "localhost" in raw_app_url or "127.0.0.1" in raw_app_url
        app_url_configured = bool(raw_app_url) and not is_localhost
        base_url = ""
        if app_url_configured:
            base_url = raw_app_url.rstrip("/")
            # If they entered the full subpage path, strip it out to point to the main page
            if base_url.lower().endswith("/chore_guide"):
                base_url = base_url[:-12].rstrip("/")
        
        whatsapp_lines = [
            "🏡 *164 Brothers House Chore Roster* 🏡",
            "",
            f'"{verse["text"]}"',
            f'— {verse["reference"]}',
            "",
            "---",
            ""
        ]
        for chore, assignees in st.session_state.roster.items():
            line = f"• *{chore}*: {', '.join(assignees)}"
            whatsapp_lines.append(line)
        if st.session_state.off_duty:
            whatsapp_lines.append("")
            whatsapp_lines.append(f"💤 *Resting:* {', '.join(st.session_state.off_duty)}")
            
        # Add a general guide link if app_url is configured
        if app_url_configured:
            whatsapp_lines.append("")
            whatsapp_lines.append(f"📖 *View Full Guide*: {base_url}/chore_guide")
            
        # Completion checkmark instructions
        whatsapp_lines.append("")
        whatsapp_lines.append("Brothers, once you complete your cleaning task, please give a tick emoji (✅) to this message so we know it’s done. Thank you!")
        
        whatsapp_text = "\n".join(whatsapp_lines)
        st.code(whatsapp_text, language="text")
        
        # Show a warning if URL is localhost
        if is_localhost:
            st.warning(
                "⚠️ **Guide links are not included** because your Website URL is set to `localhost`. "
                "Localhost links only work on your own computer — they won't open on anyone else's phone. "
                "To fix this:\n"
                "1. Deploy your app to **Streamlit Cloud** (free)\n"
                "2. Update the **Website URL** in '🛠️ Edit Names & Tasks' above with your live URL\n"
                "3. Re-generate the roster to get working links"
            )
        elif not app_url_configured:
            st.info(
                "💡 **Tip:** Set your deployed website URL in '🛠️ Edit Names & Tasks' above "
                "to include clickable Guide links for each chore."
            )

    # Print / Clear Buttons
    st.markdown("<hr>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns([1.2, 1.2, 1.5, 2.1])
    with c_btn1:
        if st.button("❌ Clear Roster", use_container_width=True):
            st.session_state.roster = {}
            st.session_state.off_duty = []
            
            # Reset database roster if connected
            if get_supabase_client() is not None:
                db_set("roster", {"roster": {}, "off_duty": []})
                
            # Remove roster file if it exists
            if os.path.exists("roster.json"):
                try:
                    os.remove("roster.json")
                except:
                    pass
                    
            st.session_state.success_msg = "Roster cleared."
            st.rerun()
            
    with c_btn2:
        # Convert roster to CSV for download
        df_data = []
        for chore, assignees in st.session_state.roster.items():
            if isinstance(assignees, str):
                assignees = [assignees]
            df_data.append({"Chore": chore, "Assigned Brothers": ", ".join(assignees)})
        
        if df_data:
            df = pd.DataFrame(df_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                "chore_roster.csv",
                "text/csv",
                use_container_width=True
            )
            
    with c_btn3:
        # Generate and copy share link
        raw_app_url = st.session_state.get("app_url", "")
        is_localhost = "localhost" in raw_app_url or "127.0.0.1" in raw_app_url
        app_url_configured = bool(raw_app_url) and not is_localhost
        if app_url_configured and st.session_state.roster:
            from utils import encode_roster
            encoded_val = encode_roster(
                st.session_state.roster,
                st.session_state.off_duty,
                st.session_state.selected_verse
            )
            share_url = f"{raw_app_url.rstrip('/')}/?r={encoded_val}"
            with st.popover("🔗 Share Link", use_container_width=True):
                st.caption("Copy this link to share the current roster, off-duty list, and Bible verse:")
                st.code(share_url, language="text")
        else:
            st.button("🔗 Share Link", disabled=True, use_container_width=True, help="Configure Website URL and generate a roster to enable sharing.")
            
    with c_btn4:
        st.caption("Tip: You can print this page using your browser's print shortcut (Ctrl+P or Cmd+P) to post it on the fridge!")
