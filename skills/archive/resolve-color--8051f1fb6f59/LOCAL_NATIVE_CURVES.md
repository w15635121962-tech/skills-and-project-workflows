# 本机原生曲线与二级工具

GitHub来源：samuelgursky/davinci-resolve-mcp，固定commit 90eba8cdf4df333beb4ce41fe0ab198b8fa7d125，MIT。原技能正文和上游codec逐字节保留；本地兼容版另存，不冒充上游原文。安装49份codec/参数/样板文件；没有新增常驻MCP服务。

运行：`node scripts/native-secondary-grade.cjs request.json`。输入包含 `baseBody` 或 `baseDrx`，新增 `nodes`（每项label/params），`output`，可选 `label`/`report`。只支持原图零或一个静态节点；原单节点F9完整保留，新节点串联其后。不得用于复杂多节点/OFX/关键帧图的无损复制。

自定义曲线必须声明 `params.customCurvesFormat: 'bezier-cage'` 或 `'anchors'`，并给 `params.customCurves: {y:[{x,y}],r:...,g:...,b:...}`。仅给Y默认四通道联动。bezier-cage只传5/8/11/...个内部控制点；编码器供给边界。裸点列、重复端点、不单调结构均有拒绝保护。anchors转Bezier的数学结构已离线检查，使用新形状前仍须独立原生测试。

真实肤色/背景选色用 `params.qualifier`；不能把HSV百分比直接当成Resolve HSL限定器的色相或饱和度。当前R21实测肤色中心约33.5，极低饱和人脸的satLow须通过画面校准（本次1.5，有软边）；这些不是所有素材通用参数。

应用前保留原项目/时间线/调色版本，先看原生画面，在隔离工程验证；生成DRX之后，通过官方 `Graph.ApplyGradeFromDRX(path,0)` 应用到明确目标。应用会替换节点图，不能当成append API。必须首中尾实帧核对，旁路新增节点复核旧grade保留；仅显示节点/仅离线parse通过不等于有效。

详见 NATIVE_CURVES_COMPATIBILITY.md、NATIVE_CODEC_PROVENANCE.json、LOCAL_ADAPTER_PROVENANCE.json。
