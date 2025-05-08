import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

from db import engine

# streamlit run main.py to run the script

st.sidebar.header("Plots shown")
big_num = st.sidebar.checkbox("Big Numbers", value=True)
profit_p_emp = st.sidebar.checkbox("Profit Per Employee", value=True)
employee_plots = st.sidebar.checkbox("Plost from Specific Employee", value=True)

st.title('Ticket Tracker')

# Big Numbers
if big_num:
    st.header("Big numbers per month", divider='blue')
    st.markdown("This plot shows values for a respective month")


    @st.cache_data(ttl=300)
    def load_months():
        with engine.connect() as conn:
            df = pd.read_sql_query("SELECT DISTINCT month_name FROM client_pay_per_work ORDER BY month_name", conn)
            df['month_date'] = pd.to_datetime(df['month_name'], format="%B %Y")
            df = df.sort_values('month_date')
        return df['month_name'].tolist()


    month = st.selectbox("Escolha um mês", load_months())


    @st.cache_data(ttl=300)
    def load_client_pay_data(selected_month):
        with engine.connect() as conn:
            query = f"SELECT * FROM client_pay_per_work WHERE month_name = '{selected_month}'"
            df = pd.read_sql_query(query, conn)
        return df


    c1, c2 = st.columns(2)

    pay_per_work = load_client_pay_data(month)

    c1.metric("Amount gained in an year", round(pay_per_work['total_payment'].sum(), 2))

    c2.metric("Hours worked", round(pay_per_work['total_hours'].sum(), 2))

# Profit Per Employee
if profit_p_emp:
    st.header("Profit per employee", divider='blue')
    st.markdown(
        "This plot shows the relation between each employee and it's mean profit generated throughout the months")


    @st.cache_data(ttl=300)
    def load_employee_profit():
        with engine.connect() as conn:
            df = pd.read_sql_query(
                "SELECT employee_id, employee, ROUND(AVG(revenue_generated), 2) AS mean_profit, ROUND(AVG(employee_total_payment), 2) AS mean_payment FROM employee_paid_and_generated GROUP BY employee_id, employee ORDER BY employee_id",
                conn)
        return df


    chart_data = load_employee_profit()

    slider = st.slider("Choose a minimum value:", 1, max_value=int(chart_data['mean_profit'].max()), step=100)
    st.markdown(f'Value selected: :blue[***{slider}***]')

    # Filter according to slider
    filtered = chart_data[chart_data['mean_profit'] >= slider].reset_index(drop=True)

    st.bar_chart(data=filtered, x="employee", y=['mean_profit', 'mean_payment'], x_label="Employee", y_label='Mean Profit',
                 use_container_width=True, stack=False)

    # Show table
    st.dataframe(chart_data)

# Plots per Employee
if employee_plots:

    st.header("Plots From Specific Employee", divider='blue')
    st.markdown("These plots will show different stats from an employee")

    @st.cache_data(ttl=300)
    def load_employees():
        with engine.connect() as conn:
            df = pd.read_sql_query(
                "SELECT name FROM employees ORDER BY id",
                conn)
        return df

    selected_employee = st.selectbox("Choose an employee", load_employees())

    ce1, ce2 = st.columns(2)

    def load_avg_days():
        with engine.connect() as conn:
            df = pd.read_sql_query(f"SELECT DATE_TRUNC('month', created_at) AS month_year, AVG(ended_at - created_at) AS avg_duration_of_task FROM tickets_infos WHERE employee = '{selected_employee}' AND ended_at IS NOT NULL GROUP BY month_year ORDER BY month_year", conn)
            df['month_year'] = pd.to_datetime(df['month_year'])
            return df

    avg_days = load_avg_days()

    chart_avg_days = (
        alt.Chart(avg_days)
        .mark_line(point=True)
        .encode(
            x=alt.X('month_year:T', title='Month'),
            y=alt.Y('avg_duration_of_task:Q',
                    sort=avg_days['avg_duration_of_task'].tolist().reverse(),
                    title='Days to complete task'),
            tooltip=['month_year', 'avg_duration_of_task']
        )
    )

    ce1.altair_chart(chart_avg_days, use_container_width=True)

    def load_avg_difficulty():
        with engine.connect() as conn:
            df = pd.read_sql_query(f"""
                        SELECT 
                            DATE_TRUNC('month', created_at) AS month_year,
                            difficulty_id,
                            difficulty, 
                            COUNT(*) AS difficulty_count
                        FROM tickets_infos
                        WHERE employee = '{selected_employee}' 
                        GROUP BY month_year, difficulty_id, difficulty
                        ORDER BY month_year, difficulty_count DESC
                    """, conn)

            df['month_year'] = pd.to_datetime(df['month_year'])

            # Group by Month + Get the most frequent difficulty
            most_frequent_difficulties = df.loc[df.groupby('month_year')['difficulty_count'].idxmax()]

            # Drops difficulty_count column
            most_frequent_difficulties = most_frequent_difficulties.drop(columns='difficulty_count')

            most_frequent_difficulties = most_frequent_difficulties.sort_values(by='difficulty_id')

            return most_frequent_difficulties

    avg_difficulty = load_avg_difficulty()

    difficulty_order = ['senior', 'hard', 'medium',  'easy']

    chart_difficulty = (
        alt.Chart(avg_difficulty)
        .mark_line(point=True)
        .encode(
            x=alt.X('month_year:T', title='Month'),
            y=alt.Y('difficulty:N',
                    sort=difficulty_order,
                    title='Difficulty'),
            tooltip=['month_year', 'difficulty']
        )
    )

    ce2.altair_chart(chart_difficulty, use_container_width=True)

    def tickets_done_per_month():
        with engine.connect() as conn:
            df = pd.read_sql_query(
                f"SELECT DATE_TRUNC('month', ended_at) AS month_year, COUNT(*) AS tickets_qty FROM tickets_infos WHERE employee = '{selected_employee}' AND ended_at IS NOT NULL GROUP BY month_year ORDER BY month_year",
                conn)
            df['month_year'] = pd.to_datetime(df['month_year'])
            return df


    count_tickets = tickets_done_per_month()

    chart_tickets_qty = (
        alt.Chart(count_tickets)
        .mark_line(point=True)
        .encode(
            x=alt.X('month_year:T', title='Month'),
            y=alt.Y('tickets_qty:Q',
                    title='Tickets Solved',
                    scale=alt.Scale(domain=[count_tickets['tickets_qty'].min(), count_tickets['tickets_qty'].max()])
                    ),
            tooltip=['month_year', 'tickets_qty']
        )
    )

    ce2.altair_chart(chart_tickets_qty, use_container_width=True)
