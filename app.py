import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import seaborn as sns
import preprocessor
import helper

st.sidebar.title("Whatsapp Chat Analyzer")
st.title("Welcome to WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)
    if st.sidebar.button("Show Analysis"):
        num_messages,words,num_media_messages,num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3,col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Total Media Shared", num_media_messages)
        with col4:
            st.metric("Total Links Shared", num_links)

        # MONTHLY TIMELINE
        st.title("Monthly Timeline")
        timeline = helper.monthy_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # DAILY TIMELINE
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['date_num'], daily_timeline['message_count'], color='red')
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Messages")
        ax.set_title("Daily Messages")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # ACTIVITY MAP
        st.title('Activity Map')
        col1,col2 = st.columns(2)
        with col1:
            st.header('Most Busy Day')
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values)
            st.pyplot(fig)
        with col2:
            st.header('Most Busy Month')
            busy_month = helper.month_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_month.index,busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(12,5))
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # FINDING THE BUSIEST USER
        if selected_user=='Overall':
            st.title("Most Busy Users")
            x,new_df = helper.most_busy_users(df)
            fig,ax = plt.subplots()
            col1,col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WORDCLOUD
        st.title("WordCloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # MOST COMMON WORDS
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user,df)
        fig,ax = plt.subplots()
        ax.barh(most_common_df[0],most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # EMOJI ANALYSIS
        emoji_df = helper.emoji_helper(selected_user, df)
        emoji_df = emoji_df.rename(columns={0:'emoji', 1:'count'})
        emoji_df.index = emoji_df.index + 1
        emoji_df.index.name = "No."
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            if emoji_df.empty:
                st.write("No emojis to display in pie chart.")
            else:
                top_emoji_df = emoji_df.head(10)
                fig = px.pie(top_emoji_df,names='emoji',values='count',title="Top Emojis",color='emoji',color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig)