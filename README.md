# Pet Daycare Management System

A Django-based pet daycare management system that helps businesses manage pets, tutors, staff, reservations, and communication.

## Features

### Staff Dashboard
- Multi-business support with session-based authentication
- Pet management with photos and detailed profiles
- Check-in/check-out tracking
- Service booking management (pending/confirmed/cancelled)
- Private and public messaging system (Woofs)
- Training progress tracking
- Monthly calendar views for each pet

### Tutor Dashboard
- Phone-based authentication
- View pet status and updates
- Service booking requests
- Photo and video feed from daycare
- Pet profile management
- Reply to staff messages
- Training progress view

### Pet Profiles
- Photo uploads with placeholder support
- Detailed metadata (birthday, species, breed, sex, neutered status)
- Chip number tracking
- Allergies and special requirements
- Address and contact information
- Training progress entries
- Notes section

### Tutor Profiles
- Contact information management (email, phone, address)
- Emergency contact notes
- Multiple pets per tutor support

## Tech Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS (custom styling)
- **Media**: File uploads for photos/videos

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd pet_app
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install django pillow
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Staff login: http://localhost:8000/staff/login/
- Tutor dashboard: http://localhost:8000/tutor/
- Admin panel: http://localhost:8000/admin/

## Project Structure

```
pet_app/
├── manage.py
├── db.sqlite3
├── petcrm/              # Main project settings
├── pets/                # Pet and business models
├── staff/               # Staff dashboard and views
├── tutor/               # Tutor dashboard and views
├── reservations/        # Booking and scheduling
└── media/               # Uploaded files (photos/videos)
```

## Usage

### Staff Login
1. Navigate to `/staff/login/`
2. Enter your business name (e.g., "Tails Daycare")
3. Access your business dashboard

### Tutor Login
1. Navigate to `/tutor/`
2. Enter your registered phone number
3. View your pets and daycare updates

## Models

- **Business**: Daycare business information
- **Tutor**: Pet owner/guardian profiles
- **Pet**: Pet profiles with metadata
- **CheckIn**: Daily attendance tracking
- **ServiceBooking**: Appointment and service reservations
- **Woof**: Messaging system (staff ↔ tutors)
- **GlobalWoof**: Business-wide announcements
- **TrainingProgress**: Pet training milestone tracking

## Development

- Run checks: `python manage.py check`
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`

## Future Enhancements

- Vaccines and health bulletin tracking
- Advanced reporting and analytics
- Email/SMS notifications
- Payment processing integration
- Mobile app

## License

MIT License
