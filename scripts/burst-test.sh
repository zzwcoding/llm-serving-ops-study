#!/bin/bash
# 并发压测小脚本:同时发 N 个请求,观察 Grafana 曲线
# 用法: ./burst-test.sh [并发数] [max_tokens]
# 例:   ./burst-test.sh 30 400
N=${1:-30}
MAXTOK=${2:-400}

echo "发送 $N 个并发请求(max_tokens=$MAXTOK)..."
START=$(date +%s)

for i in $(seq 1 "$N"); do
  curl -s http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"Qwen/Qwen2.5-1.5B-Instruct\",\"messages\":[{\"role\":\"user\",\"content\":\"讲一个300字的故事\"}],\"max_tokens\":$MAXTOK}" \
    -o /dev/null &
done
wait

echo "全部完成,总耗时 $(( $(date +%s) - START )) 秒"
