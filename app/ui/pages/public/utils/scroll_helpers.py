import streamlit as st

def render_scroll_script(current_step):
    """Скрипт для автоматической прокрутки к текущему шагу"""
    st.markdown(f"""
    <script>
        // Прокрутка к индикатору текущего шага
        setTimeout(function() {{
            const element = document.getElementById('step-indicator-{current_step}');
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }}, 100);
        
        // Прокрутка к активному полю ввода при фокусе
        document.addEventListener('DOMContentLoaded', function() {{
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {{
                input.addEventListener('focus', function() {{
                    setTimeout(() => {{
                        this.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}, 300);
                }});
            }});
        }});
    </script>
    """, unsafe_allow_html=True)

def render_step_anchor(step_name):
    """Создает якорь для шага формы"""
    st.markdown(f'<div id="{step_name}"></div>', unsafe_allow_html=True)

def render_field_anchor(field_name):
    """Создает якорь для поля формы"""
    st.markdown(f'<div id="field-{field_name}"></div>', unsafe_allow_html=True)

def render_navigation_anchor(step_number):
    """Создает якорь для навигации шага"""
    st.markdown(f'<div id="step{step_number}-nav"></div>', unsafe_allow_html=True)

def render_tab_anchor(tab_name):
    """Создает якорь для вкладки"""
    st.markdown(f'<div id="{tab_name}-tab"></div>', unsafe_allow_html=True)

def scroll_to_element(element_id, delay=100):
    """Прокручивает к элементу с заданным ID"""
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            const element = document.getElementById('{element_id}');
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }}, {delay});
    </script>
    """, unsafe_allow_html=True)

def focus_on_element(element_id, delay=300):
    """Устанавливает фокус на элемент с заданным ID"""
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            const element = document.getElementById('{element_id}');
            if (element) {{
                element.focus();
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }}, {delay});
    </script>
    """, unsafe_allow_html=True)