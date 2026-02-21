from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
IMAGES_DIR = RAW_DIR / "images"
METADATA_PATH = RAW_DIR / "HAM10000_metadata.csv"
MODELS_DIR = ROOT / "models"


def verify_paths() -> bool:
    print("=== Vérification des chemins ===")
    checks = {
        "data/raw": RAW_DIR.exists(),
        "data/raw/images": IMAGES_DIR.exists(),
        "data/raw/HAM10000_metadata.csv": METADATA_PATH.exists(),
        "models": MODELS_DIR.exists(),
    }

    all_ok = True
    for path_name, ok in checks.items():
        status = "OK" if ok else "MANQUANT"
        print(f"- {path_name}: {status}")
        all_ok = all_ok and ok
    print()
    return all_ok


def verify_dataset() -> int:
    print("=== Vérification des données ===")
    if not METADATA_PATH.exists():
        print("- Metadata introuvable, vérification des données interrompue.")
        print()
        return 1

    metadata = pd.read_csv(METADATA_PATH)
    print(f"- Lignes metadata: {len(metadata)}")

    if not IMAGES_DIR.exists():
        print("- Dossier images introuvable.")
        print()
        return 1

    image_files = list(IMAGES_DIR.glob("*.jpg"))
    print(f"- Images .jpg trouvées: {len(image_files)}")

    if "image_id" not in metadata.columns:
        print("- Colonne image_id absente du metadata.")
        print()
        return 1

    metadata["filepath"] = metadata["image_id"].apply(lambda image_id: IMAGES_DIR / f"{image_id}.jpg")
    available = metadata["filepath"].apply(Path.exists)
    available_count = int(available.sum())
    print(f"- Images référencées et présentes: {available_count}/{len(metadata)}")

    if "dx" in metadata.columns:
        dx_counts = metadata.loc[available, "dx"].value_counts().to_dict()
        print(f"- Répartition classes (images présentes): {dx_counts}")

    print()
    return 0 if available_count > 0 else 1


def verify_artifacts() -> None:
    print("=== Vérification des artefacts d'entraînement ===")
    expected = [
        MODELS_DIR / "dermai_cnn.h5",
        MODELS_DIR / "training_history_phase1.json",
        MODELS_DIR / "training_history_phase2.json",
    ]
    for path in expected:
        status = "OK" if path.exists() else "ABSENT"
        print(f"- {path.name}: {status}")
    print()


def main() -> int:
    verify_paths()
    data_status = verify_dataset()
    verify_artifacts()

    if data_status != 0:
        print("Résultat: ÉCHEC - aucune image exploitable trouvée pour l'entraînement.")
        return 1

    print("Résultat: SUCCÈS - dataset prêt pour l'entraînement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
