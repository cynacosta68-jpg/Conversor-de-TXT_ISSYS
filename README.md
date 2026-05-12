# Generador de txt ISSYS

Aplicación web que convierte los archivos Excel de prestaciones en el archivo TXT con formato de campos fijos separados por coma.

## Qué hace

1. Recibe dos archivos Excel:
   - **PrestacionesExport** — exportación de prestaciones
   - **Base_usuarios_MP** — base de usuarios con CUIT y matrícula provincial
2. Filtra solo las filas cuyo campo `numaut` empiece con `F`
3. Aplica las reglas de mapeo a los 18 campos del formato destino
4. Genera y descarga el archivo `a0100002.txt`

## Reglas de mapeo aplicadas

| Campo | Origen | Detalle |
|-------|--------|---------|
| 1 (dato de orden) | `numaut` | Dígitos después del 2° guion bajo, 10 chars |
| 2 (matrícula profesional) | — | Siempre `00000` |
| 3 (cod auditor) | — | Siempre `000` |
| 4 (fecha realización) | `fecha_prestacion` | Formato `aaaammdd` |
| 5 (cod práctica) | `cod_practica` | 6 chars |
| 6 (cantidad) | `cantidad` | 2 chars |
| 7 (% recarga) | — | `000.00` |
| 8 (% descuento) | — | `000.00` |
| 9 (tipo unidad arancelaria) | Honorario→1, Gasto→2 | 1 char |
| 10 (tipo honorarios médico) | Honorario→1, Ayudante→3, Gasto→2 | 1 char |
| 11 (tipo prestador) | `cuit` | Empieza con 3→7, sino→1 |
| 12 (código prestador) | `cuit` → lookup en Base_usuarios_MP | Matrícula, 5 chars |
| 13 (tipo integrante) | — | Siempre `1` |
| 14 (código integrante) | — | Siempre `00000` |
| 15 (folio) | `numaut` | Dígitos después del 1° guion bajo, 5 chars |
| 16-18 (diagnósticos) | — | Siempre `999` |

## Ejecutar localmente

```bash
# Clonar el repositorio
git clone https://github.com/TU-USUARIO/generador-a0100002.git
cd generador-a0100002

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run app.py
```

Se abre en `http://localhost:8501`. Subí los dos Excel y descargá el TXT.

## Deploy en Streamlit Cloud (gratis)

1. Subí este repositorio a GitHub
2. Entrá a [share.streamlit.io](https://share.streamlit.io)
3. Conectá tu cuenta de GitHub
4. Seleccioná el repositorio y el archivo `app.py`
5. Click en **Deploy**

La app queda online con una URL pública. Cada vez que subas los Excel se genera el TXT automáticamente.

## Estructura del proyecto

```
├── app.py                  # Aplicación principal
├── requirements.txt        # Dependencias Python
├── .streamlit/
│   └── config.toml         # Configuración visual de Streamlit
├── .gitignore
└── README.md
```
