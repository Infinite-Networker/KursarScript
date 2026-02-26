![image alt
](https://github.com/Infinite-Networker/KursarScript/blob/c6611414a7cd59c1349bc5061394b42bfd4065f9/My%20Official%20KursarScript%20GitHub%20Repository%20Logo%20for%20its%20ReadMe.png)

# KursarScript
KursarScript is a groundbreaking programming language designed specifically for virtual reality environments and digital economies. Create, manage, and scale virtual marketplaces, avatar interactions, and digital transactions with an intuitive syntax built for VR development.

# KursarScript Programming Language (KSPL)

A virtual reality and digital user-friendly programming language designed for virtual environments and digital economies.

## Overview

KursarScript (KSPL) is a specialized programming language that enables developers to create and manage virtual economies within VR environments. It provides built-in support for digital currencies, virtual assets, and immersive transactions through its innovative Virtu-Card system and Virtual-Terminals.

## Key Features

### 🎮 Virtual Reality Integration
- **Avatar Management**: Create and control avatars in VR environments
- **Virtual Terminals**: Service hubs for buying/selling virtual goods
- **Virtual Portals**: Connect terminals across different VR spaces
- **Immersive Transactions**: Real-time virtual economy operations

### 💳 Virtual Economy System
- **Virtu-Card**: Secure storage and transfer of digital denominations
- **Digital Currencies**: Support for virtual coins and banknotes
- **Transaction Security**: Built-in security levels and history tracking
- **Marketplace Operations**: List, buy, and sell virtual items

### 🏗️ Object-Oriented Design
- **Classes & Objects**: Define virtual entities and their behaviors
- **Methods & Fields**: Encapsulate functionality and state
- **No Inheritance**: Simplified object model for VR environments
- **Avatar Interaction**: Objects can be manipulated by avatars

### 🤖 AI-Inspired Concepts
- **Smart Operations**: Automated currency exchange and transactions
- **Adaptive Behavior**: Objects that respond to environment changes
- **Virtual Intelligence**: Basic AI for NPCs and automated systems

## Installation

### From PyPI (once published)
```bash
pip install kursarscript
```

### From Source (Development)
```bash
# Clone the repository
git clone https://github.com/Infinite-Networker/KursarScript.git
cd KursarScript

# Install in development mode
pip install -e .

# Verify installation
kursarscript --version
```

## Quick Start

### Running a Script
```bash
kursarscript examples/hello_world.kursar
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

## Language Syntax

### Variables
```
let name = "Alice"
let balance = 1000.0
let active = true
let nothing = null
```

### Functions
```
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
```
class Player {
    field health = 100
    field name = ""

    // Multi-line method body
    fn init(player_name) {
        self.name = player_name
    }

    // Single-line (inline) method body
    fn heal(amount) { self.health = self.health + amount }
    fn is_alive() { return self.health > 0 }

    fn describe() {
        print("Player:", self.name, "HP:", self.health)
    }
}

let player = Player("Hero")
player.heal(50)
player.describe()
```

### Control Flow
```
if (balance > 500) {
    print("Rich!")
} else if (balance > 100) {
    print("Okay")
} else {
    print("Need credits")
}
```

### Loops
```
// For loop
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
    if (x == 3) { continue }   // skip x=3
    if (x == 5) { break }      // stop at x=5
    print(x)
}
```

### Multi-line Expressions
```
// Multi-line list
let market_data = [
    {"item": "Sword", "price": 150.0},
    {"item": "Shield", "price": 200.0}
]

// Multi-line arithmetic
let total = 100.0 +
            200.0 +
            300.0
```

### Virtual Economy
```
// Create avatars with VirtuCards
let alice = Avatar("Alice_VR", "explorer")
alice.virtucard = create_virtucard(alice, 1000.0)
alice.virtucard.set_security("high")

// Create marketplace
let shop = VirtualTerminal("Market", "general")
shop.list_item("Health Potion", 25.0, "Restores 50 HP")

// Purchase (3-arg form)
shop.purchase_item(alice, "Health Potion", alice.virtucard)

// Purchase (2-arg shorthand)
shop.purchase("Health Potion", alice.virtucard)

// Transfer funds
let bob = Avatar("Bob_VR", "merchant")
bob.virtucard = create_virtucard(bob, 500.0)
transfer(alice.virtucard, bob.virtucard, 100.0)

// View transaction history
let history = alice.virtucard.get_history()
for txn in history {
    print(txn)
}
```

### Virtual Items with Rarity
```
let sword = VirtualItem("Dragon Sword", "weapon", 1000.0)
sword.set_rarity("legendary")       // 10x value multiplier
sword.set_attribute("damage", 500)

print(sword.calculate_value())      // 10000.0
```

## Built-in Types Reference

### Avatar
| Method / Field | Description |
|---|---|
| `Avatar(name, role)` | Create a new avatar |
| `avatar.name` | Avatar's name |
| `avatar.role` | Avatar's role (explorer, merchant, etc.) |
| `avatar.virtucard` | Attached VirtuCard (set explicitly) |
| `avatar.set_attribute(key, value)` | Set a custom attribute |
| `avatar.get_attribute(key)` | Get a custom attribute |
| `avatar.get_inventory()` | List of owned items |

### VirtuCard
| Method / Field | Description |
|---|---|
| `create_virtucard(avatar, amount)` | Factory function to create a card |
| `card.balance` | Current balance |
| `card.security_level` | Security level string |
| `card.tap_denominator(amount)` | Add bonus credits |
| `card.debit(amount)` | Deduct credits |
| `card.credit(amount)` | Add credits |
| `card.set_security(level)` | Set security: low/medium/high/maximum |
| `card.get_history()` | Get transaction history list |
| `transfer(from_card, to_card, amount)` | Transfer between cards |

### VirtualTerminal
| Method / Field | Description |
|---|---|
| `VirtualTerminal(name, category)` | Create a marketplace |
| `terminal.list_item(name, price, desc)` | List item by name+price |
| `terminal.list_item(virtual_item)` | List a VirtualItem object |
| `terminal.get_inventory()` | Get all listings |
| `terminal.purchase_item(buyer, name, card)` | 3-arg purchase |
| `terminal.purchase(name, card)` | 2-arg purchase shorthand |

### VirtualItem
| Method / Field | Description |
|---|---|
| `VirtualItem(name, type, base_value)` | Create an item |
| `item.set_rarity(level)` | common/uncommon/rare/epic/legendary |
| `item.calculate_value()` | base_value × rarity multiplier |
| `item.set_attribute(key, value)` | Custom attribute |
| `item.get_attribute(key)` | Retrieve attribute |

## Example Scripts

| File | Description |
|---|---|
| `examples/hello_world.kursar` | Language basics: variables, loops, functions, if/else |
| `examples/classes.kursar` | Object-oriented programming with classes |
| `examples/economy.kursar` | Virtual economy with VirtuCards and markets |
| `examples/advanced.kursar` | while loops, break, continue, inline method bodies |
| `examples/test.kursar` | Full comprehensive VR economy demonstration |

## Project Structure
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
├── pyproject.toml             # Package configuration
├── setup.py                   # Legacy setup support
└── README.md                  # This file
```

## Running Tests
```bash
pip install pytest
pytest tests/ -v

# Quick check
pytest tests/ -q
# Expected: 117 passed
```

## License
MIT License - see [LICENSE](LICENSE) for details.
