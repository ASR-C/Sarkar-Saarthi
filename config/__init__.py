# Django project initialization

# Python 3.14 compatibility patch for django.template.context.BaseContext.__copy__
try:
    from django.template.context import BaseContext

    def _py314_base_context_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _py314_base_context_copy
except ImportError:
    pass
