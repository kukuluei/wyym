
from django.urls import path, re_path, include
from lists import views as list_views
from lists import urls as list_urls

urlpatterns = [
    path('', list_views.home_page, name='home'),  # 匹配项目根路径 '/'
    path('lists/', include(list_urls)),         # 将 '/lists/' 开头的路径交给 lists.urls 处理
]
