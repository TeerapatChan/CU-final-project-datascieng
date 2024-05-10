import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Read the CSV file
df = pd.read_csv("airflow_data/title_affiliation.csv")
df2 = pd.read_csv("airflow_data/title_keywords.csv")
st.title("Data Analysis of Chulalongkorn Research Papers")
selected_option = st.selectbox(
    "Choose the top university of the data",
    options=["1", "2", "3", "4", "5"]
)
selected_option = int(selected_option)

df_no_Thailand = df[df['affiliation_country'] != 'Thailand']
def show_highest_collaboration_country(df):
    st.header('Country that collaborate with Chulalongkorn University')
    chart_data = df.groupby('affiliation_country').agg({'title': 'count'}).rename(columns={'title': 'number of Research Papers'}).reset_index()
    highest_value = chart_data['number of Research Papers'].max()
    # highest_collaboration_country = chart_data[chart_data['Number of Research Papers'] == highest_value]['Country'].values[0]
    highest_collaboration_country = chart_data[chart_data['number of Research Papers'] == highest_value]['affiliation_country'].values
    # for idx in chart_data.index:
    #     print(chart_data.loc[idx]['Country'])

    colors = ['blue' for i in range(len(chart_data))]
    highest_country_index = chart_data[chart_data['affiliation_country'].isin(highest_collaboration_country)].index
    # print(chart_data['Country'])
    # print(chart_data['Country'] == highest_collaboration_country)
    # print(chart_data[chart_data['Country'] == highest_collaboration_country])
    for idx in highest_country_index:
        colors[idx] = 'crimson'

    fig = go.Figure(data=[go.Bar(
        x=chart_data['affiliation_country'],
        y=chart_data['number of Research Papers'],
        marker_color=colors, # marker color can be a single color value or an iterable
        text=chart_data['number of Research Papers'],
    )])
    fig.update_layout(title_text='Highest collaboration country with Chulalongkorn University', xaxis_title='affiliation_country', yaxis_title='number of Research Papers')

    # fig = px.bar(chart_data, x="Country", y="Number of Research Papers",text_auto='.s',color="Country", color_discrete_map={index: f"rgb({2*30},{2*20},{2*10})" if chart_data.loc[index]['Country'] == highest_collaboration_country else f"rgb({2*30},{2*20},{2*10})" for index in chart_data.index})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig)
    return highest_collaboration_country
# Bar chart with custom coloring for the highest collaboration country
# colors = ['red' if country == highest_collaboration_country else 'blue' for country in chart_data.index]
# st.bar_chart(chart_data, color="#ffaa00")

def show_top_universities(df,highest_collaboration_country):
    for top_country in highest_collaboration_country:
        st.write('All universities in '+ top_country + ' that collaborate with Chulalongkorn University')
        top_country_df = df[df['affiliation_country'] == top_country]
        chart_data = top_country_df.groupby('affiliation_name').agg({'title': 'count'}).rename(columns={'title': 'number of Research Papers'}).reset_index()
        st.bar_chart(chart_data, x='affiliation_name', y='number of Research Papers')
# for top_country in highest_collaboration_country:
#     st.header('All universities of '+ top_country + ' that collaborate with Thailand')
#     top_country_df = df_no_Thailand[df_no_Thailand['Country'] == top_country]
#     chart_data = top_country_df.groupby('University').agg({'Title': 'count'}).rename(columns={'Title': 'Number of Research Papers'}).reset_index()
#     st.bar_chart(chart_data, x='University', y='Number of Research Papers')




def find_top_universities(df,selected_option):
    # Filter for Thai universities
    thai_universities = df[df["affiliation_country"].str.strip() == "Thailand"]
    not_chula = thai_universities[thai_universities["affiliation_name"].str.strip() != "Chulalongkorn University"]
    # Group by university
    grouped_universities = not_chula.groupby("affiliation_name").size().reset_index(name="amount of research")
    top_universities = grouped_universities.nlargest(selected_option, "amount of research")["affiliation_name"].tolist()
    return top_universities , not_chula
