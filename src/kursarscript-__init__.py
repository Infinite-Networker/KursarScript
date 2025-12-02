"""
KursarScript Programming Language (KSPL)
A virtual reality and digital user-friendly programming language 
designed for virtual environments and digital economies.
"""
__version__ = "1.0.0"
__author__ = "KursarScript Team"

from .interpreter import KSPLInterpreter, KSPLRuntimeError
from .compiler import KSPLCompiler
from .runtime import VirtuCard, VirtualTerminal, Avatar, VirtualItem

__all__ = [
    'KSPLInterpreter', 
    'KSPLRuntimeError', 
    'KSPLCompiler',
    'VirtuCard', 
    'VirtualTerminal', 
    'Avatar', 
    'VirtualItem'
]
