# app.py - 完整的Tesla财务预测仪表板
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# 初始化Dash应用
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
app.title = "Tesla财务预测仪表板"
server = app.server  # 为Gunicorn提供服务器实例

# ==================== 数据准备 ====================
# 1. 各地区历史收入数据
regions_data = {
    '地区': ['美国', '中国', '欧洲', '亚太', '中东', '其他'],
    '2022': [405.53, 181.45, 80, 40, 15, 92.64],
    '2023': [452.8, 251.01, 100.41, 55.78, 20.08, 87.82],
    '2024': [438, 250.24, 104.26, 62.56, 20.85, 101.15],
}

regions_df = pd.DataFrame(regions_data)

# 2. 增长率假设 - 三种情景
scenarios_data = {
    '保守': {
        '2025增长率': [0.02, 0.05, 0.08, 0.15, 0.10, 0.04],
        '2026-2030 CAGR': [0.02, 0.05, 0.08, 0.15, 0.10, 0.04],
        '颜色': '#808080'
    },
    '正常': {
        '2025增长率': [0.04, 0.07, 0.12, 0.20, 0.15, 0.064],
        '2026-2030 CAGR': [0.04, 0.07, 0.12, 0.20, 0.15, 0.064],
        '颜色': '#1f77b4'
    },
    '乐观': {
        '2025增长率': [0.06, 0.10, 0.18, 0.30, 0.20, 0.10],
        '2026-2030 CAGR': [0.06, 0.10, 0.18, 0.30, 0.20, 0.10],
        '颜色': '#2ca02c'
    }
}

# 3. 生成预测数据
def generate_forecast_data(scenario_name):
    """生成指定情景的预测数据"""
    scenario = scenarios_data[scenario_name]
    forecast_years = ['2025', '2026', '2027', '2028', '2029', '2030']
    
    forecasts = []
    for idx, region in enumerate(regions_df['地区']):
        region_data = {'地区': region}
        
        # 获取2024年基础数据
        base_value = regions_df.loc[idx, '2024']
        
        # 生成预测
        current_value = base_value
        for year in forecast_years:
            if year == '2025':
                growth_rate = scenario['2025增长率'][idx]
            else:
                growth_rate = scenario['2026-2030 CAGR'][idx]
            
            current_value = current_value * (1 + growth_rate)
            region_data[year] = round(current_value, 2)
        
        forecasts.append(region_data)
    
    return pd.DataFrame(forecasts)

# 4. 业务预测数据
years = ['2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']

business_scenarios = {
    '保守': {
        '汽车业务增长率': 0.03,
        '能源业务增长率': 0.25,
        '服务业务增长率': 0.15,
        '新业务': {
            '2026': {'Optimus': 3, 'Robotaxi': 0},
            '2027': {'Optimus': 15, 'Robotaxi': 3},
            '2028': {'Optimus': 60, 'Robotaxi': 50},
            '2029': {'Optimus': 120, 'Robotaxi': 80},
            '2030': {'Optimus': 180, 'Robotaxi': 120}
        }
    },
    '正常': {
        '汽车业务增长率': 0.04,
        '能源业务增长率': 0.40,
        '服务业务增长率': 0.26,
        '新业务': {
            '2026': {'Optimus': 3, 'Robotaxi': 0},
            '2027': {'Optimus': 20, 'Robotaxi': 5},
            '2028': {'Optimus': 90, 'Robotaxi': 80},
            '2029': {'Optimus': 200, 'Robotaxi': 130},
            '2030': {'Optimus': 300, 'Robotaxi': 200}
        }
    },
    '乐观': {
        '汽车业务增长率': 0.06,
        '能源业务增长率': 0.50,
        '服务业务增长率': 0.30,
        '新业务': {
            '2026': {'Optimus': 5, 'Robotaxi': 2},
            '2027': {'Optimus': 30, 'Robotaxi': 10},
            '2028': {'Optimus': 120, 'Robotaxi': 120},
            '2029': {'Optimus': 280, 'Robotaxi': 200},
            '2030': {'Optimus': 400, 'Robotaxi': 300}
        }
    }
}

# 历史业务数据
historical_business = {
    '汽车业务': [714.62, 824.19, 770.7],
    '能源业务': [39.09, 60.35, 100.86],
    '服务业务': [60.91, 83.19, 105.34],
    '传统业务总计': [814.62, 967.73, 976.9]
}

