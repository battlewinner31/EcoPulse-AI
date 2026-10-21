import streamlit as st

def render_logbook_tab():
    """Renders the pandas event log register."""
    st.subheader("Raw Telemetry Event Stream")
    st.caption("Continuous chronological register of physical values recorded at system polling intervals.")

    st.dataframe(
        st.session_state.event_log,
        use_container_width=True,
        hide_index=True
    )