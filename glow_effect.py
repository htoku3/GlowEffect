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
parser.add_argument("--tone_curve_delta", default=0.04, type=float)
parser.add_argument("--glow_bulr_size", default=0.4, type=float)
parser.add_argument("--glow_bulr_angle", default=None, type=float)
parser.add_argument("--glow_strength", default="0.8", type=str)
parser.add_argument("--orig_gamma", default=1.0, type=float)
parser.add_argument("--orig_brightness", default=1.0, type=float)
parser.add_argument("--orig_color", default=1.0, type=float)
parser.add_argument("--rgb_delta", default=0.0, type=float)
parser.add_argument("--rgb_angle", default=-45, type=float)
parser.add_argument("--jpeg_quality", default=85, type=int)

args = parser.parse_args()
args.glow_strength = [float(var.strip()) for var in args.glow_strength.split()]
if len(args.glow_strength) == 1:
    args.glow_strength = args.glow_strength[0]
elif len(args.glow_strength) == 3:
    pass
else:
    print("glow_strength must be float or 3d float vector.")
    print("ex. --glow_strength=0.8, --glow_strength=\"0.5 0.5 1.0\"")
    exit(1)


def main():
    img = Image.open(args.file_name)
    w, h = img.size
    img=img.convert("RGBA")
    light_img = img.copy()
    light_img = apply_tone_curve(light_img, args.tone_curve_threshold, args.tone_curve_delta, args.glow_strength)
    light_img = ImageEnhance.Color(light_img).enhance(np.clip(1.0 / (1.0 - args.tone_curve_threshold), 1, 100))
    if args.glow_bulr_angle is None:
        light_img_bulred = light_img.filter(ImageFilter.GaussianBlur(min(w, h) * args.glow_bulr_size * 1e-2))
    else:
        light_img_bulred = light_img.copy()
        for i in range(int(2 * min(w, h) * args.glow_bulr_size * 1e-2)):
            light_img_bulred = light_img_bulred.filter(make_motion_bulr_filter(theta=args.glow_bulr_angle))
    
    trans = np.array([np.cos(np.pi * args.rgb_angle/180.), -np.sin(np.pi * args.rgb_angle / 180.)])
    delta = min(w, h) * args.rgb_delta * 1e-2
    light_img_bulred_r = light_img_bulred.rotate(0, translate=tuple(delta*trans)).point(rgb_filter(0))
    light_img_bulred_g = light_img_bulred.rotate(0, translate=tuple(trans)).point(rgb_filter(1))
    light_img_bulred_b = light_img_bulred.rotate(0, translate=tuple(-delta*trans)).point(rgb_filter(2))
    img = img.point(gamma_table(args.orig_gamma))
    img = ImageEnhance.Brightness(img).enhance(args.orig_brightness)
    img = ImageEnhance.Color(img).enhance(args.orig_color)
    img = ImageChops.screen(img, light_img_bulred_r)
    img = ImageChops.screen(img, light_img_bulred_g)
    img = ImageChops.screen(img, light_img_bulred_b)
    img=img.convert("RGB")
    img.save((args.suffix).join(splitext(args.file_name)), quality=args.jpeg_quality)


def apply_tone_curve(img: Image, threshold, delta, factor):
    mono_img = np.array(img.convert(mode="L")) / 255.0
    np_image = np.array(img).astype(float)
    if isinstance(factor, float):
        factor = (factor, factor, factor)
    np_image[:,:,0] *= 0.5 * factor[0] * (np.tanh((mono_img - threshold)/delta) + 1.)
    np_image[:,:,1] *= 0.5 * factor[1] * (np.tanh((mono_img - threshold)/delta) + 1.)
    np_image[:,:,2] *= 0.5 * factor[2] * (np.tanh((mono_img - threshold)/delta) + 1.)
    np_image = np.clip(0, 255, np_image).astype(np.dtype('uint8'))
    return Image.fromarray(np_image)

def gamma_table(gamma):
    return ([int(255*(x/255)**gamma) for x in range(256)] * 3
        + list(range(256)))

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

