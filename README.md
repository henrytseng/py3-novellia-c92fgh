# Acme EHR

Acme EHR is a new service where we gather, process, and transform medical records.

## Usage

Build

```bash
bin/build
```

Running services

```bash
bin/up
```

Test

```bash
bin/test
```

Stopping services

```bash
bin/down
```

## Example

Import records

```bash
curl -X POST \
    -H "Content-Type: application/text" \
    --data-binary @tmp/missing_data.jsonl \
    http://localhost:8000/import
```

List records
```bash
curl http://localhost:8000/records\?subject\=Patient/PT-001
```

Get single record
```bash
curl http://localhost:8000/records/obs-001\?fields\=id,subject
```

Transform records

```bash
curl -X POST \
    -H "Content-Type: application/json" \
    --data-binary @tmp/transform_request.json \
    http://localhost:8000/transform
```

Get analytics

```bash
curl http://localhost:8000/analytics
```
