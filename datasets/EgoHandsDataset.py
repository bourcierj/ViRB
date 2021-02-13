import torch
import tqdm
import pickle
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms as transforms
import glob
from PIL import Image, ImageOps, ImageDraw
import json
from pycocotools.coco import COCO
import os
import contextlib
import random
from scipy.io import loadmat
import numpy as np


class EgoHandsDataset:
    """COCO detection dataset class"""

    def __init__(self, train=True):
        super().__init__()
        self.train = train
        self.imgs = glob.glob('data/egohands/images/*/*.jpg')
        self.imgs.sort()
        self.labels = glob.glob('data/egohands/labels/*/*.jpg')
        self.labels.sort()


        if self.train:
            self.imgs = self.imgs[:int(0.9*len(self.imgs))]
            self.labels = self.labels[:int(0.9 * len(self.imgs))]
        else:
            self.imgs = self.imgs[int(0.9 * len(self.imgs)):]
            self.labels = self.labels[int(0.9 * len(self.imgs)):]

        self.img_preprocessor = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.label_preprocessor = transforms.Compose([
            transforms.ToTensor()
        ])
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        if self.train:
            img = Image.open(self.imgs[idx]).convert('RGB')
            label = Image.open(self.labels[idx]).convert('I')
            ogw, ogh = img.size

            # # Scale the image
            # scale = random.uniform(0.5, 2.0)
            # img = img.resize((int(ogw * scale), int(ogh * scale)))
            # label = label.resize((int(ogw * scale), int(ogh * scale)), resample=Image.NEAREST)
            #
            # # Mirror the image half of the time
            # if random.uniform(0, 1) > 0.5:
            #     img = ImageOps.mirror(img)
            #     label = ImageOps.mirror(label)

            # Add random crop to image
            while True:
                cw = 450
                ch = 450
                x = random.randint(0, ogw - cw)
                y = random.randint(0, ogh - ch)
                img = img.crop((x, y, x+cw, y+ch))
                label = label.crop((x, y, x+cw, y+ch))

                img = self.img_preprocessor(img)
                label = self.label_preprocessor(label).long().squeeze()

                if torch.unique(label).shape > 1:
                    break

        else:
            img = self.img_preprocessor(Image.open(self.imgs[idx]).convert('RGB'))
            label = self.label_preprocessor(Image.open(self.labels[idx]).convert('I')).long().squeeze()
        return img, label

    def __len__(self):
        return len(self.imgs)

    def class_names(self):
        return [l[0] for l in cslabels]

    def num_classes(self):
        return 20