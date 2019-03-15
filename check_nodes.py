# -*- coding: utf-8 -*-
"""
Check for Kubernetes Nodes
"""

import argparse

from kubernetes import config, client
import nagiosplugin

from version import __version__ as version

class Nodes(nagiosplugin.Resource):
    """
    Check for Kubernetes Nodes
    """

    def __init__(self, kube_config):
        self.kube_config = kube_config
        self.nodes = []
        self.nodes_with_problems = []

    def probe(self):
        config.load_kube_config(self.kube_config)
        kube = client.CoreV1Api()

        for node in kube.list_node().items:
            self.nodes.append(node)
            for condition in node.status.conditions:
                if (condition.type == 'Ready' and condition.status != 'True') \
                or (condition.type != 'Ready' and condition.status != 'False'):
                    self.nodes_with_problems.append(node)

        return [
            nagiosplugin.Metric('problem_nodes', len(set(self.nodes_with_problems)), min=0),
            nagiosplugin.Metric('all_nodes', len(set(self.nodes)), min=0),
        ]


@nagiosplugin.guarded
def main():
    """
    :return:
    """
    argp = argparse.ArgumentParser(description='Nagios/Icinga check for Kubernetes Nodes')
    argp.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
    argp.add_argument('--kube-config', help='Kubernetes Config File')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        Nodes(args.kube_config),
        nagiosplugin.ScalarContext('problem_nodes', 1, 2),
        nagiosplugin.ScalarContext('all_nodes')
    )
    check.main()


if __name__ == '__main__':
    main()
