import streamlit as st
import os
import json

BROTHERS_FILE = "brothers.txt"
CHORES_FILE = "chores.txt"
ROSTER_FILE = "roster.json"

DEFAULT_BROTHERS = [
    "John", "David", "Michael", "James", 
    "Andrew", "Robert", "William", "Joseph", "Daniel"
]

DEFAULT_CHORES = [
    "Staircase", "Back Yard", "Front Yard",
    "Dining Table", "Mop Floor", "Toilet",
    "Inside Kitchen", "Sweep Floor", "Outside Kitchen"
]

# Default Chore Content Definitions (used as fallbacks to initialize instructions.json)
DEFAULT_INSTRUCTIONS = {
    "Staircase": {
        "tools": ["Broom / Hand vacuum", "Microfiber cloth", "All-purpose spray"],
        "steps": [
            "Start from the **top step** and work your way down. This ensures dust falls to steps you haven't cleaned yet.",
            "Sweep or vacuum each step carefully, paying close attention to the corners where dust gathers.",
            "Use the multi-purpose spray and microfiber cloth to wipe down the **entire handrail** and banister posts. These are high-touch areas that accumulate germs.",
            "Clear away any shoes, bags, or items left on the staircase and place them in their designated locations.",
            "Inspect the steps for any scuffs or spots and scrub them gently with a damp sponge."
        ]
    },
    "Back Yard": {
        "tools": ["Outdoor push broom", "Trash bags", "Garden hose"],
        "steps": [
            "Sweep the concrete patio area and pathways to clear leaves, twigs, and dust.",
            "Inspect the garden and lawn for any stray rubbish or weeds. Gather and dispose of them.",
            "Empty the outdoor waste bins if they are more than half full. Replace with fresh liners.",
            "Wipe down the outdoor dining table and chairs with a damp cloth.",
            "Neatly coil the garden hose and make sure gardening tools are placed back in the storage bin."
        ]
    },
    "Front Yard": {
        "tools": ["Outdoor broom", "Weeding tool", "Watering can / Hose"],
        "steps": [
            "Sweep the main entry path, porch, and driveway clear of dirt and leaves.",
            "Remove any weeds growing in the pathway cracks or flowerbeds near the front door.",
            "Water the potted plants and garden beds near the entryway (if it hasn't rained).",
            "Check for any letters or pamphlets left by the gate/doorway and bring them inside to the mail stack.",
            "Ensure the bins are placed neatly on the curb if it's collection day, or returned to their side area if collection is done."
        ]
    },
    "Dining Table": {
        "tools": ["Sponges", "Dish soap / Surface spray", "Dry dishcloth"],
        "steps": [
            "Clear all remaining dishes, cups, cutlery, and condiment bottles to the kitchen sink.",
            "Wipe down the table surface with a soapy sponge to remove grease and food particles.",
            "Spray table surface with disinfectant and wipe dry with a clean microfiber cloth.",
            "Tidy and wipe down the chairs, tucking them in neatly under the table.",
            "Ensure the salt, pepper, and decorative centerpieces are cleaned and placed back in the center."
        ]
    },
    "Mop Floor": {
        "tools": ["Mop", "Bucket", "Floor cleaner solution", "Warm water"],
        "steps": [
            "**Crucial Step:** Ensure the floors have been swept or vacuumed thoroughly before you begin mopping.",
            "Fill the bucket with warm water and mix in the recommended amount of floor cleaner.",
            "Dip the mop, wring it out well (mop should be damp, not dripping wet), and mop using a **figure-8 motion**.",
            "Work backwards towards the exit so you don't step on damp floor surfaces.",
            "Change the mop water if it starts looking dark or dirty.",
            "Place a warning sign or notify housemates to stay off the floor until dry (approx. 15-20 mins)."
        ]
    },
    "Toilet": {
        "tools": ["Toilet brush", "Disinfectant spray", "Glass cleaner", "Paper towels / Cleaning cloths"],
        "steps": [
            "Squirt toilet bowl cleaner inside the rim of the bowl. Let it sit for 10 minutes to sanitize.",
            "Wipe the mirror with glass cleaner and a microfiber cloth until streak-free.",
            "Spray and wipe down the sink basin, taps, countertops, and cabinet surfaces.",
            "Scrub the inside of the toilet bowl thoroughly with the brush and flush.",
            "Wipe the entire exterior of the toilet (seat, lid, base, flush handle) with disinfectant and paper towels (discard towels immediately).",
            "Empty the hygiene waste bin, spray it with disinfectant, and put in a new bag.",
            "Check and refill hand soap, toilet rolls, and replace the hand towel with a clean one."
        ]
    },
    "Inside Kitchen": {
        "tools": ["Dish sponge", "Degreaser spray", "Stainless steel cleaner", "Scouring pad"],
        "steps": [
            "Wash, dry, and put away all dishes, pots, and pans left in the sink area.",
            "Clean the stove cooktop, removing any burnt grease or spills using a sponge and degreaser.",
            "Wipe down countertops, microwave interior, and cabinet handles with kitchen spray.",
            "Scrub the kitchen sink basin and clean out the drain strainer.",
            "Empty the kitchen trash and compost bins. Wipe the inside of the lids with disinfectant.",
            "Fold and hang dish towels to dry, replacing damp ones with fresh towels."
        ]
    },
    "Sweep Floor": {
        "tools": ["Broom", "Dustpan", "Hand brush"],
        "steps": [
            "Clear lightweight furniture like dining chairs, trash bins, and rugs from the floor area.",
            "Sweep the floor starting from the corners and moving towards the center of the room.",
            "Gather the debris into a pile, sweep it into the dustpan, and empty it into the main trash bin.",
            "Ensure you sweep under the dining table, kitchen benches, and main entryway where crumbs accumulate.",
            "Inspect the broom head and clear away any trapped hair or fluff into the trash."
        ]
    },
    "Outside Kitchen": {
        "tools": ["Wire grill brush", "Warm soapy water", "Heavy-duty sponge", "Outdoor broom"],
        "steps": [
            "Scrub the BBQ grill grates with the wire brush to remove food residue. Wipe grates down with cooking oil.",
            "Wipe down outdoor countertops, sink basin, and prep benches with soapy water.",
            "Clean and empty the grease drip tray underneath the grill. Replace tin foil liner if needed.",
            "Sweep the surrounding concrete floor, removing grease spots with degreaser if necessary.",
            "**Safety Check:** Double-check that all gas cylinders are tightly shut off and the covers are placed securely back on the BBQ."
        ]
    }
}

