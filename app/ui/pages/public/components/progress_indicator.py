import streamlit as st

def render_progress_indicator(current_step):
    """Визуальный индикатор прогресса"""
    steps = [
        {"num": 1, "icon": "📅", "title": "Дата и время"},
        {"num": 2, "icon": "👤", "title": "Ваши данные"},
        {"num": 3, "icon": "✅", "title": "Подтверждение"},
        {"num": 4, "icon": "🔐", "title": "Авторизация"}
    ]
    
    # Мобильная адаптация
    st.markdown("""
    <style>
    /* Десктопная версия */
    .progress-desktop {
        display: flex !important;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .progress-desktop .step-card {
        flex: 1;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        transition: transform 0.2s;
    }

    .progress-desktop-card {
        display: block;
    }
    
    .progress-desktop .step-card.completed {
        background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(136, 200, 188, 0.3);
    }
    
    .progress-desktop .step-card.active {
        background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(136, 200, 188, 0.4);
        border: 3px solid rgba(255, 255, 255, 0.5);
    }
    
    .progress-desktop .step-card.pending {
        background: rgba(240, 242, 245, 0.5);
        color: #9ca3af;
        border: 2px dashed rgba(156, 163, 175, 0.3);
    }
    
    /* Мобильная версия */
    .progress-mobile {
        display: none !important;
    }
    
    @media (max-width: 768px) {
        .progress-desktop {
            display: none !important;
        }
        
        .progress-mobile {
            display: block !important;
            margin-bottom: 1.5rem;
        }
        
        .progress-bar-container {
            background: rgba(240, 242, 245, 0.8);
            height: 6px;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            overflow: hidden;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #88c8bc 0%, #6ba292 100%);
            border-radius: 10px;
            transition: width 0.4s ease;
        }
        
        .mobile-step-info {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 1rem;
            background: rgba(136, 200, 188, 0.1);
            border-radius: 10px;
            border-left: 3px solid #88c8bc;
        }
        
        .mobile-step-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #2d5a4f;
        }
        
        .mobile-step-counter {
            font-size: 0.85rem;
            color: #6ba292;
            font-weight: 500;
        }
        
        .mobile-step-icon {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        
        .progress-desktop-card {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript для адаптации
    st.markdown("""
    <script>
    (function(){
        function collapseParents(el, levels){
            var p = el.parentElement;
            var i = 0;
            while(p && i < levels){
                try{
                    p.style.cssText = 'display: none !important; visibility: hidden !important; height: 0 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important;';
                }catch(e){}
                p = p.parentElement;
                i++;
            }
        }

        function restoreParents(el, levels){
            var p = el.parentElement;
            var i = 0;
            while(p && i < levels){
                try{
                    p.style.cssText = '';
                }catch(e){}
                p = p.parentElement;
                i++;
            }
        }

        function updateProgressView(){
            try{
                var desktops = Array.from(document.querySelectorAll('.progress-desktop'));
                var mobiles = Array.from(document.querySelectorAll('.progress-mobile'));
                if(desktops.length === 0 && mobiles.length === 0) return;
                if(window.innerWidth <= 768){
                    desktops.forEach(function(d){
                        d.style.cssText = 'display: none !important; visibility: hidden !important; height: 0 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important;';
                        collapseParents(d, 3);
                    });
                    mobiles.forEach(function(m){ m.style.cssText = 'display: block !important;'; });
                } else {
                    desktops.forEach(function(d){
                        d.style.cssText = 'display: flex !important; visibility: visible !important; height: auto !important; margin: initial !important; padding: initial !important;';
                        restoreParents(d, 3);
                    });
                    mobiles.forEach(function(m){ m.style.cssText = 'display: none !important;'; });
                }
            }catch(e){console.error(e)}
        }

        window.addEventListener('load', updateProgressView);
        window.addEventListener('resize', function(){ setTimeout(updateProgressView, 100); });
        setTimeout(updateProgressView, 50);
    })();
    </script>
    """, unsafe_allow_html=True)
    
    # Вычисляем процент прогресса
    progress_percent = (current_step / len(steps)) * 100
    
    # Мобильная версия
    st.markdown(f"""
    <div class="progress-mobile">
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {progress_percent}%"></div>
        </div>
        <div class="mobile-step-info">
            <div style="display: flex; align-items: center;">
                <span class="mobile-step-icon">{steps[current_step-1]["icon"]}</span>
                <span class="mobile-step-title">{steps[current_step-1]["title"]}</span>
            </div>
            <span class="mobile-step-counter">Шаг {current_step} из {len(steps)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Десктопная версия
    st.markdown('<div class="progress-desktop">', unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    for idx, step in enumerate(steps):
        with cols[idx]:
            if step["num"] < current_step:
                st.markdown(f"""
                <div class="step-card progress-desktop-card" style="text-align: center; padding: 15px; background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
                    border-radius: 12px; color: white; box-shadow: 0 2px 8px rgba(136, 200, 188, 0.3);">
                    <div style="font-size: 28px; margin-bottom: 5px;">✓</div>
                    <div style="font-size: 12px; font-weight: 600;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
            elif step["num"] == current_step:
                st.markdown(f"""
                <div id="current-step" class="step-card progress-desktop-card" style="text-align: center; padding: 15px; background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
                    border-radius: 12px; color: white; box-shadow: 0 4px 12px rgba(136, 200, 188, 0.4);
                    border: 3px solid rgba(255, 255, 255, 0.5);">
                    <div style="font-size: 28px; margin-bottom: 5px;">{step["icon"]}</div>
                    <div style="font-size: 12px; font-weight: 700;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="step-card progress-desktop-card" style="text-align: center; padding: 15px; background: rgba(240, 242, 245, 0.5); 
                    border-radius: 12px; color: #9ca3af; border: 2px dashed rgba(156, 163, 175, 0.3);">
                    <div style="font-size: 28px; margin-bottom: 5px; opacity: 0.5;">{step["icon"]}</div>
                    <div style="font-size: 12px; font-weight: 500;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)