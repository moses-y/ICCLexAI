from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import engine_from_config, pool

from icclex import config as icclex_config
from icclex import models  # noqa: F401  (registers the tables on Base.metadata)
from icclex.db import Base

cfg = context.config
cfg.set_main_option("sqlalchemy.url", icclex_config.DATABASE_URL.replace("%", "%%"))
if cfg.config_file_name:
    from logging.config import fileConfig

    fileConfig(cfg.config_file_name)

target_metadata = Base.metadata


def include_object(obj, name, type_, reflected, compare_to):
    # The postgis/postgis image ships tiger geocoder and topology tables in the same database.
    # Autogenerate only looks at tables we define; anything else is PostGIS's, and a first draft of
    # 0001 had upgrade() dropping 80 of them.
    if type_ == "table":
        return name in target_metadata.tables
    if reflected and hasattr(obj, "table"):
        return obj.table.name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    context.configure(url=cfg.get_main_option("sqlalchemy.url"), target_metadata=target_metadata,
                      literal_binds=True, include_object=include_object)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = engine_from_config(cfg.get_section(cfg.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata, include_object=include_object,
                          process_revision_directives=None, render_item=alembic_helpers.render_item)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
