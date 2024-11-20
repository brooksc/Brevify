"""Base components for Brevify."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class Component(ABC):
    """Base component class."""
    
    @abstractmethod
    def render(self) -> str:
        """Render the component to HTML."""
        pass

class Element:
    """HTML element helper."""
    
    def __init__(
        self,
        tag: str,
        attrs: Optional[Dict[str, str]] = None,
        children: Optional[List[Union[str, 'Element']]] = None
    ):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = children or []

    def render(self) -> str:
        """Render the element to HTML."""
        # Build attributes string
        attrs = ' '.join([f'{k}="{v}"' for k, v in self.attrs.items()])
        attrs = f' {attrs}' if attrs else ''
        
        # Render children
        children = ''.join([
            child.render() if isinstance(child, Element) else str(child)
            for child in self.children
        ])
        
        # Return formatted HTML
        return f'<{self.tag}{attrs}>{children}</{self.tag}>'

# Common HTML elements
def Div(*args, **kwargs) -> Element:
    return Element('div', *args, **kwargs)

def Span(*args, **kwargs) -> Element:
    return Element('span', *args, **kwargs)

def H1(*args, **kwargs) -> Element:
    return Element('h1', *args, **kwargs)

def H2(*args, **kwargs) -> Element:
    return Element('h2', *args, **kwargs)

def H3(*args, **kwargs) -> Element:
    return Element('h3', *args, **kwargs)

def P(*args, **kwargs) -> Element:
    return Element('p', *args, **kwargs)

def A(*args, **kwargs) -> Element:
    return Element('a', *args, **kwargs)

def Img(*args, **kwargs) -> Element:
    return Element('img', *args, **kwargs)

def Button(*args, **kwargs) -> Element:
    return Element('button', *args, **kwargs)

def Form(*args, **kwargs) -> Element:
    return Element('form', *args, **kwargs)

def Input(*args, **kwargs) -> Element:
    return Element('input', *args, **kwargs)
