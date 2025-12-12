import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="QualSteam SOPT Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Visibility and Contrast
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #e0e5ec; /* Darker slate-grey for contrast */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1a202c !important; /* Force dark text for headers */
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    h1 {
        border-bottom: 2px solid #cbd5e0;
        padding-bottom: 1rem;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid #cbd5e0;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #1E3A8A; /* Dark Blue */
    }
    .metric-label {
        font-size: 15px;
        color: #4A5568; /* Dark Grey */
        font-weight: 600;
        margin-top: 5px;
    }

    /* Stat Cards (Sidebar/Right column) */
    .stat-box {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    # UPDATED: Pointing to the specific GitHub/project folder structure
    file_path = 'data/df_stable_only.csv'
    
    try:
        df = pd.read_csv(file_path)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except FileNotFoundError:
        return None

def calculate_stats(series):
    return {
        "Mean": f"{series.mean():.2f}",
        "Median": f"{series.median():.2f}",
        "Max": f"{series.max():.2f}",
        "Min": f"{series.min():.2f}",
        "Std Dev": f"{series.std():.4f}"
    }

# --- 3. MAIN APPLICATION ---
def main():
    # Header
    st.title("🏭 QualSteam Real Dairy Stable Process (SOPT)")

    # Load Data
    df = load_data()

    if df is None:
        st.error(f"⚠️ Data file not found at `data/df_stable_only.csv`. Please ensure the file exists in your repository.")
        st.stop()

    # --- SIDEBAR: SELECTION ---
    st.sidebar.header("Batch Selection")
    
    # Get unique batches
    unique_batches = df['batch_id'].unique()
    unique_batches.sort()
    
    selected_batch_id = st.sidebar.selectbox(
        "Select Batch ID",
        unique_batches,
        index=0 if len(unique_batches) > 0 else None
    )

    if selected_batch_id is None:
        st.info("No batches available.")
        st.stop()

    # Filter Data
    batch_data = df[df['batch_id'] == selected_batch_id].copy()
    
    # Calculate Time Metrics
    start_time = batch_data['Timestamp'].min()
    end_time = batch_data['Timestamp'].max()
    duration = (end_time - start_time).total_seconds() / 60.0
    date_str = start_time.strftime('%Y-%m-%d')
    time_range_str = f"{start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"

    # --- TOP METRICS ROW ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">Batch #{selected_batch_id}</div><div class="metric-label">Batch ID</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{date_str}</div><div class="metric-label">Date</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{time_range_str}</div><div class="metric-label">Time Range</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{duration:.2f} mins</div><div class="metric-label">Stable Duration</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # --- VISUALIZATION & STATS ---
    
    # Layout: Graphs on Left (Wide), Stats on Right (Narrow)
    col_graph, col_stats = st.columns([3, 1])

    with col_graph:
        st.subheader(f"Interactive Process Analysis - Batch {selected_batch_id}")
        
        # Create Subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=("Temperature", "Pressure (Inlet & Outlet)", "Steam Flow Rate", "Valve Opening"),
            row_heights=[0.25, 0.25, 0.25, 0.25]
        )

        # Colors
        c_temp = '#D32F2F'       # Red
        c_temp_sp = 'black'      # Black
        c_p1 = '#004D40'         # Teal
        c_p2 = '#00008B'         # Dark Blue
        c_p_sp = '#1A237E'       # Indigo
        c_flow = '#7B1FA2'       # Violet
        c_valve = '#B8860B'      # Dark Goldenrod

        # 1. Temperature
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['Process Temp SP'],
                                 mode='lines', line=dict(color=c_temp_sp, dash='dot', width=2),
                                 name='Process Temp SP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['Process Temp'],
                                 mode='lines', line=dict(color=c_temp, width=2),
                                 name='Process Temp'), row=1, col=1)

        # 2. Pressure
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['Pressure SP'],
                                 mode='lines', line=dict(color=c_p_sp, dash='dot', width=2),
                                 name='Pressure SP'), row=2, col=1)
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['Inlet Steam Pressure'],
                                 mode='lines', line=dict(color=c_p1, width=2),
                                 name='Inlet P1'), row=2, col=1)
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['Outlet Steam Pressure'],
                                 mode='lines', line=dict(color=c_p2, width=2),
                                 fill='tozeroy', fillcolor='rgba(0, 0, 139, 0.1)', # Light blue fill
                                 name='Outlet P2'), row=2, col=1)

        # 3. Flow
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['Steam Flow Rate'],
                                 mode='lines', line=dict(color=c_flow, width=2),
                                 fill='tozeroy', fillcolor='rgba(123, 31, 162, 0.1)',
                                 name='Flow Rate'), row=3, col=1)

        # 4. Valve
        fig.add_trace(go.Scatter(x=batch_data['Timestamp'], y=batch_data['QualSteam Valve Opening'],
                                 mode='lines', line=dict(color=c_valve, width=2),
                                 fill='tozeroy', fillcolor='rgba(184, 134, 11, 0.1)',
                                 name='Valve %'), row=4, col=1)

        # Update Layout
        fig.update_layout(
            height=900,
            showlegend=True,
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(color="black") # Force all text to black for visibility
        )

        # Explicitly ensure subplot titles are black
        fig.update_annotations(font_color="black", font_size=16)
        
        # Update Axes
        fig.update_yaxes(title_text="Temp (°C)", row=1, col=1, gridcolor='#f0f0f0')
        fig.update_yaxes(title_text="Bar", row=2, col=1, gridcolor='#f0f0f0')
        fig.update_yaxes(title_text="kg/hr", row=3, col=1, gridcolor='#f0f0f0')
        fig.update_yaxes(title_text="%", row=4, col=1, gridcolor='#f0f0f0', range=[0, 105])
        fig.update_xaxes(gridcolor='#f0f0f0', row=4, col=1)

        st.plotly_chart(fig, use_container_width=True)

    with col_stats:
        st.subheader("📊 Statistics")
        st.markdown("Detailed breakdown for the stable phase.")
        
        # Helper to display stats card
        def stat_card(title, stats_dict, color_border):
            st.markdown(f"""
            <div class="stat-box" style="border-left: 5px solid {color_border};">
                <h4 style="margin:0; color: #1a202c; font-size: 16px;">{title}</h4>
                <div style="font-size: 0.95em; margin-top: 8px; color: #4a5568;">
                    <div style="display:flex; justify-content:space-between;"><span>Mean:</span> <b>{stats_dict['Mean']}</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>Median:</span> <b>{stats_dict['Median']}</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>Max:</span> <b>{stats_dict['Max']}</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>Min:</span> <b>{stats_dict['Min']}</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>Std:</span> <b>{stats_dict['Std Dev']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 1. Temp Stats
        stats_temp = calculate_stats(batch_data['Process Temp'])
        stat_card("Process Temp (°C)", stats_temp, c_temp)

        # 2. P2 Stats
        stats_p2 = calculate_stats(batch_data['Outlet Steam Pressure'])
        stat_card("Outlet Pressure P2 (Bar)", stats_p2, c_p2)
        
        # 2b. P1 Stats
        stats_p1 = calculate_stats(batch_data['Inlet Steam Pressure'])
        stat_card("Inlet Pressure P1 (Bar)", stats_p1, c_p1)

        # 3. Flow Stats
        stats_flow = calculate_stats(batch_data['Steam Flow Rate'])
        stat_card("Steam Flow (kg/hr)", stats_flow, c_flow)

        # 4. Valve Stats
        stats_valve = calculate_stats(batch_data['QualSteam Valve Opening'])
        stat_card("Valve Opening (%)", stats_valve, c_valve)

if __name__ == "__main__":
    main()
