#!/bin/bash -eux

WORK_DIR=$(pwd)
DEPLOY_ID=$(echo "obase=16; $(date +%s%3N)" | bc | tr '[:upper:]' '[:lower:]')

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

TEMP_DIR="${PWD}/tmp"
mkdir -p "${TEMP_DIR}"
if [ ! -f "${TEMP_DIR}/deploy_id" ]; then
  echo "${DEPLOY_ID}" > "${TEMP_DIR}/deploy_id"
else
  DEPLOY_ID=$(cat "${TEMP_DIR}/deploy_id")
fi

# Generate a temporary SSH key pair
TEMP_PRIVATE_KEY_NAME="temporary_key"
TEMP_PUBLIC_KEY_NAME="${TEMP_PRIVATE_KEY_NAME}.pub"

if [ ! -f "${TEMP_DIR}/${TEMP_PRIVATE_KEY_NAME}" -a ! -f "${TEMP_DIR}/${TEMP_PUBLIC_KEY_NAME}" ]; then
  echo "creating temporary SSH public-private key pair (name: ${TEMP_PRIVATE_KEY_NAME})"
  ssh-keygen -q -b 2048 -t rsa -f "${TEMP_DIR}/${TEMP_PRIVATE_KEY_NAME}" -N ""
fi

# Start the provisioning process
terraform apply\
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