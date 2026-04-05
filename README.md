# ⚖️ Federal Court Case Explorer

An interactive dashboard that pulls **real federal court opinions** from the
[CourtListener API](https://www.courtlistener.com/) and visualizes them by
charge/topic type, court, and year. Deployed on https://court-data.streamlit.app/.

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

## Sources

All data comes from [CourtListener](https://www.courtlistener.com/), a free
legal research tool maintained by the [Free Law Project](https://free.law/),
a 501(c)(3) nonprofit. The API is free for non-commercial research use.
