#!/usr/bin/env python

"""bakersim.py

Usage:
    bakersim build-pkg <name> [--clean]
    bakersim copy-pkg <platform> <name>
    bakersim build-image <dockerfile> <id> [--clean] [--skip-pkg-rebuild] [--push] [--platform=<platform_name>]
    bakersim push-image <tag>
    bakersim kube-up
    bakersim kube-down
    bakersim kube-status
    bakersim create <name>
    bakersim pod-info <name>
    bakersim simulate <profile> [--cleanup]
    bakersim (-h | --help)

Options:
    --clean                 Remove the bakerstreet dist directory before operating
    --cleanup               Remove Kubernetes components after the simulation has run [default: False]
    --config                Use a specific configuration file
    --platform <name>       Indicate the OS platform [default: ubuntu]
    --push                  Push a created Docker image to the repository [default: True]
    --skip-pkg-rebuild      Do not rebuild OS packages when creating a development Docker image
    -h --help               Show this screen
"""

import glob
import json
import logging
import os
import shutil
import subprocess
import time
import yaml

from docopt import docopt
from pprint import pprint

bakerstreet_components = [
    'watson',
    'sherlock'
]

bakerstreet_platforms = {
    'ubuntu': {
        'pkg_name_fmt': 'datawire-{0}_{1}-{2}_all.deb',
        'pkg_ext': '.deb'
    },
    'centos': {
        'pkg_name_fmt': 'datawire-{0}-{1}-{2}.noarch.rpm',
        'pkg_ext': '.rpm'
    }
}

script_dir = os.path.dirname(os.path.realpath(__file__))
bakerstreet_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
docker_context = os.path.join(script_dir, 'docker')

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

class ReplicationController(object):

    def __init__(self, log, name, spec_file):
        self.log = log
        self.name = name
        self.spec_file = spec_file
        self.running_replicas = 0
        self.expected_replicas = 0

    def sync_running_replica_count(self):

        """
        :return: the actual number of replicas by examining the Running Pods.
        """

        out = kubectl2("get pods --output=json --selector=name={0}".format(self.name))
        items = json.loads(out)['items']

        result = 0
        for pod in items:
            status = pod.get('status', {})
            expected_containers = len(pod['spec']['containers'])
            running_containers = len([i for i in status.get('containerStatuses', []) if 'running' in i['state']])

            conditions = status.get('conditions', [])
            for condition in conditions:
                if condition['type'] == 'Ready' and condition['status'] and expected_containers == running_containers:
                    result += 1

        return result

    def sync_replicas_data(self):
        self.expected_replicas = self.sync_expected_replica_count()
        self.running_replicas = self.sync_running_replica_count()

    def sync_expected_replica_count(self):

        """
        :return: the expected number of replicas which is indicated by the Pod status.
        """

        out = kubectl2("get rc --output=json --selector=name={0}".format(self.name))
        data = json.loads(out)
        return data.get('items', [])[0].get('status', {}).get('replicas', 0)

    def create(self, **kwargs):
        self.log.info('launching replication controller: %s', self.spec_file)
        out = kubectl2('create -f {0}'.format(self.spec_file))
        self.log.info(out)
        self.sync_replicas_data()

    def delete(self):
        self.log.info('terminating replication controller: %s', self.spec_file)
        out = kubectl2('delete -f {0}'.format(self.spec_file))
        self.log.info(out)

    def spawn(self, **kwargs):
        self.sync_replicas_data()

        count = int(kwargs.get('count', 1))
        if self.running_replicas == self.expected_replicas:
            new_replica_count = self.running_replicas + count
            self.log.info('spawning replicas (running: %s, adding: %s, new total: %s)',
                          self.running_replicas, count, new_replica_count)
            kubectl2('scale rc {0} --replicas={1}'.format(self.name, new_replica_count))
        else:
            self.log.warn('running replicas does not match expected; skipping spawn (expected: %s, running: %s)',
                          self.expected_replicas, self.running_replicas)

    def kill(self, **kwargs):
        self.sync_replicas_data()
        count = int(kwargs.get('count', 1))
        if count > self.running_replicas:
            count = self.running_replicas

        new_replica_count = self.running_replicas - count

        self.log.info('removing replicas (current: %s, removing: %s)', 0, count)
        kubectl2('scale rc {0} --replicas={1}'.format(self.name, new_replica_count))


class Directory(ReplicationController):

    def __init__(self, log, spec_file):
        super(Directory, self).__init__(log, 'directory', spec_file)

    def is_running(self):
        out = kubectl2("get pods --output=json --selector=name={0}".format(self.name))
        pods = json.loads(out)
        if len(pods['items']) == 0:
            self.log.warn('pod does not exist (name: %s)', self.name)
            return False

        status = pods['items'][0]['status']
        return status['phase'] == 'Running' and 'running' in status['containerStatuses'][0]['state']

    def create(self, **kwargs):
        super(Directory, self).create(**kwargs)
        while kwargs['wait'] and not self.is_running():
            self.log.info('waiting for directory container to start')

    def get_ip(self):
        return pod_info(self.name)[0]['status']['podIP']

