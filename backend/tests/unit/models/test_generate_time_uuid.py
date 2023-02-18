from oasst_backend.models.journal import generate_time_uuid


def test_uuid_is_not_versioned():
    """The UUID should not have a version number."""
    uuid = generate_time_uuid()
    assert uuid.version is None


def test_uuid_is_orderable():
    uuid1 = generate_time_uuid(0, 12345)
    uuid2 = generate_time_uuid(0, 12345)
    assert uuid1 < uuid2


def test_uuid_is_unique():
    uuid1 = generate_time_uuid(0, 12345)
    uuid2 = generate_time_uuid(0, 12345)

    assert uuid1 != uuid2


def test_uuid_orders_by_creation_time():
    """Not by clock sequence, which is only used to break ties between UUIDs created at the same time."""
    uuid1 = generate_time_uuid(0, 5000)
    uuid2 = generate_time_uuid(0, 1)

    assert uuid1 < uuid2


def test_uuid_retains_node():
    """The node should be retained in the generated UUID."""
    uuid = generate_time_uuid(node=0x123456789ABC)

    assert uuid.node == 0x123456789ABC
