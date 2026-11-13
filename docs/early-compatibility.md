# 早期三项问题：Root、AM++、启动无网络

## Root 拦截

最初目标源于新版 Apple Music 在 Root 环境中的启动限制。早期尝试原生 Hook/Pine；在 x86_64 模拟器转译 ARM64 时遇到兼容性崩溃，不能把它归为 Apple 认证失败。稳定 v2 移除 Pine 与相关 ART Hook，直接针对 7.0 的 `AppleMusicApplication.i()Z` 检测入口修改 DEX；横屏和 DPI 通过 Activity 生命周期设置。这个修改属于已有基线，不是“所有官方 DEX 未改”。

Android 11 模拟器曾确认 su 仍存在而不再弹 Root 拦截、连续冷启动可进入在线页面。它只证明这项入口处理，不等于后面的登录/DRM 已解决。

### 可审计补丁

仓库现在提供 [patch_early_compatibility.py](../tools/patch_early_compatibility.py)。它只接受用户自行提取的Apple Music 7.0.0/1614 `classes2.dex` smali目录，并严格要求目标方法同时包含原辅助检测 `Lwg/h;->h()Z` 和 `/system/bin/su`。匹配后仅让这个应用自己的 `AppleMusicApplication.i()Z` 返回 `false`；不修改系统Root状态、不隐藏`su`，也不改变认证、TLS、DRM或原生库加载错误处理。

审计时使用的官方ARM64 base split SHA256为 `41c12111ef6fdac9ed4b61ad38e48b7dd33bc65adbedf1dd1459b1bce31a8cec`，其中原始 `classes2.dex` SHA256为 `d7b3a4efd88c6c03b57c908e01d295b12da635f551679f07af15137e0b93e81f`。不同渠道或版本必须重新核对；工具遇到锚点漂移会停止。

## AM++ 集成和大屏布局

v2 先保留原生平板布局，之后才合入 AM++ 1.6.8 原生双栏，采用 NPatch 嵌入结构；模块支持 ARM64，通用测试包另外包含 x86_64。由此必须分清：宿主、内嵌 origin.apk、AM++ 模块及加载器的 ABI 与资源。

随后处理无损徽标/播放按钮重叠、队列触摸区域落到底部导航区、旧式 MENU 键的右侧备用锚点，并隐藏设置中的 AM++ 入口。触摸菜单在模拟器原来就在右侧，因此备用锚点通过不等于实车菜单问题全部消失。此段为早期改动记录；36播放器修复及当前菜单/歌词状态见 [状态清单](known-issues.md)。未增加杜比解码或声道能力。

## 打开软件显示无网络

用户最初表现为“蜂窝数据已关闭”；忘记密码网页能打开，不能判断整机断网。对应版本设置中没有可用开关，不能让用户反复寻找不存在的入口。

代码对比：7.0 的 `MediaPlaybackPreferences.getUseCellularData(Context)` 同时判断蜂窝可用性和 `key_use_cellular_data`；播放端 `isCellularDataEnabled()` 读取另一许可。已有候选把两个入口改为允许，不伪造系统 SIM 或网络状态。API32 模拟器关闭 Wi-Fi、使用 CELLULAR 后能加载首页及保留账户播放，但没有先复现同一实车故障，不能把这个测试说成根因闭环。

同一补丁工具的 `--cellular-policy` 只处理上述两个7.0入口，并分别校验 `isCellularAvailable()/key_use_cellular_data` 与 `cellular_data_enabled/@Keep` 锚点。它不Hook `ConnectivityManager`、不伪造传输类型、不开放系统权限，也不绕过账号、订阅或服务器校验。

### 使用方式

先从用户自备的对应APK提取目标 `classes2.dex`。对于NPatch结构，应提取 `assets/npatch/origin.apk` 内的 `classes2.dex`，而不是盲目修改外层同名DEX。然后执行：

```powershell
java -jar <baksmali.jar> d <classes2.dex> -o <work/classes2-smali>

python tools/patch_early_compatibility.py <work/classes2-smali> `
  --root-gate --cellular-policy --dry-run

python tools/patch_early_compatibility.py <work/classes2-smali> `
  --root-gate --cellular-policy

java -jar <smali.jar> a <work/classes2-smali> -o <work/classes2-patched.dex>
```

正式写入前先运行 `--dry-run`。写入时每个原文件会保存为 `.smali.bak`；若备份已存在，工具拒绝覆盖。重新组装后仍需按 [打包说明](packaging.md) 替换正确的内层DEX、重新签名内外层APK并检查有效文件差异。仓库不含Apple APK、私钥或通用Root隐藏工具。

用户提供的 4.9.5 大屏包在公共蜂窝入口 `I6.e.k(Context)` 直接返回允许，播放许可仍读取设置。7.0 的改动比该对照更广；没有官方干净 4.9.5 对比，不能断言那个行为来自 Apple 或大屏作者。

## 来源

依据早期聊天“确认安卓版 Apple Music 是否检测 Root”、稳定 v2 说明、AM++ 集成说明、蜂窝修正说明与 4.9/7.0 对比记录重建。这些工作早于08，后续独立认证及实车成功记录见 [迭代记录](history.md)。
