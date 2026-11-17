
import shutil
from pathlib import Path


# Comprehensive file extension classification
FILE_CATEGORIES = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".svg", ".ico", ".tif", ".tiff", ".heic", ".heif",
        ".raw", ".cr2", ".nef", ".avif"
    ],

    "Documents": [
        ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt",
        ".ppt", ".pptx", ".odp", ".xls", ".xlsx", ".ods",
        ".csv", ".tex"
    ],

    "Videos": [
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
        ".webm", ".mpeg", ".mpg", ".m4v", ".3gp", ".ts"
    ],

    "Audio": [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a",
        ".wma", ".aiff", ".opus", ".mid", ".midi"
    ],

    "Web Files": [
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx",
        ".vue", ".svelte", ".wasm"
    ],

    "Source Code": [
        ".py", ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".go", ".rs", ".php", ".rb", ".swift",
        ".kt", ".kts", ".dart", ".r", ".m", ".mm",
        ".sh", ".bash", ".ps1", ".bat", ".cmd",
        ".ipynb", ".class", ".jar", ".war"
    ],

    "Data Files": [
        ".json", ".xml", ".yaml", ".yml", ".toml",
        ".sql", ".db", ".sqlite", ".sqlite3",
        ".parquet", ".avro", ".feather", ".pkl",
        ".pickle", ".h5", ".hdf5", ".mat", ".csv"
    ],

    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz",
        ".bz2", ".xz", ".tgz", ".zst", ".iso"
    ],

    "Applications": [
        ".exe", ".msi", ".apk", ".app", ".deb",
        ".rpm", ".dmg", ".appx", ".msix"
    ],

    "Fonts": [
        ".ttf", ".otf", ".woff", ".woff2", ".eot"
    ],

    "Design Files": [
        ".psd", ".ai", ".xd", ".fig", ".sketch",
        ".indd", ".eps", ".afdesign", ".afphoto",
        ".xcf", ".cdr", ".blend"
    ],

    "3D Files": [
        ".obj", ".stl", ".fbx", ".gltf", ".glb",
        ".dae", ".3ds", ".step", ".stp", ".iges",
        ".igs", ".3mf"
    ],

    "E-books": [
        ".epub", ".mobi", ".azw", ".azw3", ".djvu"
    ],

    "System Files": [
        ".dll", ".sys", ".ini", ".cfg", ".conf",
        ".log", ".tmp", ".bak", ".dat", ".reg"
    ]
}


class FileOrganizer:

    def __init__(self):
        self.history = []

    def get_category(self, file_path):

        path = Path(file_path)
        filename = path.name.lower()
        extension = path.suffix.lower()

        # Detect temporary Office lock files
        if filename.startswith("~$"):
            return "Temporary Files"

        # Detect common temporary files
        if extension in [".tmp", ".temp", ".bak"]:
            return "Temporary Files"

        for category, extensions in FILE_CATEGORIES.items():
            if extension in extensions:
                return category

        return "Others"

    def get_unique_path(self, destination):

        if not destination.exists():
            return destination

        counter = 1

        while True:
            new_name = (
                f"{destination.stem}_{counter}"
                f"{destination.suffix}"
            )

            new_path = destination.with_name(new_name)

            if not new_path.exists():
                return new_path

            counter += 1

    def organize_folder(self, folder_path):

        folder = Path(folder_path)

        result = {
            "moved": 0,
            "failed": 0,
            "details": [],
            "errors": []
        }

        if not folder.exists() or not folder.is_dir():
            result["errors"].append("Invalid folder selected.")
            return result

        for file_path in folder.iterdir():

            if not file_path.is_file():
                continue

            try:
                category = self.get_category(file_path)

                destination_folder = folder / category
                destination_folder.mkdir(
                    parents=True,
                    exist_ok=True
                )

                destination = destination_folder / file_path.name
                destination = self.get_unique_path(destination)

                shutil.move(
                    str(file_path),
                    str(destination)
                )

                self.history.append({
                    "original": str(file_path),
                    "destination": str(destination)
                })

                result["moved"] += 1

                result["details"].append({
                    "name": destination.name,
                    "category": category,
                    "status": "Success"
                })

            except OSError as error:

                result["failed"] += 1

                result["errors"].append(
                    f"{file_path.name}: {error}"
                )

        return result

    def undo_last_organization(self):

        restored = 0
        failed = 0

        while self.history:

            operation = self.history[-1]

            original = Path(operation["original"])
            destination = Path(operation["destination"])

            try:
                if not destination.exists() or original.exists():
                    failed += 1
                    break

                original.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                shutil.move(
                    str(destination),
                    str(original)
                )

                self.history.pop()
                restored += 1

            except OSError:
                failed += 1
                break

        return {
            "restored": restored,
            "failed": failed
        }
