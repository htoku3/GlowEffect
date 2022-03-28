#!/usr/bin/env python3
from os.path import splitext
import argparse
import numpy as np
from PIL import ImageChops, ImageFilter, ImageEnhance
from PIL import Image


def main():
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

    img = Image.open(args.file_name)
    glow = GlowEffect(image=img)
    glow.modify_original(args.orig_gamma, args.orig_brightness, args.orig_color)
    img=glow.apply_glow_effect(args.tone_curve_threshold, args.tone_curve_delta, args.glow_strength,
                               args.glow_bulr_size, args.glow_bulr_angle, args.rgb_delta, args.rgb_angle)
    img=img.convert("RGB")
    img.save((args.suffix).join(splitext(args.file_name)), quality=args.jpeg_quality)


class GlowEffect:
    @staticmethod
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

    @staticmethod
    def gamma_table(gamma):
        return ([int(255*(x/255)**gamma) for x in range(256)] * 3
            + list(range(256)))

    @staticmethod
    def rgb_filter(rgb):
        table = []
        for i in range(3):
            table += list(range(256)) if i == rgb else [0] * 256
        return table + list(range(256))

    @staticmethod
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


    def __init__(self, image: Image.Image):
        self.img = image.convert("RGBA")
        self.base_img = image.convert("RGBA")
        self.light_img = image.convert("RGBA")
        self.w, self.h = image.size

    def modify_original(self, gamma, brightness, color):
        self.base_img = self.img.point(GlowEffect.gamma_table(gamma))
        self.base_img = ImageEnhance.Brightness(self.img).enhance(brightness)
        self.base_img = ImageEnhance.Color(self.img).enhance(color)


    def apply_glow_effect(self, threshold, delta, factor, blur_size, blur_angle, rgb_delta, rgb_angle):
        self.apply_tone_curve(threshold, delta, factor)
        if blur_angle is None:
            self.apply_gaussian_blur(blur_size)
        else:
            self.apply_aniso_blur(blur_size, blur_angle)
        return self.apply_screen(rgb_angle, rgb_delta)


    def apply_tone_curve(self, threshold, delta, factor):
        mono_img = np.array(self.light_img.convert(mode="L")) / 255.0
        np_image = np.array(self.light_img).astype(float)
        if isinstance(factor, float):
            factor = (factor, factor, factor)
        np_image[:,:,0] *= 0.5 * factor[0] * (np.tanh((mono_img - threshold)/delta) + 1.)
        np_image[:,:,1] *= 0.5 * factor[1] * (np.tanh((mono_img - threshold)/delta) + 1.)
        np_image[:,:,2] *= 0.5 * factor[2] * (np.tanh((mono_img - threshold)/delta) + 1.)
        np_image = np.clip(0, 255, np_image).astype(np.dtype('uint8'))
        self.light_img = Image.fromarray(np_image)
        self.light_img = ImageEnhance.Color(self.light_img).enhance(np.clip(1.0 / (1.0 - threshold), 1, 100))
    
    def apply_gaussian_blur(self, size):
        self.light_img = self.light_img.filter(ImageFilter.GaussianBlur(min(self.w, self.h) * size * 1e-2))

    def apply_aniso_blur(self, size, angle):
        for i in range(int(2 * min(self.w, self.h) * size * 1e-2)):
            self.light_img = self.light_img.filter(GlowEffect.make_motion_bulr_filter(theta=angle))

    def apply_screen(self, rgb_angle, rgb_delta):
        trans = np.array([np.cos(np.pi * rgb_angle/180.), -np.sin(np.pi * rgb_angle / 180.)])
        delta = min(self.w, self.h) * rgb_delta * 1e-2
        light_img_bulred_r = self.light_img.rotate(0, translate=tuple(delta*trans)).point(GlowEffect.rgb_filter(0))
        light_img_bulred_g = self.light_img.rotate(0, translate=tuple(trans)).point(GlowEffect.rgb_filter(1))
        light_img_bulred_b = self.light_img.rotate(0, translate=tuple(-delta*trans)).point(GlowEffect.rgb_filter(2))
        self.base_img = ImageChops.screen(self.base_img, light_img_bulred_r)
        self.base_img = ImageChops.screen(self.base_img, light_img_bulred_g)
        self.base_img = ImageChops.screen(self.base_img, light_img_bulred_b)
        return self.base_img

if __name__ == "__main__":
    main()

