#!/usr/bin/python
from argparse import ArgumentParser
from subprocess import call
from termcolor import colored
from os import environ

def set_vars(args):
    with open('external_vars.yaml', 'w') as f:
        for key, value in args.__dict__.items():
            if value is not None:
                f.write('{}: {}\n'.format(str(key), str(value)))

if(__name__ == '__main__'):
    ######Parsing command line aurguements######
    parser = ArgumentParser(description='This script is used to install jenkins helm chart')
    parser.add_argument('--namespace', required=True, help='k8s namespace')
    parser.add_argument('--domain', required=True, help='Domain name like abc.xyz')
    parser.add_argument('--env_var', required=True, help='Environment type')
    parser.add_argument('--gcp_project_id', required=True, help='GCP Project ID')
    parser.add_argument('--dnsPod', action='store_true', help='Create External DNS pod')
    parser.add_argument('--staticIP', action='store_true', help='Global static IP for LB')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--create', action='store_true', help='Install helm chart')
    action.add_argument('--delete', action='store_true', help='Uninstall helm chart')
    args = parser.parse_args()
    service_account_file = "~/Downloads/service-exploration-280814-57f53738df29.json"
    environ['gcp_service_account_file'] = service_account_file
    set_vars(args)
    if args.create:
        print(colored('Installing jenkins helm chart','yellow'))
        call("ansible-playbook deploy_jenkins_chart.yaml", shell=True)
    elif args.delete:
        print(colored('Uninstalling jenkins helm chart','yellow'))
        call("ansible-playbook deploy_jenkins_chart.yaml", shell=True)