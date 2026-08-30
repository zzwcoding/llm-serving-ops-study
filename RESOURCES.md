# RESOURCES(信源清单)

## 知识类(官方文档/论文)

- vLLM 官方文档: https://docs.vllm.ai/ (参数、监控指标、Prometheus 示例)
- vLLM 论文(PagedAttention): SOSP '23
- HuggingFace 镜像站: https://hf-mirror.com (国内下模型)
- NVIDIA Container Toolkit 文档: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/

## 智慧类(社区/实践)

- AutoDL / gpuhome 等租卡平台的使用习惯(关机不计费、数据盘 vs 系统盘)
- 国内镜像条件反射: PyPI → mirrors.aliyun.com/pypi/simple;HF → hf-mirror.com + HF_HUB_DISABLE_XET=1;Docker Hub → docker.1ms.run 等

## 拓展阅读(暂不深入)

- [vllm-project/production-stack](https://github.com/vllm-project/production-stack) K8s 生产形态(Phase 5)
- [meituan-longcat/omni-flow](https://github.com/meituan-longcat/omni-flow) 多模态编排(知道定位即可)
