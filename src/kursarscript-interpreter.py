"""
KursarScript Interpreter - Executes KSPL code
"""
import re
import ast
import sys
from typing import Dict, List, Any, Optional
from .runtime import *

class KSPLRuntimeError(Exception):
    """Runtime errors in KursarScript"""
    pass

class KSPLInterpreter:
    """
    KursarScript Interpreter - Executes KSPL code in virtual environments
    Supports VR integration, virtual economy, and object-oriented programming
    """
    
    def __init__(self, vr_environment=None):
        self.classes = {}
        self.globals = {}
        self.vr_environment = vr_environment
        self.setup_builtins()
        
    def setup_builtins(self):
        """Setup built-in functions and classes for virtual economy"""
        self.globals.update({
            # Core virtual economy functions
            'create_virtucard': create_virtucard,
            'transfer': transfer,
            'VirtualTerminal': VirtualTerminal,
            'Avatar': Avatar,
            'VirtualItem': VirtualItem,
            
            # Built-in functions
            'print': self.builtin_print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            
            # Constants
            'true': True,
            'false': False,
            'null': None,
            
            # VR Environment integration
            'get_avatar': self.get_avatar,
            'create_portal': self.create_portal,
            'get_environment': self.get_environment
        })
        
    def builtin_print(self, *args):
        """KSPL print function with VR environment support"""
        output = ' '.join(str(arg) for arg in args)
        if self.vr_environment:
            self.vr_environment.display_message(output)
        else:
            print(output)
            
    def get_avatar(self, avatar_id):
        """Get avatar from VR environment"""
        if self.vr_environment:
            return self.vr_environment.get_avatar(avatar_id)
        return None
        
    def create_portal(self, from_terminal, to_terminal):
        """Create virtual portal between terminals"""
        if self.vr_environment:
            return self.vr_environment.create_portal(from_terminal, to_terminal)
        return None
        
    def get_environment(self):
        """Get current VR environment"""
        return self.vr_environment

    def parse(self, source: str) -> List[Any]:
        """Parse KSPL source code into executable statements"""
        lines = [ln.strip() for ln in source.split('\n')]
        statements = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if not line or line.startswith('//'):
                i += 1
                continue
                
            # Class definition
            if line.startswith('class '):
                class_stmt, i = self.parse_class(lines, i)
                statements.append(class_stmt)
                
            # Function definition
            elif line.startswith('fn '):
                fn_stmt, i = self.parse_function(lines, i)
                statements.append(fn_stmt)
                
            # Other statements
            else:
                statements.append(('stmt', line))
                i += 1
                
        return statements
        
    def parse_class(self, lines: List[str], start_index: int) -> tuple:
        """Parse class definition"""
        line = lines[start_index]
        class_match = re.match(r'class\s+(\w+)\s*\{', line)
        if not class_match:
            raise KSPLRuntimeError("Invalid class definition")
            
        class_name = class_match.group(1)
        i = start_index + 1
        body = []
        depth = 1
        
        while i < len(lines) and depth > 0:
            current_line = lines[i]
            depth += current_line.count('{')
            depth -= current_line.count('}')
            
            if depth > 0:
                body.append(current_line)
                
            i += 1
            
        return ('class', class_name, body), i
        
    def parse_function(self, lines: List[str], start_index: int) -> tuple:
        """Parse function definition"""
        line = lines[start_index]
        fn_match = re.match(r'fn\s+(\w+)\s*\(([^)]*)\)\s*\{', line)
        if not fn_match:
            raise KSPLRuntimeError("Invalid function definition")
            
        fn_name = fn_match.group(1)
        params = [p.strip() for p in fn_match.group(2).split(',') if p.strip()]
        i = start_index + 1
        body = []
        depth = 1
        
        while i < len(lines) and depth > 0:
            current_line = lines[i]
            depth += current_line.count('{')
            depth -= current_line.count('}')
            
            if depth > 0:
                body.append(current_line)
                
            i += 1
            
        return ('function', fn_name, params, body), i

    def load_class(self, class_name: str, body: List[str]) -> 'KSPLClass':
        """Load class definition from body"""
        methods = {}
        fields = {}
        i = 0
        
        while i < len(body):
            line = body[i].strip()
            
            if line.startswith('fn '):
                # Parse method
                fn_match = re.match(r'fn\s+(\w+)\s*\(([^)]*)\)\s*\{', line)
                if fn_match:
                    method_name = fn_match.group(1)
                    params = [p.strip() for p in fn_match.group(2).split(',') if p.strip()]
                    
                    i += 1
                    method_body = []
                    depth = 1
                    
                    while i < len(body) and depth > 0:
                        current_line = body[i]
                        depth += current_line.count('{')
                        depth -= current_line.count('}')
                        
                        if depth > 0:
                            method_body.append(current_line)
                            
                        i += 1
                        
                    methods[method_name] = {
                        'params': params,
                        'body': method_body
                    }
                else:
                    i += 1
                    
            elif line.startswith('field '):
                # Parse field
                field_match = re.match(r'field\s+(\w+)\s*=\s*(.*)', line)
                if field_match:
                    field_name = field_match.group(1)
                    field_value = self.eval_expression(field_match.group(2), {})
                    fields[field_name] = field_value
                i += 1
                
            else:
                i += 1
                
        return KSPLClass(class_name, methods, fields)

    def eval_expression(self, expr: str, local_env: Dict) -> Any:
        """Evaluate expression in current environment"""
        expr = expr.strip()
        
        # Handle string literals
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
            
        # Handle boolean literals
        if expr == 'true':
            return True
        if expr == 'false':
            return False
        if expr == 'null':
            return None
            
        # Handle numbers
        if re.match(r'^-?\d+$', expr):
            return int(expr)
        if re.match(r'^-?\d+\.\d+$', expr):
            return float(expr)
            
        # Handle variable references
        if expr in local_env:
            return local_env[expr]
        if expr in self.globals:
            return self.globals[expr]
            
        # Handle function calls
        if '(' in expr and expr.endswith(')'):
            return self.eval_function_call(expr, local_env)
            
        # Handle property access
        if '.' in expr:
            parts = expr.split('.')
            obj = self.eval_expression(parts[0], local_env)
            
            for prop in parts[1:]:
                if hasattr(obj, prop):
                    obj = getattr(obj, prop)
                elif isinstance(obj, dict) and prop in obj:
                    obj = obj[prop]
                else:
                    raise KSPLRuntimeError(f"Property '{prop}' not found")
                    
            return obj
            
        # Handle complex expressions with safe eval
        try:
            # Create safe environment
            safe_env = {}
            safe_env.update(self.globals)
            safe_env.update(local_env)
            
            # Use Python's AST for safe evaluation
            node = ast.parse(expr, mode='eval')
            return eval(compile(node, '<expr>', 'eval'), {'__builtins__': {}}, safe_env)
        except:
            raise KSPLRuntimeError(f"Could not evaluate expression: {expr}")

    def eval_function_call(self, expr: str, local_env: Dict) -> Any:
        """Evaluate function call"""
        # Extract function name and arguments
        fn_match = re.match(r'([\w\.]+)\s*\((.*)\)', expr)
        if not fn_match:
            raise KSPLRuntimeError(f"Invalid function call: {expr}")
            
        fn_name = fn_match.group(1)
        args_text = fn_match.group(2).strip()
        
        # Parse arguments
        args = []
        if args_text:
            arg_list = self.split_arguments(args_text)
            for arg in arg_list:
                args.append(self.eval_expression(arg, local_env))
                
        # Handle method calls on objects
        if '.' in fn_name:
            parts = fn_name.split('.')
            obj = self.eval_expression(parts[0], local_env)
            method_name = parts[1]
            
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                return method(*args)
            elif isinstance(obj, KSPLObject) and method_name in obj._klass.methods:
                return obj.call_method(method_name, self, args)
            else:
                raise KSPLRuntimeError(f"Method '{method_name}' not found")
                
        # Handle built-in function calls
        if fn_name in self.globals and callable(self.globals[fn_name]):
            return self.globals[fn_name](*args)
            
        # Handle class constructors
        if fn_name in self.classes:
            klass = self.classes[fn_name]
            return KSPLObject(klass, args)
            
        raise KSPLRuntimeError(f"Function '{fn_name}' not found")

    def split_arguments(self, args_text: str) -> List[str]:
        """Split function arguments respecting commas in nested structures"""
        args = []
        current = []
        depth = 0
        in_string = False
        string_char = None
        i = 0
        
        while i < len(args_text):
            char = args_text[i]
            
            if char in ('"', "'"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
                    string_char = None
                current.append(char)
                i += 1
                continue
                
            if not in_string and char == '(':
                depth += 1
            elif not in_string and char == ')':
                depth -= 1
            elif not in_string and depth == 0 and char == ',':
                args.append(''.join(current).strip())
                current = []
                i += 1
                continue
                
            current.append(char)
            i += 1
            
        if current:
            args.append(''.join(current).strip())
            
        return args

    def execute_statement(self, stmt: str, local_env: Dict = None) -> Any:
        """Execute a single statement"""
        if local_env is None:
            local_env = {}
            
        stmt = stmt.strip()
        if not stmt or stmt.startswith('//'):
            return None
            
        # Variable declaration
        if stmt.startswith('let '):
            let_match = re.match(r'let\s+(\w+)\s*=\s*(.*)', stmt)
            if let_match:
                var_name = let_match.group(1)
                expr = let_match.group(2)
                value = self.eval_expression(expr, local_env)
                local_env[var_name] = value
                return value
                
        # Assignment
        assign_match = re.match(r'([\w\.]+)\s*=\s*(.*)', stmt)
        if assign_match:
            target = assign_match.group(1)
            expr = assign_match.group(2)
            value = self.eval_expression(expr, local_env)
            
            # Handle property assignment
            if '.' in target:
                parts = target.split('.')
                obj_name = parts[0]
                prop_path = parts[1:]
                
                if obj_name in local_env:
                    obj = local_env[obj_name]
                elif obj_name in self.globals:
                    obj = self.globals[obj_name]
                else:
                    raise KSPLRuntimeError(f"Variable '{obj_name}' not found")
                    
                # Navigate to parent object
                current = obj
                for prop in prop_path[:-1]:
                    if hasattr(current, prop):
                        current = getattr(current, prop)
                    elif isinstance(current, dict) and prop in current:
                        current = current[prop]
                    else:
                        raise KSPLRuntimeError(f"Property '{prop}' not found")
                        
                # Set final property
                setattr(current, prop_path[-1], value)
            else:
                # Simple variable assignment
                if target in local_env:
                    local_env[target] = value
                else:
                    self.globals[target] = value
                    
            return value
            
        # Return statement
        if stmt.startswith('return '):
            expr = stmt[7:].strip()
            return self.eval_expression(expr, local_env)
            
        # If statement (simplified)
        if stmt.startswith('if '):
            if_match = re.match(r'if\s+([^{]+)\s*\{', stmt)
            if if_match:
                condition = self.eval_expression(if_match.group(1), local_env)
                # For simplicity, we'll handle basic if statements
                # Full implementation would parse the entire block
                return condition
                
        # Function call or expression
        return self.eval_expression(stmt, local_env)

    def execute_block(self, statements: List[str], local_env: Dict = None) -> Any:
        """Execute a block of statements"""
        if local_env is None:
            local_env = {}
            
        result = None
        for stmt in statements:
            result = self.execute_statement(stmt, local_env)
            if result is not None and isinstance(result, dict) and result.get('__return__'):
                return result['value']
                
        return result

    def run(self, source: str):
        """Execute KSPL source code"""
        statements = self.parse(source)
        
        # First pass: Load classes
        for stmt in statements:
            if stmt[0] == 'class':
                _, class_name, body = stmt
                klass = self.load_class(class_name, body)
                self.classes[class_name] = klass
                
                # Make class available as constructor
                def make_constructor(cls_name):
                    def constructor(*args):
                        return KSPLObject(self.classes[cls_name], args)
                    return constructor
                    
                self.globals[class_name] = make_constructor(class_name)
                
        # Second pass: Execute statements
        for stmt in statements:
            if stmt[0] == 'stmt':
                self.execute_statement(stmt[1])
            elif stmt[0] == 'function':
                # Global functions (simplified)
                _, fn_name, params, body = stmt
                self.globals[fn_name] = lambda *args: self.execute_block(
                    body, 
                    dict(zip(params, args))
                )

class KSPLClass:
    """Represents a KSPL class definition"""
    
    def __init__(self, name: str, methods: Dict, fields: Dict):
        self.name = name
        self.methods = methods
        self.fields = fields

class KSPLObject:
    """Represents an instance of a KSPL class"""
    
    def __init__(self, klass: KSPLClass, args: List = None):
        self._klass = klass
        self.__dict__.update(klass.fields)
        
        # Call constructor if exists
        if 'init' in klass.methods:
            self.call_method('init', None, args or [])
        elif args and len(args) > 0:
            self.name = args[0]
            
    def call_method(self, method_name: str, interpreter: KSPLInterpreter, args: List) -> Any:
        """Call a method on this object"""
        if method_name not in self._klass.methods:
            raise KSPLRuntimeError(f"Method '{method_name}' not found in class '{self._klass.name}'")
            
        method = self._klass.methods[method_name]
        local_env = {'self': self}
        
        # Bind parameters
        for i, param in enumerate(method['params']):
            if i < len(args):
                local_env[param] = args[i]
            else:
                local_env[param] = None
                
        return interpreter.execute_block(method['body'], local_env)
        
    def __repr__(self):
        return f"<{self._klass.name} object at {id(self)}>"
