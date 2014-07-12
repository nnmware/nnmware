from django.db.models import Q
from django.views.generic.dates import YearArchiveView, MonthArchiveView, DayArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from nnmware.core.data import get_queryset_category
from nnmware.apps.board.models import Board, BoardCategory
from nnmware.apps.board.forms import BoardForm


class BoardList(ListView):
    model = Board


class BoardYearList(YearArchiveView):
    template_name = 'board/board_list.html'
    model = Board
    date_field = "created_date"
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class BoardMonthList(MonthArchiveView):
    template_name = 'board/board_list.html'
    model = Board
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True


class BoardDayList(DayArchiveView):
    template_name = 'board/board_list.html'
    model = Board
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True


class BoardUserList(ListView):
    model = Board

    def get_queryset(self):
        return Board.objects.filter(user=self.request.user)


class BoardCategoryView(ListView):
    template_name = 'board/board_list.html'
    model = Board

    def get_queryset(self):
        return get_queryset_category(self, Board, BoardCategory)


class BoardDetail(DetailView):
    model = Board


class BoardSearch(ListView):
    model = Board

    def get_queryset(self):
        query = self.request.GET.get('q')
        qset = (Q(title__icontains=query) | Q(description__icontains=query))
        return Board.objects.filter(qset)


class BoardAdd(CreateView):
    form_class = BoardForm
    template_name = "board/form_add.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        return super(BoardAdd, self).form_valid(form)


class BoardEdit(UpdateView):
    model = Board
    form_class = BoardForm
    template_name = "board/form_edit.html"
