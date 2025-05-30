# Nobrac Backend

This is the backend service for the Nobrac application, built with Django and Django REST Framework.

## Features

- Farmer management system
- CO2 emissions calculation
- Media file handling
- Data synchronization
- RESTful API endpoints

## Setup

1. Clone the repository:
```bash
git clone https://github.com/udayjaggumanthri/nobrac_backend.git
cd nobrac_backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `/api/farmers/` - List and create farmers
- `/api/farmers/<id>/` - Retrieve, update, and delete specific farmer
- `/api/farmers/<id>/emissions/` - Get CO2 emissions data for a farmer
- `/api/farmers/media/upload/` - Upload media files for farmers
- `/api/farmers/sync/` - Synchronize farmer data

## CO2 Emissions Calculation

The system calculates CO2 emissions for:
- Fertilizer usage
- Pesticide application
- Energy consumption
- Irrigation systems

Each calculation uses specific conversion factors based on the type of input and activity.

## License

This project is licensed under the MIT License. 