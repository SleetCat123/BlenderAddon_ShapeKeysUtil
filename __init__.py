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

import sys
import importlib

bl_info = {
    "name": "ShapeKeys Util",
    "author": "@sleetcat123(Twitter)",
    "version": (1, 1, 6),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "category": "Object"
}

imports = [
    "ShapeKeysUtil",
]


def reload_modules():
    for name in imports:
        module_full_name = f"{__package__}.{name}"
        if module_full_name in sys.modules:
            importlib.reload(sys.modules[module_full_name])
        else:
            importlib.import_module(module_full_name)


def register():
    reload_modules()
    for script in imports:
        module_name = f"{__package__}.{script}"
        module = sys.modules[module_name]
        func = getattr(module, "register", None)
        if callable(func):
            func()


def unregister():
    for script in imports:
        module_name = f"{__package__}.{script}"
        module = sys.modules[module_name]
        func = getattr(module, "unregister", None)
        if callable(func):
            func()


if __name__ == "__main__":
    register()
