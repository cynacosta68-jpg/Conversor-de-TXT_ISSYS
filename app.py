import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# Configuración de página
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Generador a0100002.txt",
    page_icon="📄",
    layout="centered",
)

st.title("📄 Generador de archivo a0100002.txt")
st.markdown(
    "Subí los dos archivos Excel y el sistema genera automáticamente "
    "el TXT con el formato requerido (campos separados por coma, longitud fija)."
)

# ──────────────────────────────────────────────────────────────
# Upload de archivos
# ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    prest_file = st.file_uploader(
        "📥 PrestacionesExport (.xlsx)",
        type=["xlsx", "xls"],
        key="prest",
    )

with col2:
    base_file = st.file_uploader(
        "📥 Base_usuarios_MP (.xlsx)",
        type=["xlsx", "xls"],
        key="base",
    )


# ──────────────────────────────────────────────────────────────
# Lógica de procesamiento
# ──────────────────────────────────────────────────────────────
def process(prest_bytes: BytesIO, base_bytes: BytesIO):
    """Genera las líneas del TXT a partir de los dos Excel."""

    df = pd.read_excel(prest_bytes, dtype=str)
    base = pd.read_excel(base_bytes, dtype=str)

    # Lookup CUIT → Matrícula provincial
    base["CUIT_clean"] = base["CUIT"].str.replace("-", "", regex=False)
    cuit_to_mat = dict(zip(base["CUIT_clean"], base["Matricula"]))

    # Solo filas cuyo numaut empiece con "F"
    f_rows = df[df["numaut"].str.startswith("F", na=False)].copy()
    f_rows["cuit_clean"] = f_rows["cuit"].str.replace("-", "", regex=False)

    output_lines: list[str] = []
    warnings: list[str] = []

    for idx, row in f_rows.iterrows():
        # ── numaut → Campo 1 y Campo 15 ──
        parts = row["numaut"].split("_")
        if len(parts) < 3:
            warnings.append(f"Fila {idx}: numaut '{row['numaut']}' no tiene 3 partes")
            continue

        folio_raw = parts[1]       # Campo 15
        orden_raw = parts[2]       # Campo 1

        campo1  = orden_raw.strip().zfill(10)[:10]   # 10 Numérico
        campo2  = "00000"                              #  5 Numérico (ceros)
        campo3  = "000"                                #  3 Numérico
        campo15 = folio_raw.strip().zfill(5)[:5]      #  5 Numérico

        # ── fecha_prestacion → Campo 4 (aaaammdd) ──
        try:
            dt = pd.to_datetime(row["fecha_prestacion"])
            campo4 = dt.strftime("%Y%m%d")
        except Exception:
            campo4 = "00000000"
            warnings.append(f"Fila {idx}: fecha inválida '{row['fecha_prestacion']}'")

        # ── cod_practica → Campo 5 ──
        campo5 = str(row["cod_practica"]).strip().zfill(6)[:6]

        # ── cantidad → Campo 6 ──
        campo6 = str(row["cantidad"]).strip().zfill(2)[:2]

        # ── Campos fijos ──
        campo7  = "000.00"   # % recarga
        campo8  = "000.00"   # % descuento
        campo13 = "1"        # Tipo de integrante (siempre 1)
        campo14 = "00000"    # Código de integrante
        campo16 = "999"      # Diagnóstico 1
        campo17 = "999"      # Diagnóstico 2
        campo18 = "999"      # Diagnóstico 3

        # ── CUIT → Campo 11 (Tipo prestador) ──
        cuit_val = row["cuit_clean"]
        campo11 = "7" if cuit_val.startswith("3") else "1"

        # ── CUIT → Campo 12 (Código prestador = matrícula provincial) ──
        mat = cuit_to_mat.get(cuit_val)
        if mat is None:
            campo12 = "00000"
            warnings.append(f"Fila {idx}: CUIT '{cuit_val}' no encontrado en Base_usuarios_MP")
        else:
            campo12 = str(mat).strip().zfill(5)[:5]

        # ── Honorario / Ayudante / Gasto → Campo 9 y Campo 10 ──
        types: list[tuple[str, str]] = []

        def safe_float(val):
            try:
                return float(str(val).strip())
            except (ValueError, TypeError):
                return 0.0

        if safe_float(row["Honorario"]) != 0:
            types.append(("1", "1"))
        if safe_float(row["1er_ayudante"]) != 0:
            types.append(("1", "3"))
        if safe_float(row["2do_ayudante"]) != 0:
            types.append(("1", "3"))
        if safe_float(row["gasto"]) != 0:
            types.append(("2", "2"))

        if not types:
            types.append(("0", "0"))

        for campo9, campo10 in types:
            fields = [
                campo1, campo2, campo3, campo4, campo5, campo6,
                campo7, campo8, campo9, campo10, campo11, campo12,
                campo13, campo14, campo15, campo16, campo17, campo18,
            ]
            output_lines.append(",".join(fields))

    return output_lines, warnings


# ──────────────────────────────────────────────────────────────
# Ejecución automática al subir ambos archivos
# ──────────────────────────────────────────────────────────────
if prest_file and base_file:
    with st.spinner("Procesando archivos…"):
        lines, warns = process(prest_file, base_file)

    # Resultados
    st.success(f"✅ Archivo generado: **{len(lines)} líneas**")

    if warns:
        with st.expander(f"⚠️ {len(warns)} advertencias", expanded=False):
            for w in warns:
                st.text(w)

    # Vista previa
    with st.expander("🔍 Vista previa (primeras 20 líneas)", expanded=True):
        st.code("\n".join(lines[:20]), language="text")

    # Info de longitud
    lengths = {len(l) for l in lines}
    st.info(f"Longitud de línea: {lengths} caracteres (+ salto de línea)")

    # Botón de descarga
    txt_content = "\n".join(lines) + "\n"
    st.download_button(
        label="⬇️ Descargar a0100002.txt",
        data=txt_content.encode("utf-8"),
        file_name="a0100002.txt",
        mime="text/plain",
    )
else:
    st.info("👆 Subí ambos archivos Excel para comenzar el proceso.")