def generate_business_forecast(scenario_name):
    """生成业务预测数据"""
    scenario = business_scenarios[scenario_name]
    
    # 传统业务预测
    traditional = {
        '年份': years,
        '汽车业务': [],
        '能源业务': [],
        '服务业务': [],
        '传统业务总计': []
    }
    
    # 添加历史数据
    for i in range(3):
        traditional['汽车业务'].append(historical_business['汽车业务'][i])
        traditional['能源业务'].append(historical_business['能源业务'][i])
        traditional['服务业务'].append(historical_business['服务业务'][i])
        traditional['传统业务总计'].append(historical_business['传统业务总计'][i])
    
    # 预测数据
    last_auto = historical_business['汽车业务'][-1]
    last_energy = historical_business['能源业务'][-1]
    last_service = historical_business['服务业务'][-1]
    
    for i, year in enumerate(years[3:], 1):
        auto_value = last_auto * ((1 + scenario['汽车业务增长率']) ** i)
        energy_value = last_energy * ((1 + scenario['能源业务增长率']) ** i)
        service_value = last_service * ((1 + scenario['服务业务增长率']) ** i)
        
        traditional['汽车业务'].append(round(auto_value, 2))
        traditional['能源业务'].append(round(energy_value, 2))
        traditional['服务业务'].append(round(service_value, 2))
        traditional['传统业务总计'].append(round(auto_value + energy_value + service_value, 2))
    
    traditional_df = pd.DataFrame(traditional)
    
    # 新业务预测
    new_business = {
        '年份': years,
        'Optimus': [0, 0, 0] + [scenario['新业务'].get(year, {}).get('Optimus', 0) for year in years[3:]],
        'Robotaxi': [0, 0, 0] + [scenario['新业务'].get(year, {}).get('Robotaxi', 0) for year in years[3:]]
    }
    
    new_df = pd.DataFrame(new_business)
    new_df['新业务总计'] = new_df['Optimus'] + new_df['Robotaxi']
    
    return traditional_df, new_df

# 预先生成所有数据
forecast_data = {scenario: generate_forecast_data(scenario) for scenario in ['保守', '正常', '乐观']}
business_data = {scenario: generate_business_forecast(scenario) for scenario in ['保守', '正常', '乐观']}

