#!/usr/bin/env bash
openssl genrsa -out SSL/webhook_pkey.pem 2048 &&\
openssl req -new -x509 -nodes -days 3650 -key SSL/webhook_pkey.pem -out SSL/webhook_cert.pem

scp SSL/webhook_pkey.pem bot/SSL/webhook_pkey.pem
scp SSL/webhook_cert.pem bot/SSL/webhook_cert.pem

scp SSL/webhook_pkey.pem nginx/SSL/webhook_pkey.pem
scp SSL/webhook_cert.pem nginx/SSL/webhook_cert.pem