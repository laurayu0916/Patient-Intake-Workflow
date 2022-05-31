# data manipulation
import pandas as pd

# plotly 
import plotly.express as px

# dashboards
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import date
import base64

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

image_filename = 'keck-logo.png' 
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


retained = pd.read_excel("output.xlsx", sheet_name = 'retained', index_col=0)

steps = retained.step.unique()
owners = retained['owner of the step'].unique()

res_mean = retained.groupby(['step', 'owner of the step']).day_length.mean().sort_values(ascending=False)
lst_mean = list(res_mean.index)
res_df_mean = pd.DataFrame(lst_mean, columns=['step', 'owner of the step'])
res_df_mean.loc[:, 'mean'] = res_mean.values.round(3)

res_std = retained.groupby(['step', 'owner of the step']).day_length.std().sort_values(ascending=False)
# res_std = res_std.dropna()
lst_std = list(res_std.index)
res_df_std = pd.DataFrame(lst_std, columns=['step', 'owner of the step'])
res_df_std.loc[:, 'std'] = res_std.values.round(3)

combinations = {}
for i in range(len(lst_mean)):
    if lst_mean[i][0] not in combinations:
        combinations[lst_mean[i][0]] = [lst_mean[i][1]]
    else:
        combinations[lst_mean[i][0]].append(lst_mean[i][1])

corr_retained = pd.read_excel("output.xlsx", sheet_name = 'retained', index_col=0)
corr_retained['converted'] = corr_retained['converted'].map(lambda x: 0 if (x == 'No') else (1 if (x == 'Unknown') else 2))

df_corr = pd.DataFrame(columns=['step', 'owner of the step', 'correlation with conversion'])

for step in corr_retained.step.unique():
    for corr in combinations[step]:
        df = corr_retained[(retained['step'] == step)&(corr_retained['owner of the step'] == corr)]
        res = round(df[['day_length', 'converted']].corr().iloc[0, 1], 3)
        df_corr.loc[len(df_corr.index)] = [step, corr, res] 
        
df_corr = df_corr.sort_values(by='correlation with conversion', key=abs, ascending = False)

sizes = retained.groupby(['step', 'owner of the step']).size()
lst_size = list(sizes.index)
df_sizes = pd.DataFrame(lst_size, columns=['step', 'owner of the step'])
df_sizes.loc[:, 'size'] = sizes.values

all_df = res_df_mean.merge(res_df_std, on=['step', 'owner of the step']).\
                     merge(df_corr, on=['step', 'owner of the step']).\
                     merge(df_sizes, on=['step', 'owner of the step'])

app.layout = dbc.Col(
    style={'backgroundColor': "#F9F9F9"},
    children=[
        html.Div([
            html.Div(children=[
                html.H1('Proess Improvement Project', style={'text-align': 'center', 'fontSize': '40px'}), 
                html.H2('International Health Department', style={'text-align': 'center', 'fontSize': '20px'})
            ]),
            html.Div(children=[
                html.Img(
                    src='data:image/png;base64,{}'.format(encoded_image.decode()),
                    style={'height':'25%', 'width':'25%', 'padding-left': '100px', 'display': 'inline-block'}
                ),
                html.A(
                        html.Button(
                            "Learn More",
                            id="learnMore"

                        ),
                        href="https://www.keckmedicine.org/international-health/",
                        style={'padding-left': '750px', 'display': 'inline-block'}
                    ), 

            ]),

            dbc.Tabs(
                style={'padding-top': '30px', 'padding-left': '100px'}, 
                children=[   #create tab structure of tabs 
                dbc.Tab(
                    style={'padding-left': '100px'},
                    children=[
                        html.Div(
                            style={'padding-top': '40px', 'width': '80vh', 'height': '20vh'},
                            children=[
                                dcc.Dropdown(
                                                    id='sort_dropdown',
                                                    options=[{'label': 'mean', 'value': 'mean'},
                                                             {'label': 'standard deviation', 'value': 'std'},
                                                             {'label': 'correlation', 'value': 'correlation with conversion'},],
                                                    placeholder='Sort by ...',
                                                ),

                        ]),

                        html.Div(
                            id='all_table',
                            style={"width": "1000px"},
                            # children=[
                            #     dbc.Table.from_dataframe(all_df, striped=True, bordered=True, hover=True)
                            # ]
                        ),

                    ], label='Table'),
    
            ]), 
         

            html.Div(
                style={'padding-top': '30px'},
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id='step_dropdown',
                                    options=[{'label': i, 'value': i} for i in steps],
                                    placeholder='Select a step...',
                                ),
                                 width=5,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='correlation_dropdown',
                                    # options=[{'label': i, 'value': i} for i in correlations],
                                    placeholder='Select a correlation...',
                                ),
                                 width=5,
                            ),
                        ],
                        justify="around",
                    ),
                    dcc.Graph(id="histogram",
                              style={'padding-left': '100px','padding-top': '50px', 'width': '180vh', 'height': '90vh'},
                              figure={
                                "layout": {
                                    "height": 500,  # px
                                },
                            },
                    ),
                    html.Div(
                        style={'padding-top': '20px'},
                        children=[
                        html.H2('Summary Statistics', style={'padding-left': '100px', 'padding-top': '20px', 'fontSize': '30px'}),
                        html.Div(id='result_mean', style={'padding-left': '100px', 'fontSize': '20px'}),
                        html.Div(id='result_std', style={'padding-left': '100px', 'fontSize': '20px'}),
                        html.Div(id='result_corr', style={'padding-left': '100px', 'fontSize': '20px'}),
                    ]),
                    dcc.Graph(id="lineplot",
                              style={'padding-left': '100px','padding-top': '50px', 'width': '180vh', 'height': '90vh'},
                              figure={
                                "layout": {
                                    "height": 500,  # px
                                },
                            },
                    ),
                    html.Br(),
                ],
            ), 
        ]),

    ], lg =12, md = 6
)


