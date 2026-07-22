"""Minimal annotation web app using stdlib http.server only."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from agreement import DIMENSIONS, cohen_kappa, paired_from_files

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / "data" / "items.jsonl"
LABELS_PATH = ROOT / "labels" / "labels.jsonl"


@dataclass(frozen=True)
class Label:
    item_id: str
    rater_id: str
    rubric_id: str
    scores: dict[str, int]
    rationale: str
    cannot_judge: bool = False


def validate_label(label: Label) -> None:
    if label.cannot_judge:
        return
    for dim in DIMENSIONS:
        score = label.scores[dim]
        if score < 1 or score > 5:
            raise ValueError(f"bad {dim}: {score}")


def load_items(path: Path) -> list[dict]:
    items = []
    with path.open() as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def append_label(path: Path, label: Label) -> None:
    validate_label(label)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(
            json.dumps(
                {
                    "item_id": label.item_id,
                    "rater_id": label.rater_id,
                    "rubric_id": label.rubric_id,
                    "scores": label.scores,
                    "rationale": label.rationale,
                    "cannot_judge": label.cannot_judge,
                }
            )
            + "\n"
        )


def page_html(items: list[dict], message: str = "") -> str:
    options = "".join(
        f'<option value="{it["id"]}">{it["id"]}</option>' for it in items
    )
    fields = "".join(
        f'<label>{d}<input name="{d}" type="number" min="1" max="5" '
        f'value="3" required></label><br>'
        for d in DIMENSIONS
    )
    return (
        "<!doctype html><html><body><h1>Support-bot annotation</h1>"
        f"<p>{message}</p><form method='POST' action='/label'>"
        "<label>Rater <input name='rater_id' required></label><br>"
        f"<label>Item <select name='item_id'>{options}</select></label><br>"
        f"{fields}<label>Rationale <input name='rationale'></label><br>"
        "<button type='submit'>Save</button></form>"
        "<p><a href='/kappa?rater_a=alice&rater_b=bob'>kappa</a></p>"
        "</body></html>"
    )


class Handler(BaseHTTPRequestHandler):
    items: list[dict] = []

    def log_message(self, fmt: str, *args) -> None:
        return

    def _send(self, code: int, body: str, ctype: str = "text/html") -> None:
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/kappa"):
            qs = parse_qs(self.path.split("?", 1)[-1]) if "?" in self.path else {}
            if not LABELS_PATH.exists():
                self._send(200, "no labels yet", "text/plain")
                return
            a, b = paired_from_files(
                LABELS_PATH,
                qs.get("rater_a", ["alice"])[0],
                qs.get("rater_b", ["bob"])[0],
            )
            self._send(200, f"cohen_kappa={cohen_kappa(a, b):.3f}\n", "text/plain")
            return
        self._send(200, page_html(self.items))

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode()).items()}
        label = Label(
            item_id=form["item_id"],
            rater_id=form["rater_id"],
            rubric_id="support-v1",
            scores={d: int(form[d]) for d in DIMENSIONS},
            rationale=form.get("rationale", ""),
        )
        append_label(LABELS_PATH, label)
        msg = f"Saved {label.item_id} by {label.rater_id}."
        self._send(200, page_html(self.items, msg))


def seed_demo_labels() -> Path:
    if LABELS_PATH.exists():
        LABELS_PATH.unlink()
    items = load_items(ITEMS_PATH)
    for i, item in enumerate(items):
        for rater, bump in (("alice", 0), ("bob", 0 if i != 1 else 1)):
            scores = {
                "faithfulness": min(5, 4 + bump if i < 3 else 2),
                "helpfulness": 4,
                "tone": 3,
            }
            append_label(
                LABELS_PATH,
                Label(item["id"], rater, "support-v1", scores, "demo"),
            )
    return LABELS_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--seed-demo", action="store_true")
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    Handler.items = load_items(ITEMS_PATH)
    if args.seed_demo or not args.serve:
        path = seed_demo_labels()
        a, b = paired_from_files(path, "alice", "bob")
        print(f"seeded labels -> {path}")
        print(f"cohen_kappa(alice,bob)={cohen_kappa(a, b):.3f}")
        if not args.serve:
            return
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"annotation app on http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
