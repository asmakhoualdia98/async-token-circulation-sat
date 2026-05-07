# Analyzing Self-Stabilization of Dijkstra’s Asynchronous Token Circulation via SAT

## 🧩 Overview

This project is a Python-based SAT encoding framework for modeling and analyzing the self-stabilization properties of **Dijkstra’s asynchronous token circulation**, with a primary focus on **Dijkstra’s K-state algorithm**.

The framework generates benchmark instances in CNF format for formal verification and experimental evaluation using SAT solvers. It supports the symbolic encoding of convergence and divergence behaviors under multiple execution assumptions, including distributed unfair, synchronous, non-synchronous, and non-sequential daemons.

---

## 🚀 Features

- ✅ Daemon assumptions: `DIS-UNFAIR`, `SYNC`, `NON-SYNC`, `NON-SEQ`
- 🔁 Behavior simulation: `CONV` (converging) and `DIV` (diverging)
- ⚙️ Model options: `INI` (Initial model), `OE` (Offset-Elimination)
- 🛠 Generates CNF files encoding K-state algorithm behavioral properties


---


## 📦 Installation & Usage (Generate a Single CNF Instance)

```bash
git clone <repository-url>
pip install python-sat[pblib,aiger]
python3 GraphSolver.py ring <num_nodes> <modulus> <CONV|DIV> <model> <daemon>
```
---

## 📚 References

📄 Asma Khoualdia, Sami Cherif, Stéphane Devismes, Léo Robert. On the Self-Stabilization of Dijkstra's Asynchronous Token Circulation. International Conference on Principles and Practice of Constraint Programming (CP 2026), July 2026, Lisbon, Portugal.

📄 Asma Khoualdia, Sami Cherif, Stéphane Devismes, Léo Robert. Sur l’autostabilisation de la circulation de jeton asynchrone de Dijkstra. Journées Francophones de Programmation par Contraintes (JFPC 2026), May 2026, Louvain-la-Neuve, Belgium. https://sites.uclouvain.be/jfpc26/articles/JFPC_2026_paper_2.pdf

- - - - - - - - - - - - - - - - - - - - - - - -

You can refer to our previous work on synchronous unison, which provides both source code and benchmark instances:

📄 Asma Khoualdia, Sami Cherif, Stéphane Devismes, Léo Robert. Analyzing Self-Stabilization of Synchronous Unison via Propositional Satisfiability. International Conference on Principles and Practice of Constraint Programming (CP 2025), Glasgow, Scotland. [DOI: https://doi.org/10.4230/LIPIcs.CP.2025.19/](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2025.19)