def collab_graph(df,top_universities,thai_universities,selected_option):
    st.header("Collaboration countries with the top university in Thailand that collaborate with Chulalongkorn University")
    #Select title
    for i in range(selected_option):
        top_university = thai_universities[thai_universities["affiliation_name"] == top_universities[i]]
        title  = top_university["title"].unique()
        df_drop_keys = df.drop(columns=["keywords"])
        chosen_df = df_drop_keys[(df_drop_keys["title"].isin(title)) & (df_drop_keys["affiliation_country"] != "Thailand")]
        grouped_collab = chosen_df.groupby("affiliation_country").size().reset_index(name="amount of research")
        st.write(f"Collaboration countries with the top {i+1} university in Thailand ({top_universities[i]})")
        total_research = grouped_collab["amount of research"].sum()
        # Add a new column to calculate the percentage of research amount
        grouped_collab["Percentage"] = grouped_collab["amount of research"] / total_research
        # Group countries with less than 0.4% research amount
        threshold = 0.002
        grouped_collab.loc[grouped_collab["Percentage"] < threshold, "affiliation_country"] = "Others"
        # Filter out countries with less than 0.4% research amount
        # filtered_data = grouped_collab[grouped_collab["Percentage"] >= threshold]
        # st.write(filtered_data)
        # filtered_data = filtered_data.groupby("affiliation_country").size().reset_index(name="amount of research")
        fig_collab = px.pie(grouped_collab, values="amount of research", names="affiliation_country",height=600,width=800)



        # fig_collab = px.pie(grouped_collab, values="amount of research", names="affiliation_country")
        st.plotly_chart(fig_collab)
    return

def keyword_graph(df,top_universities,thai_universities,selected_option):
    st.header("top 10 keywords of the top university")
    #Select title
    for i in range(selected_option):
        top_university = thai_universities[thai_universities["affiliation_name"] == top_universities[i]]
        title  = top_university["title"].unique()
        #prepare data
        # thai_universities2 = top_university.drop(columns=["University", "Country"])
        # thai_universities2["Keywords"] = thai_universities2["Keywords"].str.split(",")
        # thai_universities3 = thai_universities2.explode("Keywords")
        # thai_universities3["Keywords"] = thai_universities3["Keywords"].str.strip("[]")
        df_without_year= df.drop(columns=["publication_year"])
        chosen_df = df_without_year[df_without_year["title"].isin(title)]
        grouped_keywords = chosen_df.groupby("keyword").size().reset_index(name="amount of research")
        top_keywords = grouped_keywords.nlargest(10, "amount of research")
        # grouped_keywords = thai_universities3.groupby("Keywords").size().reset_index(name="Amount of research")
        st.write(f"Keywords in the top {i+1} university in Thailand ({top_universities[i]})")
        fig = px.pie(top_keywords, values="amount of research", names="keyword")
        st.plotly_chart(fig)

def show_line_graph(df):
    # Read the CSV file
    st.header('The number of research papers over the years')
    df_with_count_key= df.dropna().groupby('keyword').agg({'title': 'count'}).reset_index()
    keyword = st.selectbox('Select keyword', df_with_count_key.dropna().sort_values(by='title',ascending=False)['keyword'].unique())

    all_years = pd.DataFrame({'publication_year': range(df['publication_year'].min(), df['publication_year'].max() + 1)})

    # Filter the DataFrame based on the selected keyword
    filtered_df = df[df['keyword'] == keyword]

    # Convert 'year' column to integers
    filtered_df['publication_year'] = filtered_df['publication_year'].astype(int)

    # Merge the DataFrame with all years with the filtered DataFrame
    merged_df = pd.merge(all_years, filtered_df, on='publication_year', how='left')

    merged_df =merged_df.groupby('publication_year').agg({'title': 'count'}).reset_index()

    # Fill missing values with 0
    merged_df.fillna({"title": 0},inplace=True)

    # Convert year to string
    merged_df['publication_year'] = merged_df['publication_year'].astype(str)
    # Plot the line chart
    st.subheader('Number of Research Papers over the years')
    st.line_chart(merged_df.rename(columns={'title': 'Number of Research Papers'}).set_index('publication_year'))

def main():
    top_universities , not_chula = find_top_universities(df,selected_option)
    collab_graph(df,top_universities,not_chula,selected_option)
    keyword_graph(df2,top_universities,not_chula,selected_option)
    highest_collaboration_country = show_highest_collaboration_country(df_no_Thailand)
    show_top_universities(df_no_Thailand,highest_collaboration_country)
    print(df2.head())
    show_line_graph(df2)
main()