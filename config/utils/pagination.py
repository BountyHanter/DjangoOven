from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 9                  # дефолт для всего проекта
    page_size_query_param = "page_size"
    max_page_size = 100              # жёсткий потолок
