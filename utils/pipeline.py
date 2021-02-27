from utils import utils
import os
import sys
import concurrent.futures
from tqdm import tqdm

def run_maker(
        *,
        images=None,
        backgrounds=None,
        should_remove_backgrounds=None,
        should_crop_whites=None,
        resize_images=None,
        resize_backgrounds=None,
        resize_ratio=None,
        target_size=None,
        n_images=None,
        n_objects=None,
        seed=None,
        output=None,
        threads=8
    ):
    input_images = utils.image_loader(images)
    input_backgrounds = utils.image_loader(backgrounds)
    object_cache = {}

    # allow users to specify a single repeat value
    # or a range repeat values
    if "," in n_objects:
        n_objects = list(range(*list(map(int, n_objects.strip().split(",")))))
    else:
        n_objects = [int(n_objects)]
    # python ranged discard last value, so add one
    n_objects += [n_objects[-1]+1]

    if not os.path.isdir(output):
        os.mkdir(output)
        os.mkdir(output +  "/tmp")
        os.mkdir(output +  "/images")
        os.mkdir(output +  "/annotations")
        all_objects = set([os.path.dirname(i).split("/")[-1].lower() for i in input_images])
        for obj in all_objects:
            os.mkdir(output +  f"/images/{obj}")
            os.mkdir(output +  f"/annotations/{obj}")

    if resize_ratio:
        print("Feature not implemented yet!!!")
        sys.exit(1)


        if "-" in resize_ratio:
            ratio_range = list(map(lambda x: int(float(x)*10), resize_ratio.strip().split("-")))
            ratios = [x/10 for x in range(*ratio_range)]

        else:
            ratios = [float(resize_ratio.strip())]


    else:
        if resize_images or should_remove_backgrounds:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
            
            def thread_function(input_image, width, height, out_path):
                image = utils.read_image(input_image)
                
                if resize_images is not None:
                    image = utils.resize_image(image, width, height)

                # remove all backgrounds
                if should_remove_backgrounds:
                    image = utils.remove_background(image)

                utils.save_image(out_path, image)
            
            # resize all images
            exec_args = []
            if resize_images is not None:
                height, width = list(map(int, resize_images.strip().split(",")))
            else:
                height, width = None, None

            for n in range(len(input_images)):
                object_name = os.path.dirname(input_images[n]).split("/")[-1].lower()
                out_path = f"{output}/tmp/obj/{object_name}/img_{n}.png"
                exec_args.append((str(input_images[n]), width, height, out_path))
                input_images[n] = out_path
            
            for itr in tqdm(executor.map(lambda p: thread_function(*p), exec_args), total=len(input_images), desc="Processing images."):
                pass

        if resize_backgrounds:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)

            def thread_function(input_image, width, height, out_path):
                image = utils.read_image(input_image)
                image = utils.resize_image(image, width, height)

                utils.save_image(out_path, image)

            # resize all backgrounds
            exec_args = []
            height, width = list(map(int, resize_backgrounds.strip().split(",")))
            
            for n in range(len(input_backgrounds)):
                out_path = f"{output}/tmp/bg/img_{n}.png"
                exec_args.append((str(input_backgrounds[n]), width, height, out_path))
                input_backgrounds[n] = out_path

            for itr in tqdm(executor.map(lambda p: thread_function(*p), exec_args), total=len(input_backgrounds), desc="Resizing backgrounds."):
                pass
            
            executor.shutdown(wait=True)
        
        utils.generate_annotation_fixed_size(input_images, input_backgrounds, n_images, n_objects, seed, threads, output)
