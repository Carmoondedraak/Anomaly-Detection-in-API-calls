#!/bin/bash

caddy stop 2>&1 > ~/.caddy.log 2>&1 &

caddy start --config /home/developer/bin/Caddyfile > ~/.caddy.log 2>&1 &
