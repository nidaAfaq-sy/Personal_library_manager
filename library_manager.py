import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Initialize session state for our library data
if 'library' not in st.session_state:
    st.session_state.library = []

def save_library():
    """Save library data to a JSON file"""
    with open('library_data.json', 'w') as f:
        json.dump(st.session_state.library, f)

def load_library():
    """Load library data from JSON file"""
    if os.path.exists('library_data.json'):
        with open('library_data.json', 'r') as f:
            st.session_state.library = json.load(f)

# Load existing data when app starts
load_library()

# Set up the main page
st.title("📚 Personal Library Manager")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose an action",
    ["View Library", "Add Book", "Search Books", "Manage Books"]
)

# Add Book Page
if page == "Add Book":
    st.header("Add New Book")
    
    with st.form("add_book_form"):
        title = st.text_input("Book Title*")
        author = st.text_input("Author*")
        
        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox(
                "Genre",
                ["Fiction", "Non-Fiction", "Science Fiction", "Mystery", 
                 "Fantasy", "Biography", "History", "Other"]
            )
            status = st.selectbox(
                "Reading Status",
                ["Unread", "Reading", "Completed", "On Hold"]
            )
            
        with col2:
            rating = st.slider("Rating", 0, 5, 0)
            date_added = st.date_input("Date Added", datetime.now())
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Book")
        
        if submitted:
            if title and author:  # Required fields
                new_book = {
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "status": status,
                    "rating": rating,
                    "date_added": str(date_added),
                    "notes": notes
                }
                st.session_state.library.append(new_book)
                save_library()
                st.success("Book added successfully!")
            else:
                st.error("Title and Author are required fields!")

# View Library Page
elif page == "View Library":
    st.header("My Library")
    
    if not st.session_state.library:
        st.info("Your library is empty. Add some books!")
    else:
        # Convert library data to DataFrame
        df = pd.DataFrame(st.session_state.library)
        
        # Filtering options
        col1, col2, col3 = st.columns(3)
        with col1:
            genre_filter = st.multiselect(
                "Filter by Genre",
                options=sorted(df['genre'].unique())
            )
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(df['status'].unique())
            )
        with col3:
            rating_filter = st.slider(
                "Minimum Rating",
                0, 5, 0
            )
        
        # Apply filters
        filtered_df = df
        if genre_filter:
            filtered_df = filtered_df[filtered_df['genre'].isin(genre_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if rating_filter > 0:
            filtered_df = filtered_df[filtered_df['rating'] >= rating_filter]
        
        # Display statistics
        st.subheader("Library Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Books", len(df))
        with col2:
            st.metric("Books Read", len(df[df['status'] == 'Completed']))
        with col3:
            st.metric("Average Rating", f"{df['rating'].mean():.1f}")
        with col4:
            st.metric("Currently Reading", len(df[df['status'] == 'Reading']))
        
        # Display books
        st.subheader("Book List")
        st.dataframe(
            filtered_df[['title', 'author', 'genre', 'status', 'rating']],
            hide_index=True
        )

# Search Books Page
elif page == "Search Books":
    st.header("Search Books")
    
    search_term = st.text_input("Enter search term")
    search_by = st.radio(
        "Search by",
        ["Title", "Author", "Notes"]
    )
    
    if search_term:
        results = []
        search_term = search_term.lower()
        
        for book in st.session_state.library:
            if search_by == "Title" and search_term in book['title'].lower():
                results.append(book)
            elif search_by == "Author" and search_term in book['author'].lower():
                results.append(book)
            elif search_by == "Notes" and book['notes'] and search_term in book['notes'].lower():
                results.append(book)
        
        if results:
            st.write(f"Found {len(results)} results:")
            st.dataframe(pd.DataFrame(results), hide_index=True)
        else:
            st.info("No books found matching your search.")

# Manage Books Page
elif page == "Manage Books":
    st.header("Manage Books")
    
    if not st.session_state.library:
        st.info("No books to manage. Add some books first!")
    else:
        book_to_edit = st.selectbox(
            "Select book to edit or delete",
            options=[book['title'] for book in st.session_state.library]
        )
        
        if book_to_edit:
            book_index = next(
                (index for (index, book) in enumerate(st.session_state.library)
                 if book['title'] == book_to_edit)
            )
            book = st.session_state.library[book_index]
            
            with st.form("edit_book_form"):
                st.subheader("Edit Book Details")
                
                new_title = st.text_input("Title", book['title'])
                new_author = st.text_input("Author", book['author'])
                new_genre = st.selectbox(
                    "Genre",
                    ["Fiction", "Non-Fiction", "Science Fiction", "Mystery",
                     "Fantasy", "Biography", "History", "Other"],
                    index=["Fiction", "Non-Fiction", "Science Fiction", "Mystery",
                          "Fantasy", "Biography", "History", "Other"].index(book['genre'])
                )
                new_status = st.selectbox(
                    "Reading Status",
                    ["Unread", "Reading", "Completed", "On Hold"],
                    index=["Unread", "Reading", "Completed", "On Hold"].index(book['status'])
                )
                new_rating = st.slider("Rating", 0, 5, book['rating'])
                new_notes = st.text_area("Notes", book['notes'])
                
                col1, col2 = st.columns(2)
                with col1:
                    update = st.form_submit_button("Update Book")
                with col2:
                    delete = st.form_submit_button("Delete Book")
                
                if update:
                    st.session_state.library[book_index] = {
                        "title": new_title,
                        "author": new_author,
                        "genre": new_genre,
                        "status": new_status,
                        "rating": new_rating,
                        "date_added": book['date_added'],
                        "notes": new_notes
                    }
                    save_library()
                    st.success("Book updated successfully!")
                    st.rerun()
                
                if delete:
                    st.session_state.library.pop(book_index)
                    save_library()
                    st.success("Book deleted successfully!")
                    st.rerun()

# Add footer
st.markdown("---")
st.markdown("*Personal Library Manager - Keep track of your reading journey*") 
