#!/bin/sh
sudo rm -r hubDatabase.sql
sudo python CreateDatabase.py&
sudo python masterServer.py&

