# Acme EHR

Acme EHR is a new service where we gather, process, and transform medical records.

Architecture utilizes Python `fastapi` with a PostgreSQL database.  Database migrations utilize `alembic`.   Validation is performed on data objects using `pydantic`.  



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



## Example: POST /import

An example of records being imported

```bash
curl -X POST \
    -H "Content-Type: application/text" \
    --data-binary @tmp/missing_data.jsonl \
    http://localhost:8000/import
```

Importing a set of ~70 records from problem set

![Screenshot 2026-04-20 at 10.31.05 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.31.05 AM.png)

Postgres database now contains records accordingly

![Screenshot 2026-04-20 at 10.31.08 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.31.08 AM.png)



## Example: GET /records?subject={query}

List records

```bash
curl http://localhost:8000/records\?subject\=Patient/PT-001
```

![Screenshot 2026-04-20 at 10.31.25 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.31.25 AM.png)

## Example: GET /records/{record_id}

Get single record

```bash
curl http://localhost:8000/records/obs-001\?fields\=id,subject
```

When record does not exist:

![Screenshot 2026-04-20 at 10.32.14 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.31.46 AM.png)

When the record exists:

![Screenshot 2026-04-20 at 10.32.14 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.32.14 AM.png)

## **Example: POST /transform**

Transform records

```bash
curl -X POST \
    -H "Content-Type: application/json" \
    --data-binary @tmp/transform_request.json \
    http://localhost:8000/transform
```

With the following transform:

```json
{
    "resourceTypes": [
        "Condition"
    ],
    "transformations": [
        {
            "action": "flatten",
            "field": "code.coding[0]"
        },
        {
            "action": "extract",
            "field": "valueQuantity.value",
            "as": "value"
        },
        {
            "action": "extract",
            "field": "valueQuantity.unit",
            "as": "unit"
        }
    ],
    "filters": {
        "subject": "Patient/PT-001"
    }
}
```



![Screenshot 2026-04-20 at 10.33.34 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.33.34 AM.png)

## Example: POST /analytics

Get analytics

```bash
curl http://localhost:8000/analytics
```

![Screenshot 2026-04-20 at 10.33.43 AM](/Users/henry/playground/py3-novellia-interview/docs/Screenshot 2026-04-20 at 10.33.43 AM.png)

