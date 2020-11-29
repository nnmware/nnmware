@NNMWARE CMF @ 2012-2020
Django-based Content Management Framework

WARNING! Now we start support to django 2.0  and refactoring engine for work with python 3.6.

contains base for:

[Core]
    Follows
    Actions
    Tags
    Docs
    Images
    User Notices
    User Messages
    Flat Comments
    Thread Comments
    Thread Categories

[Address]
    Country
    Region
    City

[Money]
    Transaction
    Currency
    Exchange Rate

[..other]
    Profiles
    Topics
    Boards
    Articles
    OEmbed Video Parsing and Storage

[Booking]
    Booking application base 

[Market]
    Market application base 

[Dossier]
    Dossier base 

[Realty]
    Realty application base

Required django(current), Pillow, unidecode.
Working with OpenStreetMap and his geotargeting.
Licensed under GPL3 
Great thanks Python, Django, Linux and all OpenSource community.

Authors:
================================
nnmware      <nnmware@gmail.com>
karlos-perez <kralole@gmail.com>


============================================
QUICK START
============================================

Install django-current, unidecode, Pillow and ReportLab(recommended)
For few apps need xlwt and ReportLab

cd /usr/src
git clone https://github.com/nnmware/nnmware.git
cd /usr/src/nnmware
./manage.py makemigrations
./manage.py makemigrations demo
./manage.py migrate
./manage.py createsuperuser
./runserver:8080

locate you browser at http://localhost:8080/admin/ ,
login and enjoy
