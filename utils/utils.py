import cv2
import numpy as np
from glob import glob
import os
import random
import concurrent.futures
from tqdm import tqdm
from threading import Thread, Lock

mutex = Lock()

# following function code was adopted from 
# https://stackoverflow.com/questions/63001988/how-to-remove-background-of-images-in-python
def remove_background(image):
    img = image
    # convert to graky
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # threshold input image as mask
    mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
    # negate mask
    mask = 255 - mask
    # apply morphology to remove isolated extraneous noise
    # use borderconstant of black since foreground touches the edges
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # anti-alias the mask -- blur then stretch
    # blur alpha channel
    mask = cv2.GaussianBlur(mask, (0,0), sigmaX=2, sigmaY=2, borderType = cv2.BORDER_DEFAULT)
    # linear stretch so that 127.5 goes to 0, but 255 stays 255
    mask = (2*(mask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)
    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask

    return result

def resize_image(image, width, height):
    img = image
    dim = (width, height)
    
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    return resized

def read_image(image_path):
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

def save_image(save_path, image):
    # implementation of singleton pattern
    if not os.path.isdir(os.path.dirname(save_path)):
        mutex.acquire()
        if not os.path.isdir(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        mutex.release()

    cv2.imwrite(save_path, image)

def image_loader(image_paths):
    all_image_paths = []

    for path_dir in image_paths:
        path_dir = path_dir.replace("\\", "")
        for image_path in glob(path_dir):
            all_image_paths.append(image_path)

    return all_image_paths

# following function code was adopted from 
# https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
def overlay_image(background_image, object_image, loc_0, loc_1):
    background_image = background_image.copy()
    alpha_object_image = object_image[:, :, 3] / 255.0
    alpha_background_image = 1.0 - alpha_object_image
    y1, y2 = loc_0, loc_0 + object_image.shape[0]
    x1, x2 = loc_1, loc_1 + object_image.shape[1]

    for c in range(0, 3):
        background_image[y1:y2, x1:x2, c] = (alpha_object_image * object_image[:, :, c] +
                                alpha_background_image * background_image[y1:y2, x1:x2, c])

    return background_image

def get_voc_object(name, xmin, ymin, xmax, ymax):
    string = open(os.path.dirname(os.path.realpath(__file__)) + "/voc_object.xml").read()

    return string.format(
        name=name,
        pose='unspecified',
        truncated=0,
        difficult=0,
        xmin=xmin,
        ymin=ymin,
        xmax=xmax,
        ymax=ymax
    )

def get_voc_xml(folder, filename, width, height, depth, objects):
    string = open(os.path.dirname(os.path.realpath(__file__)) + "/voc.xml").read()

    return string.format(
        folder=folder,
        filename=filename,
        width=width,
        height=height,
        depth=depth,
        objects=objects,
        path=""
    )

def place_objects(image, background, objects_per_image, output, n):
    bg_img_original = read_image(background)
    img = read_image(image)
    bg_shape = bg_img_original.shape
    img_shape = img.shape
 
    dim_0_range = bg_shape[0] - img_shape[0]
    dim_1_range = bg_shape[1] - img_shape[1]

    name = os.path.dirname(image).split("/")[-1]
    folder = "name"
    filename = os.path.basename(os.path.splitext(image)[0])

    for repeat in objects_per_image:
        bg_img = bg_img_original.copy()
        object_vocs = []
        filename_this = f"{filename}-{repeat}-{name}-{n}"

        for itr in range(repeat):
            loc_0 = random.choice(range(0, dim_0_range))
            loc_1 = random.choice(range(0, dim_1_range))
            bg_img = overlay_image(bg_img, img, loc_0, loc_1)
            object_vocs.append(get_voc_object(name, loc_1, loc_0, loc_1+img_shape[1], loc_0+img_shape[0]))

        complete_voc_objects = "".join(object_vocs)
        complete_voc = get_voc_xml(folder, filename_this, bg_shape[1], bg_shape[0], bg_shape[2], complete_voc_objects)

        with open(f"{output}/annotations/{name}/{filename_this}.xml", "w+") as fvoc:
            fvoc.write(complete_voc)
        cv2.imwrite(f"{output}/images/{name}/{filename_this}.jpg", bg_img)

def generate_annotation_fixed_size(images, backgrounds, images_per_object, objects_per_image, random_seed, threads, output):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
    
    if random_seed is not None:
        random.seed(random_seed)    

    exec_args = []

    for n, image in enumerate(images):
        for itr in range(images_per_object):
            # randomly pick a background
            background = random.choice(backgrounds)
            exec_args.append([image, background, objects_per_image, output, n])
            # executor.submit(place_objects, image, background, objects_per_image, output, n)

    for itr in tqdm(executor.map(lambda p: place_objects(*p), exec_args), total=len(exec_args), desc="Generating images."):
        pass
        
    executor.shutdown(wait=True)
