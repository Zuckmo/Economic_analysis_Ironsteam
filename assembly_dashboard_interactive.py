import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configure page
st.set_page_config(
    page_title="Assembly Project - Economic Analysis Dashboard",
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
if 'labor_cost_mult' not in st.session_state:
    st.session_state.labor_cost_mult = 1.0
if 'overhead_cost_mult' not in st.session_state:
    st.session_state.overhead_cost_mult = 1.0
if 'material_cost_mult' not in st.session_state:
    st.session_state.material_cost_mult = 1.0

# ==================== SIDEBAR - SIMULATION PARAMETERS ====================
with st.sidebar:
    st.markdown("### SIMULATION PARAMETERS")
    st.markdown("---")

    st.markdown("#### Selling Price per Unit (SEK)")
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

    st.markdown("#### Annual Production Volume (units)")
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

    st.markdown("#### CAPEX Cost Adjustment")

    st.markdown("**Manual Assembly CAPEX**")
    st.markdown('<span style="font-size: 0.85em; color: #888;">Base: 388,100 SEK</span>', unsafe_allow_html=True)
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
    st.markdown('<span style="font-size: 0.85em; color: #888;">Base: 444,581 SEK</span>', unsafe_allow_html=True)
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
    st.markdown('<span style="font-size: 0.85em; color: #888;">Base: 2,576,187 SEK</span>', unsafe_allow_html=True)
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

    st.markdown("#### Operational Cost Adjustment")

    st.markdown("**Material Cost Multiplier**")
    st.markdown('<span style="font-size: 0.85em; color: #888;">Base: 191.59 SEK/unit (all scenarios)</span>', unsafe_allow_html=True)
    material_mult = st.slider(
        "Material cost multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.material_cost_mult,
        step=0.1,
        label_visibility="collapsed"
    )
    st.session_state.material_cost_mult = material_mult
    st.caption(f"Multiplier: {material_mult:.1f}x")

    st.markdown("**Labor Cost Multiplier**")
    st.markdown('<span style="font-size: 0.85em; color: #888;">Manual: 2.74/unit | Hybrid: 1,365,840/yr | Auto: 780,480/yr</span>', unsafe_allow_html=True)
    labor_mult = st.slider(
        "Labor cost multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.labor_cost_mult,
        step=0.1,
        label_visibility="collapsed"
    )
    st.session_state.labor_cost_mult = labor_mult
    st.caption(f"Multiplier: {labor_mult:.1f}x")

    st.markdown("**Overhead Cost Multiplier**")
    st.markdown('<span style="font-size: 0.85em; color: #888;">Manual: 600,000/yr | Hybrid: 600,000/yr | Auto: 30,000/yr</span>', unsafe_allow_html=True)
    overhead_mult = st.slider(
        "Overhead cost multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.overhead_cost_mult,
        step=0.1,
        label_visibility="collapsed"
    )
    st.session_state.overhead_cost_mult = overhead_mult
    st.caption(f"Multiplier: {overhead_mult:.1f}x")

    st.markdown("---")
    st.markdown("**Tips:**")
    st.markdown("""
    - **Material:** Supplier price changes, bulk discounts
    - **Labor:** Wage increases, productivity improvements
    - **Overhead:** Facility costs, utilities, maintenance
    """)
    st.markdown("**Adjust sliders to simulate cost inflation or efficiency improvements.**")

# ==================== CALCULATE DYNAMICS DATA ====================

def calculate_scenario(scenario_type, selling_price, production_volume,
                        capex_multiplier, material_mult, labor_mult, overhead_mult):
    """
    Calculate financial metrics based on parameters.

    Base figures taken directly from the Final Report (Section 6):

      Manual Assembly (6.2)
        CAPEX 388,100 (5-yr depreciation = 77,620/yr)
        Material 191.59/unit | Labor 2.74/unit (cycle-time based)
        Overhead 600,000/yr | no separate maintenance
        => Cost/unit 198.85, Profit/unit 31.15, Annual profit 4,672,299

      Hybrid Assembly (6.4) - 4 stations automated (F, Q, R, Z)
        CAPEX 444,581 (5-yr depreciation = 88,916/yr)
        Material 191.59/unit | Labor 1,365,840/yr (7 operators)
        General overhead 600,000/yr | Automation maintenance 8,472/yr
        => Cost/unit 205.35, Profit/unit 24.65, Annual profit 3,697,500

      Full Automation (6.3) - REVISED
        CAPEX 2,576,187 (5-yr depreciation = 515,237.40/yr)
        Material 191.59/unit | Labor 780,480/yr (2 operators)
        Overhead 30,000/yr | Maintenance 77,286/yr (15% of depreciation)
        => Cost/unit 200.94, Profit/unit 29.06, Annual profit 4,358,497
    """

    base_data = {
        'Manual': {
            'base_capex': 388100,
            'depreciation_years': 5,
            'material_per_unit': 191.59,
            'labor_model': 'per_unit',
            'labor_per_unit': 2.7438749999999996,   # cycle-time based (6.2.3)
            'annual_overhead': 600000,
            'annual_maintenance': 0.0,               # no separate maintenance line
            'operators': 10,
            'flexibility': 'High'
        },
        'Hybrid': {
            'base_capex': 444581,
            'depreciation_years': 5,
            'material_per_unit': 191.59,
            'labor_model': 'annual',
            'annual_labor': 1365840,                 # 7 operators (6.4.3)
            'annual_overhead': 600000,               # general overhead, same as manual
            'annual_maintenance': 8472.0,            # 15% of automation portion (6.4.4)
            'operators': 7,
            'flexibility': 'Medium'
        },
        'Full Automation': {
            'base_capex': 2576187,                   # REVISED (Total automation CAPEX)
            'depreciation_years': 5,
            'material_per_unit': 191.59,
            'labor_model': 'annual',
            'annual_labor': 780480,                  # 2 operators (6.3.2)
            'annual_overhead': 30000,                # REVISED
            'annual_maintenance': 77286.0,           # REVISED (15% of annual depreciation)
            'operators': 2,
            'flexibility': 'Low'
        }
    }

    data = base_data[scenario_type]

    # CAPEX & depreciation (maintenance scales with the same CAPEX multiplier)
    adjusted_capex = data['base_capex'] * capex_multiplier
    annual_depreciation = adjusted_capex / data['depreciation_years']
    annual_maintenance = data['annual_maintenance'] * capex_multiplier

    # Per-unit cost components
    material_cost = data['material_per_unit'] * material_mult

    if data['labor_model'] == 'per_unit':
        labor_cost = data['labor_per_unit'] * labor_mult
    else:
        labor_cost = (data['annual_labor'] * labor_mult) / production_volume

    overhead_cost = (data['annual_overhead'] * overhead_mult) / production_volume
    maintenance_cost = annual_maintenance / production_volume
    capex_per_unit = annual_depreciation / production_volume

    cost_per_unit = (material_cost + labor_cost + overhead_cost +
                     maintenance_cost + capex_per_unit)
    profit_per_unit = selling_price - cost_per_unit

    # Financial calculations
    annual_revenue = selling_price * production_volume
    total_annual_cost = cost_per_unit * production_volume
    annual_profit = profit_per_unit * production_volume

    monthly_profit = annual_profit / 12
    daily_profit = annual_profit / 365

    profit_margin = (profit_per_unit / selling_price) * 100 if selling_price > 0 else 0

    # Payback period (CAPEX recovered from annual profit)
    if annual_profit > 0 and adjusted_capex > 0:
        payback_days = (adjusted_capex / annual_profit) * 365
    else:
        payback_days = 999999

    # ROI
    if annual_profit > 0 and adjusted_capex > 0:
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
        'flexibility': data['flexibility'],
        'material_cost': material_cost,
        'labor_cost': labor_cost,
        'overhead_cost': overhead_cost,
        'maintenance_cost': maintenance_cost,
        'capex_per_unit': capex_per_unit
    }

