import pytest
from src.predictor.predictor import MockPredictor

@pytest.fixture
def mock_predictor():
    """Provides a MockPredictor instance with default config."""
    return MockPredictor(config={"threshold": 0.8})

def test_mock_predictor_init(mock_predictor):
    """
    Test that the MockPredictor initializes correctly.
    """
    assert mock_predictor is not None
    assert mock_predictor.config["threshold"] == 0.8

def test_mock_predictor_predict_output_format(mock_predictor):
    """
    Test that the predict method returns the expected dictionary format.
    """
    # Dummy metrics, as they are not used by the mock
    dummy_metrics = {"cpu": 50, "memory": 60}
    prediction = mock_predictor.predict(dummy_metrics)

    assert isinstance(prediction, dict)
    assert "anomaly_score" in prediction
    assert "is_anomaly" in prediction
    assert isinstance(prediction["anomaly_score"], float)
    assert isinstance(prediction["is_anomaly"], bool)

def test_mock_predictor_anomaly_score_range(mock_predictor):
    """
    Test that the anomaly score is within the expected [0.0, 1.0] range.
    """
    for _ in range(100): # Run multiple times to check randomness
        prediction = mock_predictor.predict({})
        assert 0.0 <= prediction["anomaly_score"] <= 1.0

def test_mock_predictor_is_anomaly_logic(mock_predictor, mocker):
    """
    Test the logic for determining if a result is an anomaly based on threshold.
    """
    # Force random.uniform to return a value below the threshold
    mocker.patch('random.uniform', return_value=0.5)
    prediction_low = mock_predictor.predict({})
    assert not prediction_low["is_anomaly"]
    assert prediction_low["anomaly_score"] == 0.5

    # Force random.uniform to return a value above the threshold
    mocker.patch('random.uniform', return_value=0.9)
    prediction_high = mock_predictor.predict({})
    assert prediction_high["is_anomaly"]
    assert prediction_high["anomaly_score"] == 0.9
