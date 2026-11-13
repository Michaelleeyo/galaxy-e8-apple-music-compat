# 构建说明

## 可用工具

本页按版本列出构建入口；功能说明和运行验证见对应版本文档。

Python3.10+；JDK21（本地21.0.13+9）；Android平台 android-34/android.jar；现有 Android build-tools 中 d8.jar、zipalign、apksigner.jar；smali工具；38图标构建另需APKEditor 1.4.9。

```sh
python tools/build_adapter.py --jdk <JDK根目录> --android-jar <android.jar> --d8 <d8.jar> --out <仓库外构建目录>
python tools/patch_ui.py <外部ActionJSInterface.smali> --dry-run
python tools/patch_ui.py <外部ActionJSInterface.smali>
```

编译占位接口只进入classpath，不打入adapter.jar/DEX。build_adapter.py生成适配器DEX，随后使用下方update_adapter.py组装到已有基线。patch_ui.py用于原UI接入点的smali修改，校验锚点并生成备份；现有34及后续成品已含该接入，不重复应用。

## 基于34/35维护最终认证适配器

编译adapter后，以34/35成品为基线，仅替换origin.apk中的classes6.dex，再对齐并签名。用于修改FinalAccount/Completion；早期兼容改动保持基线内容。

```sh
python tools/update_adapter.py <自备34或35.apk> <编译输出/classes.dex> <新的候选.apk> --expected-input-sha <基线SHA256> --java <java> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <keystore路径> --alias <原别名> --expected-cert 113307a4a4974d875fff074b6f79ef557abef81aac845c145b88bc529c62eed3
```

工具校验输入哈希/签名，限制内层只变classes6.dex、外层只变origin.apk，并检查签名不改变有效内容。ZIP重组可能改变归档字节，不保证最终APK哈希复现。

涉及新UI Hook、AM++或其他DEX的功能不在此增量命令的允许范围；应单独设计补丁与回归。

## 34 → 35 无损重打包

以34APK为输入，先核对清单extractNativeLibs=true。签名参数中的keystore与alias使用基线证书对应配置。签名密码由环境变量E8_SIGN_PASSWORD提供，密钥密码不同时另设E8_KEY_PASSWORD。

```sh
python tools/repack.py <34.apk> <35-new.apk> --extract-native-libs-confirmed --java <java> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <keystore路径> --alias <原别名> --expected-cert 113307a4a4974d875fff074b6f79ef557abef81aac845c145b88bc529c62eed3
python tools/verify_apk.py <34.apk> <35-new.apk>
```

输出文件必须尚不存在。重打包后检查输入/输出证书、非签名内容集合与哈希，以及签名和16KB对齐。

## 支持的构建链

已有34/35认证增量更新、34→35压缩、35→36界面修复、36→37均衡器入口隐藏和37→38图标替换工具。早期Root/蜂窝等兼容接入仍依赖既有基线，尚不支持从官方干净包完整重建。各阶段输入哈希见发布清单。

## 发布前检查

按预期修改范围比较宿主、模块、资源及原生库；检查ABI、签名和对齐；更新发布清单与版本验证记录。运行回归见 [验证矩阵](testing.md)。

## 35 → 36界面修复

以35为基线，准备并组装宿主及模块UI DEX。认证适配器保持不变。工作目录必须尚不存在。

```sh
python tools/prepare_car_ui.py --baseline <35.apk> --expected-input-sha 4e2b203ff2d8af8c6b989cd1a166310667efc0e1ce51326325fd29eb9dd3fc63 --work <外部工作目录> --java <java> --baksmali <baksmali.jar> --smali <smali.jar>
python tools/build_car_ui.py --baseline <35.apk> --expected-input-sha 4e2b203ff2d8af8c6b989cd1a166310667efc0e1ce51326325fd29eb9dd3fc63 --host-dex <工作目录/host-classes2.dex> --module-dex <工作目录/module-classes2.dex> --output <36.apk> --java <java> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <keystore路径> --alias <原别名>
```

密码使用前述环境变量。工具校验真实35基线摘要及证书，修改歌单按钮的位图密度与AM++播放器布局后，重新签名模块及外层包，并限制有效条目差异范围。对应AM++源码补丁及验证范围见 [36修改说明](ui36-preview.md)。输出仍为宿主7.0.0/1614，可沿用原证书覆盖安装；36是本项目交付序号。

## 36 → 37隐藏均衡器入口

```sh
python tools/hide_equalizer.py --baseline <36.apk> --expected-input-sha 1d3ad9daeb18c39f96f12b0e68cdcea8f6de4fe2e4829ed676eb82861cb4412e --work <新的工作目录> --output <37.apk> --java <java> --baksmali <baksmali.jar> --smali <smali.jar> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <keystore路径> --alias <原别名>
```

仅修改宿主classes3.dex中的设置列表，详情见 [37说明](ui37-hide-equalizer.md)。

## 37 → 38深浅色启动图标

使用外部APKEditor及两张182×104 PNG构建，命令、差异范围和实车验证边界见 [38图标说明](ui38-theme-icons.md)。签名配置与其他增量工具相同。
