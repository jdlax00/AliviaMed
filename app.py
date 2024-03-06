import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load and prepare the dataset
@st.cache_data
def load_data():
    df = pd.read_csv('andy2.csv')
    df['Difference'] = df['Difference'].replace('[\$,]', '', regex=True).astype(float)
    df['Month'] = pd.to_datetime(df['Month'], format='%B', errors='coerce').dt.month
    return df

df = load_data()

# Sidebar - Hospital selection
hospital_list = df['Hospital'].unique()
selected_hospitals = st.sidebar.multiselect('Select Hospitals', hospital_list, default=hospital_list[:2])

for selected_hospital in selected_hospitals:
    df_filtered = df[df['Hospital'] == selected_hospital]

    # Start of the div block with custom styling for the border
    st.markdown(f"""
    <style>
    .hospital-section {{
        border: 1px solid #ddd; /* Faint border */
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px; /* Space between sections */
    }}
    </style>
    <div class="hospital-section">
    """, unsafe_allow_html=True)

    # Display hospital name within the styled div
    st.markdown(f"### Metrics for {selected_hospital}", unsafe_allow_html=True)
    
    # Display metrics within the styled div
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of Cases", len(df_filtered))
    with col2:
        st.metric("Average Difference ($)", round(df_filtered['Difference'].mean(), 2))
    with col3:
        st.metric("Average Service Duration", round(df_filtered['Service Duration'].mean(), 2))

    # Doctor leaderboard for each hospital
    st.markdown("#### Doctor Leaderboard", unsafe_allow_html=True)
    doctors_summary = df_filtered.groupby('Doctor').agg(Case_Count=('Doctor', 'count'), Total_Difference=('Difference', 'sum')).sort_values(by=['Case_Count', 'Total_Difference'], ascending=False).reset_index()
    st.table(doctors_summary)

    # End of the div block
    st.markdown("""
        </div>
    """, unsafe_allow_html=True)



# Time series of difference aggregated by month for both hospitals
st.subheader("Monthly Difference Trend")
plt.figure(figsize=(10, 4))
for selected_hospital in selected_hospitals:
    df_filtered = df[df['Hospital'] == selected_hospital]
    monthly_difference = df_filtered.groupby(pd.Grouper(key='Month')).agg(Monthly_Difference=('Difference', 'sum')).reset_index()
    plt.plot(monthly_difference['Month'].values, monthly_difference['Monthly_Difference'], marker='o', label=selected_hospital)

plt.title('Monthly Difference Trend')
plt.xlabel('Month')
plt.ylabel('Total Difference ($)')
plt.legend()
st.pyplot(plt)

# Gender distribution for both hospitals
st.subheader("Gender Distribution")
fig, axs = plt.subplots(1, len(selected_hospitals), figsize=(10, 4), sharey=True)
for i, selected_hospital in enumerate(selected_hospitals):
    df_filtered = df[df['Hospital'] == selected_hospital]
    gender_count = df_filtered['Sex'].value_counts().reset_index()
    gender_count.columns = ['Gender', 'Count']  # Rename for clarity
    sns.barplot(data=gender_count, x='Gender', y='Count', ax=axs[i])
    axs[i].set_title(f"{selected_hospital}")
    axs[i].set_xlabel('Gender')
    axs[i].set_ylabel('Count')

plt.tight_layout()
st.pyplot(fig)
