# TenderHub API Documentation

## Authentication Endpoints

- `POST /api/v1/auth/token/` - Obtain JWT token for authentication  
  **Payload:**  
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- `POST /api/v1/auth/token/refresh/` - Refresh JWT token  
  **Payload:**  
  ```json
  {
    "refresh": "string"
  }
  ```

## User Management

### Registration and Profile
- `POST /api/v1/users/register/` - Register a new user (client or vendor)  
  **Payload:**  
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "password2": "string",
    "first_name": "string",
    "last_name": "string",
    "user_type": "client or vendor"
  }
  ```

- `GET/PUT /api/v1/users/profile/` - Get or update current user profile  
  **Payload (PUT):**  
  ```json
  {
    "first_name": "string",
    "last_name": "string",
    "profile_picture": "file",
    "bio": "string",
    "location": "string",
    "language": "string"
  }
  ```

- `GET/PUT /api/v1/users/client-profile/` - Get or update client profile details  
  **Payload (PUT):**  
  ```json
  {
    "company_name": "string",
    "contact_number": "string",
    "address": "string"
  }
  ```

- `GET /api/v1/users/vendors/` - List all vendors  
  **Payload:** None  

- `GET/PUT /api/v1/users/vendors/me/` - Get or update current vendor's profile  
  **Payload (PUT):**  
  ```json
  {
    "hourly_rate": "number"
  }
  ```

- `GET /api/v1/users/vendors/{id}/` - Get specific vendor profile  
  **Payload:** None  

### Vendor Profile Features
- `GET /api/v1/users/vendors/{id}/portfolios/` - List vendor's portfolio items  
  **Payload:** None  

- `POST /api/v1/users/vendors/{id}/add_portfolio/` - Add portfolio item to vendor profile  
  **Payload:**  
  ```json
  {
    "title": "string",
    "description": "string",
    "image": "file",
    "link": "string",
    "date_created": "YYYY-MM-DD"
  }
  ```

- `DELETE /api/v1/users/vendors/{id}/delete_portfolio/?portfolio_id={portfolio_id}` - Delete a portfolio item  
  **Query Parameters:**  
  - `portfolio_id`: ID of the portfolio to delete  
  **Response:**  
  ```json
  {
    "message": "Portfolio deleted successfully"
  }
  ```

- `GET /api/v1/users/vendors/{id}/skills/` - List vendor's skills  
  **Payload:** None  

- `POST /api/v1/users/vendors/{id}/add_skill/` - Add skill to vendor profile  
  **Payload:**  
  ```json
  {
    "id": "integer",  // Optional: ID of existing skill
    "name": "string"  // Optional: Name for new skill (if id not provided)
  }
  ```
  **Response:**  
  ```json
  {
    "message": "Skill 'Skill Name' added successfully",
    "created": true  // Whether a new skill was created
  }
  ```

- `DELETE /api/v1/users/vendors/{id}/delete_skill/?skill_id={skill_id}` - Delete a skill from vendor profile  
  **Query Parameters:**  
  - `skill_id`: ID of the skill to remove  
  **Response:**  
  ```json
  {
    "message": "Skill 'Skill Name' removed successfully"
  }
  ```

- `GET /api/v1/users/vendors/{id}/certifications/` - List vendor's certifications  
  **Payload:** None  

- `POST /api/v1/users/vendors/{id}/add_certification/` - Add certification to vendor profile  
  **Payload:**  
  ```json
  {
    "title": "string",
    "issuing_organization": "string",
    "issue_date": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "credential_id": "string"
  }
  ```

- `DELETE /api/v1/users/vendors/{id}/delete_certification/?certification_id={certification_id}` - Delete a certification  
  **Query Parameters:**  
  - `certification_id`: ID of the certification to delete  
  **Response:**  
  ```json
  {
    "message": "Certification deleted successfully"
  }
  ```

- `GET /api/v1/users/vendors/{id}/education/` - List vendor's education  
  **Payload:** None  

- `POST /api/v1/users/vendors/{id}/add_education/` - Add education to vendor profile  
  **Payload:**  
  ```json
  {
    "institution": "string",
    "degree": "string",
    "field_of_study": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  }
  ```

- `DELETE /api/v1/users/vendors/{id}/delete_education/?education_id={education_id}` - Delete an education record  
  **Query Parameters:**  
  - `education_id`: ID of the education record to delete  
  **Response:**  
  ```json
  {
    "message": "Education record deleted successfully"
  }
  ```

### Skills and Reviews
- `GET /api/v1/users/skills/` - List available skills  
  **Payload:** None  

- `GET /api/v1/users/reviews/` - List reviews given by current user  
  **Payload:** None  

- `POST /api/v1/users/reviews/` - Create a new review  
  **Payload:**  
  ```json
  {
    "reviewee": "integer",
    "rating": "integer (1-5)",
    "comment": "string",
    "project": "integer"
  }
  ```

## Tenders

### Tender Management
- `GET /api/v1/tenders/` - List all tenders (filterable by status, tags, category)  
  **Payload:** None  
  **Query Parameters:**  
  - `category`: Filter tenders by category name

- `POST /api/v1/tenders/` - Create new tender (client only)  
  **Payload:**  
  ```json
  {
    "title": "string",
    "description": "string",
    "attachment": "file",
    "max_duration": "integer",
    "min_budget": "number",
    "max_budget": "number",
    "deadline": "YYYY-MM-DD",
    "category_id": "integer",
    "tags": [{"name": "string"}]
  }
  ```

- `GET /api/v1/tenders/{id}/` - Get tender details with bids and comments  
  **Payload:** None  

- `PUT/DELETE /api/v1/tenders/{id}/` - Update or delete tender (owner only)  
  **Payload (PUT):**  
  ```json
  {
    "title": "string",
    "description": "string",
    "attachment": "file",
    "max_duration": "integer",
    "min_budget": "number",
    "max_budget": "number",
    "deadline": "YYYY-MM-DD",
    "tags": [{"name": "string"}]
  }
  ```

### Tender Interactions
- `POST /api/v1/tenders/{id}/add_comment/` - Add comment to tender  
  **Payload:**  
  ```json
  {
    "content": "string"
  }
  ```

- `POST /api/v1/tenders/{id}/place_bid/` - Place bid on tender (vendor only)  
  **Payload:**  
  ```json
  {
    "amount": "number",
    "proposal": "string",
    "delivery_time": "integer"
  }
  ```

- `POST /api/v1/tenders/{id}/accept_bid/` - Accept a bid and create project (client only)  
  **Payload:**  
  ```json
  {
    "bid_id": "integer"
  }
  ```

### Bid Management
- `GET /api/v1/bids/` - List bids (vendors see their bids, clients see bids on their tenders)  
  **Payload:** None  

- `GET /api/v1/bids/{id}/` - Get specific bid details  
  **Payload:** None  

### Tags
- `GET /api/v1/tags/` - List all available tags  
  **Payload:** None  

### Comment Management
- `GET /api/v1/comments/` - List comments (default: comments by current user)  
  **Query Parameters:**  
  - `tender_id`: Filter comments by tender ID
  - `user_id`: Filter comments by user ID
  - `user_type`: Filter comments by user type ("client" or "vendor")
  - `from_date`: Filter comments created after this date (YYYY-MM-DD)
  - `to_date`: Filter comments created before this date (YYYY-MM-DD)
  - `page`: Page number for pagination
  - `page_size`: Number of items per page (default: 10)
  
  **Response:**  
  ```json
  {
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": [
      {
        "comment_id": "integer",
        "tender": "integer",
        "user": "integer",
        "user_name": "string",
        "user_picture": "string (url)",
        "user_type": "string (client or vendor)",
        "content": "string",
        "created_at": "datetime"
      }
    ]
  }
  ```
  **Status Codes:**  
  - `200`: Comments retrieved successfully
  - `400`: Invalid query parameters
  - `401`: Authentication required

- `GET /api/v1/comments/{id}/` - Get specific comment details  
  **Response:**  
  ```json
  {
    "comment_id": "integer",
    "tender": "integer",
    "user": "integer",
    "user_name": "string",
    "user_picture": "string (url)",
    "user_type": "string (client or vendor)",
    "content": "string",
    "created_at": "datetime"
  }
  ```
  **Status Codes:**  
  - `200`: Comment retrieved successfully
  - `404`: Comment not found
  - `401`: Authentication required

- `POST /api/v1/comments/` - Create a new comment  
  **Payload:**  
  ```json
  {
    "tender_id": "integer",
    "content": "string"
  }
  ```
  **Response:**  
  ```json
  {
    "comment_id": "integer",
    "tender": "integer",
    "user": "integer",
    "user_name": "string",
    "user_picture": "string (url)",
    "user_type": "string (client or vendor)",
    "content": "string",
    "created_at": "datetime"
  }
  ```
  **Status Codes:**  
  - `201`: Comment created successfully
  - `400`: Invalid input
  - `401`: Authentication required
  - `403`: Not authorized to comment on this tender

- `PUT /api/v1/comments/{id}/` - Update a comment (comment owner only)  
  **Payload:**  
  ```json
  {
    "content": "string"
  }
  ```
  **Response:**  
  ```json
  {
    "comment_id": "integer",
    "tender": "integer",
    "user": "integer",
    "user_name": "string",
    "user_picture": "string (url)",
    "user_type": "string (client or vendor)",
    "content": "string",
    "created_at": "datetime"
  }
  ```
  **Status Codes:**  
  - `200`: Comment updated successfully
  - `400`: Invalid input
  - `401`: Authentication required
  - `403`: Not authorized to update this comment
  - `404`: Comment not found

- `DELETE /api/v1/comments/{id}/` - Delete a comment (comment owner only)  
  **Response:**  
  ```json
  {
    "message": "Comment deleted successfully"
  }
  ```
  **Status Codes:**  
  - `204`: Comment deleted successfully
  - `401`: Authentication required
  - `403`: Not authorized to delete this comment
  - `404`: Comment not found

## Categories

### Category Management
- `GET /api/v1/categories/` - List all categories  
  **Payload:** None  

- `POST /api/v1/categories/` - Create a new category (admin only)  
  **Payload:**  
  ```json
  {
    "name": "string",
    "description": "string"
  }
  ```

## Projects

### Project Management
- `GET /api/v1/projects/` - List projects where user is participant  
  **Payload:** None  

- `GET /api/v1/projects/{id}/` - Get project details  
  **Payload:** None  

### Project Actions
- `POST /api/v1/projects/{id}/request_revision/` - Request revision (client only)  
  **Payload:**  
  ```json
  {
    "description": "string"
  }
  ```

- `POST /api/v1/projects/{id}/deliver_project/` - Deliver completed work (vendor only)  
  **Payload:**  
  ```json
  {
    "description": "string",
    "attachment": "file"
  }
  ```

- `POST /api/v1/projects/{id}/complete_project/` - Mark project as complete (client only)  
  **Payload:**  
  ```json
  {
    "description": "string"
  }
  ```

- `POST /api/v1/projects/{id}/update_price/` - Update agreed price  
  **Payload:**  
  ```json
  {
    "new_price": "number"
  }
  ```

- `POST /api/v1/projects/{id}/update_deadline/` - Update project deadline  
  **Payload:**  
  ```json
  {
    "new_deadline": "YYYY-MM-DD"
  }
  ```

### Project Activities
- `GET /api/v1/projects/{id}/activities/` - List all activities for a project  
  **Payload:** None  

- `POST /api/v1/projects/{id}/activities/` - Add new activity/comment to project  
  **Payload:**  
  ```json
  {
    "activity_type": "string",
    "description": "string",
    "attachment": "file"
  }
  ```

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
