import streamlit as st

from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
import time
import threading

st.title("Speculative Decoding")

target_model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
draft_model_id = "HuggingFaceTB/SmolLM2-135M-Instruct"

@st.cache_resource
def get_target_model():
    model = AutoModelForCausalLM.from_pretrained(target_model_id)
    tokenizer = AutoTokenizer.from_pretrained(target_model_id)
    model.generation_config.max_length   = None
    model.generation_config.min_length   = None      # ← this is the culprit
    model.generation_config.min_new_tokens = None
    return model, tokenizer

@st.cache_resource
def get_draft_model():
    return AutoModelForCausalLM.from_pretrained(draft_model_id)


target_model, tokenizer = get_target_model()
draft_model = get_draft_model()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])



streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
prompt =st.chat_input("Enter your prompt here", key="prompt")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    inputs = tokenizer(prompt, return_tensors="pt")

    thread = threading.Thread(
        target=target_model.generate,
        kwargs=dict(
            **inputs,
            assistant_model=draft_model,
            max_new_tokens=200,
            streamer=streamer,
            min_length=0,
            min_new_tokens=None,
            do_sample=False,
            use_cache=True,
        )
    )

    token_count = 0

    def stream_and_count():
        global token_count

        for text in streamer:
            # count generated tokens
            token_count += len(
                tokenizer.encode(
                    text,
                    add_special_tokens=False
                )
            )
            yield text

    start = time.time()

    thread.start()
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = st.write_stream(stream_and_count)

        # print("Response:\n" + "-"*40)
        # for token in streamer:
        #     st.write(token)
        #     # print(token, end="", flush=True)
        #     token_count += len(tokenizer.encode(token, add_special_tokens=False))

    thread.join()


    elapsed = time.time() - start
    additonal_info = f"""

    ---
    **Tokens generated:** {token_count}  
    **Time elapsed:** {elapsed:.2f}s  
    **Throughput:** {token_count/elapsed:.1f} tokens/sec
    """
    st.write(f"Tokens generated : {token_count}")
    st.write(f"Time elapsed     : {elapsed:.2f}s")
    st.write(f"Throughput       : {token_count/elapsed:.1f} tokens/sec")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response + additonal_info
    })
