import bpy
import bmesh
from . import func_utils


# 指定座標を基準にSide of Active
def select_axis_from_point(point=(0, 0, 0), mode='POSITIVE', axis='X', threshold=0.0001):
    obj = func_utils.get_active_object()
    if obj.type != 'MESH':
        return

    bpy.ops.object.mode_set(mode='EDIT')
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    # 頂点選択を有効化
    temp_select_mode = bm.select_mode
    bm.select_mode = {'VERT'}

    bpy.ops.mesh.select_all(action='DESELECT')
    # 一時的に頂点を追加し、それを基準にSide of Activeを使う
    v = bm.verts.new(point)
    func_utils.select_object(v, True)
    bm.select_history.add(v)
    func_utils.select_axis(mode=mode, axis=axis, threshold=threshold)
    # 追加した頂点を削除
    bmesh.ops.delete(bm, geom=[v], context='VERTS')

    bm.select_mode = temp_select_mode

    bmesh.update_edit_mesh(mesh=me, loop_triangles=False, destructive=True)
    # bpy.ops.object.mode_set(mode='OBJECT')
