#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement


import os
import sys
from decimal import Decimal
from pathlib import Path
#from kcl.pathops import path_is_block_special
#from getdents import files
from typing import Generator
from typing import List
from typing import Sequence

import click
from enumerate_input import enumerate_input
#from collections import defaultdict
#from prettyprinter import cpprint, install_extras
#install_extras(['attrs'])
from kcl.configops import click_read_config
from kcl.configops import click_write_config_entry
from kcl.sqlalchemy.delete_database import \
    delete_database as really_delete_database
from kcl.sqlalchemy.model.BaseMixin import BASE
from kcl.sqlalchemy.self_contained_session import create_postgresql_database
from kcl.sqlalchemy.self_contained_session import database_already_exists
from kcl.sqlalchemy.self_contained_session import self_contained_session
from kcl.sqlalchemy.self_contained_session import start_database
from kcl.userops import not_root
from retry_on_exception import retry_on_exception
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy_utils.functions import create_database


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
except ImportError:
    ic = eprint


# import pdb; pdb.set_trace()
# from pudb import set_trace; set_trace(paused=False)

global APP_NAME
APP_NAME = 'unitinv'


#@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option("--printn", is_flag=True)
@click.group()
@click.pass_context
def cli(ctx,
        verbose: bool,
        debug: bool,
        printn: bool,):

    global APP_NAME
    null = not printn
    end = '\n'
    if null:
        end = '\x00'
    if sys.stdout.isatty():
        end = '\n'

    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    ctx.obj['null'] = null
    ctx.obj['database_uri'] = 'postgresql://postgres@localhost/' + APP_NAME


@cli.command()
@click.pass_context
def ipython_core(ctx):
    start_database(verbose=False, debug=False,)
    db_url = ctx.obj['database_uri']
    engine = create_engine(db_url, poolclass=NullPool, echo=ctx.obj['verbose'], future=True)
    create_postgresql_database(db_url)
    #if not database_already_exists(ctx.obj['database_uri']):  # executes SELECT 1 FROM pg_database WHERE datname='path_test_1520320264'
    #    print("creating empty database:", db_url)
    #create_database(db_url)  # https://github.com/kvesteri/sqlalchemy-utils/issues/474
    with engine.connect() as conn:
        conn.execute('CREATE DATABASE ' + db_url)
        conn.commit()
        result = conn.execute(text("select 'hello world'"))
        print(result.all())
        import IPython; IPython.embed()

@cli.command()
@click.pass_context
def delete_database(ctx):
    start_database(verbose=False, debug=False,)
    really_delete_database(ctx.obj['database_uri'])

#@cli.command()
#@click.pass_context
#def ipython_orm(ctx):
#    with self_contained_session(db_url=ctx.obj['database_url'], future=True) as session:
#        if ctx.obj['verbose']:
#            ic(session)
#
#        import IPython; IPython.embed()
#
#        try:
#            # Use back quotes as a protection against SQL Injection Attacks. Can we do more?
#            session.bind.execute('ALTER TABLE %s ADD COLUMN %s %s' %
#                                      ('`' + self.tbl.schema + '`.`' + self.tbl.name + '`',
#                                       '`' + self.outputs[new_col] + '`', 'VARCHAR(50)'))
#        except exc.SQLAlchemyError as e:
#            #ic(e)
#            raise e
#        try:    # Refresh the metadata to show the new column
#            self.tbl = sqlalchemy.Table(self.tbl.name, self.tbl.metadata, extend_existing=True, autoload=True)
#        except exc.SQLAlchemyError as e:
#            #ic(e)
#            raise e
