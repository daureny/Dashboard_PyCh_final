from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import gunicorn


# Path to data in excel files
git_path = 'https://github.com/daureny/Dashboard_PyCh_final/raw/master/Data'

# importing FI (financial indicator sheet) - ALL sheets and adding column Дата according to sheet name in xls file
workbook = pd.ExcelFile(f'{git_path}/FI2.xlsx')
sheets = workbook.sheet_names
df_FI = pd.concat([pd.read_excel(workbook, sheet_name=s)
                  .assign(Дата=s) for s in sheets])

df_FI['Наименование банка'] = df_FI['Наименование банка'].astype('category')
df_FI = df_FI.set_index('Наименование банка')
df_FI = df_FI.iloc[:, :19]
df_FI = df_FI.drop(columns='№')
df_FI = df_FI.fillna(0)

# importing and transposing loan portfolio sheet
df_LP_raw = pd.read_excel(io=f'{git_path}/LP.xlsx', engine='openpyxl')
df_LP = df_LP_raw.transpose()

df_LP.columns = df_LP.iloc[0]
df_LP = df_LP.drop('Наименование показателя')
df_LP.index.name = 'Дата'
df_LP.columns.name = ''
df_LP.index = pd.to_datetime(df_LP.index, format='%Y-%m-%d', errors='coerce')
# df_LP.index = df_LP.index.date  # making sure the format includes only year, month, day - check later does not solve the issue
df_LP = df_LP.sort_index(ascending=True)

# importing and transposing interest margin sheet - df_IM
workbook = pd.ExcelFile(f'{git_path}/IM.xlsx')
sheets = workbook.sheet_names
df_IM = pd.concat([pd.read_excel(workbook, sheet_name=s)
                  .assign(Дата=s) for s in sheets])

df_IM = df_IM.iloc[:, :11]
df_IM = df_IM.drop(columns='N            п/п')
df_IM = df_IM.drop(0)
df_IM['Наименование банка'] = df_IM['Наименование банка'].astype('category')
df_IM = df_IM.set_index('Наименование банка')
df_IM = df_IM.drop('2')

df_IM['Процентная маржа'] = df_IM['Процентная маржа'] * 100
df_IM = df_IM.rename(columns={"Активы, приносящие доход (нетто)1": "Активы, приносящие доход (нетто)",
                              "Активы, приносящие доход (брутто)1": "Активы, приносящие доход (брутто)",
                              'Обязательства, связанные с выплатой вознаграждения1': 'Обязательства, связанные с выплатой вознаграждения',
                              'Доходы, связанные с получением вознаграждения2': 'Доходы, связанные с получением вознаграждения',
                              'Расходы, связанные с выплатой вознаграждения2': 'Расходы, связанные с выплатой вознаграждения'})

# importing and transposing interest margin sheet - df_PN - пруденциальные коэф-ты
workbook = pd.ExcelFile(f'{git_path}/PN.xlsx')
sheets = workbook.sheet_names

# create a column and assign it sheet names
df_PN = pd.concat([pd.read_excel(workbook, sheet_name=s)
                  .assign(Дата=s) for s in sheets])
# trim and clean up
df_PN = df_PN.iloc[:, :31]
df_PN = df_PN.drop(columns='№ п/п')
df_PN = df_PN.drop(columns='Собственный капитал ')
df_PN = df_PN.set_index('Наименование банков второго уровня')

# thresholds for ratios are in this dataframe
df_PNT = pd.read_excel(io=f'{git_path}/PN_threshold.xlsx',
                            engine='openpyxl')
# print(df_PNT)

df_PNT = df_PNT.set_index(df_PNT['Unnamed: 0'])
# print(df_PNT)

df_PNT.drop(df_PNT.columns[[0, 2, 3]], axis=1, inplace=True)
# print(df_PNT)

df_PNT = df_PNT.rename(columns={'Unnamed: 1': 'T'})
# print(df_PNT)

# Now selecting coefs with floor threshold (the selected ratio will not be less than the floor)
df_floor_threshold = pd.concat([
    df_PNT.iloc[0:3],     # Rows from index 0 to 2
    df_PNT.iloc[8:18],    # Rows from index 8 to 17
    df_PNT.iloc[19:22]    # Rows from index 19 to 21
])

