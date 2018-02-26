set -e
export PATH=$PATH:~/.bin
mv gulp-electron-cache /tmp/
mv .electron .bin ~/
chmod u+x ~/.bin/yarn.js
ln -s yarn.js ~/.bin/yarn
yarn config set yarn-offline-mirror "$(realpath ./yarn-mirror)"
# tar -xzvf yarn-mirror/vscode-ripgrep-0.7.1-patch.0.1.tgz
# mv package vscode-ripgrep-0.7.1-patch.0.1
# pushd vscode-ripgrep-0.7.1-patch.0.1
#     mv _node_modules node_modules
#     yarn link
#     echo > dist/postinstall.js
#     mkdir bin
#     unzip ../misc/ripgrep-0.7.1-patch.1-linux-$(node -e 'console.log(process.arch)').zip rg -d bin/
#     chmod 755 bin/rg
# popd
tar -xzvf yarn-mirror/vscode-1.0.1.tgz
mv package vscode-1.0.1
pushd vscode-1.0.1
    yarn link
    echo > bin/install
    cp ../vscode/src/vs/vscode.d.ts .
popd
pushd vscode
    echo '[]' > build/builtInExtensions.json
#     yarn link vscode-ripgrep
    pushd extensions
        rm -r vscode-api-tests vscode-colorize-tests
        pushd emmet
            yarn link vscode
        popd
    popd
    sed -i "s/'vscode\-api\-tests',//" build/gulpfile.vscode.js
    sed -i "s/'vscode\-colorize\-tests',//" build/gulpfile.vscode.js
    sed -i "s/'vscode\-api\-tests',//" build/npm/postinstall.js
    sed -i "s/'vscode\-colorize\-tests',//" build/npm/postinstall.js
    mkdir -p node_modules/.hooks
cat > node_modules/.hooks/install <<'EOF'
#!/bin/sh
[ $npm_package_name == 'vscode-ripgrep' ] || exit 0
echo $0
echo ${BASH_SOURCE[0]}
pwd
EOF
    while true; do
        npm_config_tarball="$(realpath ../misc/iojs-v1.7.9.tar.gz)" yarn install --offline --verbose --frozen-lockfile && break
    done
#     rm node_modules/vscode-ripgrep
#     cp -r ../vscode-ripgrep-0.7.1-patch.0.1 node_modules/vscode-ripgrep
    echo "/// <reference types='@types/node'/>" > extensions/emmet/src/typings/refs.d.ts
    node_modules/.bin/gulp vscode-linux-$(node -e 'console.log(process.arch)')-min $([ $FLATPAK_ARCH == 'x86_64' ] && echo '--max_old_space_size=4096')
popd
mv VSCode-linux-$(node -e 'console.log(process.arch)') /app/
ln -s ../VSCode-linux-$(node -e 'console.log(process.arch)')/code-oss /app/bin/code-oss