INSTRUCTIONS_FILE = "instructions.json"

if 'brothers_list' not in st.session_state:
    if os.path.exists(BROTHERS_FILE):
        with open(BROTHERS_FILE, "r", encoding="utf-8") as f:
            st.session_state.brothers_list = [line.strip() for line in f if line.strip()]
    else:
        st.session_state.brothers_list = DEFAULT_BROTHERS
        with open(BROTHERS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_BROTHERS))

if 'chores_list' not in st.session_state:
    if os.path.exists(CHORES_FILE):
        with open(CHORES_FILE, "r", encoding="utf-8") as f:
            st.session_state.chores_list = [line.strip() for line in f if line.strip()]
    else:
        st.session_state.chores_list = DEFAULT_CHORES
        with open(CHORES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_CHORES))

if 'roster' not in st.session_state:
    if os.path.exists(ROSTER_FILE):
        try:
            with open(ROSTER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.roster = data.get("roster", {})
                st.session_state.off_duty = data.get("off_duty", [])
        except:
            st.session_state.roster = {}
            st.session_state.off_duty = []
    else:
        st.session_state.roster = {}
        st.session_state.off_duty = []

# Load or generate instructions.json
if 'chore_details' not in st.session_state:
    if os.path.exists(INSTRUCTIONS_FILE) and os.path.getsize(INSTRUCTIONS_FILE) > 0:
        try:
            with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
                st.session_state.chore_details = json.load(f)
        except:
            st.session_state.chore_details = DEFAULT_INSTRUCTIONS.copy()
    else:
        st.session_state.chore_details = DEFAULT_INSTRUCTIONS.copy()
        with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_INSTRUCTIONS, f, ensure_ascii=False, indent=2)

