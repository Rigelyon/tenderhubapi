# TenderHub API Documentation

## Authentication Endpoints

- `POST /api/v1/auth/token/` - Obtain JWT token for authentication
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token

## User Management

### Registration and Profile
- `POST /api/v1/users/register/` - Register a new user (client or vendor)
- `GET/PUT /api/v1/users/profile/` - Get or update current user profile
- `GET/PUT /api/v1/users/client-profile/` - Get or update client profile details
- `GET /api/v1/users/vendors/` - List all vendors
- `GET/PUT /api/v1/users/vendors/me/` - Get or update current vendor's profile
- `GET /api/v1/users/vendors/{id}/` - Get specific vendor profile

### Vendor Profile Features
- `GET /api/v1/users/vendors/{id}/portfolios/` - List vendor's portfolio items
- `POST /api/v1/users/vendors/{id}/add_portfolio/` - Add portfolio item to vendor profile
- `GET /api/v1/users/vendors/{id}/certifications/` - List vendor's certifications
- `POST /api/v1/users/vendors/{id}/add_certification/` - Add certification to vendor profile
- `GET /api/v1/users/vendors/{id}/education/` - List vendor's education
- `POST /api/v1/users/vendors/{id}/add_education/` - Add education to vendor profile

### Skills and Reviews
- `GET /api/v1/users/skills/` - List available skills
- `GET /api/v1/users/reviews/` - List reviews given by current user
- `POST /api/v1/users/reviews/` - Create a new review

## Tenders

### Tender Management
- `GET /api/v1/tenders/` - List all tenders (filterable by status, tags)
- `POST /api/v1/tenders/` - Create new tender (client only)
- `GET /api/v1/tenders/{id}/` - Get tender details with bids and comments
- `PUT/DELETE /api/v1/tenders/{id}/` - Update or delete tender (owner only)

### Tender Interactions
- `POST /api/v1/tenders/{id}/add_comment/` - Add comment to tender
- `POST /api/v1/tenders/{id}/place_bid/` - Place bid on tender (vendor only)
- `POST /api/v1/tenders/{id}/accept_bid/` - Accept a bid and create project (client only)

### Bid Management
- `GET /api/v1/bids/` - List bids (vendors see their bids, clients see bids on their tenders)
- `GET /api/v1/bids/{id}/` - Get specific bid details

### Tags
- `GET /api/v1/tags/` - List all available tags

## Projects

### Project Management
- `GET /api/v1/projects/` - List projects where user is participant
- `GET /api/v1/projects/{id}/` - Get project details

### Project Actions
- `POST /api/v1/projects/{id}/request_revision/` - Request revision (client only)
- `POST /api/v1/projects/{id}/deliver_project/` - Deliver completed work (vendor only)
- `POST /api/v1/projects/{id}/complete_project/` - Mark project as complete (client only)
- `POST /api/v1/projects/{id}/update_price/` - Update agreed price
- `POST /api/v1/projects/{id}/update_deadline/` - Update project deadline

### Project Activities
- `GET /api/v1/projects/{id}/activities/` - List all activities for a project
- `POST /api/v1/projects/{id}/activities/` - Add new activity/comment to project

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=.

# Generate HTML coverage report
pytest --cov=. --cov-report=html
```

### Test Structure

- `tender/tests.py` - Tests for tender-related functionality
  - List tenders
  - Create tender
  - Place bid
  - Accept bid
  - Comment on tender

- `users/tests.py` - Tests for user authentication and profiles
  - User registration (client/vendor)
  - Profile management
  - Authentication
  - Authorization

- `project_activity/tests.py` - Tests for project activities
  - List activities
  - Create activity
  - Project lifecycle events
  - File attachments

### Test Configuration

The project uses pytest.ini for configuration:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = tenderhubapi.settings
python_files = tests.py test_*.py *_tests.py
addopts = --cov=. --cov-report=html
```

### Writing Tests

Example of writing a test:
```python
@pytest.mark.django_db
class TestFeature:
    def test_specific_functionality(self, api_client):
        # Arrange
        data = {...}
        
        # Act
        response = api_client.post('/api/endpoint', data)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
```

### Running Specific Tests

```bash
# Run tests in a specific file
pytest tender/tests.py

# Run tests matching a pattern
pytest -k "test_create"

# Run with detailed output
pytest -v
```

### Test Coverage

Coverage reports are generated in HTML format and can be found in the `htmlcov` directory after running:
```bash
pytest --cov=. --cov-report=html
```
