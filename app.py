import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import dash_bootstrap_components as dbc
from deploy.data_processor import tesla_data

# 初始化 Dash 应用
app = dash.Dash(
    __name__,
    title="Tesla Optimus & Financial Forecast Analysis",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "Tesla Business Intelligence Dashboard"

# 获取数据
data = tesla_data.data
complete_region_data = tesla_data.get_complete_region_data()
region_growth = tesla_data.get_region_growth_rates()
business_growth = tesla_data.get_business_growth_rates()
yoy_growth = tesla_data.get_year_on_year_growth()

# 创建导航栏
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.Img(src="https://www.tesla.com/themes/custom/tesla_frontend/assets/favicons/favicon-32x32.png", 
                               height="30px")),
                dbc.Col(dbc.NavbarBrand("Tesla Business Intelligence", className="ms-2")),
            ], align="center", className="g-0"),
            href="#",
            style={"textDecoration": "none"},
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("概览", href="#overview")),
                dbc.NavItem(dbc.NavLink("地区分析", href="#regional")),
                dbc.NavItem(dbc.NavLink("业务预测", href="#business")),
                dbc.NavItem(dbc.NavLink("新增业务", href="#new-business")),
                dbc.NavItem(dbc.NavLink("数据表格", href="#tables")),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True,
        ),
    ]),
    color="dark",
    dark=True,
    sticky="top",
)

# 创建标签页内容
overview_tab = dbc.Card(
    dbc.CardBody([
        html.H4("📊 概览", className="card-title"),
        html.P("特斯拉财务预测概览分析", className="card-text"),
    ]),
    className="mt-3",
)

regional_tab = dbc.Card(
    dbc.CardBody([
        html.H4("🌍 地区分析", className="card-title"),
        html.P("各地区收入分布与增长分析", className="card-text"),
    ]),
    className="mt-3",
)

business_tab = dbc.Card(
    dbc.CardBody([
        html.H4("🏢 业务预测", className="card-title"),
        html.P("各业务线收入预测分析", className="card-text"),
    ]),
    className="mt-3",
)

# 创建标签页
tabs = dbc.Tabs([
    dbc.Tab(overview_tab, label="概览", tab_id="tab-overview"),
    dbc.Tab(regional_tab, label="地区分析", tab_id="tab-regional"),
    dbc.Tab(business_tab, label="业务预测", tab_id="tab-business"),
    dbc.Tab(dbc.Card(dbc.CardBody("新增业务分析")), label="新增业务", tab_id="tab-new"),
    dbc.Tab(dbc.Card(dbc.CardBody("数据表格")), label="数据表格", tab_id="tab-tables"),
], id="tabs", active_tab="tab-overview")

# 关键指标卡片
def create_metric_card(title, value, color, icon, subtitle=""):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H4(value, className="card-title mb-0", style={"color": color}),
                    html.P(title, className="card-text text-muted mb-1"),
                    html.Small(subtitle, className="text-muted")
                ]),
                html.Div(
                    html.I(className=f"fas fa-{icon} fa-2x", style={"color": color}),
                    className="align-self-center"
                )
            ], className="d-flex justify-content-between align-items-start")
        ])
    ], className="mb-3 shadow-sm")

