import asyncio
import flask.json

from flask import Flask, request
from sqlalchemy import select

from logs_schema import BaseLoggerTable, a_session_log

CURRENT_LOG_ID: int = 0

app = Flask(__name__)


@app.route('/api/logs', methods=['GET'])
def collect_logs():
    first = request.args.get('first', type=int)

    global CURRENT_LOG_ID

    stmt = select(
        BaseLoggerTable.id,
        BaseLoggerTable.level,
        BaseLoggerTable.name,
        BaseLoggerTable.dtime,
        BaseLoggerTable.line,
        BaseLoggerTable.message,
        BaseLoggerTable.exec_text
    )

    if first:
        result = asyncio.run(a_session_log.execute(stmt))
    else:
        result = asyncio.run(a_session_log.execute(stmt.filter(BaseLoggerTable.id > CURRENT_LOG_ID)))

    log_rows = result.all()

    logs = []

    for row in log_rows:
        id_ = row[0]

        # log = '{id}, {lvl}, {name}, {dtime}, {line}, {msg}'.format(
        #     id=id_,
        #     lvl=row[1],
        #     name=row[2],
        #     dtime=row[3],
        #     line=row[4],
        #     msg=row[5],
        # )

        log = {
            'id': id_,
            'lvl': row[1],
            'name': row[2],
            'time': row[3],
            'line': row[4],
            'msg': row[5],
            'exec': row[6]
        }

        logs.append(log)

        CURRENT_LOG_ID = id_

    return flask.json.dumps(logs), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
