import streamlit as st
import requests
import json


API_URL = "http://localhost:8000"


st.title("Speculative Decoding - Frontend Only")


with st.sidebar:
    st.header("Settings")

    max_new_tokens = st.slider("Max New Tokens", min_value=10, max_value=500, value=200, step=10)

    st.divider()

    if st.button("Check Server"):
        try:
            r = requests.get(f"{API_URL}/health")
            st.success("Server is up ✅") if r.ok else st.error("Server down ❌")
        except Exception as e:
            st.error(f"Error connecting to server: {e}")



prompt = st.text_area("Prompt", placeholder="Enter your prompt here...", key="prompt")

if st.button("Generate", type="primary") and prompt:
    
    output_box = st.empty()

    full_text = ""

    with st.spinner("Generating..."):
        with requests.get(
            f"{API_URL}/generate",
            params={"prompt": prompt, "max_new_tokens": max_new_tokens},
            stream=True
        ) as r:
            
            for line in r.iter_lines():
                if line:

                    raw = line.decode("utf-8").strip()
                    if raw.startswith("data: "):
                        data = json.loads(raw[len("data: "):])
                        if data.get("done"):
                            break

                        full_text += data.get("token", "")
                        output_box.markdown(full_text + "▌")