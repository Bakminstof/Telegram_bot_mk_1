FROM python:3.10.5

RUN /usr/local/bin/python -m pip install --upgrade pip
#RUN pip install pyyaml ua-parser user-agents
COPY requirements.txt /bot/

RUN pip install -r /bot/requirements.txt

COPY bot_mk_1/ /bot/

WORKDIR /bot

EXPOSE 3333

CMD ["/usr/local/bin/python", "bot.py"]
