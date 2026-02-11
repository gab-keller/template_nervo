# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO",
    layout="wide",
)

# --- CSS: small controlled gap + no overlap + tight grouping feel ---
st.markdown(
    """
    <style>
      /* Small but non-zero gutter between columns (prevents overlap) */
      div[data-testid="stHorizontalBlock"]{
        gap: 0.35rem !important;
      }

      /* Remove most column padding to avoid artificial whitespace */
      div[data-testid="column"]{
        padding-left: 0 !important;
        padding-right: 0 !important;
      }

      /* Tighter label styling */
      .inline-label{
        margin: 0 !important;
        padding: 0 0.35rem 0 0 !important; /* <-- tiny right padding = minimal gap */
        line-height: 1.6 !important;
        white-space: nowrap !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO")


def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)


def inline_label_input(
    label_text: str,
    key: str,
    placeholder: str = "",
    label_w: float = 1.2,
    input_w: float = 4.8,
    filler_w: float = 10.0,
):
    """
    Uses 3 columns:
      [label | input | filler]
    The filler column "eats" the remaining page width so label+input stay together.
    """
    c_label, c_input, _filler = st.columns(
        [label_w, input_w, filler_w],
        vertical_alignment="center",
    )
    with c_label:
        st.markdown(f'<div class="inline-label">{label_text}</div>', unsafe_allow_html=True)
    with c_input:
        return st.text_input(
            label="",
            key=key,
            placeholder=placeholder,
            label_visibility="collapsed",
        )


# -----------------------------
# 1) História clínica
# -----------------------------
st.subheader("História clínica:")

idade_inicio = inline_label_input(
    label_text="Idade ao início dos sintomas",
    key="idade_inicio_sintomas",
    placeholder="Ex.: 45",
    label_w=1.35,   # slightly wider label prevents overlap
    input_w=5.0,
    filler_w=10.0,
)

historia_clinica = text_area_lines(
    label="",
    lines=10,
    key="historia_clinica_texto",
    placeholder="Descreva aqui a história clínica...",
)

# -----------------------------
# 2) Antecedentes Patológicos
# -----------------------------
st.subheader("Antecedentes Patológicos")
antecedentes = text_area_lines(
    label="",
    lines=4,
    key="antecedentes_patologicos_texto",
    placeholder="Comorbidades, cirurgias, alergias, etc...",
)

# -----------------------------
# 3) História familiar
# -----------------------------
st.subheader("História familiar")
hist_familiar = text_area_lines(
    label="",
    lines=4,
    key="historia_familiar_texto",
    placeholder="Detalhe antecedentes familiares relevantes...",
)

# "Padrão de herança" + checkboxes tightly grouped (use filler column to prevent spreading)
c0, c1, c2, _fill = st.columns([1.15, 1.05, 1.05, 10.0], vertical_alignment="center")
with c0:
    st.markdown('<div class="inline-label">Padrão de herança</div>', unsafe_allow_html=True)
with c1:
    esporadico = st.checkbox("Esporádico", key="hf_esporadico")
with c2:
    familiar = st.checkbox("Familiar", key="hf_familiar")

if esporadico and familiar:
    st.warning("Você marcou **Esporádico** e **Familiar** ao mesmo tempo. Se preferir, selecione apenas um.")

# -----------------------------
# 4) Medicações modificadoras de doença/Imunossupressores
# -----------------------------
st.subheader("Medicações modificadoras de doença/Imunossupressores")
st.markdown("**Tratamento atual:**")

t1 = st.checkbox("em uso de tratamento medicamentoso", key="trat_em_uso")
if t1:
    tempo_em_uso = inline_label_input(
        label_text="há quanto tempo",
        key="trat_em_uso_tempo",
        placeholder="Ex.: 6 meses / 2 anos",
        label_w=0.9,
        input_w=4.0,
        filler_w=12.0,
    )

t2 = st.checkbox("sem tratamento medicamentoso", key="trat_sem")
if t2:
    tempo_sem = inline_label_input(
        label_text="há quanto tempo",
        key="trat_sem_tempo",
        placeholder="Ex.: 3 meses / desde 2021",
        label_w=0.9,
        input_w=4.0,
        filler_w=12.0,
    )

if t1 and t2:
    st.warning("Você marcou **em uso** e **sem tratamento** ao mesmo tempo. Se quiser, mantenha apenas uma opção.")

st.markdown("**Medicamentos de uso atual ou prévio, com data de início, data de término e motivo da suspensão**")
meds_atual_previo = text_area_lines(
    label="",
    lines=5,
    key="meds_atual_previo_texto",
    placeholder="Ex.: Rituximabe 1g D1/D15 (início 01/2024), suspensão 07/2024 por infecção...",
)

st.markdown("**Outros medicamentos**")
outros_meds = text_area_lines(
    label="",
    lines=5,
    key="outros_meds_texto",
    placeholder="Liste outros medicamentos relevantes...",
)

transplantado = st.checkbox("Paciente transplantado", key="paciente_transplantado")
