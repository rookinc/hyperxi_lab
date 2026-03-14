from __future__ import annotations

import networkx as nx
import numpy as np


def chamber_adjacency_matrix(G: nx.Graph) -> tuple[list[int], np.ndarray]:
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    return nodes, A


def chamber_laplacian_matrix(G: nx.Graph) -> tuple[list[int], np.ndarray]:
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    deg = np.sum(A, axis=1)
    L = np.diag(deg) - A
    return nodes, L


def diagonal_occupancy(weights: np.ndarray) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    return np.diag(w)


def sqrt_diagonal_occupancy(weights: np.ndarray) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    return np.diag(np.sqrt(np.clip(w, 0.0, None)))


def weighted_adjacency(A: np.ndarray, weights: np.ndarray) -> np.ndarray:
    S = sqrt_diagonal_occupancy(weights)
    return S @ A @ S


def shifted_operator(A: np.ndarray, weights: np.ndarray, mu: float = 1.0) -> np.ndarray:
    return A + mu * diagonal_occupancy(weights)


def shifted_laplacian(L: np.ndarray, weights: np.ndarray, mu: float = 1.0) -> np.ndarray:
    return L + mu * diagonal_occupancy(weights)


def mode_density(vec: np.ndarray) -> np.ndarray:
    v = np.asarray(vec, dtype=float)
    return v * v


def signed_mode_density(vec: np.ndarray) -> np.ndarray:
    v = np.asarray(vec, dtype=float)
    return np.sign(v) * (v * v)


def normalize_weights_sum1(weights: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    total = float(np.sum(w))
    if total <= eps:
        return np.ones_like(w) / max(1, len(w))
    return w / total


def normalize_weights_max1(weights: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    m = float(np.max(np.abs(w)))
    if m <= eps:
        return np.zeros_like(w)
    return w / m


def occupancy_from_mass_ratio(mass_ratio: float) -> float:
    return float(mass_ratio) ** 4


def eig_sorted(M: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigvals, eigvecs = np.linalg.eigh(M)
    order = np.argsort(eigvals)[::-1]
    return eigvals[order], eigvecs[:, order]
