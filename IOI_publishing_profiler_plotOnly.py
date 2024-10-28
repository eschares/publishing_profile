# IOI Publishing Profiler
# Eric Schares, 5/4/24

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # to enable total count labels on top of stacked bar chart
import requests
from tqdm import tqdm
from stqdm import stqdm
from time import sleep
import glob

stqdm.pandas()

st.header('IOI Publishing Profiler')
st.markdown('#### Eric Schares')

with st.expander('More information:'):
    st.write('''
             This interactive dashboard helps to visualize characteristics about research publications from your university.
             
             Examples include:
             - Count and percentages of Corresponding Authored publications
             - Count and percentages of US federally funded publications
             ''')


#st.markdown('---')

# make sure these names are what appears in the Dimensions export file for CA
# For example, is it MIT or Massachusetts Institute of Technology?
institution_name = st.selectbox('**Choose an Institution to Analyze**', ['Iowa State University', 'Yale', 'MIT', 'test'])
institution_name_nospaces = institution_name.replace(' ', '')    # need a version of the name that can go into a filename

# OpenAlex IDs, lookup with https://api.openalex.org/institutions?search=name
institution_ids  = {'Iowa State University': 'I173911158',
                    'Yale': 'I32971472',
                    'MIT': 'I63966007',
                    'test': 'I173911158'}

institution_id = institution_ids[institution_name]    # used in OpenAlex data enrichment for Corresponding Authors
st.write(f'OpenAlex Institution ID: **{institution_id}**')

st.markdown('---')
st.subheader('Load Data')



### Load data - do it this way so it's not re-loaded over and over again each time we save this file
@st.cache_data
def load_data_excel(link, header):
   st.write(f'Loading file **{link}**')
   df = pd.read_excel(link, header=header)
   return df

@st.cache_data
def load_data_csv(link, header):
   st.write(f'Loading file **{link}**')
   df = pd.read_csv(link, header=header)
   return df

@st.cache_data
def load_data_parquet(link, header):
   st.write(f'Loading file **{link}**')
   df = pd.read_parquet(link)
   return df


### Load dataframe of merged publications ###
merged_file_flag = 0
df_file_picker = glob.glob(f'data/{institution_name_nospaces}/*_merged_small.parquet')
#df_file_picker
if df_file_picker:
    openalex_file_flag = 1
    if(df_file_picker[0].endswith('.xlsx')):
        merged = load_data_excel(df_file_picker[0], 1)      # df_file_picker is a list, get the 0th element, header=1 if Excel file
    else:
        merged = load_data_parquet(df_file_picker[0], 0)
else:
    st.write('No file found')


# TODO can we get away with just loading *_merged if it's available? Have to test if it is, can't go off OpenAlex data bc need to do that first
# quit going through the .merge every damn time. Just load it.

# merged = df[df['DOI'].notna()].merge(df_usff[['DOI', 'PubYear']], how='left', left_on='DOI', right_on='DOI', suffixes=('', '_y'))
# merged['is_USFF'] = 'no'
# merged.loc[ merged['PubYear_y'].notna(), 'is_USFF'] = 'yes'
# merged['is_corresponding_is_USFF'] = merged['is_corresponding'].astype(str) + '_' + merged['is_USFF'].astype(str)
# merged['is_USFF_is_corresponding'] = merged['is_USFF'].astype(str) + '_' + merged['is_corresponding'].astype(str)
# merged.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_merged.csv', index=False)

#merged

yesyes = merged[merged['is_USFF_is_corresponding']=='yes_yes']
#st.subheader('YesYes')
yesyes.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes.csv', index=False)



###### Plots ######

st.markdown('---')
st.subheader(f'Corresponding Authored Records by {institution_name}, by Year')
col1, col2 = st.columns(2)

fig = px.histogram(merged, x='PubYear', color='is_corresponding', text_auto=True,
             color_discrete_map={
                "yes": "blue",
                "no": "salmon",
                "unknown": "lightgray"},
                category_orders={"is_corresponding": ["yes", "no"]})
fig.update_xaxes(type='category', categoryorder='category ascending')
fig.update_layout(legend_traceorder='reversed')#, width=500)


# col1.subheader('Raw Counts')
# col1.plotly_chart(fig)

