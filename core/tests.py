from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from collection.models import Collection, CollectionItems
from catalog.models import Item

class AnonymousUserTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        self.librarian = User.objects.create_user(
            username="testlibrarian",
            email="librarian@example.com",
            password="testpassword",
            role=1
        )
        
        self.item1 = Item.objects.create(
            title="Public Item",
            status=0,
            location="Test Location",
            description="This is a public item"
        )
        
        self.item2 = Item.objects.create(
            title="Private Item",
            status=0,
            location="Test Location",
            description="This is a private item"
        )
        
        self.public_collection = Collection.objects.create(
            title="Public Collection",
            description="This is a public collection",
            creator=self.librarian,
            visibility=0
        )
        
        self.private_collection = Collection.objects.create(
            title="Private Collection",
            description="This is a private collection",
            creator=self.librarian,
            visibility=1
        )
        
        CollectionItems.objects.create(
            collection=self.public_collection,
            item=self.item1
        )
        
        CollectionItems.objects.create(
            collection=self.private_collection,
            item=self.item2
        )
    
    def test_homepage_access(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_public_collections(self):
        response = self.client.get(reverse('collection:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Collection")
    
    def test_cannot_view_private_collections(self):
        response = self.client.get(reverse('collection:list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Private Collection")
    
    def test_cannot_create_item(self):
        response = self.client.get(reverse('catalog:create_item'))
        self.assertRedirects(
            response, 
            '/accounts/login/?next=/catalog/create/', 
            status_code=302, 
            target_status_code=200,
            fetch_redirect_response=False
        )
    
    def test_cannot_create_collection(self):
        response = self.client.get(reverse('collection:create'))
        self.assertRedirects(
            response, 
            '/accounts/login/?next=/collection/create/', 
            status_code=302, 
            target_status_code=200,
            fetch_redirect_response=False
        )
    
    def test_cannot_leave_reviews(self):
        response = self.client.post(
            reverse('catalog:add_review', args=[self.item1.id]),
            {
                'rating': 5,
                'comment': 'Great item!'
            }
        )
        self.assertRedirects(
            response, 
            f'/accounts/login/?next=/catalog/reviews/{self.item1.id}/add/', 
            status_code=302, 
            target_status_code=200,
            fetch_redirect_response=False
        )

class SearchFunctionalityTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        self.librarian = User.objects.create_user(
            username="testlibrarian",
            email="librarian@example.com",
            password="testpassword",
            role=1
        )
        
        self.item1 = Item.objects.create(
            title="Beach House in Miami",
            status=0,
            location="Miami, FL",
            description="Beautiful beach house with ocean view"
        )
        
        self.item2 = Item.objects.create(
            title="Mountain Cabin",
            status=0,
            location="Denver, CO",
            description="Cozy cabin in the mountains"
        )
        
        self.item3 = Item.objects.create(
            title="Luxury Apartment",
            status=0,
            location="New York, NY",
            description="High-end apartment with city view"
        )
    
    def test_placeholder(self):
        self.assertTrue(True)
