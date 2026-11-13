# Apple Music原生多声道输出为独立5.1：研究起点

目标：使用Apple Music原生多声道/Atmos内容输出独立5.1，不采用立体声上混冒充原始多声道。此文是研究记录，不是已实现功能。当前39仅调整播放器尺寸，沿用既有音频实现。

## 已有材料

- 用户在早期聊天明确反馈：E8支持WANOS，网易云/酷狗5.1音源可以使用。这是用户实车反馈，尚未用本项目的逐声道点名和输出链路快照独立验证。
- 实车为Android12L/API32、ARM64。早期Android11/2500×935是旧假设及模拟器配置，不能当作车机参数。
- 早期制作过CarAudioCheck1.0/1.1及CarCompatibilityCheck1.2。归档中找到的完整CarAudioCheck报告标注为模拟器，未找到实车完整音频路由报告。
- 早期实验曾在模拟器强制显示Atmos开关，但无对应解码/直通能力，未验证真实Atmos。实验已回退，不进入当前生产认证或UI补丁。
- 37版仅隐藏均衡器入口，不新增多声道解码、声道转换、WANOS接入或功放路由。

## 7.0.0/1614代码核查记录

当前7.0.0/1614保留AudioDeviceCapabilities.isDolbyAtmosAvailable，检查audio/eac3-joc。其内部b方法查MediaCodecList.findDecoderForFormat，构造48kHz/2声道格式；或者按该编码、48kHz及0xC立体声掩码检查AudioTrack.isDirectPlaybackSupported，部分调用还检查ExoPlayer AudioCapabilities。

这只是能力入口，不能据此证明取得原始多声道音轨、成功解码，或送出独立6声道。这里的2声道探测参数也不能推断所有实际Atmos播放被固定降为2声道；运行时轨道/解码器输出必须另查。

旧版与新版先前均发现EAC3/JOC相关检测，未发现足以证明4.9.5大屏版额外实现E8专用5.1路由的证据。静态字符串或库数量均不作为声道成功依据。

## 先验证输出，再选择应用修改

1. 实车使用现成已知网易云/酷狗5.1内容，保存AudioFlinger与AudioPolicy快照，确认实际格式、声道、设备地址、direct/offload及效果链，区分公开路径与厂商专用路径。
2. 用自有无DRM的6声道PCM测试素材逐声道点名，确认是否6路独立，还是途中混成立体声后由车机扩展。应用声明6声道或全部喇叭响都不足以完成该验证。
3. 在Apple Music播放有Atmos版本的内容，检查实际选择轨道的MIME、解码器、输出声道和最终路由。依据第一处差异决定处理轨道选择、合法解码、PCM路由或厂商接口。

ADB只读快照示例（Mac/Linux/Windows终端均可调整输出文件名）：

```sh
adb -s <实车序列号> shell dumpsys media.audio_flinger > known-surround-audioflinger.txt
adb -s <实车序列号> shell dumpsys media.audio_policy > known-surround-audiopolicy.txt
adb -s <实车序列号> shell dumpsys audio > known-surround-audio.txt
```

换Apple Music后以applemusic作为文件名前缀再保存一次。对比两组实际输出格式、声道掩码及设备路由；若普通权限不足，可用实车已有root读取。

## 待确认

- 实车是否提供兼容JOC解码或可用的编码直通；WANOS本身不等同于该能力。
- 第三方进程能否使用6声道PCM输出，以及实际音箱映射。
- 车载功放/厂商HAL的接入是否需要专用服务、权限或接口。
- Apple Music实际请求到哪种音轨、是否被解码/混音阶段下混。

Android音频策略配置定义输出格式、channelMasks及路由；声明与实际输出要分开验证。参考：[AOSP音频策略](https://source.android.com/docs/core/audio/implement-policy)、[AudioTrack](https://developer.android.com/reference/android/media/AudioTrack)。
