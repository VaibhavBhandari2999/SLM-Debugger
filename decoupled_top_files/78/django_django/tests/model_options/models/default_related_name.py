"""
```markdown
This Django application models a book publishing ecosystem. It includes entities such as Authors, Editors, Books, and Stores. The core functionality revolves around representing the relationships between these entities, particularly focusing on how Editors are associated with Authors and how both Editors and Stores can be linked to Books.

#### Classes Defined:
- **Author**: Represents an author with first and last names.
- **Editor**: Represents an editor with a name and a reference to a bestselling author.
- **Book**: Represents a book with a title, multiple authors, and an editor.
- **Store**: An abstract base class for stores, which can be specialized into `BookStore` and `EditorStore`.
  - **BookStore**: A store that sells books.
"""
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)


class Editor(models.Model):
    name = models.CharField(max_length=128)
    bestselling_author = models.ForeignKey(Author, models.CASCADE)


class Book(models.Model):
    title = models.CharField(max_length=128)
    authors = models.ManyToManyField(Author)
    editor = models.ForeignKey(Editor, models.CASCADE, related_name="edited_books")

    class Meta:
        default_related_name = "books"


class Store(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=128)

    class Meta:
        abstract = True
        default_related_name = "%(app_label)s_%(model_name)ss"


class BookStore(Store):
    available_books = models.ManyToManyField(Book)


class EditorStore(Store):
    editor = models.ForeignKey(Editor, models.CASCADE)
    available_books = models.ManyToManyField(Book)

    class Meta:
        default_related_name = "editor_stores"
