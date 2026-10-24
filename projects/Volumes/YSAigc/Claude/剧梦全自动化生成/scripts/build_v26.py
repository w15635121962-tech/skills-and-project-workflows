#!/usr/bin/env python3
"""V2.6 episode md: expand fixed blocks, verify structure, emit platform payload.
Usage: build_v26.py src.md out_full.md out_platform.json"""
import json, math, re, sys
FIXED = "写实照片级、超写实质感、真人实拍电影剧照，采用 ARRI Alexa 65 摄影机拍摄，85mm 定焦镜头（Prime Lens），光圈 T1.8，竖版 9:16 画幅（Aspect Ratio），180 度快门角（180-Degree Shutter Angle），浅景深（Shallow Depth of Field），柔和奶油般散景（Bokeh），细腻胶片颗粒质感（Film Grain）。真实皮肤纹理，哑光质感（Matte, Non-Glossy），清晰可见毛孔与细微皮肤纹理起伏，真实次表面散射（Subsurface Scattering / SSS）光影效果，肤色只呈现真实皮肤下轻微血色，不形成发光红脸；皮肤高光仅允许在鼻梁、颧骨等自然出油区域出现极细微、局部的自然反光，不得形成大面积油亮色块或蜡质反光层；皮肤色调在面部各区域必须均匀一致，不得因参考图融合产生局部色差、色块拼接感或纹理断层。真人质感眼眸只保留真实环境反射，禁止眼球自发光（No Self-Illuminating Eyes）。真实布料垂坠动态褶皱，真实接触投影（Contact Shadow），光束中漂浮细微尘埃丁达尔效果（Tyndall Effect）。"
SKIN = "人物皮肤须保持细腻、紧致、哑光通透的真实质感，毛孔与皮肤纹理清晰可辨但不夸张、不放大为颗粒感；皮肤表面禁止出现以下任一状态——粗糙颗粒感、明显油光、不健康的浮油质感、过度磨皮导致的塑料感／蜡感、皮肤纹理消失导致的假面感、局部色调不均或色块拼接感、五官边缘与皮肤融合产生的模糊塌陷。人物面部主光须打在面部 45°，禁止大面积阴影糊脸；夜戏、暗房、逆光场景一律补柔光保证五官可辨。若本组镜头基于多张参考图（垫图）生成，须额外保证：不同参考图来源的皮肤质感、色温、纹理清晰度在最终画面中完全统一，不得保留原图各自的皮肤处理痕迹或产生融合接缝。"
TEARS = "泪水质感：泪液为清澈透明的真实液体，先在下眼睑边缘积聚成一道细薄水线，再沿面部自然曲率缓慢滑落，路径受颧骨与鼻翼走向约束、不走直线；泪珠只折射环境光形成细小高光，不发光、不呈油亮反光；泪痕滑过处皮肤保留极浅的湿润光泽并随后自然变淡；眼眶与鼻尖仅呈极轻微泛红，睫毛根部可被打湿成细簇；禁止泪水成串、成股或过量，禁止泪痕呈白色条带、胶状或蜡质。"
FIELDS = ["叙事任务（Narrative Task）","镜头","画面","视觉引导（Visual Flow）","微表演（Micro-Performance）","对白反应（Dialogue Reaction）","人物背景融合（Subject-Background Integration）","光影细节（Lighting Detail）","音频（Audio）","运动强度（Motion Intensity）","负面提示词（Negative Prompt）"]
RISKY = re.compile(r"blood|pleasure|thrust|naked|kill|death|suicide|gun|knife", re.I)
PLATFORM_FIX = [("轻微血色", "轻微红润")]
BANNED = ["高潮", "欲望", "血", "裸", "情欲", "性行为", "刀片", "自杀", "枪", "尸"]

