"""Verify portable file references, syntax and recorded SHA-256 digests."""
import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    errors = []
    skill = (root / 'SKILL.md').read_text()
    if not re.match(r'^---\nname: protokol\ndescription: .+\n---\n', skill):
        errors.append('SKILL.md frontmatter is missing or invalid')
    for relative in ['agents/openai.yaml', 'assets/VzorProt-Final.pdf', 'requirements.txt',
                     'requirements.lock.txt', 'references/obory.md', 'references/vzor-a-styl.md',
                     'references/technicky-postup.md', 'references/zavislosti.md', 'references/typografie.md', 'assets/psani-textu.pdf', 'assets/typograficka-pravidla.pdf', 'assets/odborne-texty.pdf']:
        if not (root / relative).is_file():
            errors.append('Missing dependency: ' + relative)
    for file in root.rglob('*.md'):
        text = file.read_text()
        for marker in ['libfile_', 'file_00000000', '/Users/', 'skill://', 'api/library/files/', 'oai-library://']:
            if marker in text:
                errors.append('Account-specific reference: ' + str(file.relative_to(root)))
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in link or link.startswith('#'):
                continue
            if not (file.parent / link.split('#')[0]).exists():
                errors.append('Broken relative link: ' + link)
    for file in (root / 'scripts').glob('*.py'):
        ast.parse(file.read_text(), filename=str(file))
    if (root / 'assets/VzorProt-Final.pdf').is_file() and not (root / 'assets/VzorProt-Final.pdf').read_bytes().startswith(b'%PDF'):
        errors.append('Bundled reference is not a PDF')
    manifest = root / 'manifest.json'
    if not manifest.is_file():
        errors.append('Manifest is missing')
    else:
        for item in json.loads(manifest.read_text())['files']:
            path = root / item['path']
            if not path.is_file():
                errors.append('Missing manifest file: ' + item['path'])
            elif hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                errors.append('Checksum mismatch: ' + item['path'])
    print(json.dumps({'valid': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
    sys.exit(bool(errors))

if __name__ == '__main__':
    main()
