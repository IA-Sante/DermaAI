from pathlib import Path
import json

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

from src.data_loader import create_generators, prepare_dataframe, split_data
from src.model import build_model, unfreeze_model

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "data" / "raw" / "HAM10000_metadata.csv"
IMAGES_DIR = ROOT / "data" / "raw" / "images"
MODEL_SAVE = ROOT / "models" / "dermai_cnn.h5"

BATCH_SIZE = 32
EPOCHS_PHASE1 = 15
EPOCHS_PHASE2 = 10


def main():
    MODEL_SAVE.parent.mkdir(parents=True, exist_ok=True)

    df = prepare_dataframe(str(METADATA_PATH), str(IMAGES_DIR))
    train_df, val_df, test_df = split_data(df)
    train_gen, val_gen, test_gen = create_generators(
        train_df,
        val_df,
        test_df,
        batch_size=BATCH_SIZE,
    )

    callbacks = [
        ModelCheckpoint(
            str(MODEL_SAVE),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    print("\n=== PHASE 1 : Entraînement de la tête ===")
    model, base_model = build_model()
    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_PHASE1,
        callbacks=callbacks,
        verbose=1,
    )
    with open(ROOT / "models" / "training_history_phase1.json", "w", encoding="utf-8") as file:
        json.dump(history1.history, file, ensure_ascii=False, indent=2)

    print("\n=== PHASE 2 : Fine-tuning ===")
    model = unfreeze_model(model, base_model, fine_tune_at=100)
    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_PHASE2,
        callbacks=callbacks,
        verbose=1,
    )
    with open(ROOT / "models" / "training_history_phase2.json", "w", encoding="utf-8") as file:
        json.dump(history2.history, file, ensure_ascii=False, indent=2)

    print("\n=== ÉVALUATION SUR LE TEST SET ===")
    test_loss, test_acc = model.evaluate(test_gen)
    print(f"Test Accuracy : {test_acc:.4f}")
    print(f"Test Loss     : {test_loss:.4f}")
    print(f"\nModèle sauvegardé dans : {MODEL_SAVE}")


if __name__ == "__main__":
    main()
