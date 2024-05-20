bl_info = {
    "name" : "UV Stacker",
    "author" : "Combo Routine",
    "version" : (0, 0, 1),
    "blender" : (2, 80, 0),
    "location" : "Image Editor > Sidebar > UV Stacker",
    "description" : "Layers (and packs) similar UVs on top of eachother",
    "category" : "UV"
}

from . import UVStacker;
from . import UVStackerPanel;
from . import UVHelpers;

def register():
    UVStackerPanel.register();

def unregister():
    UVStackerPanel.unregister();

if __name__ == "__main__":
    register();