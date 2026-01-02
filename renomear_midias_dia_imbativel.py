from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(r"C:\Users\Mauro\Downloads\assai new")

# Mapping of first-level folder name to the token used in the target filename.
CATEGORY_TOKEN = {
    "EH HOJE": "Hoje",
    "EH AMANHA": "Amanha",
    "GENERICO": "Generico",
}

# Mapping of second-level folder name to (media_type, region_token).
SUBDIR_INFO = {
    "CABECA MG": ("cabeca", "Mg"),
    "CABECA NACIONAL": ("cabeca", "Nacional"),
    "ENCERRAMENTO MG": ("assinatura", "Mg"),
    "ENCERRAMENTO NACIONAL": ("assinatura", "Nacional"),
}

# Prefix per category for assinatura files. Cabeca files share the same prefix.
ASS_PREFIX = {
    "EH HOJE": "assDiaImbativeHoje",
    "EH AMANHA": "assDiaImbativelAmanha",
    "GENERICO": "assDiaImbativeGenerico",
}

RATIOS = ("16x9", "9x16", "1x1")

# Explicit overrides to keep legacy naming quirks intact.
SPECIAL_CASES = {
    ("EH HOJE", "CABECA NACIONAL", "1x1"): "cabDiaImbativelHojeNacional1x1mp4.mp4",
}


def infer_ratio(filename: str) -> str:
    for ratio in RATIOS:
        if ratio in filename:
            return ratio
    raise ValueError(f"Nao foi possivel identificar o formato (16x9, 9x16, 1x1) em: {filename}")


def build_target_name(category_dir: str, subdir: str, ratio: str) -> str:
    if (category_dir, subdir, ratio) in SPECIAL_CASES:
        return SPECIAL_CASES[(category_dir, subdir, ratio)]

    media_type, region = SUBDIR_INFO[subdir]

    if media_type == "cabeca":
        category_token = CATEGORY_TOKEN[category_dir]
        return f"cabDiaImbativel{category_token}{region}{ratio}.mp4"

    prefix = ASS_PREFIX[category_dir]
    return f"{prefix}{region}{ratio}.mp4"


def gather_files():
    for category_dir in CATEGORY_TOKEN:
        category_path = ROOT_DIR / category_dir
        if not category_path.is_dir():
            continue

        for subdir in SUBDIR_INFO:
            subdir_path = category_path / subdir
            if not subdir_path.is_dir():
                continue

            for file_path in subdir_path.iterdir():
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() != ".mp4":
                    continue

                yield category_dir, subdir, file_path


def main() -> None:
    if not ROOT_DIR.exists():
        raise SystemExit(f"Diretorio base nao encontrado: {ROOT_DIR}")

    changes = []

    for category_dir, subdir, file_path in gather_files():
        ratio = infer_ratio(file_path.name)
        target_name = build_target_name(category_dir, subdir, ratio)
        target_path = file_path.with_name(target_name)

        if file_path.name == target_name:
            continue

        if target_path.exists():
            raise FileExistsError(
                f"O arquivo de destino {target_path} já existe. "
                "Renomeação interrompida para evitar sobrescrita."
            )

        file_path.rename(target_path)
        changes.append((file_path.name, target_name, str(target_path)))

    if not changes:
        print("Nenhum arquivo foi renomeado. Todos já estavam com o padrão esperado.")
        return

    print("Arquivos renomeados:")
    for original, new, dest in changes:
        print(f" - {original} -> {new}")


if __name__ == "__main__":
    main()
