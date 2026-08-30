# 0005 调通 OpenAI 兼容接口(阶段 1.3)

## 三问(阶段动机)

```
✅ 0.环境  ✅ 1.1 起服务  ✅ 1.2 读日志  ✅ 1.3 调接口(你在这里)  ⬜ 1.4 盯显卡  ⬜ 1.5 prefill/decode  ⬜ 2.监控 ...
```

- **这阶段干嘛的:** 服务跑起来了,现在真正"用"它——用 curl 发一个请求,拿到模型的回答。
- **什么需求逼的:** 你的 Agent 程序将来就是这样调模型的;今天用 curl 手动模拟一遍程序的行为。
- **解决了什么麻烦:** 接口调通 = 部署真正闭环;同时理解"OpenAI 兼容"这个行业标准长什么样。

## 全链路一览

```
你的 curl(扮演一个客户端程序)
   │  HTTP POST 到 8000 端口,带着 JSON 格式的"问题"
   ▼
vLLM 的 API 服务(把文字切成 token → 喂给引擎)
   │
   ▼
引擎推理(显存里算矩阵,逐 token 生成回答)
   │
   ▼
JSON 格式的"回答"返回给你
```

## 跟着数据走

发出去的 JSON(请求):

```json
{
  "model": "Qwen/Qwen2.5-1.5B-Instruct",
  "messages": [{"role": "user", "content": "用一句话解释什么是KV缓存"}]
}
```

收到的 JSON(回答)里三个字段最关键:

- `choices[0].message.content` —— 模型的回答文本
- `usage.prompt_tokens` / `completion_tokens` —— **计费单**:你的问题多少 token、回答多少 token。API 按这个收钱,推理层按这个算负载
- `choices[0].finish_reason` —— "stop"= 正常说完;"length"= 被最大长度截断(看到它要警惕)

## 新技术点四要素

**OpenAI 兼容 API(行业普通话)**
- 名字:OpenAI-compatible API;两个核心端点 `/v1/models`(花名册)、`/v1/chat/completions`(对话)
- 作用:OpenAI 的接口格式成了行业事实标准,所有推理引擎(vLLM/SGLang)都讲这口"普通话"。好处:你的 Agent 代码换底层引擎/换模型,**一行都不用改**,只改地址
- 参数:请求体里 `model`(用哪个模型)、`messages`(对话历史,role 分 system/user/assistant)、`max_tokens`(回答长度上限)
- 用法:本项目挂载点——curl 直连 `http://localhost:8000`;将来你的 LangGraph Agent 把 `base_url` 指到这里即可

**curl(命令行发 HTTP 请求)**
- 参数:`-s` 安静模式(不显示进度)、`-X POST` 请求方法、`-H` 请求头、`-d` 请求体
- 用法:`curl -s http://localhost:8000/v1/models | python3 -m json.tool`(后者把 JSON 排版好看)

## 关键顿悟

- **"OpenAI 兼容"= 可替换性。** 这就是为什么学 vLLM 部署有意义——部署完,所有会调 OpenAI 的工具直接可用。
- **usage 字段是钱。** prompt_tokens + completion_tokens 就是这个请求的成本明细,运维和计费都盯着它。
- **finish_reason 是排障信号。** 回答被截断时先看它,而不是怀疑模型笨。
