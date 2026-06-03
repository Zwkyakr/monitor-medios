import feedparser
import requests
import json
import os
import re
import time
import calendar
import unicodedata
from datetime import datetime
from flask import Flask
import threading

# ==============================================================================
# 1. CONFIGURACIÓN E IDENTIFICACIÓN (Extracción Segura de Llaves)
# ==============================================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "1468116225"))

MODO_LISTA = "AUTO" 

# ==============================================================================
# 2. DEFINICIÓN DE LISTAS DE MEDIOS
# ==============================================================================
LISTA_1 = [
    "https://veracruz.quadratin.com.mx/feed/",
    "https://golpepolitico.com/feed/",
    "https://imagendeveracruz.mx/feed/",
    "https://niusdeveracruz.com/feed/",
    "https://e-veracruz.mx/rss",
    "https://forocoatza.com/feed/",
    "https://www.lapoliticaenrosa.com/feed/",
    "https://coatzadigital.mx/feed/",
    "https://surestesur.com/feed/",
    "https://www.imagenypolitica.com/feed/",
    "https://diariodelistmo.com/feed/",
    "https://sietediasnoticias.com/feed/",
    "https://laopinion.net/feed/",
    "https://heraldodexalapa.com.mx/feed/",
    "https://www.jornada.com.mx/rss/edicion.xml",
    "https://www.razon.com.mx/feed/",
    "https://www.excelsior.com.mx/rss.xml",
    "https://mvsnoticias.com/feed/"
]

LISTA_2 = [
    "https://www.jornada.com.mx/rss/edicion.xml",
    "https://www.excelsior.com.mx/rss.xml"
]

# ==============================================================================
# 3. PARÁMETROS DE FILTRADO
# ==============================================================================
PARAMETROS = [
    "Rocío Nahle", "Rocio Nahle", "Nahle", "Mañanera", "DIF Estatal", "DIF Veracruz",
    "CGEC", "Contraloría General del Estado", "CGCS", "Coordinación General Comunicación Social",
    "SEGOB", "Secretaría de Gobierno", "SSP", "Secretaría de Seguridad Pública",
    "SEV", "Secretaría de Educación de Veracruz", "SS", "Secretaría de Salud",
    "SEFIPLAN", "Secretaría de Finanzas y Planeación", "SEDECOP", "Secretaría de Desarrollo Económico y Portuario",
    "SEDESOL", "Secretaría de Desarrollo Social", "SIOP", "Secretaría de Infraestructura y Obras Públicas",
    "STPSP", "Secretaría de Trabajo, Previsión Social y Productividad", "SECTUR", "Secretaría de Turismo",
    "SECVER", "Secretaría de Cultura de Veracruz", "SEDEMA", "Secretaría de Medio Ambiente",
    "SEDARPA", "Secretaría de Desarrollo Agropecuario, Rural, Pesca y Alimentación", "SPC", "Secretaría de Protección Civil",
    "Zona Norte", "Zona Centro", "Zona Sur", "Zona Altas Montañas", "Zona Totonacapan",
    "Acajete", "Acatlán", "Acayucan", "Actopan", "Acula", "Acultzingo", "Agua Dulce", 
    "Álamo Temapache", "Alpatláhuac", "Alto Lucero", "Altotonga", "Alvarado", "Amatitlán", 
    "Amatlán de los Reyes", "Ángel R. Cabada", "Apazapan", "Aquila", "Astacinga", 
    "Atlahuilco", "Atoyac", "Atzacan", "Atzalan", "Ayahualulco", "Banderilla", 
    "Benito Juárez", "Boca del Río", "Calcahualco", "Camerino Z. Mendoza", 
    "Carlos A. Carrillo", "Carrillo Puerto", "Catemaco", "Cazones de Herrera", 
    "Cerro Azul", "Chacaltianguis", "Chalma", "Chiconamel", "Chiconquiaco", 
    "Chicontepec", "Chinameca", "Chinampa de Gorostiza", "Chocamán", "Chontla", 
    "Chumatlán", "Coacoatzintla", "Coahuitlán", "Coatepec", "Coatzacoalcos", 
    "Coatzintla", "Comapa", "Córdoba", "Cosamaloapan", "Cosautlán de Carvajal", 
    "Coscomatepec", "Cosoleacaque", "Cotaxtla", "Coxquihui", "Coyutla", "Cuichapa", 
    "Cuitláhuac", "El Higo", "Emiliano Zapata", "Espinal", "Filomeno Mata", "Fortín", 
    "Gutiérrez Zamora", "Hidalgotitlán", "Huatusco", "Huayacocotla", "Hueyapan de Ocampo", 
    "Huiloapan", "Ignacio de la Llave", "Ilamatlán", "Isla", "Ixcatepec", 
    "Ixhuacán de los Reyes", "Ixhuatlán de Madero", "Ixhuatlán del Café", 
    "Ixhuatlán del Sureste", "Ixmatlahuacan", "Ixtaczoquitlán", "Jalacingo", 
    "Jalcomulco", "Jáltipan", "Jamapa", "Jesús Carranza", "Jilotepec", "José Azueta", 
    "Juan Rodríguez Clara", "Juchique de Ferrer", "Landero y Coss", "Las Choapas", 
    "Las Minas", "Las Vigas", "Lerdo de Tejada", "Los Reyes", "Magdalena", 
    "Maltrata", "Mariano Escobedo", "Martínez de la Torre", "Mecayapan", "Mecatlán", 
    "Miahuatlán", "Minatitlán", "Misantla", "Mixtla de Altamirano", "Moloacán", 
    "Naranjal", "Naranjos Amatlán", "Naolinco", "Nanchital", "Nautla", "Nogales", 
    "Oluta", "Omealca", "Orizaba", "Otatitlán", "Oteapan", "Ozuluama", "Pajapan", 
    "Pánuco", "Papantla", "Paso del Macho", "Paso de Ovejas", "Perote", 
    "Platón Sánchez", "Playa Vicente", "Poza Rica", "Pueblo Viejo", "Puente Nacional", 
    "Rafael Delgado", "Rafael Lucio", "Río Blanco", "Saltabarranca", 
    "San Andrés Tenejapan", "San Andrés Tuxtla", "San Juan Evangelista", 
    "Santiago Tuxtla", "Santiago Sochiapan", "Sayula de Alemán", "Soconusco", 
    "Sochiapa", "Soledad Atzompa", "Soledad de Doblado", "Soteapan", "Tamalín", 
    "Tamiahua", "Tampico Alto", "Tancoco", "Tantima", "Tantoyuca", "Tatahuicapan", 
    "Tatatila", "Tecolutla", "Tehuipango", "Tempoal", "Tenampa", "Tenochtitlán", 
    "Teocelo", "Tepatlaxco", "Tepetlán", "Tepetzintla", "Tequila", "Texcatepec", 
    "Texhuacán", "Texistepec", "Tezonapa", "Tierra Blanca", "Tihuatlán", 
    "Tlachichilco", "Tlacojalpan", "Tlacolulan", "Tlacotalpan", "Tlacotepec de Mejía", 
    "Tlaltetela", "Tlapacoyan", "Tlaquilpa", "Tlilapan", "Tomatlán", "Tonayán", 
    "Totutla", "Tres Valles", "Tuxpan", "Tuxtilla", "Úrsulo Galván", "Vega de Alatorre", 
    "Veracruz", "Villa Aldama", "Xalapa", "Xico", "Xoxocotla", "Yanga", "Yecuatla", 
    "Zacualpan", "Zaragoza", "Zentla", "Zongolica", "Zontecomatlán", "Zozocolco"
]

