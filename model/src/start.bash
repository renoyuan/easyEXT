# 启动命令（支持自动扩缩容）
GPU_COUNT=4 vllm serve main:llm_engine \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size $GPU_COUNT \
  --max-num-seqs 256          # 高并发优化[6](@ref)