perl -i -pe 's#(One Empty Record"/>)#\1\n        <style name="UnicodeBase" isDefault="true"\n         fontName="DejaVu Sans"\n         pdfFontName="/fonts/DejaVuSans.ttf"\n         pdfEncoding="Identity-H"\n         isPdfEmbedded="true"/>\n#;'  "$1.jrxml" ; rm -rf "$1.jasper" 

