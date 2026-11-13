# 银河 E8 · Apple Music 7.0 + AM++ 兼容维护

本仓库保存本地兼容补丁源码、构建工具、验证方法，以及从早期 Root 拦截到第 35 轮交付的工程记录。目标是保留 Apple Music 7.0 的界面和真实认证，提供 AM++ 大屏双栏体验。

**当前基线：34 为独立认证实现；35 在相同有效内容上进行无损 ZIP 压缩。** 不需要安装 4.9.5 或外部认证组件。这里没有 Apple APK、SO、账户数据或签名私钥，也不是 Apple Music 完整源码。

| 项目 | 状态 |
|---|---|
| 宿主 | Apple Music 7.0.0 / 1614，AM++ 1.6.8 |
| 目标设备 | 银河 E8，Android 12L / API 32，ARM64，2376×936，可用区域 2376×880 |
| 登录实现 | 原 7.0 IdMS 登录/二次验证页面 → 完成动作 → 同版本保留的 StoreAPI → 真实账户转换与音乐授权 |
| 34 独立性 | 清理模拟器中的 Apple Music 与旧组件后，仅安装本地等代码版本，真实登录成功 |
| 35 大小 | 135.13 MiB，比 34 的 185.52 MiB 减少约 27.16% |
| 验证边界 | ARM64 包做静态/签名检查；运行验证使用 x86_64 同代码本地包。没有把模拟器验证写成实车通过 |

## 阅读入口

- [完整迭代记录 01–35](docs/history.md)：问题、证据、决策、结果和未解决项。
- [早期 Root、AM++ 与无网络](docs/early-compatibility.md)。
- [认证调查与最终实现](docs/authentication.md)，[架构与接入点](docs/architecture.md)。
- [构建与签名](docs/build.md)，[验证矩阵](docs/testing.md)，[35 版压缩](docs/packaging.md)。
- [已知问题](docs/known-issues.md)，[后续维护](CONTRIBUTING.md)，[证据索引](docs/evidence.md)。

## 本地快速检查

需要 Python 3.10+、Git；纯工具测试不需要 Android SDK、账户或联网。

```sh
python -m unittest discover -s tests -v
python tools/scan_repository.py
```

早期原创横屏/DPI与菜单辅助代码保存在 `historical-src`，仅作来源明确的维护参考。

Java 适配器位于 `src/com/e8/auth36`。`auth36` 是既有运行时包名，**不是第 36 版**。旧工作目录路径与包名不一致，本次仅规范源码目录，未改动 Java 内容。

本仓库支持重新编译适配器并基于自备34/35包增量重建认证候选、对外部 smali 执行严格接入补丁，以及把自备的 34 APK 压缩成等内容包。**目前没有宣称从官方干净 APK 一键完整重建 34**：早期 Root/布局/诊断基线的生产流水线仍需整理，详见构建文档。

35 与 34 包名、versionCode 和证书相同，可以相互覆盖；“并行”指交付文件同时保留，不是两个应用同时安装。证书摘要和发布哈希见 [release-manifest.json](evidence/release-manifest.json)。

## 项目边界

不伪造身份、签名、令牌或服务器成功；不关闭 TLS 校验，不强制 FPDI Basic，不跨版本移植 SO。需要有效 Apple Music 订阅；服务器策略变化可能影响兼容性。

当前为本地整理导入，历史迭代不等同于 35 次独立 Git 提交。未自动推送 GitHub。授权范围见 [LICENSE](LICENSE) 与 [第三方说明](THIRD_PARTY_NOTICES.md)。
