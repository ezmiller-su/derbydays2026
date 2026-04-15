import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
import humanize

def format_currency(amount):
    return '${:,.2f}'.format(amount)

st.set_page_config(page_title='Derby Days 2026')

livestats = pd.read_csv('https://raw.githubusercontent.com/ezmiller-su/derbydays2026/refs/heads/main/derbydays_donations_2025.csv')
if st.sidebar.button(label='Refresh Data'):
    livestats = pd.read_csv('https://raw.githubusercontent.com/ezmiller-su/derbydays2026/refs/heads/main/derbydays_donations_2025.csv')
oldstats = pd.read_csv('scraper/derbydays_donations_2025.csv')

stats = pd.concat([livestats, oldstats])
stats['Timestamp'] = pd.to_datetime(stats['Timestamp'], format='%Y-%m-%d %H:%M:%S')

now = datetime.now()

stats = stats.sort_values(by='Timestamp')
stats = stats[stats['Timestamp'] >= pd.Timestamp('2026-04-12 16:00:00')]

total_raised = format_currency(stats["Total"].iloc[-1])
st.title(total_raised)
st.caption(f'Last Donation: {humanize.naturaltime(now - stats["Timestamp"].iloc[-1])}')

last_24h = stats[stats['Timestamp'] >= now - timedelta(hours=24)]
hour = stats[stats['Timestamp'] >= now - timedelta(hours=1)]

one_day = stats
options = {
    'Hour': hour,
    '24 Hours': last_24h,
    'All Time': stats,
    'Day': one_day,
}
day_options = {
    'Sunday':   '2026-04-12',
    'Monday':   '2026-04-13',
    'Tuesday':  '2026-04-14',
    'Wednesday':'2026-04-15',
    'Thursday': '2026-04-16',
    'Friday':   '2026-04-17'
}

timerange = st.sidebar.selectbox(label='Time range', options=list(options.keys()))
if timerange == 'Day':
    selected_day = st.sidebar.selectbox(label='Week Day', options=list(day_options.keys()))
    day = pd.Timestamp(day_options[selected_day])
    df = stats[(stats['Timestamp'] >= day) & (stats['Timestamp'] < day + timedelta(days=1))]
else:
    df = options[timerange]
if df.empty:
    st.warning("No data available for this time range.")
    st.stop()
st.sidebar.divider()

def line_graph():
    teams = [col for col in df if col.startswith('Syracuse - ')]

    if st.sidebar.toggle(label='Show Grand Total'):
        fig = px.line(df, x='Timestamp', y='Total')
        fig.update_traces(name='Grand Total')
    else:
        melted = df.melt(id_vars='Timestamp', value_vars=teams,
                         var_name='Team', value_name='Donations')
        melted['Team'] = melted['Team'].str.replace('Syracuse - ', '')
        fig = px.line(melted, x='Timestamp', y='Donations', color='Team')

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Donations ($)',
        yaxis_tickprefix='$',
        yaxis_tickformat=',.0f',
        xaxis_tickformat='%A, %-I%p',
        height=600,
        legend_title_text='',
    )
    return fig

def bar_chart():
    hourly = df.set_index('Timestamp')['Total'].resample('1h').agg(
        lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0
    ).reset_index()
    hourly.columns = ['Timestamp', 'Donations']

    fig = px.bar(hourly, x='Timestamp', y='Donations')
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Donations per Hour',
        yaxis_tickprefix='$',
        yaxis_tickformat=',.0f',
        xaxis_tickformat='%A, %-I%p',
        height=400,
    )
    return fig

st.plotly_chart(line_graph(), use_container_width=True)
st.plotly_chart(bar_chart(), use_container_width=True)