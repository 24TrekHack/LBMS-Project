from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Book, Student, IssuedBook
from .serializers import BookSerializer, StudentSerializer, IssuedBookSerializer
from django.utils import timezone
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addbook(request):
    serializer = BookSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Book Added Successfully!! 📚"
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def viewbooks(request):

    books = Book.objects.all()

    serializer = BookSerializer(books, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def searchbook(request):

    title = request.GET.get('title')
    author = request.GET.get('author')

    if title:
        books = Book.objects.filter(title__icontains=title)

    elif author:
        books = Book.objects.filter(authorname__icontains=author)

    else:
        return Response(
            {
                "message": "Enter title or author to search."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = BookSerializer(books, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addstudent(request):

    serializer = StudentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            {
                "message": "Student Added Successfully!! 🙂🙂"
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def viewstudents(request):

    students = Student.objects.all()

    serializer = StudentSerializer(students, many=True)

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issuebook(request):

    iu_number = request.data.get('iu_number')
    book_id = request.data.get('book_id')

    try:
        student = Student.objects.get(iu_number=iu_number)
    except Student.DoesNotExist:
        return Response(
            {"message": "Student Not Found 👨‍🎓❌"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {"message": "Book Not Found 📚❌"},
            status=status.HTTP_404_NOT_FOUND
        )

    if book.pstock <= 0:
        return Response(
            {"message": "Book is Out of Stock 📕❌"},
            status=status.HTTP_400_BAD_REQUEST
        )

    already_issued = IssuedBook.objects.filter(
        student=student,
        book=book,
        is_returned=False
    ).exists()

    if already_issued:
        return Response(
            {"message": "This Book is Already Issued to the Student ⚠️"},
            status=status.HTTP_400_BAD_REQUEST
        )

    IssuedBook.objects.create(
        student=student,
        book=book
    )

    book.pstock -= 1
    book.save()

    return Response(
        {"message": "Book Issued Successfully 📖✅"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def returnbook(request):

    iu_number = request.data.get('iu_number')
    book_id = request.data.get('book_id')

    try:
        student = Student.objects.get(iu_number=iu_number)
    except Student.DoesNotExist:
        return Response(
            {"message": "Student Not Found 👨‍🎓❌"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {"message": "Book Not Found 📚❌"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        issue = IssuedBook.objects.get(
            student=student,
            book=book,
            is_returned=False
        )
    except IssuedBook.DoesNotExist:
        return Response(
            {"message": "No Active Book Issue Found 😕"},
            status=status.HTTP_404_NOT_FOUND
        )

    issue.is_returned = True
    issue.return_date = timezone.now().date()
    issue.save()

    book.pstock += 1
    book.save()

    return Response(
        {"message": "Book Returned Successfully 👍👍"},
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
def trackbooks(request):

    issuedbooks = IssuedBook.objects.all()

    data = []

    for issue in issuedbooks:

        if issue.is_returned:
            status_text = "Returned 👍👍"
        else:
            status_text = "Issued 📖"

        data.append({

            "Student Name": issue.student.name,
            "IU Number": issue.student.iu_number,
            "Book": issue.book.title,
            "Author": issue.book.authorname,
            "Issue Date": issue.issue_date,
            "Return Date": issue.return_date,
            "Status": status_text

        })

    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"message": "Username or Password Missing ❌"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"message": "Invalid Username or Password ❌"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login Successful 🔐",
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    })

