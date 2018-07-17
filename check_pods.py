"""
Check for Kubernetes Pods
"""

import argparse

from kubernetes import config, client
import nagiosplugin

from version import __version__ as version


class Pods(nagiosplugin.Resource):
    """
    Check for Kubernetes Pods
    """
    phases = [
        'Pending',
        'Running',
        'Succeeded',
        'Failed',
        'Unknown'
    ]

    def __init__(self, kube_config=None):
        self.kube_config = kube_config
        self.pods = []
        self.counts = {}
        for phase in self.phases:
            self.counts[phase] = 0

    def probe(self):
        config.load_kube_config(self.kube_config)
        kube = client.CoreV1Api()
        self.pods = kube.list_pod_for_all_namespaces().items
        for pod in self.pods:
            self.counts[pod.status.phase] += 1

        metrics = []
        for phase in self.counts:
            metrics.append(nagiosplugin.Metric(phase, self.counts[phase], min=0))
        return metrics


class PodsSummary(nagiosplugin.Summary):
    """
    Check for Kubernetes Pods Summary
    """

    def ok(self, results):
        ret_str = []
        for phase in Pods.phases:
            ret_str.append("%s Pods %s" % (str(results[phase].metric), phase))
        return ', '.join(ret_str)


@nagiosplugin.guarded
def main():
    """
    :return:
    """
    argp = argparse.ArgumentParser(description='Nagios/Icinga check for Kubernetes Pods')
    argp.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
    argp.add_argument('--kube-config', help='Kubernetes Config File')

    for phase in Pods.phases:
        argp.add_argument('--warning-' + phase.lower())
        argp.add_argument('--critical-' + phase.lower())

    args = argp.parse_args()

    checks = [Pods(args.kube_config)]
    for phase in Pods.phases:
        checks.append(nagiosplugin.ScalarContext(phase,
                                                 getattr(args, 'warning_' + phase.lower()),
                                                 getattr(args, 'critical_' + phase.lower())))

    checks.append(PodsSummary())

    check = nagiosplugin.Check(*checks)
    check.main()


if __name__ == '__main__':
    main()
