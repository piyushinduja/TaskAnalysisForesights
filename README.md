# 📊 Task Analysis and Foresights

This project analyzes project schedule data using **Python (Streamlit)** and **Power BI** to generate actionable insights that help in improving task prioritization, estimating delays, and optimizing overall project timelines.

---

## 📁 Data

The dataset represents a project schedule with details such as task status, planned and actual durations, float times, predecessors/successors, and more.

### 🔧 Data Preprocessing
- Dropped irrelevant columns for simplicity.
- Renamed columns to shorter, more readable names.
- Simplified `Activity ID`s by converting them into integers from 1 to 1350 for easier visualization.

---

## ⚙️ Tech Stack

### 🐍 Python App:
- `pandas` – for data manipulation
- `matplotlib` – for custom charts
- `streamlit` – for building an interactive dashboard

### 📊 Power BI:
- Used to cross-validate and visualize certain metrics more interactively.

---

## 🔍 Analysis Performed

### 1. **Dependency on In-Progress Tasks**
- Identifies how many **"Not Started"** tasks are dependent on **"In Progress"** tasks.
- Helps prioritize high-impact in-progress tasks.
- **Example**: Task `1328` has **4** not started tasks dependent on it — making it a priority to avoid cascading delays.

---

### 2. **In-Progress Tasks' Risk Assessment**
- Estimates which in-progress tasks can be completed:
  - **On time**
  - **Using float**
  - **Will be delayed**
- Based on `% completion`, actual and original duration, and available float time.

---

### 3. **Cascading Dependencies Analysis**
- Finds tasks (in-progress or not started) that have the most downstream dependencies.
- Useful for prioritizing root tasks with large dependency chains.
- **Example**: Task `1328` affects **118** other tasks either directly or indirectly.

---

### 4. **Key Performance Metrics**
- 📈 **Estimated on-time completion (in-progress tasks):** `35%`
- 🕒 **Started on or before planned date (completed + in-progress tasks):** `~98%`

These KPIs provide a snapshot of the schedule's health and adherence.

---

## 🚀 Live App

👉 [Click here to explore the interactive Streamlit dashboard](https://4mhewnqcodg3ddjpd6q4rs.streamlit.app/)

---

## 📌 Conclusion

This analysis enables project managers to:
- Identify high-risk tasks early
- Optimize task sequencing
- Track performance through key metrics
- Make data-driven scheduling decisions

