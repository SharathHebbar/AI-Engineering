from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
import threading
import time

from transformers import TextIteratorStreamer
import torch, threading, time

target_model.generation_config.max_length   = None
target_model.generation_config.min_length   = None      # ← this is the culprit
target_model.generation_config.min_new_tokens = None


streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

inputs = tokenizer("The greatest", return_tensors="pt")

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
start = time.time()

thread.start()

print("Response:\n" + "-"*40)
for token in streamer:
    print(token, end="", flush=True)
    token_count += len(tokenizer.encode(token, add_special_tokens=False))

thread.join()

elapsed = time.time() - start
print(f"\n" + "-"*40)
print(f"Tokens generated : {token_count}")
print(f"Time elapsed     : {elapsed:.2f}s")
print(f"Throughput       : {token_count/elapsed:.1f} tokens/sec")

def get_tokens(target_model, draft_model, tokenizer, prompt):
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

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

    for token in streamer:
        print(token, end="", flush=True)
        token_count += len(tokenizer.encode(token, add_special_tokens=False))
