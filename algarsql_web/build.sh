    echo "*** gerando AlgarSQL"

    rm AlgarSQL
    rm __pycache__ -rf
    zip -r AlgarSQL.zip * -x AlgarSQL.db
    
    echo '#!/usr/bin/env python3' | cat - AlgarSQL.zip > AlgarSQL
    chmod 755 AlgarSQL
    rm AlgarSQL.zip