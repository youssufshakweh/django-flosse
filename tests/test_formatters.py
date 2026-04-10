import json

import pytest

from django_flosse.events import SSEEvent
from django_flosse.formatters import to_sse


class TestToSSEPlainString:
    def test_string_becomes_data_event(self):
        assert to_sse("hello") == SSEEvent(data="hello").encode()

    def test_empty_string_produces_blank_event(self):
        # "".splitlines() == [] → no data: lines, just the blank terminator
        wire = to_sse("")
        assert wire == "\n"

    def test_multiline_string(self):
        wire = to_sse("a\nb")
        assert "data: a\n" in wire
        assert "data: b\n" in wire


class TestToSSETuple:
    def test_two_tuple_event_and_data(self):
        wire = to_sse(("update", {"count": 1}))
        assert "event: update\n" in wire
        assert '"count": 1' in wire

    def test_two_tuple_with_string_data(self):
        wire = to_sse(("msg", "hello"))
        assert "event: msg\n" in wire
        assert "data: hello\n" in wire

    def test_three_tuple_includes_id(self):
        wire = to_sse(("update", "payload", "id-99"))
        assert "event: update\n" in wire
        assert "id: id-99\n" in wire
        assert "data: payload\n" in wire

    def test_one_tuple_raises_value_error(self):
        with pytest.raises(ValueError, match="Tuple yields must be"):
            to_sse(("only_one",))

    def test_four_tuple_raises_value_error(self):
        with pytest.raises(ValueError, match="Tuple yields must be"):
            to_sse(("a", "b", "c", "d"))


class TestToSSEDict:
    def test_dict_with_data_key_maps_to_sse_event(self):
        wire = to_sse({"data": "hi", "event": "greet"})
        assert "event: greet\n" in wire
        assert "data: hi\n" in wire

    def test_dict_with_data_and_id(self):
        wire = to_sse({"data": "x", "id": "7"})
        assert "id: 7\n" in wire

    def test_dict_with_data_and_retry(self):
        wire = to_sse({"data": "x", "retry": 2000})
        assert "retry: 2000\n" in wire

    def test_dict_without_data_key_whole_dict_is_payload(self):
        wire = to_sse({"foo": "bar"})
        parsed = json.loads(wire.split("data: ")[1].strip())
        assert parsed == {"foo": "bar"}

    def test_empty_dict_without_data_key(self):
        wire = to_sse({})
        assert "data: {}" in wire


class TestToSSESSEEvent:
    def test_sse_event_returned_as_is(self):
        ev = SSEEvent(data="direct", event="test")
        assert to_sse(ev) == ev.encode()

    def test_sse_event_with_all_fields(self):
        ev = SSEEvent(data={"k": "v"}, event="upd", id="1", retry=1000)
        assert to_sse(ev) == ev.encode()


class TestToSSEFallback:
    def test_integer_fallback_to_str(self):
        wire = to_sse(42)
        assert "data: 42\n" in wire

    def test_float_fallback_to_str(self):
        wire = to_sse(3.14)
        assert "data: 3.14\n" in wire

    def test_bool_fallback_to_str(self):
        wire = to_sse(True)
        assert "data: True\n" in wire

    def test_none_fallback_to_str(self):
        wire = to_sse(None)
        assert "data: None\n" in wire
