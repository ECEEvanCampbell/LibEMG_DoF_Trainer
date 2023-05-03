import bpy
from math import radians
import shutil
import os
import sys
import pip
try:
    from PIL import Image
except:
    pip.main(["install", "Pillow", "--target", (sys.exec_prefix)+"\\lib\\site-packages"])
    from PIL import Image
try:
    import imageio
except:
    pip.main(["install", "imageio", "--target", (sys.exec_prefix)+"\\lib\\site-packages"])
    import imageio
try:
    import numpy as np
except:
    pip.main(["install", "numpy", "--target", (sys.exec_prefix)+"\\lib\\site-packages"])
    import numpy as np

position_dictionary = {
    "neutral": {# keys are all given for the LEFT SIDE -- to get right side multiply x-location by -1
        "IK Arm Pole":   [(radians(0),radians(0),radians(0)),     (0.617,-0.385,-0.255)], # rotation, location
        "IK Arm Target": [(radians(90), radians(0), radians(20)), (0.350, -0.620, 0.435)], # rotation, location
        },
    "flexion": { # flexion and extension are considered "positions" because they describe how you'd orient your hand to interface w/ an object.
        "IK Arm Pole":   [(radians(0),radians(0),radians(0)),     (0.617,-0.385,-0.255)], # rotation, location
        "IK Arm Target": [(radians(150), radians(-15), radians(10)), (0.350, -0.620, 0.435)], # rotation, location
        },
    "extension": {
        "IK Arm Pole":   [(radians(0),radians(0),radians(0)),     (0.617,-0.385,-0.255)], # rotation, location
        "IK Arm Target": [(radians(33.3), radians(15), radians(10)), (0.350, -0.620, 0.435)], # rotation, location
    } # TODO: add supination, pronation
    # TODO: break out IK arm pole and IK arm target to different dictionaries.
    # we'd be able to have IK arm pole for things like ( --l  vs i_ limb positions)
    # we can add more positions -- like from my confounding factors paper!
    
}
gesture_dictionary = {
    "nomotion": {# keys are all given for the LEFT SIDE -- to get right side multiply x-location by -1
        "Pinky1":        [(radians(3),radians(0),radians(-20)),   (0,0,0)],
        "Ring1":         [(radians(3),radians(0),radians(-20)),   (0,0,0)],
        "Middle1":       [(radians(3),radians(0),radians(-20)),   (0,0,0)],
        "Index1":        [(radians(3),radians(0),radians(-20)),   (0,0,0)],
        "Thumb2":        [(radians(-22),radians(-5),radians(8)),  (0,0,0)]
        },
    "powergrip": {
        "Pinky1":        [(radians(3),radians(10),radians(-65)),   (0,0,0)],
        "Ring1":         [(radians(3),radians(8.5),radians(-65)),   (0,0,0)],
        "Middle1":       [(radians(7),radians(6),radians(-70)),   (0,0,0)],
        "Index1":        [(radians(8),radians(4),radians(-65)),   (0,0,0)],
        "Thumb2":        [(radians(-55),radians(-20),radians(20)),  (0,0,0)]
    },
    "handopen": {
        "Pinky1":        [(radians(-33),radians(-2),radians(-5)),   (0,0,0)],
        "Ring1":         [(radians(-10),radians(-3),radians(-2)),   (0,0,0)],
        "Middle1":       [(radians(7),radians(0),radians(0)),   (0,0,0)],
        "Index1":        [(radians(33),radians(6),radians(8)),   (0,0,0)],
        "Thumb2":        [(radians(8),radians(-17),radians(7)),  (0,0,0)]
    },
    "keygrip": {
        "Pinky1":        [(radians(8),radians(4),radians(-60)),   (0,0,0)],
        "Ring1":         [(radians(8),radians(4),radians(-60)),   (0,0,0)],
        "Middle1":       [(radians(8),radians(4),radians(-60)),   (0,0,0)],
        "Index1":        [(radians(8),radians(4),radians(-60)),   (0,0,0)],
        "Thumb2":        [(radians(-60),radians(5),radians(-20)),  (0,0,0)]
    } # TODO: add more gestures -- pinch grip, key grip, finger guns, okay, peace, hang loose.

}

FPS=24

def clear_frames():
    context = bpy.context
    for ob in context.selected_objects:
        ob.animation_data_clear()



