import json

from django_flosse.events import SSEEvent


class TestSSEEventEncode:
    def test_plain_string_data(self):
        assert SSEEvent(data="hello").encode() == "data: hello\n\n"

    def test_dict_data_is_serialised_to_json(self):
        wire = SSEEvent(data={"x": 1}).encode()
        line = [l for l in wire.splitlines() if l.startswith("data:")][0]  # noqa
        assert json.loads(line[len("data: ") :]) == {"x": 1}

    def test_list_data_is_serialised_to_json(self):
        wire = SSEEvent(data=[1, 2, 3]).encode()
        line = [l for l in wire.splitlines() if l.startswith("data:")][0]  # noqa
        assert json.loads(line[len("data: ") :]) == [1, 2, 3]

    def test_named_event_field(self):
        wire = SSEEvent(data="ping", event="heartbeat").encode()
        assert "event: heartbeat\n" in wire
        assert "data: ping\n" in wire

    def test_id_field(self):
        wire = SSEEvent(data="x", id="42").encode()
        assert "id: 42\n" in wire

    def test_retry_field(self):
        wire = SSEEvent(data="x", retry=3000).encode()
        assert "retry: 3000\n" in wire

    def test_all_fields_present(self):
        wire = SSEEvent(data="x", event="update", id="1", retry=5000).encode()
        assert "event: update\n" in wire
        assert "id: 1\n" in wire
        assert "retry: 5000\n" in wire
        assert "data: x\n" in wire

    def test_multiline_data_each_line_prefixed(self):
        wire = SSEEvent(data="line1\nline2\nline3").encode()
        assert "data: line1\n" in wire
        assert "data: line2\n" in wire
        assert "data: line3\n" in wire

    def test_always_ends_with_double_newline(self):
        assert SSEEvent(data="test").encode().endswith("\n\n")

    def test_integer_data_is_coerced_to_json(self):
        wire = SSEEvent(data=42).encode()
        assert "data: 42\n" in wire

    def test_none_data_is_serialised(self):
        wire = SSEEvent(data=None).encode()
        assert "data: null\n" in wire

    def test_unicode_data_preserved(self):
        wire = SSEEvent(data="مرحبا").encode()
        assert "مرحبا" in wire
