# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""
import datetime
import json
import os
import shutil
import tempfile

import pytest
from flask import current_app as flask_current_app, url_for
from flask_celeryext import create_celery_app
from invenio_app.config import APP_DEFAULT_SECURE_HEADERS
from invenio_app.factory import create_app
from invenio_app.limiter import set_rate_limit
from invenio_db import db as db_
from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS
from invenio_records_rest.utils import allow_all
from invenio_search import current_search, current_search_client
from sqlalchemy_utils import database_exists, create_database

from oarepo_deposit.records import DepositRecord


@pytest.fixture
def deposit_url(api):
    """Deposit API URL."""
    with api.test_request_context():
        return url_for('invenio_records_rest.recid_list').replace('/api', '')


@pytest.fixture
def licenses_url(api):
    """Deposit API URL."""
    with api.test_request_context():
        return url_for('invenio_records_rest.od_lic_list').replace('/api', '')


@pytest.yield_fixture
def api_client(api):
    """Flask test client for API app."""
    with api.test_client() as client:
        yield client


@pytest.fixture
def get_json():
    """Function for extracting json from response."""

    def inner(response, code=None):
        """Decode JSON from response."""
        data = response.get_data(as_text=True)
        if code is not None:
            assert response.status_code == code, data
        return json.loads(data)

    return inner


@pytest.fixture
def json_headers():
    """JSON headers."""
    return [('Content-Type', 'application/json'),
            ('Accept', 'application/json')]


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture.

    TODO: Remove this fixture if you add Celery support.
    """
    return {}


def wrap_rate_limit():
    """Wrap rate limiter function to avoid affecting other tests."""
    if flask_current_app.config.get('USE_FLASK_LIMITER'):
        return set_rate_limit()
    else:
        return "1000 per second"


@pytest.fixture
def use_flask_limiter(app):
    """Activate flask limiter."""
    flask_current_app.config.update(dict(
        USE_FLASK_LIMITER=True,
        RATELIMIT_GUEST_USER='2 per second',
        RATELIMIT_AUTHENTICATED_USER='4 per second',
        RATELIMIT_PER_ENDPOINT={
            'zenodo_frontpage.index': '10 per second',
            'security.login': '10 per second'
        }))
    yield
    flask_current_app.config['USE_FLASK_LIMITER'] = False


@pytest.yield_fixture(scope='session')
def instance_path():
    """Default instance path."""
    path = tempfile.mkdtemp()

    yield path

    shutil.rmtree(path)


@pytest.fixture(scope='module')
def script_dir(request):
    """Return the directory of the currently running test script."""
    return request.fspath.join('..')


@pytest.fixture(scope='session')
def env_config(instance_path):
    """Default instance path."""
    os.environ.update(
        INVENIO_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )

    return os.environ


@pytest.yield_fixture(scope='session')
def tmp_db_path():
    """Temporary database path."""
    os_path = tempfile.mkstemp(prefix='zenodo_test_', suffix='.db')[1]
    path = 'sqlite:///' + os_path
    yield path
    os.remove(os_path)


@pytest.fixture(scope='session')
def default_config(tmp_db_path):
    """Default configuration."""

    # Disable HTTPS
    APP_DEFAULT_SECURE_HEADERS['force_https'] = False
    APP_DEFAULT_SECURE_HEADERS['session_cookie_secure'] = False

    records_rest = dict(
        recid=dict(
            pid_type='recid',
            pid_minter='recid',
            pid_fetcher='recid',
            record_loaders={
                'application/json': 'oarepo_validate:json_loader',
                'application/json-patch+json': 'oarepo_validate:json_loader'
            },
            record_serializers={
                'application/json': 'oarepo_validate:json_response',
            },
            search_serializers={
                'application/json': 'oarepo_validate:json_search',
            },
            list_route='/records/',
            item_route='/records/<pid(recid,record_class="oarepo_deposit.records.DepositRecord):pid_value>',
            record_class=DepositRecord,
            create_permission_factory_imp=allow_all,
            delete_permission_factory_imp=allow_all,
            update_permission_factory_imp=allow_all,
            read_permission_factory_imp=allow_all,
        )
    )
    records_rest.update(OPENDEFINITION_REST_ENDPOINTS)

    return dict(
        PIDSTORE_RECID_FIELD='pid',
        RATELIMIT_APPLICATION=wrap_rate_limit,
        CFG_SITE_NAME="testserver",
        DEBUG_TB_ENABLED=False,
        APP_DEFAULT_SECURE_HEADERS=APP_DEFAULT_SECURE_HEADERS,
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        COMMUNITIES_MAIL_ENABLED=False,
        MAIL_SUPPRESS_SEND=True,
        LOGIN_DISABLED=True,
        DEPOSIT_DATACITE_MINTING_ENABLED=False,
        SIPSTORE_ARCHIVER_WRITING_ENABLED=False,
        OAUTHLIB_INSECURE_TRANSPORT=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', tmp_db_path),
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SEARCH_INDEX_PREFIX='oarepo-test-',
        JSONSCHEMAS_HOST='oarepo.org',
        RECORDS_REST_ENDPOINTS=records_rest
    )


@pytest.fixture()
def api(app):
    """Flask application fixture."""
    return app.wsgi_app.mounts['/api']


@pytest.yield_fixture
def api_client(api):
    """Flask test client for API app."""
    with api.test_client() as client:
        yield client


@pytest.yield_fixture(scope='session')
def app(env_config, default_config):
    """Flask application fixture."""
    app = create_app(**default_config)
    # FIXME: Needs fixing flask_celeryext,
    # which once creates the first celery app, the flask_app that is set
    # is never released from the global state, even if you create a new
    # celery application. We need to unset the "flask_app" manually.
    from celery import current_app as cca
    cca = cca._get_current_object()
    delattr(cca, "flask_app")
    celery_app = create_celery_app(app)
    celery_app.set_current()

    with app.app_context():
        yield app


@pytest.yield_fixture
def es(app):
    """Provide elasticsearch access."""
    list(current_search.delete(ignore=[400, 404]))
    current_search_client.indices.delete(index='*')
    current_search_client.indices.delete_template('*')
    list(current_search.create())
    list(current_search.put_templates())
    current_search_client.indices.refresh()
    try:
        yield current_search_client
    finally:
        current_search_client.indices.delete(index='*')
        current_search_client.indices.delete_template('*')


@pytest.yield_fixture
def db(app):
    """Setup database."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    print('DB CREATE ALLL')
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.fixture
def minimal_record():
    """Minimal record."""
    return {
        "doi": "10.5072/zenodo.123",
        "resource_type": {
            "type": "software",
        },
        "publication_date": datetime.datetime.utcnow().date().isoformat(),
        "title": {"cs-cz": "Test", "cs": "Test"},
        "creators": [{"name": "Test"}],
        "description": {"en": "My description"},
        "license": {
            "identifier": "MIT",
            "license": ""
        },
        "access_right": "open",
    }
