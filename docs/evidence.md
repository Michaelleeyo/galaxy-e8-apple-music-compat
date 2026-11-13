# 证据索引与来源

这里只保留手工审阅后的结论、原文件摘要与阶段信息。原始认证日志、截图、设备标识和请求正文不进Git。来源名是旧工作目录内的相对文件名，不要求其他维护者拥有原电脑目录。聊天用于补需求与顺序，动态断言尽量用文件佐证。

| 主题 | 本地原始来源（不入库） | 本仓库呈现 |
|---|---|---|
| Root/AM++/蜂窝 | 早期聊天“确认安卓版 Apple Music 是否检测 Root”；AppleMusic-v2-说明.txt；AppleMusic-AMpp-说明.txt；E8-cellular-fix-说明.txt；E8-4.9与7.0蜂窝判断对比.txt | early-compatibility.md |
| 08集成 | E8-integrated-report.txt | history.md 08 |
| 09–12 | E8-09实车反馈-取消码10.txt；E8-10实车图片-失败先于关闭.txt；E8-11-chain-diagnostic-report.txt；E8-12-error-diagnostic-report.txt | history.md / authentication.md |
| 13–16 | 13-模拟器真实登录成功-关键节点.txt；14-覆盖范围与日志导出.txt；15-验证结果与说明.txt；16实车结果-修复可行性与具体前提.txt | authentication.md |
| 17实车 | 17版车机Widevine系统直测结果.txt（CREATE阶段人工审阅） | 异常类型/NO_INIT，排除所有其他原文 |
| 18–29 | outputs目录同序号的核查/测试说明；work/no-widevine25、v1-runtime27 | history.md，保留受控与真实区分 |
| 30–33 | legacy-bridge30、package31、package32、package33的局部结果和构建记录 | 放弃方案及成功/失败边界 |
| 34 | package34/final-validation.json、mfa-boundary-review.json、最终源码、清安装登录记录 | release-manifest.json / 源码 / 测试矩阵 |
| 35 | package35/build-validation.json、signing-validation.json、runtime-extraction-validation.json、runtime-playback-validation.json、delivery-result.json | 发布哈希 / 压缩说明 / 测试矩阵 |

`evidence/source-index.json` 记录选定文件的SHA256，便于原电脑复核。摘要证明来源未变，不替代可公开复现的原始证据；外部读者无法仅凭哈希独立复核未公开实车日志。README明确保留这一限制。

本次仓库整理验证结果见 `evidence/repository-validation.json`：15项单元测试、Java/D8重新编译与34适配器DEX逐字节一致、真实34增量组装及无损压缩、34/35的SHA256/签名/对齐检查。私钥签名步骤未在整理阶段重新执行，未新增设备运行测试。
