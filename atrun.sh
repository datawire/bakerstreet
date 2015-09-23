#!/bin/bash

TEST_RUNNER_PUBLIC_IP=$(terraform output test_runner_public_ip)
TEST_SERVICE_PRIVATE_IP=$(terraform output test_service_private_ip)

ssh -o StrictHostKeyChecking=no -i tmp/temporary_key centos@${TEST_RUNNER_PUBLIC_IP} "py.test /home/centos/test_bakerstreet.py --wc-host=${TEST_SERVICE_PRIVATE_IP}:5002 --junitxml=/home/centos/test_bakerstreet.xml"
scp -o StrictHostKeyChecking=no -i tmp/temporary_key centos@${TEST_RUNNER_PUBLIC_IP}:/home/centos/test_bakerstreet.xml .
