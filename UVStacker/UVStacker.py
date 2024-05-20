import bpy;
import bpy_extras;
import bpy_extras.bmesh_utils;
import math;
import bmesh;
import logging;
import mathutils;
import copy;
import os;
from . import UVHelpers;


class ComparableFace:
    def __init__(self, bmFace, islandCenter, uvLayer, selectedOnly, decimalAccuracy):
        self.loops = [];
        for loop in bmFace.loops:
            if (selectedOnly and loop[uvLayer].select == False):
                continue;
            
            self.loops.append(loop);
        self.uvLayer = uvLayer;
        
        # Generate distance from face center to island center
        self.faceCenter = UVHelpers.getUVCenter(self.loops, uvLayer);
        self.distFromIslandCenter = round((self.faceCenter - islandCenter).magnitude, decimalAccuracy);
        
        # Generate distsFromIslandCenter and distsFromFaceCenter
        for loop in self.loops:
            uvCoords = loop[uvLayer].uv;
            distFromIslandCenter = round((uvCoords - islandCenter).magnitude, decimalAccuracy);
            distFromFaceCenter = round((uvCoords - self.faceCenter).magnitude, decimalAccuracy);
            self.distsFromIslandCenter.append(distFromIslandCenter);
            self.distsFromFaceCenter.append(distFromFaceCenter);
        
        # Generate edgeAngles
        for loopA in self.loops:
            for loopB in self.loops:
                if (loopA.index == loopB.index):
                    continue;
                
                # Get angle from loopA to island center to loopB
                self.edgeAngles.append(UVHelpers.calculateAngle(loopA[uvLayer].uv, islandCenter, loopB[uvLayer].uv));
    

    loops = [];
    faceCenter = mathutils.Vector((0.0, 0.0));
    distFromIslandCenter = -1.0;
    distsFromFaceCenter = [];
    distsFromIslandCenter = [];
    edgeAngles = [];
    uvLayer = None;
    
    def compare(self, other):
        if (len(self.loops) != len(other.loops)):
            return False;
        if (self.distFromIslandCenter != other.distFromIslandCenter):
            return False;
        
        # Make sure dists from island center match
        availableDists = copy.copy(other.distsFromIslandCenter);
        for dist in self.distsFromIslandCenter:
            if (dist in availableDists):
                availableDists.remove(dist);
            else:
                return False;
        
        # Make sure dists from face center match
        availableDists = copy.copy(other.distsFromFaceCenter);
        for dist in self.distsFromFaceCenter:
            if (dist in availableDists):
                availableDists.remove(dist);
            else:
                return False;
        
        # Make sure edge angles match
        availableAngles = copy.copy(other.edgeAngles);
        for angle in self.edgeAngles:
            if (angle in availableAngles):
                availableAngles.remove(angle);
            else:
                return False;
        
        return True;
    
    def compareLoopUVs(self, other):
        availableLoops = copy.copy(self.loops);
        for loopOther in other.loops:
            faceMatched = False;
            for loopSelf in availableLoops:
                if (loopOther[other.uvLayer].uv != loopSelf[self.uvLayer].uv):
                    availableLoops.remove(loopSelf);
                    faceMatched = True;
                    break;
                
            if (faceMatched == False):
                return False;
        
        return True;
        
    
    def matchIndicesFrom(self, other): # Note that faces need to be aligned before this function is called
        availableLoops = copy.copy(self.loops);
        orderedLoops = [];
        for loopOther in other.loops:
            faceMatched = False;
            for loopSelf in availableLoops:
                if (loopOther[other.uvLayer].uv != loopSelf[self.uvLayer].uv):
                    availableLoops.remove(loopSelf);
                    orderedLoops.append(loopSelf);
                    faceMatched = True;
                    break;
            
            if (faceMatched == False):
                print("no match for loop for vertex " + str(loopOther.vert.index));
                break;
        
        if (len(availableLoops) > 0):
            print("Index matching between faces failed");
            return;
        
        self.loops = orderedLoops;
            

