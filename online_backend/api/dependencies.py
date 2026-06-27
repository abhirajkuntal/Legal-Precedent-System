from src.services.legal_search_service import LegalSearchService

service = LegalSearchService()

# One global object service at the API startup and then shared through all routes to avoid all routes making their own service object with each new request 
