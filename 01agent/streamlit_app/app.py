import streamlit as st

st.set_page_config(layout="wide")

st.title("🤖 01Agent Desktop Assistant (PoC)")

st.markdown("""
    This is a Proof of Concept Streamlit application for the 01Agent frontend.
    It aims to demonstrate the feasibility of using Streamlit for a lightweight and performant UI.
""")

st.header("Agent Status")
# Placeholder for agent status
st.info("Status: Ready (Placeholder)")
st.text("CPU: --%")
st.text("Memory: --%")
st.text("Tasks Completed: --")

st.header("Send Command to Agent")
command = st.text_input("Enter your command here:", key="command_input")

if st.button("Send Command"):
    if command:
        st.success(f"Command sent: {command} (Placeholder - command is just printed to console)")
        print(f"Command received in Streamlit app: {command}") # For demonstration
    else:
        st.warning("Please enter a command.")

st.markdown("---")
st.markdown("Developed by 01Agent Team")