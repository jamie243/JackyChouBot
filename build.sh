#!/bin/bash
mkdir -p $HOME/sqlite3
curl -L https://www.sqlite.org/2024/sqlite-tools-linux-x86-3410000.zip -o sqlite-tools.zip
unzip sqlite-tools.zip -d $HOME/sqlite3
export PATH="$HOME/sqlite3/sqlite-tools-linux-x86-3410000:$PATH"
pip install -r requirements.txt
