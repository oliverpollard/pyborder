from PIL import Image, ExifTags, ImageCms
from argparse import ArgumentParser
from pathlib import Path
import io


def file_exists(parser, arg):
    if not Path(arg).exists:
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def calc_new_size(x_size, y_size, ratio):
    if x_size > y_size:
        new_size = int(ratio * x_size)
    elif x_size < y_size:
        new_size = int(ratio * y_size)
    else:
        new_size = int(ratio * x_size)

    if (new_size % 2) != 0:
        new_size = new_size + 1

    return new_size


def image_border(input_file, ratio, output_file=None):
    if output_file is None:
        output_file = input_file.with_stem(input_file.stem + "_pyborder")

    image = Image.open(input_file)
    x_size, y_size = image.size
    iccProfile = image.info.get("icc_profile")
    iccBytes = io.BytesIO(iccProfile)
    originalColorProfile = ImageCms.ImageCmsProfile(iccBytes)

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == "Orientation":
            break
    # exif = dict(image._getexif().items())

    new_size = calc_new_size(x_size, y_size, ratio)
    new_im = Image.new("RGB", (new_size, new_size), color=(255, 255, 255))
    new_im.paste(image, (int((new_size - x_size) / 2), int((new_size - y_size) / 2)))

    new_im.save(output_file, icc_profile=originalColorProfile.tobytes())


def main():
    parser = ArgumentParser(description="produces square images with white borders")
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        required=True,
        help="input image",
        metavar="FILE",
        type=lambda x: file_exists(parser, x),
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="output image",
        metavar="FILE",
    )
    parser.add_argument(
        "-r", "--ratio", dest="ratio", required=False, help="output ratio"
    )

    args = parser.parse_args()
    if args.ratio is None:
        ratio = 1.05
    else:
        ratio = float(args.ratio)

    input_file = Path(args.input)
    if input_file.is_dir():
        for image_file in input_file.iterdir():
            if (image_file.suffix.lower() in [".png", ".jpeg", ".jpg"]) and (
                not image_file.stem.endswith("_pyborder")
            ):
                print(image_file)
                image_border(image_file, ratio)

    else:
        image_border(input_file=input_file, ratio=ratio, output_file=args.output)


if __name__ == "__main__":
    main()
