import plotly.graph_objects as go
import streamlit as st

def render_analytics_tab():
    """Renders time-series Plotly telemetry charts."""
    st.subheader("Time-Series System Telemetry Trends")
    st.caption("Inspect power consumption and electrical performance across equipment lines.")

    if len(st.session_state.telemetry_history) > 1:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=st.session_state.telemetry_history['Timestamp'],
            y=st.session_state.telemetry_history['Total_kW'],
            mode='lines+markers',
            name='Total Building Power (kW)',
            line=dict(color='#00D1B2', width=3)
        ))

        fig.add_trace(go.Scatter(
            x=st.session_state.telemetry_history['Timestamp'],
            y=st.session_state.telemetry_history['AHU_kW'],
            mode='lines',
            name='AHU-01 Power (kW)',
            line=dict(color='#FFDD57', dash='dot')
        ))

        fig.add_trace(go.Scatter(
            x=st.session_state.telemetry_history['Timestamp'],
            y=st.session_state.telemetry_history['EF_kW'],
            mode='lines',
            name='EF-02 Power (kW)',
            line=dict(color='#FF3860', dash='dot')
        ))

        fig.update_layout(
            title="Active Power Readouts (kW) Over Time",
            xaxis_title="Time Stamp",
            yaxis_title="Active Power (kW)",
            template="plotly_dark",
            height=420,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Collecting telemetry polling records... Adjust sidebar toggles to generate historical plot data.")