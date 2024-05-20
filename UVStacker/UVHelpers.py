import bpy;
import math;
import mathutils;


def vertToLoops(vert):
    return vert.link_loops;


def getUVCenter(bmLoops, uvLayer):
    numLoops = len(bmLoops);
    if (numLoops == 0):
        return mathutils.Vector((0.0, 0.0));
    
    center = mathutils.Vector((0.0, 0.0));
    for loop in bmLoops:
        uvCoords = loop[uvLayer].uv;
        center += uvCoords;
        
    return center / numLoops;


def calculateAngle(uv1, uv2, uv3):
    vector1 = uv1 - uv2;
    vector2 = uv3 - uv2;

    # Calculate the dot product
    dot = vector1.x * vector2.x + vector1.y * vector2.y;

    # Calculate magnitudes
    magnitude1 = math.sqrt(vector1.x * vector1.x + vector1.y * vector1.y);
    magnitude2 = math.sqrt(vector2.x * vector2.x + vector2.y * vector2.y);
    
    if (magnitude1 == 0 or magnitude2 == 0):
        return 0;
    
    # Calculate cosine of angle
    cosineAngle = dot / (magnitude1 * magnitude2);
    
    if (cosineAngle < -1 or cosineAngle > 1):
        return 0;
    
    # Calculate angle in radians
    return math.acos(cosineAngle);


def rotateLoopAroundPoint(bmLoop, angle, pivot, uvLayer):
    uvCoords = bmLoop[uvLayer].uv;
    
    cos_theta = math.cos(angle);
    sin_theta = math.sin(angle);
    x = uvCoords[0] - pivot[0];
    y = uvCoords[1] - pivot[1];
    uvCoords[0] = x * cos_theta - y * sin_theta + pivot[0];
    uvCoords[1] = x * sin_theta + y * cos_theta + pivot[1];
    
    bmLoop[uvLayer].uv = uvCoords;