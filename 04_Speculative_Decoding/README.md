# Speculative Decoding

Speculative decoding is an optimization technique for inference that makes educated guesses about future tokens while generating the current token, all within a single forward pass. It incorporates a verification mechanism to ensure the correctness of these speculated tokens, thereby guaranteeing that the overall output of speculative decoding is identical to that of vanilla decoding. Optimizing the cost of inference of large language models (LLMs) is arguably one of the most critical factors in reducing the cost of generative AI and increasing its adoption. Towards this goal, various inference optimization techniques are available, including custom kernels, dynamic batching of input requests, and quantization of large models.

## Architecture

![Speculative Decoding](Assets/speculative decoding.png)

## Run and Test the app

```sh
streamlit run app.py
```

## Requirements

- streamlit
- transformers < 5.0


## References

- [PyTorch - A Hitchhiker’s Guide to Speculative Decoding](https://pytorch.org/blog/hitchhikers-guide-speculative-decoding/)
- [Nvidia](https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference/)
- [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/pdf/2211.17192)