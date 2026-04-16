from collections import Counter
import pandas as pd
import re
from urlextract import URLExtract
from wordcloud import WordCloud
import emoji
extractor = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'].str.contains('omitted', case=False, na=False)].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))


    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    X = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'name', 'user': 'percentage'})
    return X, df

def create_wordcloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read().split()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Remove media + deleted + empty/system messages
    temp = df[
        ~df['message'].str.contains('omitted|deleted|changed the group', case=False, na=False)
    ]

    # Optional: remove very short/noisy messages
    temp = temp[temp['message'].str.strip().str.len() > 0]

    def remove_stop_words(message):
        words = []
        for word in message.split():
            if word.lower() not in stop_words and len(word) > 2:  # 👈 ADD THIS
                words.append(word)
        return " ".join(words)
    
    import re
    def clean_text(text):
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove non-ASCII (emojis, Hindi)
        return text

    wc = WordCloud(
    width=500,
    height=500,
    min_font_size=10,
    background_color='white',
    font_path='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'  # Mac
)
    temp['message'] = temp['message'].apply(remove_stop_words)
    temp['message'] = temp['message'].apply(clean_text)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):

    # Load stopwords properly
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().split())   # ✅ use set (faster lookup)

    # Filter user
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Remove unwanted messages
    temp = df[
        ~df['message'].str.contains(
            'omitted|deleted|changed the group|joined|left',
            case=False,
            na=False
        )
    ]

    temp = temp[temp['message'].str.strip().str.len() > 0]

    # 🔥 Clean text
    def clean_text(text):
        text = re.sub(r'http\S+', '', text)       # remove links
        text = re.sub(r'[^\w\s]', '', text)       # remove punctuation
        return text

    words = []

    for message in temp['message']:
        message = clean_text(message)

        for word in message.lower().split():

            # ✅ Hinglish filtering
            if (
                word not in stop_words and
                len(word) > 2 and              # remove single chars (त, म)
                not word.isdigit()             # remove numbers
            ):
                words.append(word)

    # Get top 20
    common_words = Counter(words).most_common(20)

    return_df = pd.DataFrame(common_words, columns=['Word', 'Count'])

    return return_df

def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        for c in message:
            if c in emoji.EMOJI_DATA:
                emojis.append(c)
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['Emoji', 'Count'])
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()    

def acitivity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap