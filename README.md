<div align="center">

<!-- Banner Logo -->
![KursarScript Banner](https://github.com/Infinite-Networker/KursarScript/blob/c6611414a7cd59c1349bc5061394b42bfd4065f9/My%20Official%20KursarScript%20GitHub%20Repository%20Logo%20for%20its%20ReadMe.png)

<br/>

<!-- Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-e8003d?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-00f5ff?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-117%20Passing-39ff14?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Status](https://img.shields.io/badge/Status-Active-bf00ff?style=for-the-badge&logo=statuspage&logoColor=white)](#)
[![Made by](https://img.shields.io/badge/Made%20by-Cherry%20Computer%20Ltd.-e8003d?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PC9zdmc+&logoColor=white)](#-cherry-computer-ltd)

<br/>

# ⬡ KursarScript
### `KSPL — Virtual Reality Programming Language`

> **A groundbreaking programming language designed for virtual reality environments and digital economies.**  
> Create, manage, and scale virtual marketplaces, avatar interactions, and immersive transactions  
> with an intuitive syntax built for the metaverse.

<br/>

[⚡ Get Started](#-installation) · [{ } Syntax Guide](#-language-syntax) · [🌐 VR API](#-built-in-types-reference) · [🗺️ Roadmap](#️-roadmap) · [★ GitHub](https://github.com/Infinite-Networker/KursarScript)

<br/>

---

</div>

## 🌐 Overview

**KursarScript (KSPL)** is a specialized programming language that enables developers to create and manage virtual economies within VR environments. It provides built-in support for **digital currencies**, **virtual assets**, and **immersive transactions** through its innovative **Virtu-Card system** and **Virtual-Terminals**.

Designed from the ground up by **Cherry Computer Ltd.**, KursarScript gives VR developers first-class language primitives that no mainstream language provides — meaning less boilerplate, more immersion.

<br/>

---

## ✨ Key Features

<table>
<tr>
<td width="50%" valign="top">

### 🎮 Virtual Reality Integration
- **Avatar Management** — Create and control avatars in VR environments
- **Virtual Terminals** — Service hubs for buying/selling virtual goods
- **Virtual Portals** — Connect terminals across different VR spaces
- **Immersive Transactions** — Real-time virtual economy operations

### 🏗️ Object-Oriented Design
- **Classes & Objects** — Define virtual entities and their behaviours
- **Methods & Fields** — Encapsulate functionality and state
- **No Inheritance** — Simplified flat object model for VR environments
- **Inline Method Bodies** — Single-line and multi-line method syntax

</td>
<td width="50%" valign="top">

### 💳 Virtual Economy System
- **Virtu-Card** — Secure storage and transfer of digital denominations
- **Digital Currencies** — Support for virtual coins and banknotes
- **Transaction Security** — Built-in security levels and history tracking
- **Marketplace Operations** — List, buy, and sell virtual items

### 🤖 AI-Inspired Concepts
- **Smart Operations** — Automated currency exchange and transactions
- **Adaptive Behaviour** — Objects that respond to environment changes
- **Virtual Intelligence** — Basic AI for NPCs and automated systems

</td>
</tr>
</table>

<br/>

---

## 🚀 Installation

### From PyPI *(once published)*
```bash
pip install kursarscript
```

### From Source *(Development)*
```bash
# Clone the repository
git clone https://github.com/Infinite-Networker/KursarScript.git
cd KursarScript

# Install in development mode
pip install -e .

# Verify installation
kursarscript --version
```

<br/>

---

## ⚡ Quick Start

### Running a Script
```bash
kursarscript examples/hello_world.kursar
kursarscript examples/economy.kursar
kursarscript examples/test.kursar
```

### Interactive REPL
```bash
kursarscript -i
# or
kursarscript --interactive
```

### Python Module
```bash
python -m kursarscript script.kursar
```

<br/>

---

## 📖 Language Syntax

### Variables
```js
let name    = "Alice"
let balance = 1000.0
let active  = true
let nothing = null
```

### Functions
```js
fn greet(person) {
    print("Hello,", person)
}

fn add(a, b) {
    return a + b
}

greet("World")
let result = add(3, 7)
```

### Classes
```js
class Player {
    field health = 100
    field name   = ""

    fn init(player_name) {
        self.name = player_name
    }

    // Inline method bodies
    fn heal(amount)   { self.health = self.health + amount }
    fn is_alive()     { return self.health > 0 }

    fn describe() {
        print("Player:", self.name, "HP:", self.health)
    }
}

let player = Player("Hero")
player.heal(50)
player.describe()
```

### Control Flow
```js
if (balance > 500) {
    print("Rich!")
} else if (balance > 100) {
    print("Okay")
} else {
    print("Need credits")
}
```

### Loops
```js
// For loop over a list
let items = ["Sword", "Shield", "Potion"]
for item in items {
    print("-", item)
}

// For with range
for i in range(1, 6) {
    print(i)
}

// While loop
let count = 0
while (count < 5) {
    count = count + 1
}

// Break and Continue
for x in [1, 2, 3, 4, 5] {
    if (x == 3) { continue }   // skip x = 3
    if (x == 5) { break }      // stop at x = 5
    print(x)
}
```

### Multi-line Expressions
```js
// Multi-line list
let market_data = [
    {"item": "Sword",  "price": 150.0},
    {"item": "Shield", "price": 200.0}
]

// Multi-line arithmetic
let total = 100.0 +
            200.0 +
            300.0
```

<br/>

---

## 🌐 Virtual Economy

```js
// ── Create avatars with VirtuCards ──────────────────────────────────────────
let alice = Avatar("Alice_VR", "explorer")
alice.virtucard = create_virtucard(alice, 1000.0)
alice.virtucard.set_security("high")

// ── Build a virtual marketplace ─────────────────────────────────────────────
let shop = VirtualTerminal("NexusMarket", "general")
shop.list_item("Health Potion", 25.0, "Restores 50 HP")

// ── Purchase (2-arg shorthand) ───────────────────────────────────────────────
shop.purchase("Health Potion", alice.virtucard)

// ── Purchase (3-arg form) ────────────────────────────────────────────────────
shop.purchase_item(alice, "Health Potion", alice.virtucard)

// ── Transfer funds between avatars ──────────────────────────────────────────
let bob = Avatar("Bob_VR", "merchant")
bob.virtucard = create_virtucard(bob, 500.0)
transfer(alice.virtucard, bob.virtucard, 100.0)

// ── View transaction history ─────────────────────────────────────────────────
let history = alice.virtucard.get_history()
for txn in history {
    print(txn)
}
```

### Virtual Items with Rarity
```js
let sword = VirtualItem("Dragon Sword", "weapon", 1000.0)
sword.set_rarity("legendary")       // 10× value multiplier
sword.set_attribute("damage", 500)

print(sword.calculate_value())      // → 10000.0
```

<br/>

---

## 🌐 Built-in Types Reference

### `Avatar`
| Method / Field | Description |
|---|---|
| `Avatar(name, role)` | Create a new avatar |
| `avatar.name` | Avatar's display name |
| `avatar.role` | Avatar's role (`explorer`, `merchant`, …) |
| `avatar.virtucard` | Attached VirtuCard (set explicitly) |
| `avatar.set_attribute(key, value)` | Set a custom attribute |
| `avatar.get_attribute(key)` | Get a custom attribute |
| `avatar.get_inventory()` | List of owned items |

### `VirtuCard`
| Method / Field | Description |
|---|---|
| `create_virtucard(avatar, amount)` | Factory — create a card |
| `card.balance` | Current balance |
| `card.security_level` | Security level string |
| `card.tap_denominator(amount)` | Add bonus credits |
| `card.debit(amount)` | Deduct credits |
| `card.credit(amount)` | Add credits |
| `card.set_security(level)` | `low` / `medium` / `high` / `maximum` |
| `card.get_history()` | Get transaction history list |
| `transfer(from_card, to_card, amount)` | Transfer between cards |

### `VirtualTerminal`
| Method / Field | Description |
|---|---|
| `VirtualTerminal(name, category)` | Create a marketplace |
| `terminal.list_item(name, price, desc)` | List item by name + price |
| `terminal.list_item(virtual_item)` | List a `VirtualItem` object |
| `terminal.get_inventory()` | Get all listings |
| `terminal.purchase_item(buyer, name, card)` | 3-arg purchase |
| `terminal.purchase(name, card)` | 2-arg shorthand |

### `VirtualItem`
| Method / Field | Description |
|---|---|
| `VirtualItem(name, type, base_value)` | Create an item |
| `item.set_rarity(level)` | `common` · `uncommon` · `rare` · `epic` · `legendary` |
| `item.calculate_value()` | `base_value × rarity multiplier` |
| `item.set_attribute(key, value)` | Custom attribute |
| `item.get_attribute(key)` | Retrieve attribute |

<br/>

---

## 📂 Example Scripts

| File | Description |
|---|---|
| `examples/hello_world.kursar` | Language basics: variables, loops, functions, if/else |
| `examples/classes.kursar` | Object-oriented programming with classes |
| `examples/economy.kursar` | Virtual economy with VirtuCards and markets |
| `examples/advanced.kursar` | `while` loops, `break`, `continue`, inline method bodies |
| `examples/test.kursar` | Full comprehensive VR economy demonstration |

<br/>

---

## 🗂️ Project Structure

```
KursarScript/
├── kursarscript/              # Main Python package
│   ├── __init__.py            # Package entry point & exports
│   ├── __main__.py            # python -m kursarscript support
│   ├── interpreter.py         # KSPL interpreter (parser + executor)
│   ├── compiler.py            # KSPL compiler (tokenizer + code gen)
│   ├── runtime.py             # Built-in VR types (Avatar, VirtuCard, etc.)
│   └── cli.py                 # Command-line interface & REPL
├── examples/
│   ├── hello_world.kursar     # Beginner example
│   ├── classes.kursar         # OOP example
│   ├── economy.kursar         # Economy system example
│   ├── advanced.kursar        # while, break, continue, inline methods
│   └── test.kursar            # Comprehensive demo script
├── tests/
│   └── test_kursarscript.py   # 117 automated tests
├── src/                       # Original source files (reference)
├── docs/
│   └── ROADMAP.md             # Development roadmap
├── index.html                 # Showcase website
├── pyproject.toml             # Package configuration
├── setup.py                   # Legacy setup support
└── README.md                  # This file
```

<br/>

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v

# Quick summary
pytest tests/ -q
# Expected: 117 passed
```

<br/>

---

## 🗺️ Roadmap

| Status | Milestone |
|---|---|
| ✅ **Shipped** | Core language interpreter — variables, functions, classes, loops, control flow |
| ✅ **Shipped** | VR economy primitives — `Avatar`, `VirtuCard`, `VirtualTerminal`, `VirtualItem` |
| ✅ **Shipped** | CLI & Interactive REPL |
| ✅ **Shipped** | 117 automated tests |
| ⚡ **In Progress** | PyPI publication |
| 🔜 **Planned** | Extended standard library (networking, physics hooks, NPC modules) |
| 🔜 **Planned** | VS Code extension — syntax highlighting, IntelliSense, debugger |

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full development roadmap.

<br/>

---

## 📄 License

```
MIT License — © 2024–2025 Cherry Computer Ltd.
```

See [LICENSE](LICENSE) for the full license text. KursarScript is free for personal,
commercial, and research use.

<br/>

---

<div align="center">

## 🍒 Cherry Computer Ltd.

> *"Innovating Tomorrow's Virtual World"*

**KursarScript** is a product of **Cherry Computer Ltd.** — a forward-thinking technology  
company dedicated to building the tools and languages that power the next generation  
of virtual reality and digital economy platforms.

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-Infinite--Networker-e8003d?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Infinite-Networker)
[![Repo](https://img.shields.io/badge/Repo-KursarScript-00f5ff?style=for-the-badge&logo=git&logoColor=white)](https://github.com/Infinite-Networker/KursarScript)

<br/>

*Built with ❤️ by Cherry Computer Ltd.*

</div>
