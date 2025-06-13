from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = get_user_model()

class Amenity(models.Model):
    """
    Represents an amenity that can be associated with a listing.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_all_amenities(cls):
        """
        Returns all amenities.
        """
        return cls.objects.all()

class Listing(models.Model):
    """
    Represents a property listing.
    """
    PROPERTY_TYPE_CHOICES = [
        ('AP', 'Apartment'),
        ('HS', 'House'),
        ('ST', 'Studio'),
        ('CO', 'Condo'),
        ('TH', 'Townhouse'),
        ('OT', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=2, choices=PROPERTY_TYPE_CHOICES)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.DecimalField(max_digits=4, decimal_places=1)
    square_feet = models.PositiveIntegerField()
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='listings')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.address}"

    def main_image(self):
        """
        Returns the URL of the main image for the listing.
        """
        return self.images.first().image.url if self.images.exists() else None

    def average_rating(self):
        """
        Returns the average rating for the listing, or None if no reviews exist.
        """
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 2)
        return None

    def is_available(self, start_date, end_date):
        """
        Checks if the listing is available for the given date range.
        """
        overlapping = self.bookings.filter(
            models.Q(start_date__lt=end_date) & models.Q(end_date__gt=start_date)
        )
        return not overlapping.exists()

    @classmethod
    def get_active_listings(cls):
        """
        Returns all active listings.
        """
        return cls.objects.filter(is_active=True)

    @classmethod
    def get_by_owner(cls, user):
        """
        Returns all listings owned by the given user.
        """
        return cls.objects.filter(owner=user)

    def get_amenities_list(self):
        """
        Returns a list of amenity names for the listing.
        """
        return list(self.amenities.values_list('name', flat=True))

    def get_reviews(self):
        """
        Returns all reviews for the listing.
        """
        return self.reviews.all()

    def get_bookings(self):
        """
        Returns all bookings for the listing.
        """
        return self.bookings.all()

    class Meta:
        ordering = ['-created_at']

class ListingImage(models.Model):
    """
    Represents an image associated with a listing.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"

    def image_url(self):
        """
        Returns the URL of the image.
        """
        if self.image:
            return self.image.url
        return None

@receiver(post_delete, sender=ListingImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes image file from filesystem when corresponding `ListingImage` object is deleted.
    """
    if instance.image:
        instance.image.delete(save=False)

class Review(models.Model):
    """
    Represents a review for a listing by a user.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} for {self.listing}"

    @classmethod
    def get_reviews_for_listing(cls, listing):
        """
        Returns all reviews for a given listing.
        """
        return cls.objects.filter(listing=listing)

    @classmethod
    def get_reviews_by_user(cls, user):
        """
        Returns all reviews made by a user.
        """
        return cls.objects.filter(user=user)

class Booking(models.Model):
    """
    Represents a booking for a listing by a user.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='PENDING')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking by {self.user} for {self.listing} ({self.start_date} to {self.end_date})"

    @classmethod
    def get_bookings_for_listing(cls, listing):
        """
        Returns all bookings for a given listing.
        """
        return cls.objects.filter(listing=listing)

    @classmethod
    def get_bookings_by_user(cls, user):
        """
        Returns all bookings made by a user.
        """
        return cls.objects.filter(user=user)

class Favorite(models.Model):
    """
    Represents a user's favorite listing.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} favorited {self.listing}"

    @classmethod
    def get_favorites_for_user(cls, user):
        """
        Returns all favorite listings for a user.
        """
        return cls.objects.filter(user=user)

    @classmethod
    def is_favorited(cls, user, listing):
        """
        Checks if a listing is favorited by a user.
        """
        return cls.objects.filter(user=user, listing=listing).exists()

class Inquiry(models.Model):
    """
    Represents an inquiry made by a user for a listing.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry by {self.user} for {self.listing}"

    @classmethod
    def get_inquiries_for_listing(cls, listing):
        """
        Returns all inquiries for a given listing.
        """
        return cls.objects.filter(listing=listing)

    @classmethod
    def get_inquiries_by_user(cls, user):
        """
        Returns all inquiries made by a user.
        """
        return cls.objects.filter(user=user)
