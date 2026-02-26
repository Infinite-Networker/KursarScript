"""
KursarScript Interpreter - Executes KSPL (.kursar) source code.

Supports:
  - Classes with fields and methods
  - let / assignment statements
  - if / else if / else blocks
  - for … in … { } loops
  - Function definitions (fn)
  - Return statements
  - Method calls (obj.method(...))
  - Built-in VR economy types (Avatar, VirtuCard, VirtualTerminal, VirtualItem)
  - Python-compatible expression evaluation via safe eval
"""

import re
import ast as _ast
import sys
from typing import Dict, List, Any, Optional

from .runtime import (
    VirtuCard, VirtualTerminal, Avatar, VirtualItem,
    create_virtucard, transfer,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class KSPLRuntimeError(Exception):
    """Runtime error raised during KSPL execution."""


class _ReturnSignal(Exception):
    """Internal signal used to propagate return values through call stack."""
    def __init__(self, value: Any):
        self.value = value


class _BreakSignal(Exception):
    """Internal signal for break statement inside loops."""


class _ContinueSignal(Exception):
    """Internal signal for continue statement inside loops."""


# ---------------------------------------------------------------------------
# KSPLClass / KSPLObject
# ---------------------------------------------------------------------------

class KSPLClass:
    """Represents a KSPL class definition."""

    def __init__(self, name: str, methods: Dict, fields: Dict):
        self.name = name
        self.methods = methods    # {method_name: {'params': [...], 'body': [...]}}
        self.fields = fields      # {field_name: initial_value}


class KSPLObject:
    """Represents an instance of a KSPL class."""

    def __init__(self, klass: KSPLClass, interpreter: 'KSPLInterpreter',
                 args: List = None):
        self._klass = klass
        # Copy class-level fields
        self.__dict__.update(klass.fields)

        # Call constructor (init) if present
        if 'init' in klass.methods:
            self.call_method('init', interpreter, args or [])
        elif args and len(args) > 0:
            # Fallback: first positional arg → self.name
            self.name = args[0]

    def call_method(self, method_name: str, interpreter: 'KSPLInterpreter',
                    args: List) -> Any:
        if method_name not in self._klass.methods:
            raise KSPLRuntimeError(
                f"Method '{method_name}' not found in class '{self._klass.name}'"
            )
        method = self._klass.methods[method_name]
        local_env: Dict = {'self': self}
        for i, param in enumerate(method['params']):
            local_env[param] = args[i] if i < len(args) else None

        try:
            return interpreter.execute_block(method['body'], local_env)
        except _ReturnSignal as ret:
            return ret.value

    def __repr__(self) -> str:
        name = getattr(self, 'name', None)
        if name:
            return f"<{self._klass.name}:{name}>"
        return f"<{self._klass.name} object>"

    def __str__(self) -> str:
        return repr(self)


# ---------------------------------------------------------------------------
# KSPLInterpreter
# ---------------------------------------------------------------------------

class KSPLInterpreter:
    """
    KursarScript Interpreter.

    Usage::

        interp = KSPLInterpreter()
        interp.run(source_code)
    """

    def __init__(self, vr_environment=None):
        self.classes: Dict[str, KSPLClass] = {}
        self.globals: Dict[str, Any] = {}
        self.vr_environment = vr_environment
        self._setup_builtins()

    # ------------------------------------------------------------------
    # Built-ins
    # ------------------------------------------------------------------

    def _setup_builtins(self) -> None:
        self.globals.update({
            # VR economy types
            'create_virtucard': create_virtucard,
            'transfer': transfer,
            'VirtualTerminal': VirtualTerminal,
            'Avatar': Avatar,
            'VirtualItem': VirtualItem,
            'VirtuCard': VirtuCard,

            # Standard builtins
            'print': self._builtin_print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'range': range,
            'abs': abs,
            'max': max,
            'min': min,
            'round': round,
            'type': type,

            # KSPL literals
            'true': True,
            'false': False,
            'null': None,

            # VR helpers
            'get_avatar': self._get_avatar,
            'create_portal': self._create_portal,
            'get_environment': self._get_environment,
        })

    def _builtin_print(self, *args) -> None:
        output = ' '.join(str(a) for a in args)
        if self.vr_environment:
            self.vr_environment.display_message(output)
        else:
            print(output)

    def _get_avatar(self, avatar_id):
        if self.vr_environment:
            return self.vr_environment.get_avatar(avatar_id)
        return None

    def _create_portal(self, from_terminal, to_terminal):
        if self.vr_environment:
            return self.vr_environment.create_portal(from_terminal, to_terminal)
        return None

    def _get_environment(self):
        return self.vr_environment

    # ------------------------------------------------------------------
    # Source → statement list (parsing)
    # ------------------------------------------------------------------

    def parse(self, source: str) -> List[Any]:
        """
        Parse KSPL source into a flat list of statement tuples / dicts.
        Multi-line blocks (class, fn, if, for, else) are gathered here.
        Multi-line expressions (e.g. let x = [\n...\n]) are joined first.
        """
        lines = source.split('\n')
        # Strip line-end comments but preserve strings
        cleaned = []
        for ln in lines:
            cleaned.append(self._strip_line_comment(ln))

        statements: List = []
        i = 0
        while i < len(cleaned):
            line = cleaned[i].strip()
            if not line:
                i += 1
                continue

            # class Foo {
            if re.match(r'^class\s+\w+\s*\{', line):
                stmt, i = self._parse_block_stmt(cleaned, i, 'class')
                statements.append(stmt)

            # fn foo(...) {
            elif re.match(r'^fn\s+\w+\s*\(', line):
                stmt, i = self._parse_block_stmt(cleaned, i, 'fn')
                statements.append(stmt)

            # if (...) {  or  if ... {
            elif re.match(r'^if\s*[\(\s]', line):
                stmt, i = self._parse_if(cleaned, i)
                statements.append(stmt)

            # for x in expr {
            elif re.match(r'^for\s+\w+\s+in\s+', line):
                stmt, i = self._parse_for(cleaned, i)
                statements.append(stmt)

            # while (cond) {  or  while cond {
            elif re.match(r'^while\s*[\(\s]', line):
                stmt, i = self._parse_while(cleaned, i)
                statements.append(stmt)

            else:
                # Handle multi-line expressions: let x = [\n...\n] etc.
                joined, i = self._join_multiline_stmt(cleaned, i)
                statements.append(('stmt', joined))

        return statements

    @staticmethod
    def _bracket_balance(text: str) -> int:
        """Return net bracket/paren/brace depth for a text (ignoring strings)."""
        depth = 0
        in_str = False
        str_ch = None
        for ch in text:
            if in_str:
                if ch == str_ch:
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch in ('(', '['):
                depth += 1
            elif ch in (')', ']'):
                depth -= 1
            # We intentionally ignore '{' and '}' here because those are
            # handled by _collect_block; we only care about [] and ()
        return depth

    # Trailing binary operators that indicate line continuation.
    # Only unambiguous cases: +, comma, logical operators.
    # We exclude -, *, /, etc. to avoid false positives.
    _TRAILING_OP = re.compile(
        r'(\+|,|\band\b|\bor\b)\s*$'
    )

    def _join_multiline_stmt(self, lines: List[str], start: int) -> tuple:
        """
        Join a logical statement that may span multiple lines.
        Continuation is detected by:
          1. Unbalanced '(' or '[' at end of accumulated text
          2. Line ending with a binary operator (trailing +, -, *, etc.)
        Returns (joined_statement, next_index).
        """
        parts = [lines[start].strip()]
        depth = self._bracket_balance(parts[0])
        i = start + 1

        def _needs_continuation(text: str, d: int) -> bool:
            if d != 0:
                return True
            # Check for trailing binary operator
            return bool(self._TRAILING_OP.search(text.rstrip()))

        while _needs_continuation(' '.join(parts), depth) and i < len(lines):
            next_line = lines[i].strip()
            if next_line:
                parts.append(next_line)
                depth += self._bracket_balance(next_line)
            i += 1
        return ' '.join(parts), i

    # ---- helpers -------------------------------------------------------

    @staticmethod
    def _strip_line_comment(line: str) -> str:
        """Remove // comments that are not inside strings."""
        result = []
        in_str = False
        str_char = None
        j = 0
        while j < len(line):
            ch = line[j]
            if in_str:
                result.append(ch)
                if ch == str_char:
                    in_str = False
            else:
                if ch in ('"', "'"):
                    in_str = True
                    str_char = ch
                    result.append(ch)
                elif ch == '/' and j + 1 < len(line) and line[j + 1] == '/':
                    break  # rest is comment
                else:
                    result.append(ch)
            j += 1
        return ''.join(result)

    def _collect_block(self, lines: List[str], start: int) -> tuple:
        """
        Starting at `start` (the line containing the opening '{'), collect
        body lines until the matching closing '}'.

        Handles both multi-line blocks AND single-line blocks:
          fn init(n) { self.name = n }
          for x in items { print(x) }

        Returns (body_lines, next_index, closing_line_remainder).
        - body_lines: lines inside the block (stripped)
        - next_index: index of the line AFTER the closing '}'
        - closing_line_remainder: any text on the same line after the '}',
          e.g. ' else {' when the closing line is '} else {'

        Callers that don't care about the remainder can ignore the third
        element via:  body, next_i, _ = self._collect_block(...)
        """
        i = start
        depth = 0
        body: List[str] = []
        inline_buf: List[str] = []   # chars between { and } on the same line
        in_inline = False            # we've seen the opening { on this line

        while i < len(lines):
            stripped = lines[i].strip()

            # Walk character-by-character so we can detect depth==0 mid-line
            j = 0
            while j < len(stripped):
                ch = stripped[j]
                if ch == '{':
                    depth += 1
                    if depth == 1:
                        # Start capturing inline body content
                        in_inline = True
                        j += 1
                        continue
                    else:
                        if in_inline:
                            inline_buf.append(ch)
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        # Flush any inline body we collected
                        if inline_buf:
                            inline_content = ''.join(inline_buf).strip()
                            if inline_content:
                                # Multiple statements separated by spaces/newlines
                                for stmt_part in re.split(r'\s{2,}|\n', inline_content):
                                    stmt_part = stmt_part.strip()
                                    if stmt_part:
                                        body.append(stmt_part)
                            inline_buf = []
                            in_inline = False
                        # Remainder of the line after the closing '}'
                        remainder = stripped[j + 1:].strip()
                        i += 1
                        return body, i, remainder
                    else:
                        if in_inline:
                            inline_buf.append(ch)
                else:
                    if in_inline:
                        inline_buf.append(ch)
                j += 1

            # Whole line processed without depth hitting 0
            if in_inline and i > start:
                # We're inside the block but haven't closed yet — this is a
                # regular multi-line body line
                content = ''.join(inline_buf).strip()
                if content:
                    body.append(content)
                inline_buf = []
            elif i > start and depth > 0:
                body.append(stripped)
            i += 1

        return body, i, ''


    def _parse_block_stmt(self, lines: List[str], start: int,
                          kind: str) -> tuple:
        """Parse a class or fn block."""
        line = lines[start].strip()
        body, next_i, _ = self._collect_block(lines, start)

        if kind == 'class':
            m = re.match(r'^class\s+(\w+)', line)
            class_name = m.group(1)
            return ('class', class_name, body), next_i

        # kind == 'fn'
        m = re.match(r'^fn\s+(\w+)\s*\(([^)]*)\)', line)
        fn_name = m.group(1)
        params = [p.strip() for p in m.group(2).split(',') if p.strip()]
        return ('function', fn_name, params, body), next_i

    def _parse_if(self, lines: List[str], start: int) -> tuple:
        """
        Parse if / else-if / else chain.
        Returns a nested dict structure and the next index.

        Handles all patterns:
          if (cond) { ... }  else { ... }
          if (cond) { ... }
          } else {          <- closing brace and else on same line
        """
        line = lines[start].strip()
        # Extract condition: everything between 'if' and the opening '{' of the
        # then-block. We scan for the '{' at depth 0 (ignoring nested parens/braces).
        condition = self._extract_if_condition(line)

        then_body, next_i, remainder = self._collect_block(lines, start)

        else_body: List[str] = []
        else_ifs: List = []

        # The 'remainder' from _collect_block may already contain 'else {'
        # or 'else if (cond) {'
        def _check_else(text: str) -> str:
            """Return 'else', 'elseif', or '' depending on text."""
            t = text.strip()
            if re.match(r'^else\s+if\s*[\(\s]', t):
                return 'elseif'
            if re.match(r'^else\s*\{', t):
                return 'else'
            return ''

        def _get_elseif_cond(text: str) -> str:
            return self._extract_elseif_condition(text)

        # Synthetic line list so _collect_block can be reused for
        # the else / elseif blocks that start inline (remainder)
        # We'll create a virtual 'else {...}' line and prepend it.
        pending_remainder = remainder

        while True:
            # First check any leftover text on the closing-brace line
            which = _check_else(pending_remainder) if pending_remainder else ''

            if not which:
                # Check next real line
                if next_i >= len(lines):
                    break
                peek = lines[next_i].strip()
                which = _check_else(peek)
                if not which:
                    break
                # Use next_i as the start for _collect_block
                ei_cond = _get_elseif_cond(peek) if which == 'elseif' else ''
                ei_body, next_i, pending_remainder = self._collect_block(
                    lines, next_i
                )
            else:
                # Remainder is the else/elseif clause — inject it as a
                # synthetic single line so _collect_block can parse it.
                ei_cond = _get_elseif_cond(pending_remainder) if which == 'elseif' else ''
                synthetic = [pending_remainder] + lines[next_i:]
                ei_body, rel_i, pending_remainder = self._collect_block(
                    synthetic, 0
                )
                next_i = next_i + rel_i - 1  # adjust back to real line index

            if which == 'elseif':
                else_ifs.append((ei_cond, ei_body))
            else:  # 'else'
                else_body = ei_body
                break

        stmt = {
            'type': 'if',
            'condition': condition,
            'then': then_body,
            'elseifs': else_ifs,
            'else': else_body,
        }
        return stmt, next_i

    def _parse_for(self, lines: List[str], start: int) -> tuple:
        """Parse for variable in iterable { body }."""
        line = lines[start].strip()
        m = re.match(r'^for\s+(\w+)\s+in\s+(.*?)\s*\{', line)
        var_name = m.group(1)
        iter_expr = m.group(2).strip()
        body, next_i, _ = self._collect_block(lines, start)
        return ('for', var_name, iter_expr, body), next_i

    def _parse_while(self, lines: List[str], start: int) -> tuple:
        """Parse while (condition) { body }."""
        line = lines[start].strip()
        cond = self._extract_if_condition(line.replace('while', 'if', 1))
        body, next_i, _ = self._collect_block(lines, start)
        return ('while', cond, body), next_i

    # ------------------------------------------------------------------
    # Class loading
    # ------------------------------------------------------------------

    def _load_class(self, class_name: str, body: List[str]) -> KSPLClass:
        methods: Dict = {}
        fields: Dict = {}
        i = 0

        while i < len(body):
            line = body[i].strip()
            if not line:
                i += 1
                continue

            if re.match(r'^fn\s+\w+\s*\(', line):
                fn_m = re.match(r'^fn\s+(\w+)\s*\(([^)]*)\)', line)
                method_name = fn_m.group(1)
                params = [p.strip() for p in fn_m.group(2).split(',') if p.strip()]
                # Collect method body
                method_body, i, _ = self._collect_block(body, i)
                methods[method_name] = {'params': params, 'body': method_body}

            elif line.startswith('field '):
                field_m = re.match(r'^field\s+(\w+)\s*=\s*(.*)', line)
                if field_m:
                    fname = field_m.group(1)
                    fval = self._eval_expression(field_m.group(2).strip(), {})
                    fields[fname] = fval
                i += 1
            else:
                i += 1

        return KSPLClass(class_name, methods, fields)

    # ------------------------------------------------------------------
    # Expression evaluation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_if_condition(line: str) -> str:
        """
        Extract the condition from an 'if' line by finding the '{' that opens
        the then-block (at depth 0), returning everything between 'if' and it.

        'if (cond) {'          → 'cond'
        'if (transfer(a,b)) {' → 'transfer(a,b)'
        'if x > 0 {'           → 'x > 0'
        """
        # Skip the 'if' keyword
        rest = line[2:].strip()
        # Scan for '{' at depth 0
        depth = 0
        in_str = False
        str_ch = None
        i = 0
        while i < len(rest):
            ch = rest[i]
            if in_str:
                if ch == str_ch:
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch in ('(', '['):
                depth += 1
            elif ch in (')', ']'):
                depth -= 1
            elif ch == '{' and depth == 0:
                cond = rest[:i].strip()
                # Strip outer parens if present: (cond) → cond
                if cond.startswith('(') and cond.endswith(')'):
                    cond = cond[1:-1].strip()
                return cond
            i += 1
        return rest.strip().rstrip('{').strip()

    @staticmethod
    def _extract_elseif_condition(line: str) -> str:
        """
        Extract the condition from an 'else if ...' line.
        'else if (cond) {' → 'cond'
        """
        # Strip leading '} ' if present
        text = re.sub(r'^\}\s*', '', line.strip())
        # Strip 'else if'
        text = re.sub(r'^else\s+if\s*', '', text).strip()
        # Reuse _extract_if_condition logic but treat text as 'if text'
        rest = text
        depth = 0
        in_str = False
        str_ch = None
        i = 0
        while i < len(rest):
            ch = rest[i]
            if in_str:
                if ch == str_ch:
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch in ('(', '['):
                depth += 1
            elif ch in (')', ']'):
                depth -= 1
            elif ch == '{' and depth == 0:
                cond = rest[:i].strip()
                if cond.startswith('(') and cond.endswith(')'):
                    cond = cond[1:-1].strip()
                return cond
            i += 1
        return rest.strip().rstrip('{').strip()

    @staticmethod
    def _is_pure_call(expr: str) -> bool:
        """
        Return True iff `expr` is a single function/method call with no
        top-level binary operators after the closing ')'.

        'len(x)'              → True
        'obj.method(a)'       → True
        'len(x) + len(y)'     → False
        'len(x) > 0'          → False
        """
        # Find the position of the first '('
        paren_pos = expr.find('(')
        if paren_pos == -1:
            return False
        # Walk from that '(' to find its matching ')'
        depth = 0
        in_str = False
        str_ch = None
        for i in range(paren_pos, len(expr)):
            ch = expr[i]
            if in_str:
                if ch == str_ch:
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    # matched closing paren - check that nothing follows
                    return i == len(expr) - 1
        return False

    # ------------------------------------------------------------------
    # Expression evaluation
    # ------------------------------------------------------------------

    def _eval_expression(self, expr: str, local_env: Dict) -> Any:
        expr = expr.strip()
        if not expr:
            return None

        # String literals
        if ((expr.startswith('"') and expr.endswith('"')) or
                (expr.startswith("'") and expr.endswith("'"))):
            # Support escape sequences
            return expr[1:-1].encode('raw_unicode_escape').decode('unicode_escape')

        # KSPL booleans / null
        if expr == 'true':
            return True
        if expr == 'false':
            return False
        if expr == 'null':
            return None

        # Integer / float literals
        if re.fullmatch(r'-?\d+', expr):
            return int(expr)
        if re.fullmatch(r'-?\d+\.\d+', expr):
            return float(expr)

        # Inline list literals: [...]
        if expr.startswith('['):
            return self._eval_list_literal(expr, local_env)

        # Inline dict literals: {...}
        if expr.startswith('{'):
            return self._eval_dict_literal(expr, local_env)

        # Function / method call - only if the ENTIRE expression is a single call.
        # e.g. "len(x)" or "obj.method(a, b)" - NOT "len(x) + len(y)"
        if re.match(r'^[\w\.]+\s*\(', expr) and self._is_pure_call(expr):
            return self._eval_call(expr, local_env)

        # Property / index access: obj.prop or obj["key"] or obj[idx]
        # Only treat as pure access chain if it contains no binary operators.
        # Expressions like `data["trend"] == "rising"` should go to _safe_eval.
        _HAS_OP = re.compile(r'\s*(==|!=|<=|>=|<|>|\+|-|\*|/|%|\band\b|\bor\b|\bnot\b)\s*')
        if ('.' in expr or '[' in expr) and not _HAS_OP.search(expr):
            return self._eval_access(expr, local_env)

        # Simple name lookup
        if re.fullmatch(r'\w+', expr):
            if expr in local_env:
                return local_env[expr]
            if expr in self.globals:
                return self.globals[expr]
            # Maybe it's a class constructor name
            if expr in self.classes:
                interp = self
                cls_name = expr
                def _ctor(*args):
                    return KSPLObject(interp.classes[cls_name], interp, list(args))
                return _ctor

        # Arithmetic / comparison: delegate to Python's safe-eval
        return self._safe_eval(expr, local_env)

    def _safe_eval(self, expr: str, local_env: Dict) -> Any:
        """Evaluate arbitrary Python-compatible expression safely."""
        # Build combined environment
        env: Dict = {}
        env.update(self.globals)
        env.update(local_env)

        # Replace KSPL operators with Python equivalents
        py_expr = expr.replace(' and ', ' and ').replace(' or ', ' or ')

        try:
            tree = _ast.parse(py_expr, mode='eval')
            return eval(compile(tree, '<expr>', 'eval'),
                        {'__builtins__': {}}, env)
        except Exception as exc:
            raise KSPLRuntimeError(
                f"Cannot evaluate expression: {expr!r}  ({exc})"
            )

    # ---- list / dict literal -----------------------------------------------

    def _eval_list_literal(self, expr: str, local_env: Dict) -> list:
        """Evaluate a KSPL list literal like [a, b, {k: v}, ...]."""
        inner = expr[1:-1].strip()
        if not inner:
            return []
        items = self._split_args(inner)
        return [self._eval_expression(item.strip(), local_env) for item in items]

    def _eval_dict_literal(self, expr: str, local_env: Dict) -> dict:
        """Evaluate a KSPL dict literal like {key: val, ...}."""
        inner = expr[1:-1].strip()
        if not inner:
            return {}
        result: Dict = {}
        pairs = self._split_args(inner)
        for pair in pairs:
            pair = pair.strip()
            # Find the colon not inside nested structures
            colon_idx = self._find_colon(pair)
            if colon_idx == -1:
                continue
            k_str = pair[:colon_idx].strip().strip('"\'')
            v_str = pair[colon_idx + 1:].strip()
            result[k_str] = self._eval_expression(v_str, local_env)
        return result

    @staticmethod
    def _find_colon(s: str) -> int:
        depth = 0
        in_str = False
        str_ch = None
        for idx, ch in enumerate(s):
            if in_str:
                if ch == str_ch:
                    in_str = False
            else:
                if ch in ('"', "'"):
                    in_str = True
                    str_ch = ch
                elif ch in ('(', '[', '{'):
                    depth += 1
                elif ch in (')', ']', '}'):
                    depth -= 1
                elif ch == ':' and depth == 0:
                    return idx
        return -1

    # ---- access (obj.prop / obj["key"] / obj[idx]) -------------------------

    def _eval_access(self, expr: str, local_env: Dict) -> Any:
        """Evaluate property / index access chains."""
        # Decompose into parts, respecting nesting
        parts = self._split_access(expr)
        obj = self._eval_expression(parts[0], local_env)

        for part in parts[1:]:
            # Index access: ["key"] or [idx]
            idx_m = re.fullmatch(r'\[(.+)\]', part)
            if idx_m:
                key = self._eval_expression(idx_m.group(1), local_env)
                if isinstance(obj, dict):
                    obj = obj[key]
                elif isinstance(obj, (list, tuple)):
                    obj = obj[key]
                else:
                    obj = obj[key]
                continue

            # Method call: method(args)
            call_m = re.match(r'^(\w+)\s*\((.*)\)$', part, re.DOTALL)
            if call_m:
                method_name = call_m.group(1)
                args_text = call_m.group(2).strip()
                args = ([self._eval_expression(a.strip(), local_env)
                         for a in self._split_args(args_text)]
                        if args_text else [])

                if isinstance(obj, KSPLObject):
                    obj = obj.call_method(method_name, self, args)
                elif hasattr(obj, method_name):
                    obj = getattr(obj, method_name)(*args)
                else:
                    raise KSPLRuntimeError(
                        f"Method '{method_name}' not found on {obj!r}"
                    )
                continue

            # Property access: .prop
            prop = part.lstrip('.')
            if isinstance(obj, KSPLObject):
                if hasattr(obj, prop):
                    obj = getattr(obj, prop)
                else:
                    raise KSPLRuntimeError(
                        f"Property '{prop}' not found on {obj!r}"
                    )
            elif hasattr(obj, prop):
                obj = getattr(obj, prop)
            elif isinstance(obj, dict) and prop in obj:
                obj = obj[prop]
            else:
                raise KSPLRuntimeError(
                    f"Property '{prop}' not found on {obj!r}"
                )

        return obj

    @staticmethod
    def _split_access(expr: str) -> List[str]:
        """
        Split an access expression into parts.

        Examples:
          'a.b.c'            → ['a', 'b', 'c']
          'a["key"]'         → ['a', '["key"]']
          'a.b["k"].c(x)'    → ['a', 'b', '["k"]', 'c(x)']
          'a.method(x, y)'   → ['a', 'method(x, y)']
        """
        parts: List[str] = []
        current: List[str] = []
        depth = 0
        in_str = False
        str_ch = None
        i = 0

        while i < len(expr):
            ch = expr[i]
            if in_str:
                current.append(ch)
                if ch == str_ch:
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
                current.append(ch)
            elif ch == '[' and depth == 0:
                # Flush anything before the '[' as a part
                if current:
                    parts.append(''.join(current))
                    current = []
                # Now collect the subscript '[...]' including nested brackets
                bracket_buf: List[str] = ['[']
                depth = 1
                i += 1
                while i < len(expr) and depth > 0:
                    c2 = expr[i]
                    if c2 in ('"', "'"):
                        bracket_buf.append(c2)
                        q = c2
                        i += 1
                        while i < len(expr) and expr[i] != q:
                            bracket_buf.append(expr[i])
                            i += 1
                        if i < len(expr):
                            bracket_buf.append(expr[i])
                    elif c2 == '[':
                        depth += 1
                        bracket_buf.append(c2)
                    elif c2 == ']':
                        depth -= 1
                        bracket_buf.append(c2)
                    else:
                        bracket_buf.append(c2)
                    i += 1
                parts.append(''.join(bracket_buf))
                continue
            elif ch == '(' and depth == 0:
                # Method call – include everything up to the matching ')'
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                current.append(ch)
            elif ch == '.' and depth == 0:
                if current:
                    parts.append(''.join(current))
                current = []
            else:
                current.append(ch)
            i += 1

        if current:
            parts.append(''.join(current))

        return parts

    # ---- function / method call --------------------------------------------

    def _eval_call(self, expr: str, local_env: Dict) -> Any:
        """Evaluate a function or method call expression."""
        # Find the outermost call
        paren_idx = expr.index('(')
        fn_expr = expr[:paren_idx].strip()
        args_text = expr[paren_idx + 1:-1].strip()

        args = ([self._eval_expression(a.strip(), local_env)
                 for a in self._split_args(args_text)]
                if args_text else [])

        # Method call: obj.method(...)
        if '.' in fn_expr:
            parts = self._split_access(fn_expr)
            obj = self._eval_expression(parts[0], local_env)
            for part in parts[1:]:
                method_name = part
                if isinstance(obj, KSPLObject):
                    if method_name in obj._klass.methods:
                        return obj.call_method(method_name, self, args)
                    elif hasattr(obj, method_name):
                        return getattr(obj, method_name)(*args)
                    else:
                        raise KSPLRuntimeError(
                            f"Method '{method_name}' not found on {obj!r}"
                        )
                elif hasattr(obj, method_name):
                    attr = getattr(obj, method_name)
                    if callable(attr):
                        return attr(*args)
                    obj = attr
                    continue
                else:
                    raise KSPLRuntimeError(
                        f"Method '{method_name}' not found on {obj!r}"
                    )
            return obj   # shouldn't reach here normally

        # Built-in / global function
        if fn_expr in self.globals and callable(self.globals[fn_expr]):
            return self.globals[fn_expr](*args)

        # Class constructor
        if fn_expr in self.classes:
            return KSPLObject(self.classes[fn_expr], self, args)

        # User-defined function stored in globals
        if fn_expr in self.globals:
            fn = self.globals[fn_expr]
            if callable(fn):
                return fn(*args)

        raise KSPLRuntimeError(f"Function '{fn_expr}' not found.")

    # ---- argument splitting ------------------------------------------------

    @staticmethod
    def _split_args(text: str) -> List[str]:
        """Split comma-separated arguments, respecting nesting and strings."""
        args: List[str] = []
        current: List[str] = []
        depth = 0
        in_str = False
        str_ch = None

        for ch in text:
            if in_str:
                current.append(ch)
                if ch == str_ch:
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
                current.append(ch)
            elif ch in ('(', '[', '{'):
                depth += 1
                current.append(ch)
            elif ch in (')', ']', '}'):
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                args.append(''.join(current))
                current = []
            else:
                current.append(ch)

        if current:
            args.append(''.join(current))

        return args

    # ------------------------------------------------------------------
    # Statement execution
    # ------------------------------------------------------------------

    def execute_statement(self, stmt: Any, local_env: Dict) -> Any:
        """Execute a single parsed statement."""

        # Dict: if / for block
        if isinstance(stmt, dict):
            return self._exec_control(stmt, local_env)

        # Tuple: class / fn definition or ('stmt', raw_line)
        if isinstance(stmt, tuple):
            kind = stmt[0]

            if kind == 'class':
                _, class_name, body = stmt
                klass = self._load_class(class_name, body)
                self.classes[class_name] = klass
                interp = self
                def _make_ctor(cn):
                    def _ctor(*args):
                        return KSPLObject(interp.classes[cn], interp, list(args))
                    return _ctor
                self.globals[class_name] = _make_ctor(class_name)
                return None

            if kind == 'function':
                _, fn_name, params, body = stmt
                interp = self
                # Capture params and body in closure
                def _make_fn(p, b):
                    def _fn(*args):
                        env = dict(zip(p, args))
                        try:
                            return interp.execute_block(b, env)
                        except _ReturnSignal as ret:
                            return ret.value
                    return _fn
                self.globals[fn_name] = _make_fn(params, body)
                return None

            if kind == 'for':
                _, var_name, iter_expr, body = stmt
                iterable = self._eval_expression(iter_expr, local_env)
                result = None
                for item in iterable:
                    local_env[var_name] = item
                    try:
                        result = self.execute_block(body, local_env)
                    except _BreakSignal:
                        break
                    except _ContinueSignal:
                        continue
                    except _ReturnSignal:
                        raise
                return result

            if kind == 'while':
                _, cond_expr, body = stmt
                result = None
                import sys as _sys
                _guard = 0
                _MAX = 100_000
                while self._eval_expression(cond_expr, local_env):
                    _guard += 1
                    if _guard > _MAX:
                        raise KSPLRuntimeError(
                            f"Infinite loop detected (exceeded {_MAX} iterations)"
                        )
                    try:
                        result = self.execute_block(body, local_env)
                    except _BreakSignal:
                        break
                    except _ContinueSignal:
                        continue
                    except _ReturnSignal:
                        raise
                return result

            if kind == 'stmt':
                return self._exec_raw_stmt(stmt[1], local_env)

        # Plain string (shouldn't normally happen but handle gracefully)
        if isinstance(stmt, str):
            return self._exec_raw_stmt(stmt, local_env)

        return None

    def _exec_control(self, stmt: dict, local_env: Dict) -> Any:
        """Execute if/else control flow dict."""
        if stmt['type'] == 'if':
            cond = self._eval_expression(stmt['condition'], local_env)
            if cond:
                return self.execute_block(stmt['then'], local_env)
            for ei_cond, ei_body in stmt.get('elseifs', []):
                if self._eval_expression(ei_cond, local_env):
                    return self.execute_block(ei_body, local_env)
            if stmt.get('else'):
                return self.execute_block(stmt['else'], local_env)
        return None

    def _exec_raw_stmt(self, raw: str, local_env: Dict) -> Any:
        """Execute a raw single-line KSPL statement."""
        stmt = raw.strip()
        if not stmt or stmt.startswith('//'):
            return None

        # return expr
        if stmt.startswith('return '):
            val = self._eval_expression(stmt[7:].strip(), local_env)
            raise _ReturnSignal(val)

        # return (bare)
        if stmt == 'return':
            raise _ReturnSignal(None)

        # break
        if stmt == 'break':
            raise _BreakSignal()

        # continue
        if stmt == 'continue':
            raise _ContinueSignal()

        # let name = expr
        let_m = re.match(r'^let\s+(\w+)\s*=\s*(.+)$', stmt, re.DOTALL)
        if let_m:
            name = let_m.group(1)
            val = self._eval_expression(let_m.group(2).strip(), local_env)
            local_env[name] = val
            return val

        # obj.prop = expr  or  name = expr  (assignment, not equality test)
        assign_m = re.match(r'^([\w\.]+(?:\[.*?\])?)\s*=\s*(.+)$', stmt, re.DOTALL)
        if assign_m and '==' not in stmt and '!=' not in stmt and '>=' not in stmt and '<=' not in stmt:
            target = assign_m.group(1).strip()
            val = self._eval_expression(assign_m.group(2).strip(), local_env)
            self._assign(target, val, local_env)
            return val

        # Everything else: expression / call
        return self._eval_expression(stmt, local_env)

    def _assign(self, target: str, value: Any, local_env: Dict) -> None:
        """Assign value to a (possibly dotted) target."""
        if '.' not in target and '[' not in target:
            # Simple variable
            if target in local_env:
                local_env[target] = value
            else:
                self.globals[target] = value
            return

        # Dotted / indexed assignment: walk to parent, set last
        parts = self._split_access(target)
        obj_name = parts[0]

        if obj_name in local_env:
            obj = local_env[obj_name]
        elif obj_name in self.globals:
            obj = self.globals[obj_name]
        else:
            # Auto-create in globals
            self.globals[obj_name] = None
            obj = None

        for part in parts[1:-1]:
            idx_m = re.fullmatch(r'\[(.+)\]', part)
            if idx_m:
                key = self._eval_expression(idx_m.group(1), local_env)
                obj = obj[key]
            else:
                obj = getattr(obj, part)

        last = parts[-1]
        idx_m = re.fullmatch(r'\[(.+)\]', last)
        if idx_m:
            key = self._eval_expression(idx_m.group(1), local_env)
            obj[key] = value
        else:
            setattr(obj, last, value)

    # ------------------------------------------------------------------
    # Block execution
    # ------------------------------------------------------------------

    def execute_block(self, statements: List, local_env: Dict = None) -> Any:
        """Execute a list of statements / raw strings in a shared env."""
        if local_env is None:
            local_env = {}

        # If the block is a list of raw strings (e.g. method bodies stored
        # as lines), join them and re-parse as a whole so that multi-line
        # constructs (if/else, for, nested classes) are handled correctly.
        if statements and all(isinstance(s, str) for s in statements):
            source = '\n'.join(statements)
            statements = self.parse(source)

        result = None
        for stmt in statements:
            result = self.execute_statement(stmt, local_env)
        return result

    # ------------------------------------------------------------------
    # Top-level run
    # ------------------------------------------------------------------

    def run(self, source: str) -> None:
        """Parse and execute KSPL source code."""
        statements = self.parse(source)

        # Pass 1: register classes and functions
        for stmt in statements:
            if isinstance(stmt, tuple) and stmt[0] in ('class', 'function'):
                self.execute_statement(stmt, self.globals)

        # Pass 2: execute remaining statements
        for stmt in statements:
            if isinstance(stmt, tuple) and stmt[0] in ('class', 'function'):
                continue
            self.execute_statement(stmt, self.globals)