# ==================== 应用布局 ====================
app.layout = dbc.Container([
    # 标题区域
    dbc.Row([
        dbc.Col([
            html.H1("🚗 Tesla财务预测仪表板", className="text-center my-4 text-primary"),
            html.P("基于Optimus和Robotaxi业务的2022-2030年多情景分析", 
                  className="text-center text-muted mb-4"),
            html.Hr()
        ], width=12)
    ]),
    
    # 控制面板
    dbc.Row([
        dbc.Col([
            html.Label("📊 选择预测情景:", className="fw-bold"),
            dcc.RadioItems(
                id='scenario-selector',
                options=[
                    {'label': '保守情景', 'value': '保守'},
                    {'label': '正常情景', 'value': '正常'},
                    {'label': '乐观情景', 'value': '乐观'}
                ],
                value='正常',
                inline=True,
                className="mb-4",
                labelStyle={'margin-right': '20px', 'font-weight': 'normal'}
            )
        ], width=6),
        
        dbc.Col([
            html.Label("📅 选择分析年份:", className="fw-bold"),
            dcc.Dropdown(
                id='year-selector',
                options=[{'label': year, 'value': year} for year in years],
                value='2030',
                clearable=False,
                className="mb-4"
            )
        ], width=3),
        
        dbc.Col([
            html.Label("🌍 选择地区:", className="fw-bold"),
            dcc.Dropdown(
                id='region-selector',
                options=[{'label': region, 'value': region} for region in regions_df['地区']],
                value='美国',
                clearable=False,
                className="mb-4"
            )
        ], width=3)
    ], className="mb-4 p-3 bg-light rounded"),
    
    # 图表区域 - 选项卡
    dbc.Tabs([
        # 选项卡1: 总体概览
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='total-revenue-chart', config={'displayModeBar': True}),
                ], width=12, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='business-composition-chart'),
                ], width=6, className="mb-4"),
                
                dbc.Col([
                    dcc.Graph(id='region-comparison-chart'),
                ], width=6, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("📈 业务增长洞察", className="mb-3"),
                        html.Div(id='business-insights', className="p-3 bg-light rounded")
                    ])
                ], width=12)
            ])
        ], label="📊 总体概览"),
        
        # 选项卡2: 地区分析
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='region-growth-chart'),
                ], width=12, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='cagr-comparison-chart'),
                ], width=12, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("🌍 地区增长分析", className="mb-3"),
                        html.Div(id='region-insights', className="p-3 bg-light rounded")
                    ])
                ], width=12)
            ])
        ], label="🌍 地区分析"),
        
        # 选项卡3: 数据详情
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    html.H4("📋 各地区收入数据详情", className="mt-3 mb-3"),
                    html.Div(id='region-data-table', className="mb-4")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H5("📊 2030年业务结构预测", className="mb-3"),
                    html.Div(id='2030-structure-table')
                ], width=12)
            ])
        ], label="📋 数据详情"),
        
        # 选项卡4: 关于
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("关于此仪表板", className="mb-4"),
                        html.P("""
                            📊 此仪表板展示特斯拉(Tesla)2022-2030年的财务预测分析，包含三种不同情景：
                        """),
                        html.Ul([
                            html.Li("保守情景: 考虑市场竞争加剧和宏观经济挑战"),
                            html.Li("正常情景: 基于当前趋势的合理预测"),
                            html.Li("乐观情景: 假设新业务(Optimus & Robotaxi)成功商业化")
                        ]),
                        html.Hr(),
                        html.H5("数据来源", className="mt-4"),
                        html.P("""
                            • 历史数据: Tesla 2022-2024年财报
                            • 预测假设: 基于市场研究和行业分析
                            • 地区分类: 按主要市场划分
                        """),
                        html.H5("部署信息", className="mt-4"),
                        html.P(f"""
                            • 部署平台: Render.com
                            • 技术栈: Python, Dash, Plotly, Pandas
                            • 数据更新: {pd.Timestamp.now().strftime('%Y年%m月%d日')}
                        """),
                        html.H5("使用说明", className="mt-4"),
                        html.P("""
                            1. 选择不同的预测情景查看不同增长路径
                            2. 选择年份和地区进行针对性分析
                            3. 鼠标悬停图表查看详细数据
                            4. 点击图例可隐藏/显示数据系列
                        """)
                    ], className="p-4")
                ], width=8, className="offset-2")
            ])
        ], label="ℹ️ 关于")
    ]),
    
    # 页脚
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "© 2024 Tesla财务分析项目 | ",
                html.A("GitHub仓库", href="https://github.com/你的用户名/tesla-optimus-business-analysis", target="_blank"),
                " | 数据仅供参考，不构成投资建议"
            ], className="text-center text-muted small mt-4")
        ], width=12)
    ])
], fluid=True, className="px-4")

