#!/bin/bash

# 适配 2080Ti (11GB 显存) 的 vLLM 启动脚本
# 使用方法: ./run_vllm_2080ti.sh <模型名>
# 例如: ./run_vllm_2080ti.sh Qwen/Qwen1.5-1.8B-Chat

MODEL_NAME=${1:-Qwen/Qwen1.5-1.8B-Chat}

python -m vllm.entrypoints.openai.api_server \
  --model $MODEL_NAME \
  --dtype float16 \
  --max-model-len 2048 \
  --max-num-seqs 1 \
  --gpu-memory-utilization 0.85 \
  --disable-log-stats
