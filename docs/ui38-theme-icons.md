# 38：随系统深浅色选择启动图标

基于37版，使用用户提供的两张182×104 PNG：浅色白底黑音符，深色黑底白音符。图像不裁切、不缩放，保留原始字节；桌面最终显示尺寸由车机启动器决定。

## 实现与构建

新增 [build_theme_icons.py](../tools/build_theme_icons.py)，限定37版基线SHA256及原签名。使用外部APKEditor 1.4.9 / ARSCLib 1.3.9解码和重建资源；删除mipmap中ic_launcher及ic_launcher_round原有的adaptive和各密度候选，改为nodpi与night-nodpi的PNG，避免旧anydpi候选覆盖新图片。

仅从重建包取resources.arsc及四份PNG，写入原外层包及assets/npatch/origin.apk。原清单、DEX、SO、AM++模块和其他资源逐字节保留；旧图标文件可能仍留在ZIP内，但不再由这两个资源ID引用。

```sh
python tools/build_theme_icons.py --baseline <37.apk> --light <白底黑音符.png> --dark <黑底白音符.png> --work <新的外部工作目录> --output <38.apk> --java <java> --apkeditor <APKEditor.jar> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <keystore路径> --alias <原别名>
```

输入包括37APK、两张PNG和APKEditor；签名配置见 [构建说明](build.md)。版本仍为7.0.0/1614，38为交付序号。重建工具版本及ZIP压缩差异可能影响输出哈希，不保证逐字节复现。

## 验证与边界

[交付验证记录](../evidence/ui38-validation.json)对应已交付38版：

- aapt2资源转储确认ic_launcher与ic_launcher_round均只包含nodpi及night-nodpi候选。
- 新PNG与两张输入原图逐字节一致，尺寸182×104。
- 原签名证书、apksigner与16KB zipalign校验通过。
- 外层仅改资源表、origin.apk并加入四份PNG；内层仅改资源表并加入四份PNG。原有DEX、SO和模块内容不变。

Android资源系统按night配置选图，但未在车机上验证桌面缓存失效、即时刷新或启动器裁切行为。若桌面缓存图标，系统模式变化后可能要重新进入或重启桌面才能看到变化。本轮未新增登录、MFA、播放或音频输出回归。
