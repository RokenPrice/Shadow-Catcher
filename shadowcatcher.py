bl_info = {
 "name": "Shadow Catcher",
 "author": "Steve Hargreaves (Roken)",
 "version": (1, 0),
 "blender": (2, 7, 7),
 "location": "View3D > Tools > Shadow Catcher",
 "description": "Enables/Disables the shadow catcher and background",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "Render"}
import bpy
import io, sys, os

class CyclesShadowCatcher(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Shadow Catcher"
    bl_idname = "OBJECT_PT_Shadow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Shadow Catcher"

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)

        row = layout.row()
        row.prop(scene, "enable")

        row = layout.row()
        row.prop(scene, "background")
        
        row = layout.row()
        row.prop(scene, "image")

def setupscenes():
    def_scene = bpy.context.scene
    def_scene.name = "Scene"
    main_layer = bpy.data.scenes["Scene"].render.layers.new(name = "Main")
    main_layer = bpy.data.scenes["Scene"].render.layers.new(name = "Shadow")
    main_layer = bpy.data.scenes["Scene"].render.layers.new(name = "Shadow Clean")
    bpy.ops.scene.render_layer_remove()
    
    background_scene = bpy.ops.scene.new(type = "EMPTY")
    bg_scene = bpy.context.scene
    bg_scene.name = "Scene Background"
    bg_layer = bpy.data.scenes["Scene Background"].render.layers.new(name = "Background")
    bpy.ops.scene.render_layer_remove()
    bpy.data.scenes["Scene Background"].cycles.samples = 1
    #bpy.data.scenes["Scene Background"].render.layers["RenderLayer"].use = False
 
    #Main layer   
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene Background"].render.layers["Background"].layers[layer] = False

    for layer in range (1, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Main"].layers[layer] = False
        
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Main"].layers_exclude[layer] = False
        
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Main"].layers_zmask[layer] = False

    #Shadow layer   
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow"].layers[layer] = False

    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow"].layers[layer] = False
                    
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow"].layers_exclude[layer] = False
        
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow"].layers_zmask[layer] = False
    
    bpy.data.scenes["Scene"].render.layers["Shadow"].layers[1] = True
    bpy.data.scenes["Scene"].render.layers["Shadow"].layers[19] = False
    
    #Clean Shadow layer   
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers[layer] = False

    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers[layer] = False
                    
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers_exclude[layer] = False
        
    for layer in range (0, len(bpy.context.scene.layers)):
        bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers_zmask[layer] = False
    
    bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers[1] = True
    bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers[19] = False
    bpy.data.scenes["Scene"].render.layers["Shadow Clean"].layers_exclude[0] = True
    
    bpy.context.screen.scene = bpy.data.scenes["Scene"]
    cam = bpy.context.scene.camera
    world = bpy.context.screen.scene.world
        
    cam_tx = cam.location.x
    cam_ty = cam.location.y
    cam_tz = cam.location.z
    cam_data = cam.data
    bpy.context.screen.scene = bpy.data.scenes["Scene Background"]
    bg_cam = bpy.data.cameras.new("BG Camera")
    bg_cam_ob = bpy.data.objects.new("Camera", bg_cam)
    bpy.context.scene.objects.link(bg_cam_ob)
    bg_cam_ob.location.x = cam_tx
    bg_cam_ob.location.y = cam_ty
    bg_cam_ob.location.z = cam_tz
    bg_cam_ob.rotation_euler = cam.rotation_euler
    bg_cam_ob.data = cam_data
        
    bpy.context.screen.scene.world = world
    
    bpy.context.screen.scene = bpy.data.scenes["Scene"]
    
    return

def setcomp():
    #Switch on nodes
    global bgon
    global imageon
    global firstrun
    global background_node
    global image_node
    global mix_node
    global comp_node_main
    global main_node
    global alpha_node
    global blur_node
    global value_node
    bpy.context.scene.use_nodes = True
    comptree = bpy.context.scene.node_tree
    complinks = comptree.links
    if firstrun is True:
        comptree = bpy.context.scene.node_tree
        complinks = comptree.links
        
        # clear default nodes
        for node in comptree.nodes:
            comptree.nodes.remove(node)
        
        # create input image node
        main_node = comptree.nodes.new(type='CompositorNodeRLayers')
        main_node.location = 0,0
        main_node.scene = bpy.data.scenes['Scene']
        main_node.layer="Main"

        subtract_node = comptree.nodes.new(type='CompositorNodeMixRGB')
        subtract_node.location = 400,0
        subtract_node.blend_type = 'SUBTRACT'
        
        blur_node = comptree.nodes.new(type = "CompositorNodeBlur")
        blur_node.location = 600,0
        blur_node.use_custom_color = True
        blur_node.color = (0, 153, 0)
        
        mix_node = comptree.nodes.new(type = 'CompositorNodeMixRGB')
        mix_node.location = 1100,-100
        mix_node.blend_type = 'MULTIPLY'
        mix_node.use_custom_color = True
        mix_node.color = (0, 153, 0)
        
        invert_node = comptree.nodes.new(type = 'CompositorNodeInvert')
        invert_node.location = 500,0
        
        RGB1_node = comptree.nodes.new(type = 'CompositorNodeCurveRGB')
        RGB1_node.location = 700,0
        RGB1_node.use_custom_color = True
        RGB1_node.color = (0, 153, 0)

        value_node = comptree.nodes.new(type = "CompositorNodeValue")
        value_node.location = 700,150
        value_node.use_custom_color = True
        value_node.color = (0, 153, 0)
        
        shadow_node = comptree.nodes.new(type='CompositorNodeRLayers')
        shadow_node.location = 100,100
        shadow_node.scene = bpy.data.scenes['Scene']
        shadow_node.layer="Shadow"
        
        clean_node = comptree.nodes.new(type='CompositorNodeRLayers')
        clean_node.location = 200,200
        clean_node.scene = bpy.data.scenes['Scene']
        clean_node.layer="Shadow Clean"
        
        background_node = comptree.nodes.new(type='CompositorNodeRLayers')
        background_node.location = -100,200
        background_node.scene = bpy.data.scenes['Scene Background']
        background_node.layer="Background"
        background_node.use_custom_color = True
        background_node.color = (0, 153, 0)
        
        image_node = comptree.nodes.new(type='CompositorNodeImage')
        image_node.location = -300,200
        image_node.use_custom_color = True
        image_node.color = (0, 153, 0)
        
        alpha_node = comptree.nodes.new(type = 'CompositorNodeAlphaOver')
        alpha_node.location = 1300,100
        
        # create output node
        comp_node_main = comptree.nodes.new('CompositorNodeComposite')   
        comp_node_main.location = 1500,0
        # link nodes
        link = complinks.new(shadow_node.outputs[0], subtract_node.inputs[2])
        link = complinks.new(clean_node.outputs[0], subtract_node.inputs[1])
        link = complinks.new(subtract_node.outputs[0], blur_node.inputs[0])
        link = complinks.new(blur_node.outputs[0], invert_node.inputs[1])
        link = complinks.new(invert_node.outputs[0], RGB1_node.inputs[1])    
        link = complinks.new(RGB1_node.outputs[0], mix_node.inputs[2])
        link = complinks.new(value_node.outputs[0], mix_node.inputs[0])
        link = complinks.new(mix_node.outputs[0], alpha_node.inputs[1])
        link = complinks.new(main_node.outputs[0], alpha_node.inputs[2])
        link = complinks.new(alpha_node.outputs[0], comp_node_main.inputs[0])
    if bpy.data.scenes["Scene"].background is True:
        link = complinks.new(background_node.outputs[0], mix_node.inputs[1])
        bgon = True
        imageon = False
    if bpy.data.scenes["Scene"].image is True:
        link = complinks.new(image_node.outputs[0], mix_node.inputs[1])
        imageon = True
        bgon = False
    if bpy.data.scenes["Scene"].enable is False:
        link = complinks.new(main_node.outputs[0], comp_node_main.inputs[0])
    else:
        link = complinks.new(alpha_node.outputs[0], comp_node_main.inputs[0])
    if bpy.data.scenes["Scene"].background is False:
        if bgon is True:
            link = complinks.remove(background_node.outputs[0].links[0])
            bgon = False
        mix_node.inputs[1].default_value[3]=0
    if bpy.data.scenes["Scene"].image is False:
        if imageon is True:
            link = complinks.remove(image_node.outputs[0].links[0])
            imageon = False
        mix_node.inputs[1].default_value[3]=0
    return(complinks)

def shadowtoggle(self, context):
    global firstrun
    global bgon
    global imageon
    if firstrun is True:
        if bpy.data.scenes["Scene"].enable is True:
            setupscenes()
    setcomp()
    firstrun = False
    bpy.data.scenes["Scene"].render.layers["Shadow"].use = bpy.data.scenes["Scene"].enable
    bpy.data.scenes["Scene"].render.layers["Shadow Clean"].use = bpy.data.scenes["Scene"].enable
    bpy.data.scenes["Scene"].cycles.film_transparent = bpy.data.scenes["Scene"].enable
    bpy.data.scenes["Scene"].render.layers["Main"].layers[1]=abs(bpy.data.scenes["Scene"].enable-1)
    
    if bpy.data.scenes["Scene"].enable is False:
        bpy.data.scenes["Scene Background"].render.layers["Background"].use = False
    else:
        bpy.data.scenes["Scene Background"].render.layers["Background"].use = bpy.data.scenes["Scene"].background
    return

def backgroundtoggle(self, context):
    global bgon
    global imageon
    bpy.data.scenes["Scene Background"].render.layers["Background"].use = bpy.data.scenes["Scene"].background
    bpy.data.scenes["Scene Background"].cycles.film_transparent = abs(bpy.data.scenes["Scene"].background-1)
    if bpy.data.scenes["Scene"].image is True:
        bpy.data.scenes["Scene"].image =  abs(bpy.data.scenes["Scene"].background-1)
    setcomp()
    return 

def imagetoggle(self, context):
    global bgon
    global imageon
    if bpy.data.scenes["Scene"].background is True:
        bpy.data.scenes["Scene"].background = abs(bpy.data.scenes["Scene"].image-1)
    setcomp()
    return

def register():
    global firstrun
    global bgon
    global imageon
    firstrun = True
    bpy.types.Scene.enable = bpy.props.BoolProperty(
        name="Enable or Disable", 
        description="Enable Shadow Catcher", 
        default=0,
        update=shadowtoggle
        )

    bpy.types.Scene.background = bpy.props.BoolProperty(
        name="Enable or Disable background", 
        description="Enable background", 
        default=0,
        update = backgroundtoggle
        )
        
    bpy.types.Scene.image = bpy.props.BoolProperty(
        name="Enable or Disable image", 
        description="Enable image", 
        default=0,
        update = imagetoggle
        )
    bgon = False
    imageon = False
    bpy.utils.register_class(CyclesShadowCatcher)

def unregister():
    bpy.utils.unregister_class(CyclesShadowCatcher)

if __name__ == "__main__":
    register()


