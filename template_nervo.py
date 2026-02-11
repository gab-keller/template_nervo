```python
# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO",
    layout="wide",
)

st.title("TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO")

# Small helper to approximate "N lines" of space in a text area
def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    # Roughly ~24px per line; Streamlit uses pixel height
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)

# -----------------------------
# 1) História clínica
# -----------------------------
st.subheader("História clínica:")

c1, c2 = st.columns([1, 2])
with c1:
    st.markdown("**Idade ao início dos sintomas**")
with c2:
    idade_inicio = st.text_input(
        label="",
        key="idade_inicio_sintomas",
        placeholder="Ex.: 45",
        label_visibility="collapsed",
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

# Two checkboxes on the same line
cf1, cf2 = st.columns([1, 1])
with cf1:
    esporadico = st.checkbox("Esporádico", key="hf_esporadico")
with cf2:
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
    tc1, tc2 = st.columns([1, 2])
    with tc1:
        st.markdown("**há quanto tempo**")
    with tc2:
        tempo_em_uso = st.text_input(
            label="",
            key="trat_em_uso_tempo",
            placeholder="Ex.: 6 meses / 2 anos",
            label_visibility="collapsed",
        )

t2 = st.checkbox("sem tratamento medicamentoso", key="trat_sem")
if t2:
    tc1b, tc2b = st.columns([1, 2])
    with tc1b:
        st.markdown("**há quanto tempo**")
    with tc2b:
        tempo_sem = st.text_input(
            label="",
            key="trat_sem_tempo",
            placeholder="Ex.: 3 meses / desde 2021",
            label_visibility="collapsed",
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

# Optional: quick preview of captured data (comment out if you don't want it)
with st.expander("Visualizar dados (debug)", expanded=False):
    st.json(
        {
            "idade_inicio_sintomas": idade_inicio,
            "historia_clinica": historia_clinica,
            "antecedentes_patologicos": antecedentes,
            "historia_familiar": hist_familiar,
            "hf_esporadico": esporadico,
            "hf_familiar": familiar,
            "trat_em_uso": t1,
            "trat_em_uso_tempo": st.session_state.get("trat_em_uso_tempo", ""),
            "trat_sem": t2,
            "trat_sem_tempo": st.session_state.get("trat_sem_tempo", ""),
            "meds_atual_previo": meds_atual_previo,
            "outros_meds": outros_meds,
            "paciente_transplantado": transplantado,
        }
    )
```

