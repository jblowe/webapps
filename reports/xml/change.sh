perl -i -pe 's#<imageExpression><..CDATA..http.//. . .P.cspace_server. . +./fetchimage/index.php.csid=. . .F{blobcsid}..><.imageExpression>#<imageExpression><\!\[CDATA\["http://" + \$P{cspace_server} \+ ":8080/omca/imageserver/blobs/" \+ \$F{blobcsid} + "/derivatives/Medium/content"\]\]></imageExpression>#' *.jrxml

