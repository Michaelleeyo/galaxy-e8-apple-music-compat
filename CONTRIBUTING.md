# 维护流程

1. 记录问题对应的项目版本、ABI/API、入口、复现步骤及期望行为。
2. 根据影响范围修改认证、宿主UI、AM++模块或资源；升级宿主时重新核对混淆方法及参数。
3. 运行单元测试、仓库扫描和对应构建核验。设备验证写清版本、环境、步骤与结果。
4. 同步更新CHANGELOG、验证矩阵、发布清单及当前状态，已完成的问题移出待办。
5. 审阅变更后提交并推送。项目版本使用compat-38这样的交付序号，宿主版本单独记录。

```sh
python -m unittest discover -s tests -v
python tools/scan_repository.py
git push origin main
```

[构建说明](docs/build.md) · [当前状态](docs/known-issues.md) · [验证矩阵](docs/testing.md)
