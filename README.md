[![Build Status](https://runbot.odoo.com/runbot/badge/flat/1/master.svg)](https://runbot.odoo.com/runbot)
[![Tech Doc](https://img.shields.io/badge/master-docs-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/documentation/16.0)
[![Help](https://img.shields.io/badge/master-help-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/forum/help-1)
[![Nightly Builds](https://img.shields.io/badge/master-nightly-875A7B.svg?style=flat&colorA=8F8F8F)](https://nightly.odoo.com/)

Odoo
----

gOdoo es un fork del ERP basado en web y de código abierto <a href="https://www.odoo.com/">Odoo</a>, ajustada para su uso en gobiernos locales.

Este fork mantenido por la <a href="https://www.renca.cl/">Municipalidad de Renca</a> utiliza la edición community y es distribuído para la licencia GPL-XXX.

¿Cómo probar?
-------------

Requerimientos:
- Python 3.7 o superior
- PostgreSQL 12 o superior
- Git

Lo siguiente requiere que tengas Git instalado en tu máquina local y que tengas nociones básicas de los comandos de Git.

Primero clonamos localmente el repositorio de github
```sh
git clone https://github.com/mrenca/odoo.git
```

Luego instalamos las dependencias del proyecto
```sh
cd odoo
pip3 install setuptools wheel
pip3 install -r requirements.txt
```

Entramos a la consola de postgresql para crear el usuario, la base de datos y entregamos los accesos
```sh
psql postgres
```
```sql
CREATE DATABASE odoo;
CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo';
GRANT ALL PRIVILEGES ON DATABASE odoo TO odoo;
```

Finalmente, ejecutamos odoo indicando el nombre de la base de datos en el parámetro `-d odoo`. Si es la primera vez, debemos incorporar el parámetro `-i base` que inicializa el esquema de datos.
```sh
python3 odoo-bin --addons-path=addons -d odoo -i base
```

¿Cómo continuar?
-----------------

Para una instalación estandar favor referirse a la documentación oficial de odoo, en la sección <a href="https://www.odoo.com/documentation/16.0/es/administration/install/install.html#setup-install-source">source install</a>. IMPORTANTE: Verificar que al hacer el git clone lo efectúes del presente fork.

Para conocer el más detalles sobre el software puedes referirte a <a href="https://www.odoo.com/slides">Odoo eLearning</a>. Si eres desarrollador puedes empezar por el <a href="https://www.odoo.com/documentation/16.0/developer/howtos.html">tutorial para desarrollador</a>.
