from django.views import View, generic
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.forms import modelformset_factory, inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from decouple import config
import stripe
import math
import uuid


# from user.forms import AddressForm
from user.models import Address
from .forms import ItemCreateForm, OrderCreateForm, PaymentMethodForm, CouponForm, UserCouponForm, ShippingAddressForm, CategoryForm, SubcategoryForm, BrandForm
from .models import Category, Subcategory, Brand, Item, OrderItem, Order, Stripe, Coupon


stripe.api_key = config('STRIPE_SECRET_KEY')


# stripe.AccountLink.create(
#     account='{{CONNECTED_ACCOUNT_ID}}',
#     refresh_url="localhost:8000/reauth",
#     return_url="localhost:8000/return",
#     type="account_onboarding",
# )

# class StripeAccountView(View):
# def get(self, request, *args, **kwargs):
#     account = stripe.Account.create(
#         type="standard",
#         country="US",
#         email="jenny.rosen@example.com",
#     )
#     print(account)
#     stripe_acc = Stripe(
#         user=self.request.user,
#         id=account.id
#     )
#     stripe_acc.save()


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:

            order = Order.objects.filter(
                user=self.request.user, ordered=False).first()

            checkout_session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {"name": "T-shirt"},
                            "unit_amount": math.ceil(order.get_total()),
                            "tax_behavior": "exclusive",
                        },
                        "quantity": 1,
                    },
                    # {"price": order.get_total()},
                ],
                success_url="http://localhost:8000/success",
                cancel_url="http://localhost:8000/cancel",
            )
        except Exception as e:
            return JsonResponse({'Error': str(e)})
        return JsonResponse({'id': checkout_session.id})


class CancelView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'core/payment_cancel.html'


class SuccessView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'core/payment_success.html'


# class PaymentView(LoginRequiredMixin, generic.TemplateView):
#     template_name = 'core/payment.html'

#     def get_context_data(self, **kwargs):
#         context = super(PaymentView, self).get_context_data(**kwargs)
#         context['order'] = Order.objects.filter(
#             user=self.request.user, ordered=False).first()
#         return context


class OrderFollowupView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'core/order_followup.html'
    paginate_by = 2

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user, ordered=True)
        return queryset


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(
            user=self.request.user, ordered=False).first()
        if self.kwargs.get('payment_method') == 'D':
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()
            order_items = order.items.all()
            for item in order_items:
                item.ordered = True
                item.save()
            messages.success(
                self.request, f'Your ordered has been made. Please follow with us for any updates.')
            return redirect('core:home')
        elif self.kwargs.get('payment_method') == 'S':
            pass
        elif self.kwargs.get('payment_method') == 'P':
            pass
        messages.warning()
        return redirect('core:checkout', order.uuid)


