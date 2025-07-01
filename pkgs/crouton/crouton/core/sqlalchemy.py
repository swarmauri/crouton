from typing import Any, Callable, List, Type, Generator, Optional, Union, Dict

from fastapi import Depends, HTTPException, Request, Response
from . import CRUDGenerator, NOT_FOUND, _utils
from ._types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA

try:
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.declarative import DeclarativeMeta as Model
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError
except ImportError:
    Model = None
    Session = None
    IntegrityError = None
    sqlalchemy_installed = False
else:
    sqlalchemy_installed = True
    Session = Callable[..., Generator[Session, Any, None]]

CALLABLE = Callable[..., Model]
CALLABLE_LIST = Callable[..., List[Model]]


# Utility function for extracting query parameters
def query_params(request: Request) -> Dict[str, Any]:
    """
    Extract query parameters from the incoming request
    and return them as a dictionary.
    """
    return dict(request.query_params)


class SQLAlchemyCRUDRouter(CRUDGenerator[SCHEMA]):
    """
    CRUD router built around SQLAlchemy ORM with robust error handling.

    ─────────────────────────────────────────────────────────────────────
    Status-code policy
    ─────────────────────────────────────────────────────────────────────
    200 OK            – Successful read / update.
    201 Created       – Successful create.
    204 No Content    – Successful delete (body withheld).
    400 Bad Request   – Malformed client input (type/format errors).
    404 Not Found     – Resource not found.
    409 Conflict      – Duplicate keys / unique-constraint violations.
    422 Unprocessable – Valid JSON but semantic/relational constraint fails.
    500 Internal      – All uncaught DB / runtime failures.
    """

    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Model,
        db: "Session",
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any
    ) -> None:
        assert (
            sqlalchemy_installed
        ), "SQLAlchemy must be installed to use the SQLAlchemyCRUDRouter."

        self.db_model = db_model
        self.db_func = db
        self._pk: str = db_model.__table__.primary_key.columns.keys()[0]
        self._pk_type: type = _utils.get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or db_model.__tablename__,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs,
        )

    def _parse_query_params(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse query parameters into filters for the database query.
        Exclude pagination-related parameters like 'skip' and 'limit'.
        """
        filters = {}
        accepted_fields = self.db_model.__table__.columns
    
        # Exclude pagination-related parameters
        excluded_params = {"skip", "limit"}
    
        for key, value in query_params.items():
            if key in excluded_params:
                continue  # Skip pagination parameters
            if key in accepted_fields:
                column = getattr(self.db_model, key)
                try:
                    column_type = column.type.python_type
                    parsed_value = column_type(value)
                    filters[key] = parsed_value
                except (ValueError, TypeError) as e:
                    raise HTTPException(
                        status_code=422, detail=f"Invalid value for {key}: {e}"
                    )
            else:
                raise HTTPException(400, f"Invalid filter field: {key}")
    
        return filters
    # ────────────────────────────
    # helpers
    # ────────────────────────────
    def _db_commit(self, db: Session) -> None:
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            # Distinguish “duplicate” vs other relational failures
            raise HTTPException(
                status_code=409 if "unique" in str(exc.orig).lower() else 422,
                detail=str(exc.orig),
            ) from exc
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {exc}",
            ) from exc

    # ────────────────────────────
    # GET many
    # ────────────────────────────
    def _get_all(self, *_, **__) -> CALLABLE_LIST:
        def route(
            db: Session = Depends(self.db_func),
            pagination: PAGINATION = self.pagination,
            query_params: Dict[str, Any] = Depends(query_params),
        ) -> List[Model]:
            filters = self._parse_query_params(query_params)
            objs = (
                db.query(self.db_model)
                .filter_by(**filters)
                .order_by(getattr(self.db_model, self._pk))
                .offset(pagination.get("skip", 0))
                .limit(pagination.get("limit", 100))
                .all()
            )
            if not objs:
                raise HTTPException(404, "No matching records found.")
            return objs

        return route

    # ────────────────────────────
    # GET one
    # ────────────────────────────
    def _get_one(self, *_, **__) -> CALLABLE:
        def route(
            item_id: self._pk_type, db: Session = Depends(self.db_func)  # type: ignore
        ) -> Model:
            obj: Optional[Model] = db.get(self.db_model, item_id)
            if obj is None:
                raise HTTPException(404, "Item not found.")
            return obj

        return route

    # ────────────────────────────
    # CREATE
    # ────────────────────────────
    def _create(self, *_, **__) -> CALLABLE:
        def route(
            model: self.create_schema,  # type: ignore
            db: Session = Depends(self.db_func),
        ) -> Model:
            try:
                obj = self.db_model(**model.dict())
            except (TypeError, ValueError) as exc:
                raise HTTPException(400, f"Invalid payload: {exc}") from exc

            db.add(obj)
            self._db_commit(db)
            db.refresh(obj)           # reflect DB-side defaults
            # FastAPI automatically sets 201 when returning Response after POST
            return obj

        return route

    # ────────────────────────────
    # UPDATE
    # ────────────────────────────
    def _update(self, *_, **__) -> CALLABLE:
        def route(
            item_id: self._pk_type,      # type: ignore
            model: self.update_schema,   # type: ignore
            db: Session = Depends(self.db_func),
        ) -> Model:
            obj = self._get_one()(item_id, db)   # raises 404 if absent
            # Only update defined fields
            for field, value in model.dict(exclude_unset=True).items():
                if field != self._pk and hasattr(obj, field):
                    setattr(obj, field, value)
            self._db_commit(db)
            db.refresh(obj)
            return obj

        return route

    # ────────────────────────────
    # DELETE one
    # ────────────────────────────
    def _delete_one(self, *_, **__) -> CALLABLE:
        def route(
            item_id: self._pk_type, db: Session = Depends(self.db_func)  # type: ignore
        ) -> Response:
            obj = self._get_one()(item_id, db)   # raises 404 if absent
            db.delete(obj)
            self._db_commit(db)
            return Response(status_code=204)

        return route

    # ────────────────────────────
    # DELETE all
    # ────────────────────────────
    def _delete_all(self, *_, **__) -> CALLABLE:
        def route(db: Session = Depends(self.db_func)) -> Response:
            db.query(self.db_model).delete(synchronize_session=False)
            self._db_commit(db)
            return Response(status_code=204)

        return route
