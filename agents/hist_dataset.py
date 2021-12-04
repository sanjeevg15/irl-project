import os
import numpy as np
import torch
from torch.utils.data import Dataset
from glob import glob
from core.utils import load_demo
from PIL import Image

class DemoDataPreviousAction(Dataset):
    
    def __init__(self, demo_folder, nb_demos, transform=None):
        if transform:
            self.transform = transform
        else:
            self.transform = lambda x : x

        files = [f for f in glob(os.path.join(demo_folder, '*'))]
        files = np.random.choice(files, nb_demos, False)
        
        self.obs = []
        self.prev_a = []
        self.a = []
        for f in files:
            d = load_demo(f)
            for (o, prev_a, a) in zip(d.observations, [8] + d.actions[:-1], d.actions):
                self.obs.append(Image.fromarray(o))
                v = np.zeros(9, dtype=np.float32); v[prev_a] = 1.0
                self.prev_a.append(v)
                self.a.append(a)
                prev_a = a
        
        self.prev_a = np.array(self.prev_a)
        self.a = np.array(self.a, dtype=np.int64)[:, np.newaxis]

    def __len__(self):
        return len(self.a)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        if isinstance(idx, list):
            obs = torch.stack([self.transform(self.obs[i]) for i in idx])
        elif isinstance(idx, slice):
            obs = torch.stack([self.transform(self.obs[i]) for i in list(range(len(self.obs)))[idx]])
        else:
            obs = self.transform(self.obs[idx])
        prev_a = torch.from_numpy(self.prev_a[idx])
        a = torch.from_numpy(self.a[idx])

        return {
            'obs': obs,
            'prev_a': prev_a,
            'a': a
        }
