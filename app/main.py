import json
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI, Request
from sqlalchemy import select, func, cast, Date
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.config import ExtractionConfig
from app.models.imported_resources import ImportedResource
from app.models.records import Record
from app.database import create_engine, create_session_factory
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException

from app.requests.transform import RequestTransform

logger = logging.getLogger("acme")
logging.basicConfig(level=logging.DEBUG)


config = ExtractionConfig.model_validate(
    {
        "fields": {
            "id": "all",
            "subject": "all",
            "code": "all",
            "resourceType": "all",
            "effectiveDateTime": ["Observation"],
            "performedDateTime": ["Procedure"],
            "dosageInstruction": ["MedicationRequest"],
            "valueQuantity": ["Observation"],
            "status": [
                "Observation",
                "Procedure",
                "Condition",
                "MedicationRequest",
            ],
        }
    }
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(os.getenv("DATABASE_URI"))
    session_factory = create_session_factory(engine)

    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.config = config

    yield

    await engine.dispose()


def create_app() -> FastAPI:
    return FastAPI(
        title="ACME EHR",
        lifespan=lifespan,
    )


app = create_app()


def _get_config(request: Request):
    return request.app.state.config


def _get_session(request: Request):
    return request.app.state.session_factory()


async def _save_record(request: Request, data: Dict, line: int):
    """
    Saves record and logs import
    """

    validation_errors = []
    record = None
    try:
        record = Record.from_data(data, _get_config(request))

        # Save record
        session = _get_session(request)
        session.add(record)
        await session.commit()

    except IntegrityError as e:
        logger.error(f"Failed to insert line: {data} error: {e}")
        validation_errors.append(
            {"line": line, "reason": "Duplicate record with same id exists"}
        )

    except SQLAlchemyError as e:
        logger.error(f"Failed to insert line: {data} error: {e}")
        validation_errors.append({"line": line, "reason": "Database Error"})

    return record, validation_errors


async def _log_import(
    request: Request,
    raw_body: str,
    line: int,
    record_id: str | None,
    validation_errors: list,
):
    """
    Logs import
    """

    try:
        imported_resource = ImportedResource(
            record_id=record_id,
            raw_body=raw_body,
            validation_errors=validation_errors,
        )
        session = _get_session(request)
        session.add(imported_resource)
        await session.commit()

    except SQLAlchemyError as e:
        logger.error(f"Failed to insert line: {raw_body} error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return imported_resource


@app.get("/")
async def root():
    return {"status": "Healthy"}


@app.post("/import", status_code=201)
async def import_resources(request: Request):
    """Receives a JSONL file and imports records into the database."""

    request_body = await request.body()
    request_body = request_body.decode("utf-8")

    # Each JSONL line
    total_lines_processed = 0
    validation_errors = []
    records = []
    i = -1
    for line in request_body.split("\n"):
        i += 1
        raw_body = line.strip()

        # Ignore empty lines
        if not raw_body:
            logger.warning("Empty line detected")
            continue

        # Count lines processed
        total_lines_processed += 1

        try:
            log_imported_records = []
            data = json.loads(raw_body)

            # Distribute component records to their own records
            if "component" in data and isinstance(data["component"], list):
                components = data.pop("component")
                for component in components:
                    component_record = data.copy()
                    component_record["component"] = [component]

                    # Record
                    record, recent_validation_errors = await _save_record(
                        request, component_record, i
                    )
                    validation_errors.extend(recent_validation_errors)
                    records.append(record)
                    log_imported_records.append(
                        {
                            "raw_body": json.dumps(component_record),
                            "record_id": record.id
                            if len(recent_validation_errors) == 0
                            else None,
                            "validation_errors": recent_validation_errors,
                        }
                    )

            # Transform
            else:
                # Record
                record, recent_validation_errors = await _save_record(request, data, i)
                validation_errors.extend(recent_validation_errors)
                records.append(record)
                log_imported_records.append(
                    {
                        "raw_body": json.dumps(data),
                        "record_id": record.id
                        if len(recent_validation_errors) == 0
                        else None,
                        "validation_errors": recent_validation_errors,
                    }
                )

            # Log imported records
            for log_imported_record in log_imported_records:
                await _log_import(
                    request,
                    log_imported_record["raw_body"],
                    i,
                    log_imported_record["record_id"],
                    log_imported_record["validation_errors"],
                )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse line: {raw_body} error: {e}")
            _log_import(
                request,
                json.dumps(component_record),
                i,
                None,
                validation_errors,
            )

    return {
        "summary": {
            "total_lines_processed": total_lines_processed,
            "records": [record.values() for record in records],
            "validation_errors": validation_errors,
            "data_quality_warnings": [],
            "statistics": {"records_by_type": {}, "unique_patients": 0},
        }
    }


@app.get("/records")
async def index_records(
    request: Request,
    resourceType: str | None = None,
    subject: str | None = None,
    fields: str | None = None,
):
    """List records"""
    session = _get_session(request)
    query = select(Record)

    # Filter by resourceType
    if resourceType:
        query = query.where(Record.resource_type == resourceType)

    # Filter by subject
    if subject:
        query = query.where(Record.subject == subject)

    # Execute query
    result = await session.execute(query)
    records = result.scalars().all()

    fields = fields.split(",") if fields else None
    return [record.values(fields) for record in records]


@app.get("/records/{record_id}")
async def get_record(record_id: str, request: Request, fields: str | None = None):
    """Get single record"""
    session = _get_session(request)
    result = await session.execute(select(Record).where(Record.id == record_id))
    try:
        record = result.scalar_one()
        fields = fields.split(",") if fields else None
        return record.values(fields)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Record not found")


@app.post("/transform")
async def transform_records(request: Request, request_transform: RequestTransform):
    """Perform record transformations according requested configuration."""
    logger.info(request_transform)

    session = _get_session(request)
    query = select(Record).options(selectinload(Record.imported_resource))

    if request_transform.resourceTypes:
        query = query.where(Record.resource_type.in_(request_transform.resourceTypes))

    if request_transform.filters:
        for key, value in request_transform.filters.dict().items():
            if value is None:
                continue
            query = query.where(getattr(Record, key) == value)

    result = await session.execute(query)
    retrieved_records = result.scalars().all()
    raw_dataset = [record.imported_resource.raw_body for record in retrieved_records]

    # Transform record; only valid records
    records = []
    for raw_body in raw_dataset:
        data = json.loads(raw_body)
        record = Record.from_data(data, _get_config(request))
        records.append(record)

    return [record.values() for record in records]


@app.get("/analytics")
async def get_analytics(request: Request):
    """Gets quality metrics"""

    session = _get_session(request)

    query = select(
        func.count(Record.id).label("total_records"),
        func.count(func.distinct(Record.subject)).label("num_unique_subjects"),
    )
    record_results = await session.execute(query)
    record_results = record_results.first()
    record_results = record_results._mapping

    count_query = select(
        func.sum(func.jsonb_array_length(ImportedResource.validation_errors)).label(
            "num_validation_errors"
        ),
        func.count(func.distinct(cast(ImportedResource.created_at, Date))).label(
            "num_imports"
        ),
    )

    imported_results = await session.execute(count_query)
    imported_results = imported_results.first()
    imported_results = imported_results._mapping

    return {
        "total_records": record_results.get("total_records"),
        "num_unique_subjects": record_results.get("num_unique_subjects"),
        "validation_errors": {
            "num_errors": imported_results.get("num_validation_errors")
        },
        "num_imports": imported_results.get("num_imports"),
    }
