#!/bin/bash
python bela_order_organizer.py -f $1
cd labels_tex
pdflatex addres_label_14_a4 > /dev/null
mv addres_label_14_a4.pdf ../
