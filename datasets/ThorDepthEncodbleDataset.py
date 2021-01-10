import torch
import tqdm
import pickle
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms as transforms
import glob
from PIL import Image
import random


from datasets.EncodableDataset import EncodableDataset


class ThorDepthEncodableDataset(EncodableDataset):
    """Pets encodable dataset class"""

    def __init__(self, train=True):
        super().__init__()
        data_path = 'data/thor_depth_prediction/train/*/*rgb.jpg'\
            if train else 'data/thor_depth_prediction/test/*/*rgb.jpg'
        self.data = list(glob.glob(data_path))
        self.data.sort()
        label_path = 'data/thor_depth_prediction/train/*/*depth.jpg'\
            if train else 'data/thor_depth_prediction/test/*/*depth.jpg'
        self.labels = list(glob.glob(label_path))
        self.labels.sort()
        if train:
            self.img_preprocessor = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ColorJitter(.4, .4, .4, .2),
                transforms.RandomGrayscale(p=0.2),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            self.img_preprocessor = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        self.label_preprocessor = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=0.5, std=0.25)
        ])
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        img_path = self.data[idx]
        label_path = self.labels[idx]

        img = self.img_preprocessor(Image.open(img_path).convert('RGB'))
        mask = self.label_preprocessor(Image.open(label_path).convert('L'))

        # i = img.detach().numpy().transpose(1, 2, 0)
        # plt.figure(0)
        # plt.imshow(i)
        # m = mask.detach()
        # plt.figure(1)
        # plt.imshow(m[0])
        # plt.show()
        # exit()

        return img, mask

    def __len__(self):
        return len(self.data)

    def encode(self, model):
        model.to(self.device)
        model.eval()
        batch = []
        for img in tqdm.tqdm(self.data):
            if len(batch) == 500:
                batch = torch.stack(batch, dim=0).to(self.device)
                with torch.no_grad():
                    out = model(batch).detach()
                self.encoded_data.append(out)
                batch = []
            x = Image.open(img).convert('RGB')
            x = self.preprocessor(x)
            batch.append(x)
        batch = torch.stack(batch, dim=0).to(self.device)
        with torch.no_grad():
            out = model(batch).detach()
        self.encoded_data.append(out)
        self.encoded_data = torch.cat(self.encoded_data, dim=0).squeeze().to("cpu")
