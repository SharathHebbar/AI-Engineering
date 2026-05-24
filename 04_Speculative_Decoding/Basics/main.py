import json
import torch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from contextlib import asynccontextmanager

from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import threading

import logging

app = FastAPI()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

TARGET_MODEL_ID = "HuggingFaceTB/SmolLM2-360M-Instruct"
DRAFT_MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"


tokenizer = None
target_model = None
draft_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global tokenizer, target_model, draft_model

    logging.info("Loading target model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(TARGET_MODEL_ID)
    target_model = AutoModelForCausalLM.from_pretrained(
        TARGET_MODEL_ID,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    target_model.generation_config.max_length = None
    target_model.generation_config.min_length = None
    target_model.generation_config.min_new_tokens = None

    logging.info("Loading draft model...")
    draft_model = AutoModelForCausalLM.from_pretrained(
        DRAFT_MODEL_ID,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    target_model.eval()
    draft_model.eval()

    logging.info("Models loaded successfully. Starting server.")
    yield


app = FastAPI(title="Speculative Decoding API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/generate")
async def generate(prompt: str, max_new_tokens: int = 200):
    async def event_generator():
        inputs = tokenizer(prompt, return_tensors="pt")

        streamer = TextIteratorStreamer(
            tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        thread = threading.Thread(
            target=target_model.generate,
            kwargs=dict(
                **inputs,
                assistant_model=draft_model,
                max_new_tokens=max_new_tokens,
                streamer=streamer,
                min_length=0,
                min_new_tokens=None,
                do_sample=False,
                use_cache=True,
            )
        )

        thread.start()

        for token in streamer:

            yield {"data": json.dumps({"token": token})}

        thread.join()

        yield {"data": json.dumps({"done": True})}
    
    return EventSourceResponse(event_generator())



@app.get("/")
def read_root():
    
    return {"Hello": "World"}