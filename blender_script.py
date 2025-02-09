import bpy
import math
import os

def create_plane(name, location, size):
    """
    创建一个切割平面。
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    plane = bpy.context.object
    plane.name = name
    return plane

# 设置输出分辨率
id = 1
resolution = 2048
bpy.context.scene.render.resolution_x = resolution
bpy.context.scene.render.resolution_y = resolution
bpy.context.scene.render.resolution_percentage = 100  # 确保百分比为100%

bpy.context.scene.world.use_nodes = False
bpy.context.scene.world.color = (0, 0, 0)
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'


# 假设已经导入了你的OBJ文件
original_obj = bpy.data.objects[0]  # 获取第一个导入的对象作为原对象
original_name = original_obj.name

# 设置相机和渲染设置
camera = bpy.data.objects['Camera']
camera.location = (0, 0, 20)  # 根据实际情况调整位置
camera.rotation_euler = (0, 0, math.radians(0))  # 相机朝向Z轴负方向
    

def get_cut_plane_image(z_height, idx):
            
    # 创建一个垂直于Z轴的切割平面（位于Z=0处）
    cut_height = z_height  # 调整此值以改变切片高度
    plane_size = 6  # 根据需要调整平面大小，确保覆盖整个模型
    cut_plane = create_plane("CutPlane", (0, 0, cut_height), plane_size)

    # 设置平面旋转使其垂直于Z轴
    cut_plane.rotation_euler = (0, 0, math.radians(90))

    # 对复制的对象添加布尔修改器
    bool_mod = cut_plane.modifiers.new(type="BOOLEAN", name="Slice")
    bool_mod.operation = 'INTERSECT'
    bool_mod.object = original_obj

    # 应用修改器
    bpy.context.view_layer.objects.active = cut_plane
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)

    original_obj.hide_render = True  # 在渲染时隐藏原始模型
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
            
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)

    # 渲染设置
    output_dir = f"D:\\code\\3dobj\\{id}\\{resolution}"  # 替换为你的输出路径
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_filename = f"{idx}_{z_height}.png"
    output_path = os.path.join(output_dir, output_filename)
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    # 删除切割平面
    bpy.ops.object.select_all(action='DESELECT')
    cut_plane.select_set(True)
    bpy.context.view_layer.objects.active = cut_plane
    bpy.ops.object.delete(use_global=False)

    
import numpy as np
z_seq = np.linspace(-2.3, 4.1, 200)

for idx, z in enumerate(z_seq):
    get_cut_plane_image(z, idx)

print("Finished")
