#!/bin/bash
set -e
PDF=addres_label_14_a4.pdf

[ -z "$1" ] && { echo "Specify input file: \``basename $0` <filename.csv>'"; exit 1; }
rm -rf $PDF labels_tex/$PDF
python bela_order_organizer.py -f $1
cd labels_tex
pdflatex addres_label_14_a4 > /dev/null || { echo "Error while building the pdf"; exit 1; }
mv $PDF ../
printf "1 pdf file was created:\n\t$PDF containing address labels\n"
