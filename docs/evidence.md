# 证据索引与来源

当前交付链为34–38，版本大小与SHA256见 [发布清单](../evidence/release-manifest.json)，验证环境和结果见 [验证矩阵](testing.md)。

| 阶段 | 主要来源 | 项目记录 |
|---|---|---|
| 早期兼容 | 稳定v2、AM++集成、蜂窝修正及4.9/7.0对比说明 | [早期兼容](early-compatibility.md) |
| 09–17 | 登录诊断、认证链及Widevine系统直测结果 | [认证调查](authentication.md) · [历史](history.md) |
| 18–33 | 旧认证桥接、无Widevine实验及真实v1认证验证 | [历史](history.md) |
| 34 | 最终认证源码、清安装登录、MFA边界及静态验证 | [架构](architecture.md) · [导入验证](../evidence/repository-validation.json) |
| 35 | 压缩、签名、冷提取及播放验证；用户实车成功反馈 | [打包](packaging.md) · [验证矩阵](testing.md) |
| 36 | 同代码模拟器UI与ARM64内容核验 | [36验证](../evidence/ui36-validation.json) |
| 37 | 中文模拟器设置页与ARM64内容核验 | [37验证](../evidence/ui37-validation.json) |
| 38 | 图标原图、aapt2资源配置、签名/对齐及DEX/SO/模块比较 | [38验证](../evidence/ui38-validation.json) |

[source-index.json](../evidence/source-index.json)记录早期资料文件名与SHA256；privateSourceLabel为历史来源标签，publicSummaryUrl指向对应说明。历史文件摘要用于核对来源，当前功能结论按各版本验证记录判断。

repository-validation.json保留首次导入阶段的Java/D8编译、15项单元测试及34/35核验结果；后续发布验证按版本另记，不将历史实验结果套用到最新版。
