# 第三方来源与范围

- Apple Music Android：Apple 的专有应用。本仓库仅记录版本绑定的接口与最小接入代码，不包含 APK、SO 或完整反编译源码。
- AM++：https://github.com/Zennmn/AM-plus-plus ，本地检出提交 `388164c74de63d05495d91f8a83164fb4772ca31`；交付使用模块 1.6.8。本地 LICENSE 为 GPL-3.0。上游发布：https://github.com/Zennmn/AM-plus-plus/releases/tag/v1.6.8 。本仓库没有复制该模块或整个上游源码。
- NPatch：https://github.com/7723mod/NPatch 。既有交付采用其嵌入结构；本仓库没有复制加载器或相关二进制。
- Android SDK / JDK / smali / Kotlin 运行时均为外部依赖。本仓库中的编译占位接口只用于解析宿主已有类型，不打进适配器 DEX，不提供运行时实现。

上游链接是历史来源记录，不代表当前仍可下载或已重新审核最新发布。公开本仓库与分发修改后的第三方 APK 是两件事；发布范围默认只含本仓库原创文件。

36界面工作新增AM++对应Kotlin源码补丁：`patches/amplusplus-1.6.8-car-player.patch`，遵循GPL-3.0-only，基于上列精确提交；完整许可文本在 `licenses/AMplusplus-GPL-3.0.txt`。模块二进制未上传。