options = [name for name in df_PN.columns]
coefs = options[:-1]


# creating Dashboard

app = Dash(__name__, external_stylesheets=[dbc.themes.YETI],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=1.0'}]
           )
server = app.server

app.layout = dbc.Container([

    # next diagrams are to df_FI dataframe
    dbc.Row(html.Br()),
    dbc.Row(html.Br()),
    dbc.Row(dbc.Col(html.H2('Основные показатели банков', style={'fontWeight': 'bold'}),
                    width={'size': 6, 'offset': 4},
                    ),
            ),
    dbc.Row(html.Br()),
    dbc.Row(html.P('На данном интерактивном дешборде вы можете просмотреть статистику по банкам. Кликайте на график для того, чтобы '
                   'отфильтровать те или иные банки. Источником данных является сайт Национального Банка РК (www.nationalbank.kz)')),

    # Первый график - Динамика показателей банков
    dbc.Row(
        dbc.Col(dcc.Graph(id='graph-1'),
                width={'size': '10', 'offset': 1})
    ),

    dbc.Row(dbc.Col(dcc.Dropdown(id='line-y',
                                 options=['Активы', 'Ссудный портфель', 'Просрочка свыше 90 дней',
                                          'Провизии по МСФО', 'Обязательства',
                                          'Собственный капитал по балансу',
                                          'Превышение текущих доходов (расходов) над текущими '
                                          'расходами (доходами) после уплаты подоходного налога'],
                                 value='Активы', clearable=False),
                    width={'size': '8', 'offset': 2, 'order': 1}  # need to align
                    ),
            ),

    # График №2 - качество активов - просрочки
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="graph-2"),
                    width={'size': '6', 'offset': 0, 'order': 1}
                    ),
    # График №3 - качество активов - просрочки
            dbc.Col(dcc.Graph(id="graph-3"),
                    width={'size': '6', 'offset': 0, 'order': 2}
                    ),

        ],
    ),

    # Селектор банков для Графиков 2 и 3 - качество активов провизии
    dbc.Row(
        [
            dbc.Col(dcc.Dropdown(id='bank_name',
                                 options=df_FI.index.unique(),
                                 value='АО "Народный Банк Казахстана"', clearable=False),
                    width={'size': '6', 'offset': 2, 'order': 1}
                    ),

    # Селектор дат для Графиков 2 и 3
            dbc.Col(dcc.Dropdown(id='date',
                                 options=list(df_FI['Дата'].unique()),
                                 value=df_FI['Дата'].min(), clearable=False),
                    width={'size': '2', 'offset': 0, 'order': 2}
                    ),

        ]
    ),

    dbc.Row(

    # График №4 - Ссудный портфель всех банков в разрезе видов займов
        [
            dbc.Col(dcc.Graph(id="graph-4"),
                        width={'size': '6', 'offset': 0, 'order': 1}),

    # График №5

            dbc.Col(dcc.Graph(id="graph-5"),
                        width={'size': '6', 'offset': 0, 'order': 2}),
        ]
    ),

dbc.Row(
        # Селектор дат для Графиков 4 и 5
        [
            dbc.Col(dcc.Dropdown(id='date_start',
                                 options=df_LP.index.unique(),
                                 value=df_LP.index.min(), clearable=False),
                    width={'size': '4', 'offset': 2, 'order': 1}
                    ),


            dbc.Col(dcc.Dropdown(id='date_end',
                                 options=df_LP.index.unique(),
                                 value=df_LP.index.max(), clearable=False),
                    width={'size': '4', 'offset': 0, 'order': 2}
                    ),

        ]
    ),

    # График №6
    dbc.Row(
        dbc.Col(dcc.Graph(id='graph-6'),
                width={'size': '12', 'offset': 0})
    ),

    # Селектор для Графика №6
    dbc.Row(dbc.Col(dcc.Dropdown(id='dd_graph-6',
                                 options=[name for name in df_IM.columns],
                                 value='Процентная маржа', clearable=False),
                    width={'size': '10', 'offset': 1, 'order': 1}  # need to align
                    ),
            ),

    # График №7
    dbc.Row(
        dbc.Col(dcc.Graph(id='graph-7'),
                width={'size': '12', 'offset': 0})
    ),
    # Селектор для Графика №7
    dbc.Row(dbc.Col(dcc.Dropdown(id='dd_graph-7',
                                 options=coefs,
                                 value='Коэф.достаточности основного капитала (k1)', clearable=False),
                    width={'size': '10', 'offset': 1, 'order': 1}  # need to align
                    ),
            ),
    dbc.Row(html.Br()),
    dbc.Row(html.P('ПРЕДУПРЕЖДЕНИЕ: полнота, достоверность и точность данных, представленных данным дешбордом зависит от соответствующих данных, '
                   'опубликованных на сайте Национального Банка РК (www.nationalbank.kz). ТОО "Стандарт бизнес консалтинг" не несет ответственности '
                   'за полноту, точность и достоверность представленных данных')),
    dbc.Row(html.P('ТОО "Стандарт бизнес консалтинг", 2023. Все права защищены.')),
    dbc.Row(html.Br())
])