@app.callback(
    Output("all_table", "children"), 
    Input("sort_dropdown", "value"))

def sorting(sort_key):
    if not sort_key:
        return dbc.Table.from_dataframe(all_df, striped=True, bordered=True, hover=True)
    df = all_df.sort_values(sort_key, key=abs, ascending = False)
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

@app.callback(
    Output("histogram", "figure"), 
    Input("step_dropdown", "value"), 
    Input("correlation_dropdown", "value"))

def draw_hist(step_name, corr):
    df = retained[(retained['step'] == step_name)&(retained['owner of the step'] == corr)]
    fig = px.histogram(df, x="day_length", nbins=50)
    fig.update_layout(
        title = step_name,
    )
    return fig

@app.callback(
    Output("result_mean", "children"), 
    Input("step_dropdown", "value"), 
    Input("correlation_dropdown", "value"))

def cal_mean(step_name, corr):
    df = retained[(retained['step'] == step_name)&(retained['owner of the step'] == corr)]
    df_mean = round(df.day_length.mean(),3)
    return "The mean is: {}".format(df_mean)

@app.callback(
    Output("result_std", "children"), 
    Input("step_dropdown", "value"), 
    Input("correlation_dropdown", "value"))

def cal_std(step_name, corr):
    df = retained[(retained['step'] == step_name)&(retained['owner of the step'] == corr)]
    df_std = round(df.day_length.std(),3)
    return "The standard deviation is: {}".format(df_std)

@app.callback(
    Output("result_corr", "children"), 
    Input("step_dropdown", "value"), 
    Input("correlation_dropdown", "value"))

def cal_corr(step_name, corr):
    df = corr_retained[(retained['step'] == step_name)&(corr_retained['owner of the step'] == corr)]
    df_corr = round(df[['day_length', 'converted']].corr().iloc[0, 1], 3)
    return "The correlation with conversion is: {}".format(df_corr)

@app.callback(
    Output('correlation_dropdown', 'options'),
    Input('step_dropdown', 'value')
)

def update_dropdown(step_name):
    if not step_name:
        return [{'label': i, 'value': i} for i in owners]
    else:
        return [{'label': i, 'value': i} for i in combinations[step_name]]

@app.callback(
    Output("lineplot", "figure"), 
    Input("step_dropdown", "value"), 
    Input("correlation_dropdown", "value"))

def draw_line(step_name, corr):
    if not step_name or not corr:
        return px.line()
    else:
        df = retained[(retained['step'] == step_name)&(retained['owner of the step'] == corr)]
        df_max = df.groupby(df.index).day_length.max()
        df_max = df_max.to_frame()
        df_max = df_max.merge(retained[['converted']], left_index=True, right_index=True, how='left')
        df_temp = df_max.replace('Unknown', 'No')
        fig = px.line(df_temp, x=df_temp.index, y="day_length", color = 'converted')
        newnames = {'No':'No or Unknown', 'Yes': 'Yes', 'Missing': 'Missing'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                        legendgroup = newnames[t.name],
                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                            ))
        fig.update_layout(
            title = step_name,
        )
        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
