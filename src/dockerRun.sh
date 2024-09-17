docker run -dit -p 8080:8080 \
    -e OPENAI_API_KEY=${OPEN_API_KEY} \
    -e ENTREZ_EMAIL=${ENTREZ_EMAIL} \
    -e ENTREZ_API_KEY=${ENTREZ_API_KEY} \
    sragent:dev /bin/bash