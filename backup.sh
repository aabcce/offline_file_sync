#!/bin/bash

if [ ! -d $HOME/envlinux ]
then
  tar xlvf ../envlinux.tar.gz -C $HOME
fi

$HOME/envlinux/bin/python harness.py --task=backup


