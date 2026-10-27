# Live Demonstration Guide

This 5–7 minute walkthrough uses the running local application. No screenshots
or unobserved evidence are included in this repository; demonstrate the actual
interface and results live.

## Before the presentation

From the repository root in PowerShell, confirm Python and Java are installed,
then start the server:

```powershell
java -version
javac -version
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Keep that terminal open. In a second PowerShell window, check the health route:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Open the frontend at <http://127.0.0.1:8000/>. It should show **API connected**.
Swagger UI is at <http://127.0.0.1:8000/docs>.

## 5–7 minute sequence

### 0:00–0:45 — Introduce the problem

Explain that package names and export names alone cannot prove two APIs
compatible. This project demonstrates a cautious first-pass analysis, a
language-based strategy recommendation, and an implementation/test checklist.

### 0:45–1:30 — Show the system shape

Walk through the architecture at a high level:

1. The browser sends package metadata to the FastAPI application.
2. The analyzer compares declared language labels and export names.
3. The strategy selector returns `direct_import` for matching language labels
   or `rest_api` otherwise.
4. The planner supplies generic implementation steps and test requirements.
5. The optional billing example starts Java, which starts the Python worker and
   passes a JSON request/response through standard input/output.

The analysis and billing flows are related in the interface but are not the
same integration. The billing bridge is a local process boundary, not the
REST-based adapter suggested by the cross-language strategy.

### 1:30–3:30 — Analyze the example packages

Use the prefilled source and target:

- Source: `billing-python`, language `Python`, export `calculate_total`
- Target: `billing-java`, language `Java`, export `calculateTotal`

Click **Analyze packages**. Point out that the response includes:

- A cross-language boundary risk and a no-matching-export risk.
- The `rest_api` strategy and its rationale.
- An adapter-plan checklist and suggested tests.

Clarify that the analyzer compares declared metadata only. It does not inspect
package code, signatures, types, dependencies, or actual runtime behavior.
Matching export names would be evidence only, not a compatibility guarantee.
The plan is guidance; this application does not generate an adapter.

### 3:30–5:00 — Execute the Java/Python billing example

Enable **Execute after analysis**, leave or enter the values below, then click
**Analyze packages**:

```json
{
  "unit_price": "20.00",
  "quantity": 3
}
```

The frontend calls `POST /execute-billing-example`. The route starts the Java
bridge, Java launches the active Python interpreter, and the worker calls the
Decimal-based billing function. Point out the successful response:

```json
{
  "ok": true,
  "result": {
    "unit_price": "20.00",
    "quantity": 3,
    "total": "60.00"
  }
}
```

This proves the included demonstration path ran for this input; it does not
prove arbitrary packages are compatible.

### 5:00–6:00 — Show the API and validation

Open `/docs` and locate `POST /analyze`, `POST /analyze-with-execution`, and
`POST /execute-billing-example`. Explain that malformed or out-of-range request
values return HTTP 422. For example, an invalid decimal string is rejected
before the Java process starts.

Optional PowerShell request:

```powershell
$body = '{"unit_price":"20.00","quantity":3}'
curl.exe -sS -X POST http://127.0.0.1:8000/execute-billing-example `
  -H "Content-Type: application/json" -d $body
```

### 6:00–7:00 — Close with scope and next steps

Summarize what is implemented today and what remains future work: richer
signature/type metadata, real package introspection, additional strategy rules,
adapter scaffolding, API authentication, process isolation, and browser-level
automated tests.

## Runtime execution versus analysis

`POST /analyze` and the analysis portion of `/analyze-with-execution` are
metadata-only and do not launch the Java bridge. Setting
`execute_example: true` on `/analyze-with-execution` runs a fixed billing
demonstration (`20.00` × `3`). The browser instead posts the user's billing
form values to `/execute-billing-example`. Both paths exercise the Java-to-
Python worker boundary, but neither executes the submitted package metadata.

## Likely questions

**Does `compatible: false` mean the packages are definitely incompatible?**  
No. The analyzer is conservative and the available metadata is insufficient to
prove compatibility. It reports risks and does not claim that matching names
establish matching signatures or behavior.

**Does the application generate an adapter?**  
No. It generates a static checklist with implementation steps and test
requirements. Generating and validating production adapter code is future work.

**Why recommend REST if the demonstration uses Java and Python subprocesses?**  
`rest_api` is the strategy rule for different declared language labels. The
included billing example separately demonstrates JSON over a local process
boundary; it is not an implemented REST adapter between arbitrary packages.

**Why use `Decimal` for billing?**  
Decimal arithmetic avoids introducing binary floating-point representation
artifacts into decimal price calculations. The example does not apply a
currency-specific rounding or quantization policy.

**What happens if Java is unavailable?**  
Billing returns a gateway/service error with a useful detail; package analysis
without execution remains available. A JDK is required to compile and run the
bridge.

**Can the service be exposed publicly as-is?**  
No. It has no authentication or rate limiting, and billing starts local child
processes. Treat it as a local demonstration until access controls, resource
limits, and process isolation are added.

## After the demonstration

Stop the server with `Ctrl+C`. To rerun the tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```
