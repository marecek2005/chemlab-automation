"""Report the actual runtime and optional DOCX-to-PDF converter."""
import argparse
import importlib.metadata
import json
import shutil
import sys
from pathlib import Path

PACKAGES = ['python-docx', 'openpyxl', 'pypdf', 'matplotlib', 'PyMuPDF']

def converter():
    for name in ['soffice', 'libreoffice', 'soffice.exe']:
        path = shutil.which(name)
        if path:
            return path
    candidates = [Path('/Applications/LibreOffice.app/Contents/MacOS/soffice')]
    import os
    for env in ['PROGRAMFILES', 'PROGRAMFILES(X86)']:
        if os.environ.get(env):
            candidates.append(Path(os.environ[env]) / 'LibreOffice/program/soffice.exe')
    return next((str(p) for p in candidates if p.is_file()), None)

def check():
    versions, missing = {}, []
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            missing.append(package)
    return {'python': sys.version.split()[0], 'executable': sys.executable,
            'packages': versions, 'missing_packages': missing,
            'libreoffice': converter(), 'python_libraries_ready': not missing,
            'docx_headless_render_ready': not missing and converter() is not None}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-render', action='store_true')
    args = parser.parse_args()
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(1 if result['missing_packages'] or (args.require_render and not result['libreoffice']) else 0)
