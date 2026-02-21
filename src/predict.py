from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "dermai_cnn.h5"

CLASS_INFO = {
    0: {"name": "nv", "label": "Naevus mélanocytaire", "risk_weight": 0.1},
    1: {"name": "mel", "label": "Mélanome", "risk_weight": 0.95},
    2: {"name": "bkl", "label": "Kératose bénigne", "risk_weight": 0.2},
    3: {"name": "bcc", "label": "Carcinome basocellulaire", "risk_weight": 0.75},
    4: {"name": "akiec", "label": "Kératose actinique", "risk_weight": 0.6},
    5: {"name": "vasc", "label": "Lésion vasculaire", "risk_weight": 0.3},
    6: {"name": "df", "label": "Dermatofibrome", "risk_weight": 0.15},
}

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Modèle introuvable: {MODEL_PATH}")

model = tf.keras.models.load_model(str(MODEL_PATH))


def predict_image(image_path: str) -> dict:
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array, verbose=0)[0]
    predicted_class = int(np.argmax(predictions))
    confidence = float(predictions[predicted_class])

    score_image = float(
        np.sum([predictions[i] * CLASS_INFO[i]["risk_weight"] for i in range(len(predictions))])
    )

    return {
        "predicted_class": CLASS_INFO[predicted_class]["label"],
        "confidence": round(confidence, 4),
        "score_image": round(score_image, 4),
        "all_probabilities": {
            CLASS_INFO[i]["label"]: round(float(predictions[i]), 4)
            for i in range(len(predictions))
        },
    }


if __name__ == "__main__":
    sample_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "images" / "ISIC_0024306.jpg"
    if sample_path.exists():
        print(predict_image(str(sample_path)))
    else:
        print(f"Image de test introuvable: {sample_path}")