def main(src, out_md, out_json):
    s = open(src, encoding="utf-8").read()
    full = s.replace("{{FIXED}}", FIXED).replace("{{SKIN}}", SKIN).replace("{{TEARS}}", TEARS)
    open(out_md, "w", encoding="utf-8").write(full)
    ep = re.search(r"## (EP\d+)", full).group(1)
    errs, out = [], []
    for g in re.split(r"\n(?=### G\d+｜)", full)[1:]:
        title = g.splitlines()[0][4:].strip()
        gid = title.split("｜")[0]
        declared = float(re.search(r"([\d.]+) 秒", title).group(1))
        nshots_decl = int(re.search(r"(\d+) 镜", title).group(1))
        parts = re.split(r"\n(?=【shot )", g)
        head = [l for l in parts[0].splitlines()[1:] if l.strip()]
        for k in ["【资产引用】", "【组头｜固定画质词】", "【组头｜皮肤强制要求】", "【组头｜光影基调】", "【组头｜节奏结构】", "【组头｜景别/角度循环】", "【组头｜视觉动线】"]:
            if not any(l.startswith(k) for l in head): errs.append(f"{gid} 缺 {k}")
        assets = re.findall(r"@([^\s—]+?\.(?:png|jpg))", next((l for l in head if l.startswith("【资产引用】")), ""))
        if not any("场景" in l for l in head if l.startswith("【资产引用】")): errs.append(f"{gid} 无场景图")
        tot, shots_out = 0, []
        for p in parts[1:]:
            lines = [l for l in p.splitlines() if l.strip() and not l.startswith("### ")]
            hdr = lines[0]; sid = re.search(r"shot (\d+)", hdr).group(1)
            d = float(re.search(r"｜([\d.]+)s】", hdr).group(1)); tot += d
            if not (1.0 <= d <= 6.0): errs.append(f"shot {sid} 时长 {d} 超出 1–6s")
            names = [l.split("：", 1)[0] for l in lines[1:]]
            if names != FIELDS: errs.append(f"shot {sid} 字段顺序/缺失: {names}")
            for l in lines[1:]:
                if not l.startswith("音频") and re.search(r"[\"“][A-Za-z][^\"”]{3,}[\"”]", l): errs.append(f"shot {sid} 非音频字段含英文台词")
                if l.startswith("镜头："):
                    for key in ["景别", "焦段", "机位高度", "轴线", "构图比例", "景深", "视线偏移", "前景遮挡"]:
                        if key not in l: errs.append(f"shot {sid} 镜头缺 {key}")
                if l.startswith("对白反应") and len(l) < 40: errs.append(f"shot {sid} 对白反应过短")
            shots_out.append((sid, lines))
        if abs(tot - declared) > 0.01: errs.append(f"{gid} 时长和 {tot} ≠ 声明 {declared}")
        if len(shots_out) != nshots_decl: errs.append(f"{gid} 镜数 {len(shots_out)} ≠ {nshots_decl}")
        # platform payload
        paras = [f"{ep}｜{title}｜输出{max(4, math.ceil(tot))}秒｜480P｜九梦2.5Pro｜9:16"] + head
        for sid, lines in shots_out:
            for l in lines:
                if l.startswith("音频") and RISKY.search(l):
                    l = re.sub(r"英文旁白（[^）]*）：\"[^\"]*\"", "英文旁白：本句后期配音，本镜不生成旁白人声", l)
                paras.append(l)
        txt = "\n".join(paras)
        for a, b in PLATFORM_FIX: txt = txt.replace(a, b)
        paras = txt.split("\n")
        hits = [w for w in BANNED if w in txt]
        if hits: errs.append(f"{gid} 平台版含敏感词 {hits}")
        out.append({"episode": ep, "group": gid, "title": title, "duration": max(4, math.ceil(tot)), "exact": tot,
                    "shots": [int(x) for x, _ in shots_out], "assets": assets, "paragraphs": paras, "chars": len(txt)})
    json.dump(out, open(out_json, "w", encoding="utf-8"), ensure_ascii=False)
    for o in out: print(o["group"], o["exact"], "s →", o["duration"], "s", "shots", o["shots"], o["chars"], "字", o["assets"])
    print("总时长", sum(o["exact"] for o in out), "输出", sum(o["duration"] for o in out))
    print("ERRORS:" if errs else "校验通过：无错误", *errs, sep="\n")
if __name__ == "__main__": main(*sys.argv[1:4])
