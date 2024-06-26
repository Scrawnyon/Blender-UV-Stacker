## Blender UV Stacker
Stacks similar UVs on top of eachother to save space. Has options to automatically unwrap and pack islands

![Example](Docs/Images/Example.png)

### Usage
In Edit mode, open the N panel in the Image Editor. Tweak settings and click "Stack UVs". UV islands with the same shape will be stacked on top of eachother.<br />
Note that islands with different sizes do not stack. Enabling "Auto-Unwrap" will unwrap all meshes, which will also make the sizes match

### Requirements
Uses the bpy_extras.bmesh_utils module<br />
Tested using Blender 3.6.2