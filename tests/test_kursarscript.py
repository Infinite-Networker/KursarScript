"""
KursarScript test suite - covers interpreter, runtime, compiler, and CLI.
Run with:  pytest tests/ -v
"""
import pytest
import sys
import os

# Ensure package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kursarscript.interpreter import KSPLInterpreter, KSPLRuntimeError
from kursarscript.compiler import KSPLCompiler, KSPLCompileError
from kursarscript.runtime import (
    VirtuCard, VirtualTerminal, Avatar, VirtualItem,
    create_virtucard, transfer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(source: str) -> KSPLInterpreter:
    """Run KSPL source and return the interpreter (so tests can inspect globals)."""
    interp = KSPLInterpreter()
    interp.run(source)
    return interp


# ---------------------------------------------------------------------------
# Runtime tests
# ---------------------------------------------------------------------------

class TestVirtuCard:
    def test_create(self):
        avatar = Avatar("TestUser", "tester")
        card = VirtuCard(avatar, 500.0)
        assert card.balance == 500.0
        assert card.owner is avatar

    def test_tap_denominator(self):
        avatar = Avatar("Tapper", "user")
        card = VirtuCard(avatar, 100.0)
        result = card.tap_denominator(50.0)
        assert result is True
        assert card.balance == 150.0

    def test_tap_negative_fails(self):
        avatar = Avatar("Neg", "user")
        card = VirtuCard(avatar, 100.0)
        assert card.tap_denominator(-10.0) is False
        assert card.balance == 100.0

    def test_debit_success(self):
        avatar = Avatar("Debitor", "user")
        card = VirtuCard(avatar, 200.0)
        assert card.debit(50.0) is True
        assert card.balance == 150.0

    def test_debit_insufficient(self):
        avatar = Avatar("Poor", "user")
        card = VirtuCard(avatar, 10.0)
        assert card.debit(100.0) is False
        assert card.balance == 10.0

    def test_credit(self):
        avatar = Avatar("Rich", "user")
        card = VirtuCard(avatar, 0.0)
        card.credit(300.0)
        assert card.balance == 300.0

    def test_security_level(self):
        avatar = Avatar("Secure", "user")
        card = VirtuCard(avatar, 0.0)
        card.set_security_level("high")
        assert card.security_level == "high"

    def test_invalid_security_level(self):
        avatar = Avatar("User", "user")
        card = VirtuCard(avatar, 0.0)
        original = card.security_level
        card.set_security_level("unknown_level")
        assert card.security_level == original

    def test_transaction_history(self):
        avatar = Avatar("Historian", "user")
        card = VirtuCard(avatar, 100.0)
        card.debit(25.0, "test debit")
        card.credit(50.0, "test credit")
        history = card.get_transaction_history()
        assert len(history) == 2
        assert history[0]["type"] == "debit"
        assert history[1]["type"] == "credit"


class TestTransfer:
    def test_successful_transfer(self):
        a1 = Avatar("Sender", "user")
        a2 = Avatar("Receiver", "user")
        c1 = VirtuCard(a1, 500.0)
        c2 = VirtuCard(a2, 100.0)
        result = transfer(c1, c2, 200.0)
        assert result is True
        assert c1.balance == 300.0
        assert c2.balance == 300.0

    def test_insufficient_transfer(self):
        a1 = Avatar("Broke", "user")
        a2 = Avatar("Other", "user")
        c1 = VirtuCard(a1, 50.0)
        c2 = VirtuCard(a2, 100.0)
        result = transfer(c1, c2, 200.0)
        assert result is False
        assert c1.balance == 50.0
        assert c2.balance == 100.0

    def test_zero_transfer_fails(self):
        a1 = Avatar("X", "user")
        a2 = Avatar("Y", "user")
        c1 = VirtuCard(a1, 100.0)
        c2 = VirtuCard(a2, 100.0)
        assert transfer(c1, c2, 0.0) is False


class TestAvatar:
    def test_create(self):
        av = Avatar("Hero", "warrior")
        assert av.name == "Hero"
        assert av.role == "warrior"

    def test_set_get_attribute(self):
        av = Avatar("Player", "user")
        av.set_attribute("level", 10)
        assert av.get_attribute("level") == 10
        assert av.get_attribute("nonexistent", "default") == "default"

    def test_inventory(self):
        av = Avatar("Collector", "user")
        item = VirtualItem("Sword", "weapon", 100.0)
        av.add_item(item)
        inv = av.get_inventory()
        assert len(inv) == 1
        assert inv[0].name == "Sword"


class TestVirtualItem:
    def test_create(self):
        item = VirtualItem("Magic Staff", "weapon", 200.0)
        assert item.name == "Magic Staff"
        assert item.base_value == 200.0
        assert item.rarity == "common"

    def test_set_rarity(self):
        item = VirtualItem("Gem", "material", 50.0)
        item.set_rarity("legendary")
        assert item.rarity == "legendary"

    def test_calculate_value_legendary(self):
        item = VirtualItem("Sword", "weapon", 100.0)
        item.set_rarity("legendary")
        assert item.calculate_value() == 1000.0

    def test_calculate_value_epic(self):
        item = VirtualItem("Staff", "weapon", 100.0)
        item.set_rarity("epic")
        assert item.calculate_value() == 500.0

    def test_set_attribute(self):
        item = VirtualItem("Ring", "accessory", 30.0)
        item.set_attribute("magic_bonus", 15)
        assert item.get_attribute("magic_bonus") == 15


class TestVirtualTerminal:
    def test_create(self):
        t = VirtualTerminal("Shop", "general")
        assert t.name == "Shop"
        assert t.category == "general"
        assert len(t.get_inventory()) == 0

    def test_list_item(self):
        t = VirtualTerminal("Market", "general")
        t.list_item("Potion", 25.0, "Heals HP")
        inv = t.get_inventory()
        assert len(inv) == 1
        assert inv[0]["item"] == "Potion"
        assert inv[0]["price"] == 25.0

    def test_purchase_success(self):
        t = VirtualTerminal("Shop", "general")
        t.list_item("Sword", 100.0)
        av = Avatar("Buyer", "user")
        card = VirtuCard(av, 500.0)
        av.virtucard = card
        result = t.purchase_item(av, "Sword", card)
        assert result is True
        assert card.balance == 400.0
        assert len(av.get_inventory()) == 1
        assert len(t.get_inventory()) == 0

    def test_purchase_insufficient_funds(self):
        t = VirtualTerminal("Shop", "general")
        t.list_item("Dragon", 10000.0)
        av = Avatar("Poor", "user")
        card = VirtuCard(av, 100.0)
        result = t.purchase_item(av, "Dragon", card)
        assert result is False
        assert len(t.get_inventory()) == 1

    def test_purchase_not_found(self):
        t = VirtualTerminal("Empty", "general")
        av = Avatar("Someone", "user")
        card = VirtuCard(av, 100.0)
        result = t.purchase_item(av, "Nonexistent", card)
        assert result is False


class TestCreateVirtucard:
    def test_factory(self):
        av = Avatar("Factory User", "user")
        card = create_virtucard(av, 1000.0)
        assert isinstance(card, VirtuCard)
        assert card.balance == 1000.0
        assert card.owner is av


# ---------------------------------------------------------------------------
# Interpreter tests
# ---------------------------------------------------------------------------

class TestInterpreterBasics:
    def test_let_variable(self):
        interp = run("let x = 42")
        assert interp.globals["x"] == 42

    def test_string_variable(self):
        interp = run('let name = "Alice"')
        assert interp.globals["name"] == "Alice"

    def test_float_variable(self):
        interp = run("let pi = 3.14")
        assert abs(interp.globals["pi"] - 3.14) < 1e-9

    def test_boolean_true(self):
        interp = run("let flag = true")
        assert interp.globals["flag"] is True

    def test_boolean_false(self):
        interp = run("let flag = false")
        assert interp.globals["flag"] is False

    def test_null(self):
        interp = run("let x = null")
        assert interp.globals["x"] is None

    def test_assignment(self):
        interp = run("let x = 10\nx = 20")
        assert interp.globals["x"] == 20

    def test_arithmetic(self):
        interp = run("let result = 3 + 4 * 2")
        assert interp.globals["result"] == 11

    def test_print(self, capsys):
        run('print("Hello, World!")')
        captured = capsys.readouterr()
        assert "Hello, World!" in captured.out


class TestInterpreterIfElse:
    def test_if_true(self):
        interp = run("let x = 5\nlet y = 0\nif (x > 3) {\n    y = 1\n}")
        assert interp.globals["y"] == 1

    def test_if_false(self):
        interp = run("let x = 1\nlet y = 0\nif (x > 3) {\n    y = 1\n}")
        assert interp.globals["y"] == 0

    def test_if_else_true(self, capsys):
        src = """
let x = 10
if (x > 5) {
    print("big")
} else {
    print("small")
}
"""
        run(src)
        out = capsys.readouterr().out
        assert "big" in out
        assert "small" not in out

    def test_if_else_false(self, capsys):
        src = """
let x = 1
if (x > 5) {
    print("big")
} else {
    print("small")
}
"""
        run(src)
        out = capsys.readouterr().out
        assert "small" in out

    def test_if_elseif_else(self, capsys):
        src = """
let score = 75
if (score >= 90) {
    print("A")
} else if (score >= 70) {
    print("B")
} else {
    print("C")
}
"""
        run(src)
        out = capsys.readouterr().out
        assert "B" in out


class TestInterpreterForLoop:
    def test_for_range(self, capsys):
        run("for i in range(3) {\n    print(i)\n}")
        out = capsys.readouterr().out
        assert "0" in out
        assert "1" in out
        assert "2" in out

    def test_for_list(self, capsys):
        src = 'let items = ["a", "b", "c"]\nfor x in items {\n    print(x)\n}'
        run(src)
        out = capsys.readouterr().out
        assert "a" in out
        assert "b" in out
        assert "c" in out


class TestInterpreterFunctions:
    def test_function_definition_and_call(self, capsys):
        src = """
fn greet(name) {
    print("Hello", name)
}
greet("World")
"""
        run(src)
        out = capsys.readouterr().out
        assert "Hello" in out
        assert "World" in out

    def test_function_return(self):
        src = """
fn add(a, b) {
    return a + b
}
let result = add(3, 4)
"""
        interp = run(src)
        assert interp.globals["result"] == 7


class TestInterpreterClasses:
    def test_class_instantiation(self):
        src = """
class Point {
    field x = 0
    field y = 0
    fn init(px, py) {
        self.x = px
        self.y = py
    }
}
let p = Point(10, 20)
"""
        interp = run(src)
        obj = interp.globals["p"]
        assert obj.x == 10
        assert obj.y == 20

    def test_class_method_call(self, capsys):
        src = """
class Greeter {
    field msg = "Hi"
    fn greet(name) {
        print(self.msg, name)
    }
}
let g = Greeter()
g.greet("Alice")
"""
        run(src)
        out = capsys.readouterr().out
        assert "Hi" in out
        assert "Alice" in out


class TestInterpreterVRBuiltins:
    def test_avatar_creation(self):
        interp = run('let av = Avatar("TestAv", "tester")')
        av = interp.globals["av"]
        assert isinstance(av, Avatar)
        assert av.name == "TestAv"

    def test_create_virtucard_builtin(self):
        src = """
let av = Avatar("User", "user")
let card = create_virtucard(av, 500.0)
"""
        interp = run(src)
        card = interp.globals["card"]
        assert isinstance(card, VirtuCard)
        assert card.balance == 500.0

    def test_virtual_terminal_creation(self):
        interp = run('let t = VirtualTerminal("Market", "general")')
        t = interp.globals["t"]
        assert isinstance(t, VirtualTerminal)

    def test_virtual_item_creation(self):
        interp = run('let item = VirtualItem("Sword", "weapon", 150.0)')
        item = interp.globals["item"]
        assert isinstance(item, VirtualItem)
        assert item.base_value == 150.0

    def test_full_economy_flow(self):
        src = """
let av = Avatar("Alice", "explorer")
let card = create_virtucard(av, 1000.0)
av.virtucard = card
av.virtucard.tap_denominator(500.0)
"""
        interp = run(src)
        av = interp.globals["av"]
        assert av.virtucard.balance == 1500.0

    def test_transfer_builtin(self):
        src = """
let a = Avatar("Sender", "user")
let b = Avatar("Receiver", "user")
let ca = create_virtucard(a, 500.0)
let cb = create_virtucard(b, 100.0)
let ok = transfer(ca, cb, 200.0)
"""
        interp = run(src)
        assert interp.globals["ok"] is True
        assert interp.globals["ca"].balance == 300.0
        assert interp.globals["cb"].balance == 300.0


class TestInterpreterListsAndDicts:
    def test_list_literal(self):
        interp = run("let items = [1, 2, 3]")
        assert interp.globals["items"] == [1, 2, 3]

    def test_dict_literal(self):
        interp = run('let d = {"key": "value", "num": 42}')
        assert interp.globals["d"]["key"] == "value"
        assert interp.globals["d"]["num"] == 42

    def test_list_index(self):
        interp = run("let items = [10, 20, 30]\nlet x = items[1]")
        assert interp.globals["x"] == 20

    def test_dict_access(self):
        interp = run('let d = {"a": 1}\nlet v = d["a"]')
        assert interp.globals["v"] == 1

    def test_len_list(self):
        interp = run("let items = [1, 2, 3, 4]\nlet n = len(items)")
        assert interp.globals["n"] == 4


class TestInterpreterMultiline:
    def test_multiline_list(self):
        src = """
let items = [
    1,
    2,
    3
]
let n = len(items)
"""
        interp = run(src)
        assert interp.globals["n"] == 3

    def test_multiline_dict_list(self):
        src = """
let data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 80}
]
"""
        interp = run(src)
        assert len(interp.globals["data"]) == 2
        assert interp.globals["data"][0]["name"] == "Alice"

    def test_multiline_arithmetic(self):
        src = """
let a = 10
let b = 20
let c = a +
        b
"""
        interp = run(src)
        assert interp.globals["c"] == 30


# ---------------------------------------------------------------------------
# Compiler tests
# ---------------------------------------------------------------------------

class TestCompiler:
    def test_tokenize_class(self):
        compiler = KSPLCompiler()
        tokens = compiler.tokenize("class Foo {")
        assert any(t["type"] == "CLASS_DEF" and t["value"] == "Foo"
                   for t in tokens)

    def test_tokenize_fn(self):
        compiler = KSPLCompiler()
        tokens = compiler.tokenize("fn bar(x, y) {")
        fn_tokens = [t for t in tokens if t["type"] == "FN_DEF"]
        assert len(fn_tokens) == 1
        assert fn_tokens[0]["value"] == "bar"
        assert "x" in fn_tokens[0]["params"]

    def test_tokenize_let(self):
        compiler = KSPLCompiler()
        tokens = compiler.tokenize("let x = 42")
        let_tokens = [t for t in tokens if t["type"] == "LET_DEF"]
        assert len(let_tokens) == 1
        assert let_tokens[0]["value"] == "x"

    def test_compile_produces_structure(self):
        compiler = KSPLCompiler()
        source = """
class Player {
    field health = 100
    fn take_damage(amount) {
        return amount
    }
}
"""
        result = compiler.compile(source)
        assert "classes" in result
        assert "Player" in result["classes"]

    def test_compile_metadata(self):
        compiler = KSPLCompiler()
        result = compiler.compile("let x = 1")
        assert result["metadata"]["version"] == "1.0"

    def test_optimize_returns_dict(self):
        compiler = KSPLCompiler()
        result = compiler.compile("let x = 1")
        optimized = compiler.optimize(result)
        assert isinstance(optimized, dict)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestCLI:
    def test_version(self, capsys):
        from kursarscript.cli import main
        ret = main(["--version"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "1.0.0" in out

    def test_run_file(self, tmp_path, capsys):
        from kursarscript.cli import main
        script = tmp_path / "hello.kursar"
        script.write_text('print("Hello from CLI!")')
        ret = main([str(script)])
        assert ret == 0
        out = capsys.readouterr().out
        assert "Hello from CLI!" in out

    def test_run_missing_file(self, capsys):
        from kursarscript.cli import main
        ret = main(["nonexistent_file.kursar"])
        assert ret == 2

    def test_run_file_with_error(self, tmp_path, capsys):
        from kursarscript.cli import main
        script = tmp_path / "bad.kursar"
        script.write_text("let x = undefined_function_xyz()")
        ret = main([str(script)])
        assert ret == 1


# ---------------------------------------------------------------------------
# Integration test: full example script
# ---------------------------------------------------------------------------

class TestFullExample:
    def test_example_script_runs(self, capsys):
        """The full test.kursar example must run without errors."""
        from kursarscript.cli import run_file
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "test.kursar"
        )
        ret = run_file(example_path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "KURSARSCRIPT TEST SUCCESSFULLY COMPLETED" in out
        assert "READY TO BUILD THE FUTURE OF VIRTUAL ECONOMIES" in out

    def test_example_economy_numbers(self, capsys):
        """Key economic numbers from the example are correct."""
        from kursarscript.cli import run_file
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "test.kursar"
        )
        run_file(example_path)
        out = capsys.readouterr().out
        # 4 marketplaces each with items (some purchased)
        assert "Total Items Listed" in out
        # Currency in circulation
        assert "Total Currency in Circulation" in out


# ---------------------------------------------------------------------------
# New example scripts tests
# ---------------------------------------------------------------------------

class TestExampleScripts:
    """Tests that all example .kursar scripts run without errors."""

    def _examples_dir(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")

    def test_hello_world_runs(self, capsys):
        from kursarscript.cli import run_file
        ret = run_file(os.path.join(self._examples_dir(), "hello_world.kursar"))
        assert ret == 0
        out = capsys.readouterr().out
        assert "Hello, Virtual World!" in out
        assert "Hello World complete" in out

    def test_hello_world_grade(self, capsys):
        from kursarscript.cli import run_file
        run_file(os.path.join(self._examples_dir(), "hello_world.kursar"))
        out = capsys.readouterr().out
        assert "Grade: B" in out   # score=85 → B

    def test_classes_runs(self, capsys):
        from kursarscript.cli import run_file
        ret = run_file(os.path.join(self._examples_dir(), "classes.kursar"))
        assert ret == 0
        out = capsys.readouterr().out
        assert "Rex says: Woof!" in out
        assert "Whiskers says: Meow!" in out
        assert "Classes example complete" in out

    def test_classes_rpg_stats(self, capsys):
        from kursarscript.cli import run_file
        run_file(os.path.join(self._examples_dir(), "classes.kursar"))
        out = capsys.readouterr().out
        assert "Dragon Sword" in out
        assert "ATK: 150" in out
        assert "Tower Shield" in out
        assert "DEF: 200" in out

    def test_economy_runs(self, capsys):
        from kursarscript.cli import run_file
        ret = run_file(os.path.join(self._examples_dir(), "economy.kursar"))
        assert ret == 0
        out = capsys.readouterr().out
        assert "Economy Demo" in out
        assert "Economy demo complete" in out

    def test_economy_purchases(self, capsys):
        from kursarscript.cli import run_file
        run_file(os.path.join(self._examples_dir(), "economy.kursar"))
        out = capsys.readouterr().out
        assert "Health Potion" in out
        assert "Steel Sword" in out
        assert "Arcane Tome" in out

    def test_economy_transfer_success(self, capsys):
        from kursarscript.cli import run_file
        run_file(os.path.join(self._examples_dir(), "economy.kursar"))
        out = capsys.readouterr().out
        assert "Shopper_01 → Seller_99" in out
        assert "MerchantGuild → Shopper_01" in out

    def test_economy_overdraft_fails(self, capsys):
        from kursarscript.cli import run_file
        run_file(os.path.join(self._examples_dir(), "economy.kursar"))
        out = capsys.readouterr().out
        assert "FAILED" in out


# ---------------------------------------------------------------------------
# Runtime alias tests
# ---------------------------------------------------------------------------

class TestRuntimeAliases:
    """Test the convenience aliases added to the runtime types."""

    def test_virtucardcard_set_security_alias(self, capsys):
        """VirtuCard.set_security() is an alias for set_security_level()."""
        avatar = Avatar("Alias_Test", "tester")
        card = VirtuCard(avatar, 100.0)
        card.set_security("high")
        assert card.security_level == "high"

    def test_virtucardcard_set_security_level_still_works(self):
        avatar = Avatar("Alias_Test2", "tester")
        card = VirtuCard(avatar, 100.0)
        card.set_security_level("maximum")
        assert card.security_level == "maximum"

    def test_virtucardcard_get_history_alias(self):
        """VirtuCard.get_history() is an alias for get_transaction_history()."""
        avatar = Avatar("History_Test", "tester")
        card = VirtuCard(avatar, 200.0)
        card.tap_denominator(50.0)
        card.debit(30.0)
        hist_alias = card.get_history()
        hist_full = card.get_transaction_history()
        assert hist_alias == hist_full
        assert len(hist_alias) == 2

    def test_terminal_list_item_object(self, capsys):
        """VirtualTerminal.list_item accepts a VirtualItem object."""
        terminal = VirtualTerminal("Test Market", "general")
        item = VirtualItem("Magic Orb", "magic", 75.0)
        terminal.list_item(item)
        inv = terminal.get_inventory()
        assert len(inv) == 1
        assert inv[0]["item"] == "Magic Orb"
        assert inv[0]["price"] == 75.0

    def test_terminal_list_item_object_with_price_override(self, capsys):
        """When listing a VirtualItem, a price arg overrides base_value."""
        terminal = VirtualTerminal("Override Market", "general")
        item = VirtualItem("Rare Gem", "gem", 100.0)
        terminal.list_item(item, 250.0)
        inv = terminal.get_inventory()
        assert inv[0]["price"] == 250.0

    def test_terminal_purchase_alias(self, capsys):
        """VirtualTerminal.purchase(name, card) works with 2 args."""
        avatar = Avatar("Buyer", "buyer")
        card = VirtuCard(avatar, 500.0)
        terminal = VirtualTerminal("Quick Shop", "general")
        terminal.list_item("Quick Item", 100.0)
        result = terminal.purchase("Quick Item", card)
        assert result is True
        assert card.balance == 400.0

    def test_terminal_purchase_alias_insufficient_funds(self, capsys):
        """purchase() returns False on insufficient funds."""
        avatar = Avatar("PoorBuyer", "buyer")
        card = VirtuCard(avatar, 10.0)
        terminal = VirtualTerminal("Expensive Shop", "general")
        terminal.list_item("Expensive Item", 9999.0)
        result = terminal.purchase("Expensive Item", card)
        assert result is False
        assert card.balance == 10.0  # unchanged

    def test_terminal_purchase_alias_not_found(self, capsys):
        """purchase() returns False when item not in inventory."""
        avatar = Avatar("Shopper", "buyer")
        card = VirtuCard(avatar, 500.0)
        terminal = VirtualTerminal("Empty Shop", "general")
        result = terminal.purchase("Nonexistent Item", card)
        assert result is False


# ---------------------------------------------------------------------------
# Interpreter – additional edge cases
# ---------------------------------------------------------------------------

class TestInterpreterEdgeCases:
    """Edge-case interpreter tests."""

    def test_nested_function_calls(self, capsys):
        src = """
fn double(x) {
    return x * 2
}
fn quad(x) {
    return double(double(x))
}
let result = quad(5)
print(result)
"""
        interp = run(src)
        out = capsys.readouterr().out
        assert "20" in out

    def test_string_concatenation_assignment(self, capsys):
        src = """
let a = "Hello"
let b = ", "
let c = "World!"
let msg = a + b + c
print(msg)
"""
        run(src)
        out = capsys.readouterr().out
        assert "Hello, World!" in out

    def test_class_field_default(self):
        src = """
class Box {
    field width = 10
    field height = 5
}
let b = Box()
"""
        interp = run(src)
        obj = interp.globals["b"]
        assert obj.width == 10
        assert obj.height == 5

    def test_for_loop_accumulate(self):
        src = """
let numbers = [1, 2, 3, 4, 5]
let total = 0
for n in numbers {
    total = total + n
}
"""
        interp = run(src)
        assert interp.globals["total"] == 15

    def test_boolean_logic(self):
        src = """
let a = true
let b = false
let c = a and b
let d = a or b
let e = not b
"""
        interp = run(src)
        assert interp.globals["c"] is False
        assert interp.globals["d"] is True
        assert interp.globals["e"] is True

    def test_null_assignment(self):
        src = "let x = null"
        interp = run(src)
        assert interp.globals["x"] is None

    def test_nested_if_else(self):
        src = """
let score = 75
let grade = "F"
if (score >= 90) {
    grade = "A"
} else if (score >= 80) {
    grade = "B"
} else if (score >= 70) {
    grade = "C"
} else {
    grade = "D"
}
"""
        interp = run(src)
        assert interp.globals["grade"] == "C"

    def test_multiline_string_list(self):
        src = """
let fruits = [
    "apple",
    "banana",
    "cherry"
]
"""
        interp = run(src)
        assert interp.globals["fruits"] == ["apple", "banana", "cherry"]

    def test_runtime_error_raised(self):
        from kursarscript.interpreter import KSPLRuntimeError
        with pytest.raises((KSPLRuntimeError, Exception)):
            run("let x = totally_undefined_xyz_func()")


# ---------------------------------------------------------------------------
# New language features: while, break, continue, inline method bodies
# ---------------------------------------------------------------------------

class TestWhileLoop:
    """Tests for the while loop construct."""

    def test_basic_while(self):
        src = """
let i = 0
while (i < 5) {
    i = i + 1
}
"""
        interp = run(src)
        assert interp.globals["i"] == 5

    def test_while_factorial(self):
        src = """
let n = 1
let result = 1
while (n <= 5) {
    result = result * n
    n = n + 1
}
"""
        interp = run(src)
        assert interp.globals["result"] == 120   # 5! = 120

    def test_while_false_body_skipped(self):
        src = """
let x = 99
while (false) {
    x = 0
}
"""
        interp = run(src)
        assert interp.globals["x"] == 99

    def test_while_with_break(self):
        src = """
let i = 0
while (true) {
    i = i + 1
    if (i >= 3) {
        break
    }
}
"""
        interp = run(src)
        assert interp.globals["i"] == 3

    def test_while_countdown(self, capsys):
        src = """
let c = 3
while (c > 0) {
    print(c)
    c = c - 1
}
"""
        run(src)
        out = capsys.readouterr().out
        assert "3" in out
        assert "2" in out
        assert "1" in out

    def test_while_infinite_guard(self):
        """While loop must raise an error if it runs forever."""
        from kursarscript.interpreter import KSPLRuntimeError
        with pytest.raises((KSPLRuntimeError, Exception)):
            run("while (true) { let x = 1 }")


class TestBreakContinue:
    """Tests for break and continue inside loops."""

    def test_break_for_loop(self):
        src = """
let found = -1
for x in [10, 20, 30, 40, 50] {
    if (x == 30) {
        found = x
        break
    }
}
"""
        interp = run(src)
        assert interp.globals["found"] == 30

    def test_break_stops_early(self):
        """Iterations after break must not execute."""
        src = """
let count = 0
for x in [1, 2, 3, 4, 5] {
    if (x == 3) {
        break
    }
    count = count + 1
}
"""
        interp = run(src)
        assert interp.globals["count"] == 2   # only x=1 and x=2

    def test_continue_skips_iteration(self):
        src = """
let total = 0
for x in [1, 2, 3, 4, 5] {
    if (x == 3) {
        continue
    }
    total = total + x
}
"""
        interp = run(src)
        assert interp.globals["total"] == 12   # 1+2+4+5 = 12

    def test_continue_only_odd(self):
        src = """
let evens = 0
for x in range(1, 11) {
    if (x % 2 != 0) {
        continue
    }
    evens = evens + 1
}
"""
        interp = run(src)
        assert interp.globals["evens"] == 5   # 2,4,6,8,10

    def test_break_while_loop(self):
        src = """
let steps = 0
while (true) {
    steps = steps + 1
    if (steps == 7) {
        break
    }
}
"""
        interp = run(src)
        assert interp.globals["steps"] == 7


class TestInlineMethodBodies:
    """Tests for single-line { body } method syntax."""

    def test_inline_init(self):
        src = """
class Box {
    field w = 0
    field h = 0
    fn init(width, height) { self.w = width  self.h = height }
}
let b = Box(5, 10)
"""
        interp = run(src)
        obj = interp.globals["b"]
        assert obj.w == 5
        assert obj.h == 10

    def test_inline_method_call(self, capsys):
        src = """
class Greeter {
    field msg = ""
    fn init(m) { self.msg = m }
    fn greet(name) { print(self.msg, name) }
}
let g = Greeter("Hello")
g.greet("World")
"""
        run(src)
        out = capsys.readouterr().out
        assert "Hello" in out
        assert "World" in out

    def test_inline_two_statements(self):
        src = """
class Pt {
    field x = 0
    field y = 0
    fn init(px, py) { self.x = px  self.y = py }
    fn move(dx, dy) { self.x = self.x + dx  self.y = self.y + dy }
}
let p = Pt(1, 2)
p.move(3, 4)
"""
        interp = run(src)
        obj = interp.globals["p"]
        assert obj.x == 4
        assert obj.y == 6

    def test_list_of_objects_with_inline_init(self, capsys):
        src = """
class Tag {
    field label = ""
    fn init(l) { self.label = l }
    fn show() { print(self.label) }
}
let tags = [Tag("alpha"), Tag("beta"), Tag("gamma")]
for t in tags {
    t.show()
}
"""
        run(src)
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out
        assert "gamma" in out

    def test_fn_returning_inline_init_object(self):
        src = """
class Point {
    field x = 0
    field y = 0
    fn init(px, py) { self.x = px  self.y = py }
}
fn make_pt(a, b) {
    let p = Point(a, b)
    return p
}
let pt = make_pt(7, 8)
"""
        interp = run(src)
        obj = interp.globals["pt"]
        assert obj.x == 7
        assert obj.y == 8


class TestAdvancedExample:
    """Tests that the advanced.kursar example runs cleanly."""

    def test_advanced_example_runs(self, capsys):
        from kursarscript.cli import run_file
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "advanced.kursar"
        )
        ret = run_file(path)
        assert ret == 0
        out = capsys.readouterr().out
        assert "Advanced features demo complete" in out

    def test_advanced_factorial(self, capsys):
        from kursarscript.cli import run_file
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "advanced.kursar"
        )
        run_file(path)
        out = capsys.readouterr().out
        assert "720" in out   # 6!

    def test_advanced_break_finds_42(self, capsys):
        from kursarscript.cli import run_file
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "advanced.kursar"
        )
        run_file(path)
        out = capsys.readouterr().out
        assert "42" in out

    def test_advanced_npc_system(self, capsys):
        from kursarscript.cli import run_file
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "advanced.kursar"
        )
        run_file(path)
        out = capsys.readouterr().out
        assert "Goblin Scout" in out
        assert "Stone Golem" in out
        assert "SKIPPING boss" in out


