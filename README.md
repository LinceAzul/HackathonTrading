# Trading Bot Algorítmico - Proyecto de Portafolio

Este proyecto implementa un bot de trading algorítmico en Python diseñado para competiciones de portafolios. El objetivo es crear estrategias que maximicen el rendimiento financiero mientras mantienen un control adecuado de riesgos.

## Métricas de Evaluación de Portafolio

Un portafolio de alto rendimiento se evalúa mediante las siguientes métricas clave:

| Métrica | Definición | Relevancia en competición |
|---------|------------|---------------------------|
| ROI (Rentabilidad) | % de ganancia/pérdida sobre el capital inicial | Métrica principal: indica cuánto ganó el portafolio |
| Factor de ganancia | Ganancia bruta / Pérdida bruta | Eficiencia global: >1 es rentable, >2 excelente |
| Win Rate | % de operaciones ganadoras | Consistencia de aciertos; combinada con ratio riesgo/recompensa |
| Drawdown máximo | Caída porcentual máxima desde un pico | Mide riesgo: menor drawdown indica más estabilidad |
| Ratio Sharpe | Retorno excedente dividido por volatilidad | Rendimiento ajustado al riesgo; alto valor = ganancias que justifican el riesgo |

Otras métricas consideradas:
- **Ganancia Neta Absoluta**: Total ganado descontando costos
- **Relación Riesgo-Recompensa**: Magnitud promedio de ganancias vs pérdidas
- **Consistencia**: Crecimiento estable sin depender de operaciones singulares
- **Riesgo de Ruina**: Probabilidad de perder todo el capital

## Estructura del Proyecto

```
trading-bot/
│
├── README.md                 # Este archivo de documentación
├── main.py                   # Script principal para ejecutar la estrategia en tiempo real
├── requirements.txt          # Dependencias del proyecto
│
├── config/                   # Archivos de configuración
│   ├── settings.py           # Configuraciones generales
│   └── api_config_example.py # Plantilla para claves API (no incluye claves reales)
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
├── risk_management/          # Gestión de riesgos
│   ├── __init__.py
│   ├── position_sizing.py    # Cálculo del tamaño de posiciones
│   └── stop_loss.py          # Lógica de stop-loss
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
├── logs/                     # Archivos de registro
│   └── trading.log           # Log principal de operaciones
│
└── tests/                    # Tests automatizados
    ├── __init__.py
    ├── test_strategies.py    # Pruebas unitarias para estrategias
    └── test_indicators.py    # Pruebas unitarias para indicadores
```

## Configuración del Entorno Virtual

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
