from django.test import TestCase, Client
from catalog.models import Item, ItemReview
from collection.models import Collection, CollectionItems
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import tempfile

class ItemModelTests(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.librarian = User.objects.create_user(
            username="testlibrarian",
            email="librarian@example.com",
            password="testpassword", 
            role=1
        )
        
        self.item = Item.objects.create(
            title="Test Item",
            status=0,
            location="Test Location",
            description="This is a test item",
            created_by=self.librarian
        )
    
    def test_item_creation(self):
        self.assertEqual(self.item.title, "Test Item")
        self.assertEqual(self.item.status, 0)
        self.assertEqual(self.item.location, "Test Location")
        self.assertEqual(self.item.description, "This is a test item")
        self.assertEqual(self.item.created_by, self.librarian)
    
    def test_item_string_representation(self):
        self.assertEqual(str(self.item), "Test Item")
    
    def test_item_status_choices(self):
        self.item.status = 0
        self.item.save()
        self.assertEqual(self.item.status, 0)
        
        self.item.status = 1
        self.item.save()
        self.assertEqual(self.item.status, 1)
        
        self.item.status = 2
        self.item.save() 
        self.assertEqual(self.item.status, 2)

class ItemReviewModelTests(TestCase):
    
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
        
        self.item = Item.objects.create(
            title="Reviewable Item",
            status=0,
            location="Test Location",
            description="This is a test item",
            created_by=self.librarian
        )
        
        self.review = ItemReview.objects.create(
            rating=4,
            comment="This is a great item!",
            creator=self.patron,
            item=self.item
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, "This is a great item!")
        self.assertEqual(self.review.creator, self.patron)
        self.assertEqual(self.review.item, self.item)
    
    def test_review_relationship(self):
        self.assertEqual(self.item.reviews.count(), 1)
        self.assertEqual(self.item.reviews.first(), self.review)

class CatalogViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
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
            title="Item One",
            status=0,
            location="Test Location",
            description="This is item one",
            created_by=self.librarian
        )
        
        self.item2 = Item.objects.create(
            title="Item Two",
            status=0,
            location="Test Location",
            description="This is item two",
            created_by=self.librarian
        )
        
        self.collection = Collection.objects.create(
            title="Test Collection",
            description="This is a test collection",
            creator=self.librarian,
            visibility=0
        )
        
        CollectionItems.objects.create(
            collection=self.collection,
            item=self.item1
        )
    
    def test_item_create_view_patron(self):
        self.client.login(username='testpatron', password='testpassword')
        
        response = self.client.get(reverse('catalog:create_item'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_item_review_creation(self):
        self.client.login(username='testpatron', password='testpassword')
        
        response = self.client.post(
            reverse('catalog:add_review', args=[self.item2.id]), 
            {
                'rating': 5,
                'comment': 'Excellent item!'
            }
        )
        
        self.assertTrue(ItemReview.objects.filter(
            item=self.item2, 
            creator=self.patron,
            rating=5,
            comment='Excellent item!'
        ).exists())