# ==================== 回调函数 ====================
@app.callback(
    Output('total-revenue-chart', 'figure'),
    [Input('scenario-selector', 'value'),
     Input('year-selector', 'value')]
)
def update_total_revenue_chart(scenario, selected_year):
    """更新总收入趋势图"""
    traditional_df, new_df = business_data[scenario]
    
    # 计算总收入
    total_revenue = []
    for i, year in enumerate(years):
        trad_value = traditional_df.loc[i, '传统业务总计']
        new_value = new_df.loc[i, '新业务总计']
        total_revenue.append(trad_value + new_value)
    
    fig = go.Figure()
    
    # 传统业务
    fig.add_trace(go.Scatter(
        x=years,
        y=traditional_df['传统业务总计'],
        mode='lines+markers',
        name='传统业务',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, symbol='circle'),
        hovertemplate='<b>传统业务</b><br>年份: %{x}<br>收入: %{y:.1f}亿美元<extra></extra>'
    ))
    
    # 新业务
    fig.add_trace(go.Scatter(
        x=years,
        y=new_df['新业务总计'],
        mode='lines+markers',
        name='新业务(Optimus+Robotaxi)',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8, symbol='diamond'),
        hovertemplate='<b>新业务</b><br>年份: %{x}<br>收入: %{y:.1f}亿美元<extra></extra>'
    ))
    
    # 总收入
    fig.add_trace(go.Scatter(
        x=years,
        y=total_revenue,
        mode='lines+markers',
        name='总收入',
        line=dict(color='#ff7f0e', width=4, dash='dash'),
        marker=dict(size=10, symbol='star'),
        hovertemplate='<b>总收入</b><br>年份: %{x}<br>收入: %{y:.1f}亿美元<extra></extra>'
    ))
    
    # 添加年份标记
    if selected_year in years:
        idx = years.index(selected_year)
        fig.add_vline(
            x=idx, 
            line_width=2, 
            line_dash="dot", 
            line_color="red",
            annotation_text=f"选中: {selected_year}"
        )
    
    fig.update_layout(
        title={
            'text': f'{scenario}情景总收入预测趋势（亿美元）',
            'font': {'size': 20}
        },
        xaxis_title='年份',
        yaxis_title='收入（亿美元）',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

@app.callback(
    Output('business-composition-chart', 'figure'),
    [Input('year-selector', 'value'),
     Input('scenario-selector', 'value')]
)
def update_business_composition_chart(selected_year, scenario):
    """更新业务构成图"""
    traditional_df, new_df = business_data[scenario]
    
    # 获取指定年份数据
    year_idx = years.index(selected_year)
    
    # 业务数据
    auto_value = traditional_df.loc[year_idx, '汽车业务']
    energy_value = traditional_df.loc[year_idx, '能源业务']
    service_value = traditional_df.loc[year_idx, '服务业务']
    optimus_value = new_df.loc[year_idx, 'Optimus']
    robotaxi_value = new_df.loc[year_idx, 'Robotaxi']
    
    # 准备饼图数据
    labels = ['汽车业务', '能源业务', '服务业务', 'Optimus', 'Robotaxi']
    values = [auto_value, energy_value, service_value, optimus_value, robotaxi_value]
    
    # 过滤掉值为0的业务
    data = [(label, value) for label, value in zip(labels, values) if value > 0]
    if data:
        filtered_labels, filtered_values = zip(*data)
    else:
        filtered_labels = ['暂无数据']
        filtered_values = [100]
    
    # 颜色
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    fig = go.Figure(data=[go.Pie(
        labels=filtered_labels,
        values=filtered_values,
        hole=0.4,
        marker=dict(colors=colors[:len(filtered_labels)]),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{value:.1f}亿<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>收入: %{value:.1f}亿美元<br>占比: %{percent}<extra></extra>',
        pull=[0.1 if label in ['Optimus', 'Robotaxi'] else 0 for label in filtered_labels]
    )])
    
    fig.update_layout(
        title={
            'text': f'{selected_year}年{scenario}情景业务构成',
            'font': {'size': 18}
        },
        template='plotly_white',
        height=450,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1
        )
    )
    
    return fig

@app.callback(
    Output('region-comparison-chart', 'figure'),
    [Input('year-selector', 'value'),
     Input('scenario-selector', 'value')]
)
def update_region_comparison_chart(selected_year, scenario):
    """更新地区对比图"""
    region_forecast = forecast_data[scenario]
    
    if selected_year in ['2022', '2023', '2024']:
        # 历史年份
        data_df = regions_df
    else:
        # 预测年份
        data_df = region_forecast
    
    # 排序并获取数据
    sorted_df = data_df.sort_values(by=selected_year, ascending=True)
    values = sorted_df[selected_year].values
    labels = sorted_df['地区'].values
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(
            color=values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="收入（亿美元）", len=0.8)
        ),
        text=[f"{val:.1f}" for val in values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>收入: %{x:.1f}亿美元<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'{selected_year}年{scenario}情景各地区收入对比',
            'font': {'size': 18}
        },
        xaxis_title='收入（亿美元）',
        yaxis_title='地区',
        template='plotly_white',
        height=500,
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    return fig

