"""Independent DOCX/PDF visual-QA renderer; no account-specific services."""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path
import pymupdf
from check_env import converter

def render_pdf(pdf, output, dpi):
    output.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf) as document:
        if not len(document):
            raise ValueError('PDF has no pages')
        for i, page in enumerate(document):
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72), alpha=False)
            pixmap.save(str(output / f'page-{i + 1}.png'))
        print(f'PDF pages rendered: {len(document)}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--soffice', type=Path)
    parser.add_argument('--dpi', type=int, default=150)
    args = parser.parse_args()
    source = args.input.resolve()
    out = args.output_dir.resolve()
    if not source.is_file():
        parser.error('Input does not exist')
    if not 72 <= args.dpi <= 600:
        parser.error('DPI must be between 72 and 600')
    out.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() == '.pdf':
        render_pdf(source, out, args.dpi)
        return
    if source.suffix.lower() != '.docx':
        parser.error('Only DOCX and PDF inputs are supported')
    binary = str(args.soffice) if args.soffice else converter()
    if not binary:
        parser.error('LibreOffice is unavailable. Install it or export this DOCX to PDF in Word and render that PDF with this script.')
    with tempfile.TemporaryDirectory(prefix='protokol-render-') as temporary:
        temp = Path(temporary)
        profile = (temp / 'profile').as_uri()
        env = os.environ.copy()
        command = [binary, '-env:UserInstallation=' + profile, '--headless', '--convert-to',
                   'pdf', '--outdir', str(temp), str(source)]
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=180)
        pdf = temp / (source.stem + '.pdf')
        if result.returncode or not pdf.is_file():
            raise RuntimeError('DOCX conversion failed: ' + result.stdout + result.stderr)
        target = out / pdf.name
        target.write_bytes(pdf.read_bytes())
        render_pdf(target, out, args.dpi)
    print('Inspect every page PNG before delivering the document.')

if __name__ == '__main__':
    main()
