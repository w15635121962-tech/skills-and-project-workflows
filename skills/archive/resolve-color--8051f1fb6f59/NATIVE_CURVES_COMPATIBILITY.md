# v12 原生曲线兼容层说明

上游：samuelgursky/davinci-resolve-mcp，固定提交 `90eba8cdf4df333beb4ce41fe0ab198b8fa7d125`，MIT。原厂 `drx-generator.js` 未修改；新增副本 `上游源码/resolve-advanced/vendor/drx-codec/drx-generator-local-compat.js`。

## 本地变化及证据

- 当前 R21 真实117镜与上游 `resolve-advanced/test/fixtures/custom-curve-y.drx` 的四个YRGB样条都包含5个内部控制点，四通道同x、同y；加隐式(0,0)和末(1,1)形成7点，可解释为两段三次Bezier。
- 两份原生样板中间锚的左右相邻控制点呈共线切线。先前把内部点全部视为自由anchor的判断过早，已修正。
- 原生metadata四项 `0x860000BB/BD/BE/BF` 都为 `{F2:2}`，不是上游编码器假设的点数。具体语义未完全解码，沿用观测值2。
- 根代理报告：旧版3内部点及通道不等点数结构在独立R21工程仍崩溃；四通道同形、5内部点、meta2的最小cage已原生应用/导出成功。本代理未操作Resolve；这不等于所有复杂曲线已获原生验证。
- 副本新增显式格式约定，禁止无格式声明的裸数组。anchors输入经PCHIP单调Hermite转Bezier，输出3n+1完整点数（仅内部控制点传给编码器，即5/8/11/...），各通道共用x网格；全局限制共享切线以保单调与C1连续，固定(0,0)/(1,1)，不重复写边界。
- 只有Y输入时默认四通道跟随Y；明确给RGB输入时默认独立，其余通道使用同网格identity。可用 `linkYRGB:false` 明确选择独立Y。
- 离线验证：生成后4通道meta2、严格递增x、同控制网格、链接Y一致、未指定RGB的identity、错误裸列表/3点伪cage/移动白端点拒绝；另100组固定随机种子单调anchor验证点数、单调控制高度及C1切线通过。原生图像与mask仍由根代理验证。

## 输入

```js
{
  customCurvesFormat: 'anchors',
  customCurves: { y: [{x:0.5, y:0.51}] }
}
```

或已知原生Bezier内部控制点，不能再添加0/1边界：

```js
{
  customCurvesFormat: 'bezier-cage',
  customCurves: { y: [
    {x:1/6,y:1/6}, {x:1/3,y:1/3+0.006}, {x:0.5,y:0.51},
    {x:2/3,y:2/3+0.006}, {x:5/6,y:5/6}
  ] }
}
```

## HSL限定器轴校准

上游 `buildQualifierParams` 的 `hueCenter` 使用Resolve原生0–100刻度，并非可直接代入普通HSV百分比。根代理于当前R21真实样板实测：center33.333显著选中肤色(face delta6.19/navy delta0.034)，center0主要选藏蓝(navy delta4.82)。记录见 `native_hue_selection_calibration.json`。当前局部近似 `nativeHue≈(HSVHue/3.6+25)%100` 只反映本次样板，不是适用于所有颜色、版本与色彩空间的严格通式；实际key应再看mask和真实输出。

## 保留已有调色

对v11提取的238项Body，本代理只读核验175项是单节点、63项无节点。175项仅有默认节点F10，166项Sony LUT字符串都位于节点F9，没有发现节点外OFX/LUT负载。当前项目可用原F9逐字节移植保留原调色；无节点项应单独排除。此结论不适用于任意复杂节点图、OFX、节点sizing或多节点工程。普通 `drx-merger.js` 由语义params重建，无法证明保留原LUT/CDL/曲线/其他工具负载和拓扑。

不得将降白点描述为恢复原本不存在的画面纹理。所有生产应用必须保留本地可恢复版本、逐点真实图像比对，避免将通过codec自解析误认为Resolve已接受。