class Bakersim(object):

    def __init__(self, args, log, profile_name, sim_config):
        self.args = args
        self.log = log
        self.profile_name = profile_name
        self.sim_config = sim_config
        self.profile = sim_config['profiles'][profile_name]
        self.cycles = int(self.profile.get('cycles', -1))
        self.cycle_quantum = int(self.profile.get('cycle_quantum', 60))
        self.run_forever = self.cycles <= -1

    def run(self):
        self.log.info('preparing to run simulation: %s', self.profile_name)

        image = self.sim_config['image']

        directory_spec = generate_directory_rc(docker_image=image, name='directory')
        directory = Directory(self.log, directory_spec)

        if not directory.is_running():
            directory.create(wait=True)

        directory_ip = directory.get_ip()

        # stats_server = Pod(self.log, 'stats', stats_spec)
        # if not stats_server.is_running():
        #     stats_server.create(wait=True)
        #
        # stats_ip = stats_server.get_ip()

        server_spec = generate_bakerscale_server_rc(docker_image=image, name='bakerscale-server',
                                                    directory_ip=directory_ip)
        client_spec = generate_bakerscale_client_rc(docker_image=image, name='bakerscale-client',
                                                    directory_ip=directory_ip,
                                                    stats_ip=self.sim_config['stats_server'])

        servers = ReplicationController(self.log, 'bakerscale-server', server_spec)
        clients = ReplicationController(self.log, 'bakerscale-client', client_spec)

        servers.create()
        clients.create()

        targets = {'directory': directory, 'servers': servers, 'clients': clients}

        self.log.info('running simulation: %s', self.profile_name)
        cycle = 0
        while self.run_forever is True or cycle <= self.cycles:
            start = int(time.time())
            self.log.debug('running sim cycle (%s of %s, quantum: %s)', cycle, self.cycles, self.cycle_quantum)

            for task in self.profile['tasks']:
                task_type, task_target = task['type'].split('.')
                target = targets[task_target]
                if target:
                    self.log.debug('processing cycle task (type: %s, target: %s)', task_type, task_target)
                    getattr(target, task_type)(**task)

            cycle += 1
            elapsed = int(time.time()) - start
            if elapsed < self.cycle_quantum:
                sleep_time = self.cycle_quantum - elapsed
                self.log.debug('extra time left in cycle quantum... sleeping (seconds: %s)', sleep_time)
                time.sleep(sleep_time)

        if self.args['--cleanup']:
            clients.delete()
            servers.delete()
            directory.delete()

    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, self.profile_name)

def print_process_output(proc):
    for line in iter(proc.stdout.readline, b''):
        print(">>> " + line.rstrip())

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
            },
            'spec': {
                'containers': containers
            }
        }
    }

def generate_bakerscale_client_rc(docker_image, directory_ip, stats_ip, name='bakerscale-client'):
    content = base_kube_rc_config.copy()
    content['metadata'] = generate_base_rc_metadata(name)
    content['spec'] = generate_rc_spec(name, [
        {
            'args': ["python", "bakerscale.py", "sherlock", str(directory_ip), "{0}:8080".format(str(stats_ip))],
            'image': docker_image,
            'name': 'sherlock',
            'resources': {
                'limits': {
                    'memory': '50Mi',
                    'cpu': '20m'
                }
            }
        }])

    rc_config_path = os.path.join(script_dir,  name + '.yml')
    write_yaml(rc_config_path, content)
    return rc_config_path


def generate_bakerscale_server_rc(docker_image, directory_ip, name='bakerscale-service'):
    content = base_kube_rc_config.copy()
    content['metadata'] = generate_base_rc_metadata(name)
    content['spec'] = generate_rc_spec(name, [
        {
            'args': ["python", "bakerscale.py", "watson", str(directory_ip),
                     "http://localhost:8080/", "hello", "http://localhost:8080/health"],
            'image': docker_image,
            'name': 'watson',
            'resources': {
                'limits': {
                    'memory': '50Mi',
                    'cpu': '20m'
                }
            }
        },
        {
            'args': ["python", "bakerscale_service.py", "8080"],
            'image': docker_image,
            'name': 'server',
            'resources': {
                'limits': {
                    'memory': '50Mi',
                    'cpu': '20m'
                }
            }
        }])

    rc_config_path = os.path.join(script_dir,  name + '.yml')
    write_yaml(rc_config_path, content)
    return rc_config_path


def generate_directory_rc(docker_image, name='directory'):
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

    rc_config_path = os.path.join(script_dir, name + '.yml')
    write_yaml(rc_config_path, content)
    return rc_config_path

