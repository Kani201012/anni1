import streamlit as st
import zipfile
import io
import json
from datetime import datetime

# --- 1. DESIGN STUDIO CONFIGURATION ---
st.set_page_config(page_title="Kaydiem Titan v9.5 | Pixel-Perfect Architect", layout="wide", page_icon="💎")

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
    st.title("Titan v9.5 Studio")
    
    with st.expander("🎭 1. Layout & Architecture", expanded=True):
        layout_dna = st.selectbox("Design DNA", ["Industrial Titan", "Classic Royal", "Soft-UI", "Glass-Tech", "Brutalist", "Corporate Elite"])
        p_color = st.color_picker("Primary Brand Color", "#4A0E0E")
        s_color = st.color_picker("Accent/CTA Color", "#D4AF37")
        border_rad = st.select_slider("Corner Roundness", options=["0px", "4px", "12px", "24px", "40px", "60px"], value="40px")

    with st.expander("✍️ 2. Typography Studio", expanded=True):
        h_font = st.selectbox("Heading Font", ["Playfair Display", "Oswald", "Montserrat", "Syncopate", "Inter"])
        b_font = st.selectbox("Body Font", ["Montserrat", "Inter", "Roboto", "Open Sans"])
        h_weight = st.select_slider("Heading Weight", options=["300", "400", "700", "900"], value="700")
        ls = st.select_slider("Letter Spacing", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="0.05em")

    gsc_tag = st.text_input("GSC Verification Tag")
    st.info("Built by Kaydiem Script Lab")

st.title("🏗️ Kaydiem Titan Supreme v9.5")

# --- 2. MULTI-TAB DATA COLLECTION ---
tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🖼️ Photos", "⚡ Live E-com", "🌟 Social Proof", "⚖️ Legal"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        b_name = st.text_input("Business Name", "Red Hippo (The Planners)")
        b_phone = st.text_input("Verified Phone", "+91 84540 02711")
        b_email = st.text_input("Business Email", "events@redhippoplanners.in")
    with c2:
        b_cat = st.text_input("Category", "Luxury Wedding Planner")
        b_hours = st.text_input("Hours", "Mon-Sun: 10:00 - 19:00")
        b_url = st.text_input("URL", "https://kani201012.github.io/site/")
    b_logo = st.text_input("Logo Image URL")
    b_addr = st.text_area("Full Maps Physical Address")
    b_areas = st.text_area("Service Areas (Comma separated)", "Vasant Kunj, Chhatarpur, South Delhi, Gurugram")
    b_map = st.text_area("Map Embed Code (<iframe>)")

with tabs[1]:
    h_head = st.text_input("Hero Headline", "Crafting Dream Weddings: New Delhi's Premier Luxury Decorators")
    s_desc = st.text_input("Meta Description (160 Chars)")
    b_key = st.text_input("SEO Keywords")
    b_serv = st.text_area("Services (One per line)")
    a_txt = st.text_area("Our Story (800+ Words)", height=250)

with tabs[2]:
    st.header("📸 Photo Manager")
    c_hero = st.text_input("Main Hero Image URL")
    c_feat = st.text_input("Feature Image URL")
    c_gall = st.text_input("Gallery Image URL")

with tabs[3]:
    st.header("⚡ Headless Live Data")
    s_url = st.text_input("Published CSV URL")

with tabs[4]:
    t_data = st.text_area("Testimonials (Name | Quote)")
    f_data = st.text_area("FAQ (Question? ? Answer)")

with tabs[5]:
    st.header("⚖️ Legal Compliance Hub")
    p_body = st.text_area("Privacy Policy Content", height=300)
    t_body = st.text_area("Terms Content", height=300)

# --- 3. THE RECTIFIED ENGINE CORE ---

