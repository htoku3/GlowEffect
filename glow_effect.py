#!/usr/bin/env python3
from os.path import splitext
import argparse
import numpy as np
from PIL import ImageChops, ImageFilter, ImageEnhance
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("file_name")
parser.add_argument("--suffix", default="_out")
parser.add_argument("--quality", default="_out")
parser.add_argument("--tone_curve_threshold", default=0.9, type=float)
parser.add_argument("--tone_curve_delta", default=0.05, type=float)
parser.add_argument("--glow_bulr_size", default=0.005, type=float)
parser.add_argument("--glow_bulr_angle", default=None, type=float)
parser.add_argument("--glow_strength", default=0.8, type=float)
parser.add_argument("--orig_image_brightness", default=1.0, type=float)
parser.add_argument("--orig_image_color", default=1.0, type=float)
parser.add_argument("--rgb_delta", default=0.005, type=float)
parser.add_argument("--rgb_angle", default=-45, type=float)

args = parser.parse_args()

def main():
    img = Image.open(args.file_name)
    w, h = img.size

    img=img.convert("RGBA")
    light_img = ImageChops.multiply(img, 
                    ImageEnhance.Color(img).enhance(0.5).point(
                        tone_curve_table(args.tone_curve_threshold, args.tone_curve_delta, args.glow_strength)))
    if args.glow_bulr_angle is None:
        light_img_bulred = light_img.filter(ImageFilter.GaussianBlur(min(w, h) * args.glow_bulr_size))
    else:
        light_img_bulred = light_img.copy()
        for i in range(int(2 * min(w, h) * args.glow_bulr_size)):
            light_img_bulred = light_img_bulred.filter(make_motion_bulr_filter(theta=args.glow_bulr_angle))
    
    trans = np.array([np.cos(np.pi * args.rgb_angle/180.), -np.sin(np.pi * args.rgb_angle / 180.)])
    delta = min(w, h) * args.rgb_delta
    light_img_bulred_r = light_img_bulred.rotate(0, translate=tuple(delta*trans)).point(rgb_filter(0))
    light_img_bulred_g = light_img_bulred.rotate(0, translate=tuple(trans)).point(rgb_filter(1))
    light_img_bulred_b = light_img_bulred.rotate(0, translate=tuple(-delta*trans)).point(rgb_filter(2))
    img = ImageEnhance.Brightness(img).enhance(args.orig_image_brightness)
    img = ImageEnhance.Color(img).enhance(args.orig_image_color)
    img = ImageChops.screen(img, light_img_bulred_r)
    img = ImageChops.screen(img, light_img_bulred_g)
    img = ImageChops.screen(img, light_img_bulred_b)
    img=img.convert("RGB")
    img.save((args.suffix).join(splitext(args.file_name)), quality=100)


def tone_curve_table(threshold, delta, factor):
    threshold *= 255
    delta *= 255
    return [int(128 * max(0, factor + np.tanh((x - threshold)/delta))) for x in range(256)] * 3 + list(range(256))

def rgb_filter(rgb):
    table = []
    for i in range(3):
        table += list(range(256)) if i == rgb else [0] * 256
    return table + list(range(256))

def make_motion_bulr_filter(theta=45):
    c = np.cos(np.pi*theta/180.0)
    s = np.sin(np.pi*theta/180.0)
    flist = np.zeros((5, 5))
    for shift in np.arange(-2, 2 + 1):
        flist += np.array([[np.exp(-(c*i+s*j)**2 / 4.0
                                   -(-s*i+c*j)**2 / 0.25)
                        for i in np.arange(-2, 3)] for j in np.arange(-2, 3)])
    flist = np.reshape(flist, 5 * 5)
    flist *= 1.0/np.sum(flist)
    return ImageFilter.Kernel((5, 5), flist, scale=1.0)

if __name__ == "__main__":
    main()

