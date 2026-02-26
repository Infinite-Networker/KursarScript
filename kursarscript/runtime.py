"""
KursarScript Runtime - Core built-in types and functions
VirtuCard, VirtualTerminal, Avatar, VirtualItem
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


# ---------------------------------------------------------------------------
# VirtuCard – digital wallet for avatars
# ---------------------------------------------------------------------------

class VirtuCard:
    """
    Secure digital wallet that stores and transfers virtual currency.
    Supports denominations, security levels, and full transaction history.
    """
    SECURITY_LEVELS = ("low", "medium", "high", "maximum")

    def __init__(self, owner: 'Avatar', initial_balance: float = 0.0):
        self.owner = owner
        self.balance = float(initial_balance)
        self.security_level = "medium"
        self._transaction_history: List[Dict] = []
        self._card_id = f"VC-{id(self):X}"

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def tap_denominator(self, amount: float) -> bool:
        """Add a denomination (bonus / reward) to the card balance."""
        if amount <= 0:
            print(f"[VirtuCard] tap_denominator requires a positive amount.")
            return False
        self.balance += amount
        self._record("tap", amount, f"Denomination tapped: +{amount}")
        print(f"[VirtuCard] {self.owner.name}: +{amount} credits  (new balance: {self.balance})")
        return True

    def debit(self, amount: float, description: str = "") -> bool:
        """Deduct amount from balance. Returns True on success."""
        if amount <= 0:
            return False
        if self.balance < amount:
            print(f"[VirtuCard] Insufficient funds for {self.owner.name}. "
                  f"Need {amount}, have {self.balance}.")
            return False
        self.balance -= amount
        self._record("debit", amount, description or f"Debit: -{amount}")
        return True

    def credit(self, amount: float, description: str = "") -> bool:
        """Add amount to balance."""
        if amount <= 0:
            return False
        self.balance += amount
        self._record("credit", amount, description or f"Credit: +{amount}")
        return True

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    def set_security_level(self, level: str) -> None:
        level = level.lower()
        if level not in self.SECURITY_LEVELS:
            print(f"[VirtuCard] Unknown security level '{level}'. "
                  f"Valid: {self.SECURITY_LEVELS}")
            return
        self.security_level = level
        print(f"[VirtuCard] {self.owner.name}'s card security set to '{level}'.")

    # Convenience alias used in .kursar scripts
    def set_security(self, level: str) -> None:
        """Alias for set_security_level."""
        return self.set_security_level(level)

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_transaction_history(self) -> List[Dict]:
        """Return a copy of the transaction history list."""
        return list(self._transaction_history)

    # Convenience alias used in .kursar scripts
    def get_history(self) -> List[Dict]:
        """Alias for get_transaction_history."""
        return self.get_transaction_history()

    def _record(self, tx_type: str, amount: float, description: str) -> None:
        self._transaction_history.append({
            "type": tx_type,
            "amount": amount,
            "description": description,
            "balance_after": self.balance,
            "timestamp": datetime.now().isoformat(),
        })

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (f"VirtuCard(owner={self.owner.name!r}, "
                f"balance={self.balance}, security={self.security_level!r})")

    def __str__(self) -> str:
        return repr(self)


# ---------------------------------------------------------------------------
# Helper function – create_virtucard
# ---------------------------------------------------------------------------

def create_virtucard(owner: 'Avatar', initial_balance: float = 0.0) -> VirtuCard:
    """Factory function: create a new VirtuCard for an avatar."""
    card = VirtuCard(owner, initial_balance)
    print(f"[VirtuCard] Created for {owner.name} with balance {initial_balance}.")
    return card


# ---------------------------------------------------------------------------
# Helper function – transfer
# ---------------------------------------------------------------------------

def transfer(sender_card: VirtuCard, receiver_card: VirtuCard, amount: float) -> bool:
    """
    Transfer `amount` from sender's VirtuCard to receiver's VirtuCard.
    Returns True on success, False on failure.
    """
    if amount <= 0:
        print("[Transfer] Amount must be positive.")
        return False

    sender_name = sender_card.owner.name
    receiver_name = receiver_card.owner.name

    if sender_card.balance < amount:
        print(f"[Transfer] FAILED – {sender_name} has insufficient funds "
              f"({sender_card.balance} < {amount}).")
        return False

    sender_card.debit(amount, f"Transfer to {receiver_name}: -{amount}")
    receiver_card.credit(amount, f"Transfer from {sender_name}: +{amount}")
    print(f"[Transfer] {sender_name} → {receiver_name}: {amount} credits  ✓")
    return True


# ---------------------------------------------------------------------------
# Avatar – participant in the VR world
# ---------------------------------------------------------------------------

class Avatar:
    """
    Represents a VR participant. Holds attributes, inventory, and a VirtuCard.
    """

    def __init__(self, name: str, role: str = "user"):
        self.name = name
        self.role = role
        self.virtucard: Optional[VirtuCard] = None
        self._attributes: Dict[str, Any] = {}
        self._inventory: List['VirtualItem'] = []

    # ------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------

    def set_attribute(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)

    # ------------------------------------------------------------------
    # Inventory helpers
    # ------------------------------------------------------------------

    def add_item(self, item: 'VirtualItem') -> None:
        self._inventory.append(item)
        print(f"[Avatar] {self.name} received: {item.name}")

    def get_inventory(self) -> List['VirtualItem']:
        return list(self._inventory)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Avatar(name={self.name!r}, role={self.role!r})"

    def __str__(self) -> str:
        return repr(self)


# ---------------------------------------------------------------------------
# VirtualItem – tradeable item in the VR economy
# ---------------------------------------------------------------------------

RARITY_MULTIPLIERS: Dict[str, float] = {
    "common":    1.0,
    "uncommon":  1.5,
    "rare":      2.5,
    "epic":      5.0,
    "legendary": 10.0,
}


class VirtualItem:
    """
    A tradeable virtual item with rarity, attributes, and value calculation.
    """

    def __init__(self, name: str, item_type: str = "misc", base_value: float = 0.0):
        self.name = name
        self.item_type = item_type
        self.base_value = float(base_value)
        self.rarity = "common"
        self.owner: Optional[Avatar] = None
        self._attributes: Dict[str, Any] = {}

    def set_rarity(self, rarity: str) -> None:
        rarity = rarity.lower()
        if rarity not in RARITY_MULTIPLIERS:
            print(f"[VirtualItem] Unknown rarity '{rarity}'. "
                  f"Valid: {list(RARITY_MULTIPLIERS)}")
            return
        self.rarity = rarity

    def set_attribute(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)

    def calculate_value(self) -> float:
        """Return current market value based on rarity multiplier."""
        multiplier = RARITY_MULTIPLIERS.get(self.rarity, 1.0)
        return round(self.base_value * multiplier, 2)

    def __repr__(self) -> str:
        return (f"VirtualItem(name={self.name!r}, type={self.item_type!r}, "
                f"rarity={self.rarity!r}, value={self.calculate_value()})")

    def __str__(self) -> str:
        return repr(self)


# ---------------------------------------------------------------------------
# VirtualTerminal – marketplace hub
# ---------------------------------------------------------------------------

class VirtualTerminal:
    """
    A virtual marketplace where items can be listed, browsed, and purchased.
    """

    def __init__(self, name: str, category: str = "general"):
        self.name = name
        self.category = category
        self._inventory: List[Dict] = []   # list of {item, price, description}

    # ------------------------------------------------------------------
    # Inventory management
    # ------------------------------------------------------------------

    def list_item(self, item_name_or_obj, price: float = 0.0, description: str = "") -> None:
        """Add a new item listing to the terminal.

        Accepts either:
          list_item("Sword", 150.0, "desc")   – name + price
          list_item(virtual_item_obj)          – VirtualItem object (price from base_value)
        """
        if isinstance(item_name_or_obj, VirtualItem):
            item_obj = item_name_or_obj
            item_name = item_obj.name
            price = price if price > 0 else item_obj.base_value
            description = description or item_obj.item_type
        else:
            item_name = str(item_name_or_obj)

        listing = {
            "item": item_name,
            "price": float(price),
            "description": description,
        }
        self._inventory.append(listing)
        print(f"[Terminal:{self.name}] Listed '{item_name}' for {price} credits.")

    def get_inventory(self) -> List[Dict]:
        """Return current inventory listings."""
        return list(self._inventory)

    def get_listing(self, item_name: str) -> Optional[Dict]:
        """Find listing by name (case-insensitive)."""
        item_name_lower = item_name.lower()
        for listing in self._inventory:
            if listing["item"].lower() == item_name_lower:
                return listing
        return None

    # ------------------------------------------------------------------
    # Purchasing
    # ------------------------------------------------------------------

    def purchase_item(self, buyer: Avatar, item_name: str,
                      payment_card: VirtuCard) -> bool:
        """
        Process a purchase. Deducts price from buyer's VirtuCard.
        Returns True on success.
        """
        listing = self.get_listing(item_name)
        if not listing:
            print(f"[Terminal:{self.name}] '{item_name}' not found in inventory.")
            return False

        price = listing["price"]
        if payment_card.debit(price, f"Purchase: {item_name} from {self.name}"):
            # Create item and give to buyer
            virtual_item = VirtualItem(item_name, "purchased", price)
            virtual_item.owner = buyer
            buyer.add_item(virtual_item)
            # Remove from inventory
            self._inventory.remove(listing)
            print(f"[Terminal:{self.name}] {buyer.name} purchased '{item_name}' "
                  f"for {price} credits  ✓")
            return True
        else:
            print(f"[Terminal:{self.name}] Purchase FAILED for '{item_name}' "
                  f"– {buyer.name} has insufficient funds.")
            return False

    def purchase(self, item_name: str, payment_card: VirtuCard) -> bool:
        """
        Convenience 2-argument alias for purchase_item when buyer is inferred
        from the payment card's owner.

        Usage:  terminal.purchase("Sword", my_card)
        """
        buyer = payment_card.owner
        return self.purchase_item(buyer, item_name, payment_card)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (f"VirtualTerminal(name={self.name!r}, "
                f"category={self.category!r}, items={len(self._inventory)})")

    def __str__(self) -> str:
        return repr(self)
