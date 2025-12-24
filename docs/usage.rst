Usage Guide
===========

Installation
------------

.. code-block:: bash

   pip install tornet==2.0.1

Basic Usage
-----------

Display current IP:

.. code-block:: bash

   tornet --ip

Change IP once:

.. code-block:: bash

   tornet --change

Change IP every 60 seconds:

.. code-block:: bash

   tornet --interval 60 --count 10

Country Selection
-----------------

.. code-block:: bash

   tornet --country us --interval 60
   tornet --country de --interval 120
   tornet --country auto --interval 60
