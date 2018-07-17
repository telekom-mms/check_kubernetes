import unittest
import mock

import check_pods

nodes_all_ok = [
    mock.Mock(
        status=mock.Mock(
            phase='Running'
        )
    ),
    mock.Mock(
        status=mock.Mock(
            phase='Running'
        )
    ),
]

nodes_one_failed = [
    mock.Mock(
        status=mock.Mock(
            phase='Failed'
        )
    ),
    mock.Mock(
        status=mock.Mock(
            phase='Running'
        )
    ),
]

class TestCheckNodes(unittest.TestCase):

    @mock.patch('check_nodes.nagiosplugin.Metric')
    @mock.patch('check_nodes.client.CoreV1Api')
    @mock.patch('check_nodes.config.load_kube_config')
    def test_pods_all_ok(self, mock_config, mock_client, mock_metric):
        mock_kube = mock.Mock()

        type(mock_kube.list_pod_for_all_namespaces.return_value).items = mock.PropertyMock(return_value=nodes_all_ok)

        mock_client.return_value = mock_kube

        cls = check_pods.Pods(kube_config='empty')
        cls.probe()

        mock_config.assert_called_with('empty')
        mock_kube.list_pod_for_all_namespaces.assert_called()

        mock_metric.assert_any_call('Pending', 0, min=0)
        mock_metric.assert_any_call('Running', 2, min=0)
        mock_metric.assert_any_call('Succeeded', 0, min=0)
        mock_metric.assert_any_call('Failed', 0, min=0)
        mock_metric.assert_any_call('Unknown', 0, min=0)

    @mock.patch('check_nodes.nagiosplugin.Metric')
    @mock.patch('check_nodes.client.CoreV1Api')
    @mock.patch('check_nodes.config.load_kube_config')
    def test_pods_one_failed(self, mock_config, mock_client, mock_metric):
        mock_kube = mock.Mock()

        type(mock_kube.list_pod_for_all_namespaces.return_value).items = mock.PropertyMock(return_value=nodes_one_failed)

        mock_client.return_value = mock_kube

        cls = check_pods.Pods(kube_config='empty')
        cls.probe()

        mock_config.assert_called_with('empty')
        mock_kube.list_pod_for_all_namespaces.assert_called()

        mock_metric.assert_any_call('Pending', 0, min=0)
        mock_metric.assert_any_call('Running', 1, min=0)
        mock_metric.assert_any_call('Succeeded', 0, min=0)
        mock_metric.assert_any_call('Failed', 1, min=0)
        mock_metric.assert_any_call('Unknown', 0, min=0)


if __name__ == '__main__':
    unittest.main()
