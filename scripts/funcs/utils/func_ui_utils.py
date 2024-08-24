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

import bpy


def shapekey_util_label(layout):
    layout.label(text='ShapeKey Utils')


def box_warning_slow_method(layout):
    box = layout.box()
    box.label(text=bpy.app.translations.pgettext("box_warning_slow_method_1"))
    box.label(text=bpy.app.translations.pgettext("box_warning_slow_method_2"))
    box.label(text=bpy.app.translations.pgettext("box_warning_slow_method_3"))


def box_warning_read_pref(layout):
    box = layout.box()
    box.label(text=bpy.app.translations.pgettext("box_warning_read_pref_1"))
    box.label(text=bpy.app.translations.pgettext("box_warning_read_pref_2"))

translations_dict = {
    "en_US": {
        ("*", "box_warning_slow_method_1"): "Warning: ",
        ("*", "box_warning_slow_method_2"): "If using the settings below,",
        ("*", "box_warning_slow_method_3"): "some functions may take a while in this add-on.",
        ("*", "box_warning_read_pref_1"): "You can change a setting below",
        ("*", "box_warning_read_pref_2"): " in this add-on preference.",
    },
    "ja_JP": {
        ("*", "box_warning_slow_method_1"): "注意：",
        ("*", "box_warning_slow_method_2"): "以下の項目を有効にすると",
        ("*", "box_warning_slow_method_3"): "処理に時間がかかる場合があります。",
        ("*", "box_warning_read_pref_1"): "以下の項目は",
        ("*", "box_warning_read_pref_2"): "Preference画面から設定できます。",
    },
}

def register():
    bpy.app.translations.register(__name__, translations_dict)

def unregister():
    bpy.app.translations.unregister(__name__)