ARCHIVO_HISTORIAL = "historial_noticias.json"

# ==============================================================================
# 4. FUNCIONES LÓGICAS
# ==============================================================================
def normalizar_texto(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')

def determinar_lista_medios():
    if MODO_LISTA == "LISTA_1": return LISTA_1, "Lista 1 (Manual)"
    if MODO_LISTA == "LISTA_2": return LISTA_2, "Lista 2 (Manual)"
    return (LISTA_2, "Lista 2 (Fin de Semana)") if datetime.today().weekday() >= 5 else (LISTA_1, "Lista 1 (Entre Semana)")

def cargar_historial():
    if os.path.exists(ARCHIVO_HISTORIAL):
        try:
            with open(ARCHIVO_HISTORIAL, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def guardar_historial(historial):
    if len(historial) > 1500: historial = historial[-1500:]
    try:
        with open(ARCHIVO_HISTORIAL, "w", encoding="utf-8") as f: json.dump(historial, f, ensure_ascii=False, indent=4)
    except: pass

def evaluar_texto(texto, palabras_clave):
    texto_norm = normalizar_texto(texto)
    for kw in palabras_clave:
        kw_norm = normalizar_texto(kw)
        if len(kw_norm) <= 4:
            if re.search(rf"\b{re.escape(kw_norm)}\b", texto_norm): return True, kw
        else:
            if kw_norm in texto_norm: return True, kw
    return False, None

def enviar_mensaje_telegram(texto):
    if not TELEGRAM_TOKEN: return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown", "disable_web_page_preview": True}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 400:
            payload["parse_mode"] = ""
            response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

def ejecutar_monitoreo_silencioso():
    medios_activos, nombre_lista = determinar_lista_medios()
    historial = cargar_historial()
    alertas_enviadas = 0
    
    for url_rss in medios_activos:
        try:
            feed = feedparser.parse(url_rss)
            nombre_medio = feed.feed.get("title", url_rss.split("//")[-1].split("/")[0])
            for entrada in feed.entries:
                link = entrada.get("link")
                if not link or link in historial: continue
                
                # --- FILTRO CRÍTICO ACTUALIZADO: ÚLTIMAS 12 HORAS ---
                fecha_parsed = entrada.get("published_parsed") or entrada.get("updated_parsed")
                if fecha_parsed:
                    try:
                        nota_epoch = calendar.timegm(fecha_parsed)
                        ahora_epoch = time.time()
                        # 43200 segundos = 12 horas exactas
                        if (ahora_epoch - nota_epoch) > 43200:
                            continue  # Si es más vieja de 12 horas, la ignora por completo
                    except:
                        pass
                
                titulo = entrada.get("title", "")
                resumen = entrada.get("summary", "")
                
                hizo_match, kw_detectada = evaluar_texto(titulo, PARAMETROS)
                if not hizo_match:
                    hizo_match, kw_detectada = evaluar_texto(resumen, PARAMETROS)
                
                if hizo_match:
                    ahora = datetime.now()
                    timestamp_alerta = ahora.strftime("%H:%M del %d/%m/%Y")
                    
                    mensaje = (
                        f"🚨 *ALERTA DE MONITOREO CRÍTICO*\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"📌 *Medio:* {nombre_medio}\n"
                        f"🎯 *Match Origen:* `{kw_detectada}`\n"
                        f"📝 *Título:* {titulo}\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"🕒 _Información copiada a las {timestamp_alerta}_\n"
                        f"🔗 [Abrir Nota Completa]({link})"
                    )
                    
                    enviar_mensaje_telegram(mensaje)
                    alertas_enviadas += 1
                    time.sleep(0.4)  # Pausa de protección antispam para Telegram
                
                historial.append(link)
        except: continue
            
    guardar_historial(historial)
    return alertas_enviadas, nombre_lista

# ==============================================================================
# 5. MOTOR DE ESCUCHA INTERACTIVO
# ==============================================================================
def iniciar_interfaz_bot():
    global MODO_LISTA
    offset = 0
    time.sleep(5)  
    enviar_mensaje_telegram("🤖 *Sistema de Inteligencia de Medios Activo (Sin IA - 12H)*\nEscribe `/ayuda` para ver los comandos.")

    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=20"
            respuesta = requests.get(url, timeout=25).json()
            if not respuesta.get("ok") or not respuesta.get("result"):
                time.sleep(1)
                continue
            for actualizacion in respuesta["result"]:
                offset = actualizacion["update_id"] + 1
                mensaje = actualizacion.get("message", {})
                usuario_id = mensaje.get("from", {}).get("id")
                texto_comando = mensaje.get("text", "").strip()
                
                if usuario_id != CHAT_ID: continue
                
                if texto_comando == "/start" or texto_comando == "/ayuda":
                    menu = (
                        "📱 *Panel de Control*\n\n"
                        "👉 `/escanear` : Escaneo ultra rápido de portales (Últimas 12H).\n"
                        "👉 `/modo` : Cambiar listas de medios.\n"
                        "👉 `/parametros` : Ver criterios activos.\n"
                        "👉 `/limpiar` : Forzar re-análisis completo de portadas."
                    )
                    enviar_mensaje_telegram(menu)
                elif texto_comando == "/escanear":
                    enviar_mensaje_telegram("🔍 _Escaneando portales de noticias... Por favor espera._")
                    total, lista_usada = ejecutar_monitoreo_silencioso()
                    enviar_mensaje_telegram(f"✅ *Escaneo Terminado.*\n✨ Alertas enviadas en el rango de 12H: `{total}`")
                elif texto_comando == "/modo":
                    msg_modo = f"⚙️ Modo actual: `{MODO_LISTA}`\n\n👉 `/set_auto` | `/set_lista1` | `/set_lista2`"
                    enviar_mensaje_telegram(msg_modo)
                elif texto_comando == "/set_auto":
                    MODO_LISTA = "AUTO"
                    enviar_mensaje_telegram("🔄 Modo: `AUTOMÁTICO`")
                elif texto_comando == "/set_lista1":
                    MODO_LISTA = "LISTA_1"
                    enviar_mensaje_telegram("📌 Modo: `FORZAR LISTA 1`")
                elif texto_comando == "/set_lista2":
                    MODO_LISTA = "LISTA_2"
                    enviar_mensaje_telegram("📌 Modo: `FORZAR LISTA 2`")
                elif texto_comando == "/parametros":
                    msg_kw = f"🎯 *Criterios:* Gobernadora, Secretarías Estatales y los 212 Municipios de Veracruz activos."
                    enviar_mensaje_telegram(msg_kw)
                elif texto_comando == "/limpiar":
                    if os.path.exists(ARCHIVO_HISTORIAL): os.remove(ARCHIVO_HISTORIAL)
                    enviar_mensaje_telegram("🗑️ *Historial limpio.* Listo para procesar portadas.")
        except: time.sleep(2)

# ==============================================================================
# 6. SERVIDOR WEB PRINCIPAL
# ==============================================================================
web_app = Flask('')
@web_app.route('/')
def home(): return "Bot de Monitoreo con Filtro de Tiempo Activo 24/7 (12H Match)"

if __name__ == "__main__":
    threading.Thread(target=iniciar_interfaz_bot, daemon=True).start()
    puerto = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=puerto)
