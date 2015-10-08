#!/usr/bin/env python

"""bakersim.py

Usage:
    bakersim build-pkg <name>
    bakersim build-image <dockerfile> -t <tag>
    bakersim push-image <tag>
    bakersim foo
    bakersim install-pkg <name>
    bakersim kube-up
    bakersim kube-down
    bakersim create <name>
    bakersim pod-info <name>
    bakersim simulate <profile>
    bakersim (-h | --help)

Options:
    --config    Use a specific configuration file
    -h --help   Show this screen
"""

import json
import logging
import os
import subprocess
import yaml

from docopt import docopt

script_dir = os.path.dirname(os.path.realpath(__file__))
dockerfile_dir = os.path.join(script_dir, 'docker')

base_kube_rc_config = {
    'apiVersion': 'v1',
    'kind': 'ReplicationController',
    'metadata': {},
    'spec': {}
}

base_kube_service_config = {
    'apiVersion': 'v1',
    'kind': 'Service',
    'metadata': {},
    'spec': {}
}

def print_process_output(proc):
    for line in iter(proc.stdout.readline, b''):
        print(">>> " + line.rstrip())

# ----------------------------------------------------------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------------------------------------------------------

def simulate(name, profile):
    print("Running simulation '{0}' - {1}".format(name, profile['description']))

    run_forever = profile.get('cycles', True)
    cycle = 1

    while run_forever is True or cycle <= int(profile['cycles']):
        print("cycle {}".format(cycle))

        cycle += 1

def add_services(count):
    pass

def add_clients(count):
    pass

def remove_services(count):
    pass

def remove_clients(count):
    pass

# ----------------------------------------------------------------------------------------------------------------------
# Stats Collection Server
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Bakerscale Commands
# ----------------------------------------------------------------------------------------------------------------------

def write_yaml(path, content, mode='w+'):
    with open(path, mode) as outfile:
        outfile.write(yaml.dump(content))

def pod_phase_is(pod, phase):
    info = pod_info(pod)
    if info['items'] and len(info['items']) == 1:
        return info['items'][0]['status']['phase'] == phase

def generate_base_rc_metadata(name):
    return {'name': name, 'namespace': 'default', 'labels': {'name': name}}

def generate_rc_spec(name, containers):
    return {
        'selector': {'name': name},
        'template': {
            'metadata': {
                'labels': {'name': name}
            }
        },
        'spec': {
            'containers': containers
        }
    }

def generate_bakerscale_client_rc(docker_image, directory_ip, name='bakerscale-client'):
    content = base_kube_rc_config.copy()
    content['metadata'] = generate_base_rc_metadata(name)
    content['spec'] = generate_rc_spec(name, [
        {
            'args': ["python", "bakerscale.py", "sherlock", directory_ip],
            'image': docker_image,
            'name': name
        }])


def generate_bakerscale_service_rc(docker_image, directory_ip, name='bakerscale-service'):
    content = base_kube_rc_config.copy()
    content['metadata'] = generate_base_rc_metadata(name)
    content['spec'] = generate_rc_spec(name, [
        {
            'args': ["python", "bakerscale.py", "watson", directory_ip,
                     "http://localhost:8080/", "hello", "http://localhost:8080/health"],
            'image': docker_image,
            'name': name
        },
        {
            'args': ["python", "bakerscale_service.py", "8080"],
            'image': docker_image,
            'name': name
        }])


def generate_directory_rc(docker_image, name='dw-directory'):
    content = base_kube_rc_config.copy()
    content['metadata'] = generate_base_rc_metadata(name)
    content['spec'] = generate_rc_spec(name, [
        {
            'args': ["python", "bakerscale.py", "directory"],
            'image': docker_image,
            'name': name,
            'ports': [
                {'containerPort': 5672}
            ]
        }
    ])

    rc_config_path = os.path.join(script_dir, 'directory-controller.yml')
    write_yaml(rc_config_path, content)
    return rc_config_path

def create_directory(config):
    proc = kubectl_cmd(['create', '-f', generate_directory_rc(config['image'])])
    out, err = proc.communicate()
    print(out)

def delete_directory():
    proc = kubectl_cmd(['delete', '-f', ''])
    out, err = proc.communicate()
    print(out)

def print_pod_ip(pod_name):
    info = pod_info(pod_name)
    if info['items']:
        pod = info['items'][0]
        status = pod['status']
        if status == 'Running':
            print(status['podIP'])


def pod_info(pod_name):
    proc = kubectl_cmd(['get', 'pods', '--output=json', '--selector=name={0}'.format(pod_name)])
    out, err = proc.communicate()

    result = json.loads(out)
    return result['items']


# ----------------------------------------------------------------------------------------------------------------------
# Kubernetes Commands
# ----------------------------------------------------------------------------------------------------------------------

def kube_cmd(command, env=None):
    cmd = "{0}/{1}/{2}".format(script_dir, "kubernetes/cluster", command)
    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)

    proc = subprocess.Popen(cmd,
                            cwd=script_dir,
                            env=cmd_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return proc

def kubectl_cmd(args_and_opts, env=None):
    cmd = ['kubectl']
    cmd.extend(args_and_opts)

    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)

    proc = subprocess.Popen(cmd,
                            cwd=script_dir,
                            env=cmd_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return proc

def kube_down():
    proc = kube_cmd("kube-down.sh", {'KUBERNETES_PROVIDER': 'aws'})
    print_process_output(proc)

def kube_up(kube_config):
    env = {
        'KUBERNETES_PROVIDER': 'aws',
        'MASTER_SIZE': kube_config['master_instance_type'],

        'MINION_SIZE': kube_config['node_instance_type'],
        'NUM_MINIONS': str(kube_config['node_count'])
    }

    proc = kube_cmd("kube-up.sh", env)
    print_process_output(proc)

# ----------------------------------------------------------------------------------------------------------------------
# Packaging and Docker Commands
# ----------------------------------------------------------------------------------------------------------------------

def build_docker_image(dockerfile):
    build_command = ['docker', 'build', '-f', '{0}/{1}'.format(dockerfile_dir, dockerfile), dockerfile_dir]

    pass

def build_pkg(name):
    work_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
    pkg_command = "{0}/{1}".format(work_dir, name)
    proc = subprocess.Popen(pkg_command, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print_process_output(proc)

def copy_pkg_to_docker_build_path():
    pass

# ----------------------------------------------------------------------------------------------------------------------
# Main Program Ceremony
# ----------------------------------------------------------------------------------------------------------------------

def main(args):
    config_file = args.get('config', "{0}/bakersim.yml".format(script_dir))
    config = None
    with open(config_file, 'r') as fs:
        config = yaml.load(fs)

    if args['kube-down']:
        kube_down()
        exit(0)

    if args['kube-up']:
        kube_up(config['kubernetes'])
        exit(0)

    if args['pod-info']:
        {
            'directory': print_pod_ip,
            'bakerscale-service': print_pod_ip,
            'bakerscale-client': print_pod_ip,
        }[args['<name>']](args['<name>'])
        exit(0)

    if args['create']:
        {
            'directory': create_directory
        }[args['<name>']](config['bakerscale'])
        exit(0)

    if args['simulate']:
        profile_name = args['<profile>']
        profile = config['bakerscale']['simulation_profiles'][profile_name]
        simulate(profile_name, profile)

def call_main():
    exit(main(docopt(__doc__, options_first=True)))

if __name__ == "__main__":
    call_main()
