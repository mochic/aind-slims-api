"""Init package"""

__version__ = "0.1.1"

from aind_slims_api.configuration import AindSlimsApiSettings

config = AindSlimsApiSettings()

from aind_slims_api.core import SlimsClient  # noqa


def testmod(**testmod_kwargs):
    """
    Run doctests for the module, configured to ignore exception details and
    normalize whitespace. Also sets logging level to DEBUG.

    Accepts kwargs to pass to doctest.testmod().

    Add to modules to run doctests when run as a script:
    .. code-block:: text
        if __name__ == "__main__":
            from npc_io import testmod
            testmod()

    """
    import logging
    import doctest

    logging.basicConfig(level=logging.DEBUG)

    _ = testmod_kwargs.setdefault(
        "optionflags", doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    )
    doctest.testmod(**testmod_kwargs)
