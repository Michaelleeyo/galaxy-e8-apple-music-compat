# 构建、签名与重现边界

## 可用工具

Python3.10+；JDK21（本地21.0.13+9）；Android平台 android-34/android.jar；现有 Android build-tools 中 d8.jar、zipalign、apksigner.jar；smali工具。全部由用户在仓库外提供。

```sh
python tools/build_adapter.py --jdk <JDK根目录> --android-jar <android.jar> --d8 <d8.jar> --out <仓库外构建目录>
python tools/patch_ui.py <外部ActionJSInterface.smali> --dry-run
python tools/patch_ui.py <外部ActionJSInterface.smali>
```

编译占位接口只进编译 classpath，不进 adapter.jar/DEX。smali 工具要求精确方法、寄存器可用且锚点唯一，重复应用拒绝；修改前生成备份。然后由现有合法自备基线流水线组装 classes.dex、classes5辅助DEX和classes6适配器，更新内层 origin.apk 及外层包。**本仓库尚未提供这个完整生产组装命令**，不能把编译 adapter 当作完成 ARM64 APK 构建。

## 基于34/35维护最终认证适配器

已提供真正可用的增量组装入口：编译 adapter 后，用可信34/35成品作为外部基线，仅替换其 origin.apk 中的 classes6.dex，再对齐和沿用私钥签名。此方式适合后续修改 FinalAccount/Completion，不要求旧4.9.5组件或旧电脑脚本。它不重建其他早期补丁。

```sh
python tools/update_adapter.py <自备34或35.apk> <编译输出/classes.dex> <新的候选.apk> --expected-input-sha <基线SHA256> --java <java> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <外部私钥> --alias <原别名> --expected-cert 113307a4a4974d875fff074b6f79ef557abef81aac845c145b88bc529c62eed3
```

E8_SIGN_PASSWORD/E8_KEY_PASSWORD与下文一致。工具校验输入哈希/签名、限制内层只变classes6.dex、外层只变origin.apk，并检查重新签名不改变有效内容。没有修改生产APK；本次用真实基线与重新编译DEX验证了无签名组装路径，没有调用私钥重新签名。编译出的相同DEX重组内层ZIP可能产生不同归档字节，属于预期，不声称最终APK哈希可复现。

涉及新UI Hook、AM++或其他DEX的功能不在此增量命令的允许范围；应单独设计补丁与回归。

## 34 → 35 无损重打包

自备34APK和原签名密钥，先核对清单 extractNativeLibs=true。密码由当前进程环境变量 E8_SIGN_PASSWORD 提供，不放在命令参数或文件里。交互输入可通过 Python getpass 或本地密码管理器注入子进程环境。仓库不读取旧脚本内硬编码密码。

```sh
python tools/repack.py <34.apk> <35-new.apk> --extract-native-libs-confirmed --java <java> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <外部私钥> --alias <原别名> --expected-cert 113307a4a4974d875fff074b6f79ef557abef81aac845c145b88bc529c62eed3
python tools/verify_apk.py <34.apk> <35-new.apk>
```

输出路径不能与输入相同且不能已存在；unsigned/aligned 临时包独立生成；重新签名后核对**输入和输出**证书与指定摘要，内容集合/哈希匹配，校验签名与对齐后才交付。私钥/密钥库密码默认相同；可用 E8_KEY_PASSWORD 单独指定密钥密码。工具只转发环境变量名，不输出密码值。

## 当前缺口

早期稳定 Root/布局/蜂窝/菜单、辅助诊断DEX和AM++修改流水线来自现有16基线，不把这批完整 Apple 反编译树放进Git。后续应逐项整理成自有最小补丁和基线输入校验，再实现完整组装。当前提供最终Java源码及其原文件哈希、34/35发布哈希、工具测试，保证读者清楚哪些步骤能独立重现。

## 发布前检查

确认 ARM64 与本地变体的 adapter 字节一致；原生库及模块哈希不变；zipalign/apksigner 验证；完整功能回归按 docs/testing.md；新增产物放仓库外，更新证据清单。签名摘要不是私钥，可以公开；无法取得原私钥时不能声称可覆盖已安装版本。

## 35 → 36界面修复

此流程完全使用自备35基线及外部smali工具，不依赖原电脑工作目录，也不修改认证适配器。输出工作目录必须尚不存在。

```sh
python tools/prepare_car_ui.py --baseline <35.apk> --expected-input-sha 4e2b203ff2d8af8c6b989cd1a166310667efc0e1ce51326325fd29eb9dd3fc63 --work <外部工作目录> --java <java> --baksmali <baksmali.jar> --smali <smali.jar>
python tools/build_car_ui.py --baseline <35.apk> --expected-input-sha 4e2b203ff2d8af8c6b989cd1a166310667efc0e1ce51326325fd29eb9dd3fc63 --host-dex <工作目录/host-classes2.dex> --module-dex <工作目录/module-classes2.dex> --output <36.apk> --java <java> --zipalign <zipalign> --apksigner <apksigner.jar> --keystore <外部私钥> --alias <原别名>
```

密码使用前述环境变量。工具校验真实35基线摘要及证书，修改歌单按钮的位图密度与AM++播放器布局后，重新签名模块及外层包，并限制有效条目差异范围。对应AM++源码补丁及验证范围见 [36修改说明](ui36-preview.md)。输出仍为宿主7.0.0/1614，可沿用原证书覆盖安装；36是本项目交付序号。
