from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Listing
from .forms import ListingForm

# Function-based view for listing all listings with search and pagination
def listing_list(request):
    """
    Display a list of all listings, with optional search and pagination.
    """
    query = request.GET.get('q')
    listings = Listing.objects.all()
    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )
    paginator = Paginator(listings, 10)  # Show 10 listings per page
    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, 'listings/listing_list.html', {'listings': listings, 'query': query})

# Function-based view for a single listing
def listing_detail(request, pk):
    """
    Display the details of a single listing.
    """
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'listings/listing_detail.html', {'listing': listing})

# Function-based view for creating a listing
@login_required
def listing_create(request):
    """
    Allow authenticated users to create a new listing.
    """
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, "Listing created successfully.")
            return redirect('listings:listing_detail', pk=listing.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm()
    return render(request, 'listings/listing_form.html', {'form': form})

# Function-based view for updating a listing
@login_required
def listing_update(request, pk):
    """
    Allow owners to update their listing.
    """
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.owner:
        messages.error(request, "You do not have permission to edit this listing.")
        return redirect('listings:listing_detail', pk=pk)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully.")
            return redirect('listings:listing_detail', pk=pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/listing_form.html', {'form': form})

# Function-based view for deleting a listing
@login_required
def listing_delete(request, pk):
    """
    Allow owners to delete their listing.
    """
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.owner:
        messages.error(request, "You do not have permission to delete this listing.")
        return redirect('listings:listing_detail', pk=pk)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, "Listing deleted successfully.")
        return redirect('listings:listing_list')
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})

# Class-based views (alternative to function-based views)
class ListingListView(ListView):
    """
    Display a list of all listings, with optional search and pagination.
    """
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ListingDetailView(DetailView):
    """
    Display the details of a single listing.
    """
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

@method_decorator(login_required, name='dispatch')
class ListingCreateView(CreateView):
    """
    Allow authenticated users to create a new listing.
    """
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Listing created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class ListingUpdateView(UpdateView):
    """
    Allow owners to update their listing.
    """
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'

    def get_queryset(self):
        return Listing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Listing updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class ListingDeleteView(DeleteView):
    """
    Allow owners to delete their listing.
    """
    model = Listing
    template_name = 'listings/listing_confirm_delete.html'
    success_url = reverse_lazy('listings:listing_list')

    def get_queryset(self):
        return Listing.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Listing deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Optionally, add a mixin for owner permissions if needed in the future
# class OwnerRequiredMixin:
#     def get_queryset(self):
#         return super().get_queryset().filter(owner=self.request.user)
