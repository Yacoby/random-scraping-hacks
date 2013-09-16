#!/bin/sh
curl http://localhost:2001/schedule.json -d project=bike -d spider=$1
