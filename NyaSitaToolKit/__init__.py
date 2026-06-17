import json
import os
import re
import bpy

bl_info = {
    "name": "NyaSita RE Engine ToolKit",
    "author": "NyaSita",
    "version": (1, 6, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > NST Toolkit",
    "description": "RE Engine MOD toolbox: merge, LOD rename, bone tools, material tools, name pools (zh/en)",
    "category": "Object",
}

# --------------------------------------------------------------------------- #
#   Paths
# --------------------------------------------------------------------------- #
ADDON_DIR = os.path.dirname(__file__)
PRESETS_DIR = os.path.join(ADDON_DIR, "bone_presets")
NAME_POOLS_DIR = os.path.join(ADDON_DIR, "name_pools")


def _ensure_dirs():
    for d in (PRESETS_DIR, NAME_POOLS_DIR):
        os.makedirs(d, exist_ok=True)


# --------------------------------------------------------------------------- #
#   i18n — all user-visible strings
# --------------------------------------------------------------------------- #
_STR = {
    "panel_title":        {"zh_CN": "NST Toolkit",         "en_US": "NST Toolkit"},
    "lang_label":         {"zh_CN": "语言",                "en_US": "Language"},
    "merge_title":        {"zh_CN": "合并到活跃物体",      "en_US": "Merge to Active"},
    "merge_name":         {"zh_CN": "名称模板",            "en_US": "Name Template"},
    "merge_preview_hint": {"zh_CN": "选择物体以预览名称",  "en_US": "Select objects to preview name"},
    "merge_btn":          {"zh_CN": "根据名称模板合并",    "en_US": "Merge by Template"},
    "merge_kname_btn":    {"zh_CN": "以原物体名称合并",    "en_US": "Merge as Source Name"},
    "lod_title":          {"zh_CN": "LOD 改名 & 随机命名", "en_US": "LOD & Random Rename"},
    "lod_lod":            {"zh_CN": "LOD",                 "en_US": "LOD"},
    "lod_group":          {"zh_CN": "组",                  "en_US": "Group"},
    "lod_sub":            {"zh_CN": "Sub",                 "en_US": "Sub"},
    "lod_suffix":         {"zh_CN": "后缀",                "en_US": "Suffix"},
    "lod_strip":          {"zh_CN": "去除 .NNN",           "en_US": "Strip .NNN"},
    "lod_btn":            {"zh_CN": "应用到选中",          "en_US": "Apply to Selected"},
    "bone_title":         {"zh_CN": "防脊柱移位工具",      "en_US": "Anti-Spine-Shift"},
    "bone_suffix":        {"zh_CN": "后缀",                "en_US": "Suffix"},
    "bone_add":           {"zh_CN": "添加后缀",            "en_US": "Add Suffix"},
    "bone_revert":        {"zh_CN": "还原",                "en_US": "Revert"},
    "bone_presets":       {"zh_CN": "预设",                "en_US": "Presets"},
    "bone_save":          {"zh_CN": "保存",                "en_US": "Save"},
    "bone_select":        {"zh_CN": "选择骨骼",            "en_US": "Select Bones"},
    "bone_no_presets":    {"zh_CN": "暂无预设",            "en_US": "No presets saved yet"},
    "bone_preset_dropdown": {"zh_CN": "预设",              "en_US": "Preset"},
    # operator reports
    "err_no_active":      {"zh_CN": "没有活跃物体",        "en_US": "No active object"},
    "err_no_selected":    {"zh_CN": "请再选至少要合并的物体", "en_US": "Select objects to merge into the active"},
    "warn_join_rename":   {"zh_CN": "合并成功但改名失败",  "en_US": "Join succeeded but rename failed"},
    "info_merged":        {"zh_CN": "已合并 →",            "en_US": "Merged →"},
    "info_renamed":       {"zh_CN": "已改名 {0} 个（{1} 个无需改）", "en_US": "Renamed {0} ({1} already up-to-date)"},
    "info_renamed_all":   {"zh_CN": "所有 {0} 个已是最新", "en_US": "All {0} already up-to-date"},
    "warn_no_bones":      {"zh_CN": "没有选中骨骼",        "en_US": "No bones selected"},
    "info_bone_add":      {"zh_CN": "已给 {0} 根骨骼添加 '{1}'", "en_US": "Added '{1}' to {0} bone(s)"},
    "info_bone_revert":   {"zh_CN": "已还原 {0} 根骨骼",   "en_US": "Reverted suffix on {0} bone(s)"},
    "err_preset_name":    {"zh_CN": "请输入预设名",        "en_US": "Please enter a preset name"},
    "err_no_bones":       {"zh_CN": "没有选中骨骼",        "en_US": "No bones selected"},
    "info_preset_saved":  {"zh_CN": "预设 '{0}' 已保存（{1} 根骨骼）", "en_US": "Preset '{0}' saved ({1} bones)"},
    "info_preset_updated": {"zh_CN": "预设 '{0}' 已更新（{1} 根骨骼）", "en_US": "Preset '{0}' updated ({1} bones)"},
    "err_no_preset":      {"zh_CN": "未选择预设",          "en_US": "No preset selected"},
    "err_preset_missing": {"zh_CN": "预设文件不存在: {0}", "en_US": "Preset file not found: {0}"},
    "info_selected_bones": {"zh_CN": "已选中 {0} 根骨骼（来自 '{1}'）", "en_US": "Selected {0} bone(s) from '{1}'"},
    "warn_no_match":      {"zh_CN": "没有匹配的骨骼（'{0}'）", "en_US": "No matching bones for '{0}'"},
    "info_preset_deleted": {"zh_CN": "预设 '{0}' 已删除",  "en_US": "Preset '{0}' deleted"},
    "err_delete_failed":  {"zh_CN": "无法删除 '{0}'",      "en_US": "Could not delete '{0}'"},
    # save dialog
    "dialog_preset_name": {"zh_CN": "预设名称",            "en_US": "Preset Name"},
    "dialog_preset_desc": {"zh_CN": "保存在插件文件夹的 presets/ 中", "en_US": "Saved as .json in the addon presets/ folder"},
    # anti-spine-shift
    "spine_btn":          {"zh_CN": "Noesis骨骼缩放转RE Mesh", "en_US": "Noesis Bone Scale → RE Mesh"},
    "spine_desc":         {"zh_CN": "选中骨架 → Step1 → Step2 约束链，缩放并应用", "en_US": "Chain: Selected → Step1 → Step2 with scale & apply"},
    "err_step_missing":   {"zh_CN": "场景中没有 '{0}'",    "en_US": "'{0}' not found in scene"},
    "err_step_not_armature": {"zh_CN": "'{0}' 不是骨架",   "en_US": "'{0}' is not an armature"},
    "info_spine_done":    {"zh_CN": "约束链完成: {0} → Step1 → Step2 | Step1 已缩放 0.01 并应用", "en_US": "Chain done: {0} → Step1 → Step2 | Step1 scaled 0.01 & baked"},
    # clean & duplicate
    "clean_title":        {"zh_CN": "清空与复制",          "en_US": "Clean & Duplicate"},
    "clean_btn":          {"zh_CN": "清空模型",            "en_US": "Clean Model"},
    "dup_count":          {"zh_CN": "数量",                "en_US": "Count"},
    "dup_btn":            {"zh_CN": "复制",                "en_US": "Duplicate"},
    "err_not_mesh":       {"zh_CN": "请选一个网格物体",    "en_US": "Select a mesh object"},
    "info_cleaned":       {"zh_CN": "已清空 '{0}'（UV/顶点组/权重/颜色/材质/形态键/几何体已删除）", "en_US": "Cleaned '{0}' (UV/VGroups/Weights/Colors/Materials/ShapeKeys/Geometry removed)"},
    "info_duplicated":    {"zh_CN": "已复制 {0} 个",       "en_US": "Duplicated {0} copy(s)"},
    # material tools
    "mat_title":          {"zh_CN": "材质工具",            "en_US": "Material Tools"},
    "mat_unique_btn":     {"zh_CN": "材质独立并改名",      "en_US": "Make Unique & Rename"},
    "mat_unique_merge_btn": {"zh_CN": "材质独立并合并",    "en_US": "Unique, Rename & Merge"},
    "mat_separate_btn":   {"zh_CN": "按材质分离",          "en_US": "Separate by Material"},
    "info_mat_unique":    {"zh_CN": "已处理 {0} 个物体的材质", "en_US": "Materials made unique on {0} object(s)"},
    "info_mat_unique_merge": {"zh_CN": "材质独立并合并完成 → {0}", "en_US": "Unique, renamed & merged → {0}"},
    "info_mat_separate":  {"zh_CN": "已按材质分离，生成 {0} 个物体", "en_US": "Separated by material — {0} object(s)"},
    "err_no_mesh_sel":    {"zh_CN": "请选至少一个网格物体", "en_US": "Select at least one mesh object"},
    # backface culling
    "quick_title":        {"zh_CN": "快捷工具",            "en_US": "Quick Tools"},
    "quick_strip":        {"zh_CN": "去 .001",             "en_US": "Strip .001"},
    "bfc_title":          {"zh_CN": "背面剔除",            "en_US": "Backface Culling"},
    "bfc_show":           {"zh_CN": "显示背面",            "en_US": "Show Backfaces"},
    "info_bfc_hide":      {"zh_CN": "已隐藏 {0} 个材质的背面", "en_US": "Backfaces hidden ({0} materials)"},
    "info_bfc_show":      {"zh_CN": "已显示 {0} 个材质的背面", "en_US": "Backfaces shown ({0} materials)"},
    # random rename
    "random_title":       {"zh_CN": "随机命名为游戏网格名称", "en_US": "Random → Game Mesh Name"},
    "random_pool":        {"zh_CN": "名称池",              "en_US": "Name Pool"},
    "random_btn":         {"zh_CN": "随机命名",            "en_US": "Random Rename"},
    "random_format":      {"zh_CN": "格式",                "en_US": "Format"},
    "random_use_panel":   {"zh_CN": "使用面板数字",        "en_US": "Use Panel Nums"},
    "err_no_text":        {"zh_CN": "没有可用的文本块，请先在文本编辑器里创建一个", "en_US": "No text datablock — create one in the Text Editor first"},
    "err_text_empty":     {"zh_CN": "名称池 '{0}' 是空的", "en_US": "Name pool '{0}' is empty"},
    "err_not_enough":     {"zh_CN": "名称不够（{0} 个对象，池里只有 {1} 个名字）", "en_US": "Not enough names ({0} objects, {1} in pool)"},
    "info_random_done":   {"zh_CN": "已随机命名 {0} 个物体", "en_US": "Randomly renamed {0} object(s)"},
    # part separation
    "part_title":         {"zh_CN": "部件分离",            "en_US": "Part Separation"},
    "part_btn":           {"zh_CN": "分离到新骨架",        "en_US": "Split to New Armature"},
    "part_arm_name":      {"zh_CN": "新骨架名",            "en_US": "New Arm Name"},
    "err_no_armature":    {"zh_CN": "'{0}' 没有骨架修改器", "en_US": "'{0}' has no armature modifier"},
    "err_diff_armature":  {"zh_CN": "选中的部件用的不是同一个骨架", "en_US": "Selected objects use different armatures"},
    "info_part_done":     {"zh_CN": "已将 {0} 个部件分离到 '{1}'", "en_US": "Split {0} part(s) to '{1}'"},
    # bone name check
    "bone_check_title":   {"zh_CN": "骨骼名称检测",        "en_US": "Bone Name Check"},
    "bone_check_non_en":  {"zh_CN": "选中非英文字符骨骼",  "en_US": "Select Non-English Bones"},
    "bone_check_fix":     {"zh_CN": "标点符号替换为 _",    "en_US": "Fix Symbols → _"},
    "info_non_en":        {"zh_CN": "选中了 {0} 根含非英文字符的骨骼", "en_US": "Selected {0} bone(s) with non-English chars"},
    "info_non_en_none":   {"zh_CN": "所有骨骼名称均为纯英文", "en_US": "All bone names are English-only"},
    "info_fix_symbols":   {"zh_CN": "修复了 {0} 根骨骼名称中的标点符号", "en_US": "Fixed symbols in {0} bone name(s)"},
    "info_fix_none":      {"zh_CN": "所有骨骼名称无需修复", "en_US": "No bone names needed fixing"},
    "bone_check_fw_digit": {"zh_CN": "选中全角数字骨骼",  "en_US": "Select Fullwidth Digit Bones"},
    "bone_fix_fw_digit":   {"zh_CN": "全角数字→半角",     "en_US": "Fullwidth Digits → ASCII"},
    "info_fw_digit":       {"zh_CN": "选中了 {0} 根含全角/特殊数字的骨骼", "en_US": "Selected {0} bone(s) with fullwidth/special digits"},
    "info_fw_digit_none":  {"zh_CN": "所有骨骼名称无不规范数字字符", "en_US": "No irregular digit characters found"},
    "info_fix_fw_digit":   {"zh_CN": "已将 {0} 根骨骼的全角数字转换为半角", "en_US": "Converted fullwidth digits in {0} bone(s)"},
    "info_fix_fw_none":    {"zh_CN": "没有需要转换的骨骼", "en_US": "No bones with fullwidth digits found"},
    # mdf export
    "mdf_title":          {"zh_CN": "RE MDF 导出",         "en_US": "RE MDF Export"},
    "mdf_folder":         {"zh_CN": "导出目录",            "en_US": "Export Folder"},
    "mdf_collection":     {"zh_CN": "MDF 集合",            "en_US": "MDF Collection"},
    "mdf_version":        {"zh_CN": "游戏版本",            "en_US": "Game Version"},
    "mdf_btn":            {"zh_CN": "导出并替换全部",      "en_US": "Export & Replace All"},
    "err_no_mdf_collection": {"zh_CN": "请先选择一个 MDF 集合", "en_US": "Select an MDF collection first"},
    "info_mdf_done":      {"zh_CN": "已导出并替换 {0} 个 .mdf2{1} 文件", "en_US": "Exported & replaced {0} .mdf2{1} file(s)"},
    # mode labels
    "mode_object":        {"zh_CN": "物体模式",            "en_US": "Object Mode"},
    "mode_edit_pose":     {"zh_CN": "编辑 / 姿态模式",     "en_US": "Edit / Pose Mode"},
    "mode_edit":          {"zh_CN": "编辑模式",            "en_US": "Edit Mode"},
}


def _t(key: str, context=None) -> str:
    """Return the translated string for *key* in the current language."""
    if context is not None:
        lang = getattr(context.scene, "nst_language", "zh_CN")
    else:
        lang = "zh_CN"
    entry = _STR.get(key)
    if entry:
        return entry.get(lang, entry.get("en_US", key))
    return key


def _tfmt(key: str, context, *args) -> str:
    """Translate + format with positional args."""
    s = _t(key, context)
    try:
        return s.format(*args)
    except (IndexError, KeyError):
        return s


# --------------------------------------------------------------------------- #
#   Patterns
# --------------------------------------------------------------------------- #
_LOD_RE = re.compile(
    r"^LOD_(?P<lod>\d+)_Group_(?P<group>\d+)_Sub_(?P<sub>\d+)__(?P<rest>.+)$"
)
_RE_MESH_RE = re.compile(
    r"^Group_(?P<group>\d+)_Sub_(?P<sub>\d+)__(?P<rest>.+)$"
)
_BLENDER_SUFFIX_RE = re.compile(r"\.\d{3}$")

# ── Fullwidth / special digit → ASCII digit map ──────────────────────────
_FULLWIDTH_DIGIT_MAP = {}

# Fullwidth digits: U+FF10-U+FF19 → 0-9 (most common in CJK text)
for i in range(10):
    _FULLWIDTH_DIGIT_MAP[chr(0xFF10 + i)] = str(i)

# Mathematical bold digits: U+1D7CE-U+1D7D7
for i in range(10):
    _FULLWIDTH_DIGIT_MAP[chr(0x1D7CE + i)] = str(i)

# Mathematical double-struck digits: U+1D7D8-U+1D7E1
for i in range(10):
    _FULLWIDTH_DIGIT_MAP[chr(0x1D7D8 + i)] = str(i)

# Mathematical sans-serif digits: U+1D7E2-U+1D7EB
for i in range(10):
    _FULLWIDTH_DIGIT_MAP[chr(0x1D7E2 + i)] = str(i)

# Mathematical sans-serif bold digits: U+1D7EC-U+1D7F5
for i in range(10):
    _FULLWIDTH_DIGIT_MAP[chr(0x1D7EC + i)] = str(i)

# Mathematical monospace digits: U+1D7F6-U+1D7FF
for i in range(10):
    _FULLWIDTH_DIGIT_MAP[chr(0x1D7F6 + i)] = str(i)


def _has_fullwidth_digit(name: str) -> bool:
    """Return True if *name* contains any fullwidth / special digit character."""
    return any(c in _FULLWIDTH_DIGIT_MAP for c in name)


def _fix_fullwidth_digits(name: str) -> str:
    """Replace fullwidth / special digits in *name* with ASCII digits."""
    return "".join(_FULLWIDTH_DIGIT_MAP.get(c, c) for c in name)


def _parse_lod_name(name: str):
    m = _LOD_RE.match(name)
    if m:
        return (
            int(m.group("lod")),
            int(m.group("group")),
            int(m.group("sub")),
            m.group("rest"),
        )
    return None


# ═══════════════════════════════════════════════════════════════════════════ #
#   Bone helpers
# ═══════════════════════════════════════════════════════════════════════════ #

def _get_selected_bone_names(context):
    obj = context.active_object
    if not obj or obj.type != 'ARMATURE':
        return []
    if context.mode == 'EDIT_ARMATURE':
        return [b.name for b in obj.data.edit_bones if b.select]
    if context.mode == 'POSE':
        return [b.name for b in context.selected_pose_bones]
    return []


def _select_bones_by_names(context, arm_obj, names):
    if context.mode != 'EDIT_ARMATURE':
        bpy.ops.object.mode_set(mode='EDIT')
    suffix = context.scene.nst_bone_suffix
    ebones = arm_obj.data.edit_bones
    for eb in ebones:
        eb.select = False
        eb.select_head = False
        eb.select_tail = False
    found = 0
    for eb in ebones:
        # Exact match, or match after stripping the configured suffix
        if eb.name in names:
            match = True
        elif suffix and eb.name.endswith(suffix):
            match = eb.name[:-len(suffix)] in names
        else:
            match = False
        if match:
            eb.select = True
            eb.select_head = True
            eb.select_tail = True
            found += 1
    return found


# ═══════════════════════════════════════════════════════════════════════════ #
#   Preset file I/O
# ═══════════════════════════════════════════════════════════════════════════ #

def _preset_path(name: str) -> str:
    safe = name.replace("/", "_").replace("\\", "_")
    return os.path.join(PRESETS_DIR, f"{safe}.json")


def _list_preset_names():
    if not os.path.isdir(PRESETS_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(PRESETS_DIR) if f.endswith(".json"))


def _load_preset(name: str):
    path = _preset_path(name)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _save_preset(name: str, bone_names: list):
    _ensure_dirs()
    path = _preset_path(name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(bone_names, fh, indent=2, ensure_ascii=False)


def _delete_preset_file(name: str):
    path = _preset_path(name)
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════ #
#   Enum callbacks
# ═══════════════════════════════════════════════════════════════════════════ #

def _preset_enum_items(scene, context):
    items = []
    for name in _list_preset_names():
        items.append((name, name, ""))
    if not items:
        items.append(("__NONE__", "(no presets)", ""))
    return items


def _name_pool_enum_items(scene, context):
    items = []
    for name in _list_name_pools():
        items.append((name, name, ""))
    if not items:
        items.append(("__NONE__", "(no pools)", ""))
    return items


# ═══════════════════════════════════════════════════════════════════════════ #
#   Name pool file I/O
# ═══════════════════════════════════════════════════════════════════════════ #

def _name_pool_path(name: str) -> str:
    safe = name.replace("/", "_").replace("\\", "_")
    return os.path.join(NAME_POOLS_DIR, f"{safe}.json")


def _list_name_pools():
    if not os.path.isdir(NAME_POOLS_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(NAME_POOLS_DIR) if f.endswith(".json"))


def _load_name_pool(name: str):
    path = _name_pool_path(name)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_name_pool(name: str, items: list):
    _ensure_dirs()
    path = _name_pool_path(name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2, ensure_ascii=False)


def _delete_name_pool_file(name: str):
    path = _name_pool_path(name)
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operators — Merge & LOD
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_MergeToActive(bpy.types.Operator):
    bl_idname = "nst.merge_to_active"
    bl_label = "Merge to Active"
    bl_description = "Join selected objects into the active object, renaming the result"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        active = context.active_object

        if active is None:
            self.report({'ERROR'}, _t("err_no_active", context))
            return {'CANCELLED'}

        selected = [o for o in context.selected_objects if o != active]
        if not selected:
            self.report({'ERROR'}, _t("err_no_selected", context))
            return {'CANCELLED'}

        source_name = selected[0].name

        bpy.ops.object.join()

        template = scene.nst_name_template
        new_name = template.replace("@n", source_name)

        result = context.view_layer.objects.active
        if result:
            result.name = new_name
            self.report({'INFO'}, f"{_t('info_merged', context)} {new_name}")
        else:
            self.report({'WARNING'}, _t("warn_join_rename", context))

        return {'FINISHED'}


class NST_OT_MergeKeepName(bpy.types.Operator):
    """Merge selected objects to active, keep the first selected object's name."""
    bl_idname = "nst.merge_keep_name"
    bl_label = "Merge → Keep Name"
    bl_description = "Join selected objects into active, then rename result to the first selected's name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = context.active_object
        if active is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        selected = [o for o in context.selected_objects if o != active]
        if not selected:
            self.report({'ERROR'}, "Select at least one other object")
            return {'CANCELLED'}
        kept_name = selected[0].name
        bpy.ops.object.join()
        result = context.view_layer.objects.active
        if result:
            result.name = kept_name
            self.report({'INFO'}, f"Merged → {kept_name}")
        return {'FINISHED'}


class NST_OT_RenameLOD(bpy.types.Operator):
    bl_idname = "nst.rename_lod"
    bl_label = "Rename LOD"
    bl_description = "Replace LOD / Group / Sub numbers in selected object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        fmt = scene.nst_random_format  # 'NOESIS' or 'RE_MESH'
        lod = scene.nst_lod_num
        grp = scene.nst_group_num
        sub = scene.nst_sub_num
        suffix = scene.nst_lod_suffix
        strip_suffix = scene.nst_strip_blender_suffix

        count = 0
        skipped = 0
        is_re = (fmt == 'RE_MESH')

        for obj in context.selected_objects:
            if is_re:
                m = _RE_MESH_RE.match(obj.name)
                has_fmt = (m is not None)
            else:
                m = _parse_lod_name(obj.name)
                has_fmt = (m is not None)

            if has_fmt:
                if is_re:
                    rest = m.group("rest")
                    if strip_suffix:
                        rest = _BLENDER_SUFFIX_RE.sub("", rest)
                    new_name = f"Group_{grp}_Sub_{sub}__{rest}"
                else:
                    rest = m[3]
                    if strip_suffix:
                        rest = _BLENDER_SUFFIX_RE.sub("", rest)
                    new_name = f"LOD_{lod}_Group_{grp}_Sub_{sub}__{rest}"
            else:
                base = _BLENDER_SUFFIX_RE.sub("", obj.name) if strip_suffix else obj.name
                if is_re:
                    new_name = f"Group_{grp}_Sub_{sub}__{base}{suffix}"
                else:
                    new_name = f"LOD_{lod}_Group_{grp}_Sub_{sub}__{base}{suffix}"

            if obj.name != new_name:
                obj.name = new_name
                count += 1
            else:
                skipped += 1

        if count:
            self.report({'INFO'}, _tfmt("info_renamed", context, count, skipped))
        else:
            self.report({'INFO'}, _tfmt("info_renamed_all", context, skipped))

        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operators — Bone rename
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_BoneAddSuffix(bpy.types.Operator):
    """Append a suffix to the name of every selected bone."""
    bl_idname = "nst.bone_add_suffix"
    bl_label = "Add Bone Suffix"
    bl_description = "Add a suffix to all selected bone names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode in ('EDIT_ARMATURE', 'POSE')

    def execute(self, context):
        suffix = context.scene.nst_bone_suffix
        arm_obj = context.active_object
        count = 0

        if context.mode == 'EDIT_ARMATURE':
            for eb in arm_obj.data.edit_bones:
                if eb.select and not eb.name.endswith(suffix):
                    eb.name += suffix
                    count += 1
        else:
            for pb in context.selected_pose_bones:
                if not pb.name.endswith(suffix):
                    pb.bone.name += suffix
                    count += 1

        if count == 0:
            self.report({'WARNING'}, "No bones selected or all already have suffix")
        else:
            self.report({'INFO'}, f"Added '{suffix}' to {count} bone(s)")
        return {'FINISHED'}


class NST_OT_BoneRevertSuffix(bpy.types.Operator):
    """Remove the suffix from every selected bone's name (undo the Add)."""
    bl_idname = "nst.bone_revert_suffix"
    bl_label = "Revert Bone Suffix"
    bl_description = "Strip the suffix from all selected bone names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode in ('EDIT_ARMATURE', 'POSE')

    def execute(self, context):
        suffix = context.scene.nst_bone_suffix
        arm_obj = context.active_object
        count = 0

        if context.mode == 'EDIT_ARMATURE':
            for eb in arm_obj.data.edit_bones:
                if eb.select and eb.name.endswith(suffix):
                    eb.name = eb.name[:-len(suffix)]
                    count += 1
        else:
            for pb in context.selected_pose_bones:
                if pb.name.endswith(suffix):
                    pb.bone.name = pb.bone.name[:-len(suffix)]
                    count += 1

        if count == 0:
            self.report({'WARNING'}, "No selected bones with suffix found")
        else:
            self.report({'INFO'}, f"Reverted suffix on {count} bone(s)")
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operators — Bone presets (file-based)
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_SaveBonePreset(bpy.types.Operator):
    bl_idname = "nst.save_bone_preset"
    bl_label = "Save Bone Preset"
    bl_description = "Store current bone selection as a JSON preset file"
    bl_options = {'REGISTER', 'UNDO'}

    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name to save this preset under",
        default="",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode in ('EDIT_ARMATURE', 'POSE')

    def invoke(self, context, event):
        self.preset_name = ""
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if not self.preset_name.strip():
            self.report({'ERROR'}, _t("err_preset_name", context))
            return {'CANCELLED'}

        selected = _get_selected_bone_names(context)
        if not selected:
            self.report({'ERROR'}, _t("err_no_bones", context))
            return {'CANCELLED'}

        name = self.preset_name.strip()
        presets = _list_preset_names()
        existed = name in presets
        _save_preset(name, selected)

        if existed:
            self.report({'INFO'}, _tfmt("info_preset_updated", context, name, len(selected)))
        else:
            self.report({'INFO'}, _tfmt("info_preset_saved", context, name, len(selected)))
        return {'FINISHED'}


class NST_OT_SelectBonePreset(bpy.types.Operator):
    bl_idname = "nst.select_bone_preset"
    bl_label = "Select Preset Bones"
    bl_description = "Select all bones stored in the active preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode in ('EDIT_ARMATURE', 'POSE')

    def execute(self, context):
        preset_name = context.scene.nst_active_bone_preset
        if not preset_name or preset_name == "__NONE__":
            self.report({'ERROR'}, _t("err_no_preset", context))
            return {'CANCELLED'}

        names = _load_preset(preset_name)
        if names is None:
            self.report({'ERROR'}, _tfmt("err_preset_missing", context, preset_name))
            return {'CANCELLED'}

        found = _select_bones_by_names(context, context.active_object, set(names))

        if found:
            self.report({'INFO'}, _tfmt("info_selected_bones", context, found, preset_name))
        else:
            self.report({'WARNING'}, _tfmt("warn_no_match", context, preset_name))
        return {'FINISHED'}


class NST_OT_DeleteBonePreset(bpy.types.Operator):
    bl_idname = "nst.delete_bone_preset"
    bl_label = "Delete Bone Preset"
    bl_description = "Delete the selected preset JSON file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        name = context.scene.nst_active_bone_preset
        return name and name != "__NONE__"

    def execute(self, context):
        name = context.scene.nst_active_bone_preset
        if _delete_preset_file(name):
            self.report({'INFO'}, _tfmt("info_preset_deleted", context, name))
        else:
            self.report({'ERROR'}, _tfmt("err_delete_failed", context, name))
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operator — Anti-Spine-Shift chain
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_AntiSpineShift(bpy.types.Operator):
    """Build the constraint chain: Selected → Step1 → Step2, then bake."""
    bl_idname = "nst.anti_spine_shift"
    bl_label = "Noesis Bone Scale → RE Mesh"
    bl_description = (
        "Copy Scale chain: selected → Step1 → Step2, then scale Step1 to 0.01 and bake"
    )
    bl_options = {'REGISTER', 'UNDO'}

    _constraint_name = "NST_CopyScale"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode == 'OBJECT'

    def execute(self, context):
        scene = context.scene
        selected = context.active_object

        # ── Validate ──────────────────────────────────────────────────
        for name in ("Step1", "Step2"):
            obj = bpy.data.objects.get(name)
            if obj is None:
                self.report({'ERROR'}, _tfmt("err_step_missing", context, name))
                return {'CANCELLED'}
            if obj.type != 'ARMATURE':
                self.report({'ERROR'}, _tfmt("err_step_not_armature", context, name))
                return {'CANCELLED'}

        step1 = bpy.data.objects["Step1"]
        step2 = bpy.data.objects["Step2"]

        # ── 1. Selected → Copy Scale → Step1 ──────────────────────────
        bpy.ops.object.select_all(action='DESELECT')
        selected.select_set(True)
        context.view_layer.objects.active = selected
        _add_copy_scale_constraint(selected, step1)

        # ── 2. Step1 → Copy Scale → Step2 ─────────────────────────────
        bpy.ops.object.select_all(action='DESELECT')
        step1.select_set(True)
        context.view_layer.objects.active = step1
        _add_copy_scale_constraint(step1, step2)

        # ── 3. Apply modifiers / visual-transform on Step2 ─────────────
        bpy.ops.object.select_all(action='DESELECT')
        step2.select_set(True)
        context.view_layer.objects.active = step2
        bpy.ops.object.visual_transform_apply()

        # ── 4. Bake constraint on Step1 (bake Step2's scale → Step1), then remove it ──
        _apply_nst_constraint(context, step1)

        # ── 5. Step1 scale → 0.01  (constraint is gone, so this takes effect) ──
        step1.scale = (0.01, 0.01, 0.01)

        # ── 6. Bake constraint on selected (bake Step1's 0.01 scale → selected), then remove it ──
        _apply_nst_constraint(context, selected)

        # ── Restore selection ──────────────────────────────────────────
        bpy.ops.object.select_all(action='DESELECT')
        selected.select_set(True)
        context.view_layer.objects.active = selected

        self.report({'INFO'}, _tfmt("info_spine_done", context, selected.name))
        return {'FINISHED'}


class NST_OT_RandomRename(bpy.types.Operator):
    """Assign random unique names to selected objects from the active name pool."""
    bl_idname = "nst.random_rename"
    bl_label = "Random Rename"
    bl_description = "Rename selected objects using random names from the chosen name pool"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        pool_name = context.scene.nst_random_pool
        return context.mode == 'OBJECT' and bool(context.selected_objects) and \
               pool_name not in ("", "__NONE__")

    def execute(self, context):
        scene = context.scene
        pool_name = scene.nst_random_pool
        pool = _load_name_pool(pool_name)

        if not pool:
            self.report({'ERROR'}, _tfmt("err_text_empty", context, pool_name))
            return {'CANCELLED'}

        fmt = scene.nst_random_format        # 'NOESIS' or 'RE_MESH'
        use_panel = scene.nst_random_use_panel
        lod = scene.nst_lod_num
        grp = scene.nst_group_num
        sub = scene.nst_sub_num

        # Extract the "body" from each selected object
        # (strip LOD/Group/Sub prefix and _Mat suffix to get the core name)
        def _body(obj):
            if fmt == 'RE_MESH':
                m = _RE_MESH_RE.match(obj.name)
                if m:
                    rest = m.group("rest")
                    return rest[:-4] if rest.endswith("_Mat") else rest
            else:
                m = _LOD_RE.match(obj.name)
                if m:
                    rest = m.group("rest")
                    return rest[:-4] if rest.endswith("_Mat") else rest
            # Non-LOD object: use full name as body (strip _Mat if present)
            n = obj.name
            return n[:-4] if n.endswith("_Mat") else n

        # Group objects by body name
        groups = {}
        for obj in context.selected_objects:
            body = _body(obj)
            groups.setdefault(body, []).append(obj)

        if len(groups) > len(pool):
            self.report({'ERROR'}, _tfmt("err_not_enough", context, len(groups), len(pool)))
            return {'CANCELLED'}

        import random
        # Assign one pool name per group
        group_names = random.sample(pool, len(groups))

        for (body, objs), pool_name_item in zip(groups.items(), group_names):
            clean = pool_name_item
            if clean.endswith("_Mat"):
                clean = clean[:-4]

            for obj in objs:
                if fmt == 'RE_MESH':
                    if use_panel:
                        g, s = grp, sub
                    else:
                        m = _RE_MESH_RE.match(obj.name)
                        if m:
                            g, s = int(m.group("group")), int(m.group("sub"))
                        else:
                            g, s = 0, 0
                    new_name = f"Group_{g}_Sub_{s}__{clean}_Mat"
                else:
                    if use_panel:
                        l, g, s = lod, grp, sub
                    else:
                        m = _LOD_RE.match(obj.name)
                        if m:
                            l, g, s = int(m.group("lod")), int(m.group("group")), int(m.group("sub"))
                        else:
                            l, g, s = 1, 0, 1
                    new_name = f"LOD_{l}_Group_{g}_Sub_{s}__{clean}_Mat"

                obj.name = new_name

        total = sum(len(v) for v in groups.values())
        self.report({'INFO'}, _tfmt("info_random_done", context, total))
        return {'FINISHED'}


class NST_OT_EditNamePool(bpy.types.Operator):
    """Open the active name pool as a text datablock for editing."""
    bl_idname = "nst.edit_name_pool"
    bl_label = "Edit Name Pool"
    bl_description = "Open this pool in Blender's Text Editor for editing"
    bl_options = {'REGISTER', 'UNDO'}

    TEXT_NAME = "_NST_NamePool_Edit"

    @classmethod
    def poll(cls, context):
        name = context.scene.nst_random_pool
        return name not in ("", "__NONE__")

    def execute(self, context):
        pool_name = context.scene.nst_random_pool
        names = _load_name_pool(pool_name)
        content = "\n".join(names)

        # Create / overwrite a temporary text datablock
        text = bpy.data.texts.get(self.TEXT_NAME)
        if text is None:
            text = bpy.data.texts.new(self.TEXT_NAME)
        text.clear()
        text.write(content)

        # Switch workspace to include Text Editor, or just report
        self.report({'INFO'}, f"'{pool_name}' opened in Text Editor → save with [+] when done")
        return {'FINISHED'}


class NST_OT_SaveNamePoolFromText(bpy.types.Operator):
    """Save the edited text back into the active name pool."""
    bl_idname = "nst.save_name_pool_from_text"
    bl_label = "Save Pool from Text"
    bl_description = "Parse the text datablock and save back to the active JSON pool"
    bl_options = {'REGISTER', 'UNDO'}

    TEXT_NAME = "_NST_NamePool_Edit"

    @classmethod
    def poll(cls, context):
        name = context.scene.nst_random_pool
        return name not in ("", "__NONE__")

    def execute(self, context):
        text = bpy.data.texts.get(self.TEXT_NAME)
        if text is None:
            self.report({'ERROR'}, "No edit text found — click Edit first")
            return {'CANCELLED'}

        names = [line.body.strip() for line in text.lines if line.body.strip()]
        pool_name = context.scene.nst_random_pool
        _save_name_pool(pool_name, names)
        self.report({'INFO'}, f"'{pool_name}' saved ({len(names)} names)")
        return {'FINISHED'}


class NST_OT_SaveNamePool(bpy.types.Operator):
    """Create a new name pool."""
    bl_idname = "nst.save_name_pool"
    bl_label = "Save Name Pool"
    bl_description = "Create a new name pool with the given name"
    bl_options = {'REGISTER', 'UNDO'}

    pool_name: bpy.props.StringProperty(name="Pool Name", default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if not self.pool_name.strip():
            return {'CANCELLED'}
        name = self.pool_name.strip()
        # Don't overwrite — create empty if new
        if name not in _list_name_pools():
            _save_name_pool(name, [])
        self.report({'INFO'}, f"Name pool '{name}' created")
        return {'FINISHED'}


class NST_OT_CheckPoolDupes(bpy.types.Operator):
    """Check the active name pool for duplicate entries."""
    bl_idname = "nst.check_pool_dupes"
    bl_label = "Check Pool Dupes"
    bl_description = "Scan the selected name pool for duplicate names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        name = context.scene.nst_random_pool
        return name not in ("", "__NONE__")

    def execute(self, context):
        pool_name = context.scene.nst_random_pool
        pool = _load_name_pool(pool_name)
        seen = {}
        dupes = []
        for name in pool:
            seen[name] = seen.get(name, 0) + 1
        for name, count in seen.items():
            if count > 1:
                dupes.append(f"{name} ({count}×)")
        if dupes:
            self.report({'WARNING'}, f"Duplicates in '{pool_name}': {', '.join(dupes)}")
        else:
            self.report({'INFO'}, f"'{pool_name}': all {len(pool)} names unique")
        return {'FINISHED'}


class NST_OT_DeleteNamePool(bpy.types.Operator):
    """Delete the active name pool."""
    bl_idname = "nst.delete_name_pool"
    bl_label = "Delete Name Pool"
    bl_description = "Delete the selected name pool file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        name = context.scene.nst_random_pool
        return name not in ("", "__NONE__")

    def execute(self, context):
        name = context.scene.nst_random_pool
        _delete_name_pool_file(name)
        self.report({'INFO'}, f"Name pool '{name}' deleted")
        return {'FINISHED'}


def _add_copy_scale_constraint(owner, target):
    """Add a Copy Scale Object constraint on *owner* targeting *target*."""
    c = owner.constraints.new(type='COPY_SCALE')
    c.name = NST_OT_AntiSpineShift._constraint_name
    c.target = target
    c.use_x = True
    c.use_y = True
    c.use_z = True
    c.target_space = 'WORLD'
    c.owner_space = 'WORLD'


def _apply_nst_constraint(context, obj):
    """Bake the NST Copy Scale on *obj* into its transform, then remove the constraint."""
    c = obj.constraints.get(NST_OT_AntiSpineShift._constraint_name)
    if c is None:
        return

    # Select only this object and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj

    # Bake everything (constraint + transform) into the object's local transform
    bpy.ops.object.visual_transform_apply()

    # Clean up — the constraint has been baked, safe to remove
    c2 = obj.constraints.get(NST_OT_AntiSpineShift._constraint_name)
    if c2:
        obj.constraints.remove(c2)


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operators — Clean & Duplicate
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_CleanMesh(bpy.types.Operator):
    """Strip the active mesh object down to an empty shell."""
    bl_idname = "nst.clean_mesh"
    bl_label = "Clean Mesh"
    bl_description = "Remove UVs, vertex groups, color attributes, materials, shape keys, and all geometry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        # Shape keys (must be removed first — they own the basis)
        if mesh.shape_keys:
            obj.shape_key_clear()

        # Vertex groups
        obj.vertex_groups.clear()

        # UV layers
        while mesh.uv_layers:
            mesh.uv_layers.remove(mesh.uv_layers[0])

        # Color attributes
        if hasattr(mesh, 'color_attributes'):
            while mesh.color_attributes:
                mesh.color_attributes.remove(mesh.color_attributes[0])

        # Materials
        mesh.materials.clear()

        # Geometry — delete all verts / edges / faces
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, _tfmt("info_cleaned", context, obj.name))
        return {'FINISHED'}


class NST_OT_DuplicateCount(bpy.types.Operator):
    """Duplicate the active object N times."""
    bl_idname = "nst.duplicate_count"
    bl_label = "Duplicate by Count"
    bl_description = "Duplicate the active object the specified number of times"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == 'OBJECT'

    def execute(self, context):
        count = context.scene.nst_dup_count
        obj = context.active_object

        if count < 1:
            self.report({'WARNING'}, "Count must be >= 1")
            return {'CANCELLED'}

        for _ in range(count):
            bpy.ops.object.duplicate()

        self.report({'INFO'}, _tfmt("info_duplicated", context, count))
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operators — Material tools
# ═══════════════════════════════════════════════════════════════════════════ #

def _make_materials_unique_and_rename(context):
    """For every selected mesh: make materials single-user, rename to objName_matName.
       Returns the count of objects processed."""
    processed = 0
    for obj in list(context.selected_objects):
        if obj.type != 'MESH':
            continue
        for i, slot in enumerate(obj.material_slots):
            mat = slot.material
            if mat is None:
                continue
            # Detach from other users
            if mat.users > 1:
                mat = mat.copy()
                slot.material = mat
            # Rename: single material → object name; multiple → obj_mat
            if len(obj.material_slots) == 1:
                mat.name = obj.name
            else:
                mat.name = f"{obj.name}_{mat.name}"
        processed += 1
    return processed


class NST_OT_MakeMaterialsUnique(bpy.types.Operator):
    """Make each selected object's materials single-user and rename them."""
    bl_idname = "nst.make_materials_unique"
    bl_label = "Make Materials Unique & Rename"
    bl_description = "Duplicate shared materials per object and rename them to match the object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        n = _make_materials_unique_and_rename(context)
        if n == 0:
            self.report({'ERROR'}, _t("err_no_mesh_sel", context))
            return {'CANCELLED'}
        self.report({'INFO'}, _tfmt("info_mat_unique", context, n))
        return {'FINISHED'}


class NST_OT_MakeMaterialsUniqueAndMerge(bpy.types.Operator):
    """Make materials unique + rename, then join all selected meshes."""
    bl_idname = "nst.make_materials_unique_and_merge"
    bl_label = "Unique, Rename & Merge"
    bl_description = "Make materials unique, rename, then merge selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(context.selected_objects) >= 2 and \
               any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        n = _make_materials_unique_and_rename(context)
        if n == 0:
            self.report({'ERROR'}, _t("err_no_mesh_sel", context))
            return {'CANCELLED'}

        bpy.ops.object.join()
        result = context.view_layer.objects.active
        name = result.name if result else "?"
        self.report({'INFO'}, _tfmt("info_mat_unique_merge", context, name))
        return {'FINISHED'}


class NST_OT_PartSeparation(bpy.types.Operator):
    """Duplicate the shared armature, move selected meshes to the copy."""
    bl_idname = "nst.part_separation"
    bl_label = "Part Separation"
    bl_description = "Copy the shared skeleton and reassign selected meshes to it"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        if not meshes:
            self.report({'ERROR'}, _t("err_no_mesh_sel", context))
            return {'CANCELLED'}

        # Find the shared armature from the first mesh
        src_arm = None
        for mod in meshes[0].modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                src_arm = mod.object
                break
        if src_arm is None:
            self.report({'ERROR'}, _tfmt("err_no_armature", context, meshes[0].name))
            return {'CANCELLED'}

        # Verify all selected meshes use the SAME armature
        for obj in meshes[1:]:
            arm = None
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object:
                    arm = mod.object
                    break
            if arm != src_arm:
                self.report({'ERROR'}, _t("err_diff_armature", context))
                return {'CANCELLED'}

        # Duplicate the armature
        bpy.ops.object.select_all(action='DESELECT')
        src_arm.select_set(True)
        context.view_layer.objects.active = src_arm
        bpy.ops.object.duplicate()
        new_arm = context.view_layer.objects.active

        # Name the new armature
        new_name = context.scene.nst_part_arm_name.strip()
        if not new_name:
            new_name = f"{src_arm.name}_Split"
        new_arm.name = new_name
        # If Blender appended .001, try to strip it
        stripped = _BLENDER_SUFFIX_RE.sub("", new_arm.name)
        if stripped != new_arm.name and stripped not in {o.name for o in bpy.data.objects}:
            new_arm.name = stripped

        # Reassign all selected meshes to the new armature
        for obj in meshes:
            # Update armature modifier
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object == src_arm:
                    mod.object = new_arm

            # Update parent if parented to old armature
            if obj.parent == src_arm:
                # Preserve parent type (OBJECT or BONE) and world transform
                ptype = obj.parent_type
                pbone = obj.parent_bone if ptype == 'BONE' else ""
                mat = obj.matrix_world.copy()
                # Unparent
                obj.parent = None
                obj.matrix_world = mat
                # Reparent to new armature
                obj.parent = new_arm
                obj.parent_type = ptype
                if ptype == 'BONE':
                    obj.parent_bone = pbone
                obj.matrix_world = mat

        self.report({'INFO'}, _tfmt("info_part_done", context, len(meshes), new_arm.name))
        return {'FINISHED'}

class NST_OT_SeparateByMaterial(bpy.types.Operator):
    """Separate the active mesh by material; name each piece after its material."""
    bl_idname = "nst.separate_by_material"
    bl_label = "Separate by Material"
    bl_description = "Split the mesh by material slots, then name each piece by its material"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='MATERIAL')
        bpy.ops.object.mode_set(mode='OBJECT')

        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' and obj.material_slots:
                mat = obj.material_slots[0].material
                if mat:
                    obj.name = mat.name

        self.report({'INFO'}, _tfmt("info_mat_separate", context, len(context.selected_objects)))
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operator — Strip .NNN suffix
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_StripSuffix(bpy.types.Operator):
    """Remove Blender's auto .001 / .002 etc. from selected object names."""
    bl_idname = "nst.strip_suffix"
    bl_label = "Strip .NNN"
    bl_description = "Remove trailing .001 .002 etc. from selected object names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and bool(context.selected_objects)

    def execute(self, context):
        count = 0
        for obj in list(context.selected_objects):
            stripped = _BLENDER_SUFFIX_RE.sub("", obj.name)
            if stripped == obj.name:
                continue
            # Only strip if the clean name is truly free
            conflict = any(o != obj and o.name == stripped for o in bpy.data.objects)
            if not conflict:
                obj.name = stripped
                count += 1
        self.report({'INFO'}, f"Stripped .NNN from {count} object(s)")
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operators — Bone name check
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_OT_SelectNonEnglishBones(bpy.types.Operator):
    """Select bones whose names contain non-ASCII (non-English) characters."""
    bl_idname = "nst.select_non_english_bones"
    bl_label = "Select Non-English Bones"
    bl_description = "Find and select all bones with non-English characters in their names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode == 'EDIT_ARMATURE'

    def execute(self, context):
        arm_obj = context.active_object
        # Deselect all first
        for eb in arm_obj.data.edit_bones:
            eb.select = False
            eb.select_head = False
            eb.select_tail = False

        found = []
        for eb in arm_obj.data.edit_bones:
            if any(ord(c) > 127 for c in eb.name):
                eb.select = True
                eb.select_head = True
                eb.select_tail = True
                found.append(eb.name)

        if found:
            self.report({'INFO'}, _tfmt("info_non_en", context, len(found)))
        else:
            self.report({'INFO'}, _t("info_non_en_none", context))
        return {'FINISHED'}


class NST_OT_FixBoneSymbols(bpy.types.Operator):
    """Replace non-alphanumeric/underscore characters in bone names with _."""
    bl_idname = "nst.fix_bone_symbols"
    bl_label = "Fix Bone Symbols"
    bl_description = "Replace spaces, punctuation, and special characters in bone names with _"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode == 'EDIT_ARMATURE'

    def execute(self, context):
        arm_obj = context.active_object
        count = 0

        for eb in arm_obj.data.edit_bones:
            new_name = "".join(c if (c.isalnum() or c == '_') else '_' for c in eb.name)
            # Collapse multiple consecutive underscores
            while '__' in new_name:
                new_name = new_name.replace('__', '_')
            # Strip leading/trailing underscores
            new_name = new_name.strip('_')
            if not new_name:
                new_name = "Bone"

            if new_name != eb.name:
                eb.name = new_name
                count += 1

        if count:
            self.report({'INFO'}, _tfmt("info_fix_symbols", context, count))
        else:
            self.report({'INFO'}, _t("info_fix_none", context))
        return {'FINISHED'}


class NST_OT_SelectFullwidthBones(bpy.types.Operator):
    """Select bones whose names contain fullwidth / special digit characters
    (e.g. １２３ → 123)."""
    bl_idname = "nst.select_fullwidth_bones"
    bl_label = "Select Fullwidth-Digit Bones"
    bl_description = "Find and select all bones with fullwidth / special digit characters in their names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode == 'EDIT_ARMATURE'

    def execute(self, context):
        arm_obj = context.active_object
        # Deselect all first
        for eb in arm_obj.data.edit_bones:
            eb.select = False
            eb.select_head = False
            eb.select_tail = False

        found = []
        for eb in arm_obj.data.edit_bones:
            if _has_fullwidth_digit(eb.name):
                eb.select = True
                eb.select_head = True
                eb.select_tail = True
                found.append(eb.name)

        if found:
            self.report({'INFO'}, _tfmt("info_fw_digit", context, len(found)))
        else:
            self.report({'INFO'}, _t("info_fw_digit_none", context))
        return {'FINISHED'}


class NST_OT_FixFullwidthDigits(bpy.types.Operator):
    """Replace fullwidth / special digits in bone names with ASCII digits
    (e.g. １２３ → 123)."""
    bl_idname = "nst.fix_fullwidth_digits"
    bl_label = "Fix Fullwidth Digits"
    bl_description = "Convert fullwidth and special Unicode digits to standard ASCII digits in selected bone names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and context.mode == 'EDIT_ARMATURE'

    def execute(self, context):
        arm_obj = context.active_object
        count = 0

        for eb in arm_obj.data.edit_bones:
            if not eb.select:
                continue
            if _has_fullwidth_digit(eb.name):
                new_name = _fix_fullwidth_digits(eb.name)
                if new_name != eb.name:
                    eb.name = new_name
                    count += 1

        if count:
            self.report({'INFO'}, _tfmt("info_fix_fw_digit", context, count))
        else:
            self.report({'INFO'}, _t("info_fix_fw_none", context))
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════ #
#   Operator — RE MDF Export & Replace
# ═══════════════════════════════════════════════════════════════════════════ #

_MDF_VERSIONS = [
    (".10", "Devil May Cry 5 / Resident Evil 2", "mdf2.10"),
    (".13", "Resident Evil 3", "mdf2.13"),
    (".19", "Resident Evil 8", "mdf2.19"),
    (".21", "Resident Evil 2 / 3 / 7 Ray Tracing", "mdf2.21"),
    (".23", "Monster Hunter Rise", "mdf2.23"),
    (".32", "Resident Evil 4", "mdf2.32"),
    (".31", "Street Fighter 6", "mdf2.31"),
    (".40", "Dragon's Dogma 2 / Kunitsu-Gami / Dead Rising", "mdf2.40"),
    (".46", "Onimusha 2", "mdf2.46"),
    (".45", "Monster Hunter Wilds", "mdf2.45"),
    (".51", "Resident Evil 9 / Pragmata", "mdf2.51"),
    (".49", "Monster Hunter Stories 3", "mdf2.49"),
]


class NST_OT_ExportMDF(bpy.types.Operator):
    """Export MDF via RE-Mesh-Editor and replace all .mdf2.x files in a folder."""
    bl_idname = "nst.export_mdf"
    bl_label = "Export & Replace MDF"
    bl_description = "Export MDF to the chosen folder, then overwrite all .mdf2.x files there"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        scene = context.scene
        folder = scene.nst_mdf_folder.strip()
        ver = scene.nst_mdf_version  # e.g. ".32"

        if not folder:
            self.report({'ERROR'}, "Please set an export folder")
            return {'CANCELLED'}

        # Get MDF collection from our panel selection
        collection_name = scene.nst_mdf_collection.strip()
        if not collection_name or collection_name not in bpy.data.collections:
            self.report({'ERROR'}, _t("err_no_mdf_collection", context))
            return {'CANCELLED'}

        # Build export path
        import os as _os
        export_name = collection_name.rstrip(".mdf2") + ".mdf2" + ver
        filepath = _os.path.join(folder, export_name)

        # Call RE-Mesh-Editor's export function
        import sys
        exportMDFFile = None
        for mod_name, mod in sys.modules.items():
            if 'blender_re_mdf' in mod_name and hasattr(mod, 'exportMDFFile'):
                exportMDFFile = mod.exportMDFFile
                break
        if exportMDFFile is None:
            self.report({'ERROR'}, "RE Mesh Editor addon not found")
            return {'CANCELLED'}

        success = exportMDFFile(filepath, collection_name)
        if not success:
            self.report({'ERROR'}, "MDF export failed — check console for details")
            return {'CANCELLED'}

        # Read the exported file
        try:
            with open(filepath, 'rb') as f:
                exported_data = f.read()
        except OSError:
            self.report({'ERROR'}, "Failed to read exported file")
            return {'CANCELLED'}

        # Replace all .mdf2.X files in the folder
        suffix = ".mdf2" + ver
        count = 0
        for fname in _os.listdir(folder):
            if fname.endswith(suffix):
                target_path = _os.path.join(folder, fname)
                try:
                    with open(target_path, 'wb') as f:
                        f.write(exported_data)
                    count += 1
                except OSError:
                    pass

        self.report({'INFO'}, _tfmt("info_mdf_done", context, count, ver))
        return {'FINISHED'}


#   Helpers
# ═══════════════════════════════════════════════════════════════════════════ #

def _get_first_selected_name(context):
    active = context.active_object
    if active is None:
        return None
    selected = [o for o in context.selected_objects if o != active]
    return selected[0].name if selected else None


# ═══════════════════════════════════════════════════════════════════════════ #
#   UI Panel
# ═══════════════════════════════════════════════════════════════════════════ #

class NST_PT_Panel(bpy.types.Panel):
    bl_label = "NST Toolkit"
    bl_idname = "NST_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NST Toolkit"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        T = lambda k: _t(k, context)

        # ──  Language  ────────────────────────────────────────────────
        row = layout.row(align=True)
        row.label(text=T("lang_label"), icon='FILE_REFRESH')
        row.prop(scene, "nst_language", text="")

        # ──  Merge  ──────────────────────────────────────────────────
        box = layout.box()
        box.label(text=T("merge_title"), icon='AUTOMERGE_ON')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        box.prop(scene, "nst_name_template", text=T("merge_name"))

        source_name = _get_first_selected_name(context)
        if source_name:
            preview = scene.nst_name_template.replace("@n", source_name)
            box.label(text=f"→ {preview}", icon='FILE_TEXT')
        else:
            box.label(text=T("merge_preview_hint"), icon='INFO')

        box.operator("nst.merge_to_active", text=T("merge_btn"), icon='AUTOMERGE_ON')
        box.operator("nst.merge_keep_name", text=T("merge_kname_btn"), icon='FILE_TICK')

        # ──  Quick Tools  ────────────────────────────────────────────────
        box = layout.box()
        box.label(text=T("quick_title"), icon='TOOL_SETTINGS')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        row = box.row(align=True)
        row.operator("nst.strip_suffix", text=T("quick_strip"), icon='X')

        # ──  LOD Rename  ─────────────────────────────────────────────
        box = layout.box()
        box.label(text=T("lod_title"), icon='OUTLINER_DATA_GP_LAYER')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        row = box.row(align=True)
        row.prop(scene, "nst_random_format", text="")
        row.prop(scene, "nst_random_use_panel", text=T("random_use_panel"))
        row = box.row(align=True)
        if scene.nst_random_format == 'NOESIS':
            row.prop(scene, "nst_lod_num", text=T("lod_lod"))
        row.prop(scene, "nst_group_num", text=T("lod_group"))
        row.prop(scene, "nst_sub_num", text=T("lod_sub"))
        box.prop(scene, "nst_lod_suffix", text=T("lod_suffix"))
        box.prop(scene, "nst_strip_blender_suffix", text=T("lod_strip"))
        box.operator("nst.rename_lod", text=T("lod_btn"), icon='CHECKMARK')

        # Random Rename — uses the same LOD/Group/Sub numbers
        box.separator()
        row = box.row(align=True)
        row.prop(scene, "nst_random_pool", text="")
        row.operator("nst.save_name_pool", text="", icon='ADD')
        row.operator("nst.edit_name_pool", text="", icon='TEXT')
        row.operator("nst.save_name_pool_from_text", text="", icon='FILE_TICK')
        row.operator("nst.delete_name_pool", text="", icon='X')
        row.operator("nst.check_pool_dupes", text="", icon='ERROR')
        pool_name = scene.nst_random_pool
        if pool_name and pool_name != "__NONE__":
            n = len(_load_name_pool(pool_name))
            box.label(text=f"  {n} 个名字可用")
        box.operator("nst.random_rename", text=T("random_btn"))

        # ──  防脊柱移位工具  ─────────────────────────────────────────
        box = layout.box()
        box.label(text=T("bone_title"), icon='BONE_DATA')
        box.label(text=f"  {T('mode_edit_pose')}", icon='BONE_DATA')
        box.prop(scene, "nst_bone_suffix", text=T("bone_suffix"))
        row = box.row(align=True)
        row.operator("nst.bone_add_suffix", text=T("bone_add"), icon='ADD')
        row.operator("nst.bone_revert_suffix", text=T("bone_revert"), icon='LOOP_BACK')

        # Presets
        box.separator()
        row = box.row(align=True)
        row.label(text=T("bone_presets"), icon='PRESET')
        row.operator("nst.save_bone_preset", text=T("bone_save"), icon='FILE_TICK')

        presets_exist = bool(_list_preset_names())
        if presets_exist:
            row = box.row(align=True)
            row.prop(scene, "nst_active_bone_preset", text="")
            row.operator("nst.select_bone_preset", text=T("bone_select"), icon='RESTRICT_SELECT_OFF')
            row.operator("nst.delete_bone_preset", text="", icon='X')
        else:
            box.label(text=T("bone_no_presets"), icon='INFO')

        # ──  Bone Name Check  ──────────────────────────────────────────
        box = layout.box()
        box.label(text=T("bone_check_title"), icon='SORTALPHA')
        box.label(text=f"  {T('mode_edit')}", icon='EDITMODE_HLT')
        row = box.row(align=True)
        row.operator("nst.select_non_english_bones", text=T("bone_check_non_en"), icon='FILE_TEXT')
        row.operator("nst.fix_bone_symbols", text=T("bone_check_fix"), icon='CHECKMARK')
        row = box.row(align=True)
        row.operator("nst.select_fullwidth_bones", text=T("bone_check_fw_digit"), icon='VIEWZOOM')
        row.operator("nst.fix_fullwidth_digits", text=T("bone_fix_fw_digit"), icon='CHECKMARK')

        # ──  Noesis骨骼缩放转RE Mesh  ────────────────────────────────
        box = layout.box()
        box.label(text=T("spine_btn"), icon='CONSTRAINT_BONE')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        box.operator("nst.anti_spine_shift", text=T("spine_btn"), icon='CONSTRAINT_BONE')

        # ──  部件分离  ────────────────────────────────────────────────
        box = layout.box()
        box.label(text=T("part_title"), icon='MOD_ARMATURE')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        box.prop(scene, "nst_part_arm_name", text=T("part_arm_name"))
        box.operator("nst.part_separation", text=T("part_btn"), icon='UNLINKED')

        # ──  RE MDF Export  ───────────────────────────────────────────
        box = layout.box()
        box.label(text=T("mdf_title"), icon='EXPORT')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        box.prop(scene, "nst_mdf_folder", text=T("mdf_folder"))
        box.prop_search(scene, "nst_mdf_collection", bpy.data, "collections", text=T("mdf_collection"))
        box.prop(scene, "nst_mdf_version", text=T("mdf_version"))
        box.operator("nst.export_mdf", text=T("mdf_btn"), icon='FILE_TICK')
        # ──  Clean & Duplicate  ───────────────────────────────────────
        box = layout.box()
        box.label(text=T("clean_title"), icon='TRASH')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        row = box.row(align=True)
        row.operator("nst.clean_mesh", text=T("clean_btn"), icon='TRASH')
        box.separator()
        row = box.row(align=True)
        row.prop(scene, "nst_dup_count", text=T("dup_count"))
        row.operator("nst.duplicate_count", text=T("dup_btn"), icon='DUPLICATE')

        # ──  Material Tools  ────────────────────────────────────────────
        box = layout.box()
        box.label(text=T("mat_title"), icon='MATERIAL_DATA')
        box.label(text=f"  {T('mode_object')}", icon='OBJECT_DATA')
        row = box.row(align=True)
        row.operator("nst.make_materials_unique", text=T("mat_unique_btn"), icon='UNLINKED')
        row.operator("nst.make_materials_unique_and_merge", text=T("mat_unique_merge_btn"), icon='AUTOMERGE_ON')
        box.operator("nst.separate_by_material", text=T("mat_separate_btn"), icon='MOD_BOOLEAN')


# ═══════════════════════════════════════════════════════════════════════════ #
#   Registration
# ═══════════════════════════════════════════════════════════════════════════ #

classes = [
    NST_OT_MergeToActive,
    NST_OT_MergeKeepName,
    NST_OT_RenameLOD,
    NST_OT_BoneAddSuffix,
    NST_OT_BoneRevertSuffix,
    NST_OT_SaveBonePreset,
    NST_OT_SelectBonePreset,
    NST_OT_DeleteBonePreset,
    NST_OT_AntiSpineShift,
    NST_OT_SelectNonEnglishBones,
    NST_OT_FixBoneSymbols,
    NST_OT_SelectFullwidthBones,
    NST_OT_FixFullwidthDigits,
    NST_OT_CleanMesh,
    NST_OT_DuplicateCount,
    NST_OT_PartSeparation,
    NST_OT_StripSuffix,
    NST_OT_RandomRename,
    NST_OT_EditNamePool,
    NST_OT_SaveNamePoolFromText,
    NST_OT_SaveNamePool,
    NST_OT_DeleteNamePool,
    NST_OT_CheckPoolDupes,
    NST_OT_ExportMDF,
    NST_OT_MakeMaterialsUnique,
    NST_OT_MakeMaterialsUniqueAndMerge,
    NST_OT_SeparateByMaterial,
    NST_PT_Panel,
]


def register():
    _ensure_dirs()

    for cls in classes:
        bpy.utils.register_class(cls)

    # Language
    bpy.types.Scene.nst_language = bpy.props.EnumProperty(
        name="Language",
        items=[
            ("zh_CN", "中文", ""),
            ("en_US", "English", ""),
        ],
        default="zh_CN",
        description="UI language for NST Toolkit",
    )

    # Merge template
    bpy.types.Scene.nst_name_template = bpy.props.StringProperty(
        name="Name Template",
        description="Merged-object name template — @n → first selected object's name",
        default="LOD_1_Group_0_Sub_1__@n_Mat",
    )

    # LOD / Group / Sub numbers
    bpy.types.Scene.nst_lod_num = bpy.props.IntProperty(
        name="LOD", description="LOD number", default=1, min=0, soft_max=99,
    )
    bpy.types.Scene.nst_group_num = bpy.props.IntProperty(
        name="Group", description="Group number", default=0, min=0, soft_max=99,
    )
    bpy.types.Scene.nst_sub_num = bpy.props.IntProperty(
        name="Sub", description="Sub number", default=1, min=0, soft_max=99,
    )
    bpy.types.Scene.nst_lod_suffix = bpy.props.StringProperty(
        name="Suffix", description="Appended for non-LOD-format names", default="_Mat",
    )
    bpy.types.Scene.nst_strip_blender_suffix = bpy.props.BoolProperty(
        name="Strip .NNN", description="Remove Blender auto duplicate suffixes", default=True,
    )

    # Bone suffix
    bpy.types.Scene.nst_bone_suffix = bpy.props.StringProperty(
        name="Bone Suffix", description="Suffix to add / revert on selected bones", default="_dm",
    )

    # Active bone preset (dropdown, populated from JSON files on disk)
    bpy.types.Scene.nst_active_bone_preset = bpy.props.EnumProperty(
        name="Preset",
        description="Select a saved bone preset",
        items=_preset_enum_items,
    )

    # Duplicate count
    bpy.types.Scene.nst_dup_count = bpy.props.IntProperty(
        name="Count", description="Number of copies to create", default=1, min=1, soft_max=100,
    )

    # Part separation new armature name
    bpy.types.Scene.nst_part_arm_name = bpy.props.StringProperty(
        name="New Armature Name",
        description="Name for the duplicated armature (leave blank for auto)",
        default="",
    )

    # Random rename pool (text datablock)
    bpy.types.Scene.nst_random_pool = bpy.props.EnumProperty(
        name="Name Pool",
        description="Select a JSON name pool",
        items=_name_pool_enum_items,
    )

    bpy.types.Scene.nst_random_format = bpy.props.EnumProperty(
        name="Format",
        items=[
            ('NOESIS', 'Noesis', 'LOD_X_Group_Y_Sub_Z__Name_Mat'),
            ('RE_MESH', 'RE Mesh', 'Group_Y_Sub_Z__Name_Mat'),
        ],
        default='NOESIS',
    )

    bpy.types.Scene.nst_random_use_panel = bpy.props.BoolProperty(
        name="Use Panel Numbers",
        description="ON → use LOD/Group/Sub from the LOD Rename panel. OFF → reuse each object's existing numbers",
        default=False,
    )

    # MDF export
    bpy.types.Scene.nst_mdf_folder = bpy.props.StringProperty(
        name="Export Folder",
        description="Target folder for MDF export & replace",
        subtype='DIR_PATH',
        default="",
    )
    bpy.types.Scene.nst_mdf_collection = bpy.props.StringProperty(
        name="MDF Collection",
        description="Which MDF collection to export",
        default="",
    )
    bpy.types.Scene.nst_mdf_version = bpy.props.EnumProperty(
        name="Game Version",
        description="Target game version (determines .mdf2.x extension)",
        items=_MDF_VERSIONS,
        default=".32",
    )


def unregister():
    del bpy.types.Scene.nst_language
    del bpy.types.Scene.nst_name_template
    del bpy.types.Scene.nst_lod_num
    del bpy.types.Scene.nst_group_num
    del bpy.types.Scene.nst_sub_num
    del bpy.types.Scene.nst_lod_suffix
    del bpy.types.Scene.nst_strip_blender_suffix
    del bpy.types.Scene.nst_bone_suffix
    del bpy.types.Scene.nst_active_bone_preset
    del bpy.types.Scene.nst_dup_count
    del bpy.types.Scene.nst_part_arm_name
    del bpy.types.Scene.nst_random_pool
    del bpy.types.Scene.nst_random_format
    del bpy.types.Scene.nst_random_use_panel
    del bpy.types.Scene.nst_mdf_folder
    del bpy.types.Scene.nst_mdf_collection
    del bpy.types.Scene.nst_mdf_version

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
