# 第三方来源与范围

- Apple Music Android：Apple 的专有应用。本仓库仅记录版本绑定的接口与最小接入代码，不包含 APK、SO 或完整反编译源码。
- AM++：https://github.com/Zennmn/AM-plus-plus ，本地检出提交 `388164c74de63d05495d91f8a83164fb4772ca31`；交付使用模块 1.6.8。本地 LICENSE 为 GPL-3.0。上游发布：https://github.com/Zennmn/AM-plus-plus/releases/tag/v1.6.8 。播放器差异以最小Kotlin补丁维护。
- NPatch：https://github.com/7723mod/NPatch 。既有交付采用其嵌入结构。
- Android SDK / JDK / smali / Kotlin 运行时均为外部依赖。本仓库中的编译占位接口只用于解析宿主已有类型，不打进适配器 DEX，不提供运行时实现。

APKEditor 1.4.9 / ARSCLib 1.3.9用于38版资源解码与重建；aapt2用于资源配置检查。以上为构建时使用的版本，非上游最新版本声明。

36界面工作新增AM++对应Kotlin源码补丁：`patches/amplusplus-1.6.8-car-player.patch`，遵循GPL-3.0-only，基于上列精确提交；完整许可文本在 `licenses/AMplusplus-GPL-3.0.txt`。