# 应用布局
app.layout = dbc.Container([
    # 导航栏
    navbar,
    
    # 标题和描述
    dbc.Row([
        dbc.Col([
            html.H1("🚀 Tesla 业务预测与 Optimus 分析仪表板", 
                   className="text-center my-4 text-primary"),
            html.P("基于 Tesla 2022-2030 财务预测模型的数据分析与可视化",
                  className="text-center text-muted mb-5")
        ], width=12)
    ]),
    
    # 关键指标行
    dbc.Row([
        dbc.Col(create_metric_card(
            "2030年预测总收入", 
            "$2,926.79B", 
            "#E82127", 
            "chart-line",
            "CAGR: 20.0%"
        ), lg=3, md=6, sm=12),
        dbc.Col(create_metric_card(
            "汽车业务收入", 
            "$1,228.7B", 
            "#1E90FF", 
            "car",
            "占比: 42.0%"
        ), lg=3, md=6, sm=12),
        dbc.Col(create_metric_card(
            "新增业务收入", 
            "$500B", 
            "#4ECDC4", 
            "robot",
            "Optimus + Robotaxi"
        ), lg=3, md=6, sm=12),
        dbc.Col(create_metric_card(
            "能源业务 CAGR", 
            "40.2%", 
            "#FFD166", 
            "bolt",
            "2024-2030复合增长率"
        ), lg=3, md=6, sm=12)
    ], className="mb-4"),
    
    # 标签页
    tabs,
    
    # 动态内容区域
    html.Div(id="tab-content", className="mt-4"),
    
    # 交互控制面板
    dbc.Card([
        dbc.CardHeader("⚙️ 分析控制面板"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("选择分析维度:", className="form-label"),
                    dcc.Dropdown(
                        id="analysis-dimension",
                        options=[
                            {"label": "地区分析", "value": "regional"},
                            {"label": "业务分析", "value": "business"},
                            {"label": "时间趋势", "value": "trend"},
                            {"label": "增长率", "value": "growth"}
                        ],
                        value="regional",
                        className="mb-3"
                    )
                ], lg=4, md=6),
                dbc.Col([
                    html.Label("选择年份范围:", className="form-label"),
                    dcc.RangeSlider(
                        id="year-range-slider",
                        min=2022,
                        max=2030,
                        step=1,
                        marks={i: str(i) for i in range(2022, 2031, 2)},
                        value=[2022, 2030],
                        className="mb-3"
                    )
                ], lg=8, md=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("选择地区:", className="form-label"),
                    dcc.Dropdown(
                        id="region-selector",
                        options=[{"label": r, "value": r} for r in data['regional_data']['Region'].tolist()],
                        value=["美国", "中国", "欧洲"],
                        multi=True,
                        className="mb-3"
                    )
                ], lg=6, md=12),
                dbc.Col([
                    html.Label("业务类型:", className="form-label"),
                    dcc.Checklist(
                        id="business-selector",
                        options=[
                            {"label": "汽车业务", "value": "汽车业务"},
                            {"label": "能源业务", "value": "能源业务"},
                            {"label": "服务业务", "value": "服务业务"}
                        ],
                        value=["汽车业务", "能源业务", "服务业务"],
                        className="mb-3"
                    )
                ], lg=6, md=12)
            ])
        ])
    ], className="mt-4 mb-4 shadow"),
    
    # 图表区域
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 总收入预测趋势"),
                dbc.CardBody([
                    dcc.Graph(id="total-revenue-chart")
                ])
            ], className="shadow-sm mb-4")
        ], lg=8, md=12),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🌍 地区收入分布"),
                dbc.CardBody([
                    dcc.Graph(id="regional-pie-chart")
                ])
            ], className="shadow-sm mb-4")
        ], lg=4, md=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🏢 业务构成演变"),
                dbc.CardBody([
                    dcc.Graph(id="business-mix-chart")
                ])
            ], className="shadow-sm mb-4")
        ], lg=6, md=12),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🤖 新增业务增长"),
                dbc.CardBody([
                    dcc.Graph(id="new-business-chart")
                ])
            ], className="shadow-sm mb-4")
        ], lg=6, md=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 地区增长率分析"),
                dbc.CardBody([
                    dcc.Graph(id="growth-bar-chart")
                ])
            ], className="shadow-sm mb-4")
        ], lg=12, md=12)
    ]),
    
    # 数据表格
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📋 详细数据表格"),
                dbc.CardBody([
                    dcc.Tabs([
                        dcc.Tab(label="合并预测数据", children=[
                            dash_table.DataTable(
                                id="forecast-table",
                                columns=[
                                    {"name": "Year", "id": "Year"},
                                    {"name": "传统业务 (亿美元)", "id": "传统业务"},
                                    {"name": "新增业务 (亿美元)", "id": "新增业务"},
                                    {"name": "总收入 (亿美元)", "id": "总收入"},
                                    {"name": "YoY增长", "id": "YoY增长"}
                                ],
                                data=data['total_forecast'].to_dict('records'),
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'center', 'padding': '10px'},
                                style_header={
                                    'backgroundColor': '#E82127',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                ],
                                export_format='csv'
                            )
                        ]),
                        dcc.Tab(label="各地区数据", children=[
                            dash_table.DataTable(
                                id="regional-table",
                                columns=[{"name": col, "id": col} for col in data['regional_data'].columns],
                                data=data['regional_data'].to_dict('records'),
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'center', 'padding': '10px'},
                                style_header={
                                    'backgroundColor': '#1E90FF',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            )
                        ]),
                        dcc.Tab(label="业务结构数据", children=[
                            dash_table.DataTable(
                                id="structure-table",
                                columns=[{"name": col, "id": col} for col in data['business_structure_2030'].columns],
                                data=data['business_structure_2030'].to_dict('records'),
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'center', 'padding': '10px'},
                                style_header={
                                    'backgroundColor': '#4ECDC4',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            )
                        ])
                    ])
                ])
            ], className="shadow-sm mb-4")
        ], width=12)
    ]),
    
    # 页脚
    dbc.Row([
        dbc.Col([
            html.Footer([
                html.Hr(),
                html.P([
                    "📊 Tesla 业务预测分析仪表板 | ",
                    html.A("数据来源: Tesla Financial Forecast Model.xlsx", 
                          href="#", className="text-decoration-none")
                ], className="text-center text-muted mb-1"),
                html.P("最后更新: 2024年1月 | 分析周期: 2022-2030", 
                      className="text-center text-muted")
            ], className="mt-5")
        ])
    ])
], fluid=True, className="py-3")

