📚 QR Notes Share

A Streamlit web app that lets teachers upload classroom notes (PDFs, PPTs, DOCX, images, etc.) and instantly generate a QR code for students to scan and download — no WhatsApp, no Bluetooth, no USB drives needed.

✨ Features


📤 Upload notes with teacher name, subject, and title metadata
🔗 Instant QR code generation for each uploaded file
📋 Notes Library to browse, search, and manage previously shared notes
📱 Students scan the QR code with their phone camera to download the file directly
🗂️ Supports PDF, PPT, PPTX, DOCX, DOC, TXT, PNG, JPG, and JPEG files


🛠️ Tech Stack


Streamlit — web app framework
qrcode — QR code generation
Pillow — image processing


🚀 Getting Started

Prerequisites


Python 3.10+


Installation


Install dependencies


bash   pip install -r requirements.txt


Run the app


bash   streamlit run app.py


Open your browser at http://localhost:8501


Usage


Go to 🏠 Upload Notes in the sidebar
Fill in your name, subject, and note title
Upload your file and click Upload & Generate QR
Share the generated QR code with students — they scan it to download the file instantly
View or manage all shared notes under 📋 Notes Library


📁 Project Structure

qr_notes_system/
├── app.py              # Main Streamlit application
├── utils.py            # Helper functions (file handling, QR generation, DB operations)
├── requirements.txt    # Python dependencies
└── assets/
    └── style.css        # Custom UI styling


Note: The uploads/, qr_codes/, and notes_db.json folders/files are generated at runtime and are excluded from version control via .gitignore. They'll be created automatically the first time you run the app.



📄 License

This project is open source. Feel free to use and modify it for your own classroom or organization.

🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.