# Calculate all scenarios
manual = calculate_scenario('Manual', selling_price, production_volume,
                            manual_mult, material_mult, labor_mult, overhead_mult)
hybrid = calculate_scenario('Hybrid', selling_price, production_volume,
                            hybrid_mult, material_mult, labor_mult, overhead_mult)
automation = calculate_scenario('Full Automation', selling_price, production_volume,
                                auto_mult, material_mult, labor_mult, overhead_mult)

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
        Assembly Project - Economic Analysis Dashboard
    </h1>
    <p style='text-align: center; color: #00D9FF; font-size: 1.1em;'>
        Dynamic Financial & Operational Comparison with Real-time Simulation
    </p>
""", unsafe_allow_html=True)

# ==================== TAB NAVIGATION ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "6.1 Basic Assumptions",
    "6.2-6.4 Financial Analysis",
    "6.5 Comparison",
    "Scenarios",
    "Recommendation"
])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.markdown("### Quick Summary - Current Simulation")

    col1, col2, col3 = st.columns(3)

    for col, scenario_name in zip([col1, col2, col3], scenarios_list):
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

    st.markdown("### Cost Breakdown per Unit (Current Simulation)")

    cost_breakdown = {
        'Cost Component': ['Material', 'Labor', 'Overhead', 'Maintenance', 'CAPEX/Unit', 'Total'],
    }
    for name in scenarios_list:
        d = scenarios_dict[name]
        cost_breakdown[name] = [
            f"{d['material_cost']:.2f}",
            f"{d['labor_cost']:.2f}",
            f"{d['overhead_cost']:.2f}",
            f"{d['maintenance_cost']:.2f}",
            f"{d['capex_per_unit']:.2f}",
            f"{d['cost_per_unit']:.2f}"
        ]

    st.dataframe(pd.DataFrame(cost_breakdown), use_container_width=True, hide_index=True)

    st.markdown("---")

    st.markdown("### Detailed Comparison Table")
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
        ]
    }
    for name in scenarios_list:
        d = scenarios_dict[name]
        comparison_data[name] = [
            f"{d['capex']:,.0f}",
            f"{d['cost_per_unit']:.2f}",
            f"{d['selling_price']:.2f}",
            f"{d['profit_per_unit']:.2f}",
            f"{d['profit_margin']:.2f}%",
            f"{d['annual_revenue']:,.0f}",
            f"{d['total_annual_cost']:,.0f}",
            f"{d['annual_profit']:,.0f}",
            f"{d['monthly_profit']:,.0f}",
            f"{d['daily_profit']:,.0f}",
            f"{d['payback_days']:.0f}",
            f"{d['roi_percent']:.0f}%",
            str(d['operators']),
            d['flexibility']
        ]

    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

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
                'Actual Cycle Time (Minutes)',
                'Takt Compliance %'
            ],
            'Value': [
                '1.9 minutes',
                '115 seconds',
                '121.5 seconds',
                '2.025 minutes',
                '94.85%'
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
                'Production Capacity Efficiency',
                'Workstation Efficiency'
            ],
            'Value': [
                '94.37%',
                '94.85%',
                '94.37%',
                '105.53%',
                '100%'
            ]
        }
        st.dataframe(pd.DataFrame(efficiency_data), use_container_width=True, hide_index=True)

# ==================== TAB 3: FINANCIAL ANALYSIS ====================
with tab3:
    st.markdown("### 6.2-6.4 Financial Analysis (Manual, Hybrid & Automation)")

    colors = [colors_dict[s] for s in scenarios_list]

    col1, col2 = st.columns(2)

    with col1:
        fig_profit = go.Figure()
        profits = [scenarios_dict[s]['annual_profit'] for s in scenarios_list]
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
        fig_cost = go.Figure()
        cost_list = [scenarios_dict[s]['cost_per_unit'] for s in scenarios_list]
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
            y=[selling_price] * len(scenarios_list),
            marker=dict(color='rgba(107, 255, 107, 0.8)'),
            text=[f"{selling_price:.2f}"] * len(scenarios_list),
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
        fig_profit_unit = go.Figure()
        profit_units = [scenarios_dict[s]['profit_per_unit'] for s in scenarios_list]
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
        fig_capex = go.Figure()
        capex_list = [scenarios_dict[s]['capex'] for s in scenarios_list]
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

    colors = [colors_dict[s] for s in scenarios_list]

    col1, col2 = st.columns(2)

    with col1:
        fig_roi = go.Figure()
        roi_list = [scenarios_dict[s]['roi_percent'] for s in scenarios_list]
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
        fig_payback = go.Figure()
        payback_list = [scenarios_dict[s]['payback_days'] for s in scenarios_list]
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
        fig_operators = go.Figure()
        operators_list = [scenarios_dict[s]['operators'] for s in scenarios_list]
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
        fig_margin = go.Figure()
        margins = [scenarios_dict[s]['profit_margin'] for s in scenarios_list]
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
    st.markdown("### What-If Scenario Analysis")

    st.markdown(f"""
    **Current Simulation Parameters:**
    - **Selling Price:** {selling_price:.2f} SEK
    - **Annual Production:** {production_volume:,.0f} units
    - **Manual CAPEX Multiplier:** {manual_mult:.1f}x
    - **Hybrid CAPEX Multiplier:** {hybrid_mult:.1f}x
    - **Automation CAPEX Multiplier:** {auto_mult:.1f}x
    - **Material Cost Multiplier:** {material_mult:.1f}x
    - **Labor Cost Multiplier:** {labor_mult:.1f}x
    - **Overhead Cost Multiplier:** {overhead_mult:.1f}x
    """)

    st.markdown("---")

    mults = {'Manual': manual_mult, 'Hybrid': hybrid_mult, 'Full Automation': auto_mult}

    st.markdown("#### Price Sensitivity Analysis")
    price_range = np.arange(200, 301, 10)
    sens = {s: [] for s in scenarios_list}
    for p in price_range:
        for s in scenarios_list:
            r = calculate_scenario(s, p, production_volume, mults[s], material_mult, labor_mult, overhead_mult)
            sens[s].append(r['annual_profit'])

    fig_sensitivity = go.Figure()
    for s in scenarios_list:
        fig_sensitivity.add_trace(go.Scatter(
            x=price_range, y=np.array(sens[s])/1e6,
            mode='lines+markers', name=s, line=dict(color=colors_dict[s], width=3)
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

    st.markdown("#### Production Volume Impact")
    volume_range = np.arange(50000, 301000, 20000)
    volp = {s: [] for s in scenarios_list}
    for v in volume_range:
        for s in scenarios_list:
            r = calculate_scenario(s, selling_price, v, mults[s], material_mult, labor_mult, overhead_mult)
            volp[s].append(r['annual_profit'])

    fig_volume = go.Figure()
    for s in scenarios_list:
        fig_volume.add_trace(go.Scatter(
            x=volume_range/1000, y=np.array(volp[s])/1e6,
            mode='lines+markers', name=s, line=dict(color=colors_dict[s], width=3)
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
    st.markdown("### Strategic Recommendation")

    profits = [scenarios_dict[s]['annual_profit'] for s in scenarios_list]
    best_idx = profits.index(max(profits))
    best_scenario = scenarios_list[best_idx]
    best_data = scenarios_dict[best_scenario]

    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {colors_dict[best_scenario]}20 0%, {colors_dict[best_scenario]}05 100%);
                    border-left: 4px solid {colors_dict[best_scenario]}; border-radius: 8px; padding: 20px; margin-bottom: 20px;'>
            <h3 style='color: {colors_dict[best_scenario]}; margin-top: 0;'>RECOMMENDED: {best_scenario}</h3>
            <p style='font-size: 1.05em; line-height: 1.6;'>
                Based on current simulation parameters, <b>{best_scenario}</b> provides the best financial performance
                with an annual profit of <b>{best_data['annual_profit']/1e6:.2f}M SEK</b> and ROI of <b>{best_data['roi_percent']:.0f}%</b> per year.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Key Advantages")
        st.markdown(f"""
        - **Annual Profit:** {best_data['annual_profit']/1e6:.2f}M SEK
        - **ROI:** {best_data['roi_percent']:.0f}% per year
        - **Payback Period:** {best_data['payback_days']:.0f} days
        - **Initial Investment:** {best_data['capex']:,.0f} SEK
        - **Profit per Unit:** {best_data['profit_per_unit']:.2f} SEK
        - **Cost per Unit:** {best_data['cost_per_unit']:.2f} SEK
        - **Operators Needed:** {best_data['operators']}
        - **Flexibility:** {best_data['flexibility']}
        """)

    with col2:
        st.markdown("#### vs Other Scenarios")
        lines = []
        for s in scenarios_list:
            if s == best_scenario:
                continue
            o = scenarios_dict[s]
            diff_profit = best_data['annual_profit'] - o['annual_profit']
            diff_percent = (diff_profit / o['annual_profit']) * 100 if o['annual_profit'] != 0 else 0
            lines.append(
                f"**vs {s}:**\n"
                f"- {abs(diff_percent):.0f}% {'higher' if diff_percent >= 0 else 'lower'} annual profit\n"
                f"- {abs(best_data['payback_days'] - o['payback_days']):.0f} days payback difference\n"
                f"- {abs(best_data['roi_percent'] - o['roi_percent']):.0f}% ROI difference\n"
            )
        st.markdown("\n".join(lines))

    st.markdown("---")

    st.markdown("#### Risk Assessment")
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #00D9FF20 0%, #00D9FF05 100%);
                        border-left: 4px solid #00D9FF; border-radius: 8px; padding: 15px;'>
                <h4 style='color: #00D9FF; margin-top: 0;'>Manual Assembly</h4>
                <p><b>Risk Level: LOW</b></p>
                <ul style='margin: 10px 0;'>
                    <li>Quick payback ({manual['payback_days']:.0f} days) minimizes exposure</li>
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
                    <li>Moderate payback ({hybrid['payback_days']:.0f} days)</li>
                    <li>4 stations automated (F, Q, R, Z)</li>
                    <li>Reduced to 7 operators</li>
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

    st.markdown(f"""
    #### Implementation Notes

    **Current Operational Cost Status:**
    - Material Cost Multiplier: {material_mult:.1f}x
    - Labor Cost Multiplier: {labor_mult:.1f}x
    - Overhead Cost Multiplier: {overhead_mult:.1f}x
    - Total Cost per Unit: {best_data['cost_per_unit']:.2f} SEK

    **Cost Breakdown ({best_scenario}):**
    - Material: {best_data['material_cost']:.2f} SEK ({best_data['material_cost']/best_data['cost_per_unit']*100:.1f}%)
    - Labor: {best_data['labor_cost']:.2f} SEK ({best_data['labor_cost']/best_data['cost_per_unit']*100:.1f}%)
    - Overhead: {best_data['overhead_cost']:.2f} SEK ({best_data['overhead_cost']/best_data['cost_per_unit']*100:.1f}%)
    - Maintenance: {best_data['maintenance_cost']:.2f} SEK ({best_data['maintenance_cost']/best_data['cost_per_unit']*100:.1f}%)
    - CAPEX/Unit: {best_data['capex_per_unit']:.2f} SEK ({best_data['capex_per_unit']/best_data['cost_per_unit']*100:.1f}%)

    **For {best_scenario}:**
    - Start with current parameters
    - Monitor material and labor cost trends
    - Consider hybrid upgrade if costs rise significantly
    - Plan for scaling based on volume growth
    """)

st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #888; font-size: 0.9em;'>
    Dashboard updated with real-time simulation | Adjust parameters in the sidebar to explore different scenarios
</p>
""", unsafe_allow_html=True)