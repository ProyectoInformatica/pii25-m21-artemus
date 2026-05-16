# Especificación Técnica de la Arquitectura de ArtemusPark

Este documento detalla la organización interna y el funcionamiento técnico del software ArtemusPark, describiendo la interacción entre sus componentes sin el uso de representaciones gráficas.

## Descripción del Diseño de Software

El sistema ArtemusPark está fundamentado en una arquitectura de capas con separación estricta de responsabilidades. El diseño permite que la lógica de simulación de sensores, el procesamiento de datos y la interfaz de usuario operen de forma independiente pero coordinada.

### Componente de Interfaz de Usuario
La capa de presentación es la responsable de la interacción con el operador. Está construida sobre el framework Flet, que gestiona el renderizado de la interfaz. Esta capa se organiza mediante páginas que contienen componentes modulares. La comunicación hacia el usuario es reactiva; el sistema utiliza un mecanismo de paso de mensajes asíncronos para actualizar los elementos visuales en tiempo real cuando se detectan cambios en los sensores simulados.

### Componente de Lógica de Servicios
Los servicios constituyen el nivel de procesamiento intermedio. Su función principal es la orquestación de datos y la aplicación de reglas de negocio. Esta capa solicita información a los repositorios de datos y la transforma en estructuras comprensibles para la interfaz. Además, es aquí donde se realizan los cálculos de métricas y la evaluación de riesgos (como alertas de incendio o viento excesivo), actuando como un filtro entre los datos crudos y la información estratégica.

### Componente de Acceso a Datos (Repositorios)
La persistencia de la información se gestiona a través de una capa de abstracción denominada Repositorios. Cada tipo de dato del parque tiene un repositorio asignado que encapsula las sentencias SQL necesarias para interactuar con la base de datos MySQL. Este diseño garantiza que las capas superiores no tengan conocimiento de la estructura de las tablas ni de la tecnología de base de datos específica, facilitando el mantenimiento y la escalabilidad del sistema.

### Componente de Modelado de Entidades
Los modelos son estructuras de datos puras que definen los objetos del sistema, como Sensores, Usuarios o Puertas. Su única función es servir de vehículo para la información entre las diferentes capas, asegurando que todos los componentes del software hablen el mismo idioma técnico y manejen los mismos atributos de datos.

### Componente de Simulación y Control
El sistema integra una capa de controladores que actúan como emuladores de dispositivos de hardware. Estos controladores ejecutan bucles de simulación que generan lecturas dinámicas de temperatura, humedad y otros parámetros. Los controladores coordinan con los repositorios para registrar estas lecturas en la base de datos, imitando el comportamiento de un entorno de sensores reales en un parque físico.

### Infraestructura de Soporte
La base tecnológica se completa con un módulo de gestión de base de datos que administra la conectividad mediante un pool de conexiones optimizado, y un conjunto de módulos de configuración que centralizan los parámetros operativos del parque, como horarios, límites de seguridad y constantes del entorno.
