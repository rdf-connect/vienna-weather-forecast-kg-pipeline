import logging
from unittest.mock import AsyncMock

import pytest

import rdfc_translation_processor.processor as processor


class DummyReader:
    """A dummy async reader that yields a sequence of strings."""

    def __init__(self, messages):
        self._messages = messages

    async def strings(self):
        for msg in self._messages:
            yield msg


@pytest.mark.asyncio
async def test_translation_process(caplog):
    reader = DummyReader(["<http://ex.org/instance> <http://ex.org/prop> \"hallo welt\"@de."])
    writer = AsyncMock()

    args = processor.TranslationArgs(
        reader=reader,
        writer=writer,
        model="Helsinki-NLP/opus-mt-de-en",
        source_language="de",
        target_language="en"
    )
    proc = processor.TranslationProcessor(args)

    # Mock translator to always return "hello world"
    proc.translator = lambda text: [{"translation_text": "hello world"}]

    caplog.set_level(logging.DEBUG)

    await proc.transform()

    actual_calls = [call.args for call in writer.string.await_args_list]
    assert any("hello world" in str(args).lower() for args in actual_calls)

    writer.close.assert_awaited_once()
    assert "done reading so closed writer." in caplog.text