def add_keyframe(position, gesture, side, seconds=0, total_frames=0):
    total_frames = total_frames  + 24*seconds
    rig = bpy.data.objects["Armature"]
    rig_gesture = gesture_dictionary[gesture]
    rig_position = position_dictionary[position]
    for key in rig_position:
        rig.pose.bones[key+"."+side].rotation_euler = rig_position[key][0]                      
        rig.pose.bones[key+"."+side].keyframe_insert("rotation_euler", frame=total_frames)
        if side == "R":
            tmp = list(rig_position[key][1])
            tmp[0] = tmp[0]*-1
            tmp = tuple(tmp)
        else:
            tmp = rig_position[key][1]
        rig.pose.bones[key+"."+side].location = tmp
        rig.pose.bones[key+"."+side].keyframe_insert("location", frame=total_frames)
    for key in rig_gesture:
        if side == "R":
            tmp = list(rig_gesture[key][0])
            tmp[2] = tmp[2]*-1
            tmp = tuple(tmp)
        else:
            tmp = rig_gesture[key][0]
        rig.pose.bones[key+"."+side].rotation_euler = tmp                          
        rig.pose.bones[key+"."+side].keyframe_insert("rotation_euler", frame=total_frames)
    label = bpy.data.objects["GestureLabel"]
    
        
    return  total_frames



def initial_keyframe(position,gesture,side):
   return add_keyframe(position, gesture, side)

def capture_animation(camera_name="Head-On Camera"):
    # check if actions are empty
    if bpy.data.actions:
        # get all actions
        action_list = [action.frame_range for action in bpy.data.actions]
        # sort, remove doubles and create a set
        keys = (sorted(set([item for sublist in action_list for item in sublist])))
        
        print(keys)
        
        print("{} {}".format("first keyframe: ", keys[0]))
        print("{} {}".format("last keyframe: ", keys[-1]))
        
        # set starting frame:
        scn = bpy.context.scene
        scn.frame_start = int(keys[0])
        scn.frame_end   = int(keys[-1])
        
        camera = bpy.data.objects[camera_name]
        bpy.context.scene.camera = camera
        
        # adjust render settings to match camera settings
        bpy.context.scene.render.resolution_x = int(camera.data.sensor_width * bpy.context.scene.render.resolution_y / camera.data.sensor_height)
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.render.use_file_extension = True
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        
        # Create an animation for the bone
        curpath = bpy.path.abspath("//")
        folder = os.path.abspath(curpath + "tmp_frames")
        if os.path.isdir(folder):
            shutil.rmtree(folder)  
        os.mkdir(folder)
        for i in range(scn.frame_start, scn.frame_end):
            bpy.context.scene.frame_set(i)

            # Save the rendered image as a PNG file
            file_path = os.path.join(folder, f"frame_{i:04d}.png")
            bpy.context.scene.render.filepath = file_path
            bpy.ops.render.render(write_still=True)
    else:
        print("no actions")
    

def get_class_label(class_dictionary, compound_class):
    class_label = np.zeros((1, class_dictionary["ndim"][0]))
    if compound_class == ["neutral","nomotion"]:
        return class_label
    component_classes = []
    for key in [key for key in class_dictionary if len(class_dictionary[key])==2]:
        if key in compound_class:
            component_classes.append(class_dictionary[key])
    for endpoint in component_classes:
        class_label[0,endpoint[1]] = class_label[0,endpoint[1]] + endpoint[0]
    return class_label

def update_classmap(class_dictionary, hand, compound_motion, classmap=None, time=0, reset=False):
    # classmap: [time (float), hand (right=1, left=0), classes ------>]
    compound_class_label = get_class_label(class_dictionary, compound_motion)
    hand_label = 0 if hand == "L" else 1
    if reset or classmap is None:
        curtime = 0
        last_class = compound_class_label # if you don't have a starting class assume you start in the given gesture
    else:
        curtime = classmap[-1,0] + 1/24
        last_class = np.expand_dims(classmap[-1, 2:],0)
    num_frames = int(time * FPS)
    endtime = curtime + time
    class_labels = np.zeros((num_frames, class_dictionary["ndim"][0]))
    for dim in range(class_dictionary["ndim"][0]):
        class_labels[:,dim] = np.linspace(last_class[0,dim], compound_class_label[0,dim],num_frames)
    time_vec = np.linspace(curtime, endtime -1/FPS, time*FPS)
    classmap_i = np.vstack((time_vec, np.ones_like(time_vec)*hand_label)).T
    classmap_i = np.hstack((classmap_i, class_labels))
    if classmap is not None:
        return np.vstack((classmap, classmap_i))
    else:
        return classmap_i
        
        
    
        
