# 在银河 E8 上使用 Apple Music 7.0 + AM++

在银河E8上保留Apple Music 7.0原登录页面，使用AM++大屏双栏播放与歌词布局。

**当前交付版本：compat-39**，宿主Apple Music 7.0.0/1614、AM++ 1.6.8。[五分钟入门](docs/start-here.md) · [当前状态与待办](docs/known-issues.md)

Root启动拦截、大屏双栏、蜂窝许可、独立登录和包体压缩已有处理；39进一步放大车机播放器并保留原交互。版本变化见 [变更记录](CHANGELOG.md)，验证边界和当前待办见 [状态清单](docs/known-issues.md)。

## 按需要阅读

| 需求 | 文档 |
|---|---|
| 从头了解项目 | [五分钟入门](docs/start-here.md) |
| 查看01–39进展 | [迭代记录](docs/history.md) · [变更记录](CHANGELOG.md) |
| 继续维护功能 | [代码导读](docs/code-guide.md) · [构建说明](docs/build.md) |
| 查看当前问题及验证 | [状态清单](docs/known-issues.md) · [验证矩阵](docs/testing.md) |
| 查看36–39改动 | [播放器与歌单](docs/ui36-preview.md) · [均衡器入口](docs/ui37-hide-equalizer.md) · [日夜图标](docs/ui38-theme-icons.md) · [播放器放大](docs/ui39-player-enlarge.md) |
| 查看5.1研究方向 | [多声道输出调查](docs/audio-5.1-investigation.md)（尚未实现） |

## 代码与构建

[认证源码](src/com/e8/auth36) · [构建工具](tools) · [UI补丁](patches) · [历史UI源码](historical-src) · [测试](tests)

`auth36`是沿用的代码包名，不是交付版本号。构建工具支持34/35认证适配器增量更新、34→35压缩、35→36界面修复、36→37均衡器入口隐藏、37→38图标替换及38→39播放器模块放大。从官方干净包重建全部早期兼容改动尚未形成完整流水线。

```sh
python -m unittest discover -s tests -v
python tools/scan_repository.py
```

技术资料：[认证](docs/authentication.md) · [架构](docs/architecture.md) · [早期兼容](docs/early-compatibility.md) · [打包](docs/packaging.md) · [证据索引](docs/evidence.md) · [源码范围](docs/sources.md)。参与维护见 [CONTRIBUTING](CONTRIBUTING.md)，许可见 [LICENSE](LICENSE) 和 [第三方来源](THIRD_PARTY_NOTICES.md)。
