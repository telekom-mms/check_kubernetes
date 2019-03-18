import unittest
import mock

import check_nodes

nodes_all_ok = [
    mock.Mock(
        status=mock.Mock(
            conditions=[
                mock.Mock(type='Ready', status='True'),
                mock.Mock(type='DiskPressure', status='False'),
            ],
        )
    ),
    mock.Mock(
        status=mock.Mock(
            conditions=[
                mock.Mock(type='Ready', status='True'),
                mock.Mock(type='DiskPressure', status='False'),
            ],
        )
    ),
]

nodes_one_problem = [
    mock.Mock(
        status=mock.Mock(
            conditions=[
                mock.Mock(type='Ready', status='True'),
                mock.Mock(type='DiskPressure', status='True'),
            ],
        )
    ),
    mock.Mock(
        status=mock.Mock(
            conditions=[
                mock.Mock(type='Ready', status='True'),
                mock.Mock(type='DiskPressure', status='False'),
            ],
        )
    ),
]

class TestCheckNodes(unittest.TestCase):

    @mock.patch('check_nodes.nagiosplugin.Metric')
    @mock.patch('check_nodes.client.CoreV1Api')
    @mock.patch('check_nodes.config.load_kube_config')
    def test_node_all_ok(self, mock_config, mock_client, mock_metric):
        mock_kube = mock.Mock()

        type(mock_kube.list_node.return_value).items = mock.PropertyMock(return_value=nodes_all_ok)

        mock_client.return_value = mock_kube

        cls = check_nodes.Nodes(kube_config='empty')
        cls.probe()

        mock_config.assert_called_with('empty')
        mock_kube.list_node.assert_called()

        mock_metric.assert_any_call('problem_nodes', 0, min=0)
        mock_metric.assert_any_call('all_nodes', 2, min=0)

    @mock.patch('check_nodes.nagiosplugin.Metric')
    @mock.patch('check_nodes.client.CoreV1Api')
    @mock.patch('check_nodes.config.load_kube_config')
    def test_node_one_problem(self, mock_config, mock_client, mock_metric):
        mock_kube = mock.Mock()

        type(mock_kube.list_node.return_value).items = mock.PropertyMock(return_value=nodes_one_problem)

        mock_client.return_value = mock_kube

        cls = check_nodes.Nodes(kube_config='empty')
        cls.probe()

        mock_config.assert_called_with('empty')
        mock_kube.list_node.assert_called()

        mock_metric.assert_any_call('problem_nodes', 1, min=0)
        mock_metric.assert_any_call('all_nodes', 2, min=0)



if __name__ == '__main__':
    unittest.main()
