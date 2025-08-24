import logging
from unittest.mock import AsyncMock

import pytest

import rdfc_template_processor.processor as processor


class DummyReader:
    """A dummy async reader that yields a sequence of strings."""

    def __init__(self, messages):
        self._messages = messages

    async def strings(self):
        for msg in self._messages:
            yield msg


@pytest.mark.asyncio
async def test_transform_writes_and_closes_writer(caplog):
    messages = ["hello", "world"]
    reader = DummyReader(messages)
    writer = AsyncMock()

    args = processor.TemplateArgs(reader=reader, writer=writer)
    proc = processor.TemplateProcessor(args)

    caplog.set_level(logging.DEBUG)

    await proc.transform()

    # Writer should be called with each message
    expected_calls = [((msg,),) for msg in messages]
    actual_calls = [call.args for call in writer.string.await_args_list]
    assert actual_calls == [(msg,) for msg in messages]

    # Writer.close should be called once
    writer.close.assert_awaited_once()

    # Debug log at end should appear
    assert "done reading so closed writer." in caplog.text


@pytest.mark.asyncio
async def test_transform_without_writer(caplog):
    messages = ["foo", "bar"]
    reader = DummyReader(messages)

    args = processor.TemplateArgs(reader=reader, writer=None)
    proc = processor.TemplateProcessor(args)

    caplog.set_level(logging.INFO)

    # Should not raise even if writer is None
    await proc.transform()

    # Should log incoming messages at INFO level
    for msg in messages:
        assert msg in caplog.text
