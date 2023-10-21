poetry build-project

pushd projects/terec_api
poetry build-project
docker build . -t terec/api:latest
popd
