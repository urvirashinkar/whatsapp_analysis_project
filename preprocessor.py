import re

import pandas as pd

def preprocess(data):
    # This pattern handles both [date, time] and date, time - user formats
    # It looks for: Date, Time, User, Message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?)(?:\s-\s|\]\s)([^:]+):\s(.*)'

    messages = re.findall(pattern, data)

    if not messages:
        # If no messages found, return an empty DF so Streamlit doesn't crash
        return pd.DataFrame(columns=["date", "time", "user", "message"])

    df = pd.DataFrame(messages, columns=["date", "time", "user", "message"])

    # Combine date and time immediately into a single Series
    df['full_date'] = pd.to_datetime(df['date'] + ' ' + df['time'], dayfirst=True)

    # Extract components
    df['only_date'] = df['full_date'].dt.date
    df['year'] = df['full_date'].dt.year
    df['month_num'] = df['full_date'].dt.month
    df['month'] = df['full_date'].dt.month_name()
    df['day'] = df['full_date'].dt.day
    df['day_name'] = df['full_date'].dt.day_name()
    df['hour'] = df['full_date'].dt.hour
    df['minute'] = df['full_date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

