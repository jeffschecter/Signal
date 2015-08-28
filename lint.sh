#!/bin/bash

pylint \
  --rcfile=lint.rc \
  --msg-template="{module}:{line}.{column} {msg_id} {symbol}: {msg}"\
  handlers storage common
