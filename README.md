# ⚖️ Federal Court Case Explorer

An interactive dashboard that pulls **real federal court opinions** from the
[CourtListener API](https://www.courtlistener.com/) and visualizes them by
charge/topic type, court, and year.

Built with Python · Streamlit · Plotly · CourtListener (Free Law Project)

---

## What it does

- Filter cases by **charge type**: Drug Offenses, Immigration, Civil Rights, White Collar Fraud, Firearms, Sentencing
- Filter by **federal circuit court** or view all circuits at once
- Filter by **year range** (2000–present)
- Charts:
  - Cases by court (bar)
  - Filing trend over time (line)
  - Court activity heatmap (when viewing all circuits)
- Browseable case table with direct links to full opinions
- CSV export

---

## Setup (5 minutes)

### 1. Make sure Python is installed
```bash
python --version   # should be 3.10 or higher
```

### 2. Create a virtual environment (keeps your packages tidy)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## Sources

All data comes from [CourtListener](https://www.courtlistener.com/), a free
legal research tool maintained by the [Free Law Project](https://free.law/),
a 501(c)(3) nonprofit. The API is free for non-commercial research use.