fig2 = px.histogram(merged, x='PubYear', color='is_corresponding', barnorm='percent', text_auto=True,
             color_discrete_map={
                "yes": "blue",
                "no": "salmon",
                "unknown": "lightgray"},
                category_orders={"is_corresponding": ["yes", "no"]})
fig2.update_xaxes(type='category', categoryorder='category ascending')
fig2.update_layout(legend_traceorder='reversed')#, width=500)

# col2.subheader('Percentages')
# col2.plotly_chart(fig2)

with col1:
    st.markdown('#### Raw Counts')
    st.plotly_chart(fig)

with col2:
    st.markdown('#### Percentages')
    st.plotly_chart(fig2)



st.markdown('---')
st.subheader(f'US Federally Funded Research with any {institution_name} author, by Year')
col3, col4 = st.columns(2)

fig3 = px.histogram(merged, x='PubYear', color='is_USFF', text_auto=True,
             color_discrete_map={
                "yes": "blue",
                "no": "salmon",
                "unknown": "lightgray"},
                category_orders={"is_USFF": ["yes", "no"]})
fig3.update_xaxes(type='category', categoryorder='category ascending')
fig3.update_layout(legend_traceorder='reversed')

# col1.plotly_chart(fig3)

fig4 = px.histogram(merged, x='PubYear', color='is_USFF', barnorm='percent', text_auto=True,
             color_discrete_map={
                "yes": "blue",
                "no": "salmon",
                "unknown": "lightgray"},
                category_orders={"is_USFF": ["yes", "no"]})
fig4.update_xaxes(type='category', categoryorder='category ascending')
fig4.update_layout(legend_traceorder='reversed')

# col2.plotly_chart(fig4)

with col3:
    st.subheader('Raw Counts')
    st.plotly_chart(fig3)

with col4:
    st.subheader('Percentages')
    st.plotly_chart(fig4)



st.markdown('---')
st.subheader(f'{institution_name} Corresponding Authored US Federally Funded Research, by Year')
bullet_text = ''' Legend shows many combinations of Correspoding Author and US federal funding
* **'unknown_no'** means we don't know if the CorrAuth is from the institution of interest, but it's not federally funded (available only if data ran through OpenAlex)
* **'unknown_yes'** means it **is** federally funded, but we still don't have the CorrAuth information
* **'no_no'** are publications that are neither CorrAuth by our institution or federally funded
* **'no_yes'** are publications that are not CorrAuth by the institution of interest, but *do* have federal funding
* **'yes_no'** are publications that *are* CorrAuth from the institution of interest, but not federally funded
* **['yes_yes]** *finally* the records we are interested in. CorrAuth is from the insitution and also have federal funding acknowledged
'''

st.markdown(bullet_text)

col5, col6 = st.columns(2)

fig5 = px.histogram(merged, x='PubYear', color='is_corresponding_is_USFF', text_auto=True,
             color_discrete_map={
                "yes_yes": "blue",
                "yes_no": "lightblue",
                "no_yes": "salmon",
                "no_no": "lightgray"},
                category_orders={"is_corresponding_is_USFF": ["yes_yes", "yes_no", "no_yes", "no_no"]})
fig5.update_xaxes(type='category', categoryorder='category ascending')
fig5.update_layout(legend_traceorder='reversed')

fig6 = px.histogram(merged, x='PubYear', color='is_corresponding_is_USFF', barnorm='percent', text_auto=True,
             color_discrete_map={
                "yes_yes": "blue",
                "yes_no": "lightblue",
                "no_yes": "salmon",
                "no_no": "lightgray"},
                category_orders={"is_corresponding_is_USFF": ["yes_yes", "yes_no", "no_yes", "no_no"]})
fig6.update_xaxes(type='category', categoryorder='category ascending')
fig6.update_layout(legend_traceorder='reversed')


with col5:
    st.subheader('Raw Counts')
    st.plotly_chart(fig5)

with col6:
    st.subheader('Percentages')
    st.plotly_chart(fig6)



