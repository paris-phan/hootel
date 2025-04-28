from django.test import TestCase, Client
from collection.models import Collection, CollectionItems, CollectionAuthorizedUser
from catalog.models import Item
from django.contrib.auth import get_user_model
from django.urls import reverse

class CollectionModelTests(TestCase):
    
    def setUp(self):
        User = get_user_model()
        
        self.patron = User.objects.create_user(
            username="testpatron",
            email="patron@example.com",
            password="testpassword",
            role=0
        )
        
        self.librarian = User.objects.create_user(
            username="testlibrarian",
            email="librarian@example.com",
            password="testpassword",
            role=1
        )
        
        self.item1 = Item.objects.create(
            title="Test Item 1",
            status=0,
            location="Test Location",
            description="This is test item 1"
        )
        
        self.item2 = Item.objects.create(
            title="Test Item 2",
            status=0,
            location="Test Location",
            description="This is test item 2"
        )
        
        self.lib_public_collection = Collection.objects.create(
            title="Librarian Public Collection",
            description="This is a public collection created by a librarian",
            creator=self.librarian,
            visibility=0
        )
        
        self.lib_private_collection = Collection.objects.create(
            title="Librarian Private Collection",
            description="This is a private collection created by a librarian",
            creator=self.librarian,
            visibility=1
        )
        
        self.patron_collection = Collection.objects.create(
            title="Patron Collection",
            description="This is a collection created by a patron",
            creator=self.patron,
            visibility=0
        )
        
        CollectionItems.objects.create(
            collection=self.lib_public_collection,
            item=self.item1
        )
        
        CollectionItems.objects.create(
            collection=self.lib_private_collection,
            item=self.item2
        )
        
        CollectionAuthorizedUser.objects.create(
            collection=self.lib_private_collection,
            user=self.patron
        )
    
    def test_collection_creation(self):
        self.assertEqual(self.lib_public_collection.title, "Librarian Public Collection")
        self.assertEqual(self.lib_public_collection.description, "This is a public collection created by a librarian")
        self.assertEqual(self.lib_public_collection.creator, self.librarian)
        self.assertEqual(self.lib_public_collection.visibility, 0)
        
        self.assertEqual(self.lib_private_collection.title, "Librarian Private Collection")
        self.assertEqual(self.lib_private_collection.visibility, 1)
        
        self.assertEqual(self.patron_collection.title, "Patron Collection")
        self.assertEqual(self.patron_collection.creator, self.patron)
        self.assertEqual(self.patron_collection.visibility, 0)
    
    def test_collection_string_representation(self):
        self.assertEqual(str(self.lib_public_collection), "Librarian Public Collection")
    
    def test_collection_items_relationship(self):
        collection_item = CollectionItems.objects.get(collection=self.lib_public_collection, item=self.item1)
        self.assertEqual(collection_item.collection, self.lib_public_collection)
        self.assertEqual(collection_item.item, self.item1)
        
        collection_item = CollectionItems.objects.get(collection=self.lib_private_collection, item=self.item2)
        self.assertEqual(collection_item.collection, self.lib_private_collection)
        self.assertEqual(collection_item.item, self.item2)
    
    def test_collection_authorized_users(self):
        auth_user = CollectionAuthorizedUser.objects.get(
            collection=self.lib_private_collection, 
            user=self.patron
        )
        self.assertEqual(auth_user.collection, self.lib_private_collection)
        self.assertEqual(auth_user.user, self.patron)