# 回调函数
@app.callback(
    Output("total-revenue-chart", "figure"),
    [Input("year-range-slider", "value")]
)
def update_total_revenue_chart(year_range):
    df = data['total_forecast'].copy()
    years = [str(y) for y in range(year_range[0], year_range[1] + 1)]
    
    # 过滤数据
    df_filtered = df[df['Year'].isin(years)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_filtered['Year'],
        y=df_filtered['总收入'],
        mode='lines+markers',
        name='总收入',
        line=dict(color='#E82127', width=4),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Bar(
        x=df_filtered['Year'],
        y=df_filtered['新增业务'],
        name='新增业务',
        marker_color='#4ECDC4',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="总收入与新增业务预测",
        plot_bgcolor='white',
        height=400,
        xaxis_title="年份",
        yaxis_title="收入 (亿美元)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

@app.callback(
    Output("regional-pie-chart", "figure"),
    [Input("year-range-slider", "value"),
     Input("region-selector", "value")]
)
def update_regional_pie_chart(year_range, selected_regions):
    selected_year = str(year_range[1])
    
    if selected_year in ['2022', '2023', '2024']:
        df = data['regional_data']
        values_col = selected_year
    else:
        df = data['forecast_data']
        values_col = selected_year
    
    # 过滤选中的地区
    df_filtered = df[df['Region'].isin(selected_regions)]
    
    fig = px.pie(
        df_filtered,
        values=values_col,
        names='Region',
        title=f'各地区收入分布 ({selected_year})',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>收入: %{value:.2f}亿美元<br>占比: %{percent}'
    )
    
    return fig

@app.callback(
    Output("business-mix-chart", "figure"),
    [Input("business-selector", "value"),
     Input("year-range-slider", "value")]
)
def update_business_mix_chart(selected_businesses, year_range):
    df = data['traditional_business'].copy()
    
    # 过滤年份
    years = [str(y) for y in range(year_range[0], year_range[1] + 1)]
    years = [y if y != '2025' else '2025E' for y in years]  # 处理预测年份标签
    df_filtered = df[df['Year'].isin(years)]
    
    fig = go.Figure()
    
    colors = {'汽车业务': '#E82127', '能源业务': '#1E90FF', '服务业务': '#FFD166'}
    
    for business in selected_businesses:
        fig.add_trace(go.Bar(
            x=df_filtered['Year'],
            y=df_filtered[business],
            name=business,
            marker_color=colors.get(business, '#999'),
            hovertemplate=f'<b>{business}</b><br>年份: %{{x}}<br>收入: %{{y:.1f}}亿美元'
        ))
    
    fig.update_layout(
        title="传统业务收入构成",
        barmode='group',
        plot_bgcolor='white',
        height=400,
        xaxis_title="年份",
        yaxis_title="收入 (亿美元)",
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

@app.callback(
    Output("new-business-chart", "figure"),
    [Input("year-range-slider", "value")]
)
def update_new_business_chart(year_range):
    df = data['new_business'].copy()
    
    # 过滤年份
    years = [str(y) for y in range(year_range[0], year_range[1] + 1)]
    df_filtered = df[df['Year'].isin(years)]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Optimus vs Robotaxi', '新增业务增长趋势'),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}]]
    )
    
    # 左侧：柱状图
    fig.add_trace(
        go.Bar(
            name='Optimus',
            x=df_filtered['Year'],
            y=df_filtered['Optimus'],
            marker_color='#1E3A8A'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            name='Robotaxi',
            x=df_filtered['Year'],
            y=df_filtered['Robotaxi'],
            marker_color='#FF6B00'
        ),
        row=1, col=1
    )
    
    # 右侧：折线图
    fig.add_trace(
        go.Scatter(
            x=df_filtered['Year'],
            y=df_filtered['新业务总计'],
            mode='lines+markers',
            name='新增业务总计',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=8)
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', row=1, col=1)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', row=1, col=2)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', row=1, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', row=1, col=2)
    
    return fig

@app.callback(
    Output("growth-bar-chart", "figure"),
    [Input("analysis-dimension", "value")]
)
def update_growth_chart(analysis_dimension):
    if analysis_dimension == "regional":
        # 地区增长率
        fig = px.bar(
            region_growth.sort_values('CAGR_2024_2030', ascending=False),
            x='Region',
            y='CAGR_2024_2030',
            title='各地区2024-2030复合增长率 (CAGR)',
            color='CAGR_2024_2030',
            color_continuous_scale='RdYlGn',
            text='CAGR_2024_2030'
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            height=400,
            xaxis_title="地区",
            yaxis_title="CAGR (%)",
            coloraxis_showscale=False
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
    elif analysis_dimension == "business":
        # 业务增长率
        business_df = pd.DataFrame([
            {'业务类型': k, 'CAGR': v} 
            for k, v in business_growth.items()
        ])
        
        fig = px.bar(
            business_df,
            x='业务类型',
            y='CAGR',
            title='各业务2024-2030复合增长率 (CAGR)',
            color='CAGR',
            color_continuous_scale='Blues',
            text='CAGR'
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            height=400,
            xaxis_title="业务类型",
            yaxis_title="CAGR (%)",
            coloraxis_showscale=False
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
    else:
        # 默认显示地区增长率
        fig = px.bar(
            region_growth.sort_values('CAGR_2024_2030', ascending=False),
            x='Region',
            y='CAGR_2024_2030',
            title='各地区2024-2030复合增长率 (CAGR)',
            text='CAGR_2024_2030'
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            height=400
        )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "tab-overview":
        return html.Div([
            html.H4("概览分析", className="mb-3"),
            html.P("特斯拉财务预测模型的综合分析概览。"),
            dbc.Alert([
                html.H5("关键洞察", className="alert-heading"),
                html.Ul([
                    html.Li("预计2030年总收入将达到2,926.8亿美元"),
                    html.Li("新增业务（Optimus + Robotaxi）将成为重要增长动力"),
                    html.Li("能源业务增长最快，CAGR达40.2%"),
                    html.Li("亚太地区增长潜力最大，CAGR超过15%")
                ])
            ], color="info")
        ])
    elif active_tab == "tab-regional":
        return html.Div([
            html.H4("地区分析", className="mb-3"),
            html.P("各地区收入分布与增长分析。"),
            dash_table.DataTable(
                data=data['growth_assumptions'].to_dict('records'),
                columns=[{"name": i, "id": i} for i in data['growth_assumptions'].columns]
            )
        ])
    elif active_tab == "tab-business":
        return html.Div([
            html.H4("业务预测", className="mb-3"),
            html.P("各业务线收入预测分析。"),
            dbc.Row([
                dbc.Col([
                    html.H5("业务增长概览"),
                    dash_table.DataTable(
                        data=data['business_structure_2030'].to_dict('records'),
                        columns=[{"name": i, "id": i} for i in data['business_structure_2030'].columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'center', 'padding': '10px'}
                    )
                ], width=12)
            ])
        ])
    
    return html.Div()

# 运行应用
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"🚀 Tesla Business Intelligence Dashboard starting on port {port}")
    print(f"📊 Access the dashboard at: http://localhost:{port}")
    app.run_server(host='0.0.0.0', port=port, debug=False)

# 导出 server
server = app.server
