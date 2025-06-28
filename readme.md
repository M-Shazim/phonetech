# Phonetech

**Phonetech** is a Django-based e-commerce platform for selling mobile phones, cases, and accessories. It features a clean UI, responsive design, functional cart and checkout system, and informative policy pages. The project is production-ready and easy to extend or deploy.

---

## Project Overview

- Modern Bootstrap-based interface
- Add-to-cart and order flow
- Admin panel for product management
- Customer-friendly pages: About, Contact, Delivery, Refund, Warranty, Cancellation
- SEO-friendly structure and ready for payment integration

---

## Folder Structure

- ├── main/ # Homepage, contact, main functionalities
- ├── templates/ # All frontend HTML templates
- ├── staticfiles/ # Static assets (CSS, JS, images)
- ├── db.sqlite3 # Development database
- ├── manage.py # Django management script


---

## ⚙️ How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/M-Shazim/phonetech.git
cd phonetech

# 2. Create and activate a virtual environment
python -m venv env
source env/bin/activate     # On Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
