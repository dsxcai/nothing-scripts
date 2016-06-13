#!/usr/bin/env bash

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <workspace> <product> <suffix>"
else
    test -n "$3" && _suf="-$3" || _suf=""
    _path="$(date +%Y%m%d%H%M%S)$_suf"
    mkdir -p $_path
    ( cd $_path; scp_imgs $1 $2 )
    echo $_path
fi
