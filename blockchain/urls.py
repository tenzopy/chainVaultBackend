from django.urls import path
from .views import get_chain,mine_block,is_blockchain_valid

urlpatterns = [
    path('get/', get_chain,name='get_chain'),
    path('mine_block/', mine_block,name='mine_block'),
    path('validate/', is_blockchain_valid,name='validate_chain'),
]