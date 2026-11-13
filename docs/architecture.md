# 34/35 架构与版本绑定

```mermaid
flowchart TD
  UI[原 7.0 浏览 / 登录 / MFA 页面] --> IDMS[真实 IdMS 完成与 PET]
  IDMS --> G{精确完成动作与条件匹配?}
  G -->|否| O[原 dispatcher]
  G -->|是| A[自定义完成动作 adapter]
  A --> S[原 7.0 StoreAPI /auth/v1/native]
  S --> V{真实 status0 / 账户 / token / active匹配}
  V -->|失败| F[真实异常回传]
  V -->|成功| C[原账户转换与 provider保存]
  C --> W[原 WebClientContext.setAccount]
  W --> M[原音乐授权 provider]
  M --> R[真实 JS account 交回原 UI]
```

源码：[FinalAccount.java](../src/com/e8/auth36/FinalAccount.java) 和 [Completion.java](../src/com/e8/auth36/Completion.java)。对原 ActionJSInterface.postMessage 只插入 route 调用；见 [接入补丁](../patches/final-action-hook.smali) 与 [严格补丁工具](../tools/patch_ui.py)。没有复制整份 Apple smali。

route 只接受 run、精确 AMSIDMSAuthenticationCompleteAction、真实 username/PET、makeCurrentAccount/canMakeAccountActive 为真、ignoreAccountConversion 为假且无额外 HTTP headers。其他请求原样交回原流程；注册失败也回退原流程，不能把回退等同于兼容认证成功。

运行时注册 E8AuthenticationCompleteAction，保留原 dispatcher、事件封装和 IWebAction 合约。工作线程等待原协程；调用 hi.c.intercepted 保留调用方调度语义；90 秒等待超时是真实失败。不会把 UI 看起来消失当成结果。

`Gb.b`、`e7.e`、`B9.h/f`、`hi.c` 等都是 **7.0.0/1614 混淆版本绑定**，反射方法选择依赖参数类型；升级必须逐个核实。`Completion` 的 hi/fi/Kotlin 编译占位定义不能打包成宿主类型替代物。

34 内嵌 classes2/3/4 未变；classes.dex 加入 UI route，classes5 是关闭诊断弹窗的既有辅助 DEX，classes6 为最终 adapter。后两项不能仅用本仓库 Java 编译替代整个基线。AM++ 模块与音频原生库保持既有字节。