def setup_keyframes(class_progression):
    total_frames = 0
    reset_flag = False
    for progression in class_progression:
        if progression[0] == "RESET":
            total_frames = 0
            continue
        # deal with keyframes
        if total_frames == 0:
            initial_keyframe(progression[0], progression[1], progression[2])
        total_frames = add_keyframe(*progression, total_frames)

def setup_classmatrix(class_progression, class_dictionary):
    class_matrix = None
    reset_flag = False
    for progression in class_progression:
        if progression[0] == "RESET":
            reset_flag = True
            continue
        # deal with class labels
        class_matrix = update_classmap(class_dictionary=class_dictionary,
                                       hand=progression[2], 
                                       compound_motion=[progression[0], progression[1]],
                                       classmap=class_matrix,
                                       time=progression[3],
                                       reset=reset_flag)
        reset_flag = False
    return class_matrix
    

def compile_gif():
    print("rendering GIF")
    curpath = bpy.path.abspath("//")
    dir_path = os.path.abspath(curpath+"tmp_frames")
    image_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".png")]
    image_files.sort()  # Sort the images by filename (frame number)
    with Image.open(image_files[0]) as img:
        width, height = img.size
    images = []
    for file_path in image_files:
            # Add the image to the list
            images.append(imageio.imread(file_path))
    
    gif_path = os.path.join(curpath, "animation.gif")
    print(len(images))
    with imageio.get_writer(gif_path, mode='I', duration=1000/24) as writer:
        for image in images:
            writer.append_data(image)

def main():
    # basic proof of concept -- we'd be able to pass in a list of lists to make this
    # [
    #   [ limb position, hand position, next hand gesture to go to, amount of time to complete this stage], 
    #   [ limb position, hand position, next hand gesture to go to, amount of time to complete this stage],
    #   [ limb position, hand position, next hand gesture to go to, amount of time to complete this stage],
    # ]
    # If we say (very simple ramp up ramp down):
    # [
    #   [ arm_at_side, neutral, no motion, 3s] <- establish position at start and no motion class 
    #   [ arm_at_side, wrist_flexion, no motion, 2s] <- transition to wrist flexion in 2 seconds (RAMP) -> can be tagged for DOF/regression training
    #   [ arm_at_side, wrist_flexion, no motion, 3s] <- we've arrived in wrist flexion before, now hold for 3s  -> can be tagged for classifier or regression training
    #   [ arm_at_side, neutral, no motion, 2s] <- ramp back down to no motion
    #   [ arm_at_side, neutral, no motion, 3s] <- collect the no motion class
    # ]

    class_progression = [
        ["neutral","nomotion","R",3], # ramp up and down flexion, extension, powergrip, and hand open
        ["flexion","nomotion","R",2],
        ["flexion","nomotion","R",3],
        ["neutral","nomotion","R",2],
        ["extension","nomotion","R",2],
        ["extension","nomotion","R",3],
        ["neutral","nomotion","R",2],
        ["neutral","powergrip","R",2],
        ["neutral","powergrip","R",3],
        ["neutral","nomotion","R",2],
        ["neutral","handopen","R",2],
        ["neutral","handopen","R",3],
        ["neutral","nomotion","R",2],
        ["RESET"], # reset running clock, typically used when wanting to animate both right and left simultaneously
        #["neutral","handopen","L",2] # do hand open with the left hand at the start (ramp up 2 seconds then hold it)
    ]
    class_dictionary = {
    "flexion":[-1, 0], # target is -1 of the 0th dimension of the class
    "extension":[1, 0], # target is 1 of the 0th dimension of the class
    "powergrip":[-1, 1], # target is -1 of the 1st dimension of the class
    "handopen":[1, 1], # target is 1 of the 1st dimension of the class,
    "nomotion":[0],
    "neutral":[0],
    "ndim":[2] # number of dimensions of the class space
    }
    clear_frames()
    setup_keyframes(class_progression)
    class_matrix = setup_classmatrix(class_progression, class_dictionary)
    curpath = bpy.path.abspath("//")
    np.savetxt(curpath + "class_file.txt", class_matrix, delimiter=',')
    capture_animation()
    compile_gif()
    
if __name__ == "__main__":
    main()
   