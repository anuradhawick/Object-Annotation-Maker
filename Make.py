import argparse
from utils import pipeline


def main():
    parser = argparse.ArgumentParser(description="""Object Annotation Maker.\n\nThis programs enables the creation of bounding boxes with backgrounds for object images.\nThe project was initiated intending to help computer vision researchers and enthusiasts to perform easy data generation.\nCreated by Anuradha Wickramarachchi (anuradhawick@gmail.com).""", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--images', '-i',
                        help="""Images path, can provide wild card. \neg: "/path/img-cars-*.jpg"\n(Quotation marks are essential)""",
                        type=str,
                        required=True,
                        nargs='+')

    parser.add_argument('--backgrounds', '-b',
                        help="""Background images path, can provide wild card. \neg: "/path/img-backgrounds-*.jpg"\n(Quotation marks are essential)""",
                        type=str,
                        required=True,
                        nargs='+')

    parser.add_argument('--remove-backgrounds', "-r",
                        action='store_true',
                        help="""Whether to remove white backgrounds or not. \nNot required if you have PNG images without backgrounds.""",
                        default=False)

    parser.add_argument('--crop-whites', "-c",
                        action='store_true',
                        help="""Whether to crop out the white margins from images. \nNot required if you have PNG images without backgrounds.""",
                        default=False)

    parser.add_argument('--resize-images', "-ri",
                        type=str,
                        required=False,
                        help="""Convert input images to size before proceeding. Format H,W in pixels without spaces. Or specify only height for scaled resize.""",
                        metavar="H,W or H",
                        default=None
                        )

    parser.add_argument('--resize-backgrounds', "-rb",
                        type=str,
                        required=False,
                        help="""Convert background images to size before proceeding. Format H,W in pixels without spaces. Or specify only height for scaled resize.""",
                        metavar="H,W or H",
                        default=None)

    parser.add_argument('--resize-ratio', "-rr",
                        type=str,
                        required=False,
                        choices=[str(x/10) for x in range(1, 10)] + [f"{x/10}-{y/10}" for x in range(1, 10) for y in range(1, 10) if x<y],
                        metavar="0.5 or 0.2-0.6",
                        help="""Ratio of object to background. \nUse a range or a single value. Overrides resize-image and resize-backgroud options.\nUse - to separate range values.""",
                        default=None)

    parser.add_argument('--target-size', "-ts",
                        type=str,
                        required=False,
                        help="""Find image size. Format H,W in pixels without spaces.""",
                        default=None
                        )
                    
    parser.add_argument('--n-images', "-ni",
                        type=int,
                        required=False,
                        default=1,
                        choices=range(0,101),
                        metavar="[0-100]",
                        help="""Number of images to generate per object. Between 1 and 100."""
                        )

    parser.add_argument('--n-objects', "-no",
                        type=str,
                        required=False,
                        default=1,
                        metavar="1,100",
                        help="""Number of objects per image. Range or single value."""
                        )

    parser.add_argument('--seed', "-s",
                        type=int,
                        required=False,
                        help="""Random seed for reproducibility.""",
                        default=None)

    parser.add_argument('--threads', "-t",
                        type=int,
                        required=False,
                        help="""Number of threads for processing.""",
                        default=8)                        

    parser.add_argument('--output', "-o",
                        type=str,
                        required=True,
                        help="""Output directory."""
                        )

    args = parser.parse_args()

    images = args.images
    backgrounds = args.backgrounds
    should_remove_backgrounds = args.remove_backgrounds
    should_crop_whites = args.crop_whites
    resize_images = args.resize_images
    resize_backgrounds = args.resize_backgrounds
    resize_ratio = args.resize_ratio
    target_size = args.target_size
    n_images = args.n_images
    n_objects = args.n_objects
    seed = args.seed
    output = args.output

    pipeline.run_maker(
        images=images,
        backgrounds=backgrounds,
        should_remove_backgrounds=should_remove_backgrounds,
        should_crop_whites=should_crop_whites,
        resize_images=resize_images,
        resize_backgrounds=resize_backgrounds,
        resize_ratio=resize_ratio,
        target_size=target_size,
        n_images=n_images,
        n_objects=n_objects,
        seed=seed,
        output=output,
    )


if __name__ == "__main__":
    main()


# python Make.py -i '/Volumes/T7 Touch/Anu/FRUIT360/fruit360/fruits-360/Training/Watermelon/*.jpg' -b '/Volumes/T7 Touch/Anu/FRUIT360/fruit360/fruits-360/bg/*.jpg'