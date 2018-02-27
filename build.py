import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from xml.dom import minidom

os.environ["PATH"] += os.pathsep + str(Path.home() / '.bin')

PRODUCT = json.load(open('vscode/product.json'))
NODE_STYLE_ARCH = subprocess.run([
    'node',
    '-e',
    'console.log(process.arch)'
], stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout.strip()

shutil.move('gulp-electron-cache', '/tmp')
shutil.move('.electron', str(Path.home()))
shutil.move('.bin', str(Path.home()))
os.chmod(str(Path.home() / '.bin' / 'yarn.js'), 0o744)
os.symlink('yarn.js', str(Path.home() / '.bin' / 'yarn'))

subprocess.run([
    'yarn',
    'config',
    'set',
    'yarn-offline-mirror',
    os.path.realpath('yarn-mirror')
], check=True)

shutil.unpack_archive('yarn-mirror/vscode-ripgrep-0.7.1-patch.0.1.tgz')
shutil.move('package', 'vscode-ripgrep-0.7.1-patch.0.1')
os.chdir('vscode-ripgrep-0.7.1-patch.0.1')
subprocess.run([
    'yarn',
    'link'
], check=True)
os.mkdir('bin')
shutil.unpack_archive('../misc/ripgrep-0.7.1-patch.0-linux-' + NODE_STYLE_ARCH + '.zip', 'bin')
os.chmod('bin/rg', 0o755)
os.chdir('..')

shutil.unpack_archive('yarn-mirror/vscode-1.0.1.tgz')
shutil.move('package', 'vscode-1.0.1')
os.chdir('vscode-1.0.1')
subprocess.run([
    'yarn',
    'link'
], check=True)
open('bin/install', 'w').close()
shutil.copy('../vscode/src/vs/vscode.d.ts', '.')
os.chdir('..')

os.chdir('vscode')
with open('build/builtInExtensions.json', 'w') as f:
    f.write('[]')
subprocess.run([
    'yarn',
    'link',
    'vscode-ripgrep'
], check=True)
shutil.rmtree('extensions/vscode-api-tests')
shutil.rmtree('extensions/vscode-colorize-tests')
os.chdir('extensions/emmet')
subprocess.run([
    'yarn',
    'link',
    'vscode'
], check=True)
os.chdir('../..')
with open("build/gulpfile.vscode.js", "r") as f:
    lines = f.readlines()
with open("build/gulpfile.vscode.js", "w") as f:
    for line in lines:
        f.write(line.replace("'vscode-api-tests',", '').replace("'vscode-colorize-tests',", ''))
with open("build/npm/postinstall.js", "r") as f:
    lines = f.readlines()
with open("build/npm/postinstall.js", "w") as f:
    for line in lines:
        f.write(line.replace("'vscode-api-tests',", '').replace("'vscode-colorize-tests',", ''))
env = os.environ.copy()
env["npm_config_tarball"] = os.path.realpath('../misc/iojs-v1.7.9.tar.gz')
env["npm_config_python"] = '/app/bin/python2.7'
subprocess.run([
    'yarn',
    'install',
    '--offline',
    '--verbose',
    '--frozen-lockfile'
], check=True, env=env)
os.unlink('node_modules/vscode-ripgrep')
shutil.copytree('../vscode-ripgrep-0.7.1-patch.0.1', 'node_modules/vscode-ripgrep')
with open('extensions/emmet/src/typings/refs.d.ts', 'w') as f:
    f.write("/// <reference types='@types/node'/>")
subprocess.run([
    'node_modules/.bin/gulp',
    'vscode-linux-' + NODE_STYLE_ARCH + '-min',
    '--max_old_space_size=4096'
], check=True)
os.chdir('..')

shutil.move('VSCode-linux-' + NODE_STYLE_ARCH, '/app/share/' + PRODUCT['applicationName'])
os.symlink('../share/' + PRODUCT['applicationName'] + '/bin/' + PRODUCT['applicationName'], '/app/bin/' + PRODUCT['applicationName'])
shutil.copy('vscode/resources/linux/code.png', '/app/share/icons/hicolor/1024x1024/apps/' + PRODUCT['darwinBundleIdentifier'] + '.png')
for size in [16, 24, 32, 48, 64, 128, 192, 256, 512]:
    size = str(size)
    with open('/app/share/icons/hicolor/' + size + 'x' + size + '/apps/' + PRODUCT['darwinBundleIdentifier'] + '.png', 'wb') as f:
        f.write(subprocess.run([
            'magick',
            'convert',
            'vscode/resources/linux/code.png',
            '-resize',
            size + 'x' + size,
            '-'
        ], check=True, stdout=subprocess.PIPE).stdout)

with open("vscode/resources/linux/code.desktop", "r") as f:
    lines = f.readlines()
with open('/app/share/applications/' + PRODUCT['darwinBundleIdentifier'] + '.desktop', "w") as f:
    for line in lines:
        f.write(line
                .replace('Exec=/usr/share/@@NAME@@/@@NAME@@', 'Exec=' + PRODUCT['applicationName'])
                .replace('@@NAME_LONG@@', PRODUCT['nameLong'])
                .replace('@@NAME_SHORT@@', PRODUCT['nameShort'])
                .replace('@@NAME@@', PRODUCT['applicationName']))

with open("vscode/resources/linux/code.appdata.xml", "r") as f:
    lines = f.read()
dom = minidom.parseString(lines)
releases = dom.createElement('releases')
env = os.environ.copy()
env["TZ"] = 'UTC'
env["GIT_DIR"] = 'vscode/.git'
for entry in json.load(open('stable')):
    if entry['version'].split('.')[0] == 0:
        continue
    release = dom.createElement('release')
    release.setAttribute('version', entry['version'])
    release.setAttribute('date', subprocess.run([
        'git',
        'show',
        '-s',
        '--format=%cd',
        '--date=iso-strict-local',
        entry['id']
    ], stdout=subprocess.PIPE, universal_newlines=True, check=True, env=env).stdout.strip())
    releases.appendChild(release)
dom.getElementsByTagName('component')[0].appendChild(releases)
lines = dom.toprettyxml(encoding='UTF-8')
with open('/app/share/appdata/' + PRODUCT['darwinBundleIdentifier'] + '.appdata.xml', "w") as f:
    f.write(lines
            .replace('@@NAME_LONG@@', PRODUCT['nameLong'])
            .replace('@@NAME@@', PRODUCT['darwinBundleIdentifier'])
            .replace('@@LICENSE@@', PRODUCT['licenseName']))
