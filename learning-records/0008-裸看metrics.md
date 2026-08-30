# 0008 裸看 /metrics(2.1)— 2026-08-30

- 学了:Prometheus 指标格式(指标名{标签} 值)、gauge/counter/histogram 三种记账类型
- 坑:教程里的 `vllm:gpu_cache_usage_perc` 在 vLLM 0.27 已改名为 `vllm:kv_cache_usage_perc`(2.3 才暴露)
- 结论:指标名以服务自己的 /metrics 为准
- 对应教学稿:lessons/0008
