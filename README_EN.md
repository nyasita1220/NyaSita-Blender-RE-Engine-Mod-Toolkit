# NyaSita RE Engine ToolKit (NST Toolkit)

Blender 4.5 addon. A toolbox for making MODs for RE Engine games (Resident Evil series, Devil May Cry 5, etc.)

## Installation

1. Zip the `NyaSitaToolKit` folder
2. Blender → Edit → Preferences → Add-ons → Install → select the zip → enable
3. 3D View sidebar (N key) → **NST Toolkit** tab

## Required Modes

| Label  | Meaning |
|--------|---------|
| 🟢 Object | Object Mode |
| 🟡 Edit | Edit Mode (Armature Edit) |
| 🔵 Pose | Pose Mode |

---

## Features

### Merge to Active `🟢 Object`

| Button | Description |
|--------|------------|
| **Merge by Template** | Merge selected objects into the active one, name using template. `@n` = first selected object's name |
| **Merge as Source Name** | Merge then rename to the first selected object's name |

Template example: `LOD_1_Group_0_Sub_1__@n_Mat` → result: `LOD_1_Group_0_Sub_1__Cube_Mat`

Live preview supported.

---

### LOD Rename & Random Game Mesh Name `🟢 Object`

**Batch LOD/Group/Sub editing**: select objects → change numbers → apply to selected. Supports Strip .NNN and custom suffix.

**Random naming**: randomly assign names from a name pool (JSON files stored with the addon).

| Button | Description |
|--------|------------|
| `[▼]` | Switch name pool |
| `[+]` | Create new empty name pool |
| `[📝]` | Open pool in Blender Text Editor |
| `[✓]` | Save edits back to pool |
| `[✕]` | Delete pool |
| `[❗]` | Check pool for duplicate names |

**Format options**:
- **Noesis** → `LOD_X_Group_Y_Sub_Z__Name_Mat`
- **RE Mesh** → `Group_Y_Sub_Z__Name_Mat`

**Use Panel Numbers**: ON → use LOD panel values; OFF → preserve each object's existing numbers.

**Grouping**: objects with different LOD/Group/Sub numbers but the same body name get the same random pool name, keeping their own numbers.

---

### Anti-Spine-Shift Tool `🟡 Edit / 🔵 Pose`

**Bone suffix**: select bones → add suffix / revert.

**Preset system**: save current bone selection as JSON files (`bone_presets/` folder) for one-click recall.

| Button | Description |
|--------|------------|
| **Save** | Dialog to name and save selected bones |
| `[🔘]` | Select all bones from the preset (matches bones with `_dm` suffix) |
| `[✕]` | Delete preset |

---

### Bone Name Check `🟡 Edit`

| Button | Description |
|--------|------------|
| **Select Non-English Bones** | Find and select bones with non-ASCII characters in their names |
| **Fix Symbols → _** | Replace spaces, punctuation, and special characters with `_` |

---

### Noesis Bone Scale → RE Mesh `🟢 Object`

Standalone box. One-click constraint chain: selected armature → Copy Scale Step1 → Step1 Copy Scale Step2 → bake Step2 → Step1 scale 0.01 → bake Step1.

Requires `Step1` and `Step2` armatures in the scene.

---

### Part Separation `🟢 Object`

Select meshes sharing a skeleton → duplicate the skeleton → reassign selected meshes to the new skeleton → preserve parent-child relationships. The old skeleton is kept untouched.

---

### Material Tools `🟢 Object`

| Button | Description |
|--------|------------|
| **Make Unique & Rename** | Make materials single-user copies → rename to `objectName_materialName` |
| **Unique, Rename & Merge** | Same as above + merge into one object |
| **Separate by Material** | Split by material slots → name each piece by its material |

---

### RE MDF Export `🟢 Object`

Invoke RE Mesh Editor to export MDF, then replace all `.mdf2.x` files in the target folder with the exported one.

> Requires: [RE Mesh Editor](https://github.com/NSACloud/RE-Mesh-Editor)

| Control | Description |
|---------|------------|
| **Export Folder** | Target directory for MDF export |
| **MDF Collection** | Which MDF collection to export |
| **Game Version** | Target game (determines `.mdf2.x` extension) |
| **Export & Replace All** | Export then overwrite all matching files in the folder |

---

### Clean & Duplicate `🟢 Object`

| Button | Description |
|--------|------------|
| **Clean Model** | Remove UVs/vertex groups/color attributes/materials/shape keys/all geometry → empty mesh |
| **Duplicate** | Duplicate active object N times |

---

### Quick Tools `🟢 Object`

**Strip .001**: remove Blender's auto `.001` `.002` suffixes from selected objects (skips if name would conflict).

---

### Language

Toggle between Chinese / English at the top of the panel.

## File Structure

```
NyaSita-Blender-RE-Engine-Mod-Toolkit/
├── README.md
├── README_EN.md
└── NyaSitaToolKit/          # Zip this folder for installation
    ├── __init__.py
    ├── bone_presets/        # Bone presets (JSON)
    └── name_pools/          # Name pools (JSON)
```

## Compatibility

Blender 4.5+

## Dependencies

- [RE Mesh Editor](https://github.com/NSACloud/RE-Mesh-Editor) — required for MDF export

## License

MIT
