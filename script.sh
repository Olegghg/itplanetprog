#!/bin/bash
docker compose down
docker image rm -f docker-test2-app:latest
docker volume rm docker-test2_kea-db_data
docker compose up -d
