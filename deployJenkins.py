#!/usr/bin/python
from argparse import ArgumentParser
from subprocess import call
from termcolor import colored
import os
from google.cloud import storage

def set_vars(args):
    if args.addUsers or args.removeUsers:
        varsList = ["gcp_project_id", "addUsers", "removeUsers"]
        with open('terraform.tfvars', 'w') as f:
            for key, value in args.__dict__.items():
                if value is not None and key in varsList:
                    if isinstance(value, list):
                        f.write('{} = {}\n'.format("users", str(value)).replace("'", '"'))
                        continue
                    f.write('{} = "{}"\n'.format(key, value))
        return
    with open('external_vars.yaml', 'w') as f:
        for key, value in args.__dict__.items():
            if value is not None:
                f.write('{}: {}\n'.format(str(key), str(value)))

def addUsers():
    currentDir = os.getcwd()
    os.chdir(os.path.join(currentDir, 'IAP/terraform_scripts'))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file
    fileName = 'users.txt'
    bucketName = 'storage-lab-free'
    users = None
    downloadFileFromGStorage(fileName, bucketName)
    with open(fileName, 'r') as f:
        users = f.readlines()
    for user in args.addUsers:
        users.append(user)
    updatedList = set()
    for user in users:
        updatedList.add(user.strip('\n'))
    updatedList = list(updatedList)
    args.addUsers = updatedList
    set_vars(args)
    if args.init:
        returnCode = call("terraform init", shell=True)
        exit(0)
    returnCode = call("terraform apply -auto-approve", shell=True)
    if returnCode > 0:
        print(colored('Error occured. Exiting..', 'red'))
        exit(1)
    with open(fileName, 'w') as f:
        for user in updatedList:
            f.write(user + '\n')
    uploadFiletoGStorage(fileName, bucketName)


def removeUsers():
    currentDir = os.getcwd()
    os.chdir(os.path.join(currentDir, 'IAP/terraform_scripts'))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file
    fileName = 'users.txt'
    bucketName = 'storage-lab-free'
    users = []
    downloadFileFromGStorage(fileName, bucketName)
    with open(fileName, 'r') as f:
        users = f.readlines()
    updatedList = []
    for user in users:
        updatedList.append(user.strip('\n'))
    for user in args.removeUsers:
        try:
            updatedList.remove(user)
        except ValueError:
            print(colored('The access of user {} is already revoked or It is not authorized user.'.format(user),'red'))
            exit(1)
    args.removeUsers = updatedList
    set_vars(args)
    if args.init:
        returnCode = call("terraform init", shell=True)
        exit(0)
    returnCode = call("terraform destroy -auto-approve", shell=True)
    with open(fileName, 'w') as f:
        for user in updatedList:
            f.write(user + '\n')
    uploadFiletoGStorage(fileName, bucketName)


def downloadFileFromGStorage(fileName, bucketName):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob(fileName)
    blob.download_to_filename(fileName)
    print("Blob {} downloaded.".format(fileName))

def uploadFiletoGStorage(fileName, bucketName):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    print("Blob {} uploaded.".format(fileName))

if(__name__ == '__main__'):
    ######Parsing command line aurguements######
    parser = ArgumentParser(description='This script is used to install jenkins helm chart')
    parser.add_argument('--namespace', required=True, help='k8s namespace')
    parser.add_argument('--domain', required=True, help='Domain name like abc.xyz')
    parser.add_argument('--env_var', required=True, help='Environment type')
    parser.add_argument('--gcp_project_id', required=True, help='GCP Project ID')
    parser.add_argument('--dnsPod', action='store_true', help='Create External DNS pod')
    parser.add_argument('--staticIP', action='store_true', help='Global static IP for LB')
    parser.add_argument('--addUsers', nargs='+', help='Give access to Users to IAP')
    parser.add_argument('--removeUsers', nargs='+', help='Revoke access to Users to IAP')
    parser.add_argument('--init', action='store_true', help='Terraform init')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--create', action='store_true', help='Install helm chart')
    action.add_argument('--delete', action='store_true', help='Uninstall helm chart')
    args = parser.parse_args()
    service_account_file = "/home/pankaj/Downloads/service-exploration-280814-57f53738df29.json"
    os.environ['gcp_service_account_file'] = service_account_file
    if args.addUsers:
        addUsers()
        exit(0)
    if args.removeUsers:
        removeUsers()
        exit(0)
    set_vars(args)
    if args.create:
        print(colored('Installing jenkins helm chart','yellow'))
        call("ansible-playbook deploy_jenkins_chart.yaml", shell=True)
    elif args.delete:
        print(colored('Uninstalling jenkins helm chart','yellow'))
        call("ansible-playbook deploy_jenkins_chart.yaml", shell=True)