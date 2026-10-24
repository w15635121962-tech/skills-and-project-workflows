"""
示例9：Web UI - 使用 Streamlit 创建提示词管理界面
运行：streamlit run example9_web_ui.py
"""
import os
import sys
import json
from pathlib import Path

try:
    import streamlit as st
except ImportError:
    print("❌ 未安装 streamlit！")
    print("   请运行：pip install streamlit")
    sys.exit(1)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.prompt_manager import PromptManager


# 页面配置
st.set_page_config(
    page_title="AI 工具套件 - 提示词管理",
    page_icon="🎬",
    layout="wide"
)


# 初始化
@st.cache_resource
def get_prompt_manager():
    return PromptManager()

pm = get_prompt_manager()


# 侧边栏
st.sidebar.title("🎬 AI 工具套件")
st.sidebar.markdown("提示词库管理系统")

page = st.sidebar.selectbox(
    "选择功能",
    ["📋 浏览提示词", "🔍 搜索提示词", "➕ 添加提示词", "🎬 组装视频提示词", "✅ 验证提示词", "📥 导入/导出"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**提示词库统计**")
lib = pm.library
n_chars = len(lib.get("characters", {}))
n_scenes = len(lib.get("scenes", {}))
n_props = len(lib.get("props", {}))
n_neg = len(lib.get("negative_prompts", {}))
st.sidebar.markdown(f"- 角色：{n_chars}")
st.sidebar.markdown(f"- 场景：{n_scenes}")
st.sidebar.markdown(f"- 道具：{n_props}")
st.sidebar.markdown(f"- 负面提示词：{n_neg}")


# ======================
# 页面 1：浏览提示词
# ======================
if page == "📋 浏览提示词":
    st.title("📋 提示词库浏览")
    
    category = st.selectbox(
        "选择类别",
        ["characters", "scenes", "props", "negative_prompts", "video_prompts"]
    )
    
    if category in lib and lib[category]:
        items = lib[category]
        
        if category == "negative_prompts":
            for key, val in items.items():
                with st.expander(f"{key} - {val.get('label', key)}"):
                    st.code(val.get("prompt", ""), language="text")
        
        elif category == "video_prompts":
            for subcat, entries in items.items():
                st.subheader(f"📁 {subcat}")
                for key, val in entries.items():
                    with st.expander(f"{key}"):
                        st.code(val.get("prompt", ""), language="text")
        
        else:
            for name, data in items.items():
                with st.expander(f"🎯 {name}"):
                    if isinstance(data, dict):
                        st.markdown("**正面提示词：**")
                        st.code(data.get("positive", ""), language="text")
                        if data.get("negative"):
                            st.markdown("**负面提示词：**")
                            st.code(data.get("negative", ""), language="text")
                        if data.get("seed"):
                            st.markdown(f"**种子：** `{data['seed']}`")
                        if data.get("default_params"):
                            st.markdown("**默认参数：**")
                            st.json(data["default_params"])
                    else:
                        st.code(str(data), language="text")
    else:
        st.info(f"类别 '{category}' 中没有数据")


# ======================
# 页面 2：搜索提示词
# ======================
elif page == "🔍 搜索提示词":
    st.title("🔍 搜索提示词")
    
    keyword = st.text_input("输入搜索关键词", placeholder="例如：Bella, hospital, cinematic...")
    
    if keyword:
        results = pm.search_prompts(keyword)
        
        if results:
            st.success(f"找到 {len(results)} 条结果")
            
            for r in results:
                with st.expander(f"{r['category']} / {r['name']}"):
                    st.markdown("**正面提示词：**")
                    st.code(r["positive"], language="text")
                    if r["negative"]:
                        st.markdown("**负面提示词：**")
                        st.code(r["negative"], language="text")
                    if r["seed"]:
                        st.markdown(f"**种子：** `{r['seed']}`")
        else:
            st.warning("未找到匹配的结果")


# ======================
# 页面 3：添加提示词
# ======================
elif page == "➕ 添加提示词":
    st.title("➕ 添加新提示词")
    
    with st.form("add_prompt_form"):
        category = st.selectbox("类别", ["characters", "scenes", "props"])
        name = st.text_input("提示词名称", placeholder="例如：NewCharacter")
        positive = st.text_area("正面提示词", height=150)
        negative = st.text_area("负面提示词（可选）", height=100)
        seed_str = st.text_input("种子（可选，整数）", placeholder="例如：12345")
        
        submitted = st.form_submit_button("添加提示词")
        
        if submitted:
            if not name or not positive:
                st.error("请填写名称和正面提示词！")
            else:
                seed = int(seed_str) if seed_str.strip() else None
                pm.add_prompt(
                    category=category,
                    name=name,
                    positive=positive,
                    negative=negative,
                    seed=seed
                )
                st.success(f"✅ 已添加提示词：{category}/{name}")
                st.cache_resource.clear()  # 清除缓存


# ======================
# 页面 4：组装视频提示词
# ======================
elif page == "🎬 组装视频提示词":
    st.title("🎬 组装视频生成提示词")
    st.markdown("选择各个组件，自动组装成完整的视频提示词")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 镜头设置")
        shot_type = st.selectbox(
            "镜头类型",
            ["", "wide_shot", "medium_shot", "close_up", "extreme_close_up", "over_shoulder"]
        )
        camera_movement = st.selectbox(
            "摄像机运动",
            ["", "dolly_in", "dolly_out", "pan", "tilt", "handheld", "steadicam"]
        )
        action = st.selectbox(
            "动作描述",
            ["", "walking", "running", "dialogue", "expression_change", "object_interaction"]
        )
    
    with col2:
        st.markdown("### 风格与音频")
        style = st.selectbox(
            "风格",
            ["", "cinematic", "photorealistic", "dreamy", "tense", "romantic"]
        )
        motion_intensity = st.selectbox(
            "运动强度",
            ["", "low", "medium", "high"]
        )
        audio = st.selectbox(
            "音频提示",
            ["", "ambient", "music", "sound_effects", "dialogue"]
        )
    
    tool = st.selectbox(
        "工具预设",
        ["", "runway_gen3", "pika_2", "kling_1_5", "sora"]
    )
    
    if st.button("🔧 组装提示词"):
        video_prompt = pm.get_video_prompt(
            shot_type=shot_type or None,
            camera_movement=camera_movement or None,
            action=action or None,
            style=style or None,
            motion_intensity=motion_intensity or None,
            audio=audio or None,
            tool=tool or None
        )
        
        if video_prompt:
            st.success("✅ 提示词组装完成！")
            st.markdown("### 生成的视频提示词：")
            st.code(video_prompt, language="text")
            
            # 复制到剪贴板按钮（通过 JS）
            st.markdown("---")
            if st.button("📋 复制到剪贴板"):
                st.write("请手动复制上面的提示词")
        else:
            st.warning("请至少选择一个组件")


# ======================
# 页面 5：验证提示词
# ======================
elif page == "✅ 验证提示词":
    st.title("✅ 验证提示词")
    
    category = st.selectbox(
        "选择类别",
        ["characters", "scenes", "props", "video_prompts"]
    )
    
    if category in lib and lib[category]:
        if category == "video_prompts":
            # video_prompts 是嵌套结构
            subcat = st.selectbox("选择子类别", list(lib[category].keys()))
            name = st.selectbox("选择条目", list(lib[category][subcat].keys()))
            full_name = f"{subcat}.{name}"
        else:
            name = st.selectbox("选择提示词", list(lib[category].keys()))
            full_name = name
        
        if st.button("验证"):
            result = pm.validate_prompt(category, full_name)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if result["valid"]:
                    st.success("✅ 提示词有效")
                else:
                    st.error("❌ 提示词无效")
            
            with col2:
                if result["warnings"]:
                    st.warning(f"⚠️ {len(result['warnings'])} 个警告")
                else:
                    st.success("无警告")
            
            if result["errors"]:
                st.markdown("### 错误：")
                for err in result["errors"]:
                    st.error(err)
            
            if result["warnings"]:
                st.markdown("### 警告：")
                for warn in result["warnings"]:
                    st.warning(warn)


# ======================
# 页面 6：导入/导出
# ======================
elif page == "📥 导入/导出":
    st.title("📥 导入 / 导出提示词库")
    
    tab1, tab2 = st.tabs(["📤 导出", "📥 导入"])
    
    with tab1:
        st.markdown("### 导出提示词库")
        
        export_category = st.selectbox(
            "导出类别（留空表示全部）",
            ["（全部）", "characters", "scenes", "props"]
        )
        
        if st.button("📤 导出为 JSON"):
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                pm.export_prompts(
                    output_path=f.name,
                    category=None if export_category == "（全部）" else export_category
                )
                
                with open(f.name, 'r', encoding='utf-8') as f2:
                    st.download_button(
                        label="⬇️ 下载 JSON 文件",
                        data=f2.read(),
                        file_name=f"prompt_library_{export_category}.json",
                        mime="application/json"
                    )
            st.success("✅ 导出完成！")
    
    with tab2:
        st.markdown("### 导入提示词库")
        
        uploaded_file = st.file_uploader("选择 JSON 文件", type=["json"])
        overwrite = st.checkbox("覆盖已存在的提示词", value=False)
        
        if uploaded_file is not None:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as f:
                f.write(uploaded_file.getvalue())
                temp_path = f.name
            
            if st.button("📥 导入"):
                try:
                    pm.import_prompts(temp_path, overwrite=overwrite)
                    st.success("✅ 导入完成！")
                    st.cache_resource.clear()  # 清除缓存
                except Exception as e:
                    st.error(f"导入失败：{str(e)}")
                finally:
                    import os
                    os.unlink(temp_path)


# 页脚
st.markdown("---")
st.markdown("**AI 工具套件** - 提示词管理系统 | 版本 1.0")
