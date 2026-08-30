# 0008 裸看 /metrics(阶段 2.1)

## 三问(阶段动机)

```
✅ 1.服务跑通  ✅ 2.1 裸看指标(你在这里)  ⬜ 2.2 Prometheus  ⬜ 2.3 Grafana  ⬜ 2.4 对照实验
```

- **这阶段干嘛的:** 不装任何新软件,先看一眼 vLLM 天生自带的"体检报告" `/metrics`。
- **什么需求逼的:** 监控不是凭空来的——所有监控系统(Prometheus/Grafana)吃的都是这碗原材料。先看懂原材料,后面工具只是给它化妆。
- **解决了什么麻烦:** 以后没有 Grafana 的裸机上,一条 curl 也能读出服务健康状况。

## 全链路一览

```
vLLM 服务(一边干活一边记账:收了几个请求、每个等了多久、缓存用了几成)
   │  账本摊开在 http://localhost:8000/metrics
   ▼
curl 看一眼 = 手动查账
(下一步:Prometheus 每 15 秒自动来抄一次账)
```

## 跟着数据走

`curl -s http://localhost:8000/metrics` 出来几百行,每行长这样:

```
vllm:kv_cache_usage_perc{model_name="Qwen/Qwen2.5-1.5B-Instruct"} 0.00012
```

拆成三块:`指标名{标签=筛选条件} 数值`。像超市小票:品名{分店=xx} 金额。

重点找四类指标(在输出里 grep 它们):

| 指标 | 记账方式 | 大白话 |
|---|---|---|
| `vllm:kv_cache_usage_perc` | 当前值 | **KV 缓存车位占了几成**(0~1),逼近 1 就是请求要排队了 |
| `vllm:num_requests_running` / `waiting` | 当前值 | 正在接待几个 / 排队几个请求 |
| `vllm:prompt_tokens_total` / `generation_tokens_total` | 只增不减的累计数 | 累计收了多少字、吐了多少字(算吞吐用) |
| `vllm:time_to_first_token_seconds` | 分桶统计(histogram) | **TTFT 分布**:多少请求的首字在 0.1s 内、多少在 1s 内… |

**histogram(分桶统计)是个新东西**:它不记"平均值",而是把每次耗时扔进
`le="0.1"` `le="0.5"` `le="1"` 这样的桶里计数。像考试统计:60分以下几人、
80分以下几人。好处:能看出"大部分快、个别慢"的分布,平均值会掩盖尾巴。

## 新技术点四要素

**Prometheus 指标格式(监控界的通用账本格式)**
- 名字:Prometheus exposition format,文本协议
- 作用:任何软件只要开一个 `/metrics` 端口按这个格式写账,就能被整个监控生态接纳——vLLM、MySQL、nginx 都这么干
- 参数:三种记账类型——**gauge**(温度型,可升可降,如缓存使用率)、**counter**(里程表型,只增不减,如累计 token 数)、**histogram**(分桶型,看分布,如 TTFT)
- 用法:本项目挂载点——vLLM 的 `http://localhost:8000/metrics`

## 关键顿悟

- **监控 = 记账 + 抄表 + 画图。** vLLM 只负责记账(/metrics);抄表和画图是下两步的事。
- **分类型看指标。** 温度(gauge)、里程表(counter)、分桶(histogram)——问法不同:"现在多少"、"涨多快"、"分布怎样"。
- **指标是免费的。** 它们随服务自带,零成本;不看不白不看,看了才知道服务在喊什么。
