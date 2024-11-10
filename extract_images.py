import base64
import sys
import pathlib
import hashlib
import re

DEFAULT_ATTACHMENTS_DIR = "Attachments"


def extract_image_from_line(line:str) -> dict:
    image_encoded = line.strip()[4:-1]
    header, encoded_content = image_encoded[:22], image_encoded[22:]
    assert header == 'data:image/png;base64,'

    decoded_content = base64.decodebytes(bytes(encoded_content, 'ascii'))

    return dict(content=decoded_content, type="png")


def get_attachments_dir(note:pathlib.Path) -> pathlib.Path:
    for d in note.parents:
        if (d / ".obsidian").exists():
            return d / DEFAULT_ATTACHMENTS_DIR
    raise ValueError(f"Can't find obsidian vault root for note {note}")


def get_image_filename(attachments_dir:pathlib.Path, note_name:str, image_type:str, image_content:bytes) -> pathlib.Path:
    name_template = attachments_dir / f"_.{image_type}"
    suffix = hashlib.sha1(image_content).hexdigest()[:16]
    name = name_template.with_stem(f"{note_name}_{suffix}")

    return name


def extract_all_images(filename: str, force:bool=False, attachments_dir:str|None=None) -> str:
    _filename = pathlib.Path(filename)
    md = open(_filename).readlines()
    md_images = [ i for i, x in enumerate(md) if x.startswith('![](data:') ]
    note_name = _filename.stem

    if attachments_dir is None:
        _attachments_dir = get_attachments_dir(_filename)
    else:
        _attachments_dir = pathlib.Path(attachments_dir)

    for mdi in md_images:
        image = extract_image_from_line(md[mdi])
        image_filename = get_image_filename(_attachments_dir, note_name, image['type'], image['content'])
        if image_filename.exists() and not force:
            raise RuntimeError(f"Refusing to overwrite image file {image_filename}, enable force to override")
        image_filename.write_bytes(image['content'])
        image_line = f'![[{image_filename}]]\n'
        md[mdi] = image_line

    return "".join(md)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract all embedded images to the attachments dir")
    parser.add_argument("-f", "--force", dest="force", action="store_true", help="Overwrite existing image files")
    parser.add_argument("-i", "--in-place", dest="in_place", action="store_true", help="Overwrite source file")
    parser.add_argument("--attachments-dir", dest="attachments", help=f"Path to attachments dir (default: {DEFAULT_ATTACHMENTS_DIR} in vault root)")
    parser.add_argument("filename", help="Markdown file")

    args = parser.parse_args()

    new_md = extract_all_images(args.filename, force=args.force, attachments_dir=args.attachments)
    if args.in_place:
        open(args.filename, "w").write(new_md)
    else:
        print(new_md, end="")


if __name__ == "__main__":
    main()
