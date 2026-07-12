from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    authorname = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)

    tstock = models.PositiveIntegerField()
    pstock = models.PositiveIntegerField()

    def __str__(self):
        return self.title



class Student(models.Model):
    name = models.CharField(max_length=100)
    iu_number = models.IntegerField(unique=True)
    branch = models.CharField(max_length=20)
    section = models.CharField(max_length=5)

    def __str__(self):
        return self.name
    

class IssuedBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.book.title}"
    

