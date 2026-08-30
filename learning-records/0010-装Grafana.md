# 0010 装 Grafana(2.3)— 2026-08-30

- 学了:Grafana 只画不存;SSH 端口转发(ssh -L 3000:localhost:3000 gpu -N);数据源+面板+Dashboard 三概念
- 坑(三连):① 误选 Amazon Prometheus 数据源(EC2 IMDS 报错);② localhost 解析到 IPv6 ::1 被拒 → 用 127.0.0.1;③ 忘选面板类型(no data)
- 坑④:Grafana v13.2 换 dashboard JSON v2 schema,老格式导入被拒 → 改用"复制面板"绕过;configs/vllm-dashboard.json 留待改写
- 结论:v13.2.0 二进制,~/work/grafana/;第一条曲线 vllm:kv_cache_usage_perc
- 对应教学稿:lessons/0010
