cd matscholar-vespa
mvn clean install 
cd ..
docker image build --tag matscholar-vespa .
docker image tag matscholar-vespa:latest registry.nersc.gov/m3624/matscholar-vespa:$1
docker image push registry.nersc.gov/m3624/matscholar-vespa:$1
