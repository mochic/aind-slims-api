"""Common types for the SLIMS API.
"""

from typing import Literal

# List of slims tables manually accessed, there are many more
SLIMSTABLES = Literal[
    "Attachment",
    "Project",
    "Content",
    "ContentEvent",
    "Unit",
    "Result",
    "Test",
    "User",
    "Groups",
    "Instrument",
    "Unit",
]
