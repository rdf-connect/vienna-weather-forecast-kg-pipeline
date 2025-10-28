# vienna-weather-forecast-kg-pipeline

RDF-Connect pipeline to ingest Vienna's weather forecast in a knowledge graph.

## Usage

### Install Dependencies

#### Node

Install the Node.js dependencies:

```shell
npm install
```

#### Java

Install the Java dependencies using Gradle:

```shell
gradle copyPlugins
```

#### Python

Install the Python dependencies:

```shell
hatch env create
hatch shell
```

### Run the Pipeline

Run the pipeline using the `rdfc` command:

```shell
npx rdfc pipeline.ttl
# or with debug logs:
LOG_LEVEL=debug npx rdfc pipeline.ttl
```
