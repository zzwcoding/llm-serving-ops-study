# 0002 Docker 权限边界(0.3~0.4)— 2026-08-23

- 学了:Docker + NVIDIA Container Toolkit 安装;排查三层权限拒止
- 卡在:实例是无特权容器(tini + seccomp=2 + 无 CAP_SYS_ADMIN),unshare 被封 → Docker 不可用,无解
- 结论:计划调整——Phase 1 直装 vLLM;Docker/K8s 概念挪 Mac;Phase 5 再评估。顺带配好了 registry-mirrors
- 诊断三连:cat /proc/1/comm / unshare -m true / grep Seccomp /proc/self/status
- 对应教学稿:lessons/0002
