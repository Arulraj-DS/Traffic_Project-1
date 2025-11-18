import streamlit as st
import mysql.connector
import pandas as pd

# --------------------------
# Database connection
# --------------------------
def connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Arul@123",
            auth_plugin='mysql_native_password',
            database='police'
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# --------------------------
# Fetch data from table
# --------------------------
def fetch_all_data(query):
    conn = connection()
    if conn is None:
        return pd.DataFrame()

    try:
        mycursor = conn.cursor(dictionary=True)
        mycursor.execute(query)
        result = mycursor.fetchall()
        df = pd.DataFrame(result)
        mycursor.close()
        conn.close()
        return df
    except mysql.connector.Error as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# --------------------------
# Streamlit App
# --------------------------
st.set_page_config(layout="wide", page_title="Police Records Dashboard")

# Sidebar navigation
st.sidebar.title("🚨 Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Data Insights", "Search Vehicle Logs" ,"Creator Info"])

# --------------------------
# Page: Overview
# --------------------------
if page == "Overview":
    st.title("📋 Police Record Overview")
    query = "SELECT * FROM traffic_stops;"
    data = fetch_all_data(query)
    
    if not data.empty:
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("No data to display or failed to fetch data.")

# --------------------------
# Page: Data Insights
# --------------------------
elif page == "Data Insights":
    st.title("📊 Data Insights")
    query_map={
    "What are the top 10 vehicle_Number involved in drug-related stops?":"SELECT vehicle_number, COUNT(*) AS drug_stop_count FROM traffic_stops WHERE drugs_related_stop = 1 GROUP BY vehicle_number ORDER BY drug_stop_count DESC LIMIT 10;",
    "Which vehicles were most frequently searched?":"SELECT vehicle_number FROM traffic_stops WHERE search_conducted = 1",
    "Which driver age group had the highest arrest rate?":"SELECT CASE WHEN driver_age BETWEEN 0 AND 17 THEN '0-17' WHEN driver_age BETWEEN 18 AND 30 THEN '18-30' WHEN driver_age BETWEEN 31 AND 45 THEN '31-45' WHEN driver_age BETWEEN 46 AND 60 THEN '46-60' ELSE '60+' END AS age_group, COUNT(*) AS total_stops, SUM(is_arrested) AS total_arrests, ROUND(SUM(is_arrested) * 100.0 / COUNT(*), 2) AS arrest_rate FROM  traffic_stops GROUP BY  age_group ORDER BY arrest_rate DESC LIMIT 1;",
    "What is the gender distribution of drivers stopped in each country?":"SELECT country_name,driver_gender, count(*) as count  from traffic_stops group by country_name,driver_gender order by country_name, count desc;",
    "Which race and gender combination has the highest search rate?":"SELECT driver_race,driver_gender,COUNT(*) AS total_stops, SUM(search_conducted) AS total_searched, ROUND(SUM(search_conducted) * 100.0 / COUNT(*), 2) AS search_rate FROM traffic_stops GROUP BY  driver_race,  driver_gender ORDER BY search_rate DESC LIMIT 1;",
    "What time of day sees the most traffic stops?":"SELECT    HOUR(Stop_datetime) AS hour_of_day, COUNT(*) AS total_stops FROM  traffic_stops group by hour_of_day order by  hour_of_day limit 1;",
    "What is the average stop duration for different violations?":"select violation, round(avg(stop_duration),2) as Avg_stop_duration  from traffic_stops group by  violation order by Avg_stop_duration desc;",
    "Are stops during the night more likely to lead to arrests?":"SELECT CASE  WHEN HOUR(Stop_datetime) >= 20 OR HOUR(Stop_datetime) < 6 THEN 'Night' ELSE 'Day' END AS stop_time, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent FROM traffic_stops GROUP BY Stop_time;",
    "Which violations are most associated with searches or arrests?":"SELECT violation,COUNT(*) AS total_stops,SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS searches,ROUND(SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS search_rate_percent,SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests,ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent FROM traffic_stops GROUP BY violation ORDER BY arrest_rate_percent DESC, search_rate_percent DESC;",
    "Which violations are most common among younger drivers (<25)?":"SELECT driver_age,violation,COUNT(*) AS stop_count FROM traffic_stops WHERE driver_age < 25 GROUP BY driver_age, violation ORDER BY driver_age, stop_count DESC;",
    "Is there a violation that rarely results in search or arrest?":"SELECT violation,COUNT(*) AS total_stops,SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS searches,ROUND(SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) AS search_rate_percent,SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests,ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) AS arrest_rate_percent FROM traffic_stops GROUP BY violation ORDER BY search_rate_percent ASC, arrest_rate_percent ASC limit 1;",
    "Which countries report the highest rate of drug-related stops?":"select country_name, sum(case when drugs_related_stop then 1 else 0 end) as drugs_related_stop, ROUND(SUM(CASE WHEN drugs_related_stop THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS drug_related_rate_percent from traffic_stops group by country_name order by drug_related_rate_percent desc;",
    "What is the arrest rate by country and violation?":"SELECT country_name, violation, COUNT(*) AS total_stops,SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests,ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate_percent FROM traffic_stops GROUP BY country_name, violation ORDER BY country_name ASC, arrest_rate_percent DESC;",
    "Which country has the most stops with search conducted?":"select country_name, sum(case when search_conducted then 1 else 0 end )as total_stops from traffic_stops group by country_name order by total_stops desc;",

    "Yearly Breakdown of Stops and Arrests by Country":"select country_name,year,total_stops,total_arrests,rank() over ( partition by year order by total_arrests desc) as country_arrest_rank from (select country_name,YEAR(stop_datetime) AS year,count(*) as total_stops, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests from traffic_stops group by country_name,year )as yearly_summary order by country_arrest_rank ASC;",
    "Driver Violation Trends Based on Age and Race":"SELECT t.driver_race, a.age_group, t.violation, SUM(is_arrested) AS total_arrest, COUNT(*) AS total_violations FROM traffic_stops t JOIN (SELECT pk_id, CASE WHEN driver_age < 30 THEN 'Under 30' WHEN driver_age BETWEEN 30 AND 59 THEN '30-59' ELSE '60 and above' END AS age_group FROM traffic_stops) a ON t.pk_id = a.pk_id GROUP BY a.age_group, t.driver_race, t.violation ORDER BY a.age_group, t.driver_race;",
    "Time Period Analysis of Stops":"SELECT t.country_name, d.stop_year, d.stop_month, d.stop_hour, COUNT(*) AS total_stops FROM traffic_stops t JOIN (SELECT pk_id, EXTRACT(YEAR FROM Stop_datetime) AS stop_year, EXTRACT(MONTH FROM Stop_datetime) AS stop_month, EXTRACT(HOUR FROM Stop_datetime) AS stop_hour FROM traffic_stops) d ON t.pk_id = d.pk_id GROUP BY t.country_name, d.stop_year, d.stop_month, d.stop_hour ORDER BY d.stop_year, d.stop_month, d.stop_hour;",
    "Violations with High Search and Arrest Rates":"SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS searches, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate, ROUND((SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) + (SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS total_rate, RANK() OVER (ORDER BY (SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) + (SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) DESC) AS rank_order FROM traffic_stops GROUP BY violation ORDER BY total_rate DESC;",
    "Driver Demographics by Country":"SELECT country_name, driver_gender, driver_race, ROUND(AVG(driver_age)) AS avg_age, COUNT(*) AS total_drivers FROM traffic_stops GROUP BY country_name, driver_gender, driver_race ORDER BY country_name, total_drivers DESC;",
    "Top 5 Violations with Highest Arrest Rates":"select violation,count(*) as total_arrest from traffic_stops where is_arrested=1 group by violation limit 5;"
}

    selected_query = st.selectbox("Select a query to run", list(query_map.keys()))
    
    if st.button("Fetch Data"):
        result = fetch_all_data(query_map[selected_query])
        if not result.empty:
            st.dataframe(result, use_container_width=True)
        else:
            st.warning("No data returned.")

