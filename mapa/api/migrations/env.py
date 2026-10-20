from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import create_engine

from mapa.config import get_settings
from mapa.db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata

def include_object(obj, name, type_, reflected, compare_to):
    # La imagen de PostGIS trae esquemas propios (tiger, topology) en el search_path:
    # cualquier tabla de la base que no esté en nuestros modelos no es nuestra.
    if type_ == "table" and reflected and compare_to is None:
        return False
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)


OPTS = dict(
    target_metadata=target_metadata,
    include_object=include_object,
    process_revision_directives=alembic_helpers.writer,
    render_item=alembic_helpers.render_item,
)


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().database_url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **OPTS,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Permite que los tests inyecten una conexión/URL propia.
    url = config.attributes.get("url") or get_settings().database_url
    engine = create_engine(url)
    with engine.connect() as connection:
        context.configure(connection=connection, **OPTS)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
