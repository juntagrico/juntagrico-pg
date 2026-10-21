import logging
from contextlib import suppress

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from pgspecial.main import PGSpecial, parse_special_command

from juntagrico_pg.util.output import pretty_print, pretty_print_special

logger = logging.getLogger(__name__)

# psql meta commands that only read the catalog. others (e.g. \copy, \i, \o) access files or change settings
ALLOWED_SPECIAL_COMMANDS = (
    '\\d', '\\dt', '\\dv', '\\dm', '\\di', '\\ds', '\\df', '\\dn', '\\du', '\\dx', '\\dT', '\\l', '\\h',
)


@permission_required('juntagrico_pg.can_sql')
def home(request):
    return render(request, "jpg/home.html")


@permission_required('juntagrico_pg.can_sql')
@require_POST
def execute_sql(request):
    sql = request.POST.get('sql', '')
    max_rows = getattr(settings, 'JPG_MAX_ROWS', 1000)
    logger.info('SQL by %s (id %s): %s', request.user, request.user.pk, sql)
    try:
        with connection.cursor() as cur:
            set_statement_timeout(cur)
            try:
                if sql.startswith('\\'):
                    output = execute_special(cur, sql, max_rows)
                else:
                    cur.execute(sql)
                    output = pretty_print(cur, max_rows)
                    output += '\n'
                    output += 'ROWS: ' + str(cur.rowcount)
            finally:
                reset_statement_timeout(cur)
    except Exception as e:
        logger.warning('SQL by %s (id %s) failed: %s', request.user, request.user.pk, e)
        output = str(e)
    response = HttpResponse(output, content_type='text/plain; charset=utf-8')
    response['X-Content-Type-Options'] = 'nosniff'
    return response


def execute_special(cur, sql, max_rows):
    command = parse_special_command(sql)[0]
    if command not in ALLOWED_SPECIAL_COMMANDS:
        return f'Command {command} is not supported. Supported commands: {" ".join(ALLOWED_SPECIAL_COMMANDS)}'
    return pretty_print_special(PGSpecial().execute(cur, sql), max_rows)


def set_statement_timeout(cur):
    timeout = getattr(settings, 'JPG_STATEMENT_TIMEOUT', 30000)
    if timeout and connection.vendor == 'postgresql':
        cur.execute("SELECT set_config('statement_timeout', %s, false)", [str(timeout)])


def reset_statement_timeout(cur):
    # the connection may be reused by later requests. fails if the user left an aborted transaction
    if connection.vendor == 'postgresql':
        with suppress(DatabaseError):
            cur.execute('RESET statement_timeout')
