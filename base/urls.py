from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import chatbot, views
from .sitemaps import sitemaps

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),

    path(
        'project/<slug:slug>/',
        views.project_detail,
        name='project_detail'
    ),

    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    path('estimate/', views.estimate, name='estimate'),
    path('review/', views.leave_review, name='leave_review'),

    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.post_detail, name='post_detail'),

    path('chat/knowledge/', chatbot.knowledge, name='chat_knowledge'),
    path('chat/lead/', chatbot.lead, name='chat_lead'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