# Load app_url configuration
CONFIG_FILE = "config.json"
if 'app_url' not in st.session_state:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                st.session_state.app_url = config.get("app_url", "")
        except:
            st.session_state.app_url = ""
    else:
        st.session_state.app_url = ""

# 2. Page Navigation definitions using modern st.Page syntax
roster_page = st.Page("views/roster_generator.py", title="Roster Generator", icon="📋", default=True)
guide_page = st.Page("views/chore_guide.py", title="Chore Guide", icon="📖")

pg = st.navigation([roster_page, guide_page])

# 3. Set global page configuration (mandatory call before other streamlit visual commands)
st.set_page_config(page_title="House Chores System", page_icon="🏠", layout="wide")

# 4. Global CSS Styles for warm, premium, community-themed aesthetics (Google Font "Outfit")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Apply font globally to all widgets and layouts */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Soft, warm background color */
    .stApp {
        background-color: #faf9f6;
    }
    
    /* Sidebar warm panel background */
    section[data-testid="stSidebar"] {
        background-color: #f2efe9 !important;
    }
    
    /* Styled container for chore cards */
    .card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(46, 90, 68, 0.05);
        border: 1px solid #e8edea;
        border-left: 5px solid #2e5a44;
        text-align: left;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(46, 90, 68, 0.12);
        border-color: #2e5a44;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2e5a44;
        margin-bottom: 6px;
    }
    .card-subtitle {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #888;
        margin-bottom: 2px;
    }
    .card-assignee {
        font-size: 1.1rem;
        font-weight: 700;
        color: #222222;
    }
    
    /* Fallback image design box */
    .fallback-image-box {
        border: 2px dashed #bdc3c7;
        border-radius: 12px;
        background-color: #f9f9f9;
        padding: 45px 20px;
        text-align: center;
        margin-top: 10px;
        transition: border-color 0.2s ease;
    }
    .fallback-image-box:hover {
        border-color: #7f8c8d;
    }
    
    /* Styling primary Streamlit buttons for organic green color scheme */
    div.stButton > button[kind="primary"] {
        background-color: #2e5a44 !important;
        border-color: #2e5a44 !important;
        color: white !important;
        font-weight: 600 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #1d3b2c !important;
        border-color: #1d3b2c !important;
    }
    
    /* Text input styling focus */
    .stTextArea textarea {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# 5. Global Sidebar content (runs on all sub-pages)
st.sidebar.markdown("<h2 style='color: #2e5a44; margin-top: 0; font-size: 1.6rem;'>🏠 164 Brothers House</h2>", unsafe_allow_html=True)
st.sidebar.markdown("""
Welcome to the 164 Brothers House! This is a place where brothers live together in love. We love to open our home to welcome gospel friends and visiting saints. Because this house is a place to serve others, let us work together to keep it clean, neat, and ready for everyone.

歡迎來到 164 弟兄之家！這是一個共同生活、接待福音朋友和聖徒的地方。讓我們一起保持家中的整潔與溫馨。
""")
st.sidebar.markdown("---")

# Counts for validation checks
n_brothers = len(st.session_state.brothers_list)
n_chores = len(st.session_state.chores_list)

st.sidebar.markdown("<h4 style='color: #2e5a44; margin-bottom: 5px;'>📋 Roster Status</h4>", unsafe_allow_html=True)
if n_brothers == n_chores:
    st.sidebar.success("✅ **Count Matches:** Ready!")
    st.sidebar.caption(f"Perfect match: {n_brothers} Brothers & {n_chores} Chores.")
else:
    st.sidebar.warning("⚠️ **Count Mismatch:**")
    st.sidebar.markdown(
        f"<div style='font-size: 0.85rem; color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 6px; margin-bottom: 10px; font-weight: 500;'>"
        f"Ensure the number of brothers matches the number of chores.<br><br>"
        f"Current counts:<br>"
        f"• Brothers: <b>{n_brothers}</b><br>"
        f"• Chores: <b>{n_chores}</b>"
        f"</div>", 
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")

# 6. Run selected page routing
pg.run()
