# llm-serving-ops-study

> LLM 推理层部署运维的实战学习项目:面向 Agent 应用开发者,目标"能部署、能调参、能排障"。
> 按 learn-by-rebuild 教学法分阶段推进,每阶段有教学稿、实验记录和 git 留痕。

## 学习目标

在 GPU 机器上用 vLLM 部署开源模型,并具备:

- 看懂启动日志:显存预算、KV cache 容量、最大并发数
- 调优关键参数:`--max-model-len` / `--gpu-memory-utilization` / `--max-num-seqs` / 前缀缓存
- 用 Prometheus + Grafana 监控 TTFT / TPOT / 吞吐 / KV 缓存水位
- 用 `vllm bench serve` 压测,做容量规划("能扛多少人、何时扩容")

明确不学:CUDA kernel 实现、推理引擎源码改造(见 [MISSION.md](./MISSION.md))。

## 进度

```
✅ Phase 0 环境准备     租 GPU、nvidia-smi、SSH 免密、Docker 权限边界诊断
✅ Phase 1 跑起服务     装 vLLM、精读启动日志、调接口、prefill/decode
✅ Phase 2 监控         /metrics → Prometheus → Grafana → 30 并发对照实验
✅ Phase 3 调参         上下文长度 / 显存水位 / 限流排队 / 前缀缓存(全部有数据验证)
⬜ Phase 4 压测         vllm bench serve 并发阶梯,找拐点,出压测报告
⬜ Phase 5 量化与 K8s   FP8/AWQ 对比;production-stack 生产形态
```

当前状态和各阶段结论见 [路线图.md](./路线图.md)(续学先读它)。

## 目录结构

```
├── MISSION.md            学习目标与验收标准
├── 学习计划.md           总纲(能力目标、资源清单)
├── 路线图.md             细分路线 + 进度总览
├── RESOURCES.md          信源清单(文档/镜像/参考项目)
├── NOTES.md              教学偏好记录
├── lessons/              每阶段教学稿(大白话五节模板:三问/全链路/数据流/四要素/顿悟)
├── learning-records/     每阶段进度记录(学了什么/卡在哪/结论)
├── notes/                早期笔记与翻车实录、Phase 4/5 报告
├── configs/              Grafana dashboard JSON 等
└── scripts/              burst-test.sh 压测脚本等
```

## 环境

- 学习机:租用的 GPU 云实例(RTX 4090 24G,Ubuntu 22.04;注意:无特权容器,不支持嵌套 Docker)
- 栈:vLLM 0.27 + Prometheus 3.14 + Grafana 13.2(全部二进制直装)
- 模型:Qwen2.5-1.5B-Instruct(小模型练手,流程与 7B 一致)

## 关键结论速览(实验数据)

| 实验 | 数据 |
|---|---|
| 显存预算 | 24G = 权重 3G + KV cache 18.2G + 杂项 2G;并发 = KV 总量 ÷ 单请求预算 |
| 砍上下文 32K→4K | 最大并发 20.8x → 159.9x(零成本 7.7 倍) |
| 显存水位 0.92→0.6 | KV 缓存 18.2→10.7 GiB,并发同比缩水 |
| 限流 max-num-seqs=8 | running 顶死 8、waiting 排队、TTFT 含排队时间(排队是保护不是故障) |
| 前缀缓存 | 共享长 system prompt 显著降 TTFT;不变内容必须放 prompt 最前 |
