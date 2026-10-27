# Cross-Language Package Interoperability Agent

A FastAPI application that validates package metadata, analyzes public exports,
recommends an interoperability strategy, creates an adapter plan, and can run a
Python billing example through a Java-launched JSON worker.

## Requirements

- Python 3.10 or later
- A Java Development Kit (JDK) on `PATH` or available through `JAVA_HOME` to use
  the billing execution endpoints. The Java bridge compiles its source on demand
  when the `.class` file is absent or out of date.

## Setup and run on Windows

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If Java is not already on `PATH`, set `JAVA_HOME` to your JDK directory and add
its `bin` directory to `PATH`:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The web interface and service are available at `http://127.0.0.1:8000`.
Interactive API documentation is at `http://127.0.0.1:8000/docs`; the health
endpoint is `GET /health`.

The interface submits package analysis to `POST /analyze-with-execution` and,
when requested, billing inputs to `POST /execute-billing-example`. Both API
calls use the same origin as the UI.

## API

### `POST /analyze`

Validates the package metadata and returns the package analysis, recommended
strategy, and adapter plan.

```json
{
  "source": {
    "name": "billing-python",
    "language": "Python",
    "version": "1.0",
    "runtime": "Python 3.12",
    "exports": ["calculate_total"]
  },
  "target": {
    "name": "billing-java",
    "language": "Java",
    "version": "1.0",
    "runtime": "JVM",
    "exports": ["calculateTotal"]
  }
}
```

Names and languages must be non-empty. Export entries cannot be blank; unknown
fields are rejected. Shared export names are evidence only and do not establish
API compatibility.

### `POST /analyze-with-execution`

Accepts the same `source` and `target` objects, plus an optional
`"execute_example": true`. The optional example runs the fixed billing request
through the Java bridge and includes its result as `execution_example`.

### `POST /execute-billing-example`

Runs billing through the Java bridge. `unit_price` must be a non-negative finite
decimal string and `quantity` must be a non-negative integer.

```json
{
  "unit_price": "20.00",
  "quantity": 3
}
```

Request validation errors return HTTP 422. Java toolchain issues return HTTP 503,
bridge timeouts return HTTP 504, and other bridge failures return HTTP 502.
Billing uses Python `Decimal` arithmetic and returns the submitted price,
quantity, and calculated total.

### `GET /health`

Returns `{"status": "ok"}` when the API process is responsive. This does not
probe Java availability.

## Tests

Run the complete test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The suite covers validation, analysis, strategy selection, adapter planning,
JSON handling, billing arithmetic and errors, API routes, and the Java-to-Python
execution bridge.