@app.callback(
    Output('region-growth-chart', 'figure'),
    [Input('region-selector', 'value'),
     Input('scenario-selector', 'value')]
)
def update_region_growth_chart(selected_region, scenario):
    """更新地区增长趋势图"""
    fig = go.Figure()
    
    # 历史数据
    hist_years = ['2022', '2023', '2024']
    hist_values = [
        regions_df[regions_df['地区'] == selected_region][year].values[0]
        for year in hist_years
    ]
    
    # 预测数据
    forecast_years = ['2025', '2026', '2027', '2028', '2029', '2030']
    region_data = forecast_data[scenario]
    forecast_values = [
        region_data[region_data['地区'] == selected_region][year].values[0]
        for year in forecast_years
    ]
    
    # 合并数据
    all_years = hist_years + forecast_years
    all_values = hist_values + forecast_values
    
    # 主趋势线
    fig.add_trace(go.Scatter(
        x=all_years,
        y=all_values,
        mode='lines+markers+text',
        name=selected_region,
        line=dict(color=scenarios_data[scenario]['颜色'], width=4),
        marker=dict(size=10, symbol='circle'),
        text=[f"{val:.1f}" for val in all_values],
        textposition='top center',
        hovertemplate='<b>%{fullData.name}</b><br>年份: %{x}<br>收入: %{y:.1f}亿美元<extra></extra>'
    ))
    
    # 添加预测区域背景
    fig.add_vrect(
        x0="2025", x1="2030",
        fillcolor="lightgray", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="预测区域", annotation_position="top left"
    )
    
    # 添加增长率标注
    for i in range(1, len(all_years)):
        growth_rate = ((all_values[i] - all_values[i-1]) / all_values[i-1] * 100)
        if abs(growth_rate) > 0.1:
            fig.add_annotation(
                x=all_years[i],
                y=all_values[i],
                text=f"↑{growth_rate:.1f}%" if growth_rate > 0 else f"↓{abs(growth_rate):.1f}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green' if growth_rate > 0 else 'red',
                ax=0,
                ay=-40 if i % 2 == 0 else -60,
                font=dict(size=10, color='black')
            )
    
    fig.update_layout(
        title={
            'text': f'{selected_region}地区{scenario}情景收入增长趋势（亿美元）',
            'font': {'size': 18}
        },
        xaxis_title='年份',
        yaxis_title='收入（亿美元）',
        template='plotly_white',
        height=500,
        showlegend=True
    )
    
    return fig

@app.callback(
    Output('cagr-comparison-chart', 'figure'),
    Input('scenario-selector', 'value')
)
def update_cagr_comparison_chart(scenario):
    """更新CAGR对比图"""
    fig = go.Figure()
    
    growth_rates = scenarios_data[scenario]['2026-2030 CAGR']
    
    fig.add_trace(go.Bar(
        x=regions_df['地区'],
        y=[rate * 100 for rate in growth_rates],
        marker_color=scenarios_data[scenario]['颜色'],
        text=[f"{rate*100:.1f}%" for rate in growth_rates],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>2026-2030 CAGR: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'{scenario}情景各地区2026-2030年复合增长率(CAGR)',
            'font': {'size': 18}
        },
        yaxis_title='CAGR (%)',
        xaxis_title='地区',
        template='plotly_white',
        height=450,
        yaxis=dict(tickformat='.1f%'),
        hovermode='x'
    )
    
    return fig

