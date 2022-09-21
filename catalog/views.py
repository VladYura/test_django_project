from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import RenewBookForm


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksByLibrarianListView(PermissionRequiredMixin, ListView):
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_librarian.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.order_by('due_back')


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_visits': num_visits,
        },
    )


class BookListView(ListView):
    model = Book
    paginate_by = 10
    #  context_object_name = 'my_book_list'  # собственное имя переменной контекста в шаблоне

    # def get_context_data(self, **kwargs):
    #     #  Получаем базовую реализацию контекста
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     #  Добавляем новую переменную к контексту и инициализируем её некоторым значением
    #     context['some_data'] = 'This is just some data'
    #     return context

    # queryset = Book.objects.filter(title__icontains='war')[:5]  # Получение 5 книг, содержащих слово 'war' в заголовке

    # Также можно с помощью функции

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5]

    template_name = 'book_list.html'


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'


class AuthorListView(ListView):
    model = Author
    template_name = 'author_list.html'


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'author_detail.html'


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            return HttpResponseRedirect(reverse('borrowed-list'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=4)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request,
                  'book_renew_librarian.html',
                  {'form': form, 'bookinst': book_inst})


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    template_name = 'action_with_data/author_form.html'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'
    template_name = 'action_with_data/author_form.html'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'
    template_name = 'action_with_data/author_confirm_delete.html'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    template_name = 'action_with_data/book_form.html'


class BookUpdate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    template_name = 'action_with_data/book_form.html'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'
    template_name = 'action_with_data/book_confirm_delete.html'
