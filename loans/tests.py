from django.test import TestCase, Client
from loans.models import Loan
from catalog.models import Item
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date, timedelta

class LoanModelTests(TestCase):
    
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
            title="Loanable Item",
            status=0,
            location="Test Location",
            description="This is a test item"
        )
        
        today = date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=7)
        due_date = end_date
        
        self.loan = Loan.objects.create(
            item=self.item,
            requester=self.patron,
            status=0,
            start_date=start_date,
            end_date=end_date,
            due_date=due_date,
            reservation_total=100.00
        )
    
    def test_loan_creation(self):
        self.assertEqual(self.loan.item, self.item)
        self.assertEqual(self.loan.requester, self.patron)
        self.assertEqual(self.loan.status, 0)
        self.assertEqual(self.loan.reservation_total, 100.00)
    
    def test_loan_status_update(self):
        self.loan.status = 1
        self.loan.save()
        self.assertEqual(self.loan.status, 1)
        
        self.loan.status = 2
        self.loan.save()
        self.assertEqual(self.loan.status, 2)
        
        self.loan.status = 3
        self.loan.save()
        self.assertEqual(self.loan.status, 3)
    
    def test_loan_dates(self):
        today = date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=7)
        
        self.assertEqual(self.loan.start_date, start_date)
        self.assertEqual(self.loan.end_date, end_date)
        self.assertEqual(self.loan.due_date, end_date)

class LoanViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        self.patron = User.objects.create_user(
            username="testpatron",
            email="patron@example.com",
            password="testpassword",
            role=0
        )
        
        self.other_patron = User.objects.create_user(
            username="otherpatron",
            email="otherpatron@example.com",
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
            title="Loanable Item 1",
            status=0,
            location="Test Location",
            description="This is test item 1"
        )
        
        self.item2 = Item.objects.create(
            title="Loanable Item 2",
            status=0,
            location="Test Location",
            description="This is test item 2"
        )
        
        today = date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=7)
        
        self.pending_loan = Loan.objects.create(
            item=self.item1,
            requester=self.patron,
            status=0,
            start_date=start_date,
            end_date=end_date,
            due_date=end_date
        )
        
        self.approved_loan = Loan.objects.create(
            item=self.item2,
            requester=self.other_patron,
            status=1,
            start_date=start_date,
            end_date=end_date,
            due_date=end_date
        )
    
    def test_placeholder(self):
        self.assertTrue(True)


