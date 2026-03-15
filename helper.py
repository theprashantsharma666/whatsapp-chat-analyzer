from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]

    words = []
    for message in df['message']:
        words.extend(message.split())
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages,len(links)


def most_busy_users(df):
    df = df[df['user'] != 'group_notification']
    x = df['user'].value_counts().head()

    new_df = round(
        (df['user'].value_counts()/df.shape[0])*100,2
    ).reset_index().rename(columns={'index':'name','user':'percent'})

    return x,new_df


def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt','r', encoding='utf-8') as f:
        stop_words = f.read().split()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp.str.cat(sep=" "))

    return df_wc


def most_common_words(selected_user,df):
    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] !='<Media omitted>\n']

    words=[]
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    most_common_df = pd.DataFrame(Counter(words).most_common(20))

    return most_common_df


def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis=[]
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthy_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year','month_num','month']).count()['message'].reset_index()

    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time']=time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('date_num').count()['message'].reset_index()
    daily_timeline.rename(columns={'message':'message_count'}, inplace=True)

    return daily_timeline


def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    heatmap_data = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)

    return heatmap_data