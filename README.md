# vienna-weather-forecast-kg-pipeline

RDF-Connect pipeline to ingest Vienna’s weather forecast into a knowledge graph.  
This repository provides **incremental solutions** for the hands-on tutorial at  
[SEMANTiCS 2025](https://2025-eu.semantics.cc/page/cfp_ws):  
👉 [Tutorial Materials](https://rdf-connect.github.io/Tutorial-SEMANTiCS2025/) & [Tutorial Slides](https://rdf-connect.github.io/Tutorial-SEMANTiCS2025/slides)

---

## RDF-Connect Tutorial

This tutorial walks you step by step through building a **provenance-aware, streaming RDF pipeline** using the language-agnostic framework **RDF-Connect**.  

The use case: ingesting weather forecast data for Vienna from the **GeoSphere Austria API** into a queryable **knowledge graph**.

You will:

- Set up an RDF-Connect environment  
- Configure pipeline components  
- Implement processors in multiple programming languages  
- Run the pipeline end-to-end

By the end, you will have:

- A working RDF-Connect pipeline for real-world data  
- A clear understanding of how to integrate heterogeneous processors across languages  
- Practical experience with implementing RDF-Connect processors

The tutorial is designed for all experience levels, and you can follow along at your own pace.  
Each **task** builds on the previous one, and each solution is available in a dedicated **branch** of this repository (`task-1`, `task-2`, ...).  
You can use these branches to verify your work, catch up if stuck, or compare with the reference solution.

---

## Getting Started

The recommended starting point is to **fork and clone this repository**, then switch to the `main` branch.

### Prerequisites

Make sure the following are installed:

- **Node.js ≥16**  
- **Java ≥11**  
- **Python ≥3.8** (we recommend 3.13 for Part 2)  

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

- [ ] Create a `pipeline/` directory (all Part 1 work happens here).  
- [ ] Inside `pipeline/`, create:
  - `pipeline.ttl` (pipeline configuration)  
  - `README.md` (documentation)  
  - `package.json` (via `npm init` or manually)  
  - `.gitignore` (exclude `node_modules/` etc.)  
- [ ] Install the orchestrator:  
  ```bash
  npm install @rdfc/orchestrator-js
  ```  
- [ ] Initialize the RDF-Connect pipeline in `pipeline.ttl`:
  - Add RDF namespaces (e.g., `rdfc`, `owl`, `ex`)
  - Declare the pipeline with `<> a rdfc:Pipeline`

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

✅ The solution for this task is in the **`main` branch**.


#### Task 1: Fetch weather data as JSON

Configure the pipeline to fetch weather data from GeoSphere Austria (station `11035`, near the SEMANTiCS venue):

- API endpoint:  
  <https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min?parameters=TL,RR&station_ids=11035>

**Steps:**

- [ ] Add an `rdfc:HttpFetch` processor (from [@rdfc/http-utils-processor-ts](https://github.com/rdf-connect/http-utils-processor-ts))  
  - Configure it to fetch from the API endpoint  
  - Define input/output channels  
  - Import definition via `owl:imports`  
- [ ] Add an `rdfc:NodeRunner` (from [@rdfc/js-runner](https://github.com/rdf-connect/js-runner))  
  - Import and attach it to the pipeline  
  - Connect it to the `rdfc:HttpFetch` processor using the `rdfc:processor` property
- [ ] Add a `rdfc:LogProcessorJs` (from [@rdfc/log-processor-ts](https://github.com/rdf-connect/log-processor-ts))  
  - Configure it with e.g., log level: `info` & label: `output`  
  - Connect the output channel of `rdfc:HttpFetch` to its input channel
  - Import its definition and attach it to the `rdfc:NodeRunner`
- [ ] Run the pipeline:  
  ```bash
  npx rdfc pipeline.ttl
  # or with debug logging:
  LOG_LEVEL=debug npx rdfc pipeline.ttl
  ```

✅ Solution available in **`task-1` branch**.


#### Task 2: Convert JSON to RDF

You will now convert the JSON stream into RDF using **[RML](https://rml.io/)** with the help of the `rdfc:RmlMapper` processor.

To help you with this, we prepared an [RML mapping file](./pipeline/resources/mapping.rml.ttl) for you that you can use to convert the JSON data to RDF.

**Processors to use:**

- `rdfc:GlobRead` – read mapping file ([@rdfc/file-utils-processors-ts](https://github.com/rdf-connect/file-utils-processors-ts))  
- `rdfc:RmlMapper` – convert JSON to RDF ([rml-processor-jvm](https://github.com/rdf-connect/rml-processor-jvm))  
- `rdfc:JvmRunner` – run Java processors ([rdf-connect/jvm-runner](https://github.com/rdf-connect/jvm-runner))  

**Steps:**

- [ ] Use `rdfc:GlobRead` to read the RML mapping file
  -  Configure it to read the mapping file from where you saved it (e.g., `./resources/mapping.rml.ttl`)  
  -  Import its definition and attach it to the existing `rdfc:NodeRunner`
- [ ] Pass mapping + JSON into `rdfc:RmlMapper`  
- [ ] Add the `rdfc:RmlMapper` (from [rml-processor-jvm](https://github.com/rdf-connect/rml-processor-jvm))
  - Configure the input/output channels
  - Import its definition via `owl:imports`
- [ ] Add an `rdfc:JvmRunner` (from [rdf-connect/jvm-runner](https://github.com/rdf-connect/jvm-runner))
  - Import and attach it to the pipeline
  - Connect the `rdfc:RmlMapper` processor to it using the `rdfc:processor` property
- [ ] Redirect the logging processor to log **RDF output** instead of raw JSON  

✅ Solution available in **`task-2` branch**.


#### Task 3: Validate RDF with SHACL

Next, validate the RDF output against a provided SHACL shape.

To help you with this, we prepared a [SHACL shape file](./pipeline/resources/shacl-shape.ttl) for you that you can use to validate the RDF data.


**Processors:**

- `rdfc:Validate` – validate RDF data using a SHACL shape ([@rdfc/shacl-processor-ts](https://github.com/rdf-connect/shacl-processor-ts))  
- Another `rdfc:LogProcessorJs` – log validation reports  

**Steps:**

- [ ] Add the `rdfc:Validate` (from [@rdfc/shacl-processor-ts](https://github.com/rdf-connect/shacl-processor-ts))
  - Configure it to use the provided SHACL shape file
  - Define input/output channels
  - Import its definition via `owl:imports`
  - Attach it to the existing `rdfc:NodeRunner`
- [ ] Log only valid data through the first logger  
- [ ] Log reports at `warn` level with the second logger  

✅ Solution available in **`task-3` branch**.


#### Task 4: Ingest RDF into Virtuoso

Finally, ingest the validated data into a **Virtuoso triple store** (via Docker Compose, or your own instance).

To help you with this, we prepared a [Docker Compose file](./pipeline/resources/docker-compose.yml) for you that you can use to run a Virtuoso instance via Docker.
The instance provided in the Docker Compose file is configured to be accessible at `http://localhost:8890/sparql` with SPARQL update enabled.

**Processors:**

- `rdfc:Sdsify` – convert RDF to SDS records ([@rdfc/sds-processors-ts](https://github.com/rdf-connect/sds-processors-ts))  
- `rdfc:SPARQLIngest` – send SDS records to Virtuoso ([@rdfc/sparql-ingest-processor-ts](https://github.com/rdf-connect/sparql-ingest-processor-ts))  

**Steps:**

- [ ] Convert validated RDF to SDS records with `rdfc:Sdsify` (from [@rdfc/sds-processors-ts](https://github.com/rdf-connect/sds-processors-ts))
  - Configure it with input/output channels and an SDS stream ID (e.g., `http://ex.org/ViennaWeather`)  
  - Import its definition via `owl:imports`  
  - Attach it to the existing `rdfc:NodeRunner`
- [ ] Add the `rdfc:SPARQLIngest` (from [@rdfc/sparql-ingest-processor-ts](https://github.com/rdf-connect/sparql-ingest-processor-ts))
  - Configure it to use the Virtuoso SPARQL endpoint (e.g., `http://localhost:8890/sparql`)  
  - Define input/output channels  
  - Import its definition and attach it to the `rdfc:NodeRunner`
- [ ] Change the input channel of the first `rdfc:LogProcessorJs` processor to the output channel of the `rdfc:SPARQLIngest` processor to log the SPARQL queries that are sent to the Virtuoso instance.

✅ Solution available in **`task-4` branch**.  

🎉 You have now completed **Part 1**! Your pipeline fetches, converts, validates, and ingests Vienna’s weather forecast into Virtuoso. You can query the data using SPARQL.


---

### Part 2: Implementing a Custom Processor

The data includes **German literals** (`@de`). To make it more accessible, we will implement a **custom Python processor** that translates them into English (`@en`) using a lightweight local ML model from Hugging Face.

#### Task 5: Set up the processor project

As you might have noticed, we have worked in the `pipeline/` directory for the first part of the tutorial.
However, there is also a `processor/` directory in the root of the project.
This is where you will implement the custom Python processor in this part of the tutorial.

To kickstart the development of a new processor, the RDF-Connect ecosystem provides template repositories that you can use as a starting point, allowing you to directly dive into the actual processor logic without having to worry about the project setup and configuration.
We will use the [template-processor-py](https://github.com/rdf-connect/template-processor-py) repository as a starting point.

**Steps:**

- [ ] Either clone the template or use the preconfigured project in `processor/`  
- [ ] Install dependencies (see template `README.md`)  
- [ ] Rename the template processor (e.g., `TranslationProcessor`) in `processor.py`, `processor.ttl`, `pyproject.toml`, and `README.md`
  - See "Next Steps" in the `README.md` file of the template repository for guidance.
- [ ] Build and verify  

✅ Solution in **`task-5` branch**


#### Task 6: Implement translation logic

We’ll translate German literals using the Hugging Face model [Helsinki-NLP/opus-mt-de-en](https://huggingface.co/Helsinki-NLP/opus-mt-de-en).

**Steps:**

- [ ] Install `transformers`:  
  ```bash
  uv add transformers
  ```  
- [ ] Load the model + tokenizer in `TranslationProcessor.init`  
- [ ] In `transform`, implement the logic to translate language-tagged literals:
  - parse triples with `rdflib`  
  - Identify literals with `@de`  
  - Translate to English  
  - Emit both original and translated triples  
- [ ] (Optional) Add unit tests  
- [ ] Build the project  

✅ Solution in **`task-6` branch**


#### Task 7: Integrate the processor into the pipeline

Run your Python processor inside the pipeline with `rdfc:PyRunner` ([rdf-connect/py-runner](https://github.com/rdf-connect/py-runner)).

**Steps:**

- [ ] Build the processor into a package  
- [ ] Add a `pyproject.toml` in `pipeline/`
  - Specify the Python version to use to one specific version (e.g., `==3.13.*`). You need this to have a deterministic path for the `owl:imports` statement
  - Configure `[tool.hatch.envs.default]` to use a virtual environment called `.venv`
- [ ] Install your built processor locally with `uv add ../processor/dist/your-processor.tar.gz`  
- [ ] Add `rdfc:PyRunner` to the pipeline and attach your processor (from [rdf-connect/py-runner](https://github.com/rdf-connect/py-runner))
- [ ] Connect it between the RML step and the SHACL validator  

✅ Solution in **`task-7` branch**  

🎉 You have now completed **Part 2**! The full pipeline now **translates German literals to English** before validation and ingestion into Virtuoso. Run the pipeline with:  

```bash
npx rdfc pipeline.ttl
# or with debug logs:
LOG_LEVEL=debug npx rdfc pipeline.ttl
```

Query Virtuoso and confirm the translated literals are present.