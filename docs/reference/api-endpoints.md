# 🔌 API Endpoints Reference

Complete reference for all REST API endpoints.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

Currently no authentication required. Add authentication for production use.

## Endpoints

### Health Check

<div class="grid cards" markdown>
-   **GET /**

    ---

    Health check endpoint to verify API is running.

    **Response:** `200 OK`
    ```json
    {
      "status": "healthy",
      "message": "House Price Quoting Service is running"
    }
    ```

</div>

### Get Quote (Query Parameters)

<div class="grid cards" markdown>
-   **GET /quote/**

    ---

    Get house price prediction using query parameters.

    **Parameters:**

    | Name | Type | Required | Range | Description |
    |------|------|----------|-------|-------------|
    | `LotArea` | float | Yes | > 0 | Lot size in square feet |
    | `YearBuilt` | int | Yes | 1800-2100 | Year house was built |
    | `YearRemodAdd` | int | Yes | 1950-2100 | Year of remodel |
    | `OverallQual` | int | Yes | 1-10 | Overall quality rating |
    | `OverallCond` | int | Yes | 1-10 | Overall condition rating |

    **Example Request:**
    ```bash
    curl "http://localhost:8000/quote/?LotArea=8450&YearBuilt=2003&YearRemodAdd=2003&OverallQual=7&OverallCond=5"
    ```

    **Response:** `200 OK`
    ```json
    {
      "predicted_price": 184408.00,
      "input_features": {
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "OverallQual": 7,
        "OverallCond": 5
      }
    }
    ```

</div>

### Post Quote (JSON Body)

<div class="grid cards" markdown>
-   **POST /quote/**

    ---

    Get house price prediction using JSON request body.

    **Request Body:**
    ```json
    {
      "LotArea": 8450,
      "YearBuilt": 2003,
      "YearRemodAdd": 2003,
      "OverallQual": 7,
      "OverallCond": 5
    }
    ```

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/quote/" \
      -H "Content-Type: application/json" \
      -d '{
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "OverallQual": 7,
        "OverallCond": 5
      }'
    ```

    **Response:** `200 OK`
    ```json
    {
      "predicted_price": 184408.00,
      "input_features": {
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "OverallQual": 7,
        "OverallCond": 5
      }
    }
    ```

</div>

## Response Schemas

### QuoteResponse

```typescript
{
  predicted_price: number;     // Predicted house price in dollars
  input_features: {            // Echo of input features
    LotArea: number;
    YearBuilt: number;
    YearRemodAdd: number;
    OverallQual: number;
    OverallCond: number;
  }
}
```

### ErrorResponse

```typescript
{
  detail: [
    {
      loc: string[];           // Location of error
      msg: string;             // Error message
      type: string;            // Error type
    }
  ]
}
```

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request completed successfully |
| 422 | Validation Error | Invalid input parameters |
| 500 | Internal Server Error | Unexpected server error |

## Validation Rules

### LotArea

- **Type:** float
- **Range:** > 0
- **Typical:** 1,300 - 215,245 sq ft
- **Error:** "ensure this value is greater than 0"

### YearBuilt

- **Type:** integer
- **Range:** 1800 - 2100
- **Validation:** Must be ≤ current year
- **Error:** "ensure this value is less than or equal to 2100"

### YearRemodAdd

- **Type:** integer
- **Range:** 1950 - 2100
- **Validation:** Must be ≥ YearBuilt
- **Error:** "YearRemodAdd must be >= YearBuilt"

### OverallQual

- **Type:** integer
- **Range:** 1 - 10
- **Description:** Rates overall material and finish
- **Error:** "ensure this value is between 1 and 10"

### OverallCond

- **Type:** integer
- **Range:** 1 - 10
- **Description:** Rates overall condition
- **Error:** "ensure this value is between 1 and 10"

## Examples

### Python

```python
import requests

# GET request
response = requests.get(
    "http://localhost:8000/quote/",
    params={
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "OverallQual": 7,
        "OverallCond": 5,
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Predicted price: ${data['predicted_price']:,.2f}")
else:
    print(f"Error: {response.json()}")
```

### JavaScript

```javascript
fetch('http://localhost:8000/quote/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    LotArea: 8450,
    YearBuilt: 2003,
    YearRemodAdd: 2003,
    OverallQual: 7,
    OverallCond: 5
  })
})
.then(res => res.json())
.then(data => console.log(`Price: $${data.predicted_price}`))
.catch(err => console.error('Error:', err));
```

### cURL

```bash
# GET request
curl "http://localhost:8000/quote/?LotArea=8450&YearBuilt=2003&YearRemodAdd=2003&OverallQual=7&OverallCond=5"

# POST request
curl -X POST "http://localhost:8000/quote/" \
  -H "Content-Type: application/json" \
  -d '{"LotArea":8450,"YearBuilt":2003,"YearRemodAdd":2003,"OverallQual":7,"OverallCond":5}'
```

## Rate Limiting

Currently no rate limiting. Consider implementing for production:

- Per-IP limits
- API key quotas
- Burst protection

## CORS

CORS is enabled for all origins in development. Configure appropriately for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST"],
)
```

## Interactive Documentation

Visit `/docs` for interactive Swagger UI:

```
http://localhost:8000/docs
```

Features:
- Try endpoints directly in browser
- See request/response schemas
- View validation rules
- Copy as cURL/Python/JavaScript

## Related Documentation

- [How to integrate API →](../how-to/api-integration.md)
- [Data schema →](data-schema.md)
- [Architecture →](../explanation/architecture.md)
