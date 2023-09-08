# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

sucess_count_df = spacex_df.groupby(['Launch Site']).sum()['class'].reset_index()
sucess_count_df.rename(columns={'class': 'Successes Count'}, inplace=True)
sucess_count_df.sort_values(by=['Successes Count'], inplace=True, ascending=False)

sites_drop_options = [{'label': 'All Sites', 'value': 'ALL'}]
sites_drop_options.extend(
    [{'label': site, 'value': site} for site in sucess_count_df['Launch Site']]
)


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=sites_drop_options,
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                       2500: '2500',
                                                       5000: '5000',
                                                       7500: '7500',
                                                       },
                                                value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df,
                     values='class',
                     names='Launch Site',
                     title='Total Success Launches by Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        count_class = df['class'].value_counts().reset_index()
        count_class.columns = ['class', 'count']
        fig = px.pie(count_class,
                     values='count',
                     names='class',
                     title=f'Total Success Launches for site {entered_site}')
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                       (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
    else:
        df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                       (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                       (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for site {entered_site}')
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
