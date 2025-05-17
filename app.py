import pandas as pd
import matplotlib.pyplot as plt
import ast
from collections import defaultdict
import streamlit as st


# Can also use the Budget values againt the WBS categories...

# Load Excel file
# df = pd.read_excel("Modified_Tasks_Data.xlsx")
df = pd.read_excel("MDC1_BL_1.xlsx")
df = df.rename(columns={'(*)Activity Type': 'Activity Type', '(*)Planned Start': 'Planned Start', '(*)Planned Finish': 'Planned Finish', '(*)Actual Duration(d)': 'Actual Duration', 'Remaining Duration(d)': 'Remaining Duration', '(*)Total Float(d)': 'Total Float', '(*)Remaining Float(d)': 'Remaining Float', 'Original Duration(d)': 'Original Duration'})

st.title("Project Schedule Insights")

# Graph 1
in_progress_ids = df[df['Activity Status'] == 'In Progress']['Activity ID'].tolist()
not_started_df = df[df['Activity Status'] == 'Not Started'].copy()
not_started_df['Parsed Predecessors'] = not_started_df['Predecessor Details'].apply(ast.literal_eval)
# st.dataframe(not_started_df)

dependency_count = defaultdict(int)
for _, row in not_started_df.iterrows():
    # st.header(row)
    preds = [int(p.split(':')[0]) for p in row['Parsed Predecessors']]
    for pid in preds:
        if pid in in_progress_ids:
            dependency_count[pid] += 1

dependency_df = pd.DataFrame(dependency_count.items(), columns=['In Progress Task ID', '# Not Started Dependents'])
dependency_df = dependency_df.sort_values(by='# Not Started Dependents', ascending=False)

st.header("1. Dependency on In Progress Tasks")
st.dataframe(dependency_df)
st.bar_chart(dependency_df.set_index('In Progress Task ID'))

# Graph 2

in_progress_df = df[df['Activity Status'] == 'In Progress'].copy()
in_progress_df['% Complete'] = in_progress_df['Activity % Complete(%)'] / 100
in_progress_df['Estimated Duration'] = (in_progress_df['Actual Duration'] / in_progress_df['% Complete'].replace(0, 0.1)) * (1 - in_progress_df['% Complete'])
in_progress_df['Estimated Duration'] = in_progress_df["Estimated Duration"] + in_progress_df["Actual Duration"]
in_progress_df['Max Duration Inc. Float'] = in_progress_df['Original Duration'] + in_progress_df['Total Float']

def classify(row):
    if row['Estimated Duration'] <= row['Original Duration']:
        return 'On-Time'
    elif row['Estimated Duration'] <= row['Max Duration Inc. Float']:
        return 'Can be on-time using float'
    else:
        return 'Delayed'

in_progress_df['Status'] = in_progress_df.apply(classify, axis=1)
status_counts = in_progress_df['Status'].value_counts()

st.header("2. In Progress Task Risk Assessment")
st.write("Task completion estimate based on actuals, float, and progress")
fig, ax = plt.subplots()
colors = ['#4CAF50', '#FFC107', '#F44336']  # Green, Yellow, Red
labels = ['On-time', 'Can be achieved on-time using float', 'Delayed']
sizes = status_counts.values
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
ax.axis('equal')
st.pyplot(fig)
st.dataframe(in_progress_df[['Original Duration', 'Max Duration Inc. Float', 'Estimated Duration']])

# Graph 3

st.header("3. Projected Dependency Cascade")
st.write("This chart shows the top N root tasks and how many downstream tasks are dependent on them.")

incomplete_tasks_df = df[df['Activity Status'].isin(['Not Started', 'In Progress'])].copy()

incomplete_tasks_df['Parsed Successors'] = incomplete_tasks_df['Successor Details'].fillna("").apply(
    lambda x: [s.split(':')[0].strip() for s in str(x).split(',') if ':' in s]
)

dependency_map = {row['Activity ID']: row['Parsed Successors'] for _, row in incomplete_tasks_df.iterrows()}

