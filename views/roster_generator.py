import streamlit as st
import random
import pandas as pd
import os
import json

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

# Initialize verse in session state if not present
if 'selected_verse' not in st.session_state:
    st.session_state.selected_verse = random.choice(BIBLE_VERSES)

# Page Title & Header
st.markdown("<h1 style='text-align: center; color: #2e5a44; margin-bottom: 0;'>🏠 Brother House Roster Guide</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #e76f51; font-weight: 700; font-size: 1.15rem; letter-spacing: 1px; margin-top: 5px; margin-bottom: 15px;'>✨ HOUSE OF JESUS LOVER ✨</p>", unsafe_allow_html=True)

# Display Random Bible Verse Card
verse = st.session_state.selected_verse
st.markdown(f"""
<div style="background-color: #fdfaf2; border: 1px solid #e6dfd3; padding: 20px 25px; border-radius: 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
    <p style="font-size: 1.15rem; color: #5c5549; font-style: italic; margin-bottom: 8px; line-height: 1.5; font-weight: 500;">
        "{verse['text']}"
    </p>
    <p style="font-size: 0.95rem; color: #2e5a44; font-weight: 700; margin: 0;">
        — {verse['reference']}
    </p>
</div>
""", unsafe_allow_html=True)

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
    
    # Add App URL field
    st.markdown("---")
    st.markdown("🌐 **Website URL Configuration (for WhatsApp links)**")
    app_url_input = st.text_input(
        "Live Deployed Website URL", 
        value=st.session_state.get("app_url", ""),
        placeholder="https://164-brothers-house.streamlit.app",
        help="Paste your live Streamlit website link here. When you copy the roster for WhatsApp, it will automatically append a direct link to the Chore Guide!"
    )
    
    # Save changes button
    if st.button("💾 Save Changes & Update Lists", use_container_width=True):
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
            
            # Save to text files for persistence
            with open("brothers.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(new_brothers))
            with open("chores.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(new_chores))
            
            # Save config.json
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump({"app_url": st.session_state.app_url}, f, ensure_ascii=False, indent=2)
                
            st.success("House roster lists and website config updated successfully!")
            st.rerun()

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
    
    # Save roster to JSON file for persistence
    roster_data = {
        "roster": new_roster,
        "off_duty": off_duty
    }
    with open("roster.json", "w", encoding="utf-8") as f:
        json.dump(roster_data, f, ensure_ascii=False, indent=2)

    # Automatically select a new Bible verse to go with the new roster
    st.session_state.selected_verse = random.choice(BIBLE_VERSES)
    st.success("✨ New chore roster generated successfully!")
    st.rerun()

# Roster Display Section
st.markdown("---")
st.markdown("<h2 style='color: #2e5a44;'>📅 Current Roster Assignments</h2>", unsafe_allow_html=True)

if not st.session_state.roster:
    st.info("No active roster found. Click 'Generate Roster' above to assign tasks!")
else:
    # Display Roster in a beautiful grid
    roster_items = list(st.session_state.roster.items())
    
    # Set columns for display
    cols = st.columns(3)
    
    for idx, (chore, assignees) in enumerate(roster_items):
        col_index = idx % 3
        with cols[col_index]:
            # HTML Card styling (Minimalist Left-Accent Card without emojis)
            st.markdown(f"""
            <div class="card">
                <div class="card-title">{chore}</div>
                <div class="card-subtitle">Assigned to:</div>
                <div class="card-assignee">{', '.join(assignees)}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button link to instructions
            cleaned_name = chore.replace(" ", "_").lower()
            # We can use button or link to switch page.
            # To switch page in Streamlit multi-page navigation, we can use a query parameter or st.Page execution,
            # but standard streamlit doesn't support direct cross-page anchor links in custom HTML cards,
            # so we can just show a helper text or a streamlit button. Let's add a button in each column.
            # Wait, a Streamlit button under each card is extremely neat and functional!
            if st.button(f"📖 Guide for {chore}", key=f"guide_btn_{idx}", use_container_width=True):
                st.session_state.selected_chore_guide = chore
                st.switch_page("views/chore_guide.py")

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
            whatsapp_lines.append(f"• *{chore}*: {', '.join(assignees)}")
        if st.session_state.off_duty:
            whatsapp_lines.append("")
            whatsapp_lines.append(f"💤 *Resting:* {', '.join(st.session_state.off_duty)}")
            
        # Add Guide redirect link if app_url is configured
        if st.session_state.get("app_url"):
            base_url = st.session_state.app_url.rstrip("/")
            # If they entered the full subpage path, strip it out to point to the main page
            if base_url.lower().endswith("/chore_guide"):
                base_url = base_url[:-12].rstrip("/")
            whatsapp_lines.append("")
            whatsapp_lines.append(f"📖 *View Detailed Guide:* {base_url}")
            
        # Completion checkmark instructions
        whatsapp_lines.append("")
        whatsapp_lines.append("Brothers, once you complete your cleaning task, please give a tick emoji (✅) to this message so we know it’s done. Thank you!")
        
        whatsapp_text = "\n".join(whatsapp_lines)
        st.code(whatsapp_text, language="text")

    # Print / Clear Buttons
    st.markdown("<hr>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 2])
    with c_btn1:
        if st.button("❌ Clear Roster", use_container_width=True):
            st.session_state.roster = {}
            st.session_state.off_duty = []
            
            # Remove roster file if it exists
            if os.path.exists("roster.json"):
                try:
                    os.remove("roster.json")
                except:
                    pass
                    
            st.success("Roster cleared.")
            st.rerun()
            
    with c_btn2:
        # Convert roster to CSV for download
        df_data = []
        for chore, assignees in st.session_state.roster.items():
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
        st.caption("Tip: You can print this page using your browser's print shortcut (Ctrl+P or Cmd+P) to post it on the fridge!")
