# Library Management Module for Odoo 19

A comprehensive library management system built for Odoo 19 that helps manage books, members, and borrowing operations.

## Features

### Book Management
- Complete book catalog with ISBN, author, publisher, and publication details
- Book categorization (Fiction, Non-Fiction, Science, Technology, History, Biography, Children, Other)
- Cover image support
- Inventory tracking (total copies, available copies, borrowed copies)
- Automatic availability status computation
- Book borrowing history

### Member Management
- Member registration with complete contact information
- Multiple membership types:
  - **Basic**: 1 year duration
  - **Premium**: 2 years duration
  - **Student**: 6 months duration
  - **Senior**: 3 years duration
- Automatic membership expiry calculation
- Member status tracking (Active, Expired, Suspended)
- Borrowing statistics per member
- Overdue book tracking

### Borrowing Operations
- Book borrowing and return workflow
- Automatic due date calculation (14 days from borrow date)
- Overdue detection and tracking
- Fine calculation ($1 per day overdue)
- Fine payment tracking
- Borrowing duration tracking
- Status tracking (Draft, Borrowed, Returned, Cancelled)

### Security
- Three access levels:
  - **User**: Read-only access to books and members
  - **Librarian**: Can manage books and borrowings, create members
  - **Manager**: Full access including delete permissions

### Additional Features
- Mail integration for activity tracking and messaging
- Chatter support on all major forms
- Smart buttons for quick navigation
- Kanban, Tree, and Form views for all models
- Advanced search and filtering options
- Group by capabilities
- Demo data for testing

## Module Structure

```
library_management/
├── models/
│   ├── __init__.py
│   ├── library_book.py          # Book model
│   ├── library_member.py        # Member model
│   └── library_borrowing.py     # Borrowing model
├── views/
│   ├── library_book_views.xml
│   ├── library_member_views.xml
│   ├── library_borrowing_views.xml
│   └── library_menus.xml
├── security/
│   ├── library_security.xml     # Security groups and rules
│   └── ir.model.access.csv      # Access rights
├── data/
│   ├── library_data.xml         # Sequences and master data
│   └── library_demo.xml         # Demo data
├── __init__.py
├── __manifest__.py
└── README.md
```

## Installation

1. Copy the `library_management` folder to your Odoo addons directory
2. Update the apps list in Odoo (Settings > Apps > Update Apps List)
3. Search for "Library Management" in the Apps menu
4. Click Install

## Configuration

### Setting up Security Groups

After installation, assign users to appropriate groups:

1. Go to Settings > Users & Companies > Users
2. Select a user
3. Navigate to the "Access Rights" tab
4. Under "Library Management", assign one of the following roles:
   - User (read-only access)
   - Librarian (operational access)
   - Manager (full access)

### Loading Demo Data

Demo data is automatically loaded if you install the module with demo data enabled. It includes:
- 6 sample books across different categories
- 4 sample members with different membership types
- 4 borrowing records in various states

## Usage

### Adding a Book

1. Navigate to Library > Catalog > Books
2. Click "Create"
3. Fill in the book details:
   - Title (required)
   - Author (required)
   - ISBN
   - Publisher, Publication Date
   - Category, Pages
   - Total Copies (required)
4. Optionally add a cover image and description
5. Click "Save"

### Registering a Member

1. Navigate to Library > Catalog > Members
2. Click "Create"
3. Fill in member details:
   - Name (required)
   - Email (required)
   - Phone
   - Membership Type
   - Address information
4. Click "Save"
5. Member ID is automatically generated

### Processing a Borrowing

1. Navigate to Library > Operations > Borrowings
2. Click "Create"
3. Select the book and member
4. Borrow date defaults to today
5. Due date is automatically set to 14 days from borrow date
6. Click "Confirm Borrowing"
7. When the book is returned, open the record and click "Return Book"

### Handling Overdue Books

- Overdue books are highlighted in red in the borrowing list
- Fines are automatically calculated at $1 per day
- When a book is returned with a fine, click "Pay Fine" to mark it as paid

## Technical Details

### Dependencies
- `base`: Odoo base module
- `mail`: For chatter and activity tracking

### Models

#### library.book
- Inherits: `mail.thread`, `mail.activity.mixin`
- Key Fields: name, isbn, author, publisher, category, total_copies, available_copies
- Computed Fields: available_copies, borrowed_copies, state
- Constraints: ISBN uniqueness, positive values for copies and pages

#### library.member
- Inherits: `mail.thread`, `mail.activity.mixin`
- Key Fields: name, email, member_id, membership_type, membership_date, expiry_date
- Computed Fields: expiry_date, borrowed_books_count, total_borrowed_count, overdue_count, state
- Constraints: Email uniqueness and format validation

#### library.borrowing
- Inherits: `mail.thread`, `mail.activity.mixin`
- Key Fields: name, book_id, member_id, borrow_date, due_date, return_date, state
- Computed Fields: duration, is_overdue, days_overdue, fine_amount
- Constraints: Date validation, member status check, book availability check

### Workflows

#### Book Availability
1. When a borrowing is confirmed → book's borrowed_copies increases
2. When a book is returned → book's borrowed_copies decreases
3. available_copies = total_copies - borrowed_copies
4. state = 'borrowed' if available_copies <= 0 else 'available'

#### Member Status
1. Active: membership not expired and not suspended
2. Expired: membership expiry date has passed
3. Suspended: manually set to inactive

#### Fine Calculation
- Fine = days_overdue × $1
- days_overdue calculated from due_date to return_date (or today if still borrowed)

## Support

For issues, questions, or contributions, please contact your system administrator.

## License

LGPL-3

## Author

Your Company

## Version

19.0.1.0.0
