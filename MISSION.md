# MISSION

**一句话目标:** 以 Agent 开发者的身份,把 LLM 推理层学到"能部署、能调参、能排障"的程度。

**验收标准(学完后能做到):**
1. 在 GPU 机器上用 vLLM 部署开源模型,暴露 OpenAI 兼容 API
2. 看懂启动日志:显存预算、KV cache 容量、最大并发数
3. 会调 `--max-model-len` / `--gpu-memory-utilization` / `--max-num-seqs` / 前缀缓存
4. 会用 Prometheus + Grafana 看 TTFT/TPOT/QPS/KV cache 使用率
5. 会用 `vllm bench serve` 压测并找到并发拐点
6. 能讲清 KV cache、continuous batching、PD 分离、量化取舍

**明确不学:** CUDA kernel 实现、推理引擎源码改造、omni-flow 内部实现。

详见 [学习计划.md](./学习计划.md) 与 [路线图.md](./路线图.md)。
