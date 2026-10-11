"""
料理マスタ(pairing_dishes.json)を index.html の中に写す道具。

index.html をPC上で直接開く(ダブルクリック)と、ブラウザの安全のための仕組みで
別ファイルの pairing_dishes.json を読み込めず、料理が表示されない。
そのため index.html の中にも同じデータを入れておき、画面はそちらを使う。

料理を追加・変更するときは pairing_dishes.json(Android版と共通の元データ)を編集し、
このスクリプトを実行して index.html に反映する。

  python tools/embed_pairing.py          # index.html に反映する
  python tools/embed_pairing.py --check  # 食い違いがないかだけ確認する(違えば終了コード1)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "pairing_dishes.json"
HTML_PATH = ROOT / "index.html"
START = '<script type="application/json" id="pairingData">'
END = "</script><!-- /pairingData -->"


def load_master():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    dishes = data["dishes"]
    ids = [d["id"] for d in dishes]
    names = [d["name"] for d in dishes]
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        sys.exit("料理マスタにIDまたは料理名の重複があります")
    return data


def embedded_text(data):
    # HTMLの中に置くため、"</" は "<\/" にしてscriptタグが途中で閉じないようにする
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/")


def main():
    data = load_master()
    html = HTML_PATH.read_text(encoding="utf-8")
    start = html.find(START)
    end = html.find(END)
    if start < 0 or end < 0:
        sys.exit("index.html に料理データの埋め込み場所が見つかりません")
    current = html[start + len(START):end]
    wanted = embedded_text(data)
    if "--check" in sys.argv:
        if json.loads(current.replace(r"<\/", "</")) != data:
            print("index.html の料理データが pairing_dishes.json と食い違っています。embed_pairing.py を実行してください。")
            sys.exit(1)
        print(f"OK: index.html の料理データは pairing_dishes.json と同じです({len(data['dishes'])}品)")
        return
    html = html[:start + len(START)] + wanted + html[end:]
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")
    print(f"index.html に料理データを反映しました({len(data['dishes'])}品)")


if __name__ == "__main__":
    main()
