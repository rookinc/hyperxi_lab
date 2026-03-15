#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass
from itertools import product, combinations_with_replacement
from collections import Counter

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


ALPHABET = ("F", "V", "S")


@dataclass(frozen=True)
class Chamber:
    id: int
    members: tuple[int, int]


def canonical_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def shell_profile(G: nx.Graph, src: int = 0) -> tuple[int, ...]:
    d = nx.single_source_shortest_path_length(G, src)
    c = Counter(d.values())
    return tuple(c[k] for k in range(max(c) + 1))


def triangle_count(G: nx.Graph) -> int:
    return sum(nx.triangles(G).values()) // 3


def graph6_string(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def read_graph6(path: Path) -> nx.Graph:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"No graph6 data found in {path}")
    return nx.from_graph6_bytes(lines[0].encode())


def build_chambers(fm: FlagModel, gen: CoxeterGenerators) -> tuple[list[Chamber], dict[int, int]]:
    seen: set[int] = set()
    chambers: list[Chamber] = []
    owner: dict[int, int] = {}

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        x = fm.get(i)
        sx = gen.S(x)
        j = fm.index(sx)

        pair = canonical_pair(i, j)
        cid = len(chambers)
        chambers.append(Chamber(id=cid, members=pair))

        for k in pair:
            seen.add(k)
            owner[k] = cid

    if len(chambers) != 60:
        raise RuntimeError(f"Expected 60 chambers, got {len(chambers)}")

    return chambers, owner


def chamber_images_for_word(
    chamber: Chamber,
    fm: FlagModel,
    gen: CoxeterGenerators,
    owner: dict[int, int],
    word: str,
) -> set[int]:
    out: set[int] = set()
    for flag_idx in chamber.members:
        x = fm.get(flag_idx)
        y = gen.apply_word(x, word)
        y_idx = fm.index(y)
        out.add(owner[y_idx])
    return out


def words_up_to_length(max_len: int, alphabet: tuple[str, ...] = ALPHABET) -> list[str]:
    out: list[str] = []
    for n in range(1, max_len + 1):
        for tup in product(alphabet, repeat=n):
            out.append("".join(tup))
    return out


def word_profile(
    word: str,
    chambers: list[Chamber],
    fm: FlagModel,
    gen: CoxeterGenerators,
    owner: dict[int, int],
) -> dict:
    sizes = []
    self_hits = 0
    detailed = {}

    for ch in chambers:
        imgs = chamber_images_for_word(ch, fm, gen, owner, word)
        if ch.id in imgs:
            self_hits += 1
        sizes.append(len(imgs))
        detailed[ch.id] = imgs

    hist = Counter(sizes)
    return {
        "word": word,
        "hist": dict(sorted(hist.items())),
        "uniform": len(hist) == 1,
        "size": sizes[0] if len(set(sizes)) == 1 else None,
        "self_hits": self_hits,
        "images": detailed,
    }


def build_graph_from_words(
    words: tuple[str, ...],
    chambers: list[Chamber],
    fm: FlagModel,
    gen: CoxeterGenerators,
    owner: dict[int, int],
) -> tuple[nx.Graph, dict[int, dict[str, set[int]]]]:
    G = nx.Graph()
    G.add_nodes_from(range(len(chambers)))

    local_data: dict[int, dict[str, set[int]]] = {}

    for ch in chambers:
        row = {}
        union = set()

        for w in words:
            imgs = chamber_images_for_word(ch, fm, gen, owner, w)
            imgs.discard(ch.id)
            row[w] = set(imgs)
            union |= imgs

        row["all"] = set(union)
        local_data[ch.id] = row

        for dst in union:
            G.add_edge(ch.id, dst)

    return G, local_data


def summarize_graph(G: nx.Graph) -> dict:
    return {
        "vertices": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "degree_set": sorted(set(dict(G.degree()).values())),
        "connected": nx.is_connected(G),
        "triangles": triangle_count(G),
        "diameter": nx.diameter(G) if nx.is_connected(G) else None,
        "shell_profile": shell_profile(G, 0) if nx.is_connected(G) else None,
        "graph6": graph6_string(G),
    }


