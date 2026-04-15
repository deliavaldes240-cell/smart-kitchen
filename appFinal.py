import streamlit as st
import pandas as pd
import random
from collections import defaultdict
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime

# ==================== CONEXIÓN MONGODB ====================
def get_db():
    try:
        uri = st.secrets["MONGODB_URI"]
    except Exception:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        uri = os.getenv("MONGODB_URI")
    client = MongoClient(uri)
    return client["smart_kitchen"]

db = get_db()

col_ingredientes = db["ingredientes"]
col_recetas      = db["recetas"]
col_despensa     = db["despensa"]
col_menu         = db["menu"]
col_logs         = db["logs"]

# ================= CONFIG =================
st.set_page_config(page_title="Smart Kitchen", page_icon="🍳", layout="wide")

# ================= ESTILO UNIFICADO =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* ── Base ── */
.stApp {
    background: linear-gradient(180deg, #F4F7F2, #FEDBD8);
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background-color: #461220; }
section[data-testid="stSidebar"] * { color: #F4F7F2 !important; }

/* ── Header principal de la app ── */
.app-header {
    font-size: 42px;
    font-weight: 700;
    color: #461220;
    font-family: 'Inter', sans-serif;
    margin-bottom: 4px;
}
.subtitle {
    color: #8C2F39;
    font-size: 16px;
    font-family: 'Inter', sans-serif;
    margin-bottom: 24px;
}

/* ── Título de pantalla (nivel 1) ── */
.sk-title {
    font-size: 26px;
    font-weight: 700;
    color: #461220;
    font-family: 'Inter', sans-serif;
    margin-top: 8px;
    margin-bottom: 6px;
    border-bottom: 3px solid #B23A48;
    padding-bottom: 6px;
}

/* ── Subtítulo separador de sección (nivel 2) ── */
.sk-subtitle {
    font-size: 13px;
    font-weight: 700;
    color: #B23A48;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 28px;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #FEDBD8;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Texto de descripción de pantalla ── */
.screen-desc {
    background: #FFFFFF;
    border-left: 6px solid #B23A48;
    padding: 14px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(70, 18, 32, 0.08);
    margin-bottom: 20px;
    color: #461220;
    font-size: 15px;
    font-family: 'Inter', sans-serif;
}

/* ── Toast de éxito ── */
.toast-success {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 9999;
    background: #2D6A4F;
    color: #ffffff;
    padding: 14px 22px;
    border-radius: 14px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    gap: 10px;
    animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
    pointer-events: none;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeOut {
    from { opacity: 1; }
    to   { opacity: 0; transform: translateY(-10px); }
}

/* ── Toast de error ── */
.toast-error {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 9999;
    background: #7B2D2D;
    color: #ffffff;
    padding: 14px 22px;
    border-radius: 14px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    gap: 10px;
    animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
    pointer-events: none;
}

/* ── Texto cuerpo general ── */
.sk-body {
    font-size: 15px;
    color: #333333;
    font-family: 'Inter', sans-serif;
}

/* ── Cards ── */
.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 6px 16px rgba(70, 18, 32, 0.15);
    margin-bottom: 20px;
}

/* ── Botones ── */
.stButton > button {
    background-color: #B23A48;
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    border: none;
    transition: background-color 0.2s;
}
.stButton > button:hover { background-color: #8C2F39; }

/* ── Overrides de Streamlit nativos para consistencia ── */
h1, h2, h3 {
    font-family: 'Inter', sans-serif !important;
    color: #461220 !important;
}
h2 { color: #B23A48 !important; font-size: 18px !important; }
h3 { color: #B23A48 !important; font-size: 16px !important; }

/* ── Métricas ── */
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #461220 !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    color: #B23A48 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers de tipografía ──────────────────────────────
def sk_title(texto):
    st.markdown(f'<div class="sk-title">{texto}</div>', unsafe_allow_html=True)

def sk_subtitle(texto):
    st.markdown(f'<div class="sk-subtitle">{texto}</div>', unsafe_allow_html=True)

def sk_desc(texto):
    st.markdown(f'<div class="screen-desc">{texto}</div>', unsafe_allow_html=True)

def sk_body(texto):
    st.markdown(f'<div class="sk-body">{texto}</div>', unsafe_allow_html=True)

# ── Toast system ──────────────────────────────────────
def show_toast(mensaje, tipo="success"):
    css_class = "toast-success" if tipo == "success" else "toast-error"
    icono = "✅" if tipo == "success" else "❌"
    st.markdown(
        f'<div class="{css_class}">{icono} {mensaje}</div>',
        unsafe_allow_html=True
    )

def set_toast(mensaje, tipo="success"):
    """Guarda un toast en session_state para mostrarlo después del rerun."""
    st.session_state["_toast_msg"]  = mensaje
    st.session_state["_toast_tipo"] = tipo

def render_toast():
    """Renderiza el toast guardado (si existe) y lo limpia."""
    if st.session_state.get("_toast_msg"):
        show_toast(st.session_state["_toast_msg"], st.session_state.get("_toast_tipo", "success"))
        st.session_state["_toast_msg"]  = None
        st.session_state["_toast_tipo"] = None
# ──────────────────────────────────────────────────────

st.markdown('<div class="app-header">🍳 Smart Kitchen</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Organiza tu cocina de forma inteligente</div>', unsafe_allow_html=True)

# Renderizar toast pendiente al inicio de cada página
render_toast()

# ================= CATÁLOGO =================
ingredientes_por_categoria = {
    "Lácteos":   ["Leche", "Huevo", "Mantequilla", "Queso", "Yogurt", "Crema"],
    "Carnes":    ["Carne molida", "Salmón", "Pollo", "Jamón", "Carne de Res"],
    "Granos":    ["Arroz", "Pasta"],
    "Verduras":  ["Brocoli", "Papas", "Coliflor", "Tomates", "Calabacitas", "Cebolla"],
    "Frutas":    ["Plátano", "Manzana", "Naranja", "Frutos rojos"]
}

# ================= CONVERSIONES =================
CONVERSIONES = {"ml": 1, "litro": 1000, "taza": 240, "cucharada": 15, "g": 1, "kg": 1000}

DENSIDADES_DEFAULT = {
    "pasta":  0.75,
    "arroz":  0.85,
    "leche":  1.03,
    "harina": 0.6,
    "azucar": 0.85,
    "mantequilla": 0.96,
}

# ================= INIT =================
def precargar_ingredientes():
    if col_ingredientes.count_documents({}) == 0:
        docs = []
        for categoria, lista in ingredientes_por_categoria.items():
            for ing in lista:
                nombre = ing.lower()
                docs.append({
                    "nombre":      nombre,
                    "unidad_base": "pieza",
                    "densidad":    DENSIDADES_DEFAULT.get(nombre, None),
                    "categoria":   categoria
                })
        col_ingredientes.insert_many(docs)

precargar_ingredientes()

# ================= LOGGING =================
def log_evento(evento, detalle=""):
    col_logs.insert_one({
        "evento":    evento,
        "detalle":   detalle,
        "timestamp": datetime.utcnow()
    })

# ================= HELPERS =================
def obtener_todos_ingredientes():
    """Lee los ingredientes directamente del catálogo MongoDB (no del dict hardcoded)."""
    docs = list(col_ingredientes.find({}, {"nombre": 1}))
    return sorted([d["nombre"].capitalize() for d in docs])

def parse_ingredientes(texto):
    if not texto:
        return []
    resultado = []
    for linea in texto.split("\n"):
        if "|" in linea:
            partes = linea.split("|")
            resultado.append({
                "nombre":   partes[0].strip().lower(),
                "cantidad": float(partes[1]),
                "unidad":   partes[2].strip()
            })
        else:
            resultado.append({"nombre": linea.strip().lower(), "cantidad": 1, "unidad": "pieza"})
    return resultado

def normalizar(nombre):
    return nombre.lower().strip().rstrip("s")

def clasificar(ingrediente):
    ingrediente = ingrediente.lower()
    # Primero buscar en MongoDB por si fue agregado dinámicamente
    doc = col_ingredientes.find_one({"nombre": ingrediente})
    if doc and doc.get("categoria"):
        return doc["categoria"]
    # Fallback al diccionario hardcoded
    for categoria, lista in ingredientes_por_categoria.items():
        for item in lista:
            if item.lower() in ingrediente:
                return categoria
    return "Otros"

def obtener_densidad(nombre):
    doc = col_ingredientes.find_one({"nombre": nombre.lower()})
    if doc and doc.get("densidad"):
        return doc["densidad"]
    return DENSIDADES_DEFAULT.get(nombre.lower(), None)

def convertir_a_base(nombre, cantidad, unidad):
    unidad  = unidad.lower()
    nombre  = nombre.lower()
    if unidad == "unidad":
        unidad = "pieza"
    if unidad in ["ml", "litro", "taza", "cucharada"]:
        ml = cantidad * CONVERSIONES.get(unidad, 1)
        densidad = obtener_densidad(nombre)
        if densidad:
            return ml * densidad, "g"
        return ml, "ml"
    elif unidad in ["g", "kg"]:
        return cantidad * CONVERSIONES.get(unidad, 1), "g"
    return cantidad, unidad

# ================= CATÁLOGO INGREDIENTES =================
def obtener_ingredientes_catalogo():
    docs = list(col_ingredientes.find({}, {"_id": 1, "nombre": 1, "unidad_base": 1}))
    return pd.DataFrame(docs)

def obtener_nombres_ingredientes():
    return [d["nombre"] for d in col_ingredientes.find({}, {"nombre": 1})]

def agregar_ingrediente_catalogo(nombre, unidad, categoria="Otros"):
    nombre = nombre.lower().strip()
    if unidad == "unidad":
        unidad = "pieza"
    if not col_ingredientes.find_one({"nombre": nombre}):
        col_ingredientes.insert_one({
            "nombre":      nombre,
            "unidad_base": unidad,
            "densidad":    DENSIDADES_DEFAULT.get(nombre, None),
            "categoria":   categoria
        })
        log_evento("crear_ingrediente", nombre)
        return True   # fue creado nuevo
    return False  # ya existía

def actualizar_unidad_ingrediente(id_ing, nueva_unidad):
    if nueva_unidad == "unidad":
        nueva_unidad = "pieza"
    col_ingredientes.update_one({"_id": id_ing}, {"$set": {"unidad_base": nueva_unidad}})
    log_evento("editar_unidad", str(id_ing))

# ================= RECETAS =================
def cargar_recetas():
    docs = list(col_recetas.find())
    if not docs:
        return pd.DataFrame(columns=["_id", "nombre", "ingredientes"])
    return pd.DataFrame(docs)

def guardar_receta(nombre, ingredientes):
    col_recetas.insert_one({"nombre": nombre, "ingredientes": ingredientes})
    log_evento("crear_receta", nombre)

def actualizar_receta(id_receta, nuevo_nombre, nuevos_ingredientes):
    col_recetas.update_one(
        {"_id": id_receta},
        {"$set": {"nombre": nuevo_nombre, "ingredientes": nuevos_ingredientes}}
    )
    log_evento("editar_receta", nuevo_nombre)

def eliminar_receta(id_receta):
    col_recetas.delete_one({"_id": id_receta})
    log_evento("eliminar_receta", str(id_receta))

# ================= DESPENSA =================
def agregar_despensa(ingrediente, cantidad, unidad):
    ingrediente = ingrediente.lower()
    if unidad == "unidad":
        unidad = "pieza"
    cantidad_base, unidad_base = convertir_a_base(ingrediente, cantidad, unidad)
    doc = col_despensa.find_one({"ingrediente": ingrediente})
    if doc:
        col_despensa.update_one(
            {"ingrediente": ingrediente},
            {"$set": {"cantidad": doc["cantidad"] + cantidad_base, "unidad": unidad_base}}
        )
    else:
        col_despensa.insert_one({"ingrediente": ingrediente, "cantidad": cantidad_base, "unidad": unidad_base})
    log_evento("agregar_despensa", ingrediente)

def obtener_despensa():
    docs = list(col_despensa.find())
    if not docs:
        return pd.DataFrame(columns=["_id", "ingrediente", "cantidad", "unidad"])
    return pd.DataFrame(docs)

def eliminar_despensa(id_doc):
    col_despensa.delete_one({"_id": id_doc})
    log_evento("eliminar_despensa", str(id_doc))

# ================= MENÚ =================
def generar_menu():
    recetas  = cargar_recetas()
    despensa = obtener_despensa()
    ingredientes_casa = list(despensa["ingrediente"]) if not despensa.empty else []
    dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    menu = []
    usados_ingredientes = set()
    usados_recetas      = []

    for d in dias:
        scores = []
        for _, r in recetas.iterrows():
            ingredientes = parse_ingredientes(r["ingredientes"])
            nombres      = [i["nombre"] for i in ingredientes]
            en_despensa  = sum(n in ingredientes_casa for n in nombres)
            reutilizados = sum(n in usados_ingredientes for n in nombres)
            nuevos       = len(nombres) - en_despensa
            penalizacion = usados_recetas.count(r["nombre"]) * 5
            ruido        = random.uniform(-2, 2)
            score        = (en_despensa * 3) + (reutilizados * 2) - (nuevos * 0.5) - penalizacion + ruido
            scores.append((score, r))

        scores.sort(key=lambda x: x[0], reverse=True)
        elegido = random.choice(scores[:3])[1]
        menu.append((d, elegido["nombre"]))
        usados_recetas.append(elegido["nombre"])
        usados_ingredientes.update(i["nombre"] for i in parse_ingredientes(elegido["ingredientes"]))

    col_menu.delete_many({})
    col_menu.insert_many([{"dia": dia, "receta": receta} for dia, receta in menu])
    log_evento("generar_menu")

def actualizar_menu(dia, nueva_receta):
    col_menu.update_one({"dia": dia}, {"$set": {"receta": nueva_receta}})
    log_evento("actualizar_menu", f"{dia}->{nueva_receta}")

# ================= LISTA DE COMPRAS =================
FORZAR_GRAMOS = {"pasta", "arroz", "harina", "azucar", "sal"}

def lista_super():
    menu_df  = pd.DataFrame(list(col_menu.find()))
    recetas  = cargar_recetas()
    despensa = obtener_despensa()

    if menu_df.empty:
        return {}

    ingredientes_menu = defaultdict(lambda: {"cantidad": 0, "unidad": ""})

    for r_nombre in menu_df["receta"]:
        fila = recetas[recetas["nombre"] == r_nombre]
        if not fila.empty:
            for i in parse_ingredientes(fila.iloc[0]["ingredientes"]):
                nombre = normalizar(i["nombre"])
                cant, unidad = convertir_a_base(nombre, float(i["cantidad"]), i["unidad"])
                if nombre in FORZAR_GRAMOS and unidad == "ml":
                    densidad = obtener_densidad(nombre)
                    if densidad:
                        cant  = cant * densidad
                        unidad = "g"
                ingredientes_menu[nombre]["cantidad"] += cant
                if not ingredientes_menu[nombre]["unidad"]:
                    ingredientes_menu[nombre]["unidad"] = unidad

    casa = {}
    if not despensa.empty:
        for _, row in despensa.iterrows():
            nombre = normalizar(row["ingrediente"])
            cant, _ = convertir_a_base(nombre, row["cantidad"], row["unidad"])
            casa[nombre] = casa.get(nombre, 0) + cant

    agrupado = defaultdict(list)
    for ing, data in ingredientes_menu.items():
        falta = data["cantidad"] - casa.get(ing, 0)
        if falta > 0:
            agrupado[clasificar(ing)].append((ing, falta, data["unidad"]))

    return agrupado

# ================= OPCIONES DE UNIDAD =================
UNIDADES = ["pieza", "kg", "g", "litro", "ml", "taza", "cucharada", "otro"]
UNIDADES_RECETA = ["pieza", "kg", "g", "litro", "ml", "taza", "cucharada"]
CATEGORIAS = ["Lácteos", "Carnes", "Granos", "Verduras", "Frutas", "Otros"]

# ================= SIDEBAR =================
opcion = st.sidebar.radio("Smart Kitchen", [
    "📊 Dashboard", "🥗 Ingredientes", "➕ Nueva receta",
    "📖 Recetario", "🧠 Plan inteligente", "🛒 Lista de compras", "🥕 Despensa"
])

if "last_screen" not in st.session_state or st.session_state.last_screen != opcion:
    log_evento("ver_pantalla", opcion)
    st.session_state.last_screen = opcion

# ================= DASHBOARD =================
if opcion == "📊 Dashboard":
    sk_title("📊 Dashboard")
    sk_desc("Aquí puedes ver estadísticas del uso de Smart Kitchen.")

    total_recetas      = col_recetas.count_documents({})
    total_ingredientes = col_despensa.count_documents({})
    logs_df            = pd.DataFrame(list(col_logs.find()))
    menus_generados    = col_logs.count_documents({"evento": "generar_menu"})
    modificaciones     = col_logs.count_documents({"evento": "actualizar_menu"})

    col1, col2, col3 = st.columns(3)
    col4, col5       = st.columns(2)
    col1.metric("📖 Recetas registradas",       total_recetas)
    col2.metric("📅 Menús generados",            menus_generados)
    col3.metric("🥕 Ingredientes en despensa",   total_ingredientes)
    col4.metric("🛒 Listas del súper generadas", menus_generados)
    col5.metric("✏️ Modificaciones manuales",    modificaciones)

    st.divider()

    if not logs_df.empty:
        sk_subtitle("📊 Uso de funcionalidades")
        eventos = logs_df[logs_df["evento"] != "ver_pantalla"]["evento"].value_counts()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(eventos.index, eventos.values, color="#B23A48")
        ax.set_ylabel("Frecuencia", fontsize=12)
        ax.set_title("Frecuencia de uso por funcionalidad", fontsize=14, color="#461220")
        ax.set_xticklabels(eventos.index, rotation=30, ha="right", fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        st.pyplot(fig)

        sk_subtitle("Actividad de la aplicación")
        logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"])
        actividad = logs_df.groupby(logs_df["timestamp"].dt.date).size().reset_index()
        actividad.columns = ["fecha", "eventos"]

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.plot(actividad["fecha"], actividad["eventos"], marker="o", color="#461220", linewidth=2)
        ax2.fill_between(actividad["fecha"], actividad["eventos"], alpha=0.1, color="#B23A48")
        ax2.set_ylabel("Eventos", fontsize=12)
        ax2.set_xlabel("Fecha", fontsize=12)
        ax2.set_title("Actividad diaria", fontsize=14, color="#461220")
        ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%d-%m-%Y"))
        fig2.autofmt_xdate(rotation=45)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        st.pyplot(fig2)

# ================= INGREDIENTES =================
elif opcion == "🥗 Ingredientes":
    sk_title("🥗 Ingredientes")
    sk_desc("Administra tu catálogo de ingredientes y define su unidad base. Los ingredientes que agregues aquí estarán disponibles en Despensa y Recetas.")

    sk_subtitle("Agregar nuevo ingrediente")
    col1, col2, col3 = st.columns(3)
    nuevo_nombre = col1.text_input("Nombre ingrediente")
    nueva_unidad = col2.selectbox("Unidad base", UNIDADES)
    nueva_categoria = col3.selectbox("Categoría", CATEGORIAS)
    if nueva_unidad == "otro":
        nueva_unidad = st.text_input("Especifica unidad")

    if st.button("➕ Agregar ingrediente", use_container_width=True):
        if nuevo_nombre:
            creado = agregar_ingrediente_catalogo(nuevo_nombre, nueva_unidad, nueva_categoria)
            if creado:
                set_toast(f"✅ '{nuevo_nombre.capitalize()}' agregado al catálogo")
            else:
                set_toast(f"'{nuevo_nombre.capitalize()}' ya existe en el catálogo", tipo="error")
            st.rerun()
        else:
            set_toast("Escribe un nombre de ingrediente", tipo="error")
            st.rerun()

    st.divider()
    sk_subtitle("Ingredientes registrados")
    df = obtener_ingredientes_catalogo()

    if df.empty:
        st.info("No hay ingredientes aún")
    else:
        for _, row in df.iterrows():
            col1, col2, _ = st.columns([3, 2, 1])
            col1.write(row["nombre"])
            unidad_actual = row["unidad_base"].replace("unidad", "pieza")
            idx = UNIDADES.index(unidad_actual) if unidad_actual in UNIDADES else 0
            nueva_unidad = col2.selectbox("Unidad", UNIDADES, index=idx, key=f"unidad_{row['_id']}")
            if nueva_unidad == "otro":
                nueva_unidad = st.text_input("Especifica", value=unidad_actual, key=f"otro_{row['_id']}")
            if nueva_unidad != unidad_actual:
                actualizar_unidad_ingrediente(row["_id"], nueva_unidad)
                set_toast(f"'{row['nombre'].capitalize()}' actualizado a {nueva_unidad}")
                st.rerun()

# ================= NUEVA RECETA =================
elif opcion == "➕ Nueva receta":
    sk_title("➕ Nueva receta")
    sk_desc("Crea una nueva receta agregando sus ingredientes.")

    if "nueva_receta_ingredientes" not in st.session_state:
        st.session_state.nueva_receta_ingredientes = []

    sk_subtitle("Nombre receta")
    nombre = st.text_input("", placeholder="Ej. Pasta al pesto", label_visibility="collapsed")
    ingredientes_lista = st.session_state.nueva_receta_ingredientes

    sk_subtitle("Ingredientes de la receta")
    for idx, ing in enumerate(ingredientes_lista):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        col1.write(ing["nombre"])
        col2.write(ing["cantidad"])
        col3.write(ing["unidad"])
        if col4.button("❌", key=f"del_{idx}"):
            ingredientes_lista.pop(idx)
            set_toast(f"'{ing['nombre'].capitalize()}' eliminado de la receta")
            st.rerun()

    sk_subtitle("Agregar ingrediente")
    col1, col2, col3 = st.columns(3)
    lista_catalogo = obtener_nombres_ingredientes()
    opcion_ing = col1.selectbox("Ingrediente", ["Selecciona ingrediente"] + lista_catalogo + ["Otro..."], key="select_ing_nueva")
    nuevo_ing  = col1.text_input("Nuevo ingrediente", key="nuevo_ing_nueva") if opcion_ing == "Otro..." else opcion_ing
    nueva_cant = col2.number_input("Cantidad", min_value=0.1, value=1.0, key="cant_nueva")
    nueva_uni  = col3.selectbox("Unidad", UNIDADES_RECETA, key="uni_nueva")

    if st.button("➕ Agregar ingrediente", use_container_width=True):
        if nuevo_ing and nuevo_ing != "Selecciona ingrediente":
            if not any(i["nombre"] == nuevo_ing.lower().strip() for i in ingredientes_lista):
                if opcion_ing == "Otro...":
                    agregar_ingrediente_catalogo(nuevo_ing, nueva_uni)
                ingredientes_lista.append({"nombre": nuevo_ing.lower().strip(), "cantidad": nueva_cant, "unidad": nueva_uni})
                set_toast(f"'{nuevo_ing.capitalize()}' agregado a la receta")
                st.rerun()
            else:
                set_toast("Ese ingrediente ya está en la receta", tipo="error")
                st.rerun()
        else:
            set_toast("Selecciona un ingrediente primero", tipo="error")
            st.rerun()

    st.divider()
    if st.button("💾 Guardar receta", use_container_width=True):
        if nombre and ingredientes_lista:
            texto = "\n".join([f"{i['nombre']}|{i['cantidad']}|{i['unidad']}" for i in ingredientes_lista])
            guardar_receta(nombre, texto)
            st.session_state.nueva_receta_ingredientes = []
            set_toast(f"Receta '{nombre}' guardada exitosamente 🍽️")
            st.rerun()
        else:
            set_toast("Falta nombre o ingredientes", tipo="error")
            st.rerun()

# ================= RECETARIO =================
elif opcion == "📖 Recetario":
    sk_title("📖 Recetario")
    sk_desc("Explora, edita o elimina tus recetas guardadas.")

    recetas = cargar_recetas()
    cols = st.columns(2)

    for i, r in recetas.iterrows():
        with cols[i % 2]:
            with st.expander(f"🍽️ {r['nombre']}"):
                nuevo_nombre = st.text_input("Nombre", value=r["nombre"], key=f"nombre_{r['_id']}")
                lista_key    = f"ingredientes_{r['_id']}"
                if lista_key not in st.session_state:
                    st.session_state[lista_key] = parse_ingredientes(r["ingredientes"])
                ingredientes_lista = st.session_state[lista_key]

                sk_subtitle("Ingredientes")
                for idx, ing in enumerate(ingredientes_lista):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    col1.write(ing["nombre"])
                    col2.write(ing["cantidad"])
                    col3.write(ing["unidad"])
                    if col4.button("❌", key=f"del_{r['_id']}_{idx}"):
                        ingredientes_lista.pop(idx)
                        set_toast(f"'{ing['nombre'].capitalize()}' eliminado")
                        st.rerun()

                sk_subtitle("Agregar ingrediente")
                col1, col2, col3 = st.columns(3)
                lista_catalogo = obtener_nombres_ingredientes()
                opcion_ing = col1.selectbox("Ingrediente", ["Selecciona ingrediente"] + lista_catalogo + ["Otro..."], key=f"select_{r['_id']}")
                nuevo_ing  = col1.text_input("Nuevo ingrediente", key=f"nuevo_{r['_id']}") if opcion_ing == "Otro..." else opcion_ing
                nueva_cant = col2.number_input("Cantidad", min_value=0.1, value=1.0, key=f"cant_{r['_id']}")
                nueva_uni  = col3.selectbox("Unidad", UNIDADES_RECETA, key=f"uni_{r['_id']}")

                if st.button("➕ Agregar", key=f"add_{r['_id']}"):
                    if nuevo_ing and nuevo_ing != "Selecciona ingrediente":
                        if not any(i["nombre"] == nuevo_ing.lower().strip() for i in ingredientes_lista):
                            if opcion_ing == "Otro...":
                                agregar_ingrediente_catalogo(nuevo_ing, nueva_uni)
                            ingredientes_lista.append({"nombre": nuevo_ing.lower().strip(), "cantidad": nueva_cant, "unidad": nueva_uni})
                            set_toast(f"'{nuevo_ing.capitalize()}' agregado")
                            st.rerun()
                        else:
                            set_toast("Ese ingrediente ya está en la receta", tipo="error")
                            st.rerun()
                    else:
                        set_toast("Selecciona un ingrediente primero", tipo="error")
                        st.rerun()

                col_g, col_e = st.columns(2)
                if col_g.button("💾 Guardar cambios", key=f"guardar_{r['_id']}", use_container_width=True):
                    texto = "\n".join([f"{i['nombre']}|{i['cantidad']}|{i['unidad']}" for i in ingredientes_lista])
                    actualizar_receta(r["_id"], nuevo_nombre, texto)
                    set_toast(f"Receta '{nuevo_nombre}' actualizada")
                    st.rerun()

                if col_e.button("🗑️ Eliminar", key=f"del_rec_{r['_id']}", use_container_width=True):
                    eliminar_receta(r["_id"])
                    set_toast(f"Receta '{r['nombre']}' eliminada", tipo="error")
                    st.rerun()

# ================= PLAN INTELIGENTE =================
elif opcion == "🧠 Plan inteligente":
    sk_title("🧠 Plan inteligente")
    sk_desc("Genera automáticamente un menú semanal optimizado con los ingredientes que tienes en casa.")

    if st.button("🔄 Generar menú automático"):
        if cargar_recetas().empty:
            set_toast("Primero agrega recetas en el Recetario", tipo="error")
            st.rerun()
        else:
            generar_menu()
            set_toast("Menú semanal generado exitosamente 📅")
            st.rerun()

    menu_df = pd.DataFrame(list(col_menu.find()))
    recetas = cargar_recetas()
    nombres = list(recetas["nombre"]) if not recetas.empty else []

    if not menu_df.empty and nombres:
        if not set(menu_df["receta"]).issubset(set(nombres)):
            generar_menu()
            set_toast("El menú fue regenerado porque había recetas eliminadas")
            st.rerun()

        sk_subtitle("Menú de la semana")
        for _, row in menu_df.iterrows():
            col1, col2 = st.columns([1, 3])
            col1.markdown(f'<div class="sk-body"><b>{row["dia"]}</b></div>', unsafe_allow_html=True)
            idx_actual = nombres.index(row["receta"]) if row["receta"] in nombres else 0
            nueva = col2.selectbox("", nombres, index=idx_actual, key=row["dia"])
            if nueva != row["receta"]:
                actualizar_menu(row["dia"], nueva)
                set_toast(f"{row['dia']} actualizado a '{nueva}'")
                st.rerun()

# ================= LISTA DE COMPRAS =================
elif opcion == "🛒 Lista de compras":
    sk_title("🛒 Lista de compras")
    sk_desc("Esto es lo que tienes que comprar en el supermercado para seguir el menú semanal.")

    lista = lista_super()
    if not lista:
        st.info("Genera primero un menú en 🧠 Plan inteligente")
    for sec, items in lista.items():
        sk_subtitle(sec)
        for ing, cant, unidad in items:
            sk_body(f"• {ing.capitalize()} — {round(cant, 2)} {unidad}")

# ================= DESPENSA =================
elif opcion == "🥕 Despensa":
    sk_title("🥕 Despensa")
    sk_desc("Estos son los ingredientes que tienes en casa. Agrega los que hayas comprado.")

    # FIX: usa obtener_todos_ingredientes() que lee de MongoDB, no del dict hardcoded
    todos_ingredientes = obtener_todos_ingredientes()

    if not todos_ingredientes:
        st.warning("No hay ingredientes en el catálogo. Agrega algunos en 🥗 Ingredientes primero.")
    else:
        ing      = st.selectbox("Ingrediente", todos_ingredientes)
        col1, col2 = st.columns(2)
        cantidad = col1.number_input("Cantidad", min_value=0.0, value=1.0)
        unidad   = col2.selectbox("Unidad", UNIDADES)
        if unidad == "otro":
            unidad = col2.text_input("Especifica unidad")

        if st.button("➕ Agregar a despensa", use_container_width=True):
            agregar_despensa(ing, cantidad, unidad)
            set_toast(f"'{ing}' agregado a tu despensa 🥕")
            st.rerun()

    st.divider()
    sk_subtitle("Ingredientes en casa")
    despensa = obtener_despensa()
    for _, row in despensa.iterrows():
        col1, col2, col3 = st.columns([4, 2, 1])
        col1.write(row["ingrediente"].capitalize())
        col2.write(f"{row['cantidad']} {row['unidad']}")
        if col3.button("❌", key=str(row["_id"])):
            eliminar_despensa(row["_id"])
            set_toast(f"'{row['ingrediente'].capitalize()}' eliminado de la despensa", tipo="error")
            st.rerun()
