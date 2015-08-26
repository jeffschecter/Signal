#!/bin/bash

pylint --rcfile=lint.rc handlers
pylint --rcfile=lint.rc storage
pylint --rcfile=lint.rc app.py
