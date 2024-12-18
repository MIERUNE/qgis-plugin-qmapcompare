# qgis-plugin-template

QGIS3.x プラグイン開発のひな形

## Preparation

1. install `uv`
   - https://docs.astral.sh/uv/#getting-started

2. install dependencies with uv

    ```sh
    # macOS
    uv venv --python /Applications/QGIS.app/Contents/MacOS/bin/python3 --system-site-packages
    
    # Windows 適切なバージョンのQGISのディレクトリを参照すること
    uv venv --python C:\Program Files\QGIS 3.28.2\apps\Python39\python.exe --system-site-packages
    ```

    仮想環境がカレントディレクトリに`.venv`フォルダとして作成されます。

3. (when VSCode) 仮想環境をVSCode上のPythonインタプリタとして選択

    VSCodeはカレントディレクトリの仮想環境を検出しますが、手動で選択する必要がある場合もあります。  

    1. [Cmd + Shift + P]でコマンドパレットを開く
    2. [Python: Select Interpreter]を見つけてクリック
    3. 利用可能なインタプリタ一覧が表示されるので、先ほど作成した仮想環境`/.venv/bin/python`を選択（通常、リストの一番上に"Recommended"として表示される）
