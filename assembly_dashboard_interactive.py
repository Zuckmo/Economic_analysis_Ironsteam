import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Configure page
st.set_page_config(
    page_title="Assembly Project - Economic Analysis Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #0F1419;
            color: #F5F7FA;
        }
        
        h1, h2, h3 {
            color: #F5F7FA;
            font-weight: 700;
        }
        
        .metric-box {
            background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
            border-left: 4px solid;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .section-header {
            font-size: 20px;
            font-weight: 700;
            padding: 15px;
            border-bottom: 2px solid;
            margin: 20px 0 15px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selling_price' not in st.session_state:
    st.session_state.selling_price = 230.0
if 'manual_capex_mult' not in st.session_state:
    st.session_state.manual_capex_mult = 1.0
if 'hybrid_capex_mult' not in st.session_state:
    st.session_state.hybrid_capex_mult = 1.0
if 'auto_capex_mult' not in st.session_state:
    st.session_state.auto_capex_mult = 1.0
if 'production_volume' not in st.session_state:
    st.session_state.production_volume = 150000

# ==================== SIDEBAR - SIMULASI PARAMETER ====================
with st.sidebar:
    st.markdown("### 🎛️ SIMULATION PARAMETERS")
    st.markdown("---")
    
    # Selling Price Slider
    st.markdown("#### 💰 Selling Price per Unit (SEK)")
    selling_price = st.slider(
        "Adjust selling price",
        min_value=200.0,
        max_value=300.0,
        value=st.session_state.selling_price,
        step=1.0,
        label_visibility="collapsed"
    )
    st.session_state.selling_price = selling_price
    st.info(f"Current price: **{selling_price:.2f} SEK/unit**")
    
    st.markdown("---")
    
    # Production Volume Slider
    st.markdown("#### 📦 Annual Production Volume (units)")
    production_volume = st.slider(
        "Adjust production volume",
        min_value=50000,
        max_value=300000,
        value=int(st.session_state.production_volume),
        step=10000,
        label_visibility="collapsed"
    )
    st.session_state.production_volume = production_volume
    st.info(f"Current volume: **{production_volume:,.0f} units/year**")
    
    st.markdown("---")
    
    # CAPEX Multipliers
    st.markdown("#### 🏗️ CAPEX Cost Adjustment")
    
    st.markdown("**Manual Assembly CAPEX**")
    manual_mult = st.slider(
        "Manual CAPEX multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.manual_capex_mult,
        step=0.1,
        label_visibility="collapsed"
    )
    st.session_state.manual_capex_mult = manual_mult
    st.caption(f"Multiplier: {manual_mult:.1f}x")
    
    st.markdown("**Hybrid Assembly CAPEX**")
    hybrid_mult = st.slider(
        "Hybrid CAPEX multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.hybrid_capex_mult,
        step=0.1,
        label_visibility="collapsed"
    )
    st.session_state.hybrid_capex_mult = hybrid_mult
    st.caption(f"Multiplier: {hybrid_mult:.1f}x")
    
    st.markdown("**Full Automation CAPEX**")
    auto_mult = st.slider(
        "Automation CAPEX multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.auto_capex_mult,
        step=0.1,
        label_visibility="collapsed"
    )
    st.session_state.auto_capex_mult = auto_mult
    st.caption(f"Multiplier: {auto_mult:.1f}x")
    
    st.markdown("---")
    st.markdown("**💡 Tip:** Adjust the sliders to simulate different scenarios!")

# ==================== CALCULATE DYNAMICS DATA ====================

def calculate_scenario(scenario_type, selling_price, production_volume, capex_multiplier):
    """Calculate financial metrics based on parameters"""
    
    # Base data from PDF
    base_data = {
        'Manual': {
            'base_capex': 388100,
            'material_cost': 191.59,
            'labor_cost': 2.74,
            'overhead_cost': 4.00,
            'operators': 10,
            'payback_base': 29,
            'flexibility': 'High'
        },
        'Hybrid': {
            'base_capex': 444581,
            'material_cost': 191.59,
            'labor_cost': 9.11,
            'overhead_cost': 4.06,
            'operators': 7,
            'payback_base': 44,
            'flexibility': 'Medium'
        },
        'Full Automation': {
            'base_capex': 7658631,
            'material_cost': 191.59,
            'labor_cost': 0.52,
            'overhead_cost': 4.42,
            'operators': 2,
            'payback_base': 949,
            'flexibility': 'Low'
        }
    }
    
    data = base_data[scenario_type]
    
    # Adjust CAPEX
    adjusted_capex = data['base_capex'] * capex_multiplier
    capex_per_unit = adjusted_capex / 5 / production_volume  # 5 year depreciation
    
    # Calculate costs
    cost_per_unit = data['material_cost'] + data['labor_cost'] + data['overhead_cost'] + capex_per_unit
    profit_per_unit = selling_price - cost_per_unit
    
    # Financial calculations
    annual_revenue = selling_price * production_volume
    total_annual_cost = cost_per_unit * production_volume
    annual_profit = profit_per_unit * production_volume
    
    monthly_profit = annual_profit / 12
    daily_profit = annual_profit / 250
    
    profit_margin = (profit_per_unit / selling_price) * 100
    
    # Payback period (adjusted based on profit change)
    if profit_per_unit > 0:
        payback_days = adjusted_capex / (annual_profit / 365)
    else:
        payback_days = 999999
    
    # ROI
    if annual_profit > 0:
        roi_percent = (annual_profit / adjusted_capex) * 100
    else:
        roi_percent = 0
    
    return {
        'capex': adjusted_capex,
        'cost_per_unit': cost_per_unit,
        'selling_price': selling_price,
        'profit_per_unit': profit_per_unit,
        'annual_revenue': annual_revenue,
        'total_annual_cost': total_annual_cost,
        'annual_profit': annual_profit,
        'monthly_profit': monthly_profit,
        'daily_profit': daily_profit,
        'profit_margin': profit_margin,
        'payback_days': payback_days,
        'roi_percent': roi_percent,
        'operators': data['operators'],
        'flexibility': data['flexibility']
    }

# Calculate all scenarios
manual = calculate_scenario('Manual', selling_price, production_volume, manual_mult)
hybrid = calculate_scenario('Hybrid', selling_price, production_volume, hybrid_mult)
automation = calculate_scenario('Full Automation', selling_price, production_volume, auto_mult)

scenarios_dict = {
    'Manual': manual,
    'Hybrid': hybrid,
    'Full Automation': automation
}

scenarios_list = list(scenarios_dict.keys())
colors_dict = {
    'Manual': '#00D9FF',
    'Hybrid': '#FFB700',
    'Full Automation': '#FF006E'
}

# ==================== MAIN HEADER ====================
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 10px;'>
        🏭 Assembly Project - Economic Analysis Dashboard
    </h1>
    <p style='text-align: center; color: #00D9FF; font-size: 1.1em;'>
        Dynamic Financial & Operational Comparison with Real-time Simulation
    </p>
""", unsafe_allow_html=True)

# ==================== TAB NAVIGATION ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "6.1 Basic Assumptions",
    "6.2-6.4 Financial Analysis",
    "6.5 Comparison",
    "💡 Scenarios",
    "🎯 Recommendation"
])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.markdown("### 📈 Quick Summary - Current Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    for idx, (col, scenario_name) in enumerate(zip([col1, col2, col3], scenarios_list)):
        with col:
            data = scenarios_dict[scenario_name]
            color = colors_dict[scenario_name]
            
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {color}20 0%, {color}05 100%);
                            border: 2px solid {color}; border-radius: 10px; padding: 20px;'>
                    <h3 style='color: {color}; margin-bottom: 15px;'>{scenario_name}</h3>
                    <div style='display: grid; gap: 12px;'>
                        <div>
                            <p style='color: #888; font-size: 0.9em; margin: 0;'>CAPEX</p>
                            <p style='font-size: 1.3em; font-weight: 700; margin: 5px 0 0 0;'>
                                {data['capex']:,.0f} SEK
                            </p>
                        </div>
                        <div>
                            <p style='color: #888; font-size: 0.9em; margin: 0;'>Cost/Unit</p>
                            <p style='font-size: 1.2em; font-weight: 700; margin: 5px 0 0 0;'>
                                {data['cost_per_unit']:.2f} SEK
                            </p>
                        </div>
                        <div>
                            <p style='color: #888; font-size: 0.9em; margin: 0;'>Profit/Unit</p>
                            <p style='font-size: 1.3em; font-weight: 700; color: {color}; margin: 5px 0 0 0;'>
                                {data['profit_per_unit']:.2f} SEK
                            </p>
                        </div>
                        <div>
                            <p style='color: #888; font-size: 0.9em; margin: 0;'>Annual Profit</p>
                            <p style='font-size: 1.3em; font-weight: 700; color: {color}; margin: 5px 0 0 0;'>
                                {data['annual_profit']/1e6:.2f}M SEK
                            </p>
                        </div>
                        <div style='border-top: 1px solid {color}40; padding-top: 10px;'>
                            <p style='color: #888; font-size: 0.9em; margin: 0;'>Payback Period</p>
                            <p style='font-size: 1.2em; font-weight: 700; margin: 5px 0 0 0;'>
                                {data['payback_days']:.0f} days
                            </p>
                        </div>
                        <div>
                            <p style='color: #888; font-size: 0.9em; margin: 0;'>ROI/Year</p>
                            <p style='font-size: 1.2em; font-weight: 700; margin: 5px 0 0 0;'>
                                {data['roi_percent']:.0f}%
                            </p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Comparison Table
    st.markdown("### 📊 Detailed Comparison Table")
    comparison_data = {
        'Metric': [
            'CAPEX (SEK)',
            'Cost/Unit (SEK)',
            'Selling Price (SEK)',
            'Profit/Unit (SEK)',
            'Profit Margin (%)',
            'Annual Revenue (SEK)',
            'Total Annual Cost (SEK)',
            'Annual Profit (SEK)',
            'Monthly Profit (SEK)',
            'Daily Profit (SEK)',
            'Payback Period (days)',
            'ROI (% per year)',
            'Operators',
            'Flexibility'
        ],
        'Manual': [
            f"{manual['capex']:,.0f}",
            f"{manual['cost_per_unit']:.2f}",
            f"{manual['selling_price']:.2f}",
            f"{manual['profit_per_unit']:.2f}",
            f"{manual['profit_margin']:.2f}%",
            f"{manual['annual_revenue']:,.0f}",
            f"{manual['total_annual_cost']:,.0f}",
            f"{manual['annual_profit']:,.0f}",
            f"{manual['monthly_profit']:,.0f}",
            f"{manual['daily_profit']:,.0f}",
            f"{manual['payback_days']:.0f}",
            f"{manual['roi_percent']:.0f}%",
            str(manual['operators']),
            manual['flexibility']
        ],
        'Hybrid': [
            f"{hybrid['capex']:,.0f}",
            f"{hybrid['cost_per_unit']:.2f}",
            f"{hybrid['selling_price']:.2f}",
            f"{hybrid['profit_per_unit']:.2f}",
            f"{hybrid['profit_margin']:.2f}%",
            f"{hybrid['annual_revenue']:,.0f}",
            f"{hybrid['total_annual_cost']:,.0f}",
            f"{hybrid['annual_profit']:,.0f}",
            f"{hybrid['monthly_profit']:,.0f}",
            f"{hybrid['daily_profit']:,.0f}",
            f"{hybrid['payback_days']:.0f}",
            f"{hybrid['roi_percent']:.0f}%",
            str(hybrid['operators']),
            hybrid['flexibility']
        ],
        'Full Automation': [
            f"{automation['capex']:,.0f}",
            f"{automation['cost_per_unit']:.2f}",
            f"{automation['selling_price']:.2f}",
            f"{automation['profit_per_unit']:.2f}",
            f"{automation['profit_margin']:.2f}%",
            f"{automation['annual_revenue']:,.0f}",
            f"{automation['total_annual_cost']:,.0f}",
            f"{automation['annual_profit']:,.0f}",
            f"{automation['monthly_profit']:,.0f}",
            f"{automation['daily_profit']:,.0f}",
            f"{automation['payback_days']:.0f}",
            f"{automation['roi_percent']:.0f}%",
            str(automation['operators']),
            automation['flexibility']
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ==================== TAB 2: BASIC ASSUMPTIONS ====================
with tab2:
    st.markdown("""
        ### 6.1 Basic Assumptions
        
        The economic analysis is based on the following fundamental parameters:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Annual Demand & Production")
        assumption_data = {
            'Parameter': [
                'Annual Demand',
                'Working Days per Year',
                'Daily Production Required',
                'Shifts per Day',
                'Hours per Shift',
                'Total Minutes per Day'
            ],
            'Value': [
                f'{production_volume:,.0f} units',
                '300 days',
                f'{production_volume/300:,.0f} units',
                '2 shifts',
                '8 hours',
                '960 minutes'
            ]
        }
        st.dataframe(pd.DataFrame(assumption_data), use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Takt Time & Efficiency")
        takt_data = {
            'Metric': [
                'Takt Time (Minutes)',
                'Takt Time (Seconds)',
                'Actual Bottleneck Cycle Time',
                'Takt Compliance %'
            ],
            'Value': [
                '1.9 minutes',
                '115 seconds',
                '121.5 seconds',
                '94.8%'
            ]
        }
        st.dataframe(pd.DataFrame(takt_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Workstation Configuration")
        station_data = {
            'Metric': [
                'Total Assembly Time',
                'Theoretical Min Stations',
                'Actual Stations',
                'Efficiency vs Theoretical'
            ],
            'Value': [
                '458.75 seconds',
                '4 stations',
                '4 stations',
                '100%'
            ]
        }
        st.dataframe(pd.DataFrame(station_data), use_container_width=True, hide_index=True)
    
    with col4:
        st.markdown("#### Overall Efficiency Metrics")
        efficiency_data = {
            'Metric': [
                'Line Balancing Efficiency',
                'Takt Compliance',
                'Station Utilization',
                'Workstation Efficiency'
            ],
            'Value': [
                '94.37%',
                '94.85%',
                '94.37%',
                '100%'
            ]
        }
        st.dataframe(pd.DataFrame(efficiency_data), use_container_width=True, hide_index=True)

# ==================== TAB 3: FINANCIAL ANALYSIS ====================
with tab3:
    st.markdown("### 6.2-6.4 Financial Analysis (Manual, Hybrid, & Automation)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Annual Profit Comparison
        fig_profit = go.Figure()
        profits = [manual['annual_profit'], hybrid['annual_profit'], automation['annual_profit']]
        colors = [colors_dict['Manual'], colors_dict['Hybrid'], colors_dict['Full Automation']]
        
        fig_profit.add_trace(go.Bar(
            x=scenarios_list,
            y=profits,
            marker=dict(color=colors),
            text=[f"{p/1e6:.2f}M" for p in profits],
            textposition='outside'
        ))
        
        fig_profit.update_layout(
            title="Annual Profit Comparison",
            yaxis_title="Profit (SEK)",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_profit, use_container_width=True)
    
    with col2:
        # Cost vs Price
        fig_cost = go.Figure()
        
        cost_list = [manual['cost_per_unit'], hybrid['cost_per_unit'], automation['cost_per_unit']]
        
        fig_cost.add_trace(go.Bar(
            name='Cost/Unit',
            x=scenarios_list,
            y=cost_list,
            marker=dict(color='rgba(255, 107, 107, 0.8)'),
            text=[f"{c:.2f}" for c in cost_list],
            textposition='outside'
        ))
        
        fig_cost.add_trace(go.Bar(
            name='Selling Price',
            x=scenarios_list,
            y=[selling_price] * 3,
            marker=dict(color='rgba(107, 255, 107, 0.8)'),
            text=[f"{selling_price:.2f}"] * 3,
            textposition='outside'
        ))
        
        fig_cost.update_layout(
            title="Cost vs Selling Price",
            yaxis_title="Price (SEK)",
            height=400,
            template="plotly_dark",
            barmode='group'
        )
        st.plotly_chart(fig_cost, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Profit per Unit
        fig_profit_unit = go.Figure()
        profit_units = [manual['profit_per_unit'], hybrid['profit_per_unit'], automation['profit_per_unit']]
        
        fig_profit_unit.add_trace(go.Bar(
            x=scenarios_list,
            y=profit_units,
            marker=dict(color=colors),
            text=[f"{p:.2f}" for p in profit_units],
            textposition='outside'
        ))
        
        fig_profit_unit.update_layout(
            title="Profit per Unit",
            yaxis_title="Profit (SEK)",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_profit_unit, use_container_width=True)
    
    with col4:
        # CAPEX
        fig_capex = go.Figure()
        capex_list = [manual['capex'], hybrid['capex'], automation['capex']]
        
        fig_capex.add_trace(go.Bar(
            x=scenarios_list,
            y=capex_list,
            marker=dict(color=colors),
            text=[f"{c/1e6:.2f}M" for c in capex_list],
            textposition='outside'
        ))
        
        fig_capex.update_layout(
            title="Initial Investment (CAPEX)",
            yaxis_title="CAPEX (SEK)",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_capex, use_container_width=True)

# ==================== TAB 4: COMPARISON ====================
with tab4:
    st.markdown("### 6.5 Comparison of All Three Assembly Scenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ROI Comparison
        fig_roi = go.Figure()
        roi_list = [manual['roi_percent'], hybrid['roi_percent'], automation['roi_percent']]
        
        fig_roi.add_trace(go.Bar(
            x=scenarios_list,
            y=roi_list,
            marker=dict(color=colors),
            text=[f"{r:.0f}%" for r in roi_list],
            textposition='outside'
        ))
        
        fig_roi.update_layout(
            title="ROI per Year",
            yaxis_title="ROI (%)",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        # Payback Period
        fig_payback = go.Figure()
        payback_list = [manual['payback_days'], hybrid['payback_days'], automation['payback_days']]
        
        fig_payback.add_trace(go.Bar(
            x=scenarios_list,
            y=payback_list,
            marker=dict(color=colors),
            text=[f"{p:.0f} days" for p in payback_list],
            textposition='outside'
        ))
        
        fig_payback.update_layout(
            title="Payback Period",
            yaxis_title="Days",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_payback, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Operators
        fig_operators = go.Figure()
        operators_list = [manual['operators'], hybrid['operators'], automation['operators']]
        
        fig_operators.add_trace(go.Bar(
            x=scenarios_list,
            y=operators_list,
            marker=dict(color=colors),
            text=operators_list,
            textposition='outside'
        ))
        
        fig_operators.update_layout(
            title="Operators Required",
            yaxis_title="Number of Operators",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_operators, use_container_width=True)
    
    with col4:
        # Profit Margin
        fig_margin = go.Figure()
        margins = [manual['profit_margin'], hybrid['profit_margin'], automation['profit_margin']]
        
        fig_margin.add_trace(go.Bar(
            x=scenarios_list,
            y=margins,
            marker=dict(color=colors),
            text=[f"{m:.2f}%" for m in margins],
            textposition='outside'
        ))
        
        fig_margin.update_layout(
            title="Profit Margin %",
            yaxis_title="Margin (%)",
            height=400,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig_margin, use_container_width=True)

# ==================== TAB 5: SCENARIO ANALYSIS ====================
with tab5:
    st.markdown("### 💡 What-If Scenario Analysis")
    
    st.markdown("""
    **Current Simulation Parameters:**
    - **Selling Price:** {:.2f} SEK
    - **Annual Production:** {:,.0f} units
    - **Manual CAPEX Multiplier:** {:.1f}x
    - **Hybrid CAPEX Multiplier:** {:.1f}x
    - **Automation CAPEX Multiplier:** {:.1f}x
    """.format(selling_price, production_volume, manual_mult, hybrid_mult, auto_mult))
    
    st.markdown("---")
    
    # Sensitivity Analysis - Price Impact
    st.markdown("#### Price Sensitivity Analysis")
    price_range = np.arange(200, 301, 10)
    manual_profit_by_price = []
    hybrid_profit_by_price = []
    auto_profit_by_price = []
    
    for p in price_range:
        m = calculate_scenario('Manual', p, production_volume, manual_mult)
        h = calculate_scenario('Hybrid', p, production_volume, hybrid_mult)
        a = calculate_scenario('Full Automation', p, production_volume, auto_mult)
        manual_profit_by_price.append(m['annual_profit'])
        hybrid_profit_by_price.append(h['annual_profit'])
        auto_profit_by_price.append(a['annual_profit'])
    
    fig_sensitivity = go.Figure()
    fig_sensitivity.add_trace(go.Scatter(
        x=price_range, y=np.array(manual_profit_by_price)/1e6,
        mode='lines+markers', name='Manual', line=dict(color='#00D9FF', width=3)
    ))
    fig_sensitivity.add_trace(go.Scatter(
        x=price_range, y=np.array(hybrid_profit_by_price)/1e6,
        mode='lines+markers', name='Hybrid', line=dict(color='#FFB700', width=3)
    ))
    fig_sensitivity.add_trace(go.Scatter(
        x=price_range, y=np.array(auto_profit_by_price)/1e6,
        mode='lines+markers', name='Full Automation', line=dict(color='#FF006E', width=3)
    ))
    
    fig_sensitivity.update_layout(
        title="Annual Profit vs Selling Price",
        xaxis_title="Selling Price (SEK)",
        yaxis_title="Annual Profit (M SEK)",
        height=500,
        template="plotly_dark",
        hovermode='x unified'
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    st.markdown("---")
    
    # Volume Sensitivity
    st.markdown("#### Production Volume Impact")
    volume_range = np.arange(50000, 301000, 20000)
    manual_profit_by_vol = []
    hybrid_profit_by_vol = []
    auto_profit_by_vol = []
    
    for v in volume_range:
        m = calculate_scenario('Manual', selling_price, v, manual_mult)
        h = calculate_scenario('Hybrid', selling_price, v, hybrid_mult)
        a = calculate_scenario('Full Automation', selling_price, v, auto_mult)
        manual_profit_by_vol.append(m['annual_profit'])
        hybrid_profit_by_vol.append(h['annual_profit'])
        auto_profit_by_vol.append(a['annual_profit'])
    
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Scatter(
        x=volume_range/1000, y=np.array(manual_profit_by_vol)/1e6,
        mode='lines+markers', name='Manual', line=dict(color='#00D9FF', width=3)
    ))
    fig_volume.add_trace(go.Scatter(
        x=volume_range/1000, y=np.array(hybrid_profit_by_vol)/1e6,
        mode='lines+markers', name='Hybrid', line=dict(color='#FFB700', width=3)
    ))
    fig_volume.add_trace(go.Scatter(
        x=volume_range/1000, y=np.array(auto_profit_by_vol)/1e6,
        mode='lines+markers', name='Full Automation', line=dict(color='#FF006E', width=3)
    ))
    
    fig_volume.update_layout(
        title="Annual Profit vs Production Volume",
        xaxis_title="Production Volume (k units)",
        yaxis_title="Annual Profit (M SEK)",
        height=500,
        template="plotly_dark",
        hovermode='x unified'
    )
    st.plotly_chart(fig_volume, use_container_width=True)

# ==================== TAB 6: RECOMMENDATION ====================
with tab6:
    st.markdown("### 🎯 Strategic Recommendation")
    
    # Determine best scenario
    profits = [manual['annual_profit'], hybrid['annual_profit'], automation['annual_profit']]
    best_idx = profits.index(max(profits))
    best_scenario = scenarios_list[best_idx]
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {colors_dict[best_scenario]}20 0%, {colors_dict[best_scenario]}05 100%);
                    border-left: 4px solid {colors_dict[best_scenario]}; border-radius: 8px; padding: 20px; margin-bottom: 20px;'>
            <h3 style='color: {colors_dict[best_scenario]}; margin-top: 0;'>✅ RECOMMENDED: {best_scenario}</h3>
            <p style='font-size: 1.05em; line-height: 1.6;'>
                Based on current simulation parameters, <b>{best_scenario}</b> provides the best financial performance
                with an annual profit of <b>{manual['annual_profit']/1e6:.2f}M SEK</b> and ROI of <b>{manual['roi_percent']:.0f}%</b> per year.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💡 Key Advantages")
        st.markdown(f"""
        - **Annual Profit:** {manual['annual_profit']/1e6:.2f}M SEK
        - **ROI:** {manual['roi_percent']:.0f}% per year
        - **Payback Period:** {manual['payback_days']:.0f} days
        - **Initial Investment:** {manual['capex']:,.0f} SEK
        - **Profit per Unit:** {manual['profit_per_unit']:.2f} SEK
        - **Operators Needed:** {manual['operators']}
        - **Flexibility:** {manual['flexibility']}
        """)
    
    with col2:
        st.markdown("#### ⚖️ vs Other Scenarios")
        
        if best_scenario == 'Manual':
            hybrid_diff_profit = manual['annual_profit'] - hybrid['annual_profit']
            hybrid_diff_percent = (hybrid_diff_profit / hybrid['annual_profit']) * 100
            auto_diff_profit = manual['annual_profit'] - automation['annual_profit']
            auto_diff_percent = (auto_diff_profit / automation['annual_profit']) * 100
            
            st.markdown(f"""
            **vs Hybrid:**
            - {hybrid_diff_percent:.0f}% higher profit
            - {manual['payback_days'] - hybrid['payback_days']:.0f} days faster payback
            - {manual['roi_percent'] - hybrid['roi_percent']:.0f}% higher ROI
            
            **vs Full Automation:**
            - {auto_diff_percent:.0f}% higher profit
            - {automation['payback_days'] - manual['payback_days']:.0f}x faster payback
            - {manual['roi_percent'] - automation['roi_percent']:.0f}% higher ROI
            """)
    
    st.markdown("---")
    
    # Risk Assessment
    st.markdown("#### 📊 Risk Assessment")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #00D9FF20 0%, #00D9FF05 100%);
                        border-left: 4px solid #00D9FF; border-radius: 8px; padding: 15px;'>
                <h4 style='color: #00D9FF; margin-top: 0;'>Manual Assembly</h4>
                <p><b>Risk Level: LOW</b></p>
                <ul style='margin: 10px 0;'>
                    <li>Quick payback minimizes exposure</li>
                    <li>Operators can assist each other</li>
                    <li>Simple maintenance</li>
                    <li>High operational flexibility</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #FFB70020 0%, #FFB70005 100%);
                        border-left: 4px solid #FFB700; border-radius: 8px; padding: 15px;'>
                <h4 style='color: #FFB700; margin-top: 0;'>Hybrid Assembly</h4>
                <p><b>Risk Level: MEDIUM</b></p>
                <ul style='margin: 10px 0;'>
                    <li>Moderate payback period</li>
                    <li>Partial automation support</li>
                    <li>Balanced approach</li>
                    <li>Medium flexibility</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #FF006E20 0%, #FF006E05 100%);
                        border-left: 4px solid #FF006E; border-radius: 8px; padding: 15px;'>
                <h4 style='color: #FF006E; margin-top: 0;'>Full Automation</h4>
                <p><b>Risk Level: HIGH</b></p>
                <ul style='margin: 10px 0;'>
                    <li>Very long payback ({automation['payback_days']:.0f} days)</li>
                    <li>System failure = line stop</li>
                    <li>Complex maintenance</li>
                    <li>Low flexibility</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    #### 📝 Implementation Notes
    
    **For Manual Assembly:**
    - Start production immediately with minimal upfront investment
    - Focus on operator training and quality control
    - Monitor profitability and reinvest returns
    - Consider hybrid upgrade if demand exceeds {:.0f} units/year
    
    **When to Consider Alternatives:**
    - **Hybrid:** If labor costs rise >20% or demand exceeds 200k units/year
    - **Automation:** Only for mature, unchanging products with consistent 200k+ unit demand and available capital
    """.format(production_volume))

st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #888; font-size: 0.9em;'>
    Dashboard updated with real-time simulation | Adjust parameters in the sidebar to explore different scenarios
</p>
""", unsafe_allow_html=True)
