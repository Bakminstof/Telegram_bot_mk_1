FROM ubuntu:20.04

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/nginx.conf

COPY /SSL /etc/nginx/SSL/

WORKDIR /etc/nginx

EXPOSE 443

CMD ["nginx"]
