# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "ShapeKeys Util",
    "author": "@sleetcat123(Twitter)",
    "version": (1, 1, 6),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "category": "Object"
}


def reload():
    import importlib
    for file in files:
        importlib.reload(file)


try:
    is_loaded
    reload()
except NameError:
    from .scripts import (
        addon_preferences,
        consts,
        link_with_AutoMerge,
        link_with_MizoresCustomExporter,
        menu_edit_mesh_context,
        menu_object_context,
        translations,
    )
    from BlenderAddon_ShapeKeysUtil.scripts.funcs import (
        func_select_axis_from_point,
        func_apply_modifiers_with_shapekeys,
        func_separate_shapekeys,
        func_separate_lr_shapekey_all,
        func_separate_lr_shapekey,
        func_apply_as_shapekey,
        func_apply_modifiers,
    )
    from BlenderAddon_ShapeKeysUtil.scripts.funcs.utils import (
        func_object_utils,
        func_package_utils,
        func_mesh_utils,
        func_collection_utils,
        func_ui_utils,
    )
    from BlenderAddon_ShapeKeysUtil.scripts.ops import (
        op_apply_modifiers, op_separate_lr_shapekey,
        op_sideofactive_point,
        op_separate_lr_shapekey_all_tag_detect, op_assign_lr_shapekey_tag, op_separate_lr_shapekey_all,
        op_separate_shapekeys,
    )

files = [
    addon_preferences,
    consts,
    func_apply_as_shapekey,
    func_apply_modifiers,
    func_apply_modifiers_with_shapekeys,
    func_package_utils,
    func_select_axis_from_point,
    func_separate_lr_shapekey,
    func_separate_lr_shapekey_all,
    func_separate_shapekeys,
    func_object_utils,
    func_package_utils,
    func_mesh_utils,
    func_collection_utils,
    func_ui_utils,
    link_with_AutoMerge,
    link_with_MizoresCustomExporter,
    menu_edit_mesh_context,
    menu_object_context,
    op_apply_modifiers,
    op_assign_lr_shapekey_tag,
    op_separate_lr_shapekey,
    op_separate_lr_shapekey_all,
    op_separate_lr_shapekey_all_tag_detect,
    op_separate_shapekeys,
    op_sideofactive_point,
    translations,
]

is_loaded = False


def register():
    global is_loaded
    if is_loaded:
        reload()
    for file in files:
        func = getattr(file, "register", None)
        if callable(func):
            func()
    is_loaded = True


def unregister():
    for file in files:
        func = getattr(file, "unregister", None)
        if callable(func):
            func()


if __name__ == "__main__":
    register()
