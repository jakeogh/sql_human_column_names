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


#import os
import sys

import click
from kcl.sqlalchemy.self_contained_session import create_postgresql_database
from kcl.sqlalchemy.self_contained_session import start_database
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.pool import NullPool

#from decimal import Decimal
#from pathlib import Path
#from kcl.pathops import path_is_block_special
#from getdents import files
#from typing import Generator
#from typing import List
#from typing import Sequence



def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
except ImportError:
    ic = eprint


@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option("--printn", is_flag=True)
@click.option("--all", 'all_types', is_flag=True)
@click.pass_context
def cli(ctx,
        verbose: bool,
        debug: bool,
        printn: bool,
        all_types: bool):

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

    start_database(verbose=False, debug=False,)
    db_url = ctx.obj['database_uri']
    engine = create_engine(db_url,
                           poolclass=NullPool,
                           echo=ctx.obj['verbose'],
                           future=True,)
    create_postgresql_database(db_url)
    with engine.connect() as conn:
        if all_types:
            results = \
                conn.execute(text('select * from pg_type'))
        else:
            results = \
                conn.execute(text('select pg_type.typname, format_type(pg_type.oid, -1), pg_type.typlen, pg_type.typtype from pg_type where typisdefined and typarray!=:z and typtype!=:a and not typname like :x and not typname not like :b'), {"z": 0, "a": "d", "x": 'reg%', "b": 'bpchar'})
                #conn.execute(text('select pg_type.typname, format_type(pg_type.oid, -1), pg_type.typlen, pg_type.typtype from pg_type where typisdefined and typarray!=:z and typtype!=:a and not typname like :x'), {"z": 0, "a": "d", "x": 'reg%'})
                #conn.execute(text('select pg_type.typname, pg_type.typlen, pg_type.typtype from pg_type where typisdefined and typarray!=:z and typtype!=:a and not typname like :x'), {"z": 0, "a": "d", "x": 'reg%'})
                #conn.execute(text('select pg_type.typname, pg_type.typlen, pg_type.typtype from pg_type where typisdefined and typarray!=:z and typtype!=:a and not typispreferred'), {"z": 0, "a": 'd'})
                #conn.execute(text('select pg_type.typname, pg_type.typlen, pg_type.typtype from pg_type where typisdefined=:y and typarray!=:z and typtype!=:a'), {"y": True, "z": 0, "a": 'd'})
        for result in results:
            print(result)

