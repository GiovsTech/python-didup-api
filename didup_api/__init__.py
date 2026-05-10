"""
didup_api: A python library for Argo DidUP API
"""

__version__ = "0.1.0"
__author__ = "GiovsTechs"
__license__ = "GPLv3"

from .Interface import Argo
from .Client import Client

__all__ = [
    "Argo",
    "Client",
]
