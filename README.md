# Proyecto 1 “Clasificador de colores LEGO”
Descripción: Este proyecto consiste en la implementación de una maqueta robótica enfocada en la Mineria 4.0. Representa específicamente la etapa de procesamiento de minerales dentro de un ciclo de extracción subterránea.

 El sistema simula una planta de clasificación automatizada donde el "material crudo" (bloques LEGO) es identificado y separado según su tipo (color). Su objetivo principal es demostrar como se pueden alejar a los trabajadores de las zonas de riesgo mediante la teleoperación, permitiendo controlar y supervisar la clasificación de materiales desde una interfaz segura en un computador, manteniendo siempre al humano a cargo de la supervisión.

●	Características:
		Las funcionalidades principales del sistema, integradas con la interfaz de control son:
		
		● Clasificación Automática Continua: Ejecuta el ciclo completo de procesamiento, donde el robot detecta el mineral y decide autónomamente su destino según el color.
		
		● CLasificacion manual asitida: Permite al operador derivar manualmente el material (bloques) hacia los depósitos específicos (Verde, Azul, Rojo, Amarillo) mediante la interfaz de control.
		
		● Control de Mecanismo de Clasificación: Otorga control directo sobre el actuador de clasificación (abrir garra o empujar bloque) para tareas de mantenimiento o desatasco.
		
		● Monitoreo de Sensores: Despliega en pantalla el estado actual del proceso y confirma el tipo de mineral detectado antes de su distribución.
		
●	Instalación:

Pasos para preparar el sistema de control (Cliente) y la planta robótica (Servidor):
1. Despliegue en el Robot:
   
   	● Cargar el firmware de Pybricks en el Hub SPIKE Prime.
   
   	● Asegurar la conexión BLuetooth y verificar la carga de bateria.
3. Despliegue en el Controlador(PC):
   
   ● Instalar Python version 3.8
   
   ● Instalar Pybricksdev version 2.3.0

   ● Descargar el código fuente desde el repositorio:
   	https://github.com/sbmartin05/Proyectos1/blob/main/SpikeColorSorter.py

   
  
●	Uso básico:

 Instrucciones para operar la planta clasificadora desde la interfaz gráfica (GUI):
	
	● Modo de Procesamiento Automático:
		1. Ejecute el script principal.
		2. Presione el botón "Clasificación Automática (continua)"
		3. El sistema procesará el flujo de entrada de minerales continuamente.
		
	● Gestión Manual de Depósitos:
		1. Si requiere mover un bloque a un sector específico, presione el botón del color
		correspondiente (Verde, Azul, Rojo, Amarillo).
		2. El mecanismo orientará el material hacia dicho cuadrante.

	● Operación de Mantenimiento:
		1. Utilice el botón "Abrir garra" para liberar material atascado o recibir carga.
		2. Utilice el botón "Empujar" para forzar el movimiento del bloque hacia el depósito
		final.



●	Capturas

<img width="403" height="468" alt="Captura de pantalla 2025-12-30 091743" src="https://github.com/user-attachments/assets/aec8b8e4-f8f3-40a0-bbb0-44a50ec97fc7" />

