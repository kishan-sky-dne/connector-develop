#!/usr/bin/env bash
echo "Applying environment changes"
if [[ $CI_COMMIT_REF_NAME == "master" ]] ; then
## setting variables ###
   sed -i "s#tokenUrl.*#tokenUrl: $MASTER_OAUTH_URL#" "${CI_PROJECT_DIR}"/openapi/openapi.yaml;
   sed -i "s#jwt_pub_key.*#jwt_pub_key=/app/jwt-key-master.pub#" "${CI_PROJECT_DIR}"/docker/connectors/config/connectors.conf;
   sed -i "s#auth.ts.isp.sky.com#cauth.bmtapps.bskyb.com#" "${CI_PROJECT_DIR}"/docker/connectors/config/connectors.conf;
fi

echo "Building ${CI_PROJECT_NAME} image"
docker rm -f connectors-develop
make build-docker

# verifying the container runs only on the develop branch
if [ "${CI_COMMIT_REF_NAME}" = "develop" ]
then
     echo "Running docker command to start ${CI_PROJECT_NAME}"
     make kill-docker
     make run-docker

     address="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}' ${CI_PROJECT_NAME}-"${CI_COMMIT_REF_NAME}")"

     echo "📀 Connecting to ${CI_PROJECT_NAME} on ${address}"
     for try in $(seq 1 360)
     do
         echo "Retrying ${try} time"
         # added max-timeout of 15 seconds to curl so that it does not hang forever if the container keeps on reloading
         HTTP_STATUS_CODE=$(curl --noproxy "*" -k -v -f -s -L -o /dev/null -I -w "%{http_code}" -m 15 http://"${address}":5000/api/v1/healthcheck)
         echo "HTTP Status Code: ${HTTP_STATUS_CODE}"
         if [ "${HTTP_STATUS_CODE}" = 200 ]
         then
             echo "🙌 Sucessfully connected to ${CI_PROJECT_NAME} container, skipping the remaining retries."
             break
         elif [ "${HTTP_STATUS_CODE}" = 502 ]
         then
             echo "🔥 Could'nt connect to ${CI_PROJECT_NAME} container, retrying after 10 seconds"
             echo "💤 Sleeping for 10 seconds"
             sleep 10
         else
             echo "🐞 Could'nt connect to ${CI_PROJECT_NAME} container after ${try} attempts, failing the test as the ${CI_PROJECT_NAME} image has
             issues and failing to connect with the http status code as ${HTTP_STATUS_CODE}."
             echo "Below are the logs from the failed ${CI_PROJECT_NAME} container for debugging purpose"
             sleep 10
             docker logs "${CI_PROJECT_NAME}"-"${CI_COMMIT_REF_NAME}"
             echo "Now, exiting with an error-code of 1"
             exit 1
         fi
     done
     make kill-docker
fi

echo "Pushing ${CI_PROJECT_NAME} image to the FC registry with the tag ${CI_COMMIT_REF_NAME}"
make push-registry-fc
