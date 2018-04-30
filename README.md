How to install and run (windows):

1. Download repository

2. Unzip node_modules.zip to the project's top level directory

3. Download and install redis from here:
https://github.com/rgl/redis/downloads

4. Type services into windows search bar and open

5. Scroll down to find Redis Server and press start service

6. Via pip install the following modules:
asgiref (2.2.0)
channels (2.0.0)
channels-redis (2.1.1)
daphne (2.1.0)
Django (2.0.3)
django-channels (0.7.0)
django-webpack-loader (0.6.0)
djangorestframework (3.7.7)
Twisted (17.9.0)

7. In the terminal in the current directory enter the following command:
node_modules\.bin\webpack --config webpack.config.js

8. In the terminal in the current directory enter the following command:
python manage.py runserver 8080

9. The game should now be live at 127.0.0.1:8080
