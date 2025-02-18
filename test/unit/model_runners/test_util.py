from unittest.mock import MagicMock, patch

from fmeval.model_runners.util import get_sagemaker_session, is_endpoint_in_service, get_bedrock_runtime_client

ENDPOINT_NAME = "valid_endpoint_name"


def test_get_sagemaker_session():
    mock_sagemaker_client = MagicMock()
    mock_sagemaker_runtime_client = MagicMock()
    mock_other_client = MagicMock()

    def mock_boto3_session_client(*_, **kwargs):
        if kwargs.get("service_name") == "sagemaker":
            client = mock_sagemaker_client
        elif kwargs.get("service_name") == "sagemaker-runtime":
            client = mock_sagemaker_runtime_client
        else:
            client = mock_other_client  # we don't care which it is
        client.service_name = kwargs.get("service_name")
        return client  # like sagemaker-runtime

    with patch("boto3.session.Session.client", side_effect=mock_boto3_session_client, autospec=True) as boto3_client:
        sagemaker_session = get_sagemaker_session()
        assert sagemaker_session.sagemaker_client == mock_sagemaker_client
        assert mock_sagemaker_client.service_name == "sagemaker"
        assert sagemaker_session.sagemaker_runtime_client == mock_sagemaker_runtime_client
        assert mock_sagemaker_runtime_client.service_name == "sagemaker-runtime"


def test_get_bedrock_runtime_client():
    mock_bedrock_runtime_client = MagicMock()
    mock_other_client = MagicMock()

    def mock_boto3_session_client(*_, **kwargs):
        if kwargs.get("service_name") == "bedrock-runtime":
            client = mock_bedrock_runtime_client
        else:
            client = mock_other_client  # we don't care which it is
        client.service_name = kwargs.get("service_name")
        return client  # like bedrock-runtime

    with patch("boto3.session.Session.client", side_effect=mock_boto3_session_client, autospec=True) as boto3_client:
        bedrock_runtime_client = get_bedrock_runtime_client()
        assert bedrock_runtime_client.service_name == "bedrock-runtime"


def test_is_endpoint_in_service_true():
    mock_sagemaker_session = MagicMock()
    mock_sagemaker_session.sagemaker_client.describe_endpoint.return_value = {"EndpointStatus": "InService"}
    assert is_endpoint_in_service(mock_sagemaker_session, ENDPOINT_NAME) == True


def test_is_endpoint_in_service_false():
    mock_sagemaker_session = MagicMock()
    mock_sagemaker_session.sagemaker_client.describe_endpoint.return_value = {"EndpointStatus": "Updating"}
    assert is_endpoint_in_service(mock_sagemaker_session, ENDPOINT_NAME) == False
