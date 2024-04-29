import cv2
import torch
import numpy as np
import albumentations as album
import segmentation_models_pytorch as smp
import os


class_names = ['null', 'accessories', 'bag', 'belt', 'blazer', 'blouse', 'bodysuit', 'boots', 'bra', 'bracelet', 'cape', 'cardigan', 'clogs', 'coat', 'dress', 'earrings', 'flats', 'glasses', 'gloves', 'hair', 'hat', 'heels', 'hoodie', 'intimate', 'jacket', 'jeans', 'jumper', 'leggings', 'loafers', 'necklace', 'panties', 'pants', 'pumps', 'purse', 'ring', 'romper', 'sandals', 'scarf', 'shirt', 'shoes', 'shorts', 'skin', 'skirt', 'sneakers', 'socks', 'stockings', 'suit', 'sunglasses', 'sweater', 'sweatshirt', 'swimwear', 't-shirt', 'tie', 'tights', 'top', 'vest', 'wallet', 'watch', 'wedges']

import math
colors = [
    ("black", (0, 0, 0)),
    ("silver", (192, 192, 192)),
    ("gray", (128, 128, 128)),
    ("white", (255, 255, 255)),
    ("maroon", (128, 0, 0)),
    ("red", (255, 0, 0)),
    ("purple", (128, 0, 128)),
    ("fuchsia", (255, 0, 255)),
    ("green", (0, 128, 0)),
    ("lime", (0, 255, 0)),
    ("olive", (128, 128, 0)),
    ("yellow", (255, 255, 0)),
    ("navy", (0, 0, 128)),
    ("blue", (0, 0, 255)),
    ("teal", (0, 128, 128)),
    ("aqua", (0, 255, 255)),
    ("brown", (150, 75, 0)),
    ("orange", (255, 165, 0)),
]

def distance(a,b):
    dx = a[0]-b[0]
    dy = a[1]-b[1]
    dz = a[2]-b[2]
    return math.sqrt(dx*dx+dy*dy+dz*dz)

def findclosest(pixel):
    mn = 999999
    for name,rgb in colors:
        d = distance(pixel, rgb)
        if d < mn:
            mn = d
            color = name
    return color


def one_hot_encode(label, label_values):
    semantic_map = []
    for colour in label_values:
        equality = np.equal(label, colour)
        class_map = np.all(equality, axis = -1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1)

    return semantic_map

def reverse_one_hot(image):
    x = np.argmax(image, axis = -1)
    return x

def get_rgb(img, mask):
    r = img[:, :, 0][mask].mean()
    g = img[:, :, 1][mask].mean()
    b = img[:, :, 2][mask].mean()
    return r, g, b





remove_items = {
    "male" : [
        'blouse',
        'bra',
        'cape',
        'dress',
        'flats',
        'heels',
        'intimate',
        'leggings',
        'panties',
        'pumps',
        'purse',
        'romper',
        'skirt',
        'tights',
        'top',
        'wedges'
    ],
    "female" : [
        'vest',
        'wallet',
        'watch'
    ]
}


def update_matrix(matrix, scaler):
    updated_matrix = matrix.copy()
    for item, count in scaler.items():
        idx = combos_idx[item]
        updated_matrix[:, idx] = updated_matrix[:, idx] + 1
        updated_matrix[:, idx] = updated_matrix[:, idx] * count
    return updated_matrix

def get_recommendations(query_items, matrix, gender="other", n=10):
    response = np.zeros(len(combos))
    for item in query_items:
        idx = combos_idx[item]
        response = response + matrix[idx]
    for item in query_items:
        idx = combos_idx[item]
        response[idx] = 0
    if gender != "other":
        for item in remove_items[gender]:
            for color in color_labels:
                idx = combos_idx[color+" "+item]
                response[idx] = 0
    
    idx_sort = response.argsort()
    combos_ = np.array(combos)
    response = combos_[idx_sort[::-1]][:n]

    return [color+" "+item for color, item in response]

from itertools import product

dont_include = ("null", "accessories", "hair", "skin")
dont_include_idx = (0, 1, 19, 41)
items = {tag: i for i, tag in enumerate(class_names) if tag not in dont_include}
color_labels = [color for color, _ in colors]
item_labels = [item for item, _ in items.items()]

combos = list(product(color_labels, item_labels))
combos_idx = {
    color+" "+item: i for i, (color, item) in enumerate(combos)
}

matrix = np.fromfile('matrix.dat', dtype=int).reshape(
    len(combos), len(combos)
)


def get_custom_recommendations(query_items, context_items, gender="other", n=10):
    updated_matrix = update_matrix(
        matrix, context_items
    )
    response = get_recommendations(query_items, updated_matrix, gender=gender, n=n)
    return response





ENCODER = 'resnet50'
ENCODER_WEIGHTS = 'imagenet'
DEVICE = torch.device("cpu")
best_model = torch.load('best_model_01.pth', map_location=DEVICE)

def to_tensor(x, **kwargs):
    return x.transpose(2, 0, 1).astype('float32')
def crop_image(image, true_dimensions):
    return album.CenterCrop(p=1, height=true_dimensions[0], width=true_dimensions[1])(image=image)

preprocessing_fn = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)
preprocessing = album.Compose([
    album.Lambda(image=preprocessing_fn),
    album.Lambda(image=to_tensor, mask=to_tensor)
])
def compute_padding(n, m=16):
        return n + (m - n%m)
def segment(image_file):
    image = cv2.imread(image_file)[:,:,::-1]
    true_dimensions = image.shape
    augmentation = album.Compose([
        album.PadIfNeeded(min_height=compute_padding(true_dimensions[0]),
                        min_width=compute_padding(true_dimensions[1]),
                        always_apply=True, border_mode=0),
    ])
    transformed_image = augmentation(image=image.copy())["image"]
    transformed_image = preprocessing(image=transformed_image)["image"]
    x_tensor = torch.from_numpy(transformed_image).to(DEVICE).unsqueeze(0)
    # Predict test image
    pred_mask = best_model(x_tensor)
    pred_mask = pred_mask.detach().squeeze().cpu().numpy()
    # Convert pred_mask from `CHW` format to `HWC` format
    pred_mask = np.transpose(pred_mask,(1,2,0))
    pred_mask = crop_image(reverse_one_hot(pred_mask), true_dimensions)['image']
    return image, pred_mask

def get_items_from_segmentation(image, mask):
    img_items = np.unique(mask).astype(int)
    img_items = [x for x in img_items if x not in (0, 1, 19, 41)]
    
    img_color_items = []
    for n in img_items:
        item = class_names[n]
        r, g, b = get_rgb(image, mask==n)
        color = findclosest([r, g, b])
        img_color_items += [color+" "+item]
    return img_color_items


def get_items_from_segmentation(image, mask):
    img_items = np.unique(mask).astype(int)
    img_items = [x for x in img_items if x not in (0, 1, 19, 41)]
    
    img_color_items = []
    for n in img_items:
        item = class_names[n]
        r, g, b = get_rgb(image, mask==n)
        color = findclosest([r, g, b])
        img_color_items += [color+" "+item]
    return img_color_items

def build_context(items):
    context = {}
    for item in items:
        if item not in context:
            context[item] =  1
        else:
            context[item] += 1
    return context