# --------------------------
# Page: Search Vehicle Logs
# --------------------------
elif page == "Search Vehicle Logs":
    st.title("🔍 Search Vehicle Logs and Violation")
    query = "SELECT * FROM traffic_stops;"
    data = fetch_all_data(query)

    with st.form("Log_Form"):
        country_name = st.text_input("Country Name").strip().lower()
        driver_gender = st.selectbox("Gender", ["M", "F"]).lower()
        driver_age = st.number_input("Driver Age", min_value=0, max_value=120, step=1)
        driver_race = st.text_input("Driver Race").strip().lower()
        search_conducted = int(st.selectbox("Search Conducted?", ["0", "1"]))
        stop_duration = st.selectbox("Stop Duration", data["stop_duration"].dropna().unique())
        drugs_related_stop = int(st.selectbox("Drug Related Stop?", ["0", "1"]))
        vehicle_number = st.text_input("Vehicle Number").strip()

        submitted = st.form_submit_button("Predict Vehicle Outcome")

        if submitted:
            filtered_data = data[
                (data["driver_gender"].str.lower() == driver_gender) &
                (data["driver_age"] == driver_age) &
                (data["search_conducted"] == search_conducted) &
                (data["stop_duration"] == stop_duration) &
                (data["drugs_related_stop"] == drugs_related_stop) &
                (data["vehicle_number"] == vehicle_number)
            ]

            if not filtered_data.empty:
                predicted_outcome = filtered_data["stop_outcome"].mode()[0]
                predicted_violation = filtered_data["violation"].mode()[0]
                stop_dt = filtered_data.iloc[0]["Stop_datetime"]  # take first row
                gender_display = "Male" if driver_gender == "m" else "Female"
            else:
                predicted_outcome = "No Record"
                predicted_violation = "No Record"
                stop_dt = "N/A"

            st.success(f"Predicted Outcome: {predicted_outcome}")
            st.info(f"Predicted Violation: {predicted_violation}")

            search_text="A search was conducted"  if int(search_conducted) else "No search was conducted"
            drug_text= "was drug-related" if int(drugs_related_stop) else "was not drug-related"

            

            st.write( f""" **🎯Prediction Summary**                     
🧾 A {driver_age}-year-old {gender_display} driver in {country_name} was stopped at {stop_dt.strftime("%b %d, %Y - %I:%M %p")}. {search_text}, and the stop {drug_text}.  
**Stop duration:** {stop_duration}  
**Vehicle number:** {vehicle_number}
""")

            

# -------------------------------- PAGE 4: Creator Info --------------------------------
elif page == "Creator Info":
    st.title("👩‍💻 Creator of this Project ")
    st.write("""
    **✍️Developed by  :** Arul Raj
             
    **🧠Skills        :** Python, SQL ,Streamlit, Pandas
    
    **🌐GitHub        :** [arulraj-github](https://github.com/arulraj-github)         
             
    """)