class ComparableIsland:
    def __init__(self, linkedUVIsland, islandIndex, uvLayer, selectedOnly, decimalAccuracy):
        self.comparableFaces = [];
        self.islandIndex = islandIndex;
        self.uvLayer = uvLayer;
        numFaces = len(linkedUVIsland);
        
        # Get loops
        self.loops = [];
        self.numUniqueLoops = 0;
        foundUVCoordinates = [];
        for face in linkedUVIsland:
            for loop in face.loops:
                if (selectedOnly and loop[uvLayer].select == False):
                    continue;
                
                self.loops.append(loop);
                self.initialLoopSelectedState.append(loop[uvLayer].select);
                
                # See if these UV coordinates are unique (no overlap)
                uvCoords = loop[uvLayer].uv;
                if (uvCoords in foundUVCoordinates):
                    foundUVCoordinates.append(uvCoords);
                    self.numUniqueLoops += 1;
        
        # Generate comparable faces
        self.islandCenter = UVHelpers.getUVCenter(self.loops, uvLayer);
        for face in linkedUVIsland:
            self.comparableFaces.append(ComparableFace(face, self.islandCenter, uvLayer, selectedOnly, decimalAccuracy));

    islandIndex = -1;
    islandCenter = mathutils.Vector((0.0, 0.0));
    loops = [];
    initialLoopSelectedState = [];
    numUniqueLoops = -1;
    comparableFaces = [];
    uvLayer = None;
    
    def compare(self, other):
        if (self.numUniqueLoops != other.numUniqueLoops):
            return False;
        if (len(self.loops) != len(other.loops)):
            return False;
        if (len(self.comparableFaces) != len(other.comparableFaces)):
            return False;
        
        # Make sure dists from island center match
        availableFaces = copy.copy(other.comparableFaces);
        for faceA in self.comparableFaces:
            matchFound = False;
            for faceB in availableFaces:
                if (faceA.compare(faceB)):
                    availableFaces.remove(faceB);
                    matchFound = True;
                    break;
            
            if (matchFound == False):
                return False;
        
        return True;

    def findUniqueMatchingFace(self, other):
        facesA = self.comparableFaces;
        facesB = other.comparableFaces;
        
        # Generate a list of lists, indicating which faces match
        matchesFound = [];
        i = 0;
        for faceA in facesA:
            matchesFound.append([]);
            for faceB in facesB:
                if (faceA.compare(faceB)):
                    matchesFound[i].append(faceB);
            i += 1;
        
        # Check if any match list only has one unique match
        i = 0;
        for matchList in matchesFound:
            if (len(matchList) == 1):
                return (facesA[i], matchList[0]);
            i += 1;
        
        # If unique match wasn't found, return null
        return (None, None);
    
    def matchIndicesFrom(self, other): # Note that faces need to be aligned before this function is called
        availableFaces = copy.copy(self.comparableFaces);
        orderedFaces = [];
        for faceOther in other.comparableFaces:
            faceMatched = False;
            for faceSelf in availableFaces:
                if (faceOther.compareLoopUVs(faceSelf)):
                    faceSelf.matchIndicesFrom(faceOther);
                    availableFaces.remove(faceSelf);
                    orderedFaces.append(faceSelf);
                    faceMatched = True;
                    break;
            
            if (faceMatched == False):
                print("no match for face");
        
        if (len(availableFaces) > 0):
            print("Index matching between indexes failed");
            return;
        
        self.comparableFaces = orderedFaces;
    
    def returnInitialLoopSelectedStates(self):
        i = 0;
        length = len(self.loops);
        while (i < length):
            self.loops[i][self.uvLayer].select = self.initialLoopSelectedState[i];
            i += 1;


