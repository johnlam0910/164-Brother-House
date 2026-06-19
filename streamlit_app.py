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
        "tools": [
            "Broom / Hand vacuum",
            "Microfiber cloth",
            "All-purpose spray"
        ],
        "steps": [
            "Main Wooden Staircase and floor cleanning for second and third floor ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBeb6EbGKbWRbZamY-Fkv-6AeLNs0PmXjMQp3szISo7uN4?e=B8SB6Q))",
            "Sweep and Wipe through the stair, ensure to clean the dust on the side area. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAVevAreS1hR5rjMhTM7uW_Ael_2PGkKy4uY9hoMwfcfgU?e=G0FEpM))",
            "Sweep and mop the second floor ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAbEtWRDM53Tp9MQ3PHURjXAQuHHKhimd5f6ZhikbK8fk0?e=BdWTbA))",
            "Sweep and mop the third floor ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCtgC5ftj4vQqAd3g-tl7otAdt2f2F3NKuRqqjLU6ZZjls?e=52ptNw))"
        ]
    },
    "Back Yard": {
        "tools": [
            "Outdoor push broom",
            "Trash bags",
            "Garden hose"
        ],
        "steps": [
            "Sweep loose leaves, dirt, and debris. Clean the tiled floor area and ensure shoes, racks, and detergent bottles are placed systematically. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCP8VIJl2_XSbQMMy_-S2I2AUHBRZa8DvdtBZiBIiJaTTU?e=Qr72Gg))",
            "Find the dustpan and broom outside the backyard ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAhpCgToY7UR4iY_kM5tEBTAa-VZ97BMAZq-Zviyz5HsA0?e=tza5Uq))"
        ]
    },
    "Front Yard": {
        "tools": [
            "Outdoor broom",
            "Weeding tool",
            "Watering can / Hose",
            "Gardening gloves"
        ],
        "steps": [
            "Sweep loose leaves, dirt, and debris. Clean the tiled floor area and ensure shoes, racks are placed systematically. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQB3RR26KfwlT55yxCG3zTBiAdeVzo0kwyhtdY4T4c_Yq18?e=IAGron))",
            "Sweep loose leaves, dirt, and debris ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCzKjccDTgNTpt9hVQGSM4kAYwZFCrjJWtyk7c7uD6Yr-k?e=SAPOHl))",
            "Find the dustpan and broom outside the front yard ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDFHIqgph7ZTIHMBtaCMufCAZaQDOZ8DpnRFfeaBx6w4HA?e=cmx4xA))"
        ]
    },
    "Dining Table": {
        "tools": [
            "Sponges",
            "Dish soap / Surface spray",
            "Dry dishcloth"
        ],
        "steps": [
            "Use the cloth beside the sink to clean the dining table and edible things. Separate and use another cloth if you use chemincal liquid, avoid to mix together and posioning. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBem4NV_fdqQrrgvQYM5DR-AXyo_j3J7muzYrYWj8Q9qDA?e=AiefzN))",
            "Wipe Glass Dining Table ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDhwPOPAClEQrtDEI08xHjVAT1yU7SDxUWefgNhjbAfHxM?e=EoFsxe))",
            "Wipe Wodden Table ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAMzyWH_tZxTZkphbylx7BOAW98KC3f4OHx7kbTVv2joDM?e=CZNMhX))",
            "Wipe Round Table. Restock tissue boxes, remove trash or used tissue. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCYoEHYa0KVQIW2ATx6M6MgARsFYqziZCvUQPQ4EfUV7DA?e=9wwOjF))"
        ]
    },
    "Mop Floor": {
        "tools": [
            "Mop",
            "Bucket",
            "Floor cleaner solution",
            "Warm water"
        ],
        "steps": [
            "Find the mop handle and bucket outside backyard. Wash the mop head after every interior floor routine. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAKKKyjdcZfQZRMFrM9NMOQATZofBJXZULc2EblPiWNsb8?e=1s4hm3))",
            "Indoor Broom & Dustpan Inventory: Store in the inside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQChwfeDL6W-QINAS8jGBevgAao0F8_1MwSk1ZoQTK4768I?e=5ULqD1))",
            "You can find all the Chemical and floor cleaners for mopping and cleanning toilet can be found in the floor outside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBTO0uNpw3TQpGaCNAmPR8RAcOULDU15314DBrbtaS_du8?e=EYUgIs))"
        ]
    },
    "Toilet": {
        "tools": [
            "Toilet brush",
            "Disinfectant spray",
            "Glass cleaner",
            "Paper towels / Cleaning cloths"
        ],
        "steps": [
            "Clean the white ceramic basin surface. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDtLDHZ7swJRKT85lTf8nqtAV4JkRSrBXK4sLFCuboYDeE?e=pQJDyz))",
            "Toilet Bowl Thorough Disinfection: Apply specialized toilet bowl cleaner inside the rim, scrub with a brush, and flush. Sanitize both sides of the seat, the outer lid, and the flush tank handle using disinfectant. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBAoceL6SQmTrRz4I79nb_VAQtg2fLipnPM-u9QQyauMHA?e=BY9naT))",
            "You can find all the Chemical and floor cleaners for mopping and cleanning toilet can be found in the floor outside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBTO0uNpw3TQpGaCNAmPR8RAcOULDU15314DBrbtaS_du8?e=EYUgIs))"
        ]
    },
    "Inside Kitchen": {
        "tools": [
            "Dish sponge",
            "Degreaser spray",
            "Stainless steel cleaner",
            "Scouring pad"
        ],
        "steps": [
            "Clean the table surface and tidy up ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBBFyCtK81hQaQmXzeE8tgxAZQMnVvpk2815Yv0uMn0jlo?e=uh9S7O))",
            "Remove all the food wastes on the sink. Use dishwashing liquid and a non-scratch scrub pad to clean the interior basin. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDljE4kVyHASrmHtwyqQk6vAbDhp9inj-HU7o2aC0Korcs?e=x7ciph))",
            "Water Purifier Exterior Care: Use a cloth to wipe the touch screen panel and exterior body of the PuriCare machine. Do not use wet cloths directly on electronic displays or underlying electrical cords. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDEH6KTxtP0QJekE4-IbhzHAWc2uergwFOmyFABBZnG35c?e=fyv62G))",
            "Clean the sink, remove the food waste ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDZ8iulfJCmQpdNM7LVVu0nATShkNxBPLsXn1UspjpkGos?e=ILTrG5))",
            "Use a dry, clean cloth to dry the water stored in the sink. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQDMvmt-wFGbQ6ASztpwxAhaAc3RxhK-wxqL1PEVjgPD99U?e=x4d27E))",
            "Microwave Cleaning: Remove the glass turntable plate and wash it separately. Clean the interior ceilings and walls. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQCUAk_RdcgtTboAL0JsRayIAS93xZAd5n3CmC7b86HYtY0?e=wRqpn6))",
            "Use the cloth beside the sink to clean the dining table and edible things. Separate and use another cloth if you use chemincal liquid, avoid to mix together and posioning. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQBem4NV_fdqQrrgvQYM5DR-AXyo_j3J7muzYrYWj8Q9qDA?e=AiefzN))"
        ]
    },
    "Sweep Floor": {
        "tools": [
            "Broom",
            "Dustpan",
            "Hand brush"
        ],
        "steps": [
            "Find the mop handle and bucket outside backyard. Wash the mop head after every interior floor routine. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAKKKyjdcZfQZRMFrM9NMOQATZofBJXZULc2EblPiWNsb8?e=1s4hm3))",
            "Indoor Broom & Dustpan Inventory: Store in the inside kitchen ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQChwfeDL6W-QINAS8jGBevgAao0F8_1MwSk1ZoQTK4768I?e=5ULqD1))"
        ]
    },
    "Outside Kitchen": {
        "tools": [
            "Wire grill brush",
            "Warm soapy water",
            "Heavy-duty sponge",
            "Outdoor broom"
        ],
        "steps": [
            "Wipe the surface and ensure the kitchen utlities are tidy. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQAaIYwqEMztSYWg5w66MFZPAaksFQB4vYJuo0Yc55J823I?e=ap23ke))",
            "These haning towel for drying up the utilities. Do not use them for cleaning purpose, ensure they are clean. Put them to the washing machine and dry out and hang to the original position in every cleanning rountine. ([📷 Image Guide](https://entuedu-my.sharepoint.com/:i:/g/personal/chunwai001_e_ntu_edu_sg/IQD7fQfgo2igTpS67CoBv9_-AadLqzFhZbCNcZJcLKqTsU0?e=FzOF4T))"
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
guide_page = st.Page("views/chore_guide.py", title="Chore Guide", icon="📖", url_path="chore_guide")

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
    
    /* Compact Cards layout for responsive mobile-friendly grid */
    .compact-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 2px 8px rgba(46, 90, 68, 0.04);
        border: 1px solid #e8edea;
        border-left: 4px solid #2e5a44;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
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
    }
    .compact-card-link:hover {
        color: #1d3b2c !important;
        text-decoration: underline;
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
