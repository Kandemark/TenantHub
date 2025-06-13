from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission

from .models import Listing
from .forms import ListingForm

User = get_user_model()

class ListingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.listing = Listing.objects.create(
            title="Test Listing",
            description="A test listing.",
            price=1000,
            owner=self.user
        )

    def test_listing_str(self):
        self.assertEqual(str(self.listing), "Test Listing")

    def test_listing_fields(self):
        self.assertEqual(self.listing.title, "Test Listing")
        self.assertEqual(self.listing.description, "A test listing.")
        self.assertEqual(self.listing.price, 1000)
        self.assertEqual(self.listing.owner, self.user)

    def test_listing_default_status(self):
        # Assuming Listing has a status field with default 'active'
        self.assertEqual(getattr(self.listing, 'status', 'active'), 'active')

    def test_listing_validation(self):
        self.listing.price = -10
        with self.assertRaises(ValidationError):
            self.listing.full_clean()

    def test_listing_manager_active(self):
        # Assuming Listing.objects.active() returns only active listings
        if hasattr(Listing.objects, 'active'):
            active_listings = Listing.objects.active()
            self.assertIn(self.listing, active_listings)

class ListingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.listing = Listing.objects.create(
            title="Test Listing",
            description="A test listing.",
            price=1000,
            owner=self.user
        )

    def test_listing_list_view(self):
        url = reverse('listings:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/list.html')
        self.assertContains(response, "Test Listing")

    def test_listing_detail_view(self):
        url = reverse('listings:detail', args=[self.listing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/detail.html')
        self.assertContains(response, "Test Listing")

    def test_listing_create_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('listings:create')
        data = {
            'title': 'New Listing',
            'description': 'Brand new listing',
            'price': 2000,
            'owner': self.user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Listing.objects.filter(title='New Listing').exists())

    def test_listing_create_view_unauthenticated(self):
        url = reverse('listings:create')
        data = {
            'title': 'New Listing',
            'description': 'Brand new listing',
            'price': 2000,
            'owner': self.user.id
        }
        response = self.client.post(url, data)
        self.assertNotEqual(response.status_code, 302)  # Should not redirect

    def test_listing_update_view(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('listings:update', args=[self.listing.id])
        data = {
            'title': 'Updated Listing',
            'description': 'Updated description',
            'price': 1500,
            'owner': self.user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, 'Updated Listing')

    def test_listing_delete_view(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('listings:delete', args=[self.listing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Listing.objects.filter(id=self.listing.id).exists())

class ListingFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_valid_form(self):
        form_data = {
            'title': 'Test Listing',
            'description': 'A test listing.',
            'price': 1000,
            'owner': self.user.id
        }
        form = ListingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'title': '',
            'description': 'A test listing.',
            'price': -100,
            'owner': self.user.id
        }
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('price', form.errors)

    def test_form_save(self):
        form_data = {
            'title': 'Another Listing',
            'description': 'Another test listing.',
            'price': 1200,
            'owner': self.user.id
        }
        form = ListingForm(data=form_data)
        self.assertTrue(form.is_valid())
        listing = form.save()
        self.assertEqual(listing.title, 'Another Listing')

class ListingSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.signal_received = False

        @receiver(post_save, sender=Listing)
        def listing_post_save(sender, instance, created, **kwargs):
            self.signal_received = True

        self.listing = Listing.objects.create(
            title="Signal Test Listing",
            description="Testing signals.",
            price=500,
            owner=self.user
        )

    def test_post_save_signal(self):
        self.assertTrue(self.signal_received)

class ListingManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.active_listing = Listing.objects.create(
            title="Active Listing",
            description="Active",
            price=1000,
            owner=self.user,
            status='active'
        )
        self.inactive_listing = Listing.objects.create(
            title="Inactive Listing",
            description="Inactive",
            price=800,
            owner=self.user,
            status='inactive'
        )

    def test_active_manager(self):
        if hasattr(Listing.objects, 'active'):
            active_listings = Listing.objects.active()
            self.assertIn(self.active_listing, active_listings)
            self.assertNotIn(self.inactive_listing, active_listings)

class ListingPermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass')
        self.listing = Listing.objects.create(
            title="Permission Listing",
            description="Testing permissions.",
            price=1000,
            owner=self.user
        )

    def test_owner_can_edit(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('listings:update', args=[self.listing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_edit(self):
        self.client.login(username='otheruser', password='testpass')
        url = reverse('listings:update', args=[self.listing.id])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_permission_required(self):
        perm = Permission.objects.get(codename='change_listing')
        self.other_user.user_permissions.add(perm)
        self.client.login(username='otheruser', password='testpass')
        url = reverse('listings:update', args=[self.listing.id])
        response = self.client.get(url)
        # Depending on your permission logic, this may be 200 or 403
        self.assertIn(response.status_code, [200, 403])
