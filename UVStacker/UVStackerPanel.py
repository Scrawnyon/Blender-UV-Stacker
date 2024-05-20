bl_info = {
    "name" : "UV Stacker",
    "author" : "Combo Routine",
    "version" : (0, 0, 1),
    "blender" : (2, 80, 0),
    "location" : "Image Editor > Sidebar > UV Stacker",
    "description" : "Layers (and packs) similar UVs on top of eachother",
    "category" : "UV"
}

import bpy;
from .UVStacker import main;

# Operator
class IMAGE_OT_UVStacker(bpy.types.Operator):
    bl_idname = "object.stack_uvs";
    bl_label = "Stack UVs";
    bl_options = { "REGISTER", "UNDO" }

    def execute(self, context):
        main(
            context.scene.selectedOnly,
            context.scene.doPacking,
            context.scene.packMargin,
            context.scene.decimalAccuracy,
            context.scene.autoUnwrap);
        return { "FINISHED" };


# Panel (Sidebar > UV Stacker)
class IMAGE_PT_UVStackerPanel(bpy.types.Panel):
    bl_label = "UV Stacker";
    bl_idname = "IMAGE_EDITOR_PT_UVSTACKER"
    bl_space_type = "IMAGE_EDITOR";
    bl_region_type = "UI";
    bl_category = "UV Stacker";
    
    # TODO: MARGIN FOR PACKING
    bpy.types.Scene.selectedOnly = bpy.props.BoolProperty(
        name="Selected Only",
        description = "Only pack islands selected in the image editor",
        default = False
    );
    bpy.types.Scene.doPacking = bpy.props.BoolProperty(
        name="Do Packing",
        description = "Pack all islands to fit the UV image",
        default = True
    );
    bpy.types.Scene.packMargin = bpy.props.FloatProperty(
        name="Pack Margin",
        description = "Margin between islands when using \"Do Packing\"",
        default = 0.1,
        min = 0.0,
        max = 1.0
    );
    bpy.types.Scene.decimalAccuracy = bpy.props.IntProperty(
        name="Decimal Accuracy",
        description = "Max distance between UV verts need to be to be considered the same",
        default = 4,
        min = 1,
        max = 10
    );
    bpy.types.Scene.autoUnwrap = bpy.props.BoolProperty(
        name="Auto-Unwrap",
        description = "Individually unwrap each separate mesh before stacking/unpacking",
        default = False
    );
    
    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT';
    
    def draw(self, context):
        row = self.layout.row();
        self.layout.prop(context.scene, "selectedOnly");
        row = self.layout.row();
        self.layout.prop(context.scene, "doPacking");
        row = self.layout.row();
        self.layout.prop(context.scene, "packMargin");
        row = self.layout.row();
        self.layout.prop(context.scene, "decimalAccuracy");
        row = self.layout.row();
        self.layout.prop(context.scene, "autoUnwrap");
        
        row = self.layout.row();
        row.operator(IMAGE_OT_UVStacker.bl_idname, text = "Stack UVs", icon = "CONSOLE");


def register():
    bpy.types.Scene.selectedOnly = bpy.props.BoolProperty(name = "Selected Only", default = True);
    bpy.types.Scene.doPacking = bpy.props.BoolProperty(name = "Do Packing", default = False);
    bpy.types.Scene.packMargin = bpy.props.FloatProperty(name = "Pack Margin", default = 0.1, min = 0.0, max = 1.0);
    bpy.types.Scene.decimalAccuracy = bpy.props.IntProperty(name = "Decimal Accuracy", default = 4, min = 1, max = 10);
    bpy.types.Scene.autoUnwrap = bpy.props.BoolProperty(name = "Auto-Unwrap", default = False);
    bpy.utils.register_class(IMAGE_PT_UVStackerPanel);
    bpy.utils.register_class(IMAGE_OT_UVStacker);


def unregister():
    bpy.utils.unregister_class(IMAGE_PT_UVStackerPanel);
    bpy.utils.unregister_class(IMAGE_OT_UVStacker);
    del bpy.types.Scene.selectedOnly;
    del bpy.types.Scene.doPacking;
    del bpy.types.Scene.packMargin;
    del bpy.types.Scene.decimalAccuracy;
    del bpy.types.Scene.autoUnwrap;


if __name__ == "__main__":
    register();