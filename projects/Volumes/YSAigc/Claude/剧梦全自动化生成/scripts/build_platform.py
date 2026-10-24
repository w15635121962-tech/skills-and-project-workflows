#!/usr/bin/env python3
"""Convert an episode prompt-group md into platform-ready 分镜 payloads (JSON).
Usage: build_platform.py EPxx.md assets.json out.json
assets.json: {"S24-A": ["Aria.png","Hades.png","Blackwood别墅卧室.png"], ...}
"""
import json, math, re, sys

FIXED = "写实照片级、超写实质感、真人实拍电影剧照，采用 ARRI Alexa 65 摄影机拍摄，85mm 定焦镜头（Prime Lens），光圈 T1.8，竖版 9:16 画幅（Aspect Ratio），180 度快门角（180-Degree Shutter Angle），浅景深（Shallow Depth of Field），柔和奶油般散景（Bokeh），细腻胶片颗粒质感（Film Grain）。真实皮肤纹理，哑光质感（Matte, Non-Glossy），清晰可见毛孔与细微皮肤纹理起伏，真实次表面散射（Subsurface Scattering / SSS）光影效果，肤色只呈现真实皮肤下轻微红润，不形成发光红脸；皮肤高光仅允许在鼻梁、颧骨等自然出油区域出现极细微、局部的自然反光，不得形成大面积油亮色块或蜡质反光层；皮肤色调在面部各区域必须均匀一致，不得因参考图融合产生局部色差、色块拼接感或纹理断层。真人质感眼眸只保留真实环境反射，禁止眼球自发光（No Self-Illuminating Eyes）。真实布料垂坠动态褶皱，真实接触投影（Contact Shadow），光束中漂浮细微尘埃丁达尔效果（Tyndall Effect）。"
MUST = "人物皮肤须保持细腻、紧致、哑光通透的真实质感，毛孔与皮肤纹理清晰可辨但不夸张、不放大为颗粒感；皮肤表面禁止出现以下任一状态——粗糙颗粒感、明显油光、不健康的浮油质感、过度磨皮导致的塑料感／蜡感、皮肤纹理消失导致的假面感、局部色调不均或色块拼接感、五官边缘与皮肤融合产生的模糊塌陷。人物面部主光须打在面部 45°，禁止大面积阴影糊脸；夜戏、暗房、逆光场景一律补柔光保证五官可辨。若本组镜头基于多张参考图（垫图）生成，须额外保证：不同参考图来源的皮肤质感、色温、纹理清晰度在最终画面中完全统一，不得保留原图各自的皮肤处理痕迹或产生融合接缝。"
NEG = "禁止静止起手与静止收尾；禁止双脚并拢立正、双手对称垂放；禁止面无表情只用眼神演戏；禁止眼神无落点、瞳孔涣散、眼球发光、直视镜头；禁止东亚式内敛克制的身体语言（含蓄掩口笑、身体内收、鞠躬式道歉）；禁止群体同步动作与表情克隆；禁止多指、断指、手臂穿模、五官塌陷、面部畸变；禁止画面出现字幕、水印、logo、分屏；禁止非说话者产生口型。"
RISKY_VO = re.compile(r"blood|pleasure|thrust|naked|sex|kill|die|dead|death|suicide|gun|knife", re.I)
BANNED = ["血", "裸", "情欲", "性行为", "性爱", "刀片", "自杀", "枪", "尸"]
MAXDUR = 30

def clean(t):
    t = t.replace("**", "").strip()
    t = t.replace("固定画质词：见〇节，照抄。", "固定画质词：" + FIXED)
    t = t.replace("强制要求：见〇节，照抄。", "强制要求：" + MUST)
    t = t.replace("通用负面词", NEG)
    m = re.match(r"对白反应：旁白\s*(.+?)\s*无口型。?$", t)
    if m and RISKY_VO.search(m.group(1)):
        t = "对白反应：本镜旁白后期配音，不生成人声，无口型。"
    return t

def paras(block):
    return [clean(p) for p in re.split(r"\n\s*\n", block) if p.strip() and not p.strip().startswith("**【组头】")]

def main(md, assets_path, out):
    s = open(md, encoding="utf-8").read()
    assets = json.load(open(assets_path, encoding="utf-8"))
    ep = re.search(r"## (EP\d+)", s).group(1)
    groups = re.split(r"\n(?=### S\d+-)", s)[1:]
    result = []
    for g in groups:
        title = g.splitlines()[0][4:].strip()
        gid = title.split("｜")[0]
        parts = re.split(r"\n(?=\*\*【shot )", g)
        head = paras("\n".join(parts[0].splitlines()[1:]))
        shots = []
        for p in parts[1:]:
            d = float(re.search(r"duration:\s*([\d.]+)s", p).group(1))
            shots.append((d, paras(p)))
        # split into k balanced chunks <= MAXDUR
        total = sum(d for d, _ in shots)
        k = max(1, math.ceil(total / MAXDUR))
        def best(seq, k):
            if k == 1: return [seq]
            cands = []
            for i in range(1, len(seq)):
                rest = best(seq[i:], k - 1)
                parts_ = [seq[:i]] + rest
                cands.append((max(sum(d for d, _ in c) for c in parts_), parts_))
            return min(cands, key=lambda x: x[0])[1]
        chunks = best(shots, k)
        for i, ch in enumerate(chunks):
            label = gid if len(chunks) == 1 else f"{gid}{i+1}"
            dur = sum(d for d, _ in ch)
            secs = max(4, math.ceil(dur))
            body = [f"{ep}｜{label}｜{title.split('｜',1)[1] if '｜' in title else ''}｜本分镜 {len(ch)} 镜 共 {dur:g} 秒｜输出{secs}秒｜480P｜九梦2.5Pro｜独立生成组"]
            h = list(head)
            if len(chunks) > 1:
                h = [x for x in h if not x.startswith("节奏结构")]
                h.append(f"节奏结构：本分镜为 {gid} 的第 {i+1}/{len(chunks)} 段，{len(ch)} 镜，共 {dur:g}s；时长分配 " + " / ".join(f"{d:g}s" for d, _ in ch) + "。")
                if i > 0:
                    h = [x for x in h if not x.startswith("与上一组的接续")]
                    h.append(f"与上一组的接续：紧接 {gid}{i} 段末镜的终态，人物位置、服装、光影完全连续。")
            body += h
            for d, sp in ch:
                body += sp
            text = "\n".join(body)
            hits = [w for w in BANNED if w in text]
            result.append({"episode": ep, "label": label, "duration": secs, "shots": len(ch),
                           "assets": assets.get(gid, []), "paragraphs": body, "chars": len(text), "banned_hits": hits})
    json.dump(result, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in result:
        print(r["label"], r["duration"], "s", r["shots"], "镜", r["chars"], "字", r["assets"], "BANNED:" if r["banned_hits"] else "", r["banned_hits"])

if __name__ == "__main__":
    main(*sys.argv[1:4])
