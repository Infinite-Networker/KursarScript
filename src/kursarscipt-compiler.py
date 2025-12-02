"""
KursarScript Compiler - Compiles KSPL code to executable format
"""
import re
import ast
from typing import Dict, List, Any, Tuple

class KSPLCompileError(Exception):
    """Compilation errors in KursarScript"""
    pass

class KSPLCompiler:
    """Compiles KursarScript source code to executable format"""
    
    def __init__(self):
        self.classes = {}
        self.symbol_table = {}
        self.current_scope = "global"
        
    def tokenize(self, source: str) -> List[Dict]:
        """Convert source code into tokens"""
        tokens = []
        lines = source.split('\n')
        line_num = 1
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                line_num += 1
                continue
                
            # Class definition
            class_match = re.match(r'class\s+(\w+)\s*\{', line)
            if class_match:
                tokens.append({
                    'type': 'CLASS_DEF',
                    'value': class_match.group(1),
                    'line': line_num
                })
                continue
                
            # Function definition
            fn_match = re.match(r'fn\s+(\w+)\s*\(([^)]*)\)\s*\{', line)
            if fn_match:
                params = [p.strip() for p in fn_match.group(2).split(',') if p.strip()]
                tokens.append({
                    'type': 'FN_DEF',
                    'value': fn_match.group(1),
                    'params': params,
                    'line': line_num
                })
                continue
                
            # Field definition
            field_match = re.match(r'field\s+(\w+)\s*=\s*(.*)', line)
            if field_match:
                tokens.append({
                    'type': 'FIELD_DEF',
                    'value': field_match.group(1),
                    'expr': field_match.group(2),
                    'line': line_num
                })
                continue
                
            # Variable declaration
            let_match = re.match(r'let\s+(\w+)\s*=\s*(.*)', line)
            if let_match:
                tokens.append({
                    'type': 'LET_DEF',
                    'value': let_match.group(1),
                    'expr': let_match.group(2),
                    'line': line_num
                })
                continue
                
            # Assignment
            assign_match = re.match(r'([\w\.]+)\s*=\s*(.*)', line)
            if assign_match:
                tokens.append({
                    'type': 'ASSIGNMENT',
                    'target': assign_match.group(1),
                    'expr': assign_match.group(2),
                    'line': line_num
                })
                continue
                
            # Return statement
            return_match = re.match(r'return\s+(.*)', line)
            if return_match:
                tokens.append({
                    'type': 'RETURN',
                    'expr': return_match.group(1),
                    'line': line_num
                })
                continue
                
            # If statement
            if_match = re.match(r'if\s+(.+)\s*\{', line)
            if if_match:
                tokens.append({
                    'type': 'IF_STMT',
                    'condition': if_match.group(1),
                    'line': line_num
                })
                continue
                
            # Else statement
            elif line.strip() == '} else {':
                tokens.append({
                    'type': 'ELSE_STMT',
                    'line': line_num
                })
                continue
                
            # Method call or expression
            if '(' in line and line.endswith(')'):
                tokens.append({
                    'type': 'EXPRESSION',
                    'value': line,
                    'line': line_num
                })
            else:
                tokens.append({
                    'type': 'STATEMENT',
                    'value': line,
                    'line': line_num
                })
                
            line_num += 1
            
        return tokens
    
    def parse(self, tokens: List[Dict]) -> Dict[str, Any]:
        """Parse tokens into AST"""
        ast = {
            'classes': {},
            'global_code': [],
            'imports': []
        }
        
        i = 0
        current_class = None
        current_method = None
        
        while i < len(tokens):
            token = tokens[i]
            
            if token['type'] == 'CLASS_DEF':
                class_name = token['value']
                current_class = {
                    'name': class_name,
                    'methods': {},
                    'fields': {},
                    'line': token['line']
                }
                ast['classes'][class_name] = current_class
                current_method = None
                
            elif token['type'] == 'FN_DEF' and current_class:
                method_name = token['value']
                current_method = {
                    'name': method_name,
                    'params': token['params'],
                    'body': [],
                    'line': token['line']
                }
                current_class['methods'][method_name] = current_method
                
            elif token['type'] == 'FIELD_DEF' and current_class:
                field_name = token['value']
                current_class['fields'][field_name] = {
                    'expr': token['expr'],
                    'line': token['line']
                }
                
            elif token['type'] in ['LET_DEF', 'ASSIGNMENT', 'EXPRESSION', 'STATEMENT']:
                if current_method:
                    current_method['body'].append(token)
                else:
                    ast['global_code'].append(token)
                    
            elif token['type'] == 'RETURN':
                if current_method:
                    current_method['body'].append(token)
                else:
                    raise KSPLCompileError("Return outside of method")
                    
            elif token['type'] == 'IF_STMT':
                if_stmt = {
                    'type': 'IF',
                    'condition': token['condition'],
                    'then_branch': [],
                    'else_branch': [],
                    'line': token['line']
                }
                
                # Parse then branch
                i += 1
                while i < len(tokens) and tokens[i]['type'] not in ['ELSE_STMT', 'BRACE_CLOSE']:
                    if_stmt['then_branch'].append(tokens[i])
                    i += 1
                    
                # Parse else branch if exists
                if i < len(tokens) and tokens[i]['type'] == 'ELSE_STMT':
                    i += 1
                    while i < len(tokens) and tokens[i]['type'] != 'BRACE_CLOSE':
                        if_stmt['else_branch'].append(tokens[i])
                        i += 1
                        
                if current_method:
                    current_method['body'].append(if_stmt)
                else:
                    ast['global_code'].append(if_stmt)
                    
            i += 1
            
        return ast
    
    def compile(self, source: str) -> Dict[str, Any]:
        """Compile KSPL source code to executable format"""
        tokens = self.tokenize(source)
        ast = self.parse(tokens)
        return self.generate_code(ast)
    
    def generate_code(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executable code from AST"""
        executable = {
            'classes': {},
            'global_instructions': [],
            'metadata': {
                'version': '1.0',
                'compiler': 'KSPL Compiler'
            }
        }
        
        # Compile classes
        for class_name, class_info in ast['classes'].items():
            executable_class = {
                'name': class_name,
                'methods': {},
                'fields': class_info['fields'],
                'constructor': None
            }
            
            # Compile methods
            for method_name, method_info in class_info['methods'].items():
                executable_method = {
                    'params': method_info['params'],
                    'instructions': []
                }
                
                # Compile method body
                for stmt in method_info['body']:
                    if stmt['type'] == 'LET_DEF':
                        executable_method['instructions'].append({
                            'op': 'STORE',
                            'target': stmt['value'],
                            'expr': stmt['expr']
                        })
                    elif stmt['type'] == 'ASSIGNMENT':
                        executable_method['instructions'].append({
                            'op': 'ASSIGN',
                            'target': stmt['target'],
                            'expr': stmt['expr']
                        })
                    elif stmt['type'] == 'RETURN':
                        executable_method['instructions'].append({
                            'op': 'RETURN',
                            'expr': stmt['expr']
                        })
                    elif stmt['type'] == 'EXPRESSION':
                        executable_method['instructions'].append({
                            'op': 'EXEC',
                            'expr': stmt['value']
                        })
                        
                executable_class['methods'][method_name] = executable_method
                
                if method_name == 'init':
                    executable_class['constructor'] = executable_method
                    
            executable['classes'][class_name] = executable_class
            
        # Compile global code
        for stmt in ast['global_code']:
            if stmt['type'] == 'LET_DEF':
                executable['global_instructions'].append({
                    'op': 'STORE_GLOBAL',
                    'target': stmt['value'],
                    'expr': stmt['expr']
                })
            elif stmt['type'] == 'ASSIGNMENT':
                executable['global_instructions'].append({
                    'op': 'ASSIGN_GLOBAL',
                    'target': stmt['target'],
                    'expr': stmt['expr']
                })
            elif stmt['type'] == 'EXPRESSION':
                executable['global_instructions'].append({
                    'op': 'EXEC_GLOBAL',
                    'expr': stmt['value']
                })
                
        return executable
    
    def optimize(self, executable: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations to the executable code"""
        # Simple constant propagation and dead code elimination
        optimized = executable.copy()
        
        # TODO: Implement optimizations
        # - Constant folding
        # - Dead code elimination  
        # - Method inlining
        
        return optimized
