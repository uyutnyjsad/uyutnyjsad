admin / admin123 (суперпользователь)

olga_sadovod / user123

serg_garden / user123

python -m venv .venv

.venv/Scripts/activate

pip install -r requirements.txt

cd garden_decor

python manage.py makemigrations

python manage.py migrate

python manage.py loaddata fixtures.json

python manage.py runserver