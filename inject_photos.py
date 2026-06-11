#!/usr/bin/env python3
import os
import argparse
import urllib.parse
from html import escape


def quote_path(p):
    parts = p.replace('\\', '/').split('/')
    return '/'.join(urllib.parse.quote(part) for part in parts)


def generate_photos_index(images_dir, out_html='photos_list.html'):
    images_dir = os.path.abspath(images_dir)
    if not os.path.isdir(images_dir):
        raise SystemExit(f'Images folder not found: {images_dir}')

    # Gather immediate files in root and subdirectories
    blocks = []

    # root-level images
    root_files = sorted([f for f in os.listdir(images_dir)
                         if os.path.isfile(os.path.join(images_dir, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))])
    if root_files:
        blocks.append(('root', root_files))

    for name in sorted(os.listdir(images_dir)):
        path = os.path.join(images_dir, name)
        if os.path.isdir(path):
            imgs = sorted([f for f in os.listdir(path)
                           if os.path.isfile(os.path.join(path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))])
            if imgs:
                blocks.append((name, imgs))

    # Build simple HTML
    lines = ['<!doctype html>', '<html lang="en"><head><meta charset="utf-8"><title>Photos list</title></head><body>']
    for folder, imgs in blocks:
        heading = escape(folder)
        lines.append(f'<section class="photo-block">')
        lines.append(f'<h2>{heading}</h2>')
        for fn in imgs:
            rel = os.path.join('images', folder if folder != 'root' else '', fn).replace('\\', '/')
            rel = rel.replace('//', '/')
            src = quote_path(rel)
            lines.append(f'<img src="{src}" alt="">')
        lines.append('</section>')

    lines.append('</body></html>')

    with open(out_html, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'Wrote photos index to {out_html} ({len(blocks)} folders)')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Inject <img> tags or generate photos index from images folder')
    p.add_argument('--generate-index', action='store_true', help='Generate an HTML file listing images grouped by folder')
    p.add_argument('--images', default='images', help='Path to images folder')
    p.add_argument('--out-index', default='photos_list.html', help='Output HTML file for generated index')
    # legacy insert mode
    p.add_argument('folder', nargs='?', help='Path to folder with images (e.g. images/Arctic Sunrise)')
    p.add_argument('--cell', type=int, default=1, help='1-based index of the photo-cell to target')
    p.add_argument('--html', default='index_work.html', help='Path to HTML file to edit')
    p.add_argument('--out', default=None, help='Optional output HTML file (safe)')
    args = p.parse_args()

    if args.generate_index:
        generate_photos_index(args.images, args.out_index)
    else:
        if not args.folder:
            p.error('folder is required unless --generate-index is used')
        insert_images(args.html, args.folder, args.cell, args.out)
