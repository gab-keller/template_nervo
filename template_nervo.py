# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO",
    layout="wide",
)

st.markdown(
    """
    <style>
      /* Keep a small gutter so label never touches the input */
      div[data-testid="stHorizontalBlock"]{ gap: 0.6rem !important; }

      /* Restore some padding so elements don't collide */
      div[data-testid="column"]{
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
      }

      /* Label should NOT overflow into the next column */
      .inline-label{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
        white-space: normal !important;   /* allow wrapping */
        overflow: hidden !important;      /* no spillover */
        text-overflow: ellipsis !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO")


def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)


def inline_label_input(label_text: str, key: str, placeholder: str = ""):
    # Wider label column prevents overlap across different zoom/screen sizes.
    # Filler keeps the pair left-aligned.
    c_label, c_input, _fill = st.columns([3.2, 3.8, 10.0], vertical_alignment="center")
    with c_label:
        st.markdown(f'<div class="inline-label">{label_text}</div>', unsafe_allow_html=True)
    with c_input:
        return st.text_input("", key=key, placeholder=placeholder, label_visibility="collapsed")


# 1) História clínica
st.subheader("História clínica:")

idade_inicio = inline_label_input(
    "Idade ao início dos sintomas",
    key="idade_inicio_sintomas",
    placeholder="Ex.: 45",
)

historia_clinica = text_area_lines(
    label="",
    lines=10,
    key="historia_clinica_texto",
    placeholder="Descreva aqui a história clínica...",
)

# 2) Antecedentes Patológicos
st.subheader("Antecedentes Patológicos")
antecedentes = text_area_lines(
    label="",
    lines=4,
    key="antecedentes_patologicos_texto",
    placeholder="Comorbidades, cirurgias, alergias, etc...",
)

# 3) História familiar
st.subheader("História familiar")
hist_familiar = text_area_lines(
    label="",
    lines=4,
    key="historia_familiar_texto",
    placeholder="Detalhe antecedentes familiares relevantes...",
)

# Tight grouped checkboxes (left), with filler
c0, c1, c2, _fill = st.columns([2.2, 1.4, 1.4, 10.0], vertical_alignment="center")
with c0:
    st.markdown('<div class="inline-label">Padrão de herança</div>', unsafe_allow_html=True)
with c1:
    esporadico = st.checkbox("Esporádico", key="hf_esporadico")
with c2:
    familiar = st.checkbox("Familiar", key="hf_familiar")

if esporadico and familiar:
    st.warning("Você marcou **Esporádico** e **Familiar** ao mesmo tempo. Se preferir, selecione apenas um.")

# 4) Medicações modificadoras de doença/Imunossupressores
st.subheader("Medicações modificadoras de doença/Imunossupressores")
st.markdown("**Tratamento atual:**")

t1 = st.checkbox("em uso de tratamento medicamentoso", key="trat_em_uso")
if t1:
    _ = inline_label_input("há quanto tempo", key="trat_em_uso_tempo", placeholder="Ex.: 6 meses / 2 anos")

t2 = st.checkbox("sem tratamento medicamentoso", key="trat_sem")
if t2:
    _ = inline_label_input("há quanto tempo", key="trat_sem_tempo", placeholder="Ex.: 3 meses / desde 2021")

if t1 and t2:
    st.warning("Você marcou **em uso** e **sem tratamento** ao mesmo tempo. Se quiser, mantenha apenas uma opção.")

st.markdown("**Medicamentos de uso atual ou prévio, com data de início, data de término e motivo da suspensão**")
meds_atual_previo = text_area_lines("", 5, "meds_atual_previo_texto")

st.markdown("**Outros medicamentos**")
outros_meds = text_area_lines("", 5, "outros_meds_texto")

transplantado = st.checkbox("Paciente transplantado", key="paciente_transplantado")
