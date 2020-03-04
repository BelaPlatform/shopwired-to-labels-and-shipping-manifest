#!/bin/bash
set -e
PDF=addres_label_14_a4.pdf
ZIP=orders-labels-manifest.zip

[ -z "$1" ] && { echo "Specify input file: \``basename $0` <filename.csv>'"; exit 1; }
OUTPUTS="$PDF items_to_ship.txt order_info.txt MANIFEST.csv NEW_ORDER.csv"
rm -rf labels_tex/$PDF $OUTPUTS $ZIP
python bela_order_organizer.py -f $1
cd labels_tex
pdflatex addres_label_14_a4 > /dev/null || { echo "Error while building the pdf"; exit 1; }
mv $PDF ../
cd ..
printf "1 pdf file was created:\n\t$PDF containing address labels\n"
zip -rq $ZIP $OUTPUTS
printf "1 zip file was created:\n\t$ZIP containing all the above\n"