class CheckoutView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(
            user=self.request.user, ordered=False).first()
        billing_address = Address.objects.filter(
            user=self.request.user, address_type='B').first()
        form = PaymentMethodForm()
        ad_form = ShippingAddressForm()
        return render(self.request, 'core/checkout.html', {'order': order, 'billing_address': billing_address, 'form': form, 'ad_form': ad_form})

    def post(self, *args, **kwargs):
        order = Order.objects.filter(
            user=self.request.user, ordered=False).first()
        form = PaymentMethodForm(self.request.POST)
        ad_form = ShippingAddressForm(self.request.POST)

        billing_address = Address.objects.filter(
            user=self.request.user, address_type='B').first()
        order.billing_address = billing_address

        if form.is_valid() and ad_form.is_valid():
            if order.billing_address:
                payment_method = form.cleaned_data.get('payment_choice')

                default = ad_form.cleaned_data.get('default')
                if default:
                    shipping_address = Address.objects.get_or_create(
                        user=order.user,
                        apartment=order.billing_address.apartment,
                        building=order.billing_address.building,
                        street=order.billing_address.street,
                        district=order.billing_address.district,
                        city=order.billing_address.city,
                        country=order.billing_address.country,
                        zip=order.billing_address.zip,
                        address_type='S',
                        default=default,
                    )

                    shipping_address_inst = Address.objects.filter(
                        user=order.user, address_type='S').first()

                    order.shipping_address = shipping_address_inst
                    order.billing_address.default = True
                    order.save()
                    return redirect('core:payment', payment_method)
                else:

                    for field in ad_form:
                        if field == '':
                            messages.info(
                                self.request, f'Your shipping address fields aren\'t complete')
                            return redirect('core:checkout', order.uuid)
                        return True

                    shipping_address = Address.objects.get_or_create(
                        user=order.user,
                        apartment=ad_form.cleaned_data.get('apartment'),
                        building=ad_form.cleaned_data.get('building'),
                        street=ad_form.cleaned_data.get('street'),
                        district=ad_form.cleaned_data.get('district'),
                        city=ad_form.cleaned_data.get('city'),
                        country=ad_form.cleaned_data.get('country'),
                        zip=ad_form.cleaned_data.get('zip'),
                        address_type='S',
                        default=False,
                    )
                    order.shipping_address.add(shipping_address)
                    order.save()
                    return redirect('core:payment', payment_method)

            else:
                messages.info(
                    self.request, f'You don\'t have a registered billing address. Please update your account info and follow up with your purchase.')
                return redirect('auth:profile_update', self.request.user.profile.slug)

    def test_func(self):
        pk = self.kwargs['pk']
        order = Order.objects.get(uuid=pk)
        if self.request.user == order.user:
            return True
        return False


class UseCouponView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.filter(
                user=self.request.user, ordered=False).first()
            if order:

                # updated_request = request.POST.copy()
                # code = uuid.UUID(updated_request.get('code'))
                # updated_request.update({'code': code})
                # form = UserCouponForm(updated_request)

                form = request.POST
                code = uuid.UUID(form['code'])
                coupon = get_object_or_404(Coupon, code=code)

                if coupon.expired:
                    messages.warning(request, f"This Code has expired !")
                    return redirect('core:order_summary')
                if self.request.user in coupon.user.all():
                    messages.warning(
                        request, f"You have already used this code !")
                    return redirect('core:order_summary')

                coupon.user.add(self.request.user)
                order.coupon = coupon
                coupon.save()
                order.save()
                messages.success(request, f"Promocode Activated !")
                return redirect('core:order_summary')

            messages.error(request, f"You don't have an active order.")
            return redirect('core:order_summary')
        except:
            messages.warning(request, f"This Code is invalid !")
            return redirect('core:order_summary')


class CouponUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Coupon
    fields = ('expired',)
    success_url = reverse_lazy('core:coupons')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class CouponListView(UserPassesTestMixin, generic.ListView):
    model = Coupon
    template_name = 'core/coupon_list.html'
    paginate_by = 2

    def get_queryset(self):
        queryset = Coupon.objects.filter(expired=False)
        if queryset is not None:
            return queryset
        return super(CouponListView, self).get_queryset()

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class CouponCreateView(UserPassesTestMixin, generic.CreateView):
    model = Coupon
    form_class = CouponForm
    template_name = 'core/coupon_create.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class BrandDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Brand
    template_name = 'core/brand_confirm_delete.html'
    success_url = reverse_lazy('core:categories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class BrandUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'core/brand_create.html'
    success_url = reverse_lazy('core:brand')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


# class BrandListView(UserPassesTestMixin, generic.ListView):
#     model = Brand
#     template_name = 'core/brand_list.html'
#     paginate_by = 2

#     def get_queryset(self):
#         queryset = Brand.objects.filter(
#             category__slug=self.kwargs.get('cat_slug'), sub_category__slug=self.kwargs.get('scat_slug'))
#         if queryset is not None:
#             return queryset
#         return super(BrandListView, self).get_queryset()

#     def test_func(self):
#         if self.request.user.is_superuser:
#             return True
#         return False


class BrandCreateView(UserPassesTestMixin, generic.CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'core/brand_create.html'
    success_url = reverse_lazy('core:brands')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class SubcategoryDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Subcategory
    template_name = 'core/subcategory_confirm_delete.html'
    success_url = reverse_lazy('core:categories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class SubcategoryUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Subcategory
    form_class = SubcategoryForm
    template_name = 'core/subcategory_create.html'
    success_url = reverse_lazy('core:subcategories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class SubcategoryDetailView(View):
    def get(self, *args, **kwargs):
        # paginator
        queryset = Brand.objects.filter(
            sub_category__slug=self.kwargs.get('slug'))
        return render(self.request, 'core/subcategory_detail.html', {'queryset': queryset})


# class SubcategoryListView(UserPassesTestMixin, generic.ListView):
#     model = Subcategory
#     template_name = 'core/subcategory_list.html'
#     paginate_by = 2

#     def test_func(self):
#         if self.request.user.is_superuser:
#             return True
#         return False


class SubcategoryCreateView(UserPassesTestMixin, generic.CreateView):
    model = Subcategory
    form_class = SubcategoryForm
    template_name = 'core/subcategory_create.html'
    success_url = reverse_lazy('core:subcategories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class CategoryDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Category
    template_name = 'core/category_confirm_delete.html'
    success_url = reverse_lazy('core:categories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class CategoryUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_create.html'
    success_url = reverse_lazy('core:categories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class CategoryDetailView(View):

    def get(self, *args, **kwargs):
        # paginator
        queryset = Subcategory.objects.filter(
            category__slug=self.kwargs.get('slug'))
        return render(self.request, 'core/category_detail.html', {'queryset': queryset})


class CategoryListView(generic.ListView):
    model = Category
    template_name = 'core/category_list.html'
    paginate_by = 2


class CategoryCreateView(UserPassesTestMixin, generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_create.html'
    success_url = reverse_lazy('core:categories')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


@ login_required()
def increase_order_item(request, slug):
    item = Item.objects.get(slug=slug)
    order = Order.objects.filter(
        user=request.user, ordered=False).first()
    order_item = order.items.get(item=item)

    if order_item.quantity < item.quantity:
        order_item.quantity += 1
        order_item.save()
        return redirect("core:order_summary")
    else:
        messages.error(
            request, f'The current item quantity is the maximum product quantity in store.')
        return redirect("core:order_summary")


@ login_required()
def decrease_order_item(request, slug):
    item = Item.objects.get(slug=slug)
    order = Order.objects.filter(
        user=request.user, ordered=False).first()
    order_item = order.items.get(item=item)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
        return redirect("core:order_summary")
    else:
        order.items.remove(order_item)
        order_item.delete()
        messages.error(request, f'Product has been removed from cart.')
        if not order.items.all():
            order.delete()
            messages.error(request, f'Your order had been deleted.')
            return redirect("core:order_summary")
        return redirect("core:order_summary")


@ login_required()
def delete_order_item(request, slug):
    item = Item.objects.get(slug=slug)
    order = Order.objects.filter(
        user=request.user, ordered=False).first()
    order_item = order.items.get(item=item)

    if request.method == "POST":
        order.items.remove(order_item)
        order_item.delete()
        if not order.items.all():
            order.delete()
            messages.error(request, f'Your order had been deleted.')
            return redirect("core:order_summary")
        return redirect("core:order_summary")

    return render(request, 'core/orderitem_confirm_delete.html', {'object': item, 'order': order})


@ login_required()
def delete_order(request, pk):
    order = Order.objects.get(uuid=pk)

    if request.method == "POST":
        order.delete()
        return redirect("core:home")

    return render(request, 'core/item_confirm_delete.html', {'object': order})


class OrderSummaryView(LoginRequiredMixin, FormMixin, generic.ListView):
    model = Order
    form_class = UserCouponForm
    template_name = 'core/order_summary.html'

    def get_queryset(self):
        try:
            queryset = Order.objects.filter(
                user=self.request.user, ordered=False).first()
            return queryset
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            redirect('core:home')


@ login_required
def add_to_cart(request, slug):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            item = Item.objects.get(slug=slug)
            quantity = form.cleaned_data['quantity']

            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False).first()
            order = Order.objects.filter(
                user=request.user, ordered=False).first()

            if order:
                if order_item:
                    order_item.quantity += quantity
                    order_item.save()
                    order.items.add(order_item)
                    messages.info(request, "This item quantity was updated.")
                    return redirect('core:order_summary')

                else:
                    order_item = OrderItem.objects.create(
                        item=item, quantity=quantity, user=request.user)
                    order.items.add(order_item)
                    messages.info(request, "This item was added to your cart.")
                    return redirect('core:order_summary')

            else:
                order_item = OrderItem.objects.create(
                    item=item, quantity=quantity, user=request.user)

                billing_address = Address.objects.filter(
                    user=request.user, address_type='B').first()

                order = Order.objects.create(
                    user=request.user, billing_address=billing_address)
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                return redirect('core:order_summary')


class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Item
    template_name = 'core/item_confirm_delete.html'
    success_url = reverse_lazy('core:home')

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.seller:
            return True
        return False


class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Item
    form_class = ItemCreateForm
    template_name = 'core/item_create.html'

    def test_func(self):
        item = self.get_object()

        if self.request.user == item.seller:
            return True
        return False


class ItemDetailView(FormMixin, generic.DetailView):
    model = Item
    form_class = OrderCreateForm

    def get_context_data(self, **kwargs):
        item = self.get_object()
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(Q(name__contains=item.name) |
                                               Q(category=item.category)).exclude(id=item.id)
        if self.request.user.is_authenticated:
            context['order'] = Order.objects.filter(
                user=self.request.user, ordered=False).first()
        return context


class ItemCreateView(LoginRequiredMixin, generic.CreateView):
    model = Item
    form_class = ItemCreateForm
    template_name = 'core/item_create.html'

    def form_valid(self, form):
        product = form.save(commit=False)
        product.seller = self.request.user
        product.save()
        return super().form_valid(form)


class BrowseView(generic.ListView):
    model = Item
    template_name = 'core/browse.html'
    paginate_by = 1

    def get_queryset(self):
        queryset = super().get_queryset()

        hot_deals = self.request.GET.get('hot_deals')
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        sub_category = self.request.GET.get('sub_category')
        brand = self.request.GET.get('brand')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        order_by = self.request.GET.get('order_by')

        if order_by:
            if order_by == 'first':
                queryset = queryset.order_by('created_at')
            if order_by == 'last':
                queryset = queryset.order_by('-created_at')
            if order_by == 'lowest':
                queryset = queryset.order_by('price')
            if order_by == 'highest':
                queryset = queryset.order_by('-price')

        if hot_deals:
            queryset = queryset.filter(discount_price__isnull=False)
        if search:
            queryset = queryset.filter(Q(category__slug__icontains=search) | Q(
                sub_category__slug__icontains=search) | Q(brand__slug__icontains=search) | Q(name__icontains=search))
        if category:
            queryset = queryset.filter(category=category)
        if sub_category:
            queryset = queryset.filter(sub_category=sub_category)
        if brand:
            queryset = queryset.filter(sub_category=sub_category)
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        return queryset

    def get_context_data(self, **kwargs):
        filter = self.request.GET.dict()

        # subcatg_set = set(Item.objects.all().values_list(
        #     'sub_category__name', flat=True))
        # brand_set = set(Item.objects.all().values_list(
        #     'brand__name', flat=True))
        context = super().get_context_data(**kwargs)
        # context['last']
        context['categories'] = Category.objects.all()
        # set(Item.objects.all().values_list(
        #     'category__name', flat=True))
        context['sub_categories'] = Subcategory.objects.all()
        # Subcategory.objects.filter(
        #     name__in=subcatg_set).values('category', 'name')
        context['brands'] = Brand.objects.all()
        # Brand.objects.filter(name__in=brand_set)

        if filter:
            for key, value in filter.items():
                context[key] = value

        return context


def home(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    items = Item.objects.all()
    order = None
    if request.user.is_authenticated:
        order = Order.objects.filter(
            user=request.user, ordered=False).first()

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'items': items,
        'order': order,
    }

    return render(request, 'core/home.html', context)
