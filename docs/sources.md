# 公开源码与历史来源

可维护的原创源码和工具已经提交到本仓库，点击以下链接即可查看，不依赖原电脑：

| 内容 | 仓库文件 |
|---|---|
| 最终完成动作、真实账户转换与音乐授权 | [FinalAccount.java](../src/com/e8/auth36/FinalAccount.java) |
| 原协程交接适配 | [Completion.java](../src/com/e8/auth36/Completion.java) |
| 编译占位接口（不打入DEX） | [stubs](../stubs) |
| 最小原UI接入片段 | [final-action-hook.smali](../patches/final-action-hook.smali) |
| 编译 / 增量组装 / 压缩 / 核验 | [tools](../tools) |
| 早期原创横屏与菜单辅助 | [historical-src](../historical-src) |
| 工具测试 | [test_tools.py](../tests/test_tools.py) |

[evidence/source-index.json](../evidence/source-index.json) 原先的 `source` 字段表示历史取证文件名，容易误认为源码链接。现在明确改为 `privateSourceLabel`，并增加 `publicSummaryUrl` 指向可公开阅读的调查结论；这不是原始日志的公开副本。

原始认证日志含敏感信息，未发布；Apple 的完整反编译树、APK、SO也未发布。完整从干净官方包重建全部历史补丁的流水线尚未整理完成，不能用一个本地文件名或总结链接冒充已公开源码。可重建范围见 [构建说明](build.md)。
