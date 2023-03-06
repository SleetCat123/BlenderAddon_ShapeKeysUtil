import bpy
from . import consts


def apply_as_shapekey(modifier):
    try:
        # 名前の文字列から%AS%を削除する
        modifier.name = modifier.name[len(consts.APPLY_AS_SHAPEKEY_PREFIX):len(modifier.name)]
        # Apply As Shape
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
    except RuntimeError:
        # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
        print("!!! Apply as shapekey failed !!!: [{0}]".format(modifier.name))
        bpy.ops.object.modifier_remove(modifier=modifier.name)
    else:
        try:
            print("Apply as shapekey: [{0}]".format(modifier.name))
        except UnicodeDecodeError:
            print("Apply as shapekey")
