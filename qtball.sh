#!/bin/sh
git gc
cd ..
tar cvjf /home/tarbox/Desktop/qtreactor.tar.bz2 --exclude='.*' --exclude='*pyc' qtreactor
