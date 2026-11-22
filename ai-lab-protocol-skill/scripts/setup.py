"""Install bundled Python 3.11 wheels in an isolated environment."""
import argparse
import os
import platform
import subprocess
import sys
import venv
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('--venv', type=Path, default=root / '.venv')
    parser.add_argument('--online', action='store_true', help='Allow PyPI for unsupported Python/platform combinations')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    system, arch = platform.system(), platform.machine().lower()
    key = {('Linux', 'x86_64'): 'linux-x86_64', ('Darwin', 'arm64'): 'macos-arm64',
           ('Windows', 'amd64'): 'windows-x86_64', ('Windows', 'x86_64'): 'windows-x86_64'}.get((system, arch))
    supported = key is not None and sys.version_info[:2] == (3, 11)
    if not supported and not args.online:
        parser.error('Offline wheels support CPython 3.11 on Linux x86_64, macOS arm64 and Windows x86_64. Use Python 3.11 or explicitly pass --online.')
    python = args.venv / ('Scripts/python.exe' if system == 'Windows' else 'bin/python')
    command = [str(python), '-m', 'pip', 'install', '--disable-pip-version-check']
    if not args.online:
        command += ['--no-index', '--find-links', str(root / 'wheels' / key)]
    command += ['-r', str(root / 'requirements.lock.txt')]
    print('Environment:', args.venv)
    print('Install command:', subprocess.list2cmdline(command))
    print('Native LibreOffice is separate; see references/zavislosti.md.')
    if args.dry_run:
        return
    venv.EnvBuilder(with_pip=False, symlinks=system != 'Windows').create(args.venv)
    bootstraps = list((root / 'wheels' / (key or 'linux-x86_64')).glob('pip-*-py3-none-any.whl'))
    if len(bootstraps) != 1:
        parser.error('Exactly one bundled pip bootstrap wheel is required')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(bootstraps[0])
    subprocess.run(command, check=True, env=env)
    subprocess.run([str(python), str(root / 'scripts/check_env.py')], check=True)

if __name__ == '__main__':
    main()
