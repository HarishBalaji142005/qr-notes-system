"""
QR-Based Digital Notes Sharing System
======================================
A Streamlit web app for teachers/students to upload and share notes via QR codes.
"""

import streamlit as st
import os
import json
import socket
from datetime import datetime
from utils import (
    save_uploaded_file,
    generate_qr_code,
    get_local_ip,
    load_notes_db,
    save_notes_db,
    delete_note,
    get_file_icon,
    format_file_size,
    UPLOADS_DIR,
    QR_DIR,
    DB_PATH
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="QR Notes Share",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# INJECT CSS
# ─────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR – NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">📚 QR Notes Share</div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Upload Notes", "📋 Notes Library", "ℹ️ How It Works"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(
        '<p class="sidebar-info">Share classroom notes instantly via QR codes.<br>'
        'No WhatsApp. No Bluetooth. Just scan & download.</p>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# PAGE: UPLOAD NOTES
# ─────────────────────────────────────────────
if page == "🏠 Upload Notes":

    st.markdown('<h1 class="page-title">📤 Upload & Share Notes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Upload your notes and get an instant QR code for sharing.</p>', unsafe_allow_html=True)

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Note Details")

        teacher_name = st.text_input("👤 Teacher / Uploader Name", placeholder="e.g. Dr. Ahmed Khan")
        subject_name = st.text_input("📖 Subject Name", placeholder="e.g. Data Structures")
        note_title   = st.text_input("🏷️ Note Title", placeholder="e.g. Chapter 3 - Linked Lists")

        uploaded_file = st.file_uploader(
            "📎 Upload File",
            type=["pdf", "ppt", "pptx", "docx", "doc", "txt", "png", "jpg", "jpeg"],
            help="Supported: PDF, PPT, DOCX, TXT, Images"
        )

        upload_btn = st.button("🚀 Upload & Generate QR", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        if upload_btn:
            # Validation
            if not teacher_name.strip():
                st.error("⚠️ Please enter the teacher/uploader name.")
            elif not subject_name.strip():
                st.error("⚠️ Please enter the subject name.")
            elif not note_title.strip():
                st.error("⚠️ Please enter the note title.")
            elif uploaded_file is None:
                st.error("⚠️ Please select a file to upload.")
            else:
                with st.spinner("Processing upload..."):
                    # Save file
                    saved_path, filename = save_uploaded_file(uploaded_file)

                    # Build download URL
                    local_ip = get_local_ip()
                    port = 8501
                    download_url = f"http://{local_ip}:{port}/?file={filename}"

                    # Generate QR code
                    qr_path = generate_qr_code(download_url, filename)

                    # Save metadata to DB
                    db = load_notes_db()
                    note_id = f"note_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                    note_entry = {
                        "id": note_id,
                        "title": note_title.strip(),
                        "subject": subject_name.strip(),
                        "teacher": teacher_name.strip(),
                        "filename": filename,
                        "file_path": saved_path,
                        "qr_path": qr_path,
                        "download_url": download_url,
                        "file_size": os.path.getsize(saved_path),
                        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    db.append(note_entry)
                    save_notes_db(db)

                # Success Card
                st.markdown('<div class="card success-card">', unsafe_allow_html=True)
                st.success("✅ Notes uploaded successfully!")
                st.markdown(f"**📁 File:** `{filename}`")
                st.markdown(f"**📖 Subject:** {subject_name.strip()}")
                st.markdown(f"**👤 Uploaded by:** {teacher_name.strip()}")
                st.markdown(f"**🕐 Time:** {note_entry['upload_time']}")
                st.markdown("---")
                st.markdown("#### 📲 QR Code for Students")
                st.image(qr_path, width=250, caption="Scan to download notes")

                # QR download button
                with open(qr_path, "rb") as qf:
                    st.download_button(
                        label="⬇️ Download QR Image",
                        data=qf.read(),
                        file_name=f"qr_{filename}.png",
                        mime="image/png",
                        use_container_width=True
                    )

                st.info(f"🔗 Share URL: `{download_url}`")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card placeholder-card">', unsafe_allow_html=True)
            st.markdown(
                """
                <div style='text-align:center; padding: 40px 20px;'>
                    <div style='font-size:80px;'>📲</div>
                    <h3 style='color:#64748b;'>Your QR code will appear here</h3>
                    <p style='color:#94a3b8;'>Fill in the form and click <b>Upload & Generate QR</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: NOTES LIBRARY
# ─────────────────────────────────────────────
elif page == "📋 Notes Library":

    st.markdown('<h1 class="page-title">📋 Notes Library</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Browse, search, and manage all uploaded notes.</p>', unsafe_allow_html=True)

    db = load_notes_db()

    if not db:
        st.markdown(
            '<div class="card" style="text-align:center;padding:60px;">'
            '<div style="font-size:70px;">📭</div>'
            '<h3 style="color:#64748b;">No notes uploaded yet</h3>'
            '<p style="color:#94a3b8;">Go to <b>Upload Notes</b> to get started.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        # Search bar
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search notes by title, subject, or teacher...", label_visibility="collapsed", placeholder="🔍 Search notes by title, subject, or teacher...")
        with col_s2:
            st.markdown(f"**{len(db)} note(s) uploaded**")

        # Filter
        filtered = [
            n for n in db
            if search_query.lower() in n["title"].lower()
            or search_query.lower() in n["subject"].lower()
            or search_query.lower() in n["teacher"].lower()
        ] if search_query else db

        if not filtered:
            st.warning("No notes match your search.")
        else:
            for note in reversed(filtered):  # newest first
                icon = get_file_icon(note["filename"])
                size_str = format_file_size(note["file_size"])

                with st.expander(f"{icon} {note['title']}  —  {note['subject']}  •  {note['teacher']}  •  {note['upload_time']}"):
                    col_info, col_qr, col_actions = st.columns([2, 1, 1])

                    with col_info:
                        st.markdown(f"**📁 File:** `{note['filename']}`")
                        st.markdown(f"**📦 Size:** {size_str}")
                        st.markdown(f"**🔗 URL:** `{note['download_url']}`")

                    with col_qr:
                        if os.path.exists(note["qr_path"]):
                            st.image(note["qr_path"], width=150, caption="Scan QR")

                    with col_actions:
                        # Download file
                        if os.path.exists(note["file_path"]):
                            with open(note["file_path"], "rb") as df:
                                st.download_button(
                                    "⬇️ Download File",
                                    data=df.read(),
                                    file_name=note["filename"],
                                    use_container_width=True,
                                    key=f"dl_{note['id']}"
                                )
                        # Download QR
                        if os.path.exists(note["qr_path"]):
                            with open(note["qr_path"], "rb") as qf:
                                st.download_button(
                                    "📲 Download QR",
                                    data=qf.read(),
                                    file_name=f"qr_{note['filename']}.png",
                                    mime="image/png",
                                    use_container_width=True,
                                    key=f"qrdl_{note['id']}"
                                )
                        # Delete
                        if st.button("🗑️ Delete", use_container_width=True, key=f"del_{note['id']}"):
                            delete_note(note["id"])
                            st.success("Note deleted.")
                            st.rerun()

# ─────────────────────────────────────────────
# PAGE: HOW IT WORKS
# ─────────────────────────────────────────────
elif page == "ℹ️ How It Works":

    st.markdown('<h1 class="page-title">ℹ️ How It Works</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Simple 6-step workflow to share notes instantly.</p>', unsafe_allow_html=True)

    steps = [
        ("1️⃣", "Teacher Uploads Notes", "Fill in the subject, name, and upload a file (PDF, DOCX, PPT, etc.)"),
        ("2️⃣", "System Stores File", "The file is securely saved to the local `uploads/` folder."),
        ("3️⃣", "Download Link Generated", "A unique download URL is created using your local network IP."),
        ("4️⃣", "QR Code Generated", "The URL is converted into a scannable QR code image."),
        ("5️⃣", "Students Scan QR", "Students scan the QR code using any mobile camera — no app required."),
        ("6️⃣", "Notes Open Instantly", "The file opens or downloads directly on the student's phone."),
    ]

    cols = st.columns(3)
    for i, (emoji, title, desc) in enumerate(steps):
        with cols[i % 3]:
            st.markdown(
                f'<div class="card step-card">'
                f'<div class="step-emoji">{emoji}</div>'
                f'<h4>{title}</h4>'
                f'<p>{desc}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### 📡 Network Setup Tip")
    st.info(
        "**For QR sharing to work on mobile phones:**\n\n"
        "1. Make sure your PC and students' phones are on the **same Wi-Fi network**.\n"
        "2. Run the app with: `streamlit run app.py --server.address 0.0.0.0`\n"
        "3. The QR code will contain your local IP address automatically.\n"
        "4. Students scan the QR with the default camera app — no extra app needed!"
    )

    st.markdown("### 🗂️ Supported File Types")
    cols2 = st.columns(5)
    types = [("📄", "PDF"), ("📊", "PPT / PPTX"), ("📝", "DOCX / DOC"), ("📃", "TXT"), ("🖼️", "PNG / JPG")]
    for i, (ic, ft) in enumerate(types):
        with cols2[i]:
            st.markdown(
                f'<div class="card" style="text-align:center;padding:20px;">'
                f'<div style="font-size:36px;">{ic}</div>'
                f'<b>{ft}</b></div>',
                unsafe_allow_html=True
            )
