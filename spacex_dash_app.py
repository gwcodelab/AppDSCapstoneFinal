# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                  dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                ],
                                                value='ALL',
                                                placeholder="place holder here",
                                                searchable=True
                                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.P("Launch Site Success / Failue:"),
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                
                                
                                dcc.RangeSlider(
                                                id='payload-slider',
                                                min=spacex_df['Payload Mass (kg)'].min(),
                                                max=spacex_df['Payload Mass (kg)'].max(),
                                                step=100,
                                                marks={i: str(i) for i in range(0, int(spacex_df['Payload Mass (kg)'].max())+1, 1000)},
                                                value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                                            ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    #filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df['class']==1]
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='All sites')
        return fig
        #return dcc.Graph(figure=fig)
    else:
        # return the outcomes piechart for a selected site
        #filtered_df2 = spacex_df[spacex_df['Launch Site']==entered_site].groupby('class').count().reset_index()
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        fail_count = filtered_df[filtered_df['class'] == 0].shape[0]
        data = {'Success': success_count, 'Fail': fail_count}

        # Count the occurrences of success and failure
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
    
        # Map class values to labels
        success_fail_counts['class'] = success_fail_counts['class'].map({1: 'Success', 0: 'Fail'})

        # Plotting the pie chart with Plotly Express
        fig = px.pie(success_fail_counts, names='class', values='count', 
        #fig = px.pie(filtered_df2, values='class', 
        #fig = px.pie(data.values(), labels=data.keys(),
        #names='Launch Site', 
        title=f'Pie chart for {entered_site} is selected')
        return fig
    

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),              
              Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id="payload-slider", component_property="value"))

def get_scatter_chart(entered_site, entered_p):
    #filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= entered_p[0]) &
        (spacex_df['Payload Mass (kg)'] <= entered_p[1])
    ]
    if entered_site == 'ALL':
        # If all sites are selected, show data for all sites
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category', 
            title='Correlation between Payload and Success for All Sites'
        )
    else:
        # If a specific site is selected, filter data for that site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category', 
            title=f'Correlation between Payload and Success for {entered_site}'
        )
    return fig
# Run the app
if __name__ == '__main__':
    app.run_server(port=9090)