def main(selectedOnly, doPacking, packMargin, decimalAccuracy, autoUnwrap):
    # Clear console
    if os.name == "nt":
        os.system("cls");
    else:
        os.system("clear");
    
    # Make sure we're in edit mode
    if (bpy.context.active_object.mode != 'EDIT'):
        bpy.ops.object.mode_set(mode = 'EDIT');
    if (selectedOnly == False):
        bpy.ops.mesh.select_all(action = 'SELECT');

    # Get the active object and its mesh
    activeObj = bpy.context.object;
    bMesh = bmesh.from_edit_mesh(activeObj.data);
    
    # Get UV islands
    uvLayer = bMesh.loops.layers.uv.active;
    linkedUVIslands = bpy_extras.bmesh_utils.bmesh_linked_uv_islands(bMesh, uvLayer); # Returns lists of faces connected by UV islands
    
    # Unwrap mesh
    if (autoUnwrap):
        bpy.ops.mesh.select_all(action = 'DESELECT');
        for island in linkedUVIslands:
            singleVert = island[0].loops[0].vert;
            singleVert.select = True;
            bpy.ops.mesh.select_linked();
            bpy.ops.uv.unwrap();
            bpy.ops.mesh.select_all(action = 'DESELECT');
        bpy.ops.mesh.select_all(action = 'SELECT');
        
    activeObj.data.update();
    linkedUVIslands = bpy_extras.bmesh_utils.bmesh_linked_uv_islands(bMesh, uvLayer);

    # Generate comparable islands
    islands = [];
    i = 0;
    for linkedUVIsland in linkedUVIslands:
        islands.append(ComparableIsland(linkedUVIsland, i, uvLayer, selectedOnly, decimalAccuracy));
        newIslandIndex = len(islands) - 1;
        if (len(islands[newIslandIndex].loops) == 0):
            del islands[newIslandIndex];
        i += 1;
    
    # Generate groups that contain all matching islands
    i = 0;
    matchingIslandLists = []; # Group matching islands in this list of lists
    doesIslandHaveGroup = {};
    numIslands = len(islands);
    while (i < numIslands):
        # If this island hasn't been matched with anything yet, generate a group for it
        matchingIslandLists.append([]);
        if (i in doesIslandHaveGroup) == False:
            matchingIslandLists[i].append(islands[i]);
            doesIslandHaveGroup[i] = True;
            
        ii = i + 1;
        while (ii < numIslands):
            if (ii in doesIslandHaveGroup):
                ii += 1;
                continue;
            
            if (islands[i].compare(islands[ii])):
                # If islands match, add island B to list of matching islands
                print("island " + str(i) + " matches island " + str(ii));
                if (islands[ii] in matchingIslandLists[i]) == False:
                    matchingIslandLists[i].append(islands[ii]);
                    doesIslandHaveGroup[ii] = True;
            else:
                print("island " + str(i) + " doesnt match island " + str(ii));
            
            ii += 1;
        i += 1;
    
    # Match all islands' position and rotation to the first island of the group
    for islandList in matchingIslandLists:
        i = 0;
        for island in islandList:
            if (i < len(islandList) - 1):
                islandA = islandList[i];
                islandB = islandList[i + 1];
                
                # Find a face that has only one matching face in the other island. Use this to calculate rotation
                matchingFaces = islandA.findUniqueMatchingFace(islandB);
                if (matchingFaces != (None, None)):
                    # Generate rotation and position differences between the two islands
                    UVCenterA = islandA.islandCenter;
                    UVCenterB = islandB.islandCenter;
                    rotOffset = (matchingFaces[0].faceCenter - UVCenterA).angle_signed(matchingFaces[1].faceCenter - UVCenterB);
                    islandCenterOffset = UVCenterA - UVCenterB;
                    
                    # Rotate and offset all loops to match island A
                    for loop in islandA.loops:
                        if (selectedOnly and loop[uvLayer].select == False):
                            continue;
                        
                        UVHelpers.rotateLoopAroundPoint(loop, -rotOffset, UVCenterA, uvLayer);
                        loop[uvLayer].uv -= islandCenterOffset;
                    
                    # Now that the islands are on top of eachother, make sure the face/loop orders are the same, so
                    # we can easily match UV positions after packing
                    islandB.matchIndicesFrom(islandList[0]);
                
            i += 1;
    
    # Pack islands
    if (doPacking):
        # Select the first islands of each group for packing
        bpy.ops.uv.select_all(action = 'DESELECT');
        for islandList in matchingIslandLists:
            if (len(islandList) == 0):
                continue;
            
            for loop in islandList[0].loops:
                loop[uvLayer].select = True;
        
        # Pack selected islands
        bpy.ops.uv.pack_islands(margin = packMargin);
    
    # Return the selected states for all loops
    for island in islands:
        island.returnInitialLoopSelectedStates();
    
    # Now match the remaining islands to the packed versions
    for islandList in matchingIslandLists:
        if (len(islandList) == 0):
            continue;
        
        parentIsland = islandList[0];
        i = 1;
        while i < len(islandList):
            childIsland = islandList[i];
            ii = 0;
            print("Matching island " + str(childIsland.islandIndex) + " to island " + str(parentIsland.islandIndex));
            for loop in childIsland.loops:
                if (selectedOnly and loop[uvLayer].select == False):
                    continue;
                
                loop[uvLayer].uv = parentIsland.loops[ii][uvLayer].uv;
                ii += 1;
            i += 1;
    
    # Update object data
    activeObj.data.update();