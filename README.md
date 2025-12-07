# 🃏 Pocket Bower: Euchre AI Solvers

**Pocket Bower** is a modular Python framework for building, training, and analyzing AI agents for [**Euchre**](https://en.wikipedia.org/wiki/Euchre).

Designed as a companion to the educational AI Poker-Bot [pocket-pluribus](https://github.com/roguetrainer/pocket-pluribus), this repository focuses on the challenges of **Cooperative Imperfect Information Games**.

---
![Euchre](../img/euchre.png)
---

## 📖 About the Name

If you weren't raised in Ontario, Canada (or other Euchre strongholds like Michigan or Wisconsin), and didn't grow up playing Euchre at the cottage or during lunch breaks, you might be unfamiliar with the concept of the **"bower"**.

### What is a Bower?

In Euchre, the **bower** refers to the Jack of the trump suit—the most powerful card in the game. But there's a twist:

- **Right Bower**: The Jack of the trump suit (e.g., J♠ if Spades are trump)
- **Left Bower**: The Jack of the *same color* as trump (e.g., J♣ if Spades are trump)

The Left Bower **becomes** a trump card, even though it's a different suit. This creates fascinating strategic depth: a seemingly worthless Jack of Clubs transforms into the second-highest trump when Spades are called. Understanding bower logic is essential to playing Euchre well—and teaching an AI to handle it is one of this project's core challenges.

### Why "Pocket"?

The "pocket" prefix serves two purposes:

1. **Sister Project**: This is a companion repository to [pocket-pluribus](https://github.com/roguetrainer/pocket-pluribus), which implements AI for multi-player Poker. Both projects explore imperfect information games, but Euchre adds the unique challenge of *cooperative* team play.

2. **Educational Scale**: This is an **educational** implementation, not a production-grade AI system. Think of it as a "pocket-sized" version of state-of-the-art game AI—compact enough to understand, modify, and learn from, while still demonstrating the core algorithms (CFR, MCTS) used in cutting-edge systems.

**How close are we to state-of-the-art?** While we haven't benchmarked against world-class Euchre bots (or human experts), our implementation includes the same fundamental techniques used in competitive AI:
- **CFR** for bidding strategy (the algorithm behind superhuman Poker AI like Libratus and Pluribus)
- **MCTS** for card play (the backbone of AlphaGo and other game-playing AI)
- **Heuristic evaluation** based on decades of Euchre strategy

A fully state-of-the-art system would require deeper abstractions, massive self-play training (thousands of CPU-hours), and extensive hyperparameter tuning. Our system trains in *minutes* and demonstrates core concepts—making it ideal for learning, experimentation, and building intuition about AI for imperfect information games.

### On National Character and Card Games

The [geopolitical games adage](https://github.com/roguetrainer/pocket-pluribus/blob/main/docs/geopolitical-games-adage.md) suggests that nations reveal their strategic character through their favored games: China through Go (territorial patience), Russia through Chess (tactical brutality), America through Poker (bluffing under uncertainty).

**So what does Euchre say about Canada?**

Euchre is fundamentally a **cooperative partnership game**—you succeed or fail *with* your partner, not against them. There's no individual victory. This speaks to a certain Canadian sensibility: collective achievement over individual glory, implicit coordination without explicit communication, and trusting your partner to do their part.

But here's the twist: your partner sits *across* from you, not beside you. You can't see their cards. You have to **infer** their strategy from the cards they play, signal your own intentions through legal moves, and hope they're paying attention. It's cooperation through polite implication—the most Canadian thing imaginable.

Consider the key strategic elements:

- **Positional awareness**: Your value depends entirely on where you sit relative to the dealer. Sometimes you have power, sometimes you don't. Accept it gracefully.
- **"Stick the dealer" rule**: If everyone passes, the dealer is *forced* to call trump. The group pressures the person with positional obligation to make a decision, even if it's risky. Very parliamentary.
- **Going alone**: You *can* tell your partner to sit out and try to win all five tricks yourself for bonus points... but it's rare, slightly scandalous, and usually ends badly. Ambition is allowed, but hubris is punished.
- **Modest stakes**: Games are to 10 points. Hands are quick. Nobody's betting the farm. It's cottage entertainment, not Vegas showmanship.

If Poker is American capitalism (leverage your stack, bluff aggressively, winner-take-all), and Go is Chinese strategy (patient encirclement, long-term positioning), then **Euchre is Canadian governance**: coalition-building, reading the room, making the best of your position, and politely forcing someone to make a decision when consensus fails.

Also, there are *bowers*—cards that secretly change identity based on context. The Jack of Clubs isn't *always* a Club. Sometimes it's a Spade. Identity is fluid! Multiculturalism! Bilingualism! (Okay, we're reaching here.)

**Alternative theory**: Canadians just liked a game you could play quickly at the cottage while the fish weren't biting, and we're reading way too much into it. But where's the fun in that?

---

## 🚀 Features

* **Robust Game Engine:** Pure Python implementation of Euchre rules (Bower logic, Ordering Up, Stick the Dealer).
* **Agent Zoo:** Random, Rule-Based (Heuristic), MCTS (Information Set), and CFR (Nash Equilibrium for Bidding).
* **Educational Notebooks:** Visualizations of state and AI decision making.

📚 **For a deep dive into the AI methods, comparisons with Chess/Go/Poker AI, and MCTS applications beyond games, see [OVERVIEW.md](OVERVIEW.md)**

## 📦 Installation

```bash
pip install -e .
```

## ⚡ Quickstart

Check notebooks/01_game_walkthrough.ipynb to see the engine in action.
