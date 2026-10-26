# ローカルプロトタイプの起動方法

## 必要なもの

- Python 3.14
- Rust と Cargo
- Git

Python の依存関係をインストールします。

```bash
pip install -r requirements.txt
```

## 1つのコマンドで起動

リポジトリのルートディレクトリで実行します。

### Linux / macOS

```bash
chmod +x start.sh
./start.sh
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

ランチャーは Rust サーバーをビルドし、ローカルの SQLite データベース用ディレクトリを準備します。サーバーが `127.0.0.1:5000` で待ち受けることを確認してから Python クライアントを起動します。ビルドやサーバー起動に失敗した場合、クライアントは起動しません。どちらかのプロセスが終了すると、もう一方も停止します。

デフォルトのデータベースファイルは `database/the_last_signal.db` です。必要であれば、起動前に `DATABASE_PATH` と `DATABASE_URL` を設定してください。

## 手動で起動する方法

**ターミナル 1 — Rust サーバー**

```bash
cd server_rust
cargo run --locked
```

**ターミナル 2 — Python クライアント**（リポジトリのルートで実行）

```bash
python -m client_python.main
```

`cargo clean` は、完全な再ビルドが必要な場合にのみ実行してください。

## トラブルシューティング

- `cargo` が見つからない場合、Rust と Cargo をインストールし、PATH に追加してください。
- `python` が見つからない場合、Python をインストールし、PATH を確認してください。
- ポート `5000` が既に使われている場合、別のプロセスがポートを使用していないか確認してください。
- データベース接続エラーが出る場合は、`DATABASE_PATH` と `DATABASE_URL` が同じローカルデータベースを参照していることを確認してください。
