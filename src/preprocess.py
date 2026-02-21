from pathlib import Path

import numpy as np
from PIL import Image

IMG_SIZE = (224, 224)


def preprocess_image(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE)
    img_array = np.array(img, dtype=np.float32) / 255.0
    return img_array


def preprocess_for_model(image_path: str) -> np.ndarray:
    img = preprocess_image(image_path)
    return np.expand_dims(img, axis=0)


if __name__ == "__main__":
    sample = Path(__file__).resolve().parents[1] / "data" / "raw" / "images"
    first = next(sample.glob("*.jpg"), None)
    if first is None:
        print("Aucune image trouvée dans data/raw/images")
    else:
        arr = preprocess_for_model(str(first))
        print("Image prétraitée, shape:", arr.shape)
