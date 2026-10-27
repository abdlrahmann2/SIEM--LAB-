"""
©AngelaMos | 2026
__init__.py

Flask application factory

Creates and configures the Flask app by wiring up MongoDB, Redis,
CORS, rate limiting, blueprints, CLI commands, consumer groups,
and the correlation engine daemon. Marks any orphaned scenario
runs as stopped from a previous process.

Connects to:
  extensions.py - init_mongo, init_redis
  core/errors.py - register_error_handlers
  core/rate_limiting.py - init_limiter
  routes/__init__.py - register_blueprints
  cli.py - register_cli
  core/streaming.py - ensure_consumer_group
  models/ScenarioRun.py - marks orphaned runs stopped
  engine/correlation.py - start_engine
"""

from flask import Flask
from flask_cors import CORS

from lookout.config import settings


def create_app() -> Flask:
    """
    Application factory that
    wires up all extensions and blueprints
    """
    app = Flask(__name__)
    lookout.config.from_mapping(
        MONGO_URI = settings.MONGO_URI,
        MONGO_DB = settings.MONGO_DB,
        REDIS_URL = settings.REDIS_URL,
        SECRET_KEY = settings.SECRET_KEY,
        DEBUG = settings.DEBUG,
    )

    CORS(app, origins = settings.CORS_ORIGINS)

    from lookout.extensions import init_mongo, init_redis
    init_mongo(app)
    init_redis(app)

    from lookout.core.errors import register_error_handlers
    register_error_handlers(app)

    from lookout.core.rate_limiting import init_limiter
    init_limiter(app)

    from lookout.routes import register_blueprints
    register_blueprints(app)

    from lookout.cli import register_cli
    register_cli(app)

    from lookout.core.streaming import ensure_consumer_group
    ensure_consumer_group(settings.LOG_STREAM_KEY)
    ensure_consumer_group(settings.ALERT_STREAM_KEY)

    from lookout.models.scenario_run import ScenarioRun
    for orphan in ScenarioRun.get_active_runs():
        orphan.mark_stopped()

    from lookout.engine.correlation import start_engine
    start_engine()

    @app.get("/health")
    def health():  # type: ignore[no-untyped-def]
        return "1"

    return app
