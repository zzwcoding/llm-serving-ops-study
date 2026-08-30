# 0005 调通 OpenAI 接口(1.3)— 2026-08-30

- 学了:curl 调 `/v1/models` 和 `/v1/chat/completions`;响应字段 content/usage/finish_reason
- 观察:1.5B 模型答非所问(把 LLM KV cache 答成通用 KV 存储)——小模型质量的直观体感
- 技巧:中文转义用 `python3 -m json.tool --no-ensure-ascii`
- 对应教学稿:lessons/0005