# call back to graph-1
@app.callback(
    Output("graph-1", "figure"),
    Input("line-y", "value"))
def generate_chart(selected_item):
    # create traces
    data = []

    for bank in df_FI.index.unique():
        trace = go.Scatter(
            x=df_FI[df_FI.index == bank]['Дата'],
            y=df_FI[df_FI.index == bank][selected_item],
            mode='markers+lines',
            name=bank,
            line=dict(width=4)
        )

        data.append(trace)

    layout = go.Layout(
        # title='Динамика показателей банков (активы, ссудный портфель, чистый доход)')
        title={
            'text': '1. Динамика показателей банков по статьям финансовой отчетности',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
            },
    )
    fig = go.Figure(data=data, layout=layout)

    return fig


# call-back to graph-2
@app.callback(
    Output("graph-2", "figure"),
    Input("bank_name", "value"),
    Input("date", "value"))
def generate_chart(bank_name, date):
    labels = ['Ссудный портфель', 'Просрочка свыше 7 дней', 'Просрочка свыше 90 дней']
    values = []

    for label in labels:
        try:
            values.append(int(df_FI[(df_FI.index == bank_name) & (df_FI['Дата'] == date)][label].iloc[0]))
        except:
            print('Нет такой даты')


    data = go.Pie(labels=labels, values=values)

    t2 = '2. Качество активов - просрочки'
    layout = go.Layout(

        title={
            'text': t2,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
            }
    )
    fig = go.Figure(data=data, layout=layout)

    return fig


# call back to graph-3
@app.callback(
    Output("graph-3", "figure"),
    Input("bank_name", "value"),
    Input("date", "value"))
def generate_chart(bank_name, date):
    labels = ['Ссудный портфель', 'Провизии по МСФО']
    values = []

    for label in labels:
        try:
            values.append(int(df_FI[(df_FI.index == bank_name) & (df_FI['Дата'] == date)][label].iloc[0]))
        except:
            print('No such date')

    data = go.Pie(labels=labels, values=values)

    t3 = '3. Качество активов - провизии'
    layout = go.Layout(
        title={
            'text': t3,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
            }
        )
    fig = go.Figure(data=data, layout=layout)

    return fig


# call back to graph-4
@app.callback(
    Output("graph-4", "figure"),
    Input("date_start", "value"),
    Input('date_end', 'value'))
def generate_chart(date_start, date_end):


    labels = ['Межбанковские займы', 'Операции «Обратное РЕПО»',
              'Займы небанковским юридическим лицам и индивидуальным предпринимателям (включая нерезидентов), '
              'за исключением субъектов малого и среднего предпринимательства – резидентов РК',
              'Займы небанковским юридическим лицам и индивидуальным предпринимателям - резидентам РК, являющимся '
              'субъектами малого и среднего предпринимательства',
              'Займы физическим лицам (включая нерезидентов), за исключением кредитов индивидуальным предпринимателям на '
              'предпринимательские цели']
    date_start = pd.to_datetime(date_start)
    date_end = pd.to_datetime(date_end)
    df_LP_sub = df_LP[labels].loc[date_start:date_end]


    # create traces using a list comprehension:
    data = [go.Bar(
        y=df_LP_sub[asset],  # reverse your x- and y-axis assignments
        x=df_LP_sub.index,
        name=asset
    ) for asset in df_LP_sub.columns]

    # create a layout, remember to set the barmode here

    t4 = '4. Ссудный портфель банков в разрезе видов'

    layout = go.Layout(
        title={
            'text': t4,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
            },
        barmode='stack',
        legend=dict(yanchor="top", y=-0.2, xanchor="left", x=0),
        height = 600,
        width = 800
    )

    fig = go.Figure(data=data, layout=layout)

    return fig