# base code from StackOverflow user Maarten Fabré, modified by Eric Schares
# this is VERY hardcoded to what I'm trying to do so edit carefully
# for example, I hardcode the yesyes_bypublisher['PubYear'] filter
# had to do it this way to automate the calcuation by year of number of publishers that make up 50%
def get_50_percent_passyear(year, pct=50):
    '''
    Input: year as int
    Returns: int, length of Series required to meet pct level, defaults to 50%  (example: 4)
    '''    
    group = yesyes_bypublisher[yesyes_bypublisher['PubYear']==year]
    
    # moves is one Series, in this case DOI. Descending series of counts
    moves = group['DOI'].sort_values(ascending=False)
    #print(moves)
    
    # cumsum is series of fractions, cumulatively summing each row (0.21, 0.34. 0.45, 0.56)
    cumsum = moves.cumsum() / moves.sum()
    #print(cumsum)
    
    # idx is the length of cumulative sum where it is still less than .50, then go one more
    idx = len(cumsum[cumsum < pct/100]) + 1
    #print(f'idx: {idx}\n')
    
    # `idx` is the first index which has a cumulative sum of `pct` or higher
    # so grab indexes 0 to whatever index we need
    idx = moves.index[:idx]  
    #print(f'second idx: {idx}')
    
    # here, `idx` is the Index of all the moves with a cumulative contribution of `pct` or higher
    #print(f'here is {group.loc[idx]}')
    return len(group.loc[idx].set_index(['Publisher'], drop=True)['DOI'])


st.markdown('---')
st.header(f"Further Details on the 'yes_yes' Section")
st.subheader(f'Look at {institution_name} Corresponding Authored & Federally Funded Documents')
st.subheader('Breakdown by **:red[Publisher]**')
#col7, col8 = st.columns(2)

yesyes_bypublisher = yesyes.groupby(['Publisher', 'PubYear']).count().reset_index()[['Publisher', 'PubYear', 'DOI']]
yesyes_bypublisher.sort_values(by='DOI', ascending=False, inplace=True)
yesyes_bypublisher.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_groupbypublisher.csv', index=False)

# #fig7 = px.bar(yesyes_bypublisher, x='PubYear', y='DOI', color='Publisher', text_auto=True, barmode='stack')
# fig7 = px.pie(yesyes_bypublisher, values='DOI', names='Publisher', facet_col='PubYear')
# fig7.update_traces(textposition='inside', textinfo='percent+label+value')#, rotation=-75)
# #fig7.update_xaxes(type='category', categoryorder='category ascending')
# fig7.update_layout(width=1900, showlegend=False)

# st.plotly_chart(fig7)

st.subheader('By Count')

fig8 = px.bar(yesyes_bypublisher, x='PubYear', y='DOI', color='Publisher', text_auto=True)
fig8.update_xaxes(type='category', categoryorder='category ascending')
st.plotly_chart(fig8)

#st.write(len(get_50_percent(yesyes_bypublisher[yesyes_bypublisher['PubYear']==2023])))
#st.write(f"Publishers :{yesyes_bypublisher.groupby(['PubYear'])['Publisher'].count()}")



st.subheader('By Percent')
fig9 = px.histogram(yesyes_bypublisher, x='PubYear', y='DOI', color='Publisher', text_auto=True, barnorm='percent')
fig9.update_xaxes(type='category', categoryorder='category ascending')
#fig9.update_yaxes(type='category', categoryorder='total ascending')
fig9.update_traces(texttemplate = "%{value:.2f}%")
fig9.update_layout(height=650, width=1600)
fig9.update_yaxes(tick0=0, dtick=10)
#fig9.add_shape(type="line", x0=min('PubYear'), x1=max('PubYear'), y0=50, y1=50, line=dict(color="Purple", width=10, dash="dot")),
fig9.add_hline(y=25, line_width=2, line_color='purple', line_dash='dot')
fig9.add_hline(y=50, line_width=2, line_color='purple', line_dash='dot')
fig9.add_hline(y=75, line_width=2, line_color='purple', line_dash='dot')
st.plotly_chart(fig9)


publisher_50percent_point = yesyes_bypublisher.groupby(['PubYear'])['Publisher'].count().reset_index()
publisher_50percent_point.loc[:, '50percent_point'] = publisher_50percent_point.loc[ :, 'PubYear'].apply(get_50_percent_passyear)
publisher_50percent_point.rename(columns={'Publisher': 'NumPublishers'}, inplace=True)
publisher_50percent_point



st.markdown('---')
#st.header('Further Details on the `yes_yes` Documents (Corresponding & Federally Funded)')
st.subheader('Breakdown by **:red[Journal Title]**')

yesyes_byjournaltitle = yesyes.groupby(['Source title', 'PubYear', 'Publisher']).count().reset_index()[['Source title', 'PubYear', 'Publisher', 'DOI']]
yesyes_byjournaltitle.sort_values(by='DOI', ascending=False, inplace=True)
yesyes_byjournaltitle.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_groupbyjournaltitle.csv', index=False)

