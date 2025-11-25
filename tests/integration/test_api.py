"""Integration tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    def test_health_check(self, api_client):
        """Test the root health check endpoint."""
        response = api_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data

    def test_get_quote_valid_input(self, api_client):
        """Test GET /quote/ with valid parameters."""
        params = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 200
        data = response.json()
        assert "predicted_price" in data
        assert "input_features" in data
        assert isinstance(data["predicted_price"], (int, float))
        assert data["predicted_price"] > 0

    def test_post_quote_valid_input(self, api_client):
        """Test POST /quote/ with valid JSON body."""
        payload = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.post("/quote/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "predicted_price" in data
        assert data["predicted_price"] > 0

    def test_get_and_post_same_result(self, api_client):
        """Test that GET and POST return the same prediction."""
        house_data = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        get_response = api_client.get("/quote/", params=house_data)
        post_response = api_client.post("/quote/", json=house_data)

        assert get_response.status_code == 200
        assert post_response.status_code == 200

        # Predictions should be the same
        assert (
            get_response.json()["predicted_price"]
            == post_response.json()["predicted_price"]
        )

    def test_input_features_echoed_in_response(self, api_client):
        """Test that input features are returned in the response."""
        payload = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.post("/quote/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["input_features"]["LotArea"] == 8450
        assert data["input_features"]["YearBuilt"] == 2003
        assert data["input_features"]["OverallQual"] == 7

    @pytest.mark.parametrize(
        "invalid_params,expected_status",
        [
            # Negative lot area
            (
                {
                    "LotArea": -100,
                    "YearBuilt": 2003,
                    "YearRemodAdd": 2003,
                    "OverallQual": 7,
                    "OverallCond": 5,
                },
                422,
            ),
            # Year built too old
            (
                {
                    "LotArea": 8450,
                    "YearBuilt": 1700,
                    "YearRemodAdd": 2003,
                    "OverallQual": 7,
                    "OverallCond": 5,
                },
                422,
            ),
            # Year built in future
            (
                {
                    "LotArea": 8450,
                    "YearBuilt": 2100,
                    "YearRemodAdd": 2003,
                    "OverallQual": 7,
                    "OverallCond": 5,
                },
                422,
            ),
            # Quality out of range
            (
                {
                    "LotArea": 8450,
                    "YearBuilt": 2003,
                    "YearRemodAdd": 2003,
                    "OverallQual": 15,
                    "OverallCond": 5,
                },
                422,
            ),
            # Condition out of range
            (
                {
                    "LotArea": 8450,
                    "YearBuilt": 2003,
                    "YearRemodAdd": 2003,
                    "OverallQual": 7,
                    "OverallCond": 0,
                },
                422,
            ),
        ],
    )
    def test_validation_errors(self, api_client, invalid_params, expected_status):
        """Test that invalid inputs return 422 validation errors."""
        response = api_client.get("/quote/", params=invalid_params)

        assert response.status_code == expected_status

    def test_remodel_before_built_validation(self, api_client):
        """Test that YearRemodAdd cannot be before YearBuilt."""
        params = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2000,  # Before built!
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 422
        assert "YearRemodAdd cannot be before YearBuilt" in response.text

    def test_missing_required_field(self, api_client):
        """Test that missing required fields return 422."""
        params = {
            "LotArea": 8450,
            # Missing other required fields
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 422

    def test_invalid_data_type(self, api_client):
        """Test that invalid data types return 422."""
        params = {
            "LotArea": "not_a_number",
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 422

    def test_quality_boundary_values(self, api_client):
        """Test quality and condition boundary values (1 and 10)."""
        # Minimum values
        params_min = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 1,
            "OverallCond": 1,
        }

        response_min = api_client.get("/quote/", params=params_min)
        assert response_min.status_code == 200

        # Maximum values
        params_max = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 10,
            "OverallCond": 10,
        }

        response_max = api_client.get("/quote/", params=params_max)
        assert response_max.status_code == 200

        # Both should return valid predictions
        assert response_min.json()["predicted_price"] > 0
        assert response_max.json()["predicted_price"] > 0

    def test_recent_year_sold(self, api_client):
        """Test with recent/current year (uses datetime.now())."""
        params = {
            "LotArea": 8450,
            "YearBuilt": 2020,
            "YearRemodAdd": 2022,
            "OverallQual": 8,
            "OverallCond": 8,
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 200
        assert response.json()["predicted_price"] > 0

    def test_old_house(self, api_client):
        """Test with an old house (built in 1800s)."""
        params = {
            "LotArea": 8450,
            "YearBuilt": 1850,
            "YearRemodAdd": 1850,
            "OverallQual": 5,
            "OverallCond": 5,
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 200
        assert response.json()["predicted_price"] > 0

    def test_response_format(self, api_client):
        """Test that response has correct schema."""
        payload = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.post("/quote/", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check schema
        assert set(data.keys()) == {"predicted_price", "input_features"}
        assert isinstance(data["predicted_price"], (int, float))
        assert isinstance(data["input_features"], dict)
        assert set(data["input_features"].keys()) == {
            "LotArea",
            "YearBuilt",
            "YearRemodAdd",
            "OverallQual",
            "OverallCond",
        }

    def test_concurrent_requests(self, api_client):
        """Test that service handles multiple requests."""
        params = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        responses = [api_client.get("/quote/", params=params) for _ in range(5)]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        # All should return same prediction
        prices = [r.json()["predicted_price"] for r in responses]
        assert all(p == prices[0] for p in prices)

    def test_floating_point_lot_area(self, api_client):
        """Test that floating point values are accepted for LotArea."""
        params = {
            "LotArea": 8450.5,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        response = api_client.get("/quote/", params=params)

        assert response.status_code == 200
        assert response.json()["input_features"]["LotArea"] == 8450.5