# call back to graph-5
@app.callback(
    Output("graph-5", "figure"),
    Input("date_start", "value"),
    Input('date_end', 'value'))
def generate_chart(date_start, date_end):

    labels = ['Займы, по которым отсутствует просроченная задолженность по основному долгу и/или начисленному '
              'вознаграждению ', 'Займы с просроченной задолженностью от 1 до 30 дней', 'Займы с просроченной '
                                                                                        'задолженностью от 31 до 60 '
                                                                                        'дней', 'Займы с просроченной '
                                                                                                'задолженностью от 61 '
                                                                                                'до 90 дней',
              'Займы с просроченной задолженностью свыше 90 дней', 'Провизии по МСФО', 'Провизии по займам с '
                                                                                       'просроченной задолженностью свыше 90 дней']
    date_start = pd.to_datetime(date_start)
    date_end = pd.to_datetime(date_end)
    df_LP_sub = df_LP[labels].loc[date_start:date_end]


    # create traces using a list comprehension:
    # create a layout, remember to set the barmode here
    data = [go.Bar(
        y=df_LP_sub[asset],  # reverse your x- and y-axis assignments
        # x=df_LP.loc[(df_LP['Дата'] >= start_date) & (df_LP['Дата'] <= end_date), 'Дата'],
        x=df_LP_sub.index,
        name=asset
    ) for asset in df_LP_sub.columns]

    t5 = '5. Провизии по ссудному портфелю банков'
    layout = go.Layout(
        title={
            'text': t5,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
            },
        barmode='stack',
        legend=dict(yanchor="top", y=-0.2, xanchor="left", x=0),
        height=600,
        width=800
    )

    fig = go.Figure(data=data, layout=layout)

    return fig


# call-back to graph-6
@app.callback(
    Output("graph-6", "figure"),
    Input("dd_graph-6", "value"))
def generate_chart(selected_item):
    # create traces
    data = []

    for bank in df_IM.index.unique():
        trace = go.Scatter(
            x=df_IM[df_IM.index == bank]['Дата'],
            y=df_IM[df_IM.index == bank][selected_item],
            mode='markers+lines',
            name=bank,
            line=dict(width=4)
        )

        data.append(trace)

    t6 = '6. Динамика процентных доходов/расходов и маржи'
    layout = go.Layout(
        title={
            'text': t6,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
        },
        )

    fig = go.Figure(data=data, layout=layout)

    return fig


# call back to graph 7

# in case we need heatmap
# fig = go.Figure(data=go.Heatmap(df_to_plotly(df_PN)))

@app.callback(
    Output("graph-7", "figure"),
    Input("dd_graph-7", "value"))
def generate_chart(selected_item):
    # create traces
    data = []

    for bank in df_PN.index.unique():
        trace = go.Scatter(
            x=df_PN[df_PN.index == bank]['Дата'],
            y=df_PN[df_PN.index == bank][selected_item],
            mode='markers+lines',
            name=bank,
            line=dict(width=4)
        )

        data.append(trace)

    t7 = '7. Динамика пруденциальных нормативов и их соблюдение'
    layout = go.Layout(
        title={
            'text': t7,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'black', 'family': "Arial Black, sans-serif"}  # Example of a bolder font
        }
        )

    fig = go.Figure(data=data, layout=layout)


    try:

        threshold_value = df_PNT.loc[selected_item, 'T']  # Adjust based on actual DataFrame structure

        if selected_item in df_floor_threshold.index:
            fig.add_hrect(y0=0, y1=threshold_value, line_width=0, fillcolor="red", opacity=0.3)
        else:
            fig.add_hrect(y0=threshold_value, y1=threshold_value * 2, line_width=0, fillcolor="red", opacity=0.3)
    except KeyError:
        print(f"No such key '{selected_item}' in df_PNT")



    return fig


if __name__ == "__main__":
    app.run_server(debug=False)
