from PIL import Image
import numpy as np
import cv2

path = r'C:/Users/Mayur/.gemini/antigravity/brain/e160f8a8-1edc-4f0d-b3c1-f510bdfd5837/.user_uploaded/media_1792938723069_a04a0a10.png'
im = Image.open(path).convert('L')
arr = np.array(im, dtype=np.float32)

# Background is 255 (white). Ink is 0 (black).
# Alpha: when pixel is 255 -> alpha is 0. When pixel is < 20 -> alpha is 255.
# Use smooth linear interpolation from 245 down to 10
alpha = np.clip((245.0 - arr) / (245.0 - 40.0) * 255.0, 0, 255).astype(np.uint8)

# Dark mode: pure white (#f0f6fc) with alpha
h, w = arr.shape
dark_img = np.zeros((h, w, 4), dtype=np.uint8)
dark_img[:, :, 0] = 240 # R
dark_img[:, :, 1] = 246 # G
dark_img[:, :, 2] = 252 # B
dark_img[:, :, 3] = alpha

im_dark = Image.fromarray(dark_img, mode='RGBA')
im_dark.save('assets/thank-you-dark.png')

# Light mode: charcoal (#1f2328) with alpha
light_img = np.zeros((h, w, 4), dtype=np.uint8)
light_img[:, :, 0] = 31 # R
light_img[:, :, 1] = 35 # G
light_img[:, :, 2] = 40 # B
light_img[:, :, 3] = alpha

im_light = Image.fromarray(light_img, mode='RGBA')
im_light.save('assets/thank-you-light.png')

print('Saved assets/thank-you-dark.png and light.png')
