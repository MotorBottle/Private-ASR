import os
import torch

device = os.getenv("DEVICE", "cuda:0" if torch.cuda.is_available() else "cpu")  # 自动检测GPU或使用CPU
print(device)