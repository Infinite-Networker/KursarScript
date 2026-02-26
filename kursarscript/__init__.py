"""
KursarScript Programming Language (KSPL)
A virtual reality and digital user-friendly programming language
designed for virtual environments and digital economies.
"""

__version__ = "1.0.0"
__author__ = "KursarScript Team"

from .interpreter import KSPLInterpreter, KSPLRuntimeError
from .compiler import KSPLCompiler, KSPLCompileError
from .runtime import VirtuCard, VirtualTerminal, Avatar, VirtualItem, create_virtucard, transfer

__all__ = [
    # Interpreter
    'KSPLInterpreter',
    'KSPLRuntimeError',
    # Compiler
    'KSPLCompiler',
    'KSPLCompileError',
    # Runtime types
    'VirtuCard',
    'VirtualTerminal',
    'Avatar',
    'VirtualItem',
    # Runtime helpers
    'create_virtucard',
    'transfer',
]