top20_toggle = st.radio('', ['Show only the Top 20 journal titles', 'Show up to 2,000 journal titles'], label_visibility = 'collapsed')
if top20_toggle=='Show only the Top 20 journal titles':
    maxallowed = 20
else:
    maxallowed = 2000

fig10 = px.histogram(yesyes_byjournaltitle, x='Source title', y='DOI', color='PubYear', text_auto='True',
                    title='Top Journal Titles with Corresponding Authored USFF Outputs',
                    category_orders={'PubYear': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]})
fig10.update_xaxes(categoryorder='total descending', maxallowed=maxallowed)
fig10.update_layout(height=1000, showlegend=True, legend_traceorder='reversed')

journal_totals = yesyes_byjournaltitle.groupby('Source title')['DOI'].sum().sort_values(ascending=False).reset_index()
journal_totals[0:maxallowed]
# Add total count labels on top of each stacked bar chart
# This didn't work for some reason, the plot ended up squished way over to the right with a big blank area??
# fig10.add_trace(go.Scatter(
#     x=journal_totals[0:maxallowed]['Source title'],
#     y=journal_totals[0:maxallowed]['DOI'],
#     text=journal_totals[0:maxallowed]['DOI'],
#     mode='text',
#     textposition='top center',
#     textfont=dict(size=12,),
#     showlegend=False
# ))

st.plotly_chart(fig10)


# fig11 = px.histogram(yesyes_byjournaltitle, x='PubYear', y='DOI', color='Source title', text_auto='True', barnorm='percent')
# fig11.update_xaxes(type='category', categoryorder='category ascending')
# fig11.update_traces(texttemplate = "%{value:.2f}%")
# fig11.update_layout(height=1000, showlegend=True)
# st.plotly_chart(fig11)
# 



st.markdown('---')
#st.header('Further Details on the `yes_yes` Documents (Corresponding & Federally Funded)')
st.subheader('Breakdown by **:red[Funder]**')

# Load funder name conversion dictionary into memory, don't want to keep re-opening it every time
import csv

lookup_data = {}

# def load_lookupfile(file_path):
#     with open(file_path, 'r') as f:
#         reader = csv.reader(f)
#         for line in reader:
#             print(line)
#             key, value = (line[0], line[1])
#             lookup_data[key] = value

def lookup(key):
    return lookup_data.get(key)

@st.cache_data
def load_dict_from_csv(file_path, key_column, value_column):
    """Loads a dictionary from an csv file.

    Args:
        file_path: The path to the file.
        key_column: The name of the column to use as keys in the dictionary.
        value_column: The name of the column to use as values in the dictionary.

    Returns:
        A dictionary created from the data.
    """

    dict_df = pd.read_csv(file_path)
    lookup_data = dict(zip(dict_df[key_column], dict_df[value_column]))
    return lookup_data

#load_lookupfile('Dimensions_USFFGroup_mapped_to_RORs_and_2ndlevel_parent_onlytwocolumns.csv')
lookup_data = load_dict_from_csv('Dimensions_USFFGroup_mapped_to_RORs_and_2ndlevel_parent_onlytwocolumns.csv', 'Name_no_parentheses', 'parentName')

def convert_Funder_string_to_Parent(funder_string: str) -> list:
    """
    Pass in Dimensions `Funder` cell on each row
    Comes in as long string of funder names
    Want to isolate the US federal funders and use the conversion file to get the 2nd level Parent name
    
    
    Input: Funder cell (Directorate for Computer & Information Science & Engineering; National Cancer Institute)
    Output: List of Parent names (['US National Science Foundation', 'Health and Human Services'])
    """
    #print(f'Checking {funder_string=}')
    
    result = []
    
    parts = funder_string.split('; ')  # when only one passed in, no semicolon, still returns it
    
    for i in range(len(parts)):
        #print(parts[i])
        #print(lookup(parts[i]))
        if lookup(parts[i]):
            #print(f'{parts[i]}, parent is {lookup(parts[i])}')
            result.append(lookup(parts[i]))
    
    return(result)

def dedupe_Funder_names(multiple_funder_string: list) -> list:
    '''
    Takes in a list of normalized 2nd level funder names
    Converts to set to keep only unique ones
    Converts back to list
    Returns list of only the unique ones
    '''
    newset = set(multiple_funder_string)
    return(list(newset))

