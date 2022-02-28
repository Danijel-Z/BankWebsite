import os
from model import Customer

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import ( 
    ComplexField, 
    CorsOptions, 
    SearchIndex, 
    ScoringProfile, 
    SearchFieldDataType, 
    SimpleField, 
    SearchableField 
)

index_name = "customers"
# Get the service endpoint and API key from the environment
endpoint = "https://customer.search.windows.net"
key = "1E8B6CE47A624F80EE657D63E9988697"

# Create a client
credential = AzureKeyCredential(key)


client = SearchClient(endpoint=endpoint,
                      index_name=index_name,
                      credential=credential)

def createIndex():
    
    searchIndexClient = SearchIndexClient(endpoint=endpoint,
                        index_name=index_name,
                        credential=credential)

    fields = [
            SearchableField(name="id", type=SearchFieldDataType.String, sortable=True, key=True),
            SimpleField(name="Birthday", type=SearchFieldDataType.String, sortable=True),
            
            SearchableField(name="GivenName", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="Surname", type=SearchFieldDataType.String, sortable=True),
            
            SimpleField(name="Streetaddress", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="City", type=SearchFieldDataType.String, sortable=True)
            ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []

    index = SearchIndex(
        name=index_name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = searchIndexClient.create_index(index)                    


def addDocuments():
    
    docs = []
    for customer in Customer.query.all():
        d = {
               "id" : str(customer.id),
               "Birthday": str(customer.Birthday),
               "GivenName": customer.GivenName,
                "Surname" : customer.Surname,
               "Streetaddress": customer.Streetaddress,
               "City": customer.City,

        }
        docs.append(d)
    result = client.upload_documents(documents=docs)


    