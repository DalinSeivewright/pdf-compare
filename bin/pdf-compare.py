#!/usr/bin/python3

from PIL import Image, ImageDraw
from pdf2image import convert_from_bytes
from argparse import ArgumentParser
from os import path
from random import choice
from string import ascii_letters


INPUT_SETTING = 'inputs'
OUTPUT_DIR_SETTING = 'output-dir'
EXCLUDE_MATCHING_SETTING = 'exclude-matching'
QUIET_MODE_SETTING = 'quiet'
VERBOSE_SETTING = 'verbose'
PREFIX_SIZE = 6
VERBOSE_VALUE = 0
QUIET_MODE = False


def main():
    settings = get_parameters()
    validate_settings(settings)
    debug(settings)
# TODO Enhance this to support N Pdf comparing although I am not sure how useful that would be
    extra_info("Loading Inputs...")
    source_pdf_a = convert_from_bytes(open(settings[INPUT_SETTING][0], 'rb').read())
    source_pdf_b = convert_from_bytes(open(settings[INPUT_SETTING][1], 'rb').read())
    debug_print_pdf_info([source_pdf_a, source_pdf_b])

    extra_info("Determining minimum size needed for diff images...")
    diff_size = get_diff_size(source_pdf_a, source_pdf_b)
    diff_page_count = max(len(source_pdf_a), len(source_pdf_b))
    diff_file_prefix = generate_filename_prefix()
    info('Using ' + diff_file_prefix + ' as delta file prefix.')
    extra_info("Starting difference generation process...")
    differences = generate_pdf_diff(diff_file_prefix,
                                    diff_page_count,
                                    diff_size,
                                    source_pdf_a,
                                    source_pdf_b,
                                    settings[OUTPUT_DIR_SETTING],
                                    settings[EXCLUDE_MATCHING_SETTING])
    info('Compare Completed.  Prefix:  ' + diff_file_prefix + ".  " + str(differences) + ' page difference(s) detected.')


def get_parameters():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-i', '--input', action='append', dest=INPUT_SETTING)
    arg_parser.add_argument('-o', '--output-dir', action='store', dest=OUTPUT_DIR_SETTING)
    arg_parser.add_argument('-e', '--exclude-matching', action='store_true', dest=EXCLUDE_MATCHING_SETTING)
    arg_parser.add_argument('-q', '--quiet', action='store_true', dest=QUIET_MODE_SETTING)
    arg_parser.add_argument('-v', '--verbose', action='count', default=0, dest=VERBOSE_SETTING)
    return vars(arg_parser.parse_args())


def validate_settings(settings):
    if settings[INPUT_SETTING] is None:
        exit('Input PDFs not specified.')
    if len(settings[INPUT_SETTING]) != 2:
        exit('You must specify exactly 2 inputs.')
    if settings[OUTPUT_DIR_SETTING] is None:
        exit('Output Directory must be specified')

    global VERBOSE_VALUE
    VERBOSE_VALUE = settings[VERBOSE_SETTING]
    global QUIET_MODE
    QUIET_MODE = settings[QUIET_MODE_SETTING]


def debug_print_pdf_info(sources):
    if not is_debug_mode(VERBOSE_VALUE):
        return
    # I know.
    pdf_index = 1
    for pdf in sources:
        debug("Source " + str(pdf_index))
        debug("--------")
        page_index = 1
        for page in pdf:
            debug("Page " + str(page_index), page.format, page.size, page.mode)
            page_index = page_index + 1
        print("")
        pdf_index = pdf_index + 1


def get_diff_size(images_a, images_b):
    if len(images_a) == 0 and len(images_b) > 0:
        return images_b[0].size

    if len(images_b) == 0 and len(images_a) > 0:
        return images_a[0].size

    if len(images_b) == 0 and len(images_a) > 0:
        return 0, 0
    size_a = images_a[0].size
    size_b = images_b[0].size
    return max(size_a[0], size_b[0]), max(size_a[1], size_b[1])


def generate_filename_prefix():
    prefix = ''
    for i in range(PREFIX_SIZE):
        prefix = prefix + choice(ascii_letters)
    return prefix


def generate_pdf_diff(prefix, pages, page_size, source_pdf_a, source_pdf_b, output_dir, exclude_matching):
    differences = 0
    for page in range(0, pages):
        extra_info("Processing Page " + str(page) + "...")
        delta_image = Image.new(source_pdf_b[0].mode, page_size)
        page_a = get_source(source_pdf_a, page)
        page_b = get_source(source_pdf_b, page)
        differences_detected = generate_page_diff(delta_image, page_a, page_b)
        if not differences_detected and exclude_matching:
            extra_info('Skipping save of page ' + str(page + 1) + ' because sources match.')
            continue
        image_path = path.join(output_dir, prefix + '_page' + str(page + 1) + '.png')
        delta_image.save(image_path)
        extra_info('Saved page ' + str(page + 1) + ' delta to ' + image_path)
        if differences_detected:
            differences = differences + 1
    return differences


def get_source(source_list, index):
    if index >= len(source_list):
        return None
    return source_list[index]


def generate_page_diff(diff, source_a, source_b):
    if (source_a is None and source_b is not None) or (source_b is None and source_a is not None):
        image_draw = ImageDraw.Draw(diff)
        image_draw.rectangle([(0, 0), diff.size], fill=(255, 0, 0))
        return True

    differences_detected = False
    for pixel_x in range(0, diff.size[0]):
        for pixel_y in range(0, diff.size[1]):
            pixel_a = get_pixel(source_a, pixel_x, pixel_y)
            pixel_b = get_pixel(source_b, pixel_x, pixel_y)
            if pixel_a is None or pixel_b is None or is_pixel_different(pixel_a, pixel_b):
                differences_detected = True
                diff.putpixel((pixel_x, pixel_y), (255, 0, 0))
    return differences_detected


def get_pixel(source, x, y):
    if source is None:
        return None
    size = source.size
    if x >= size[0]:
        return None
    if y >= size[1]:
        return None
    return source.getpixel((x, y))


def is_pixel_different(pixel_a, pixel_b):
    return pixel_a[0] != pixel_b[0] or pixel_a[1] != pixel_b[1] or pixel_a[2] != pixel_b[2]


def log(level, *output):
    if QUIET_MODE:
        return

    if level == 0 and is_info_mode(VERBOSE_VALUE):
        print(*output)
        return

    if level == 1 and is_extra_info_mode(VERBOSE_VALUE):
        print(*output)
        return
    if level == 2 and is_debug_mode(VERBOSE_VALUE):
        print("DEBUG:", *output)


def info(*output):
    log(0, *output)


def extra_info(*output):
    log(1, *output)


def debug(*output):
    log(2, *output)


def is_info_mode(verbose):
    return verbose >= 0


def is_extra_info_mode(verbose):
    return verbose >= 1


def is_debug_mode(verbose):
    return verbose >= 2


if __name__ == '__main__':
    main()
