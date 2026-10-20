from itertools import islice

from texttable import Texttable


def render_table(headers, rows, max_rows):
    """
    render rows as text table. at most max_rows rows are rendered
    """
    rows = list(islice(rows, max_rows + 1))
    truncated = len(rows) > max_rows
    rows = rows[:max_rows]
    columns = len(headers) if headers else max((len(row) for row in rows), default=0)
    if columns == 0:
        return ''
    # pgspecial may return rows of different length (e.g. the \h listing)
    rows = [list(row) + [''] * (columns - len(row)) for row in rows]
    table = Texttable(max_width=0)
    table.set_cols_align(['l'] * columns)
    table.set_cols_valign(['m'] * columns)
    if headers:
        table.header(headers)
    table.add_rows(rows, header=False)
    output = table.draw()
    if truncated:
        output += f'\nOnly the first {max_rows} rows are shown.'
    return output


def pretty_print(cursor, max_rows):
    if cursor.description is not None:
        columns = [col[0] for col in cursor.description]
        return render_table(columns, cursor.fetchmany(max_rows + 1), max_rows)
    return ''


def pretty_print_special(results, max_rows):
    """
    render the (title, rows, headers, status) tuples returned by pgspecial
    """
    parts = []
    for title, rows, headers, status in results:
        if title:
            parts.append(title)
        if rows is not None:
            parts.append(render_table(headers, rows, max_rows))
        if status:
            parts.append(str(status))
    return '\n'.join(parts)
