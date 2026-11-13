# 在银河 E8 上使用 Apple Music 7.0 + AM++

这个项目记录了我们如何让 Apple Music 7.0 在银河 E8 上保留原登录界面，并使用 AM++ 的大屏双栏布局，以及过程中遇到的问题和解决办法。

**第一次看，先读 [五分钟看懂这个项目](docs/start-here.md)。不需要先翻源码或35轮日志。**

## 现在做到哪了

- 早期处理了 Root 启动拦截，合入 AM++，调整横屏布局，并处理应用的蜂窝许可判断。
- 34 版保留 7.0 的登录和二次验证页面，最后通过 **7.0 自带的另一条真实认证接口** 完成账户交接，不依赖安装 4.9.5。
- 35 版保持34的有效内容，只压缩安装包：185.52 MiB → 135.13 MiB。
- 已完成同代码模拟器真实登录与播放相关验证；最终34/35的ARM64实车回归、34新触发二次验证、长期续期仍需验证，详见 [已知问题](docs/known-issues.md)。

## 按你想做的事来读

| 你想了解什么 | 打开这里 |
|---|---|
| 整个项目在做什么，为什么这样解决 | **[五分钟入门](docs/start-here.md)** |
| 当时一步步遇到了什么，哪些方案放弃了 | [01–35迭代经过](docs/history.md) |
| 接着修功能或页面Bug，从哪个文件入手 | **[维护与代码导读](docs/code-guide.md)** |
| 怎样编译、修改认证适配器、重新打包 | [构建说明](docs/build.md) |
| 哪些通过了测试，哪些还不能保证 | [验证记录](docs/testing.md) · [已知问题](docs/known-issues.md) |

## 代码在哪

[认证源码](src/com/e8/auth36) · [构建工具](tools) · [早期横屏/菜单源码](historical-src) · [测试](tests)

`auth36` 是沿用的代码包名，不代表有第36版。

仓库包含原创补丁和工具，没有完整Apple源码、APK、SO、账户数据或私钥。目前能基于自备34/35包重建认证适配器；**从干净官方包重建所有早期改动的流水线还没全部整理完**。修改页面与AM++也需要补相应生产补丁，不能只改这里的Java认证文件。

## 开发检查

```sh
python -m unittest discover -s tests -v
python tools/scan_repository.py
```

技术细节按需查阅：[认证调查](docs/authentication.md) · [架构](docs/architecture.md) · [Root/AM++/蜂窝](docs/early-compatibility.md) · [压缩](docs/packaging.md) · [证据来源](docs/evidence.md) · [源码范围](docs/sources.md)。

提交问题请参考 [维护流程](CONTRIBUTING.md)，不要上传账号、密码、验证码或认证令牌。不伪造身份或成功结果，不关闭TLS校验。项目版本绑定Apple Music7.0.0/1614、AM++1.6.8；需要真实订阅，服务器变化可能影响兼容性。许可范围见 [LICENSE](LICENSE) 和 [第三方说明](THIRD_PARTY_NOTICES.md)。
