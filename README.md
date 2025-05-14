# Trading Bot Algorítmico - Proyecto de Portafolio

## Introducción

Este proyecto implementa un bot de trading algorítmico en Python diseñado para competiciones de portafolios financieros. El trading algorítmico utiliza programas informáticos para ejecutar operaciones de compra y venta de activos financieros siguiendo reglas predefinidas basadas en análisis técnico, fundamental o cuantitativo.

La automatización del trading ofrece ventajas significativas:
- **Eliminación del factor emocional**: Las decisiones se basan estrictamente en los parámetros programados
- **Velocidad de ejecución**: Capacidad para procesar datos y ejecutar órdenes en milisegundos
- **Backtesting**: Posibilidad de probar estrategias en datos históricos antes de usarlas con dinero real
- **Operativa 24/7**: El bot puede monitorear mercados y operar sin interrupciones

El objetivo principal de este proyecto es crear estrategias que maximicen el rendimiento financiero mientras mantienen un control adecuado de riesgos, aplicando principios sólidos de gestión monetaria y análisis sistemático.

## Métricas de Evaluación de Portafolio

Un portafolio de alto rendimiento en competiciones de trading no se evalúa únicamente por sus ganancias, sino por el equilibrio entre rentabilidad y riesgo. A continuación se detallan las métricas más relevantes:

### Métricas Principales

| Métrica | Definición | Relevancia en competición |
|---------|------------|---------------------------|
| **ROI (Rentabilidad)** | % de ganancia/pérdida sobre el capital inicial | Métrica principal: indica cuánto ganó el portafolio (ej. 15% significa un 15% de ganancia sobre lo invertido) |
| **Factor de ganancia** | Ganancia bruta / Pérdida bruta | Eficiencia global: >1 es rentable, >2 excelente. Por ejemplo, factor 1.5 significa que por cada $1 perdido, se ganan $1.5 |
| **Win Rate** | % de operaciones ganadoras | Consistencia de aciertos (ej. 60% significa que 6 de cada 10 trades fueron positivos) |
| **Drawdown máximo** | Caída porcentual máxima desde un pico | Mide riesgo: menor drawdown indica más estabilidad. Ejemplo: Si comienzas con $1000, subes a $1200, luego caes a $900, el drawdown es -25% |
| **Ratio Sharpe** | Retorno excedente dividido por volatilidad | Rendimiento ajustado al riesgo; >1 positivo, >2 excelente |

### Métricas Adicionales

- **Ganancia Neta Absoluta**: Total ganado descontando costos (comisiones, etc.)
- **Relación Riesgo-Recompensa**: Magnitud promedio de ganancias vs pérdidas por operación. Por ejemplo, si tu estrategia solo acierta 20% de las veces, necesitas que la ganancia de cada trade ganador sea ~5 veces la pérdida de un trade perdedor para ser rentable.
- **Consistencia**: Curva de capital (equity curve) estable y ascendente, con ganancias logradas de forma constante sin depender de un solo trade afortunado.
- **Riesgo de Ruina**: Probabilidad de perder todo el capital, vinculada a la gestión de riesgo mediante tamaños de posición adecuados y uso de stop-loss.

En la práctica, el ranking en competiciones suele ordenarse por ganancia final (ROI), pero si dos equipos logran ganancias similares, métricas como drawdown o Sharpe podrían decantar al ganador. Una estrategia ganadora será la que haga crecer el capital de forma sostenible y segura durante el periodo de la competencia.

## Estructura del Proyecto

La organización de archivos y carpetas sigue las mejores prácticas de desarrollo de software, facilitando la modularidad, el mantenimiento y la colaboración:

```
pyproject.toml            # Dependencias del proyecto
|
README.md                 # Este archivo de documentación
|
src/
│
├── data/                     # Datos financieros
│   ├── raw/                  # Datos sin procesar
│   └── processed/            # Datos preprocesados
│
├── strategies/               # Módulos de estrategias de trading
│   ├── __init__.py
│   ├── mean_reversion.py     # Estrategia de reversión a la media
│   └── trend_following.py    # Estrategia de seguimiento de tendencia
│
├── utils/                    # Utilidades comunes
│   ├── __init__.py
│   ├── data_fetcher.py       # Obtención de datos de API
│   └── indicators.py         # Cálculo de indicadores técnicos
│
├── backtesting/              # Scripts para pruebas con datos históricos
│   ├── __init__.py
│   ├── backtest_engine.py    # Motor de backtesting
│   └── performance.py        # Cálculo de métricas de rendimiento
│
└── tests/                    # Tests automatizados
    ├── __init__.py
```

### Detalles de los Componentes

- **config/**: Almacena parámetros de estrategia y credenciales de APIs. Las claves API reales no deben subirse al repositorio por seguridad.
- **data/**: Contiene datos de mercado para backtesting o análisis. Se separan datos crudos de los ya procesados para mantener organización.
- **strategies/**: Contiene la lógica principal de trading. Cada estrategia se encapsula en su propio módulo para facilitar pruebas y reutilización.
- **risk_management/**: Define reglas para dimensionar posiciones y limitar pérdidas, un componente crítico para la supervivencia del portafolio.
- **utils/**: Funciones auxiliares que pueden usarse en múltiples partes del proyecto.
- **backtesting/**: Herramientas para simular estrategias en datos históricos antes de usarlas en tiempo real.
- **logs/**: Registros de operaciones, errores y eventos del sistema para depuración y análisis.
- **tests/**: Pruebas automatizadas para verificar el correcto funcionamiento de componentes críticos.

## Configuración del Entorno Virtual

Un entorno virtual permite aislar las dependencias del proyecto, facilitando la reproducibilidad y evitando conflictos con otros proyectos Python.

### En Windows

1. Asegúrate de tener Python instalado (preferiblemente Python 3.8+)
2. Abre el Símbolo del Sistema (cmd) o PowerShell
3. Navega hasta la carpeta del proyecto:
   ```
   cd ruta\a\trading-bot
   ```
4. Crea un entorno virtual:
   ```
   python -m venv venv
   ```
5. Activa el entorno virtual:
   ```
   venv\Scripts\activate
   ```
6. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

### En macOS/Linux

1. Asegúrate de tener Python instalado (preferiblemente Python 3.8+)
2. Abre la Terminal
3. Navega hasta la carpeta del proyecto:
   ```
   cd ruta/a/trading-bot
   ```
4. Crea un entorno virtual:
   ```
   python3 -m venv venv
   ```
5. Activa el entorno virtual:
   ```
   source venv/bin/activate
   ```
6. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso Básico

Para ejecutar el bot de trading:

1. Configura tus claves API en el archivo `config/api_config.py` (crea este archivo basándote en `api_config_example.py`)
2. Ejecuta:
   ```
   python main.py
   ```

## Desarrollo de Estrategias

Para crear una nueva estrategia:

1. Crea un nuevo archivo en la carpeta `strategies/`
2. Implementa la lógica de trading
3. Realiza pruebas de backtesting en `backtesting/`
4. Integra la estrategia en el script principal

## Contribuciones

Para contribuir al proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
