import os, cv2
import numpy as np
import pandas as pd


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


def get_rgb_prod(img, mask):
    r = img[0, :, :][mask].mean()
    g = img[1, :, :][mask].mean()
    b = img[2, :, :][mask].mean()
    return r, g, b


def collect_new_data():
    return


def build_features():
    return


select_classes = ['null', 'accessories', 'bag', 'belt', 'blazer', 'blouse', 'bodysuit',
                  'boots', 'bra', 'bracelet', 'cape', 'cardigan', 'clogs', 'coat', 'dress',
                  'earrings', 'flats', 'glasses', 'gloves', 'hair', 'hat', 'heels', 'hoodie',
                  'intimate', 'jacket', 'jeans', 'jumper', 'leggings', 'loafers', 'necklace',
                  'panties', 'pants', 'pumps', 'purse', 'ring', 'romper', 'sandals', 'scarf',
                  'shirt', 'shoes', 'shorts', 'skin', 'skirt', 'sneakers', 'socks', 'stockings',
                  'suit', 'sunglasses', 'sweater', 'sweatshirt', 'swimwear', 't-shirt', 'tie',
                  'tights', 'top', 'vest', 'wallet', 'watch', 'wedges']


import math
from PIL import Image


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


from itertools import product


dont_include = ("null", "accessories", "hair", "skin")
dont_include_idx = (0, 1, 19, 41)
items = {tag: i for i, tag in enumerate(select_classes) if tag not in dont_include}
color_labels = [color for color, _ in colors]
item_labels = [item for item, _ in items.items()]


combos = list(product(color_labels, item_labels))
combos_idx = {
    color+" "+item: i for i, (color, item) in enumerate(combos)
}


matrix_idx = {
    color: {
        item: i
    } for i, (color, item) in enumerate(combos)
}


matrix = np.zeros((len(combos), len(combos)))


class_dict = pd.read_csv(os.path.join('/usr/local/airflow/dags/data', 'class_dict.csv'))
# Get class RGB values
class_rgb_values = class_dict[['r','g','b']].values.tolist()



DATA_DIR = "/data"
files = os.listdir(f"{DATA_DIR}/labels/pixel_level_labels_colored")
for fnum, file_name in enumerate(files):
    segmentations = cv2.imread(f"{DATA_DIR}/labels/pixel_level_labels_colored/{file_name}")[:,:,::-1]
    img = cv2.imread(f"{DATA_DIR}/images/{file_name[:-4]}.jpg")

    mask = reverse_one_hot(one_hot_encode(segmentations, class_rgb_values).astype('float'))

    img_items = np.unique(mask)
    img_items = [x for x in img_items if x not in (0, 1, 19, 41)]

    img_color_items = []
    for n in img_items:
        item = select_classes[n]
        r, g, b = get_rgb(img, mask==n)
        color = findclosest([r, g, b])
        img_color_items += [color+" "+item]

    for item1 in img_color_items:
        for item2 in img_color_items:
            idx1 = combos_idx[item1]
            idx2 = combos_idx[item2]
            matrix[idx1, idx2] += 1
    if fnum%10:
        print(f"{fnum} of {len(files)} done.")
matrix.astype(int).tofile(f'{DATA_DIR}/output/matrix.dat')