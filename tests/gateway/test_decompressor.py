import zlib

from nextcore.gateway import Decompressor


def test_decompress():
    decompressor = Decompressor()

    content = b"Hello, world!"
    compressed = zlib.compress(content) + Decompressor.ZLIB_SUFFIX

    assert decompressor.decompress(compressed) == content
