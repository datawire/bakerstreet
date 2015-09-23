#!/bin/bash -eux

WORK_DIR=$(pwd)
TEMP_DIR="${PWD}/tmp"
DEPLOY_ID=$(cat $TEMP_DIR/deploy_id)

for i in "$@"; do
  case $i in
    -w=*|--work-directory=*)
      WORK_DIR="${i#*=}"
    shift
    ;;
    -i=*|--deploy-id=*)
      DEPLOY_ID="${i#*=}"
    shift
    ;;
    *)
      echo "unknown option (option: $i)"
      exit 1
    ;;
  esac
done

terraform destroy --force\
  -var-file=at.tfvars\
  -var "package_repository=datawire/stable"\
  -var "aws_access_key=${AWS_ACCESS_KEY_ID}"\
  -var "aws_secret_key=${AWS_SECRET_ACCESS_KEY}"\
  -var "deploy_id=${DEPLOY_ID}"\
  -var "proton_rpm=${TEMP_DIR}/datawire-proton.rpm"\
  -var "datawire_rpm=${TEMP_DIR}/datawire.rpm"\
  -var "directory_rpm=${TEMP_DIR}/datawire-directory.rpm"\
  -var "watson_rpm=${TEMP_DIR}/datawire-watson.rpm"\
  -var "sherlock_rpm=${TEMP_DIR}/datawire-sherlock.rpm"\
  "${WORK_DIR}"