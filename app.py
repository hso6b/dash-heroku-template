import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')


markdown_text = '''
The [General Social Survey (GSS)](http://www.gss.norc.org/) is a sociological survey that contains a standard core of demographic records, experiences, and attitudes, 
plus topics of special interest since 1972 by the National Opinion Research Center at the University of Chicago. It is one of the most important data sources for the social Sciences.

There is a consistent finding that there is a gender wage gap in the United States. Not even in the States, all over the world men tend to earn more than women.
However, there's also a finding that in most countries the gender pay gap has decreased in the last couple of decades.  

So we will use the GSS data to investigate and discuss this.
'''

gss_display = gss_clean.groupby('sex', sort=False).agg({'income':'mean',
                                                        'job_prestige':'mean',
                                                        'socioeconomic_index':'mean',
                                                        'education':'mean'})
gss_display = gss_display.rename({'income':'Avg. income ',
                                  'job_prestige':'Avg. job_prestige',
                                  'socioeconomic_index':'Avg. socioeconomic_index',
                                  'education':'Avg. education'}, axis=1)
gss_display = round(gss_display,2)
gss_display = gss_display.reset_index().rename({'sex':'Gender'}, axis=1)


table = ff.create_table(gss_display)
table.update_layout(width=1000, height=200)

gss_plot = gss_clean.groupby(['sex', 'male_breadwinner']).size()
gss_plot = gss_plot.reset_index()
gss_plot = gss_plot.rename({0:'count'}, axis=1)


fig_bar = px.bar(gss_plot, x='male_breadwinner', y='count', color='sex',
             labels={'male_breadwinner':'Level of agreement to male_breadwinner', 'count':'Number of people'},       
             text='count',
             barmode = 'group')
fig_bar.update_layout(showlegend=True)
fig_bar.update_layout(width=1000, height=400)
fig_bar.update(layout=dict(title=dict(x=0.5)))


fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color='sex',
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige Score', 
                         'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig_scatter.update(layout=dict(title=dict(x=0.5)))


# income for men and women
fig_box_income = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
             labels={'income':'Annual Income', 'sex':''})
fig_box_income.update(layout=dict(title=dict(x=0.5)))
fig_box_income.update_layout(showlegend=False)
fig_box_income.update_layout(width=1000, height=400)


# job_prestige for men and women
fig_box_prestige = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                          labels={'job_prestige':'Occupational Prestige Score', 'sex':''})
fig_box_prestige.update(layout=dict(title=dict(x=0.5)))
fig_box_prestige.update_layout(showlegend=False)
fig_box_prestige.update_layout(width=1000, height=400)


gss_new = gss_clean[['income', 'sex', 'job_prestige']]

gss_new['job_prestige_group'] = pd.cut(gss_clean.job_prestige, bins=6)

gss_new = gss_new.dropna()


fig_boxes = px.box(gss_new, x='income', y='sex', color='sex', 
                   facet_col='job_prestige_group', facet_col_wrap=2,
                   labels={'income':'Annaul Income', 'sex':''},
                   color_discrete_map = {'male':'blue', 'female':'red'},
                   width=1000, height=600)
fig_boxes.update(layout=dict(title=dict(x=0.5)))
fig_boxes.update_layout(showlegend=True)



stylesheets = ['https://necolas.github.io/normalize.css/8.0.1/normalize.css']
app = dash.Dash(__name__, external_stylesheets=stylesheets)

colors = {
    'background': 'grey'
}


app.layout = html.Div(
    [
        html.H1("Exploring the GSS Data to Discuss Gender Wage Gap"),
        
        dcc.Markdown(children=markdown_text),
        
        html.H2("Comparing Men and Women for the mean income, occupational prestige, socioeconomic index, and years of education"),
        
        dcc.Graph(figure=table),
        
        html.H2("The number of men and women who respond with each level of agreement to 'male_breadwinner'"),
        
        dcc.Graph(figure=fig_bar),
        
        html.H2("Income vs. Prestige by Gender"),
        
        dcc.Graph(figure=fig_scatter),
        
        html.Div([
            
            html.H3("Distribution of Income for Men and Women"),
            
            dcc.Graph(figure=fig_box_income)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H3("Distribution of Prestige for Men and Women"),
            
            dcc.Graph(figure=fig_box_prestige)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2("Distribution of Income for Men and Women for each category of Occupational Prestige"),
        
        dcc.Graph(figure=fig_boxes),
        
        html.H2("Creating Barplot"),
        
        html.Div([
            
            html.H3("x-axis feature"),
            
            dcc.Dropdown(id='x-axis', 
                         options=[{'label': i, 'value': i} for i in ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']],
                         value='satjob'),
            
            html.H3("groupby feature"),
            
            dcc.Dropdown(id='groupby',
                         options=[{'label': i, 'value': i} for i in ['sex', 'region', 'education']],
                         value='sex'),
    
        
        ], style={'width': '25%', 'float': 'left'}),
        
        html.Div([
             
            dcc.Graph(id="graph")
        
        ], style={'width': '70%', 'float': 'right'})
        
    ], style={'backgroundColor': colors['background']}
)


@app.callback(Output(component_id="graph",component_property="figure"), 
                  [Input(component_id='x-axis',component_property="value"),
                   Input(component_id='groupby',component_property="value")])

def make_figure(x, y):
    df = gss_clean.groupby([x, y]).size()
    df = df.reset_index().rename({0:'count'}, axis=1)
    return px.bar(
        df,
        x=x,
        y='count',
        color=y,
        barmode='group'
)


if __name__ == '__main__':
    app.run_server(debug=True, port=8051, host='0.0.0.0')
