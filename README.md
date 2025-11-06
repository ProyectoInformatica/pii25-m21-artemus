## equipos-y-proyectos-pii25-m21-artemus

# 🌱 Artemus – Ciudad Inteligente: Módulo de Parque Central

Proyecto de Ingeniería Informática – Universidad Europea de Madrid  
Desarrollo de un sistema IoT para la gestión inteligente y sostenible de parques urbanos.

---

## 🧭 Descripción del proyecto

**Artemus** es un sistema IoT que permite monitorizar y gestionar las condiciones ambientales de un parque urbano de 3.6 hm².  
El sistema integra sensores y actuadores para optimizar **riego**, **iluminación**, **seguridad** y **educación ambiental** en tiempo real.

### 🧠 Tecnologías principales
- **Python 3** – Lógica del sistema  
- **Flet** – Interfaz gráfica  
- **Arduino / Raspberry Pi** – Hardware IoT  
- **JSON** – Gestión de datos  
- **Scrum + Trello** – Planificación y seguimiento ágil del proyecto

---

## 📁 Estructura general
```

/src                → Código fuente principal
/assets             → Recursos visuales (iconos, imágenes, logos)
/docs               → Documentación técnica
/tests              → Scripts de prueba
.gitignore
README.md

````

---

## ⚙️ Instalación

```bash
# Clonar el repositorio
git clone https://github.com/[usuario]/artemus.git
cd artemus

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
````

---

## 🧩 Reglas de trabajo con Git

### 🔀 Formato para crear ramas

Cada nueva rama debe seguir este formato:

```
feature/issueX_Y_[usuario]_[descripcion_breve]
```

**Ejemplos:**

```
feature/issue3_Y_Israel_sensor_humedad
feature/issue7_Y_Pablo_UI_riego
```

📘 Donde:

* `issueX_Y` → número y subnúmero de la historia de usuario o tarea en Trello
* `[usuario]` → nombre o alias del miembro que crea la rama
* `[descripcion_breve]` → resumen corto de la tarea o funcionalidad

---

### 🔁 Formato para Pull Requests (PR)

El **nombre del PR debe coincidir con el nombre exacto de la tarea en Trello**.

**Ejemplo:**

```
HU3 - 3: Establecer políticas de commits y revisiones
```

**Buenas prácticas:**

* Añadir descripción breve del cambio realizado
* Indicar si requiere revisión de hardware o pruebas de integración
* Solicitar revisión al *Scrum Master* antes de fusionar

---

## 👥 Equipo

| Rol                       | Nombre             | Funciones principales                            |
| ------------------------- | ------------------ | ------------------------------------------------ |
| 🧭 Scrum Master           | **Pablo Piqueras** | Coordinación general, integración de sensores    |
| 🧩 Product Owner          | **Israel Gómez**   | Definición de requisitos, desarrollo de software |
| 🔧 Desarrollador Hardware | **Aldo Zamora**    | Sensores, actuadores y calibración IoT           |
| 🧪 QA / Documentación     | **Xiaojie Hu**     | Pruebas, validación y documentación              |

---

## 📋 Metodología

* **Metodología:** Ágil (Scrum)
* **Duración de los sprints:** 2 semanas
* **Herramientas de gestión:** Trello + GitHub
* **Revisión de sprint:** viernes de la segunda semana

---

## 🧱 Licencia

Proyecto académico desarrollado en el marco del **Grado en Ingeniería Informática (UEM)**.
El código puede reutilizarse citando la fuente y manteniendo la licencia original.

---

## 📫 Contacto

* 📧 **Equipo Artemus:** [Israel Gómez](mailto:22484886@live.uem.es), [Pablo Piqueras](mailto:22470465@live.uem.es), [Xiaojie Hu](mailto:224D3854@live.uem.es), [Aldo Zamora](mailto:22431451@live.uem.es) y [Alfonso Vilchez de las Heras](mailto:20014029@live.uem.es) 
* 🏫 **Universidad Europea de Madrid**
* 🌐 **Proyecto:** *Smart Cities – Módulo de Parque Central*