top_n_tasks = sorted(dependency_map.items(), key=lambda x: len(x[1]), reverse=True)[:15]
top_task_ids = [task for task, _ in top_n_tasks]

def trace_downstream(task, visited):
    if task in visited:
        return set()
    visited.add(task)
    affected = set()
    for succ in dependency_map.get(task, []):
        affected.add(succ)
        affected |= trace_downstream(succ, visited)
    return affected

cascade_count = {}
for task in top_task_ids:
    affected = trace_downstream(task, set())
    cascade_count[task] = len(affected)

cascade_series = pd.Series(cascade_count).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
cascade_series.plot(kind='bar', color='#F44336', ax=ax)
ax.set_title("Top 15 Tasks by Downstream Dependencies")
ax.set_ylabel("Number of Affected Tasks")
ax.set_xlabel("Root Task")

plt.xticks(rotation=90)
plt.tight_layout()
st.pyplot(fig)
st.subheader("Raw Counts")
st.dataframe(cascade_series.reset_index().rename(columns={'index': 'Task ID', 0: 'Affected Task Count'}))

st.metric(
    label="Estimated On-Time Completion Rate (In-Progress Tasks)",
    value="30.00%",
    # delta="-10% vs last review",  # optional if comparing previous snapshot
    help="Percentage of in-progress tasks projected to finish on or before time"
)

st.metric(
    label="Before or On-Time Start Rate (Completed and In-Progress tasks)",
    value="97.96%",
    # delta="+3% improvement",  # optional
    help="Share of tasks that started on or before their planned start date"
)


# # --- Insight 2: In-Progress Completion Estimate ---
# in_progress_df = df[df['Activity Status'] == 'In Progress'].copy()
# in_progress_df['% Complete'] = in_progress_df['Activity % Complete(%)'] / 100
# in_progress_df['Estimated Duration'] = in_progress_df['Actual Duration'] / in_progress_df['% Complete'].replace(0, 0.01)
# in_progress_df['Est. Remaining'] = in_progress_df['Estimated Duration'] - in_progress_df['Actual Duration']
# in_progress_df['On Track'] = in_progress_df['Est. Remaining'] <= in_progress_df['Remaining Duration']
# on_track_summary = in_progress_df['On Track'].value_counts()
# on_track_percent = on_track_summary.get(True, 0) / on_track_summary.sum() * 100


# # Insight 4: On-Time Start Analysis
# start_df = df[df['Activity Status'].isin(['Completed', 'In Progress'])].copy()
# mask = (~start_df['Actual Start'].isna()) & (~start_df['Planned Start'].isna())
# start_df = start_df[mask]
# start_df['On Time Start'] = start_df['Actual Start'] <= start_df['Planned Start']
# start_stats = start_df['On Time Start'].value_counts(normalize=True) * 100

# # --- Streamlit App ---



# st.header("2. In-Progress Task Completion Estimate")
# st.metric("On-Time %", f"{on_track_percent:.2f}%")
# st.bar_chart(on_track_summary.rename({True: "On Time", False: "Delayed"}))

# st.header("4. On-Time Start Analysis")
# st.metric("On-Time Start %", f"{start_stats.get(True, 0):.2f}%")
# st.metric("Late Start %", f"{start_stats.get(False, 0):.2f}%")

# # Graph 2
# # df = pd.read_excel("./MDC1_BL.xlsx")
# # df = df.rename(columns={'(*)Activity Type': 'Activity Type', '(*)Planned Start': 'Planned Start', '(*)Planned Finish': 'Planned Finish', '(*)Actual Duration(d)': 'Actual Duration', 'Remaining Duration(d)': 'Remaining Duration', '(*)Total Float(d)': 'Total Float', '(*)Remaining Float(d)': 'Remaining Float', '(*)Predecessor Details': 'Predecessor Details', '(*)Successor Details': 'Successor Details', 'Original Duration(d)': 'Original Duration'})



# # Graph 5
# # df = pd.read_excel("MDC1_BL.xlsx")  