if st.button("🚀 DEPLOY 100% PIXEL-PERFECT ASSET"):
    
    img_h = c_hero if c_hero else "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&q=80&w=1600"
    img_f = c_feat if c_feat else "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800"
    img_g = c_gall if c_gall else "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?auto=format&fit=crop&q=80&w=1600"

    logo_h = f'<img src="{b_logo}" alt="{b_name}" class="h-8 md:h-14 w-auto object-contain">' if b_logo else f'<span class="text-lg md:text-2xl font-black tracking-tighter" style="color:var(--p)">{b_name}</span>'

    a_list = [a.strip() for a in b_areas.split(",")]
    s_areas_json = json.dumps(a_list)
    wa_c = b_phone.replace(" ", "").replace("+", "")

    theme_css = f"""
    :root {{ --p: {p_color}; --s: {s_color}; --radius: {border_rad}; }}
    
    /* RESET & OVERFLOW PROTECTION */
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; width: 100%; overflow-x: hidden; position: relative; }}
    
    body {{ font-family: '{b_font}', sans-serif; color: #0f172a; line-height: 1.6; background: #fff; }}
    h1, h2, h3 {{ font-family: '{h_font}', sans-serif; font-weight: {h_weight}; letter-spacing: {ls}; text-transform: uppercase; line-height: 1.1; overflow-wrap: break-word; word-break: break-word; }}
    
    .hero-title {{ font-size: clamp(1.2rem, 7vw, 85px); text-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
    .section-title {{ font-size: clamp(1.5rem, 5vw, 65px); color: var(--p); }}
    
    .btn-supreme {{ background: var(--s); color: white; padding: 1rem 2rem; border-radius: var(--radius); font-weight: 900; transition: all 0.3s; display: inline-block; text-align: center; border:none; box-shadow: 0 10px 20px -5px var(--s); }}
    
    .glass-nav {{ background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(0,0,0,0.05); width: 100%; z-index: 9999; position: sticky; top: 0; }}
    
    /* RECTIFIED HERO SECTION - TRUE FULL WIDTH */
    .hero-mask {{ 
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.6)), url('{img_h}'); 
        background-size: cover; background-position: center; 
        min-height: 75vh; display: flex; align-items: center; justify-content: center; 
        width: 100%; padding: 40px 20px;
    }}
    
    .legal-text {{ white-space: pre-wrap; word-wrap: break-word; font-size: 1rem; color: #334155; line-height: 1.8; }}
    .legal-bold-title {{ font-weight: 900; font-size: clamp(1.8rem, 5vw, 4rem); color: var(--p); margin-bottom: 1.5rem; text-transform: uppercase; }}
    .wa-float {{ position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; width: 55px; height: 55px; border-radius: 50px; display: flex; align-items: center; justify-content: center; z-index: 99999; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
    """

    def get_layout(title, desc, content, is_index=False):
        v_tag = f'<meta name="google-site-verification" content="{gsc_tag}">' if (is_index and gsc_tag) else ""
        
        dynamic_script = ""
        if is_index and s_url:
            dynamic_script = f"""
            <script>
            let currentProducts = [];
            async function fetchLiveData() {{
                try {{
                    const response = await fetch('{s_url}');
                    const csv = await response.text();
                    if (csv.trim().startsWith("<!DOCTYPE")) return;
                    const rows = csv.split('\\n').map(row => row.split(',')).slice(1);
                    const container = document.getElementById('live-data-container');
                    container.innerHTML = "";
                    rows.forEach((parts, index) => {{
                        if (parts.length >= 2) {{
                            const p = {{ id: index, name: parts[0].replace(/"/g, "").trim(), price: parts[1].replace(/"/g, "").trim(), desc: (parts[2] || "").replace(/"/g, "").trim(), img1: (parts[3] || "{img_f}").trim() }};
                            currentProducts.push(p);
                            container.innerHTML += `
                            <div onclick="openProduct(${{index}})" class="product-card flex flex-col justify-between">
                                <img src="${{p.img1}}" class="w-full h-40 object-cover mb-4 rounded-[1.5rem] bg-slate-50">
                                <div>
                                    <h3 class="text-lg font-black mb-1 uppercase" style="color:var(--p)">${{p.name}}</h3>
                                    <p class="font-black text-xl mb-4" style="color:var(--s)">${{p.price}}</p>
                                </div>
                            </div>`;
                        }}
                    }});
                }} catch (e) {{ console.log("Connection fail"); }}
            }}
            function openProduct(id) {{
                const p = currentProducts[id];
                document.getElementById('m-title').innerText = p.name;
                document.getElementById('m-price').innerText = p.price;
                document.getElementById('m-desc').innerText = p.desc;
                document.getElementById('m-img-1').src = p.img1;
                document.getElementById('m-wa').href = "https://wa.me/{wa_c}?text=" + encodeURIComponent("Hello, I am interested in " + p.name);
                document.getElementById('modal').style.display = 'flex';
            }}
            window.onload = fetchLiveData;
            </script>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    {v_tag}
    <title>{title} | {b_name}</title>
    <meta name="description" content="{desc}"><meta name="keywords" content="{b_key}">
    <link rel="canonical" href="{b_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family={h_font.replace(' ', '+')}:wght@700;900&family={b_font.replace(' ', '+')}:wght@400;700&display=swap" rel="stylesheet">
    <style>{theme_css}</style>
    <script type="application/ld+json">
    {{ "@context": "https://schema.org", "@type": "LocalBusiness", "name": "{b_name}", "address": {{ "@type": "PostalAddress", "streetAddress": "{b_addr}" }}, "telephone": "{b_phone}", "areaServed": {s_areas_json} }}
    </script>
</head>
<body class="bg-white">
    <nav class="glass-nav p-4 md:p-6 shadow-sm">
        <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <a href="index.html">{logo_h}</a>
            <div class="flex items-center space-x-4 md:space-x-12 text-[9px] md:text-xs font-black uppercase tracking-widest text-slate-600">
                <a href="index.html">Home</a> <a href="about.html">About</a> <a href="contact.html">Contact</a>
                <a href="tel:{b_phone}" class="bg-slate-900 text-white px-4 py-2 rounded-full font-bold">Call</a>
            </div>
        </div>
    </nav>
    <main class="flex-grow">{content}</main>
    
    <div id="modal" onclick="if(event.target == this) this.style.display='none'">
        <div class="modal-content shadow-2xl">
            <div class="grid md:grid-cols-2">
                <div class="p-4 bg-slate-50 flex flex-col gap-4">
                    <img id="m-img-1" class="w-full h-48 object-cover rounded-[1.5rem] shadow-xl">
                </div>
                <div class="p-8 flex flex-col justify-center text-left">
                    <h2 id="m-title" class="text-2xl font-black mb-2 uppercase text-p" style="color:var(--p)"></h2>
                    <p id="m-price" class="text-xl font-black mb-4 text-s" style="color:var(--s)"></p>
                    <p id="m-desc" class="text-slate-600 mb-8 leading-relaxed text-xs"></p>
                    <a id="m-wa" href="#" target="_blank" class="btn-supreme w-full text-sm uppercase tracking-widest">Confirm</a>
                </div>
            </div>
        </div>
    </div>

    <a href="https://wa.me/{wa_c}" class="wa-float" target="_blank"><svg style="width:30px;height:30px" viewBox="0 0 24 24"><path fill="currentColor" d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91c0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23c-1.48 0-2.93-.39-4.19-1.15l-.3-.17l-3.12.82l.83-3.04l-.2-.32a8.188 8.188 0 0 1-1.26-4.38c.01-4.54 3.7-8.24 8.25-8.24m-3.53 3.16c-.13 0-.35.05-.54.26c-.19.2-.72.7-.72 1.72s.73 2.01.83 2.14c.1.13 1.44 2.19 3.48 3.07c.49.21.87.33 1.16.43c.49.16.94.13 1.29.08c.4-.06 1.21-.5 1.38-.98c.17-.48.17-.89.12-.98c-.05-.09-.18-.13-.37-.23c-.19-.1-.1.13-.1.13s-1.13-.56-1.32-.66c-.19-.1-.32-.15-.45.05c-.13.2-.51.65-.62.78c-.11.13-.23.15-.42.05c-.19-.1-.8-.3-1.53-.94c-.57-.5-1.02-1.12-1.21-1.45c-.11-.19-.01-.29.09-.38c.09-.08.19-.23.29-.34c.1-.11.13-.19.19-.32c.06-.13.03-.24-.01-.34c-.05-.1-.45-1.08-.62-1.48c-.16-.4-.36-.34-.51-.35c-.11-.01-.25-.01-.4-.01Z"/></svg></a>

    <footer class="bg-slate-950 text-slate-400 py-16 px-6 border-t border-slate-900 overflow-hidden">
        <div class="max-w-7xl mx-auto flex flex-col gap-12 text-left">
            <div>
                <h4 class="text-white text-2xl font-black mb-6 uppercase tracking-tighter uppercase">{b_name}</h4>
                <p class="text-xs leading-relaxed mb-10 max-w-xs">{b_addr}</p>
                <div class="p-6 border border-slate-800 rounded-3xl w-full">
                    <h5 class="text-white text-[10px] font-black uppercase tracking-widest mb-4 opacity-50">Verified Coverage</h5>
                    <div class="flex flex-wrap gap-2">{"".join([f'<span class="bg-slate-800 text-[9px] px-2 py-1 rounded-full uppercase font-bold text-white border border-slate-700">{a}</span>' for a in a_list])}</div>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-8">
                <div><h4 class="text-white font-bold mb-4 uppercase text-[10px] tracking-widest">Policy</h4><ul class="space-y-2 text-[10px] uppercase"><li><a href="privacy.html">Privacy</a></li><li><a href="terms.html">Terms</a></li></ul></div>
                <div><h4 class="text-white font-bold mb-4 uppercase text-[10px] tracking-widest">Support</h4><p class="text-[10px] font-bold text-white leading-loose">{b_phone}<br>{b_email}</p></div>
            </div>
        </div>
    </footer>
    {dynamic_script}
</body></html>"""

    # --- ENHANCED INDEX CONTENT ---
    serv_html = "".join([f'<div class="bg-slate-50 p-8 rounded-[2rem] border border-slate-100 shadow-xl"><h3 class="text-lg font-black mb-2 uppercase" style="color:var(--p)">{s.strip()}</h3><p class="text-slate-500 text-xs font-bold uppercase tracking-tight italic">Verified solution for {b_name}.</p></div>' for s in b_serv.splitlines() if s.strip()])
    t_cards = "".join([f'<div class="p-8 bg-slate-50 rounded-[2.5rem] border border-slate-100 italic text-lg shadow-inner mb-6">"{t.split("|")[1].strip()}"<br><span class="font-black not-italic text-xs block mt-4 uppercase tracking-widest text-brand" style="color:var(--p)">— {t.split("|")[0].strip()}</span></div>' for t in t_data.splitlines() if "|" in t])
    f_cards = "".join([f'<details class="mb-4 bg-white p-6 rounded-2xl border border-slate-100 cursor-pointer shadow-sm"><summary class="font-black text-sm uppercase tracking-tight">{f.split("?")[0].strip()}?</summary><p class="mt-4 text-slate-600 leading-relaxed font-medium text-xs">{f.split("?")[1].strip()}</p></details>' for f in f_data.splitlines() if "?" in f])

    d_section = f"""<section class="py-20 px-6 max-w-[1440px] mx-auto text-center border-b"><h2 class="section-title mb-16 uppercase tracking-tighter" style="color:var(--p)">Available Packages</h2><div id="live-data-container" class="grid grid-cols-1 md:grid-cols-4 gap-6 text-left"></div></section>""" if s_url else ""

    idx_content = f"""
    <section class="hero-mask px-4 text-center text-white">
        <div class="max-w-[1000px] mx-auto">
            <h1 class="hero-title mb-8 uppercase tracking-tighter leading-none">{h_head}</h1>
            <p class="text-sm md:text-2xl font-light mb-10 max-w-2xl mx-auto opacity-90 leading-snug">{s_desc}</p>
            <a href="tel:{b_phone}" class="btn-supreme uppercase tracking-[0.3em] text-[10px] md:text-sm shadow-2xl" style="background:var(--p)">Direct Booking</a>
        </div>
    </section>
    <section class="max-w-[1440px] mx-auto py-16 px-6 text-center border-b">
        <h2 class="section-title mb-16 uppercase tracking-tighter" style="color:var(--p)">Our Services</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">{serv_html}</div>
    </section>
    {d_section}
    <section class="bg-slate-50 py-20 px-6 border-y text-left">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-2 gap-16 items-center">
            <img src="{img_f}" class="shadow-2xl" style="border-radius: var(--radius)">
            <div>
                <h2 class="text-3xl font-black mb-8 uppercase tracking-tighter leading-none" style="color:var(--p)">Verified 2026 Authority</h2>
                <p class="text-sm text-slate-600 mb-8 leading-relaxed italic">"Transforming industrial and luxury landscapes since inception. Quality verified by engineering excellence."</p>
                <a href="about.html" class="btn-supreme text-[10px] tracking-widest uppercase">Full Story</a>
            </div>
        </div>
    </section>
    <section class="py-20 px-6 max-w-7xl mx-auto text-center"><div class="grid md:grid-cols-2 gap-16 text-left"><div><h2 class="text-2xl font-black mb-10 uppercase tracking-tighter" style="color:var(--p)">Trust</h2>{t_cards}</div><div><h2 class="text-2xl font-black mb-10 uppercase tracking-tighter" style="color:var(--p)">FAQ</h2>{f_cards}</div></div></section>
    """

    # --- ZIP OUTPUT ---
    z_b = io.BytesIO()
    with zipfile.ZipFile(z_b, "a", zipfile.ZIP_DEFLATED, False) as z_f:
        z_f.writestr("index.html", get_layout("Home", s_desc, idx_content, True))
        z_f.writestr("about.html", get_layout("About", "History", f"<section class='max-w-7xl mx-auto py-24 px-6'><h1 class='legal-bold-title'>About Us</h1><div class='text-sm md:text-lg leading-relaxed text-slate-700 legal-text'>{a_txt}</div><img src='{img_g}' class='mt-10 w-full h-[400px] object-cover shadow-2xl' style='border-radius: var(--radius)'></section>"))
        z_f.writestr("contact.html", get_layout("Contact", "Location", f"<section class='max-w-[1440px] mx-auto py-24 px-6 text-center'><h1 class='legal-bold-title'>Contact Us</h1><div class='grid md:grid-cols-2 gap-12 text-left'><div class='bg-slate-950 p-8 md:p-16 text-white' style='border-radius: var(--radius)'><p class='text-2xl font-black mb-4 text-white'>{b_phone}</p><p class='text-sm mb-10 opacity-80'>{b_addr}</p><a href='tel:{b_phone}' class='btn-supreme w-full'>BOOK CONSULTATION</a></div><div class='rounded-[2rem] overflow-hidden border shadow-2xl bg-slate-100'>{b_map}</div></div></section>"))
        z_f.writestr("privacy.html", get_layout("Privacy", "Legal", f"<div class='max-w-4xl mx-auto py-24 px-6'><h1 class='legal-bold-title uppercase'>Privacy Policy</h1><div class='legal-text'>{p_body}</div></div>"))
        z_f.writestr("terms.html", get_layout("Terms", "Legal", f"<div class='max-w-4xl mx-auto py-24 px-6'><h1 class='legal-bold-title uppercase'>Terms</h1><div class='legal-text'>{t_body}</div></div>"))
        z_f.writestr("404.html", get_layout("404", "Not Found", "<div class='py-48 text-center'><h1 class='text-[100px] font-black uppercase text-slate-200'>404</h1></div>"))
        z_f.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {b_url}sitemap.xml")
        z_f.writestr("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{b_url}index.html</loc></url><url><loc>{b_url}about.html</loc></url></urlset>')

    st.success("💎 TITAN SUPREME v9.5 DEPLOYED. Verified Pixel-Perfect on Mobile.")
    st.download_button("📥 DOWNLOAD ENTERPRISE BIZ PACKAGE", z_b.getvalue(), f"{b_name.lower().replace(' ', '_')}_v9_5.zip")
