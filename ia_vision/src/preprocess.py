"""
Preprocessing pipeline for ISIC dermatology images.
"""

import cv2
import numpy as np
from PIL import Image


class ImagePreprocessor:
    """Preprocess medical images for model training and inference.

    Parameters
    ----------
    target_size : tuple[int, int]
        Target (width, height) passed to ``cv2.resize``. Defaults to (224, 224).
        The resulting array shape will be (height, width, 3) following NumPy
        convention.
    """

    def __init__(self, target_size: tuple = (224, 224)):
        self.target_size = target_size

    def load_image(self, image_path: str) -> np.ndarray:
        """Load an image from disk as an RGB NumPy array.

        Parameters
        ----------
        image_path : str
            Path to the image file.

        Returns
        -------
        np.ndarray
            RGB image array with shape (H, W, 3) and dtype uint8.
        """
        img = Image.open(image_path).convert("RGB")
        return np.array(img)

    def resize(self, image: np.ndarray) -> np.ndarray:
        """Resize an image to ``self.target_size``.

        Parameters
        ----------
        image : np.ndarray
            Input image array (H, W, 3).

        Returns
        -------
        np.ndarray
            Resized image array.
        """
        return cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize pixel values to the [0, 1] range.

        Parameters
        ----------
        image : np.ndarray
            Input image array with values in [0, 255].

        Returns
        -------
        np.ndarray
            Float32 array with values in [0, 1].
        """
        return image.astype(np.float32) / 255.0

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

        The enhancement is applied per channel in the LAB colour space to
        improve local contrast without over-amplifying noise.

        Parameters
        ----------
        image : np.ndarray
            RGB image array with dtype uint8.

        Returns
        -------
        np.ndarray
            Contrast-enhanced RGB image array with dtype uint8.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    def preprocess(self, image_path: str) -> np.ndarray:
        """Run the full preprocessing pipeline on a single image.

        Steps: load → resize → CLAHE → normalize.

        Parameters
        ----------
        image_path : str
            Path to the image file.

        Returns
        -------
        np.ndarray
            Preprocessed float32 array of shape (height, width, 3) in [0, 1],
            where (height, width) correspond to the reversed ``target_size``
            tuple (which is given as (width, height) to ``cv2.resize``).
        """
        image = self.load_image(image_path)
        image = self.resize(image)
        image = self.apply_clahe(image)
        image = self.normalize(image)
        return image

    def process_batch(self, image_paths: list) -> np.ndarray:
        """Preprocess a batch of images.

        Parameters
        ----------
        image_paths : list[str]
            List of paths to image files.

        Returns
        -------
        np.ndarray
            Array of shape (N, H, W, 3) containing all preprocessed images.
        """
        return np.stack([self.preprocess(p) for p in image_paths])
