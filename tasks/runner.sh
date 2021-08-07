#!/bin/bash
cd ~/tasks
touch $1.inprogress
bash $1.task
rm $1.inprogress
