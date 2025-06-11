 mkdir /tmp/pdfs
 fd -e pdf -ls | grep 'שופרסל' | awk '$5 ~ /M$/' | sort -h -k 5  | sed 's/.* .\//.\//'  | while read filename; do     gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=/tmp/pdfs/"$(basename "$filename")" "$filename"; done
 echo Saved new receipts in /tmp/pdfs
