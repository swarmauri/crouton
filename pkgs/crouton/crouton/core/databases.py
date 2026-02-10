from typing import (
    Any,
    Callable,
    List,
    Mapping,
    Type,
    Coroutine,
    Optional,
    Union,
)

import logging
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from . import CRUDGenerator, NOT_FOUND
from ._types import PAGINATION, PYDANTIC_SCHEMA, DEPENDENCIES
from ._utils import AttrDict, get_pk_type

logger = logging.getLogger(__name__)

try:
    from sqlalchemy.sql.schema import Table
    from databases.core import Database
except ImportError:
    Database = None  # type: ignore
    Table = None
    databases_installed = False
else:
    databases_installed = True

Model = Mapping[Any, Any]
CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, List[Model]]]


def pydantify_record(
    models: Union[Model, List[Model]]
) -> Union[AttrDict, List[AttrDict]]:
    if type(models) is list:
        return [AttrDict(**dict(model)) for model in models]
    else:
        return AttrDict(**dict(models))  # type: ignore


class DatabasesCRUDRouter(CRUDGenerator[PYDANTIC_SCHEMA]):
    
    def __init__(
        self,
        schema: Type[PYDANTIC_SCHEMA],
        table: "Table",
        database: "Database",
        create_schema: Optional[Type[PYDANTIC_SCHEMA]] = None,
        update_schema: Optional[Type[PYDANTIC_SCHEMA]] = None,
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
            databases_installed
        ), "Databases and SQLAlchemy must be installed to use the DatabasesCRUDRouter."

        self.table = table
        self.db = database
        self._pk = table.primary_key.columns.values()[0].name
        self._pk_col = self.table.c[self._pk]
        self._pk_type: type = get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or table.name,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs
        )

    def _handle_db_error(self, e: Exception, default_status: int = 500) -> None:
        """
        Centralized database error handler.
        Logs the real exception and raises an HTTPException.
        """
        logger.exception("Database operation failed")

        if isinstance(e, IntegrityError):
            raise HTTPException(422, "Key already exists") from e   

        elif isinstance(e, SQLAlchemyError):
            raise HTTPException(default_status, "Database error") from e

        else:
            raise HTTPException(default_status, "Unexpected server error") from e   

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            pagination: PAGINATION = self.pagination,
        ) -> List[Model]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            query = self.table.select().limit(limit).offset(skip)
            return pydantify_record(await self.db.fetch_all(query))  # type: ignore

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: self._pk_type) -> Model:  # type: ignore
            query = self.table.select().where(self._pk_col == item_id)
            model = await self.db.fetch_one(query)

            if model:
                return pydantify_record(model)  # type: ignore
            else:
                raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            schema: self.create_schema,  # type: ignore
        ) -> Model:
            query = self.table.insert()

            try:
                rid = await self.db.execute(query=query, values=schema.dict())
                if type(rid) is not self._pk_type:
                    rid = getattr(schema, self._pk, rid)

                return await self._get_one()(rid)
            except Exception as e:
                self._handle_db_error(e, default_status=422)

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, schema: self.update_schema  # type: ignore
        ) -> Model:
            query = self.table.update().where(self._pk_col == item_id)

            try:
                await self.db.fetch_one(
                    query=query, values=schema.dict(exclude={self._pk})
                )
                return await self._get_one()(item_id)
            except HTTPException:
                raise
            except Exception as e:
                self._handle_db_error(e, default_status=404)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route() -> List[Model]:
            query = self.table.delete()
            await self.db.execute(query=query)

            return await self._get_all()(pagination={"skip": 0, "limit": None})

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: self._pk_type) -> Model:  # type: ignore
            query = self.table.delete().where(self._pk_col == item_id)

            try:
                row = await self._get_one()(item_id)
                await self.db.execute(query=query)
                return row
            except HTTPException:
                raise
            except Exception as e:
                self._handle_db_error(e, default_status=404)

        return route
