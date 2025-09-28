# commerce/pagination.py
from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    """
    Custom pagination class using Page Number pagination.
    """
    page_size = 10                      # default items per page
    page_size_query_param = "page_size" # allow client to set page size
    max_page_size = 100                 # prevent abuse with large requests
