#!/bin/bash
set -e

DOCKER_REPO=${CONTAINER_REGISTRY:-}
DOCKER_USER=${CONTAINER_USER:-pcm32}

# Uncomment to push intermediate images, otherwise only the images needed for the helm chart are pushed.
#PUSH_INTERMEDIATE_IMAGES=yes

if [[ ${#DOCKER_REPO} > 0 ]];
then
    if [[ ! "$DOCKER_REPO" == */ ]];
    then
        DOCKER_REPO=$DOCKER_REPO"/"
    fi
fi


ANSIBLE_REPO=galaxyproject/ansible-galaxy-extras
ANSIBLE_RELEASE=18.01-k8s
GALAXY_VER_FOR_POSTGRES=18.01
POSTGRES_VERSION=`grep FROM docker-galaxy-stable/compose/galaxy-postgres/Dockerfile | awk -F":" '{ print $2 }'`
GALAXY_BASE_FROM_TO_REPLACE=quay.io/bgruening/galaxy-base:18.01

TAG=v18.01
# Uncomment to avoid using the cache when building docker images.
#NO_CACHE="--no-cache"

if [[ ! -z ${CONTAINER_TAG_PREFIX+x} ]];
then
	if [[ ! -z ${BUILD_NUMBER+x} ]];
	then
            TAG=${CONTAINER_TAG_PREFIX}.${BUILD_NUMBER}
        fi
fi


GALAXY_BASE_TAG=$DOCKER_REPO$DOCKER_USER/galaxy-base:$TAG

if [ -n $ANSIBLE_REPO ]
    then
       echo "Making custom galaxy-base:$TAG from $ANSIBLE_REPO at $ANSIBLE_RELEASE"
       docker build $NO_CACHE --build-arg ANSIBLE_REPO=$ANSIBLE_REPO --build-arg ANSIBLE_RELEASE=$ANSIBLE_RELEASE -t $GALAXY_BASE_TAG docker-galaxy-stable/compose/galaxy-base/
       if [[ ! -z ${PUSH_INTERMEDIATE_IMAGES+x} ]];
       then
	   echo "Pushing intermediate image $DOCKER_REPO$DOCKER_USER/galaxy-base:$TAG"
           docker push $GALAXY_BASE_TAG
       fi
fi

GALAXY_RELEASE=release_18.01
GALAXY_REPO=galaxyproject/galaxy

GALAXY_INIT_TAG=$DOCKER_REPO$DOCKER_USER/galaxy-init:$TAG

if [ -n $GALAXY_REPO ]
    then
       echo "Making custom galaxy-init:$TAG from $GALAXY_REPO at $GALAXY_RELEASE"
       DOCKERFILE_INIT_1=Dockerfile
       if [ -n $ANSIBLE_REPO ]
          then
         sed s+$GALAXY_BASE_FROM_TO_REPLACE+$GALAXY_BASE_TAG+ docker-galaxy-stable/compose/galaxy-init/Dockerfile > docker-galaxy-stable/compose/galaxy-init/Dockerfile_init
	       FROM=`grep ^FROM docker-galaxy-stable/compose/galaxy-init/Dockerfile_init | awk '{ print $2 }'`
	       echo "Using FROM $FROM for galaxy init"
	       DOCKERFILE_INIT_1=Dockerfile_init
       fi
       docker build $NO_CACHE --build-arg GALAXY_REPO=$GALAXY_REPO --build-arg GALAXY_RELEASE=$GALAXY_RELEASE -t $GALAXY_INIT_TAG -f docker-galaxy-stable/compose/galaxy-init/$DOCKERFILE_INIT_1 docker-galaxy-stable/compose/galaxy-init/
       #if [[ ! -z ${PUSH_INTERMEDIATE_IMAGES+x} ]];
       #then
	       echo "Pushing intermediate image $GALAXY_INIT_TAG"
         docker push $GALAXY_INIT_TAG
       #fi
fi

# GALAXY_INIT_FLAVOURED_TAG=$DOCKER_REPO$DOCKER_USER/galaxy-init-flavoured:$TAG
#
# DOCKERFILE_INIT_FLAVOUR=Dockerfile_init
# if [ -n $GALAXY_REPO ]
# then
# 	echo "Making custom galaxy-init-pheno-flavoured:$TAG starting from galaxy-init-pheno:$TAG"
# 	sed s+pcm32/galaxy-init$+$GALAXY_INIT_PHENO_TAG+ Dockerfile_init > Dockerfile_init_tagged
# 	DOCKERFILE_INIT_FLAVOUR=Dockerfile_init_tagged
# fi
# docker build $NO_CACHE -t $GALAXY_INIT_FLAVOURED_TAG -f $DOCKERFILE_INIT_FLAVOUR .
# docker push $GALAXY_INIT_PHENO_FLAVOURED_TAG

GALAXY_WEB_K8S_TAG=$DOCKER_REPO$DOCKER_USER/galaxy-web-k8s:$TAG

DOCKERFILE_WEB=Dockerfile
if [ -n $GALAXY_REPO ]
then
	echo "Making custom galaxy-web-k8s:$TAG from $GALAXY_REPO at $GALAXY_RELEASE"
	sed s+$GALAXY_BASE_FROM_TO_REPLACE+$GALAXY_BASE_TAG+ docker-galaxy-stable/compose/galaxy-web/Dockerfile > docker-galaxy-stable/compose/galaxy-web/Dockerfile_web
	DOCKERFILE_WEB=Dockerfile_web
fi
docker build $NO_CACHE --build-arg GALAXY_ANSIBLE_TAGS=supervisor,startup,scripts,nginx,k8,k8s -t $GALAXY_WEB_K8S_TAG -f docker-galaxy-stable/compose/galaxy-web/$DOCKERFILE_WEB docker-galaxy-stable/compose/galaxy-web/
docker push $GALAXY_WEB_K8S_TAG

# Build postgres
POSTGRES_TAG=$DOCKER_REPO$DOCKER_USER/galaxy-postgres:$POSTGRES_VERSION"_for_"$GALAXY_VER_FOR_POSTGRES
docker build -t $POSTGRES_TAG -f docker-galaxy-stable/compose/galaxy-postgres/Dockerfile docker-galaxy-stable/compose/galaxy-postgres/
docker push $POSTGRES_TAG

# Build proftpd
PROFTPD_TAG=$DOCKER_REPO$DOCKER_USER/galaxy-proftpd:for_galaxy_v$GALAXY_VER_FOR_POSTGRES
docker build -t $PROFTPD_TAG -f docker-galaxy-stable/compose/galaxy-proftpd/Dockerfile docker-galaxy-stable/compose/galaxy-proftpd/
docker push $PROFTPD_TAG


echo "Relevant containers:"
echo "Web:          $GALAXY_WEB_K8S_TAG"
echo "Init:         $GALAXY_INIT_TAG"
echo "Postgres:     $POSTGRES_TAG"
echo "Proftpd:      $PROFTPD_TAG"
