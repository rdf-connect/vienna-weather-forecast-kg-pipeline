from dataclasses import dataclass
from logging import getLogger, Logger
from transformers import pipeline
from rdflib import Graph, Literal

from rdfc_runner import Processor, Reader, Writer


# --- Type Definitions ---
@dataclass
class TranslationArgs:
    reader: Reader
    writer: Writer
    model: str
    source_language: str
    target_language: str


# --- Processor Implementation ---
class TranslationProcessor(Processor[TranslationArgs]):
    logger: Logger = getLogger('rdfc.TranslationProcessor')

    def __init__(self, args: TranslationArgs):
        super().__init__(args)
        self.translator = None
        self.logger.debug(msg="Created TranslationProcessor with args: {}".format(args))

    async def init(self) -> None:
        """This is the first function that is called (and awaited) when creating a processor.
        This is the perfect location to start things like database connections."""
        self.logger.debug("Initializing TranslationProcessor with args: {}".format(self.args))
        self.translator = pipeline(task='translation', model=self.args.model)

    async def transform(self) -> None:
        """Function to start reading channels.
        This function is called for each processor before `produce` is called.
        Listen to the incoming stream, log them, and push them to the outgoing stream."""
        async for data in self.args.reader.strings():
            self.logger.debug(f"Received data for translation:\n{data}")
            # Parse all triples with rdflib.
            g = Graph()
            g.parse(data=data, format="turtle")

            # Collect new translated triples to add to the graph.
            new_triples = []
            for s, p, o in g:
                if isinstance(o, Literal) and o.language == self.args.source_language:
                    # Translate the literal value
                    translated_text = self.translator(str(o))[0]['translation_text']
                    self.logger.debug(f"Translating '{o}' to '{translated_text}'")

                    # Create a new literal with @en language tag
                    new_literal = Literal(translated_text, lang=self.args.target_language)
                    new_triples.append((s, p, new_literal))

            # Add new triples to the graph.
            for triple in new_triples:
                g.add(triple)

            # Serialize the updated graph back to Turtle format.
            serialized_data = g.serialize(format="turtle")

            # Output the message to the writer
            await self.args.writer.string(serialized_data)

        # Close the writer after processing all messages
        await self.args.writer.close()
        self.logger.debug("done reading so closed writer.")

    async def produce(self) -> None:
        """Function to start the production of data, starting the pipeline.
        This function is called after all processors are completely set up."""
        pass