def create_directory(config):
    proc = kubectl(['create', '-f', generate_directory_rc(config['image'])])
    out, err = proc.communicate()
    print(out)

def delete_directory():
    proc = kubectl(['delete', '-f', ''])
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
    proc = kubectl(['get', 'pods', '--output=json', '--selector=name={0}'.format(pod_name)])
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

def kubectl(args_and_opts, env=None):
    if isinstance(args_and_opts, basestring):
        args_and_opts = args_and_opts.split(' ')

    if not isinstance(args_and_opts, list):
        raise ValueError('kubectl arguments and options must be passed as string or list')

    cmd = ['kubectl']
    cmd.extend(args_and_opts)

    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)

    proc = subprocess.Popen(cmd, cwd=script_dir, env=cmd_env, close_fds=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc

def kubectl2(args_and_opts, env=None):
    proc = kubectl(args_and_opts, env)
    out, err = proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError('error executing <kubectl {0}> (status: {1}, msg: {2})'.format(args_and_opts,
                                                                                          proc.returncode,
                                                                                          out))
    return out

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

def is_kube_available():
    proc = kubectl(['cluster-info'])
    exit_code = proc.wait()
    return exit_code == 0

# ----------------------------------------------------------------------------------------------------------------------
# Packaging and Docker Commands
# ----------------------------------------------------------------------------------------------------------------------

def package_and_build(config, args):
    if args['--clean']:
        clean_dist()

    if args['build-image']:
        build_image(config, args)

def clean_dist():
    shutil.rmtree(os.path.join(bakerstreet_dir, "dist"))

def push_image(image_id):
    cmd = ['docker', 'push', image_id]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print_process_output(proc)

def build_image(config, args):
    platform = args['--platform']
    skip_pkg_rebuild = args['--skip-pkg-rebuild']

    dockerfile = args['<dockerfile>']
    if dockerfile.endswith('-dev.dockerfile'):
        for component in bakerstreet_components:
            version, release = pkg_version(component)

            pkg_name_fmt = bakerstreet_platforms[platform]['pkg_name_fmt']
            pkg_file_ext = bakerstreet_platforms[platform]['pkg_ext']
            pkg_file = pkg_name_fmt.format(component, version, release)

            if not skip_pkg_rebuild:
                build_pkg(component)

            shutil.copy(os.path.join(bakerstreet_dir, 'dist', platform, pkg_file), docker_context)
            shutil.move(os.path.join(docker_context, pkg_file),
                        os.path.join(docker_context, 'datawire-{0}{1}'.format(component, pkg_file_ext)))

    build_command = ['docker', 'build',

                     '-t', '{0}'.format(args['<id>']),
                     '-f', '{0}/{1}'.format(docker_context, dockerfile),
                     docker_context]

    proc = subprocess.Popen(build_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print_process_output(proc)

    if args['--push']:
        push_image(args['<id>'])

def build_pkg(name):
    work_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
    pkg_command = ["python", "{0}/pkg-{1}".format(work_dir, name)]

    proc = subprocess.Popen(pkg_command, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print_process_output(proc)

def pkg_version(name):
    cmd = ["python", "pkg-{0}".format(name), "--show-version"]

    proc = subprocess.Popen(cmd, cwd=bakerstreet_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    version, err = proc.communicate()

    cmd = ["python", "pkg-{0}".format(name), "--show-iteration"]
    proc = subprocess.Popen(cmd, cwd=bakerstreet_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    iteration, err = proc.communicate()

    return version.rstrip(), iteration.rstrip()

# ----------------------------------------------------------------------------------------------------------------------
# Main Program Ceremony
# ----------------------------------------------------------------------------------------------------------------------

def main(args):
    config_file = args.get('config', "{0}/bakersim.yml".format(script_dir))
    config = None
    with open(config_file, 'r') as fs:
        config = yaml.load(fs)

    logging_config = config.get('logging', {
        'level': 'INFO', 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'})

    logging.basicConfig(format=logging_config['format'], level=logging_config['level'])
    log = logging.getLogger(__name__)

    if args['build-image']:
        package_and_build(config, args)

    if args['kube-down'] and is_kube_available():
        kube_down()
        exit(0)

    if args['kube-up'] and not is_kube_available():
        kube_up(config['kubernetes'])
        exit(0)

    if args['kube-status']:
        is_up = is_kube_available()
        log.info('kubernetes cluster is available (status: %s)', "up" if is_up else "down")
        exit(0 if is_up else 1)

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
        if not is_kube_available():
            log.error("Cannot run simulation because Kubernetes cluster is not available")
            exit(1)

        profile_name = args['<profile>']
        sim_config = config['bakerscale']
        Bakersim(args, log, profile_name, sim_config).run()
        exit(0)

def call_main():
    exit(main(docopt(__doc__)))

if __name__ == "__main__":
    call_main()
