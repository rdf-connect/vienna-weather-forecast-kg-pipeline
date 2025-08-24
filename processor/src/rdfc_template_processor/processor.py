import logging
from dataclasses import dataclass
from logging import getLogger, Logger

from rdfc_runner import Processor, ProcessorArgs, Reader, Writer


# --- Type Definitions ---
@dataclass
class TemplateArgs(ProcessorArgs):
    reader: Reader
    writer: Writer


# --- Processor Implementation ---
class TemplateProcessor(Processor[TemplateArgs]):
    logger: Logger = getLogger('rdfc.TemplateProcessor')

    def __init__(self, args: TemplateArgs):
        super().__init__(args)
        self.logger.debug(msg="Created TemplateProcessor with args: {}".format(args))

    async def init(self) -> None:
        """This is the first function that is called (and awaited) when creating a processor.
        This is the perfect location to start things like database connections."""
        self.logger.debug("Initializing TemplateProcessor with args: {}", self.args)

    async def transform(self) -> None:
        """Function to start reading channels.
        This function is called for each processor before `produce` is called.
        Listen to the incoming stream, log them, and push them to the outgoing stream."""
        async for msg in self.args.reader.strings():
            # Log the incoming message
            self.logger.log(msg=msg, level=logging.INFO)

            # Echo the message to the writer
            if self.args.writer:
                await self.args.writer.string(msg)

        # Close the writer after processing all messages
        if self.args.writer:
            await self.args.writer.close()
        self.logger.debug("done reading so closed writer.")

    async def produce(self) -> None:
        """Function to start the production of data, starting the pipeline.
        This function is called after all processors are completely set up."""
        pass
