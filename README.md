# 💼 SAP Order-to-Cash (O2C) Process Simulator

**Capstone Project | SAP Track — KIIT**

An interactive web-based simulation of the complete **SAP Order-to-Cash (O2C) cycle**, built with Python and Streamlit. It replicates the real SAP SD/FI module workflow — from Sales Order creation to Accounts Receivable clearance.

🔗 **Live Demo:** [Click to Open App](https://your-app-link.streamlit.app)

---

## 📌 Problem Statement

Understanding the SAP O2C process is critical for SD/FI consultants, but real SAP systems are expensive and complex to access for learning purposes. There is a need for an affordable, hands-on simulation tool that mirrors the actual SAP workflow — step by step — with proper T-codes, document flow, and business logic.

## ✅ Features / O2C Steps Simulated

| Step | SAP T-Code | Description |
|------|-----------|-------------|
| 1️⃣ Sales Order | VA01 | Create customer sales order with pricing & GST |
| 2️⃣ Credit Check | FD32 / VKM3 | Automatic credit limit verification & block release |
| 3️⃣ Delivery | VL01N | Create outbound delivery with shipping details |
| 4️⃣ Goods Issue | VL02N | Post Goods Issue — stock transfer to customer |
| 5️⃣ Invoice | VF01 | Create billing document with accounting entry |
| 6️⃣ Payment | F-28 | Post incoming payment & clear AR |
| 7️⃣ Reports | VA05/VF05/FBL5N | AR Ledger, order list, analytics & CSV export |

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **UI Framework**: Streamlit
- **Data Processing**: Pandas
- **Deployment**: Streamlit Community Cloud (free)

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sap-o2c-simulator.git
cd sap-o2c-simulator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## ☁️ How to Deploy on Streamlit Cloud (Free — Get a Live Link!)

1. Push your code to GitHub (see GITHUB_UPLOAD_GUIDE.txt)
2. Go to: https://share.streamlit.io
3. Sign in with your GitHub account
4. Click **"New app"**
5. Select your repository → Branch: `main` → Main file: `app.py`
6. Click **"Deploy"** — you get a public link in ~2 minutes! 🎉

---

## 📁 Project Structure

```
sap-o2c-simulator/
│
├── app.py              # Main Streamlit application (all 7 O2C steps)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🔮 Future Improvements

- Add SAP ABAP-style ALV grid reports with filters
- Integrate with a database (SQLite) for persistent multi-session data
- Add email notification simulation for invoice dispatch
- Include returns & credit memo process (RE document)
- Add multi-user support for team-based training scenarios

---

## 👤 Author

- **Name**: [Your Full Name]
- **Roll Number**: [Your Roll Number]
- **Batch / Program**: SAP Track | KIIT

---

## 📄 License

Submitted as Capstone Project — SAP Track, KIIT. April 2026.
