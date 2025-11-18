# Traffic_Project-1
This project involves processing a dataset stored in an Excel file, cleaning and formatting the data (Data Processing), importing it into a MySQL database, and retrieving information using SQL queries based on various requirements. The processed data is visualized through an interactive dashboard built with Streamlit.


#Technologies Used
------------------

Python – Core programming language

Streamlit – Framework for building interactive web dashboards

Pandas – Data cleaning, manipulation, and analysis

SQL – To retrieve data from the database

MySQL – Database used to store the processed records

MySQL Connector – Python library for connecting to MySQL


#Data Processing (Data_Processing.ipynb)
-----------------------------------------

Data preprocessing is performed using Pandas. The main steps include:

1. Importing Required Libraries
import pandas as pd

2. Checking Null Values (Fill or correct missing values.)
df.isnull().sum()

3. Checking Duplicate Records
df[df['vehicle_number'].duplicated()]

4. Removing Unwanted Columns
df.drop(['column1', 'column2'], axis=1, inplace=True)

5. Renaming Columns
df.rename(columns={'OldName': 'NewName'}, inplace=True)

6. Converting Data Types
df['column'] = df['column'].astype(int)

7. Combining Date and Time
df['Stop_datetime'] = pd.to_datetime(df['stop_date'].astype(str) + ' ' + df['stop_time'].astype(str))

8. Dropping Unnecessary Columns
df.drop(['stop_date', 'stop_time', 'driver_age_raw', 'violation_raw'], axis=1, inplace=True)

9. Handling Missing Values in Specific Fields
df['search_type'] = df['search_type'].fillna('No Search')


#Visualization and App (Traffic_Project.py)
----------------------------------------------

The Streamlit app provides multiple interactive features:

1. Overview
Connects to the MySQL database: Displays all records in a table format

2. Data Insights
Runs analytical SQL queries
Each question is selected using a Selectbox
A button triggers execution of the query
Results are displayed dynamically

3. Search Vehicle Logs
Users can search using vehicle/driver details
Displays complete information related to the search

4. Creator Info
Shows developer information
Includes GitHub link for reference

5. Page Navigation
Custom navigator allows users to switch between pages easily

