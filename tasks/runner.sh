#!/bin/bash
cd ~/tasks
touch $1.inprogress
bash $1.task $2
rm $1.inprogress
