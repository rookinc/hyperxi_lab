#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Tuple, List, Set

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel, Flag
from hyperxi.transport.coxeter_generators import CoxeterGenerators


@dataclass(frozen=True)
class Chamber:
    id: int
    members: tuple[int, int]  # flag indices


def shell_profile(G: nx.Graph, src: int = 0) -> tuple[int, ...]:
    d = nx.single_source_shortest_path_length(G, src)
    c = Counter(d.values())
    return tuple(c[k] for k in range(max(c) + 1))


def triangle_count(G: nx.Graph) -> int:
    return sum(nx.triangles(G).values()) // 3


def graph6_string(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def canonical_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def build_chambers(fm: FlagModel, gen: CoxeterGenerators) -> tuple[list[Chamber], dict[int, int]]:
    """
    Chambers are S-orbits on the 120 true flags.
    Returns:
      - list of 60 chambers
      - owner map: flag_index -> chamber_id
    """
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
    """
    Apply a word to both flag representatives of a chamber, then project back down.
    """
    out: set[int] = set()

    for flag_idx in chamber.members:
        x = fm.get(flag_idx)
        y = gen.apply_word(x, word)
        y_idx = fm.index(y)
        out.add(owner[y_idx])

    return out


def build_true_chamber_graph() -> tuple[nx.Graph, list[Chamber], dict[int, int], dict[int, dict[str, set[int]]]]:
    """
    Build the 60-vertex chamber graph from the true flag model using:
      chambers = S-orbits
      branching words = FV and VF
    """
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    chambers, owner = build_chambers(fm, gen)

    G = nx.Graph()
    G.add_nodes_from(range(len(chambers)))

    local_data: dict[int, dict[str, set[int]]] = {}

    for ch in chambers:
        m_minus = chamber_images_for_word(ch, fm, gen, owner, "FV")
        m_plus = chamber_images_for_word(ch, fm, gen, owner, "VF")

        # Remove accidental self-images if any
        m_minus.discard(ch.id)
        m_plus.discard(ch.id)

        local_data[ch.id] = {
            "FV": set(m_minus),
            "VF": set(m_plus),
            "all": set(m_minus) | set(m_plus),
        }

        for dst in local_data[ch.id]["all"]:
            G.add_edge(ch.id, dst)

    return G, chambers, owner, local_data


def print_local_summary(local_data: dict[int, dict[str, set[int]]], limit: int = 20) -> None:
    print("LOCAL CHAMBER BRANCHING")
    print("-" * 80)
    for cid in range(min(limit, len(local_data))):
        row = local_data[cid]
        print(
            f"{cid:2d} -> "
            f"FV={sorted(row['FV'])}  "
            f"VF={sorted(row['VF'])}  "
            f"ALL={sorted(row['all'])}"
        )


def main() -> None:
    print("=" * 80)
    print("BUILD TRUE CHAMBER GRAPH FROM TRUE FLAGS")
    print("=" * 80)

    G, chambers, owner, local_data = build_true_chamber_graph()

    print("GRAPH SUMMARY")
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("triangles:", triangle_count(G))
    print("diameter:", nx.diameter(G))
    print("shell profile from 0:", shell_profile(G, 0))
    print("graph6:", graph6_string(G))
    print()

    overlap_hist = Counter()
    for cid, row in local_data.items():
        overlap_hist[len(row["FV"] & row["VF"])] += 1

    print("LOCAL OVERLAP HISTOGRAM  |FV(c) ∩ VF(c)|")
    print("-" * 80)
    print(dict(sorted(overlap_hist.items())))
    print()

    print_local_summary(local_data, limit=20)

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "build_true_chamber_graph_from_flags.txt"
    g6_path = out_dir / "true_chamber_graph.g6"

    lines = [
        "=" * 80,
        "BUILD TRUE CHAMBER GRAPH FROM TRUE FLAGS",
        "=" * 80,
        "",
        "GRAPH SUMMARY",
        "-" * 80,
        f"vertices: {G.number_of_nodes()}",
        f"edges: {G.number_of_edges()}",
        f"degree set: {sorted(set(dict(G.degree()).values()))}",
        f"connected: {nx.is_connected(G)}",
        f"triangles: {triangle_count(G)}",
        f"diameter: {nx.diameter(G)}",
        f"shell profile from 0: {shell_profile(G, 0)}",
        f"graph6: {graph6_string(G)}",
        "",
        "LOCAL OVERLAP HISTOGRAM  |FV(c) ∩ VF(c)|",
        "-" * 80,
        str(dict(sorted(overlap_hist.items()))),
        "",
        "LOCAL CHAMBER BRANCHING",
        "-" * 80,
    ]

    for cid in range(len(local_data)):
        row = local_data[cid]
        lines.append(
            f"{cid:2d} -> FV={sorted(row['FV'])}  VF={sorted(row['VF'])}  ALL={sorted(row['all'])}"
        )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    g6_path.write_text(graph6_string(G) + "\n", encoding="utf-8")

    print()
    print(f"saved {report_path.relative_to(ROOT)}")
    print(f"saved {g6_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
