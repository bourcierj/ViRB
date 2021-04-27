import torch
import tqdm
import numpy as np
import torchvision.transforms as transforms
from torch.utils.data import Dataset
import glob
from PIL import Image


class NyuDepthEncodableDataset(Dataset):
    """NYU Depth encodable dataset class"""

    def __init__(self, train=True):
        super().__init__()
        data_path = 'data/nyu/train/images/*.png'\
            if train else 'data/nyu/test/images/*.png'
        self.data = list(glob.glob(data_path))
        self.data.sort()
        label_path = 'data/nyu/train/depths/*.tiff'\
            if train else 'data/nyu/test/depths/*.tiff'
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
            transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                 std=[0.5, 0.5, 0.5])
        ])
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        img_path = self.data[idx]
        label_path = self.labels[idx]

        img = self.img_preprocessor(Image.open(img_path))
        mask = np.array(Image.open(label_path).resize((224, 224)))
        mask = torch.tensor(mask)
        mask = mask.unsqueeze(0)

        return img, mask

    def __len__(self):
        return len(self.data)

    def num_classes(self):
        return int(max(self.labels) + 1)
