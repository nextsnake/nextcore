from nextcore.http.route import Route


def test_same_no_changes():
    r1 = Route("GET", "/example")
    r2 = Route("GET", "/example")

    assert r1.bucket == r2.bucket, "Both should have the same bucket"


def test_ignore_non_major_params():
    r1 = Route("GET", "/example/{non_major}", non_major=False)
    r2 = Route("GET", "/example/{non_major}", non_major=True)

    assert r1.bucket == r2.bucket, "Did not ignore non-major params"


def test_major_params():
    r1 = Route("GET", "/example/{guild_id}", guild_id=5)
    r2 = Route("GET", "/example/{guild_id}", guild_id=4)

    assert r1.bucket != r2.bucket, "Ignored major params"
