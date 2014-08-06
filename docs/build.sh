#!/bin/sh


export LC_ALL=zh_CN.UTF-8

make html

################################################
#The making of latex by default is disabled,
#you can enable this if you want to build pdf
################################################
#cd _build/latex
#xelatex *.tex
#cp {{ project_name }}.pdf ../.

