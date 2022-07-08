FROM python:3.10.5

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install uwsgi

COPY requirements.txt /api/

RUN pip install -r /api/requirements.txt

COPY api/ /api/

COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

WORKDIR /api

EXPOSE 3003

CMD ["/usr/local/bin/uwsgi", "--ini", "/etc/uwsgi/uwsgi.ini"]
