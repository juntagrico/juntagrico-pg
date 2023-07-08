Installation
============

Basic Installation
------------------
Install juntagrico-pg with :command:`pip`::

    $ pip install juntagrico-pg

Django Settings
---------------
You have to add the app to your installed apps in your Django settings

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'juntagrico',
        'juntagrico_pg',
    ]
    
URLs
----

Add this line in your `urls.py`:

.. code-block:: python
    path('', include('juntagrico_pg.urls'))
