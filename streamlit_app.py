import streamlit as st
import os
import json
from utils import decode_roster, get_supabase_client, db_get, db_set

# 1. Set global page configuration (mandatory call as the first Streamlit command)
st.set_page_config(page_title="House Chores System", page_icon="🏠", layout="wide")

BROTHERS_FILE = "brothers.txt"
CHORES_FILE = "chores.txt"
ROSTER_FILE = "roster.json"

# Parse shared roster query parameters
shared_roster_param = st.query_params.get("r", None)
shared_roster = None
shared_off_duty = None
shared_verse = None

if shared_roster_param:
    shared_roster, shared_off_duty, shared_verse = decode_roster(shared_roster_param)
    if shared_roster is not None:
        # Override the current session state or file
        st.session_state.roster = shared_roster
        st.session_state.off_duty = shared_off_duty if shared_off_duty is not None else []
        if shared_verse is not None:
            st.session_state.selected_verse = shared_verse
        
        # Save to roster.json and Supabase for persistence
        try:
            roster_data = {
                "roster": st.session_state.roster,
                "off_duty": st.session_state.off_duty
            }
            if get_supabase_client() is not None:
                db_set("roster", roster_data)
            with open(ROSTER_FILE, "w", encoding="utf-8") as f:
                json.dump(roster_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
            
        # Set a flag to trigger a success toast message in views/roster_generator.py
        st.session_state.show_shared_roster_toast = True
        
        # Clean up the URL query parameter so it doesn't stay in the browser
        if "r" in st.query_params:
            del st.query_params["r"]

DEFAULT_BROTHERS = [
    "John", "David", "Michael", "James", 
    "Andrew", "Robert", "William", "Joseph", "Daniel"
]

DEFAULT_CHORES = [
    "Staircase (Sweep Second & Third Floor)", "Back Yard", "Front Yard",
    "Dining Table + (Mop Second & Third Floor)", "Mop Floor", "Toilet",
    "Inside Kitchen", "Sweep Floor", "Outside Kitchen"
]

# Default Chore Content Definitions (used as fallbacks to initialize instructions.json)
DEFAULT_INSTRUCTIONS = {
    "Staircase (Sweep Second & Third Floor)": {
        "tools": [
            "(Inside Kitchen) Broom and Dustpan"
        ],
        "steps": [
            "Find the Broom and Dustpan in the inside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQChwfeDL6W-QINAS8jGBevgAao0F8_1MwSk1ZoQTK4768I?e=5ULqD1))",
            "Sweep through the dust on the wooden staircase, second, and third floor (cleaning all dust from the side areas). ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAVevAreS1hR5rjMhTM7uW_Ael_2PGkKy4uY9hoMwfcfgU?e=G0FEpM))",
            "Return the broom and dustpan to the original place."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBeb6EbGKbWRbZamY-Fkv-6AeLNs0PmXjMQp3szlSo7uN4?e=B8SB6Q"
    },
    "Back Yard": {
        "tools": [
            "(Back Yard) Broom and Dustpan"
        ],
        "steps": [
            "Find the Broom and Dustpan in the Back Yard. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAhpCgToY7UR4iY_kM5tEBTAa-VZ97BMAZq-Zviyz5HsA0?e=tza5Uq))",
            "Sweep away all loose leaves, dirt, and debris from the floor area. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCP8VIJl2_XSbQMMy_-S2I2AUHBRZa8DvdtBZiBIiJaTTU?e=Qr72Gg))",
            "Organize all shoes and shoe racks."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCP8VIJl2_XSbQMMy_-S2I2AUHBRZa8DvdtBZiBIiJaTTU?e=Qr72Gg"
    },
    "Front Yard": {
        "tools": [
            "(Front Yard) Broom and Dustpan"
        ],
        "steps": [
            "Find the Broom and Dustpan in the Back Yard. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDFHIqgph7ZTIHMBtaCMufCAZaQDOZ8DpnRFfeaBx6w4HA?e=cmx4xA))",
            "Sweep away all loose leaves, dirt, and debris from the floor area. ([📷 Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCzKjccDTgNTpt9hVQGSM4kAYwZFCrjJWtyk7c7uD6Yr-k?e=SAPOHl))",
            "Organize all shoes and shoe racks. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQB3RR26KfwlT55yxCG3zTBiAdeVzo0kwyhtdY4T4c_Yq18?e=IAGron))"
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQB3RR26KfwlT55yxCG3zTBiAdeVzo0kwyhtdY4T4c_Yq18?e=IAGron"
    },
    "Dining Table + (Mop Second & Third Floor)": {
        "tools": [
            "(Kitchen) Table Cloth",
            "(Store room) Roll tissue",
            "(Backyard) Mop and Bucket",
            "(Outside Kitchen) Floor cleaner"
        ],
        "steps": [
            "Find the table towel beside the sink in either the inside or outside kitchen. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBem4NV_fdqQrrgvQYM5DR-AXyo_j3J7muzYrYWj8Q9qDA?e=AiefzN))",
            "Wipe the glass ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDhwPOPAClEQrtDEI08xHjVAT1yU7SDxUWefgNhjbAfHxM?e=EoFsxe)), wooden ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAMzyWH_tZxTZkphbylx7BOAW98KC3f4OHx7kbTVv2joDM?e=CZNMhX)), and round ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCYoEHYa0KVQIW2ATx6M6MgARsFYqziZCvUQPQ4EfUV7DA?e=9wwOjF)) dining tables.",
            "Remove trash or used tissues from the tables and refill the tissue.",
            "Find the Mop and Bucket in the Backyard ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAKKKyjdcZfQZRMFrM9NMOQATZofBJXZULc2EblPiWNsb8?e=1s4hm3)), find the floor cleaner in the outside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBTO0uNpw3TQpGaCNAmPR8RAcOULDU15314DBrbtaS_du8?e=EYUgIs)).",
            "Mop the staircase, second floor ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAbEtWRDM53Tp9MQ3PHURjXAQuHHKhimd5f6ZhikbK8fk0?e=BdWTbA)), and third floor ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCtgC5ftj4vQqAd3g-tl7otAdt2f2F3NKuRqqjLU6ZZjls?e=52ptNw)).",
            "Wash the mop head thoroughly after completing the floor routine.",
            "Return the mop and bucket to the original place."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBem4NV_fdqQrrgvQYM5DR-AXyo_j3J7muzYrYWj8Q9qDA?e=AiefzN"
    },
    "Mop Floor": {
        "tools": [
            "(Backyard) Mop and Bucket",
            "(Outside Kitchen) Floor cleaner"
        ],
        "steps": [
            "Find the Mop and Bucket in the Backyard ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAKKKyjdcZfQZRMFrM9NMOQATZofBJXZULc2EblPiWNsb8?e=1s4hm3)), find the floor cleaner in the outside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBTO0uNpw3TQpGaCNAmPR8RAcOULDU15314DBrbtaS_du8?e=EYUgIs)).",
            "Mop through the ground floor (includes the children's room, inside and outside kitchen).",
            "Wash the mop head thoroughly after completing the floor routine.",
            "Return the mop and bucket to the original place."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAKKKyjdcZfQZRMFrM9NMOQATZofBJXZULc2EblPiWNsb8?e=1s4hm3"
    },
    "Toilet": {
        "tools": [
            "(Outside Kitchen) Toilet Cleaner",
            "(Store room) Roll tissue"
        ],
        "steps": [
            "Clean the white hand wash basin and mirror surface. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDtLDHZ7swJRKT85lTf8nqtAV4JkRSrBXK4sLFCuboYDeE?e=pQJDyz))",
            "Clean both sides of the seat, the outer lid, and the flush handle with a toilet brush and cleaner. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBAoceL6SQmTrRz4I79nb_VAQtg2fLipnPM-u9QQyauMHA?e=BY9naT))",
            "Clean the floor and the remaining hair on the floor drain cover.",
            "Refill the empty toilet tissue."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDtLDHZ7swJRKT85lTf8nqtAV4JkRSrBXK4sLFCuboYDeE?e=pQJDyz"
    },
    "Inside Kitchen": {
        "tools": [
            "Kitchen Cloth"
        ],
        "steps": [
            "Find the designated cloth beside the sink for cleaning the kitchen table. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBBFyCtK81hQaQmXzeE8tgxAZQMnVvpk2815Yv0uMn0jlo?e=uh9S7O))",
            "Tidy up the utilities on the table.",
            "Clear food waste from the sink and wash the basin with dishwashing liquid and a non-scratch pad. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDljE4kVyHASrmHtwyqQk6vAbDhp9inj-HU7o2aC0Korcs?e=x7ciph))",
            "Wipe the water machine ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDEH6KTxtP0QJekE4-IbhzHAWc2uergwFOmyFABBZnG35c?e=fyv62G)) and dry the remaining water in the sink ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDMvmt-wFGbQ6ASztpwxAhaAc3RxhK-wxqL1PEVjgPD99U?e=x4d27E)).",
            "Clean the microwave oven (surface and interior). ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCUAk_RdcgtTboAL0JsRayIAS93xZAd5n3CmC7b86HYtY0?e=wRqpn6))",
            "Clean the fridge (surface and interior), and clean up any spoiled or expired foods."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBBFyCtK81hQaQmXzeE8tgxAZQMnVvpk2815Yv0uMn0jlo?e=uh9S7O"
    },
    "Sweep Floor": {
        "tools": [
            "(Inside Kitchen) Broom and Dustpan"
        ],
        "steps": [
            "Find the Broom and Dustpan in the inside kitchen. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQChwfeDL6W-QINAS8jGBevgAao0F8_1MwSk1ZoQTK4768I?e=5ULqD1))",
            "Sweep through the dust on the ground floor (includes the children's room, inside and outside kitchen).",
            "Return the broom and dustpan to the original place."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAKKKyjdcZfQZRMFrM9NMOQATZofBJXZULc2EblPiWNsb8?e=1s4hm3"
    },
    "Outside Kitchen": {
        "tools": [
            "Kitchen Cloth"
        ],
        "steps": [
            "Find the designated cloth beside the sink for cleaning the kitchen table. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAaIYwqEMztSYWg5w66MFZPAaksFQB4vYJuo0Yc55J823I?e=ap23ke))",
            "Tidy up the utilities on the table.",
            "Clear food waste from the sink and wash the basin with dishwashing liquid and a non-scratch pad.",
            "Use dishwashing liquid to clean the cooking area and the wall.",
            "Clean the public fridge (surface and interior), and clean up any spoiled, expired foods, or leftovers."
        ],
        "onedrive_url": "https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAaIYwqEMztSYWg5w66MFZPAaksFQB4vYJuo0Yc55J823I?e=ap23ke"
    }
}

INSTRUCTIONS_FILE = "instructions.json"

# Check if Supabase is connected
supabase_active = get_supabase_client() is not None

if 'brothers_list' not in st.session_state:
    db_brothers = db_get("brothers_list") if supabase_active else None
    if db_brothers is not None:
        st.session_state.brothers_list = db_brothers
    elif os.path.exists(BROTHERS_FILE):
        with open(BROTHERS_FILE, "r", encoding="utf-8") as f:
            st.session_state.brothers_list = [line.strip() for line in f if line.strip()]
    else:
        st.session_state.brothers_list = DEFAULT_BROTHERS
        with open(BROTHERS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_BROTHERS))

if 'chores_list' not in st.session_state:
    db_chores = db_get("chores_list") if supabase_active else None
    if db_chores is not None:
        st.session_state.chores_list = db_chores
    elif os.path.exists(CHORES_FILE):
        with open(CHORES_FILE, "r", encoding="utf-8") as f:
            st.session_state.chores_list = [line.strip() for line in f if line.strip()]
    else:
        st.session_state.chores_list = DEFAULT_CHORES
        with open(CHORES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_CHORES))

if 'roster' not in st.session_state:
    db_roster = db_get("roster") if supabase_active else None
    if db_roster is not None:
        st.session_state.roster = db_roster.get("roster", {})
        st.session_state.off_duty = db_roster.get("off_duty", [])
    elif os.path.exists(ROSTER_FILE):
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
    db_details = db_get("chore_details") if supabase_active else None
    if db_details is not None:
        st.session_state.chore_details = db_details
    elif os.path.exists(INSTRUCTIONS_FILE) and os.path.getsize(INSTRUCTIONS_FILE) > 0:
        try:
            with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
                st.session_state.chore_details = json.load(f)
        except:
            st.session_state.chore_details = DEFAULT_INSTRUCTIONS.copy()
    else:
        st.session_state.chore_details = DEFAULT_INSTRUCTIONS.copy()
        with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_INSTRUCTIONS, f, ensure_ascii=False, indent=2)

# Ensure instructions_default.json exists
INSTRUCTIONS_DEFAULT_FILE = "instructions_default.json"
if not os.path.exists(INSTRUCTIONS_DEFAULT_FILE) or os.path.getsize(INSTRUCTIONS_DEFAULT_FILE) == 0:
    try:
        with open(INSTRUCTIONS_DEFAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_INSTRUCTIONS, f, ensure_ascii=False, indent=2)
    except:
        pass

# Load app_url configuration
CONFIG_FILE = "config.json"
if 'app_url' not in st.session_state:
    db_config = db_get("config") if supabase_active else None
    if db_config is not None:
        st.session_state.app_url = db_config.get("app_url", "")
    elif os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                st.session_state.app_url = config.get("app_url", "")
        except:
            st.session_state.app_url = ""
    else:
        st.session_state.app_url = ""

# Cookie Management for Device Persistence
import extra_streamlit_components as stx

@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Read cookie on startup to auto-login
if not st.session_state.admin_authenticated:
    try:
        cookie_val = cookie_manager.get('admin_authenticated')
        if cookie_val == 'true':
            st.session_state.admin_authenticated = True
            st.rerun()
    except:
        pass

# 2. Page Navigation definitions using modern st.Page syntax
roster_page = st.Page("views/roster_generator.py", title="Roster Generator", icon="📋", default=True)
guide_page = st.Page("views/chore_guide.py", title="Chore Guide", icon="📖", url_path="chore_guide")

pg = st.navigation([roster_page, guide_page])

# 3. Set global page configuration (done at startup)

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
    
    /* Responsive title and heading system */
    .main-header {
        text-align: center;
        margin-bottom: 15px;
    }
    .main-title {
        color: #2e5a44;
        margin-bottom: 0px;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.25;
        text-align: center;
    }
    .main-subtitle {
        color: #e76f51;
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: 1px;
        margin-top: 5px;
        margin-bottom: 15px;
        text-align: center;
    }
    .guide-subtitle {
        color: #555;
        font-size: 1.1rem;
        margin-top: 5px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* Bible Verse Card class */
    .bible-verse-card {
        background-color: #fdfaf2;
        border: 1px solid #e6dfd3;
        padding: 20px 25px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .bible-verse-text {
        font-size: 1.15rem;
        color: #5c5549;
        font-style: italic;
        margin-bottom: 8px;
        line-height: 1.5;
        font-weight: 500;
    }
    .bible-verse-ref {
        font-size: 0.95rem;
        color: #2e5a44;
        font-weight: 700;
        margin: 0;
    }
    
    /* Home Reminder Card class */
    .reminder-card {
        background-color: #f4f7f5;
        border-left: 5px solid #2e5a44;
        padding: 20px;
        border-radius: 8px;
        margin-top: 10px;
        box-shadow: 0 2px 6px rgba(46, 90, 68, 0.05);
    }
    .reminder-title {
        margin-top: 0;
        color: #2e5a44;
        font-weight: 600;
        font-size: 1.15rem;
    }
    .reminder-text {
        color: #444;
        margin-bottom: 15px;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .reminder-quote {
        font-style: italic;
        color: #2e5a44;
        font-weight: 600;
        margin: 0;
        font-size: 1rem;
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
    
    /* Compact Cards layout for responsive mobile-friendly grid */
    .compact-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 2px 8px rgba(46, 90, 68, 0.04);
        border: 1px solid #e8edea;
        border-left: 4px solid #2e5a44;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        position: relative;
        cursor: pointer;
    }
    .compact-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 90, 68, 0.08);
        border-color: #2e5a44;
    }
    .compact-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #2e5a44;
        margin-bottom: 2px;
    }
    .compact-card-subtitle {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #888;
        margin-bottom: 2px;
    }
    .compact-card-assignee {
        font-size: 1rem;
        font-weight: 600;
        color: #222222;
        margin-bottom: 6px;
    }
    .compact-card-link {
        font-size: 0.8rem;
        color: #2e5a44 !important;
        text-decoration: none;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 3px;
        position: relative;
        z-index: 2; /* keep clickability above overlay if text is targeted */
    }
    .compact-card-link:hover {
        color: #1d3b2c !important;
        text-decoration: underline;
    }
    .compact-card-overlay-link {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
        text-decoration: none;
        background-color: transparent;
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
    
    /* Image reference card hover animation (Visual Guide OneDrive cards) */
    a[href*="sharepoint.com"] > div {
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    a[href*="sharepoint.com"] > div:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46, 90, 68, 0.15) !important;
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

    /* =========================================================================
       Responsive Mobile Styles (max-width: 768px)
       ========================================================================= */
    @media (max-width: 768px) {
        /* Compress Streamlit's default page margins */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        
        /* Downscale header font sizes to prevent vertical overflow / multi-line wrap */
        .main-title {
            font-size: 1.45rem !important;
        }
        .main-subtitle {
            font-size: 0.9rem !important;
            margin-bottom: 10px !important;
        }
        .guide-subtitle {
            font-size: 0.9rem !important;
            margin-bottom: 10px !important;
        }
        
        /* Make tabs more touch-friendly on mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0 !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 12px 16px !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 12px !important;
        }
        
        /* Ensure checkboxes have good tap target size */
        .stCheckbox label {
            padding: 8px 0 !important;
            font-size: 0.95rem !important;
            line-height: 1.4 !important;
        }
        
        /* Compress custom card paddings for better layout fit */
        .bible-verse-card {
            padding: 15px 18px !important;
            margin-bottom: 12px !important;
        }
        .bible-verse-text {
            font-size: 1rem !important;
        }
        .bible-verse-ref {
            font-size: 0.85rem !important;
        }
        
        .reminder-card {
            padding: 15px !important;
        }
        .reminder-title {
            font-size: 1.05rem !important;
        }
        .reminder-text {
            font-size: 0.95rem !important;
            margin-bottom: 10px !important;
        }
        .reminder-quote {
            font-size: 0.9rem !important;
        }
        
        .compact-card {
            padding: 14px 16px !important;
            border-left-width: 5px !important;
        }
        .compact-card-title {
            font-size: 1rem !important;
        }
        .compact-card-assignee {
            font-size: 1.05rem !important;
        }
        
        /* Make expanders more touch-friendly */
        .streamlit-expanderHeader {
            font-size: 0.95rem !important;
            padding: 10px 12px !important;
        }
        
        /* Full-width columns on mobile for stacked layout */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
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

# Show database connection status
if supabase_active:
    st.sidebar.markdown(
        "<div style='font-size: 0.85rem; color: #1557b0; background-color: #e8f0fe; border: 1px solid #c2e7ff; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; text-align: center;'>"
        "🟢 Cloud Database Connected"
        "</div>", 
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        "<div style='font-size: 0.85rem; color: #b06000; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; text-align: center;'>"
        "🟡 Local Files Mode (Offline)"
        "</div>", 
        unsafe_allow_html=True
    )

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

# Administrator Authentication Panel
st.sidebar.markdown("<h4 style='color: #2e5a44; margin-bottom: 5px;'>🔑 Admin Control Panel</h4>", unsafe_allow_html=True)

if st.session_state.admin_authenticated:
    st.sidebar.success("🔓 Admin Mode Active")
    if st.sidebar.button("🔒 Log Out", use_container_width=True):
        st.session_state.admin_authenticated = False
        try:
            cookie_manager.delete('admin_authenticated', key='delete_auth_cookie_sidebar')
        except:
            pass
        st.rerun()
else:
    admin_passcode_input = st.sidebar.text_input(
        "Enter Admin Passcode:", 
        type="password",
        help="Enter passcode to unlock roster settings and instructions editing."
    )
    correct_passcode = st.secrets.get("ADMIN_PASSCODE", "164brothers")
    if admin_passcode_input == correct_passcode:
        st.session_state.admin_authenticated = True
        try:
            cookie_manager.set('admin_authenticated', 'true', key='set_auth_cookie_sidebar')
        except:
            pass
        st.sidebar.success("🔓 Access Granted!")
        st.rerun()
    elif admin_passcode_input:
        st.sidebar.error("❌ Incorrect Passcode")

st.sidebar.markdown("---")

# Show success toast if shared roster was loaded
if st.session_state.get("show_shared_roster_toast"):
    st.toast("📥 Loaded shared roster from link!", icon="✅")
    del st.session_state.show_shared_roster_toast

# 6. Run selected page routing
pg.run()
