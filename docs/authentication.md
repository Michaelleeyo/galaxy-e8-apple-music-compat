# 认证调查：从关闭弹框到真实兼容路径

## 最初误区与收敛

实车输入后弹框关闭，应用没有崩溃。仅观察 UI 不能区分取消、未发起、未记录或原生失败；13 的实际日志出现 `ExpectedDataBuffer.hasValue=false` 和 WebContainer ResolveFailed，随后 Failure/DefaultFailure，证明关闭是失败结果后的行为。`ExpectedDataBuffer.error()` 是结果读取接口，不能覆盖其底层所有创建路径，也不是唯一故障点。

GrandSlam ec=0 和 HTTP200 都只表示各自阶段，不能当成最终账户成功。14 日志大量 URLPatternMatcher 17/7 错误消耗展开额度；15 把重复错误合并，关键认证保留独立预算，采集会话原异常并支持完整导出。这比继续拍最后几行更能定位。

## 15/16 的实车证据

`AMSIDMSAuthenticationCompleteAction → FPDI Full → Widevine challenge 失败 → FPDIInit=0 → setup HTTP500 → 保存 sb.g / 关闭会话 → null → Empty signature → JNI500 → Accounts112 → WebContainer1524`。

16 明确 `httpStatus=500, serviceCode=null`，退出在 HTTP 检查，**尚未执行成功响应后的 FPDISetup**。原生 init 返回 0 不代表服务器接受设备证明。1328 字节经 Base64/JSON 变成 1772 字符/1788 字节，与原编码器及 Gson 32 组受控测试一致；未发现所检查 Java 封装截断，仍不能证明 SO 内证明有效。

Media3 DummyExoMediaDrm 的 openSession 固定抛 MediaDrmException；正常 FrameworkMediaDrm 创建失败被捕获后选择 Dummy。17 独立系统直测终于取得 CREATE 原异常：`android.media.UnsupportedSchemeException: Failed to instantiate drm object: NO_INIT`，附 No supported hal instance found；OPEN_SESSION/CHALLENGE 跳过。此为当时该系统调用结果，不表示车机永久不支持，也不直接解释服务端 500 的全部原因。

## 放弃无依据降级，验证旧式原装协议

静态核实 Full 条件/规则、签名装饰器与旧账户接入，未找到对该动作已验证的服务端 Basic 兼容开关。未通过强制 Basic、空签名或跨版本 SO 来制造成功。4.9.5 在同车机真实播放是事实，但用户卸载旧包后装 7.0，且签名不同，不能假设共享数据迁移成立。

25 的无 Widevine 模拟器是隔离受控环境；26 完成 MFA 后复现外层 112/500/1524，但没有 15/16 全部内部节点。并非严格只改变 Widevine 的成功/失败 A/B。

27–29 实际到达 `POST https://auth.itunes.apple.com/auth/v1/native`，原装管线与业务解析正常。早期请求 HTTP200、-20101、无账户，只能证明该次拒绝；原装 `otp/1.5/finish` 是机器 provisioning，不能视为用户二次认证。某轮有效 Anisette 仍被拒绝，因此不能把 -45061 认定唯一原因。随后凭据核对也发现密码阶段 -22406，修正输入后原旧版真实 MFA 成功。这里不保留任何输入值。

## 最终突破：不是把 4.9.5 塞进 7.0

30/31 先证明旧引擎真实登录、账户转换和播放授权可联通，但外部组件与额外 UI 不符合需求。32 自动跳转仍改变前半流程，33 同 APK 隔离旧引擎也带来旧 UI/依赖负担，均放弃。

34 保持 7.0 原账号/密码/MFA 页面，等原 IdMS 产生真实 **passwordEquivalentToken（PET）**，仅处理精确完成动作。由 7.0 自带 `Gb.b.a(user, PET, 0, continuation)` 调用原 StoreAPI；这次真实返回 status=0、有账户和密码令牌，说明早期原密码尝试失败不能推断接口已停用。

接着校验 activeAccount 与用户匹配、XToken 存在，经原 `e7.e.getAccounts` 转为 AMS 账户；原 provider 保存账户、更新 WebClientContext；原 B9 音乐令牌 provider 真实授权成功后，才用 `makeJSAccountFromAccount` 返回 `{"account": genuineAccount}`。不生成或编造认证数据，不修改 StoreAPI 的签名/TLS/bag 管线。

这条路径避免在该完成动作使用失败的 AMS Full 实现，不等于移除所有后续 Full 调用。续期/重新认证仍需长期实测，服务器策略也可能改变。