# Match Funder strings to the names of the 2nd level Parents (under US Govt.)
# Use `yesyes`, which is the full DOI-level data
yesyes.loc[yesyes['Funder'].notna(), 'ParentAgencyWithDuplicates'] = yesyes.loc[yesyes['Funder'].notna(),'Funder'].apply(convert_Funder_string_to_Parent)
# then you have to dedupe the 2nd level Parents. If it acknowledges USDA twice and NASA three times, just keep one of each.
yesyes.loc[yesyes['Funder'].notna(), 'ParentAgency'] = yesyes.loc[yesyes['Funder'].notna(),'ParentAgencyWithDuplicates'].apply(dedupe_Funder_names)
yesyes.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_with_funderDuplicates.csv', index=False)

# Explode to repeat DOIs that have multiple funders
funders_exploded = yesyes.explode('ParentAgency')
funders_exploded.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_DOIlevel_funders_exploded.csv', index=False)

# any time you have a df name that contains _by, it's from a groupby. Summary data in there
yesyes_byfunderexploded = funders_exploded.groupby(['ParentAgency', 'PubYear']).count().reset_index()[['ParentAgency', 'PubYear', 'DOI']]
yesyes_byfunderexploded.sort_values(by='PubYear', ascending=True, inplace=True)
yesyes_byfunderexploded["PubYear"] = yesyes_byfunderexploded["PubYear"].astype(str)
yesyes_byfunderexploded.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_groupbyfunderexploded.csv', index=False)

fig11 = px.bar(yesyes_byfunderexploded, x='ParentAgency', y='DOI', color='PubYear', text_auto='True',
                     title='Top Funding Agencies with Corresponding Authored USFF Outputs<br>Papers that acknowledge more than one funder are included here multiple times',
                     category_orders={'PubYear': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]})
fig11.update_xaxes(categoryorder='total descending')
fig11.update_layout(height=1000, showlegend=True, legend_traceorder='reversed')

funder_totals = yesyes_byfunderexploded.groupby('ParentAgency')['DOI'].sum().sort_values(ascending=False).reset_index()
#funder_totals

# Add total count labels on top of each stacked bar chart
# https://stackoverflow.com/questions/72761553/plotly-how-to-display-the-total-sum-of-the-values-at-top-of-a-stacked-bar-chart
fig11.add_trace(go.Scatter(
    x=funder_totals['ParentAgency'],
    y=funder_totals['DOI'],
    text=funder_totals['DOI'],
    mode='text',
    textposition='top center',
    textfont=dict(size=12,),
    showlegend=False
))

st.plotly_chart(fig11)


# Let the user choose a funder to look at more closely. First list all the possible funders found in this set
list_of_funders = funder_totals['ParentAgency']
chosen_funder = st.selectbox('Choose a funder to look at their publications in more detail', list_of_funders)

# funders_exploded is still DOI-level
chosen_funder_DOIlevel = funders_exploded[funders_exploded['ParentAgency']==chosen_funder]
chosen_funder_DOIlevel[['DOI', 'Source title', 'Publisher', 'PubYear', 'Title', 'ISSN', 'Open Access', 'Authors', 'Authors (Raw Affiliation)', 'Corresponding Authors', 'Authors Affiliations', 'Research Organizations - standardized', 'Funder', 'ParentAgency']]

chosenfunder_byjournaltitle = chosen_funder_DOIlevel.groupby(['Source title', 'PubYear', 'Publisher']).count().reset_index()[['Source title', 'PubYear', 'Publisher', 'DOI']]
chosenfunder_byjournaltitle.sort_values(by=['DOI', 'PubYear'], ascending=False, inplace=True)
chosenfunder_byjournaltitle.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_chosenfunder_groupbyjournaltitle.csv', index=False)

fig12 = px.histogram(chosenfunder_byjournaltitle, x='Source title', y='DOI', color='PubYear', text_auto='True',
                     title=f'Top Journal Titles with Corresponding Author from {institution_name}<br>and Funding from {chosen_funder}',
                     category_orders={'PubYear': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]})
fig12.update_xaxes(categoryorder='total descending', maxallowed=maxallowed)
fig12.update_layout(height=1000, showlegend=True, legend_traceorder='reversed')
st.plotly_chart(fig12)
