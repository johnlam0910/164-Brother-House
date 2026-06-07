# 🏠 164 Brothers House - Chore Roster & Guide System

Welcome to the **164 Brothers House Chore Roster & Guide System**! This is a clean, modern, and warm multi-page web application built with Python and Streamlit. 

It is designed for the community brothers living at the 164 House to coordinate weekly duties, encourage one another through scripture, and maintain a high standard of cleanliness and hospitality for visiting saints and gospel friends.

---

## ✨ Key Features

*   **📋 Brother House Roster Guide**:
    *   **Edit Names & Tasks**: Easily modify the list of brothers and chores directly on the webpage interface.
    *   **Smart Randomizer**: Automatically pairs brothers to the 9 house chores with 1-to-1 matching.
    *   **Mismatch Support**:
        *   If there are *fewer* brothers than chores, it recycles names so all chores get done.
        *   If there are *more* brothers than chores, it lists the remaining members as **Off-Duty/Resting**.
    *   **Roster Validation**: Live sidebar warning notice that checks if the counts match.
*   **📱 WhatsApp Exporter**:
    *   Generates a beautifully formatted, copyable text block with bold elements (`*Chore*: Brother`) and lists.
    *   Automatically prepends the active Bible verse and appends a chore completion tick reminder (`✅`) for easy group chat sharing.
*   **📖 Interactive Chore Guide**:
    *   Displays clean, structured cleaning instruction checklists for all chores.
    *   Lists required **Tools & Supplies** for each duty.
    *   **Visual Guides**: Dynamically loads illustration photos from the `assets/` directory. Supports multiple photo tabs if more than one guide image exists.
*   **✝️ Bible Verse Encounters**:
    *   Shows a random verse on top of the Roster page to encourage loving service and hospitality.
    *   Features a `🔄 Next Bible Verse` button to cycle verses manually.
*   **💾 Local Disk Persistence**:
    *   All edits (brothers list, chores list) and generated rosters are saved to disk (`brothers.txt`, `chores.txt`, `roster.json`, `instructions.json`). 
    *   The website automatically restores the saved roster and setup even if the web server restarts or your browser tab is closed!

---

## 🛠️ How to Edit & Customize Later

Because the system uses local file storage, you can easily customize the app by editing these files in a simple text editor (like Notepad or VS Code) and pushing them to GitHub:

1.  **Add/Remove Brothers permanently**: Open and edit `brothers.txt` (one name per line).
2.  **Add/Modify Chores permanently**: Open and edit `chores.txt` (one chore per line).
3.  **Edit Cleaning Instructions**: Open and edit `instructions.json` to customize the supplies and steps for any chore.
4.  **Add Visual Guide Photos**: Place images in the `assets/` folder and name them starting with the chore name (e.g. `staircase.jpg`, `outside_kitchen.png`). For multiple photos, name them sequentially (e.g., `staircase_1.jpg`, `staircase_2.jpg`).

---

## 🚀 How to Run Locally

If you want to run the project on your local machine:

1.  **Clone or download** the repository folder.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Launch the Streamlit app**:
    ```bash
    streamlit run streamlit_app.py
    ```
4.  Open `http://localhost:8501` in your browser.
