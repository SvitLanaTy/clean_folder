from pathlib import Path
import shutil
import sys
import re


GROUPS_FILE = {
    'images': ['JPEG', 'JPG', 'PNG', 'SVG'],
    'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
    'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
    'video': ['AVI', 'MP4', 'MOV', 'MKV'],
    'archives': ['ZIP', 'GZ', 'TAR'],
    'my_other': []
}

FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()

group_folders = {'archives': [], 'video': [], 'audio': [],
                 'documents': [], 'images': [], 'my_other': []}

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = dict()

for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyrillic)] = latin
    TRANS[ord(cyrillic.upper())] = latin.upper()


def normalize(name: str) -> str:
    if name.find(".") == 0:
        name = name.replace('.', '_', 1)

    if name.rfind(".") != -1:
        base_name, ext = name.rsplit('.', 1)
        translate_name = re.sub(
            r'[^a-zA-Z\.\d]', '_', base_name.translate(TRANS))
        return f"{translate_name}.{ext}"
    else:
        return re.sub(r'\W', '_', name.translate(TRANS))


def get_extension(name: str) -> str:
    return Path(name).suffix[1:].upper()


def scan(folder: Path):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'my_other'):
                FOLDERS.append(item)
                scan(item)
            continue
        extension = get_extension(item.name)
        full_name = folder / item.name
        if not extension:
            group_folders['my_other'].append(full_name)
        else:
            all_ext = []
            for val in GROUPS_FILE.values():
                all_ext += val
            if extension in all_ext:
                for key, value in GROUPS_FILE.items():
                    if extension in value:
                        group_folders[key].append(full_name)
                        EXTENSIONS.add(extension)
                        break
            else:
                UNKNOWN.add(extension)
                group_folders['my_other'].append(full_name)


def handle_non_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    file_name.replace(target_folder / normalize(file_name.name))


def handle_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / \
        normalize(file_name.name.replace(file_name.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(file_name.absolute()),
                              str(folder_for_file.absolute()))
    except shutil.ReadError:
        folder_for_file.rmdir()
        return
    file_name.unlink()


def main(folder: Path):
    scan(folder)
    for file in group_folders['images']:
        handle_non_archive(file, folder / 'images')
    for file in group_folders['audio']:
        handle_non_archive(file, folder / 'audio')
    for file in group_folders['video']:
        handle_non_archive(file, folder / 'video')
    for file in group_folders['documents']:
        handle_non_archive(file, folder / 'documents')
    for file in group_folders['my_other']:
        handle_non_archive(file, folder / 'my_other')

    for file in group_folders['archives']:
        handle_archive(file, folder / 'archives')

    for folder in FOLDERS[::-1]:
        try:
            folder.rmdir()
        except OSError:
            print(f'Error during remove folder {folder}')


def start():
    if sys.argv[1]:
        folder_process = Path(sys.argv[1])
        main(folder_process)
