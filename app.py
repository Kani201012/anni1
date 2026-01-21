import streamlit as st
import zipfile
import io
import json
from datetime import datetime

# --- 1. DESIGN STUDIO CONFIGURATION ---
st.set_page_config(page_title="Kaydiem Titan v8.1 | Stable E-com Architect", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main { background: #0f172a; color: white; }
    .stTabs [data-baseweb="tab"] { color: white; font-weight: bold; font-size: 1.1rem; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 4em; 
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
        color: white; font-weight: 900; border: none; font-size: 1.4rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: all 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: DESIGN STUDIO ---
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/business_profile_96dp.png", width=50)
    st.title("Titan v8.1 Studio")
    
    with st.expander("🎭 Architecture", expanded=True):
        layout_dna = st.selectbox("Design DNA", ["Classic Royal", "Industrial Titan", "Soft-UI", "Glass-Tech"])
        p_color = st.color_picker("Primary Brand Color", "#4A0E0E")
        s_color = st.color_picker("Accent/CTA Color", "#D4AF37")
        # FIXED: Value "24px" is now inside the options list to prevent ValueError
        border_rad = st.select_slider("Corner Roundness", options=["0px", "12px", "24px", "60px"], value="24px")

    with st.expander("✍️ Typography", expanded=True):
        h_font = st.selectbox("Heading Font", ["Playfair Display", "Oswald", "Montserrat", "Syncopate"])
        b_font = st.selectbox("Body Font", ["Montserrat", "Inter", "Roboto"])
        h_weight = st.select_slider("Weight", options=["300", "400", "700", "900"], value="700")

    gsc_tag = st.text_input("GSC Verification Tag")
    st.info("Built by www.kaydiemscriptlab.com")

st.title("🏗️ Kaydiem Titan Supreme v8.1")

# --- 2. MULTI-TAB DATA COLLECTION ---
tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🛒 Master Inventory", "🌟 Social Proof", "⚖️ Legal"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Red Hippo (The Planners)")
        biz_phone = st.text_input("Verified Phone", "+91 84540 02711")
    with c2:
        biz_cat = st.text_input("Category", "Luxury Wedding Planner")
        prod_url = st.text_input("Production URL", "https://kani201012.github.io/site/")
    biz_logo = st.text_input("Logo URL")
    biz_addr = st.text_area("Full Maps Physical Address")
    biz_areas = st.text_area("Service Areas", "Vasant Kunj, Chhatarpur, South Delhi")
    map_iframe = st.text_area("Map Embed HTML Code")

with tabs[1]:
    hero_h = st.text_input("Hero Headline", "Crafting Dream Weddings")
    seo_d = st.text_input("Meta Description", "Premium Wedding Planner & Decorator.")
    biz_key = st.text_input("SEO Keywords")
    biz_serv = st.text_area("Services (One per line)")
    about_txt = st.text_area("Our Story (800+ Words)", height=250)

with tabs[2]:
    st.header("📈 Enterprise Inventory & E-commerce Hub")
    st.warning("GUIDE: Column order: Name | Value | Description | Image1 | Image2 | Image3")
    sheet_url = st.text_input("Published CSV URL")

with tabs[3]:
    testi = st.text_area("Testimonials (Name | Quote)")
    faqs = st.text_area("FAQ (Question? ? Answer)")

with tabs[4]:
    priv_body = st.text_area("Privacy Policy Content", height=300)
    terms_body = st.text_area("Terms Content", height=300)

# --- 3. THE SUPREME ENGINE V8.1 ---

if st.button("🚀 DEPLOY 1st CLASS DYNAMIC ASSET"):
    
    img_h = "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&q=80&w=1600"
    img_fallback = "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800"
    logo_html = f'<img src="{biz_logo}" alt="{biz_name}" class="h-12 w-auto">' if biz_logo else f'<span class="text-2xl font-black" style="color:var(--p)">{biz_name}</span>'
    wa_clean = biz_phone.replace(" ", "").replace("+", "")
    wa_base_url = f"https://wa.me/{wa_clean}?text="

    theme_css = f"""
    :root {{ --p: {p_color}; --s: {s_color}; --radius: {border_rad}; }}
    body {{ font-family: '{b_font}', sans-serif; color: #0f172a; line-height: 1.7; overflow-x: hidden; width: 100%; }}
    h1, h2, h3 {{ font-family: '{h_font}', sans-serif; font-weight: {h_weight}; text-transform: uppercase; line-height: 1.1; }}
    .hero-title {{ font-size: clamp(2.2rem, 9vw, 95px); text-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
    .btn-accent {{ background: var(--s); color: white; padding: 1.1rem 2.8rem; border-radius: var(--radius); font-weight: 900; transition: all 0.4s; display: inline-block; box-shadow: 0 10px 20px -5px var(--s); cursor: pointer; }}
    .glass-nav {{ background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(0,0,0,0.08); width: 100%; }}
    
    .hero-mask {{ 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.5)), url('{img_h}'); 
        background-size: cover; background-position: center; min-height: 85vh; 
        display: flex; align-items: center; justify-content: center; margin: 0; padding: 0; width: 100%;
    }}
    
    .product-card {{ background: white; border-radius: var(--radius); padding: 2rem; border: 1px solid #f1f5f9; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); transition: 0.3s; cursor: pointer; }}
    #modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 10000; padding: 1rem; overflow-y: auto; align-items: center; justify-content: center; }}
    .modal-content {{ background: white; max-width: 900px; width: 100%; border-radius: var(--radius); overflow: hidden; position: relative; }}
    .legal-text {{ white-space: pre-wrap; word-wrap: break-word; font-size: 1.1rem; color: #334155; }}
    .legal-bold-title {{ font-weight: 900; font-size: clamp(2rem, 6vw, 4rem); color: var(--p); margin-bottom: 2rem; text-transform: uppercase; }}
    """

    def get_layout(title, desc, content, is_index=False):
        v_tag = f'<meta name="google-site-verification" content="{gsc_tag}">' if (is_index and gsc_tag) else ""
        
        dynamic_script = ""
        if is_index and sheet_url:
            dynamic_script = f"""
            <script>
            let currentProducts = [];
            async function fetchLiveData() {{
                try {{
                    const response = await fetch('{sheet_url}');
                    const csvText = await response.text();
                    if (csvText.includes("<!DOCTYPE")) return;
                    const rows = csvText.split('\\n').slice(1);
                    const container = document.getElementById('live-data-container');
                    container.innerHTML = "";
                    
                    rows.forEach((line, index) => {{
                        if (!line.trim()) return;
                        const parts = line.split('|').map(p => p.trim());
                        if (parts.length >= 2) {{
                            const product = {{
                                id: index, name: parts[0], price: parts[1], desc: parts[2] || "",
                                img1: parts[3] || "{img_fallback}", img2: parts[4] || "", img3: parts[5] || ""
                            }};
                            currentProducts.push(product);
                            container.innerHTML += `
                            <div onclick="openProduct(${{index}})" class="product-card flex flex-col justify-between transition-all hover:scale-[1.02]">
                                <img src="${{product.img1}}" class="w-full h-48 object-cover mb-6 rounded-[2rem] bg-slate-100">
                                <div>
                                    <h3 class="text-xl font-black mb-2 uppercase" style="color:var(--p)">${{product.name}}</h3>
                                    <p class="font-black text-2xl mb-4" style="color:var(--s)">${{product.price}}</p>
                                    <p class="text-slate-400 text-[10px] font-black uppercase tracking-widest">Click for Details →</p>
                                </div>
                            </div>`;
                        }}
                    }});
                }} catch (e) {{ console.log("System Offline"); }}
            }}

            function openProduct(id) {{
                const p = currentProducts[id];
                const wa_msg = encodeURIComponent(`Hello {biz_name}, I am interested in ${{p.name}} (${{p.price}}).`);
                document.getElementById('m-title').innerText = p.name;
                document.getElementById('m-price').innerText = p.price;
                document.getElementById('m-desc').innerText = p.desc;
                document.getElementById('m-img-1').src = p.img1;
                document.getElementById('m-img-2').src = p.img2 || p.img1;
                document.getElementById('m-img-3').src = p.img3 || p.img1;
                document.getElementById('m-btn').href = "{wa_base_url}" + wa_msg;
                document.getElementById('modal').style.display = 'flex';
            }}
            function closeModal() {{ document.getElementById('modal').style.display = 'none'; }}
            window.onload = fetchLiveData;
            </script>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    {v_tag}
    <title>{title} | {biz_name}</title>
    <meta name="description" content="{desc}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family={h_font.replace(' ', '+')}:wght@700;900&family={b_font.replace(' ', '+')}:wght@400;700&display=swap" rel="stylesheet">
    <style>{theme_css}</style>
</head>
<body class="bg-white flex flex-col min-h-screen">
    <nav class="glass-nav sticky top-0 z-50 p-4 md:p-6 border-b">
        <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <a href="index.html">{logo_html}</a>
            <div class="flex items-center space-x-6 md:space-x-10 text-[10px] md:text-xs font-black uppercase tracking-widest">
                <a href="index.html">Home</a> <a href="about.html">About</a> <a href="contact.html">Contact</a>
                <a href="tel:{biz_phone}" class="btn-accent" style="padding: 0.5rem 1.5rem; font-size: 10px;">CALL NOW</a>
            </div>
        </div>
    </nav>
    <main class="flex-grow">{content}</main>
    <div id="modal" onclick="if(event.target == this) closeModal()">
        <div class="modal-content shadow-2xl">
            <div class="grid md:grid-cols-2">
                <div class="p-6 bg-slate-50 flex flex-col gap-4">
                    <img id="m-img-1" class="w-full h-64 object-cover rounded-3xl">
                    <div class="grid grid-cols-2 gap-4">
                        <img id="m-img-2" class="w-full h-32 object-cover rounded-2xl">
                        <img id="m-img-3" class="w-full h-32 object-cover rounded-2xl">
                    </div>
                </div>
                <div class="p-12 flex flex-col justify-center">
                    <h2 id="m-title" class="text-4xl font-black mb-4 uppercase"></h2>
                    <p id="m-price" class="text-3xl font-black mb-6" style="color:var(--s)"></p>
                    <p id="m-desc" class="text-slate-600 mb-10 leading-relaxed text-sm"></p>
                    <a id="m-btn" href="#" target="_blank" class="btn-accent w-full mb-4">CONFIRM BOOKING</a>
                    <button onclick="closeModal()" class="text-slate-400 text-xs font-bold uppercase tracking-widest underline">Close</button>
                </div>
            </div>
        </div>
    </div>
    <footer class="bg-slate-950 text-slate-400 py-20 px-10">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-2 gap-16">
            <div><h4 class="text-white text-3xl font-black mb-4 uppercase tracking-tighter">{biz_name}</h4><p class="text-sm">{biz_addr}</p></div>
            <div class="md:text-right">
                <p class="text-[10px] font-black uppercase opacity-30 underline italic">Built by Kaydiem Script Lab</p>
                <p class="text-lg font-bold text-white mt-4">{biz_phone}<br>{biz_email}</p>
            </div>
        </div>
    </footer>
    {dynamic_script}
</body></html>"""

    idx_content = f"""
    <section class="hero-mask px-6 text-center text-white">
        <div class="max-w-[1200px] mx-auto">
            <h1 class="hero-title mb-10 uppercase tracking-tighter leading-none">{hero_h}</h1>
            <p class="text-lg md:text-3xl font-light mb-16 max-w-4xl mx-auto opacity-90 leading-tight">{seo_d}</p>
            <a href="#inventory" class="btn-accent uppercase tracking-[0.4em] text-[10px] md:text-sm shadow-2xl">Explore Collection</a>
        </div>
    </section>
    <section id="inventory" class="py-32 px-6 max-w-[1440px] mx-auto text-center border-b">
        <h2 class="section-title mb-20 uppercase tracking-tighter">Exclusive Offers</h2>
        <div id="live-data-container" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8 text-left">
            <p class="p-20 text-center text-slate-400 animate-pulse">Syncing with Google Database...</p>
        </div>
    </section>
    <section class="bg-slate-50 py-32 px-6 border-y text-center">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-5xl font-black mb-12 uppercase tracking-tighter text-p" style="color:var(--p)">Luxury & Authority</h2>
            <p class="text-xl text-slate-600 mb-12 italic leading-relaxed">"Providing the 1st-class aesthetic foundation for Riyadh's vision. Unmatched quality, verified by decade-long excellence."</p>
            <a href="about.html" class="font-black text-xs uppercase underline decoration-p decoration-4 underline-offset-8" style="color:var(--p)">Read Full Story</a>
        </div>
    </section>
    """

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr("index.html", get_layout("Home", seo_d, idx_content, True))
        zf.writestr("about.html", get_layout("About", "History", f"<section class='max-w-7xl mx-auto py-32 px-6'><h1 class='legal-bold-title'>Our Heritage</h1><div class='text-xl leading-relaxed text-slate-700 legal-text'>{about_txt}</div></section>"))
        zf.writestr("privacy.html", get_layout("Privacy", "Legal", f"<div class='max-w-4xl mx-auto py-32 px-10'><h1 class='legal-bold-title'>Privacy Policy</h1><div class='text-lg legal-text'>{priv_body}</div></div>"))
        zf.writestr("terms.html", get_layout("Terms", "Legal", f"<div class='max-w-4xl mx-auto py-32 px-10'><h1 class='legal-bold-title'>Terms</h1><div class='text-lg legal-text'>{terms_body}</div></div>"))
        zf.writestr("contact.html", get_layout("Contact", "Location", f"<section class='max-w-[1440px] mx-auto py-32 px-6 text-center'><h1 class='legal-bold-title'>Connect</h1><div class='grid md:grid-cols-2 gap-16 text-left'><div class='bg-slate-950 p-12 md:p-24 text-white' style='border-radius: var(--radius)'><p class='text-4xl font-black mb-8'>{biz_phone}</p><p class='text-2xl mb-12 opacity-80'>{biz_addr}</p></div><div class='rounded-[3rem] overflow-hidden border shadow-2xl bg-slate-100'>{map_iframe}</div></div></section>"))
        zf.writestr("404.html", get_layout("404", "Not Found", "<div class='py-64 text-center'><h1 class='text-[120px] font-black uppercase tracking-widest'>404</h1></div>"))
        zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {prod_url}sitemap.xml")
        zf.writestr("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{prod_url}index.html</loc></url></urlset>')

    st.success("💎 TITAN SUPREME v8.1 STABLE DEPLOYED. Padding & Scaling Fixed.")
    st.download_button("📥 DOWNLOAD COMPLETE BIZ PACKAGE", zip_buf.getvalue(), f"{biz_name.lower()}_v8_1.zip")
