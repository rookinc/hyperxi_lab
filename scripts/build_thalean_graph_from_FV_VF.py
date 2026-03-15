#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass
from collections import Counter

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


@dataclass(frozen=True)
class Chamber:
    id: int
    members: tuple[int, int]


def canonical_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def triangle_count(G: nx.Graph) -> int:
    return sum(nx.triangles(G).values()) // 3


def shell_profile(G: nx.Graph, src: int = 0) -> tuple[int, ...] | None:
    if not nx.is_connected(G):
        return None
    d = nx.single_source_shortest_path_length(G, src)
    c = Counter(d.values())
    return tuple(c[k] for k in range(max(c) + 1))


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


def chamber_image_set(
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


def build_thalean_graph() -> tuple[nx.Graph, dict[int, dict[str, set[int]]]]:
    """
    Candidate rigorous Thalean graph:
      - vertices = S-orbit chambers
      - edges come from the chamber images of FV and VF
    """
    fm = FlagModel()
    gen = CoxeterGenerators(fm)
    chambers, owner = build_chambers(fm, gen)

    G = nx.Graph()
    G.add_nodes_from(range(len(chambers)))

    local: dict[int, dict[str, set[int]]] = {}

    for ch in chambers:
        fv = chamber_image_set(ch, fm, gen, owner, "FV")
        vf = chamber_image_set(ch, fm, gen, owner, "VF")

        fv.discard(ch.id)
        vf.discard(ch.id)

        all_nbrs = set(fv) | set(vf)

        local[ch.id] = {
            "FV": set(fv),
            "VF": set(vf),
            "ALL": set(all_nbrs),
        }

        for dst in all_nbrs:
            G.add_edge(ch.id, dst)

    return G, local


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
    print("BUILD THALEAN GRAPH FROM FV AND VF")
    print("=" * 80)

    G, local = build_thalean_graph()

    print("GRAPH SUMMARY")
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("triangles:", triangle_count(G))
    print("diameter:", nx.diameter(G) if nx.is_connected(G) else None)
    print("shell profile from 0:", shell_profile(G, 0))
    print("graph6:", graph6_string(G))
    print()

    fv_hist = Counter(len(local[c]["FV"]) for c in local)
    vf_hist = Counter(len(local[c]["VF"]) for c in local)
    all_hist = Counter(len(local[c]["ALL"]) for c in local)
    overlap_hist = Counter(len(local[c]["FV"] & local[c]["VF"]) for c in local)

    print("LOCAL IMAGE HISTOGRAMS")
    print("-" * 80)
    print("|FV(c)| :", dict(sorted(fv_hist.items())))
    print("|VF(c)| :", dict(sorted(vf_hist.items())))
    print("|ALL(c)|:", dict(sorted(all_hist.items())))
    print("|FV(c) ∩ VF(c)|:", dict(sorted(overlap_hist.items())))
    print()

    print("FIRST 20 LOCAL ROWS")
    print("-" * 80)
    for cid in range(min(20, len(local))):
        row = local[cid]
        print(f"{cid:2d} -> FV={sorted(row['FV'])}  VF={sorted(row['VF'])}  ALL={sorted(row['ALL'])}")
    print()

    matches = compare_to_targets(G)
    print("TARGET COMPARISON")
    print("-" * 80)
    print(matches)

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "build_thalean_graph_from_FV_VF.txt"
    g6_path = out_dir / "build_thalean_graph_from_FV_VF.g6"

    lines = [
        "=" * 80,
        "BUILD THALEAN GRAPH FROM FV AND VF",
        "=" * 80,
        "",
        "GRAPH SUMMARY",
        "-" * 80,
        f"vertices: {G.number_of_nodes()}",
        f"edges: {G.number_of_edges()}",
        f"degree set: {sorted(set(dict(G.degree()).values()))}",
        f"connected: {nx.is_connected(G)}",
        f"triangles: {triangle_count(G)}",
        f"diameter: {nx.diameter(G) if nx.is_connected(G) else None}",
        f"shell profile from 0: {shell_profile(G, 0)}",
        f"graph6: {graph6_string(G)}",
        "",
        "LOCAL IMAGE HISTOGRAMS",
        "-" * 80,
        f"|FV(c)| : {dict(sorted(fv_hist.items()))}",
        f"|VF(c)| : {dict(sorted(vf_hist.items()))}",
        f"|ALL(c)|: {dict(sorted(all_hist.items()))}",
        f"|FV(c) ∩ VF(c)|: {dict(sorted(overlap_hist.items()))}",
        "",
        "FIRST 20 LOCAL ROWS",
        "-" * 80,
    ]

    for cid in range(min(20, len(local))):
        row = local[cid]
        lines.append(f"{cid:2d} -> FV={sorted(row['FV'])}  VF={sorted(row['VF'])}  ALL={sorted(row['ALL'])}")

    lines.extend([
        "",
        "TARGET COMPARISON",
        "-" * 80,
        str(matches),
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    g6_path.write_text(graph6_string(G) + "\n", encoding="utf-8")

    print()
    print(f"saved {report_path.relative_to(ROOT)}")
    print(f"saved {g6_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
