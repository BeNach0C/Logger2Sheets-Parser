Logger2Sheets Parser
====================
Español:
Este parser toma el output de Logger y lo organiza en un archivo de celdas.
El output son varios archivos cada uno para las siguientes acciones:
Bloques puestos y rotos, Cofres y mesas, Fluidos y Letreros.
Lo demás no creí que fuera necesario organizar, ya que es simple de leer en el log.
Cada archivo posee una página por jugador, la cuál va organizada por fecha y hora.

Uso:
El archivo log_analizer.exe (o en su defecto el .py) debe ir en la ruta de logs del plugin.
Ejemplo: SERVER/Plugins/Logger/Logs/log_analizer.exe
Después de abrirlo el archivo creará la carpeta "Filtered Sheet", con los archivos solicitados.

English: 
This parser organizes the Logger output into a sheet file.
The output consists of several files, each for the following actions:
Blocks placed and broken, Chests & tables, Fluids, and Signs.
I didn't think the rest needed organizing, as it's easy to read in the logs.
Each file has one page per player, organized by date and time.

USAGE:
The log_analizer.exe file (or the .py file) must be placed in the plugin's log directory.
Example: SERVER/Plugins/Logger/Logs/log_analizer.exe
After opening it, the file will create the "Filtered Sheet" folder, containing the requested files.


Logger Plugin:
https://github.com/ExceptedPrism3/Logger
