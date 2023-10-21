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
import importlib
import os
import re
from glob import glob


bl_info = {
    "name": "ShapeKeys Util",
    "author": "@sleetcat123(Twitter)",
    "version": (1, 1, 6),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "category": "Object"
}

loaded_modules = {}


def register_module(module):
    func = getattr(module, "register", None)
    if callable(func):
        func()


def unregister_module(module):
    func = getattr(module, "unregister", None)
    if callable(func):
        func()


def register():
    path = os.path.dirname(__file__)
    # print(path)
    module_files = glob(f'{path}/scripts/**/*.py', recursive=True)
    regex = re.compile(r"[\\/]")
    module_names = [regex.sub('.', p[len(path):-3]) for p in module_files]
    # print(module_names)
    for module_name in module_names:
        if module_name in loaded_modules:
            module = loaded_modules[module_name]
            module = importlib.reload(module)
            # print("reload: " + str(module))
        else:
            module = importlib.import_module(module_name, package=__package__)
            loaded_modules[module_name] = module
        register_module(module)


def unregister():
    global loaded_modules
    for module in loaded_modules.values():
        unregister_module(module)
        try:
            importlib.reload(module)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    register()