def compare_to_targets(G: nx.Graph) -> dict[str, bool]:
    targets = {
        "artifacts/census/thalean_graph.g6": ROOT / "artifacts" / "census" / "thalean_graph.g6",
        "artifacts/census/thalion_graph.g6": ROOT / "artifacts" / "census" / "thalion_graph.g6",
    }

    out = {}
    for label, path in targets.items():
        if path.exists():
            try:
                H = read_graph6(path)
                out[label] = nx.is_isomorphic(G, H)
            except Exception:
                out[label] = False
    return out


def main() -> None:
    print("=" * 80)
    print("SEARCH TRUE CHAMBER BRANCH WORDS")
    print("=" * 80)

    max_len = 3

    fm = FlagModel()
    gen = CoxeterGenerators(fm)
    chambers, owner = build_chambers(fm, gen)

    print("SEARCH PARAMETERS")
    print("-" * 80)
    print("alphabet:", ALPHABET)
    print("max word length:", max_len)
    print("chambers:", len(chambers))
    print()

    words = words_up_to_length(max_len)
    profiles = []

    print("SCANNING SINGLE WORDS")
    print("-" * 80)
    for w in words:
        prof = word_profile(w, chambers, fm, gen, owner)
        profiles.append(prof)
        print(
            f"{w:>3}  hist={prof['hist']}  uniform={prof['uniform']}  "
            f"size={prof['size']}  self_hits={prof['self_hits']}"
        )

    good_branch_words = [
        p["word"]
        for p in profiles
        if p["uniform"] and p["size"] == 2
    ]

    print()
    print("UNIFORMLY 2-BRANCHING WORDS")
    print("-" * 80)
    print(good_branch_words if good_branch_words else "none")
    print()

    print("TESTING WORD PAIRS")
    print("-" * 80)

    pair_results = []

    for w1, w2 in combinations_with_replacement(good_branch_words, 2):
        G, local_data = build_graph_from_words((w1, w2), chambers, fm, gen, owner)
        summary = summarize_graph(G)
        matches = compare_to_targets(G)

        overlap_hist = Counter()
        for cid, row in local_data.items():
            overlap_hist[len(row[w1] & row[w2])] += 1

        rec = {
            "pair": (w1, w2),
            "summary": summary,
            "overlap_hist": dict(sorted(overlap_hist.items())),
            "matches": matches,
        }
        pair_results.append(rec)

        print(f"PAIR {w1}, {w2}")
        print("  vertices:", summary["vertices"])
        print("  edges:", summary["edges"])
        print("  degree set:", summary["degree_set"])
        print("  connected:", summary["connected"])
        print("  triangles:", summary["triangles"])
        print("  diameter:", summary["diameter"])
        print("  shell profile:", summary["shell_profile"])
        print("  overlap hist:", rec["overlap_hist"])
        print("  matches:", matches)
        print()

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "search_true_chamber_branch_words.txt"

    lines = [
        "=" * 80,
        "SEARCH TRUE CHAMBER BRANCH WORDS",
        "=" * 80,
        "",
        "SEARCH PARAMETERS",
        "-" * 80,
        f"alphabet: {ALPHABET}",
        f"max word length: {max_len}",
        f"chambers: {len(chambers)}",
        "",
        "SCANNING SINGLE WORDS",
        "-" * 80,
    ]

    for p in profiles:
        lines.append(
            f"{p['word']:>3}  hist={p['hist']}  uniform={p['uniform']}  "
            f"size={p['size']}  self_hits={p['self_hits']}"
        )

    lines.extend([
        "",
        "UNIFORMLY 2-BRANCHING WORDS",
        "-" * 80,
        str(good_branch_words if good_branch_words else "none"),
        "",
        "TESTING WORD PAIRS",
        "-" * 80,
    ])

    for rec in pair_results:
        pair = rec["pair"]
        summary = rec["summary"]
        lines.extend([
            f"PAIR {pair[0]}, {pair[1]}",
            f"  vertices: {summary['vertices']}",
            f"  edges: {summary['edges']}",
            f"  degree set: {summary['degree_set']}",
            f"  connected: {summary['connected']}",
            f"  triangles: {summary['triangles']}",
            f"  diameter: {summary['diameter']}",
            f"  shell profile: {summary['shell_profile']}",
            f"  graph6: {summary['graph6']}",
            f"  overlap hist: {rec['overlap_hist']}",
            f"  matches: {rec['matches']}",
            "",
        ])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
