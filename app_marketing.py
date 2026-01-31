import streamlit as st
import os
from google import genai
from google.genai import types

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agência Mobile", layout="wide", page_icon="📱")
st.title("📱 Agência de Bolso 7.3")
st.markdown("*Sua agência de marketing, agora em qualquer lugar.*")

# --- GERENCIAMENTO DE CHAVE (SECRETS OU MANUAL) ---
# Tenta pegar dos Segredos da Nuvem (st.secrets)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Se não tiver nos segredos, pede na tela (fallback)
    api_key = st.session_state.get("api_key", "")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    # Se não achou nos segredos, mostra o campo
    if "GEMINI_API_KEY" not in st.secrets:
        api_key_input = st.text_input("Cole sua API Key aqui:", value=api_key, type="password")
        if api_key_input:
            st.session_state["api_key"] = api_key_input
            api_key = api_key_input
    else:
        st.success("🔑 Chave segura conectada!")

    st.markdown("---")
    st.subheader("👥 O Elenco")
    desc_ela = st.text_area("ELA:", value="Mulher jovem, cabelo castanho, olhos grandes, sardas.", height=70)
    desc_ele = st.text_area("ELE:", value="Homem, loiro escuro, óculos, barba por fazer.", height=70)
    estilo_visual = st.selectbox("Estilo", ["Traço Sketch P&B", "Webtoon Colorido", "Realista Cinematic"])

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📚 1. Livro", "🎨 2. Roteiro", "🚀 3. Finalizar (Visão)"])

# === ABA 1: CARREGAR LIVRO (MOBILE FRIENDLY) ===
with tab1:
    st.header("📚 Matéria Prima")
    st.info("No celular, suba o arquivo .txt ou .md do capítulo aqui.")
    
    arquivo_livro = st.file_uploader("Upload do Capítulo/Livro", type=["txt", "md"])
    
    if arquivo_livro:
        texto_livro = arquivo_livro.read().decode("utf-8")
        st.session_state['texto_livro'] = texto_livro
        st.success("✅ Texto carregado na memória!")
        st.text_area("Preview:", value=texto_livro[:500] + "...", height=100, disabled=True)

# === ABA 2: ROTEIRO VISUAL ===
with tab2:
    st.header("🎨 Criar Cena Visual")
    if 'texto_livro' not in st.session_state:
        st.warning("⚠️ Suba o arquivo do livro na Aba 1 primeiro.")
    else:
        if st.button("Listar Cenas"):
            with st.spinner("Lendo..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"Liste resumidamente 5 cenas deste texto:\n{st.session_state['texto_livro']}"
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                    st.session_state['lista_cenas'] = resp.text
                except Exception as e: st.error(f"Erro: {e}")

        if 'lista_cenas' in st.session_state:
            st.info(st.session_state['lista_cenas'])
            cena = st.text_input("Qual cena adaptar?", placeholder="Copie o nome da cena")
            
            if st.button("Gerar Webtoon"):
                if not api_key: st.error("Falta API Key")
                else:
                    with st.spinner("Escrevendo..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            prompt = f"""Roteiro de Webtoon de 4 painéis da cena '{cena}'.
                            Texto Original: {st.session_state['texto_livro']}
                            Estilo: {estilo_visual}. Personagens: {desc_ela} e {desc_ele}.
                            Saída: Descrição + Balão + Prompt de Imagem (Inglês)."""
                            resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                            st.session_state['quadrinho_final'] = resp.text
                        except Exception as e: st.error(f"Erro: {e}")

        if 'quadrinho_final' in st.session_state: st.markdown(st.session_state['quadrinho_final'])

# === ABA 3: FINALIZAR (VISÃO) ===
with tab3:
    st.header("🚀 Finalizar Post (Visão)")
    uploaded_img = st.file_uploader("Sua Imagem Pronta", type=["png", "jpg", "jpeg"])
    
    if uploaded_img and st.button("✍️ Gerar Legenda"):
        if not api_key: st.error("Falta API Key")
        else:
            with st.spinner("Olhando..."):
                try:
                    client = genai.Client(api_key=api_key)
                    img_bytes = uploaded_img.getvalue()
                    part = types.Part.from_bytes(data=img_bytes, mime_type=uploaded_img.type)
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=["Crie legenda engajadora e 3 CTAs curtos para vender este livro de romance.", part])
                    st.markdown(resp.text)
                except Exception as e: st.error(f"Erro: {e}")