@app.callback(
    [Output('region-data-table', 'children'),
     Output('2030-structure-table', 'children'),
     Output('business-insights', 'children'),
     Output('region-insights', 'children')],
    [Input('year-selector', 'value'),
     Input('scenario-selector', 'value'),
     Input('region-selector', 'value')]
)
def update_data_tables(selected_year, scenario, selected_region):
    """更新数据表格和洞察信息"""
    # 1. 地区数据表格
    if selected_year in ['2022', '2023', '2024']:
        table_data = regions_df[['地区', '2022', '2023', '2024']].copy()
    else:
        region_forecast = forecast_data[scenario]
        table_data = regions_df[['地区', '2022', '2023', '2024']].copy()
        
        for _, region_row in region_forecast.iterrows():
            region = region_row['地区']
            value = region_row[selected_year]
            table_data.loc[table_data['地区'] == region, selected_year] = value
    
    # 计算增长率
    if selected_year != '2022':
        table_data[f'增长率'] = ((table_data[selected_year] - table_data['2022']) / table_data['2022'] * 100).round(1)
    
    # 创建表格
    cols = ['地区', '2022', '2023', '2024']
    if selected_year not in cols:
        cols.append(selected_year)
    if '增长率' in table_data.columns:
        cols.append('增长率')
    
    table_data = table_data[cols]
    
    region_table = dbc.Table(
        [
            html.Thead(
                html.Tr([html.Th(col, style={'text-align': 'center'}) for col in table_data.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(
                        f"{table_data.iloc[i][col]:.1f}%" if col == '增长率' else 
                        f"{table_data.iloc[i][col]:.1f}" if isinstance(table_data.iloc[i][col], (int, float)) else 
                        str(table_data.iloc[i][col]),
                        style={'text-align': 'center'}
                    ) for col in table_data.columns
                ]) for i in range(len(table_data))
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="mt-2"
    )
    
    # 2. 2030年业务结构表格
    traditional_df, new_df = business_data[scenario]
    year_2030_idx = years.index('2030')
    
    business_data_2030 = {
        '业务类型': ['汽车业务', '能源业务', '服务业务', 'Optimus', 'Robotaxi', '总收入'],
        '收入（亿美元）': [
            traditional_df.loc[year_2030_idx, '汽车业务'],
            traditional_df.loc[year_2030_idx, '能源业务'],
            traditional_df.loc[year_2030_idx, '服务业务'],
            new_df.loc[year_2030_idx, 'Optimus'],
            new_df.loc[year_2030_idx, 'Robotaxi'],
            traditional_df.loc[year_2030_idx, '传统业务总计'] + new_df.loc[year_2030_idx, '新业务总计']
        ]
    }
    
    business_df = pd.DataFrame(business_data_2030)
    business_df['占比'] = (business_df['收入（亿美元）'] / business_df['收入（亿美元）'].iloc[-1] * 100).round(1)
    
    structure_table = dbc.Table(
        [
            html.Thead(
                html.Tr([html.Th(col, style={'text-align': 'center'}) for col in business_df.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(
                        f"{business_df.iloc[i][col]:.1f}%" if col == '占比' else 
                        f"{business_df.iloc[i][col]:.1f}" if isinstance(business_df.iloc[i][col], (float)) else 
                        str(business_df.iloc[i][col]),
                        style={
                            'text-align': 'center',
                            'font-weight': 'bold' if business_df.iloc[i]['业务类型'] == '总收入' else 'normal'
                        }
                    ) for col in business_df.columns
                ]) for i in range(len(business_df))
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="mt-2"
    )
    
    # 3. 业务增长洞察
    if selected_year != '2022':
        growth_rate = ((table_data[table_data['地区'] == selected_region][selected_year].values[0] - 
                       table_data[table_data['地区'] == selected_region]['2022'].values[0]) / 
                      table_data[table_data['地区'] == selected_region]['2022'].values[0] * 100).round(1)
        
        if growth_rate > 20:
            insight = f"🚀 强劲增长：{selected_region}地区从2022到{selected_year}年预计增长{growth_rate}%，表现突出！"
        elif growth_rate > 10:
            insight = f"📈 稳步增长：{selected_region}地区预计增长{growth_rate}%，保持良好发展态势。"
        elif growth_rate > 0:
            insight = f"📊 温和增长：{selected_region}地区预计增长{growth_rate}%，市场趋于成熟。"
        else:
            insight = f"⚠️ 增长放缓：{selected_region}地区预计增长{growth_rate}%，需要关注市场变化。"
    else:
        insight = "请选择预测年份查看增长分析。"
    
    business_insight = html.Div([
        html.H6("业务增长洞察", className="mb-2"),
        html.P(insight, className="mb-0"),
        html.Small(f"基于{scenario}情景预测", className="text-muted")
    ])
    
    # 4. 地区增长洞察
    cagr = scenarios_data[scenario]['2026-2030 CAGR'][regions_df[regions_df['地区'] == selected_region].index[0]] * 100
    
    if cagr > 15:
        region_insight_text = f"🌱 高速增长区域：预计2026-2030年CAGR达{cagr:.1f}%，是特斯拉的重点增长市场。"
    elif cagr > 8:
        region_insight_text = f"📈 稳定增长区域：预计CAGR为{cagr:.1f}%，贡献稳定的收入增长。"
    else:
        region_insight_text = f"🏢 成熟市场区域：预计CAGR为{cagr:.1f}%，市场趋于饱和，需寻求新的增长点。"
    
    region_insight = html.Div([
        html.H6("地区增长潜力", className="mb-2"),
        html.P(region_insight_text, className="mb-0"),
        html.Small("复合年增长率(CAGR)分析", className="text-muted")
    ])
    
    return region_table, structure_table, business_insight, region_insight

# ==================== 运行应用 ====================
if __name__ == '__main__':
    # 本地运行时
    app.run(debug=False, host='0.0.0.0', port=8050)