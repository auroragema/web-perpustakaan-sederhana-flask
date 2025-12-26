import csv
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Reading the CSV file and converting it into a list of dictionaries
def load_books_from_csv(filepath):
    books = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            books.append(row)
    return books

# Load books from CSV
all_books = load_books_from_csv('C:/app/Books.csv')


# Data Dummy
recommended_books = [
    {"title": "The Lord of the Rings, the Return of the King", "rating": 4.59},
    {"title": "Harry Potter and the Order of the Phoenix", "rating": 4.49},
    {"title": "Redemption", "rating": 4.8},
    {"title": "The Godfather", "rating": 4.37},
    {"title": "Stephen Hawking's Universe", "rating": 4.28}
]

# Home route with search functionality
@app.route('/', methods=['GET'])
def home():
    # Load all books
    all_books = load_books_from_csv('C:/app/Books.csv')
    
    # Get search query from request
    search_query = request.args.get('query', '').lower()

    # Filter books based on search query
    if search_query:
        recommended_books = [
            book for book in all_books if search_query in book['title'].lower()
        ]
    else:
        recommended_books = all_books[:5]

    return render_template('home.html', recommended_books=recommended_books)


@app.route('/books', methods=['GET', 'POST'])
def books():
    search_query = request.args.get('q', '').lower()
    print(f"Search Query: {search_query}")
    filtered_books = [
        book for book in all_books if search_query in book['title'].lower()
    ] if search_query else all_books

    print(f"Filtered Books: {filtered_books}")
    return render_template(
        'books.html', 
        all_books=filtered_books, 
        query=search_query
    )

@app.route('/search', methods=['GET'])
def search_books():
    search_query = request.args.get('query', '').lower()  # Get the search query from the URL
    all_books = load_books_from_csv('C:/app/Books.csv')  # Load books from CSV

    # Ensure search query is not empty
    if search_query:
        filtered_books = [
            book for book in all_books if search_query in book['title'].lower()
        ]
    else:
        filtered_books = all_books  # Show all books if no search query is entered

    # Pass filtered_books to the template
    return render_template('search.html', books=filtered_books)

@app.route('/detail/<book_title>')
def detail(book_title):
    # Cari buku berdasarkan judul
    book = next((book for book in all_books if book['title'].lower() == book_title.lower()), None)

    if not book:
        # Jika buku tidak ditemukan, tampilkan halaman error
        return render_template('404.html', message="Buku tidak ditemukan.")

    # Render halaman detail buku dengan data dari CSV
    return render_template('detail.html', book=book)

@app.route('/peminjaman', methods=['GET', 'POST'])
def peminjaman():
    books = load_books_from_csv('C:/app/Books.csv')
    
    # Dapatkan tanggal hari ini dalam format YYYY-MM-DD
    today_date = datetime.today().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        user_name = request.form.get('name', '').strip()
        borrow_date = request.form.get('borrow_date', '').strip()
        jumlah_buku = int(request.form.get('jumlah_buku', 0))
        book_titles = []
        
        # Mengumpulkan nama buku yang dipilih
        for i in range(jumlah_buku):
            book_titles.append(request.form.get(f'book_title_{i}', '').strip())
        
        # Validasi: semua input harus diisi
        if not user_name or not borrow_date or any(not title for title in book_titles):
            error_message = "Semua field harus diisi!"
            return render_template('peminjaman.html', error_message=error_message, books=books, today_date=today_date)
        
        # Hitung tanggal pengembalian: 14 hari setelah tanggal peminjaman
        borrow_date_obj = datetime.strptime(borrow_date, '%Y-%m-%d')
        return_date_obj = borrow_date_obj + timedelta(days=14)
        return_date = return_date_obj.strftime('%Y-%m-%d')

        return render_template('peminjaman_success.html', user_name=user_name, book_titles=book_titles, borrow_date=borrow_date, return_date=return_date)
    
    return render_template('peminjaman.html', books=books, today_date=today_date)


@app.route('/submit_peminjaman', methods=['POST'])
def submit_peminjaman():
    borrower_name = request.form['borrowerName']
    book_titles = [request.form[f'bookTitle{i+1}'] for i in range(int(request.form['bookCount']))]
    borrow_date = request.form['borrowDate']
    
    # Process the form data (e.g., store in a database or perform further logic)
    return f"Borrowing request submitted for {', '.join(book_titles)} by {borrower_name} on {borrow_date}."

if __name__ == '__main__':
    app.run(debug=True)
