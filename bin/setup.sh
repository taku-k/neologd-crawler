#!/bin/bash
set -e

ROOT=`cd $(dirname $0) && cd .. && pwd`

if [ ! -d "${ROOT}/mecab-ipadic-neologd" ]; then
    git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
    for f in `ls -d ${PWD}/mecab-ipadic-neolod/seed/*`; do
        xz -d ${f};
    done;
fi
