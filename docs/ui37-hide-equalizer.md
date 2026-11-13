# 37：隐藏应用内均衡器入口

在36界面修复之上，只移除Apple Music设置中的均衡器条目。系统MusicFX、音频处理、既有EQ参数、音量平衡及车机音效均不由本补丁修改。

## 实现

7.0.0/1614的SettingsViewModel.getAudioCategory构造音频设置列表，其中均衡器使用资源equalizer/equalizer_description。该列表原来就允许可选条目为null，随后过滤空条目。

最小改动是在该列表的均衡器位置放入已有null寄存器，替代均衡器行对象；不修改点击处理器、偏好键、音效能力判断或DSP。

[hide_equalizer.py](../tools/hide_equalizer.py) 会校验输入哈希、原签名及方法结构，反汇编对应基线classes3.dex、实施这一个位置替换并组装，确认内层只变classes3.dex、外层只变origin.apk，然后沿用原证书签名。

```sh
python tools/hide_equalizer.py --baseline <36-ARM64.apk> --expected-input-sha 1d3ad9daeb18c39f96f12b0e68cdcea8f6de4fe2e4829ed676eb82861cb4412e --work <新的外部工作目录> --output <37.apk> --java <java> --baksmali <baksmali.jar> --smali <smali.jar> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <keystore路径> --alias <原别名>
```

密码仍通过E8_SIGN_PASSWORD/E8_KEY_PASSWORD环境变量提供，参见 [构建说明](build.md)。ARM64和本地模拟器基线分别反汇编和打补丁，保留各自其他代码；不把模拟器整份classes3.dex覆盖到ARM64包。

## 运行验证

可见窗口的API32/x86_64模拟器，系统首选语言zh-Hans-CN：

- 覆盖安装保留应用数据；中文设置不再显示均衡器，也没有留空行。
- 音频质量、交叉渐入渐出、音量平衡条目存在。
- 音频质量子页可打开；返回设置后均衡器仍隐藏。
- 本轮未操作音效开关、频段或其他设置值。

实车37运行、新登录/MFA、听觉输出和长期续期不在本次验证范围。36的菜单跑左问题仍留待实车ADB排查。

ARM64交付包140,735,031字节，沿用原签名；[静态与运行验证](../evidence/ui37-validation.json)记录了模块/原生库/其他宿主DEX保持不变，ARM64设置模型与实测本地模型一致。
