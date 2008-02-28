#!/bin/sh
cd ..
tar cvjf /tmp/qtreactor.tar.bz2 --exclude='.*' --exclude='*pyc' --exclude=_trial_temp qtreactor
