# vienna-weather-forecast-kg-pipeline

RDF-Connect pipeline to produce a knowledge graph from Vienna’s weather forecast.  
This repository provides **incremental solutions** for the hands-on tutorial at 
[SEMANTiCS 2025](https://2025-eu.semantics.cc/page/cfp_ws):  
👉 [Tutorial Website](https://rdf-connect.github.io/Tutorial-SEMANTiCS2025/) & [Tutorial Slides](https://rdf-connect.github.io/Tutorial-SEMANTiCS2025/slides)

🌐 [RDF-Connect Homepage](https://rdf-connect.github.io) | [RDF-Connect GitHub](https://github.com/rdf-connect)

---

## RDF-Connect Tutorial

This tutorial walks you step by step through building a **provenance-aware, streaming RDF pipeline** using the language-agnostic framework **RDF-Connect**.  

The use case: Producing and publishing a queryable **knowledge graph** from Vienna's weather forecast data extracted from the **GeoSphere Austria JSON API**.

You will:

- Set up an RDF-Connect environment  
- Configure pipeline components  
- Implement processors in multiple programming languages  
- Run the pipeline end-to-end

By the end, you will have:

- A working RDF-Connect pipeline for real-world data  
- A clear understanding of how to integrate heterogeneous processors across execution environments  
- Practical experience with implementing RDF-Connect processors

The tutorial is designed for all experience levels, and you can follow along at your own pace.  
Each **task** builds on the previous one, and each solution is available in a dedicated **branch** of this repository (`task-1`, `task-2`, ...).  
You can use these branches to verify your work, catch up if stuck, or compare with the reference solution.

The solution for the **entire pipeline** is available in the [**`task-7` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-7).

---

## Getting Started

The recommended starting point is to **fork and clone this repository**, then switch to the `main` branch.

### Prerequisites

Make sure the following are installed:

- **Node.js ≥16**  
- **Java ≥17**  
  - Gradle ≥8.5 (you can also manually download the JARs and put them in `pipeline/build/plugins/`)
- **Python ≥3.8** (we recommend 3.13 for Part 2)  
  - Hatch (for managing Python environments and dependencies)
  - uv (for managing Python packages)

**If you do not want to install these tools locally**, we have provided a **Dockerfile** that sets up an environment with all software installed.
You can build and run it with:

```bash
# Start the Docker Compose environment containing the devbox and Virtuoso
cd pipeline/resources
docker compose up -d

# Access the devbox container
docker compose exec devbox bash
cd pipeline/
# You can now run commands like `npm install` or `npx rdfc pipeline.ttl` inside the container

# Or directly run the commands
docker compose exec devbox bash -c "cd pipeline && npm install"
docker compose exec devbox bash -c "cd pipeline && npx rdfc pipeline.ttl"
```

The pipeline will store data in a **Virtuoso triple store**.  
We recommend running Virtuoso via **Docker + Docker Compose**, so install both if you plan to follow that setup.
You can also use your own Virtuoso instance if you prefer.

---

## Tasks

### Part 1: Assembling the Pipeline

#### Task 0: Set up the project structure for the pipeline

In this step, you’ll prepare the project with an empty pipeline config.  
You may start from our provided project structure (recommended) or consult the [example pipelines](https://github.com/rdf-connect/example-pipelines/tree/main/java/hello-world) repository for inspiration.

**Steps:**

- [x] Create a `pipeline/` directory (all Part 1 work happens here).  
- [x] Inside `pipeline/`, create:
  - `pipeline.ttl` (pipeline configuration)  
  - `README.md` (documentation)  
  - `package.json` (via `npm init` or manually)  
  - `.gitignore` (exclude `node_modules/` etc.)  
- [x] Install the orchestrator:  
  ```bash
  npm install @rdfc/orchestrator-js
  ```  
- [x] Initialize the RDF-Connect pipeline in `pipeline.ttl`:
  - Add RDF namespaces (e.g., `rdfc`, `owl`, `ex`)
  - Declare the pipeline with the following triple:
    ```turtle
    <> a rdfc:Pipeline.
    ```

**Expected structure:**

```
├── pipeline/           # Part 1 work lives here
│   ├── node_modules/   
│   ├── .gitignore      
│   ├── package.json    
│   ├── pipeline.ttl    
│   └── README.md       
├── processor/          # Custom processor (Part 2)
└── README.md           # Tutorial instructions
```

✅ The solution for this task is in the [**`main` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/main).


#### Task 1: Fetch weather data from the GeoSphere Austria API

Configure the pipeline to fetch weather data from GeoSphere Austria (station `11035`, near the SEMANTiCS venue) in JSON format:

**API endpoint**:  
- <https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min?parameters=TL,RR&station_ids=11035>

**Processors to add:**

- `rdfc:HttpFetch` – HTTP processor implemented in TypeScript (implementation & documentation at [@rdfc/http-utils-processor-ts](https://github.com/rdf-connect/http-utils-processor-ts))
- `rdfc:LogProcessorJs` – Processor that logs to RDF-Connect logging system any input stream, implemented in TypeScript (implementation & documentation at [@rdfc/log-processor-ts](https://github.com/rdf-connect/log-processor-ts))

**Runners to add:**

- `rdfc:NodeRunner` – run JavaScript processors (implementation & documentation at [@rdfc/js-runner](https://github.com/rdf-connect/js-runner))

**Steps:**

- [x] Add an `rdfc:HttpFetch` processor instance
  - Install the processor
    ```bash
    npm install @rdfc/http-utils-processor-ts
    ```
  - Import semantic definition via `owl:imports`  
    ```turtle
    ### Import runners and processors
    <> owl:imports <./node_modules/@rdfc/http-utils-processor-ts/processors.ttl>.
    ```  
  - Define a channel for the fetched JSON data
    ```turtle
    ### Define the channels
    <json> a rdfc:Reader, rdfc:Writer.
    ```
  - Configure it to fetch from the API endpoint  
    ```turtle
    ### Define the processors
    # Processor to fetch data from a JSON API
    <fetcher> a rdfc:HttpFetch;
        rdfc:url <https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min?parameters=TL,RR&station_ids=11035>;
        rdfc:writer <json>.
    ```
- [x] Add an `rdfc:NodeRunner` Node.js runner instance
  - Install the runner
    ```bash
    npm install @rdfc/js-runner
    ```
  - Import its semantic definition  
    ```turtle
    ### Import runners and processors
    <> owl:imports <./node_modules/@rdfc/js-runner/index.ttl>.
    ```
  - Define it as part of the pipeline and link the `rdfc:HttpFetch` processor instance to it using the `rdfc:consistsOf`,  `rdfc:instantiates` and `rdfc:processor` properties
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
     rdfc:consistsOf [
         rdfc:instantiates rdfc:NodeRunner;
         rdfc:processor <fetcher>;
     ].
    ```
- [x] Add a `rdfc:LogProcessorJs` processor instance
  - Install the processor
    ```bash
    npm install @rdfc/log-processor-ts
    ```
  - Import its semantic definition
    ```turtle
    ### Import runners and processors
    <> owl:imports <./node_modules/@rdfc/log-processor-ts/processor.ttl> .
    ```
  - Create an instance and configure it with e.g., log level: `info`, label: `output` and link it to the output channel of `rdfc:HttpFetch`
    ```turtle
    ### Define the processors
    # Processor to log the output
    <logger> a rdfc:LogProcessorJs;
          rdfc:reader <json>;
          rdfc:level "info";
          rdfc:label "output".
    ``` 
  - Attach it to the `rdfc:NodeRunner`
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>;
       ].
    ```
- [x] Run the pipeline:  
  ```bash
  npx rdfc pipeline.ttl
  # or with debug logging:
  LOG_LEVEL=debug npx rdfc pipeline.ttl
  ```

✅ Complete solution available in [**`task-1` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-1).


#### Task 2: Convert the weather data from JSON to RDF

You will now convert the JSON stream into RDF using **[RML](https://rml.io/)** with the help of the `rdfc:RmlMapper` processor.

To help you with this, we prepared an [RML mapping file](./pipeline/resources/mapping.rml.ttl) for you that you can use to convert the JSON data to RDF.

**Processors to add:**

- `rdfc:GlobRead` – read mapping file from disk, implemented in TypeScript (implementation & documentation at [@rdfc/file-utils-processors-ts](https://github.com/rdf-connect/file-utils-processors-ts))  
- `rdfc:RmlMapper` – convert heterogeneous data to RDF, implemented in Java (implementation & documentation at [rml-processor-jvm](https://github.com/rdf-connect/rml-processor-jvm)). Internally, it uses the [RMLMapper engine](https://github.com/RMLio/rmlmapper-java)

**Runners to add:**

- `rdfc:JvmRunner` – run Java processors (implementation & documentation at [rdf-connect/jvm-runner](https://github.com/rdf-connect/jvm-runner))  

**Steps:**

- [x] Use `rdfc:GlobRead` to read the RML mapping file
  - Install this Node.js processor
    ```bash
    npm install @rdfc/file-utils-processors-ts
    ```
  - Import its semantic definition into the pipeline
    ```turtle
    ### Import runners and processors
    <> owl:imports <./node_modules/@rdfc/file-utils-processors-ts/processors.ttl>.
    ```
  - Define a channel for the RML mapping data
    ```turtle
    ### Define the channels
    <mappingData> a rdfc:Reader, rdfc:Writer.
    ```
  - Create an instance and configure it to read the mapping file from disk (e.g., `./resources/mapping.rml.ttl`)
    ```turtle
    ### Define the processors
    # Processor to read and stream out the RML mappings
    <mappingReader> a rdfc:GlobRead;
        rdfc:glob <./resources/mapping.rml.ttl>;
        rdfc:output <mappingData>;
        rdfc:closeOnEnd true.
    ```
  - Attach it to the existing `rdfc:NodeRunner`
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>, <mappingReader>;
       ].
    ```
- [x] Add a Java Virtual Machine (JVM) runner (`rdfc:JvmRunner`) that allow us to execute Java processors
  - Import its semantic definition which, in this case, is packed within the built JAR file of the runner
    ```turtle
    ### Import runners and processors
    <> owl:imports <https://javadoc.jitpack.io/com/github/rdf-connect/jvm-runner/runner/master-SNAPSHOT/runner-master-SNAPSHOT-index.jar>.
    ```
  - Link it to the pipeline
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>, <mappingReader>;
       ], [
           rdfc:instantiaties rdfc:JvmRunner;
       ].
    ```
- [x] Add an `rdfc:RmlMapper` processor instance
  - Install the Java processor using Gradle:
    - If you do not want to use Gradle, you can manually download the JAR files from [JitPack](https://javadoc.jitpack.io/com/github/rdf-connect/rml-processor-jvm/master-SNAPSHOT/rml-processor-jvm-master-SNAPSHOT-all.jar) and put them in `pipeline/build/plugins/`. Otherwise, you can use the provided Dockerfile to run Gradle in a container.
    - Create a `build.gradle` file inside the `./pipeline` folder with the following content
        ```gradle
        plugins {
            id 'java'
        }
    
        repositories {
            mavenCentral()
            maven { url = uri("https://jitpack.io") }  // if your processors are on GitHub
        }
        dependencies {
            implementation("com.github.rdf-connect:rml-processor-jvm:master-SNAPSHOT:all")
        }
    
        tasks.register('copyPlugins', Copy) {
            from configurations.runtimeClasspath
            into "$buildDir/plugins"
        }
    
        configurations.all {
            resolutionStrategy.cacheChangingModulesFor 0, 'seconds'
        }
        ```
    - Build and pack the processor binary
      ```bash
      gradle copyPlugins
      ```
    - Import its semantic definition
      ```turtle
      ### Import runners and processors
      <> owl:imports <./build/plugins/rml-processor-jvm-master-SNAPSHOT-all.jar>.
      ```
    - Define an output channel for the resulting RDF data
      ```turtle
      ### Define the channels
      <rdf> a rdfc:Reader, rdfc:Writer.
      ```
    - Create an instance (`rdfc:RmlMapper`) and configure it to receive the RML mapping rules and JSON data stream
      ```turtle
      ### Define the processors
      # Processor to do the RML mapping
      <mapper> a rdfc:RmlMapper;
          rdfc:mappings <mappingData>;
          rdfc:source [
              rdfc:triggers true;
              rdfc:reader <json>;
              rdfc:mappingId ex:source1;
          ];
          rdfc:defaultTarget [
              rdfc:writer <rdf>;
              rdfc:format "turtle";
          ].
      ```
    - Link the processor to the corresponding runner using the `rdfc:processor` property
      ```turtle
      ### Define the pipeline
      <> a rdfc:Pipeline;
         rdfc:consistsOf [
             rdfc:instantiates rdfc:NodeRunner;
             rdfc:processor <fetcher>, <logger>, <mappingReader>;
         ], [
             rdfc:instantiaties rdfc:JvmRunner;
             rdfc:processor <mapper>;
         ].
      ```
- [x] Redirect the logging processor to log the resulting **RDF output** instead of the initial raw JSON
  ```turtle
  ### Define the processors
  # Processor to log the output
  <logger> a rdfc:LogProcessorJs;
        rdfc:reader <rdf>;
        rdfc:level "info";
        rdfc:label "output".
  ```
- [x] Run the pipeline:  
  ```bash
  npx rdfc pipeline.ttl
  # or with debug logging:
  LOG_LEVEL=debug npx rdfc pipeline.ttl
  ```

✅ Complete solution available in [**`task-2` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-2).


#### Task 3: Validate the produced RDF with SHACL

Next, validate the RDF output against a provided SHACL shape.

To help you with this, we prepared a [SHACL shape file](./pipeline/resources/shacl-shape.ttl) that you can use to validate the RDF data.


**Processors to add:**

- `rdfc:Validate` – validate RDF data using a given SHACL shape, implemented in TypeScript (implementation & documentation at [@rdfc/shacl-processor-ts](https://github.com/rdf-connect/shacl-processor-ts)). Internally, this processor relies on [`shacl-engine`](https://github.com/rdf-ext/shacl-engine), a JavaScript SHACL engine implementation  
- Another instance of `rdfc:LogProcessorJs` – for logging SHACL validation reports  

**Steps:**

- [x] Add an `rdfc:Validate` processor instance
  - Install the processor
    ```bash
    npm install @rdfc/shacl-processor-ts
    ```
  - Import its semantic definition into the pipeline
    ```turtle
    ### Import runners and processors
    <> owl:imports <./node_modules/@rdfc/shacl-processor-ts/processors.ttl>.
    ```
  - Define a channel for the SHACL validation reports and for the successfully validated RDF data
    ```turtle
    ### Define the channels
    <report> a rdfc:Reader, rdfc:Writer.
    <validated> a rdfc:Reader, rdfc:Writer.
    ```
  - Create an instance and configure it to use the provided SHACL shape file and to read the stream of produced RDF data
    ```turtle
    ### Define the processors
    # Processor to validate the output RDF with SHACL
    <validator> a rdfc:Validate;
        rdfc:shaclPath <./resources/shacl-shape.ttl>;
        rdfc:incoming <rdf>;
        rdfc:outgoing <validated>;
        rdfc:report <report>;
        rdfc:validationIsFatal false;
        rdfc:mime "text/turtle".
    ```
  - Link it to the corresponding runner: `rdfc:NodeRunner`
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>, <mappingReader>, <validator>;
       ], [
           rdfc:instantiaties rdfc:JvmRunner;
           rdfc:processor <mapper>;
       ].
    ```
- [x] Use a new instance of `rdfc:LogProcessorJs` to log validation reports at `warn` level
  - Define the new logger instance
    ```turtle
    ### Define the processors  
    # Processor to log the SHACL report
    <reporter> a rdfc:LogProcessorJs;
        rdfc:reader <report>;
        rdfc:level "warn";
        rdfc:label "report".
    ```
  - Link it to the corresponding runner: `rdfc:NodeRunner`
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>, <mappingReader>, <validator>, <reporter>;
       ], [
           rdfc:instantiaties rdfc:JvmRunner;
           rdfc:processor <mapper>;
       ].
    ```
- [x] Log only valid data through the first logger
  ```turtle
  ### Define the processors
  # Processor to log the output
  <logger> a rdfc:LogProcessorJs;
      rdfc:reader <validated>;  # update the channel it logs
      rdfc:level "info";
      rdfc:label "output".
  ``` 
- [x] Run the pipeline with a successfully validated result. You shall see the produced RDF in the console, similarly to the outcome of `task-2`, given that the validation is successful.
  ```bash
  npx rdfc pipeline.ttl
  ```
- [x] Run the pipeline with a failed validation
  - To see the validation process in action, let's alter the SHACL shape to require a property that won't be present in the data. We can add the following property shape
    ```turtle
    ex:ObservationCollectionShape a sh:NodeShape ;
        #...
        sh:property [
            sh:path sosa:fakeProperty ;
            sh:class sosa:Observation ;
            sh:minCount 1 ;
        ] .
    ```
  - Run the pipeline again to see the warning report
    ```bash
    npx rdfc pipeline.ttl
    ```

✅ Complete solution available in [**`task-3` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-3).


#### Task 4: Ingest validated RDF weather data into Virtuoso triple store

Finally, ingest the validated data into a **Virtuoso triple store** (via Docker Compose, or your own instance).

To help you with this, we prepared a [Docker Compose file](./pipeline/resources/docker-compose.yml) that you can use to run a Virtuoso instance via Docker.
The instance provided in the Docker Compose file is configured to be accessible at `http://localhost:8890/sparql` with SPARQL update enabled.

**Processors to add:**

- `rdfc:SPARQLIngest` – produce and execute SPARQL UPDATE queries from received triples/quads, implemented in TypeScript (implementation & documentation at [@rdfc/sparql-ingest-processor-ts](https://github.com/rdf-connect/sparql-ingest-processor-ts))  

**Steps:**

- [x] Add the `rdfc:SPARQLIngest` processor instance to ingest RDF data into the Virtuoso instance
  - Install the processor
    ```bash
    npm install @rdfc/sparql-ingest-processor-ts
    ```
  - Import its semantic definition into the pipeline
    ```turtle
    ### Import runners and processors
    <> owl:imports <./node_modules/@rdfc/sparql-ingest-processor-ts/processors.ttl>.
    ```
  - Define a channel for the SPARQL queries sent to Virtuoso
    ```turtle
    ### Define the channels
    <sparql> a rdfc:Reader, rdfc:Writer.
    ```
  - Create an instance and configure it to read the RDF data and send them to the Virtuoso SPARQL endpoint
    ```turtle
    ### Define the processors
    # Processor to ingest RDF data into a SPARQL endpoint
    <ingester> a rdfc:SPARQLIngest;
        rdfc:memberStream <validated>;
        rdfc:ingestConfig [
            rdfc:memberIsGraph false;
            rdfc:targetNamedGraph "http://ex.org/ViennaWeather";
            rdfc:graphStoreUrl "http://localhost:8890/sparql";
            rdfc:forVirtuoso true
        ];
        rdfc:sparqlWriter <sparql>.
    ```
  - Link it to the corresponding runner: `rdfc:NodeRunner`
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>, <mappingReader>, <validator>, <reporter>, <ingester>;
       ], [
           rdfc:instantiaties rdfc:JvmRunner;
           rdfc:processor <mapper>;
       ].
    ```
- [x] Change the input channel of the first `rdfc:LogProcessorJs` processor to the output channel of the `rdfc:SPARQLIngest` processor to log the SPARQL queries that are sent to the Virtuoso instance.
    ```turtle
    ### Define the processors
    # Processor to log the output
    <logger> a rdfc:LogProcessorJs;
        rdfc:reader <sparql>;  # update the channel it logs
        rdfc:level "info";
        rdfc:label "output".
    ```
- [x] Start the Virtuoso instance via Docker Compose (if you haven't already)
  ```bash
  cd resources
  docker-compose up -d
  ```
- [x] Run the pipeline:  
  ```bash
  npx rdfc pipeline.ttl
  # or with debug logging:
  LOG_LEVEL=debug npx rdfc pipeline.ttl
  ```

✅ Complete solution available in [**`task-4` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-4).  

🎉 You have now completed **Part 1**! Your pipeline fetches, converts, validates, and ingests Vienna’s weather forecast into Virtuoso. You can query the data using SPARQL, by opening your browser at <http://localhost:8890/sparql> and running the following query:
```sparql
SELECT * WHERE {
  GRAPH <http://ex.org/ViennaWeather> {
    ?s ?p ?o.
  }
}
```


---

### Part 2: Implementing a Custom Processor

The RDF data we produced in Part 1 includes **German literals** (`@de`). To make it more accessible, we will implement a **custom Python processor** that translates them into English (`@en`) using a lightweight local Machine Learning model from [Hugging Face](https://huggingface.co).

#### Task 5: Set up the processor project

As you might have noticed, we have worked in the `pipeline/` directory for the first part of the tutorial.
However, there is also a `processor/` directory in the root of the project.
This is where you will implement the custom Python processor in this part of the tutorial.

To kickstart the development of a new processor, the RDF-Connect ecosystem provides template repositories that you can use as a starting point, allowing you to directly dive into the actual processor logic without having to worry about the project setup and configuration.
We will use the [template-processor-py](https://github.com/rdf-connect/template-processor-py) repository as a starting point.

**Steps:**

- [ ] Either clone the template or use the preconfigured project in `processor/`  
- [ ] Install dependencies (see the `README.md` in the `procesor/` directory) 
  - Create a virtual environment using `hatch`
    ```bash
    hatch env create
    hatch shell
    ```
- [ ] Rename the template processor (e.g., `TranslationProcessor`) in `processor.py`, `processor.ttl`, `pyproject.toml`, and `README.md`
  - See "Next Steps" in the `README.md` file of the template repository for guidance.
- [ ] Build and verify  
  ```bash
  hatch build
  hatch test
  ```

✅ Complete solution available in [**`task-5` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-5).


#### Task 6: Implement translation logic and semantic description

We’ll translate German literals using the Hugging Face model [Helsinki-NLP/opus-mt-de-en](https://huggingface.co/Helsinki-NLP/opus-mt-de-en).

**Steps:**

- [ ] Install `transformers` and its dependencies (`sacremoses`, `sentencepiece` and `torch`), and the `rdflib` library for RDF parsing:
  ```bash
  uv add transformers sacremoses sentencepiece torch rdflib
  ```  
- [ ] Define the processor's argument types, which include the RDF-Connect reader and writer channels, the ML model name, the source and target translation languages
  ```python
  # --- Type Definitions ---
  @dataclass
  class TranslationArgs:
      reader: Reader
      writer: Writer
      model: str
      source_language: str
      target_language: str
  ```
- Define the corresponding semantic description (via a SHACL shape) for the inputs and outputs of the processor in the `processor/processor.ttl` file. Make sure the `sh:name` properties of the property shapes match the `TranslationArgs` variable names
  ```turtle
  rdfc:TranslationProcessor rdfc:pyImplementationOf rdfc:Processor;
      rdfs:label "Translation Processor";
      rdfs:comment "A processor to translate text using a specified ML translation model.";
      rdfc:modulePath "rdfc_translation_processor.processor";
      rdfc:class "TranslationProcessor".
    
  [ ] a sh:NodeShape;
      sh:targetClass rdfc:TranslationProcessor;
      sh:property [
          sh:class rdfc:Reader;
          sh:path rdfc:reader;
          sh:name "reader";
          sh:minCount 1;
          sh:maxCount 1;
      ], [
          sh:class rdfc:Writer;
          sh:path rdfc:writer;
          sh:name "writer";
          sh:minCount 1;
          sh:maxCount 1;
      ], [
          sh:datatype xsd:string;
          sh:path rdfc:model;
          sh:name "model";
          sh:minCount 1;
          sh:maxCount 1;
      ], [
          sh:datatype xsd:string;
          sh:path rdfc:sourceLanguage;
          sh:name "source_language";
          sh:minCount 1;
          sh:maxCount 1;
      ], [
          sh:datatype xsd:string;
          sh:path rdfc:targetLanguage;
          sh:name "target_language";
          sh:minCount 1;
          sh:maxCount 1;
      ].
  ```
- [ ] Load the model + tokenizer in `TranslationProcessor.init`  
  ```python
  from transformers import pipeline
  #...
  async def init(self) -> None:
      """This is the first function that is called (and awaited) when creating a processor.
      This is the perfect location to start things like database connections."""
      self.logger.debug("Initializing TranslationProcessor with args: {}".format(self.args))
      self.translator = pipeline(task='translation', model=self.args.model)
  ```
- [ ] In `transform`, implement the logic to translate language-tagged literals:
  - parse RDF triples with `rdflib`  
  - Identify literals in German having a `@de` tag  
  - Translate to English  
  - Emit both original and translated triples  
    ```python
    from rdflib import Graph, Literal
    #...
    async def transform(self) -> None:
        """Function to start reading channels.
        This function is called for each processor before `produce` is called.
        Listen to the incoming stream, log them, and push them to the outgoing stream."""
        async for data in self.args.reader.strings():
            # Log the incoming message
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
    ```
- [ ] (Optional) Add unit tests
  ```python
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
      
      caplog.set_level(logging.DEBUG)
  
      await proc.init()
      await proc.transform()
  
      # Writer should be called with each message
      actual_calls = [call.args for call in writer.string.await_args_list]
      assert any("hello world" in str(args).lower() for args in actual_calls)
  
      # Writer.close should be called once
      writer.close.assert_awaited_once()
  
      # Debug log at end should appear
      assert "done reading so closed writer." in caplog.text
  ```
- [ ] Run the tests
  ```bash
  hatch test
  ```

✅ Complete solution available in [**`task-6` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-6).


#### Task 7: Integrate the processor into the pipeline

Run your Python processor inside the pipeline with a Python runner for RDF-Connect.

**Processors to add:**
- `rdfc:TranslationProcessor` — German to English RDF literal translation (implemented in the previous step).

**Runners to add:**
- `rdfc:PyRunner` — run Python processors (implementation & documentation at [rdf-connect/py-runner](https://github.com/rdf-connect/py-runner)).

**Steps:**

- [ ] Build the processor into a package
  ```bash
  hatch build
  ```
- [ ] Create a `pyproject.toml` file inside the `pipeline/` folder to configure the Python environment for the pipeline
  - Specify the Python version to use to one specific version (e.g., `==3.13.*`). You need this to have a deterministic path for the `owl:imports` statement
  - Configure `[tool.hatch.envs.default]` to use a virtual environment called `.venv`
  ```toml
  [project]
  name = "vienna-weather-forecast-kg-pipeline"
  version = "0.0.1"
  description = "RDF-Connect pipeline to ingest Vienna's weather forecast in a knowledge graph."
  requires-python = "==3.13.*"
  dependencies = [
      "rdfc-runner>=1.0.0",
  ]
  
  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"
  
  [tool.hatch.build.targets.wheel]
  packages = ["resources"]
  
  [tool.hatch.envs.default]
  type = "virtual"
  path = ".venv"
  system-packages = false
  installer = "uv"
  env-vars = { PYTHONPATH = "src" }
  ```
- [ ] Add an instance of your processor to the pipeline
  - Install your built processor locally
    ```bash
    uv add ../processor/dist/rdfc_translation_processor-0.0.1.tar.gz
    ```
  - Import the semantic definition of your processor in `pipeline.ttl` using `owl:imports`
    ```turtle
    ### Import runners and processors
    <> owl:imports <./.venv/lib/python3.13/site-packages/rdfc_translation_processor/processor.ttl>.
    ```
  - Define a channel for the translated data
    ```turtle
    ### Define the channels
    <translated> a rdfc:Reader, rdfc:Writer.
    ```
  - Create an instance of your processor and configure it to read from the output channel of the RML mapper and write to the new output channel
      ```turtle
      ### Define the processors
      # Processor to translate RDF literals from German to English
      <translator> a rdfc:TranslationProcessor;
          rdfc:reader <rdf>;
          rdfc:writer <translated>;
          rdfc:model "Helsinki-NLP/opus-mt-de-en";
          rdfc:sourceLanguage "de";
          rdfc:targetLanguage "en".
      ```
- [ ] Update the input channel of the SHACL validator to read from the output channel of your processor
  ```turtle
  ### Define the processors
  # Processor to validate the output RDF with SHACL
  <validator> a rdfc:Validate;
      rdfc:shaclPath <./resources/shacl-shape.ttl>;
      rdfc:incoming <translated>;
      rdfc:outgoing <validated>;
      rdfc:report <report>;
      rdfc:validationIsFatal false;
      rdfc:mime "text/turtle".
    ```
- [ ] Add `rdfc:PyRunner` to the pipeline and attach your processor that needs to be run in Python
  - Import its semantic definition
    ```turtle
    ### Import runners and processors
    <> owl:imports <./.venv/lib/python3.13/site-packages/rdfc_runner/index.ttl>.
    ```
  - Link it to the pipeline and to the translation processor
    ```turtle
    ### Define the pipeline
    <> a rdfc:Pipeline;
       rdfc:consistsOf [
           rdfc:instantiates rdfc:NodeRunner;
           rdfc:processor <fetcher>, <logger>, <mappingReader>, <validator>, <reporter>, <ingester>;
       ], [
           rdfc:instantiates rdfc:JvmRunner;
           rdfc:processor <mapper>;
       ], [
           rdfc:instantiates rdfc:PyRunner;
           rdfc:processor <translator>;
       ].
    ```

✅ Complete solution available in [**`task-7` branch**](https://github.com/rdf-connect/vienna-weather-forecast-kg-pipeline/tree/task-7).  

🎉 You have now completed **Part 2**! The full pipeline now **translates German literals to English** before validation and ingestion into Virtuoso. Run the pipeline with:  

```bash
npx rdfc pipeline.ttl
# or with debug logs:
LOG_LEVEL=debug npx rdfc pipeline.ttl
```

Query Virtuoso and confirm the translated literals are present.
