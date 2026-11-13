# 源码与工具范围

| 内容 | 项目文件 |
|---|---|
| 当前认证完成动作及账户转换 | [FinalAccount.java](../src/com/e8/auth36/FinalAccount.java) |
| 协程交接 | [Completion.java](../src/com/e8/auth36/Completion.java) |
| 编译占位接口 | [stubs](../stubs)（仅编译使用） |
| 原UI完成动作接入 | [final-action-hook.smali](../patches/final-action-hook.smali) |
| AM++播放器源码改动 | [Kotlin补丁](../patches/amplusplus-1.6.8-car-player.patch) |
| 早期横屏与菜单辅助 | [historical-src](../historical-src) |
| 编译、认证增量更新、压缩 | build_adapter.py、update_adapter.py、repack.py |
| 36播放器/歌单UI | prepare_car_ui.py、patch_car_ui.py、build_car_ui.py |
| 37均衡器入口 | hide_equalizer.py |
| 38日夜图标 | build_theme_icons.py |
| 39播放器放大完整增量构建 | build_ui39.py |
| 自动检查 | [tests](../tests) · [tools](../tools) |

构建工具操作指定宿主基线，完整支持范围见 [构建说明](build.md)。Root与蜂窝已有严格补丁工具，38→39增量构建已经闭合；AM++原始嵌入引用上游项目，不在本仓库重复维护。从官方干净包到全部历史兼容内容仍不是单命令构建。认证接口的混淆名称绑定7.0.0/1614。
