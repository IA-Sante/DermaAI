"""
predict.py – Fonction de prédiction DermaAI prête pour le backend.

Usage:
    from predict import load_model, predict_image

    model = load_model("models/dermai_cnn.h5")
    result = predict_image(model, "path/to/image.jpg")
    print(result)
    # {'predicted_class': 'mel', 'confidence': 0.87, 'probabilities': {...}}
"""

import os
from typing import Dict, List, Union

import numpy as np
from PIL import Image
import tensorflow as tf

CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
IMG_SIZE = (224, 224)

# Labels lisibles pour l'interface utilisateur
CLASS_LABELS = {
    "akiec": "Actinic keratoses",
    "bcc":   "Basal cell carcinoma",
    "bkl":   "Benign keratosis-like lesions",
    "df":    "Dermatofibroma",
    "mel":   "Melanoma",
    "nv":    "Melanocytic nevi",
    "vasc":  "Vascular lesions",
}


def load_model(model_path: str = "models/dermai_cnn.h5") -> tf.keras.Model:
    """
    Charge le modèle Keras sauvegardé.

    Args:
        model_path: Chemin vers le fichier .h5.

    Returns:
        Modèle Keras chargé.

    Raises:
        FileNotFoundError: Si le fichier modèle est introuvable.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Modèle introuvable : {model_path}\n"
            "Lancez d'abord src/train.py pour entraîner "
            "et sauvegarder le modèle."
        )
    return tf.keras.models.load_model(model_path)


def preprocess_image(image_input: Union[str, Image.Image]) -> np.ndarray:
    """
    Prépare une image pour l'inférence.

    Args:
        image_input: Chemin vers l'image ou objet PIL.Image.

    Returns:
        Tableau numpy de forme (1, 224, 224, 3), normalisé entre 0 et 1.
    """
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")

    img = img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def predict_image(model: tf.keras.Model,
                  image_input: Union[str, Image.Image]) -> Dict:
    """
    Prédit la classe d'une lésion cutanée.

    Args:
        model:        Modèle Keras chargé (via ``load_model``).
        image_input:  Chemin vers l'image ou objet PIL.Image.

    Returns:
        Dictionnaire contenant :
        - ``predicted_class``  : code court de la classe (ex. ``"mel"``).
        - ``predicted_label``  : nom complet (ex. ``"Melanoma"``).
        - ``confidence``       : probabilité de la classe prédite (float).
        - ``probabilities``    : dict {classe: probabilité}
                                pour toutes les classes.
    """
    img_array = preprocess_image(image_input)
    preds = model.predict(img_array, verbose=0)[0]

    idx = int(np.argmax(preds))
    predicted_class = CLASSES[idx]

    probabilities = {cls: float(preds[i]) for i, cls in enumerate(CLASSES)}

    return {
        "predicted_class": predicted_class,
        "predicted_label": CLASS_LABELS[predicted_class],
        "confidence": float(preds[idx]),
        "probabilities": probabilities,
    }


def predict_batch(model: tf.keras.Model,
                  image_paths: List[str]) -> List[Dict]:
    """
    Prédit les classes pour une liste d'images.

    Args:
        model:        Modèle Keras chargé.
        image_paths:  Liste de chemins vers les images.

    Returns:
        Liste de dictionnaires (même format que ``predict_image``).
    """
    arrays = np.concatenate(
        [preprocess_image(p) for p in image_paths], axis=0
    )
    preds = model.predict(arrays, verbose=0)

    results = []
    for pred in preds:
        idx = int(np.argmax(pred))
        predicted_class = CLASSES[idx]
        results.append({
            "predicted_class": predicted_class,
            "predicted_label": CLASS_LABELS[predicted_class],
            "confidence": float(pred[idx]),
            "probabilities": {
                cls: float(pred[i]) for i, cls in enumerate(CLASSES)
            },
        })
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path> [model_path]")
        sys.exit(1)

    image_path = sys.argv[1]
    _model_path = sys.argv[2] if len(sys.argv) > 2 else "models/dermai_cnn.h5"

    m = load_model(_model_path)
    result = predict_image(m, image_path)
    print(
        f"Classe prédite  : {result['predicted_class']}"
        f" – {result['predicted_label']}"
    )
    print(f"Confiance       : {result['confidence']:.2%}")
    print("Probabilités    :")
    for cls, prob in sorted(result["probabilities"].items(),
                            key=lambda x: x[1], reverse=True):
        print(f"  {cls:6s} ({CLASS_LABELS[cls]:35s}) : {prob:.2%}")
