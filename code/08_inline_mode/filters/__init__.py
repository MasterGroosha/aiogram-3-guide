from .text_has_link import HasLinkFilter
from .check_via_bot import ViaBotFilter

# Делаем так, чтобы затем просто импортировать
# from filters import HasLinkFilter
__all__ = [
    "HasLinkFilter",
    "ViaBotFilter"
]
