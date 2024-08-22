from pathlib import Path
import torch

image_dir = Path('images').resolve()
processed_dir = Path('processed_images').resolve()
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
