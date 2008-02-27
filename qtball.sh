#!/bin/sh
git gc
cd ..
tar cvjf /home/tarbox/Desktop/qtreactor.tar.bz2 --exclude=.git --exclude='*pyc' qtreactor
