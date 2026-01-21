import streamlit as st
import zipfile
import io
import json
from datetime import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Kaydiem Titan v9.6 | Elite Web Architect", layout="wide", page_icon="💎")

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
    st.title("Titan v9.6 Studio")
    
    with st.expander("🎭 Architecture & DNA", expanded=True):
        layout_dna = st.selectbox("Design DNA", ["Industrial Titan", "Classic Royal", "Soft-UI", "Glass-Tech", "Brutalist", "Corporate Elite"])
        p_color = st.color_picker("Primary Brand Color", "#4A0E0E")
        s_color = st.color_picker("Accent/CTA Color", "#D4AF37")
        border_rad = st.select_slider("Corner Roundness", options=["0px", "4px", "12px", "24px", "40px", "60px"], value="40px")

    with st.expander("✍️ Typography Studio", expanded=True):
        h_font = st.selectbox("Heading Font", ["Playfair Display", "Oswald", "Montserrat", "Syncopate", "Inter"])
        b_font = st.selectbox("Body Font", ["Montserrat", "Inter", "Roboto", "Open Sans"])
        h_weight = st.select_slider("Heading Weight", options=["300", "400", "700", "900"], value="700")
        ls = st.select_slider("Letter Spacing", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="0.05em")

    gsc_tag = st.text_input("GSC Verification Tag")
    st.info("Built by Kaydiem Script Lab")

st.title("🏗️ Kaydiem Titan Supreme v9.6")

# --- 2. MULTI-TAB DATA COLLECTION ---
tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🖼️ Photos", "⚡ Live E-com", "🌟 Social Proof", "⚖️ Legal"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Red Hippo (The Planners)")
        biz_phone = st.text_input("Verified Phone", "+91 84540 02711")
        biz_email = st.text_input("Business Email", "events@redhippoplanners.in")
    with c2:
        biz_cat = st.text_input("Category", "Luxury Wedding Planner")
        biz_hours = st.text_input("Hours", "Mon-Sun: 10:00 - 19:00")
        prod_url = st.text_input("URL", "https://kani201012.github.io/site/")
    biz_logo = st.text_input("Logo URL (Direct Image Link)")
    biz_addr = st.text_area("Full Maps Physical Address")
    biz_areas = st.text_area("Service Areas (Comma separated)", "Vasant Kunj, Chhatarpur, South Delhi, Gurugram")
    map_iframe = st.text_area("Map Embed Code (<iframe>)")

with tabs[1]:
    hero_h = st.text_input("Hero Headline", "Crafting Dream Weddings: New Delhi's Premier Luxury Decorators")
    seo_d = st.text_input("Meta Description (160 Chars)")
    biz_key = st.text_input("SEO Keywords")
    biz_serv = st.text_area("Services (One per line)")
    about_txt = st.text_area("Our Story (800+ Words)", height=250)

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

if st.button("🚀 DEPLOY 100% ELITE BUSINESS ASSET"):
    
    img_h = c_hero if c_hero else "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&q=80&w=1600"
    img_f = c_feat if c_feat else "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800"
    img_g = c_gall if c_gall else "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?auto=format&fit=crop&q=80&w=1600"

    logo_h = f'<img src="{biz_logo}" alt="{biz_name}" class="h-8 md:h-14 w-auto object-contain">' if biz_logo else f'<span class="text-xl md:text-3xl font-black tracking-tighter" style="color:var(--p)">{biz_name}</span>'

    a_list = [a.strip() for a in biz_areas.split(",")]
    s_areas_json = json.dumps(a_list)
    wa_c = biz_phone.replace(" ", "").replace("+", "")

    theme_css = f"""
    :root {{ --p: {p_color}; --s: {s_color}; --radius: {border_rad}; }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; width: 100%; overflow-x: hidden; position: relative; }}
    body {{ font-family: '{b_font}', sans-serif; color: #0f172a; line-height: 1.6; background: #fff; }}
    h1, h2, h3 {{ font-family: '{h_font}', sans-serif; font-weight: {h_weight}; letter-spacing: {ls}; text-transform: uppercase; line-height: 1.1; overflow-wrap: break-word; }}
    
    .hero-title {{ font-size: clamp(1.4rem, 8vw, 95px); text-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
    .section-title {{ font-size: clamp(1.6rem, 6vw, 70px); color: var(--p); }}
    
    .btn-supreme {{ background: var(--s); color: white; padding: 1rem 2rem; border-radius: var(--radius); font-weight: 900; transition: all 0.4s; display: inline-block; text-align: center; border:none; box-shadow: 0 10px 20px -5px var(--s); }}
    .btn-supreme:hover {{ transform: translateY(-3px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); cursor: pointer; }}
    
    .glass-nav {{ background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(0,0,0,0.05); width: 100%; z-index: 9999; position: sticky; top: 0; }}
    
    .hero-mask {{ 
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.6)), url('{img_h}'); 
        background-size: cover; background-position: center; 
        min-height: 80vh; display: flex; align-items: center; justify-content: center; 
        width: 100%; margin: 0; padding: 60px 20px;
    }}
    
    /* RECTIFIED PRODUCT GRID */
    .product-card {{ background: white; border-radius: var(--radius); padding: 2.5rem; border: 1px solid #f1f5f9; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); transition: 0.3s; cursor: pointer; }}
    .product-card:hover {{ transform: scale(1.03); box-shadow: 0 30px 50px rgba(0,0,0,0.1); }}

    /* RECTIFIED FULL-SCREEN MODAL */
    #modal {{ display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.95); z-index: 100000; padding: 1.5rem; align-items: center; justify-content: center; overflow-y: auto; }}
    .modal-content {{ background: white; max-width: 1100px; width: 100%; border-radius: var(--radius); overflow: hidden; position: relative; display: flex; flex-direction: column; }}
    
    .legal-text {{ white-space: pre-wrap; word-wrap: break-word; font-size: 1.1rem; color: #334155; line-height: 1.8; }}
    .legal-bold-title {{ font-weight: 900; font-size: clamp(2rem, 6vw, 4.5rem); color: var(--p); margin-bottom: 2rem; text-transform: uppercase; line-height: 1; }}
    .wa-float {{ position: fixed; bottom: 25px; right: 25px; background: #25d366; color: white; width: 60px; height: 60px; border-radius: 50px; display: flex; align-items: center; justify-content: center; z-index: 99999; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
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
                    const csvText = await response.text();
                    if (csvText.includes("<!DOCTYPE")) return;

                    // Improved Pipe Parser
                    const rows = csvText.split('\\n').map(row => row.split('|')).slice(1);
                    const container = document.getElementById('live-data-container');
                    container.innerHTML = "";
                    
                    rows.forEach((parts, index) => {{
                        if (parts.length >= 2) {{
                            const p = {{ 
                                id: index, 
                                name: parts[0].trim(), 
                                price: parts[1].trim(), 
                                desc: (parts[2] || "").trim(), 
                                img1: (parts[3] || "{img_f}").trim(),
                                img2: (parts[4] || "").trim(),
                                img3: (parts[5] || "").trim()
                            }};
                            currentProducts.push(p);
                            container.innerHTML += `
                            <div onclick="openProduct(${{index}})" class="product-card flex flex-col justify-between">
                                <img src="${{p.img1}}" class="w-full h-56 object-cover mb-8 rounded-[2rem] bg-slate-50" onerror="this.src='{img_f}'">
                                <div>
                                    <h3 class="text-2xl font-black mb-2 uppercase text-p" style="color:var(--p)">${{p.name}}</h3>
                                    <p class="font-black text-2xl mb-6 text-s" style="color:var(--s)">${{p.price}}</p>
                                    <p class="text-slate-400 text-[10px] font-black uppercase tracking-widest italic underline decoration-slate-100 underline-offset-4">Learn More →</p>
                                </div>
                            </div>`;
                        }}
                    }});
                }} catch (e) {{ console.log("Offline"); }}
            }}

            function openProduct(id) {{
                const p = currentProducts[id];
                document.getElementById('m-title').innerText = p.name;
                document.getElementById('m-price').innerText = p.price;
                document.getElementById('m-desc').innerText = p.desc;
                document.getElementById('m-img-1').src = p.img1;
                document.getElementById('m-img-2').src = p.img2 || p.img1;
                document.getElementById('m-img-3').src = p.img3 || p.img1;
                document.getElementById('m-wa').href = "https://wa.me/{wa_c}?text=" + encodeURIComponent("Hello {biz_name}, I am interested in: " + p.name);
                document.getElementById('modal').style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }}
            function closeModal() {{ 
                document.getElementById('modal').style.display = 'none'; 
                document.body.style.overflow = 'auto';
            }}
            window.onload = fetchLiveData;
            </script>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    {v_tag}
    <title>{title} | {biz_name}</title>
    <meta name="description" content="{desc}"><meta name="keywords" content="{biz_key}">
    <link rel="canonical" href="{prod_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family={h_font.replace(' ', '+')}:wght@700;900&family={b_font.replace(' ', '+')}:wght@400;700&display=swap" rel="stylesheet">
    <style>{theme_css}</style>
    <script type="application/ld+json">
    {{ "@context": "https://schema.org", "@type": "LocalBusiness", "name": "{biz_name}", "address": {{ "@type": "PostalAddress", "streetAddress": "{biz_addr}" }}, "telephone": "{biz_phone}", "areaServed": {s_areas_json} }}
    </script>
</head>
<body class="bg-white">
    <nav class="glass-nav p-4 md:p-6 shadow-sm">
        <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <a href="index.html">{logo_h}</a>
            <div class="flex items-center space-x-6 md:space-x-12 text-[10px] md:text-xs font-black uppercase tracking-widest text-slate-600">
                <a href="index.html" class="hover:text-blue-600">Home</a> <a href="about.html">About</a> <a href="contact.html">Contact</a>
                <a href="tel:{biz_phone}" class="bg-slate-900 text-white px-5 py-2 rounded-full font-bold">Call</a>
            </div>
        </div>
    </nav>
    <main class="flex-grow">{content}</main>
    
    <div id="modal" onclick="if(event.target == this) closeModal()">
        <div class="modal-content shadow-2xl animate-in zoom-in duration-300">
            <div class="grid md:grid-cols-2">
                <div class="p-6 bg-slate-50 flex flex-col gap-4">
                    <img id="m-img-1" class="w-full h-80 object-cover rounded-[2.5rem] shadow-xl">
                    <div class="grid grid-cols-2 gap-4">
                        <img id="m-img-2" class="w-full h-32 object-cover rounded-2xl" onerror="this.style.display='none'">
                        <img id="m-img-3" class="w-full h-32 object-cover rounded-2xl" onerror="this.style.display='none'">
                    </div>
                </div>
                <div class="p-12 flex flex-col justify-center text-left">
                    <h2 id="m-title" class="text-4xl font-black mb-4 uppercase text-p" style="color:var(--p)"></h2>
                    <p id="m-price" class="text-3xl font-black mb-8 text-s" style="color:var(--s)"></p>
                    <p id="m-desc" class="text-slate-600 mb-12 leading-relaxed text-lg"></p>
                    <a id="m-wa" href="#" target="_blank" class="btn-supreme w-full uppercase tracking-widest shadow-2xl">Book Appointment</a>
                    <button onclick="closeModal()" class="text-xs font-black uppercase tracking-widest opacity-30 mt-8 underline">Close Window</button>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-slate-950 text-slate-400 py-24 px-10 border-t border-slate-900">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-4 gap-16 text-left">
            <div class="col-span-2">
                <h4 class="text-white text-3xl font-black mb-8 uppercase tracking-tighter uppercase">{biz_name}</h4>
                <p class="text-sm leading-relaxed mb-10 max-w-md">{biz_addr}</p>
                <div class="bg-slate-900/50 p-6 border border-slate-800 rounded-3xl">
                    <h5 class="text-white text-[10px] font-black uppercase tracking-widest mb-4 opacity-50">Verified Service Coverage</h5>
                    <div class="flex flex-wrap gap-2">{"".join([f'<span class="bg-slate-800 text-[10px] px-3 py-1 rounded-full uppercase font-bold text-white tracking-widest border border-slate-700">{a}</span>' for a in a_list])}</div>
                </div>
                <p class="text-[10px] mt-10 opacity-30 uppercase font-black tracking-widest italic tracking-widest underline decoration-white underline-offset-8 decoration-2">Architected By Kaydiem Script Lab</p>
            </div>
            <div><h4 class="text-white font-bold mb-8 uppercase text-xs tracking-widest">Navigation</h4><ul class="space-y-4 text-sm font-bold uppercase tracking-widest"><li><a href="privacy.html" class="hover:text-white transition">Privacy</a></li><li><a href="terms.html" class="hover:text-white transition">Terms</a></li></ul></div>
            <div><h4 class="text-white font-bold mb-8 uppercase text-xs tracking-widest text-brand" style="color:var(--s)">Direct Connect</h4><p class="text-lg font-bold text-white leading-loose">{biz_phone}<br>{biz_email}</p></div>
        </div>
    </footer>
    {dynamic_script}
</body></html>"""

    # --- ENHANCED INDEX CONTENT ---
    serv_html = "".join([f'<div class="bg-slate-50 p-12 rounded-[2.5rem] border border-slate-100 shadow-xl hover:scale-[1.02] transition-transform"><h3 class="text-2xl font-black mb-4 uppercase" style="color:var(--p)">{s.strip()}</h3><p class="text-slate-500 text-sm leading-relaxed font-bold uppercase tracking-tight italic">Verified solution for {biz_name}.</p></div>' for s in biz_serv.splitlines() if s.strip()])
    t_html = "".join([f'<div class="p-10 bg-slate-50 rounded-[3rem] border border-slate-100 italic text-xl shadow-inner mb-8">"{t.split("|")[1].strip()}"<br><span class="font-black not-italic text-sm block mt-6 uppercase tracking-widest text-brand" style="color:var(--p)">— {t.split("|")[0].strip()} <span class="text-emerald-500 font-black ml-2">● Partner</span></span></div>' for t in t_data.splitlines() if "|" in t])
    f_html = "".join([f'<details class="mb-6 bg-white p-6 rounded-2xl border border-slate-100 cursor-pointer shadow-sm"><summary class="font-black text-lg uppercase tracking-tight">{f.split("?")[0].strip()}?</summary><p class="mt-4 text-slate-600 leading-relaxed font-medium">{f.split("?")[1].strip()}</p></details>' for f in f_data.splitlines() if "?" in f])

    d_section = f"""<section class="py-32 px-6 max-w-[1440px] mx-auto text-center border-b"><h2 class="section-title mb-20 uppercase tracking-tighter" style="color:var(--p)">Verified Packages</h2><div id="live-data-container" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-10 text-left"><p class="p-20 text-center text-slate-400 font-bold animate-pulse uppercase tracking-widest">Connecting to Data Hub...</p></div></section>""" if s_url else ""

    idx_content = f"""
    <section class="hero-mask px-6 text-center text-white">
        <div class="max-w-[1200px] mx-auto">
            <h1 class="hero-title mb-10 uppercase tracking-tighter leading-none">{h_head}</h1>
            <p class="text-lg md:text-3xl font-light mb-16 max-w-4xl mx-auto opacity-90 leading-tight">{s_desc}</p>
            <a href="tel:{b_phone}" class="btn-supreme uppercase tracking-[0.4em] text-[10px] md:text-sm shadow-2xl" style="background:var(--p)">Consult Now</a>
        </div>
    </section>
    <section class="max-w-[1440px] mx-auto py-24 px-6 text-center border-b">
        <h2 class="section-title mb-20 uppercase tracking-tighter" style="color:var(--p)">Core Specialties</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-10 text-left">{serv_html}</div>
    </section>
    {d_section}
    <section class="bg-slate-50 py-32 px-6 border-y text-left">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-2 gap-24 items-center">
            <img src="{img_f}" class="shadow-2xl" style="border-radius: var(--radius)">
            <div>
                <h2 class="text-5xl font-black mb-12 uppercase tracking-tighter leading-none" style="color:var(--p)">Verified Heritage</h2>
                <p class="text-2xl text-slate-600 mb-12 leading-relaxed italic">"Supplying the engineering foundation for the 2026 city landscape. Precision execution, certified safety, and direct quality oversight."</p>
                <a href="about.html" class="btn-supreme text-xs tracking-widest uppercase">Our Story</a>
            </div>
        </div>
    </section>
    <section class="py-32 px-6 max-w-7xl mx-auto text-center"><div class="grid md:grid-cols-2 gap-24 text-left"><div><h2 class="text-4xl font-black mb-16 uppercase tracking-tighter" style="color:var(--p)">Success</h2>{t_html}</div><div><h2 class="text-4xl font-black mb-16 uppercase tracking-tighter" style="color:var(--p)">Insights</h2>{f_html}</div></div></section>
    """

    # --- ZIP OUTPUT ---
    z_b = io.BytesIO()
    with zipfile.ZipFile(z_b, "a", zipfile.ZIP_DEFLATED, False) as z_f:
        z_f.writestr("index.html", get_layout("Home", s_desc, idx_content, True))
        z_f.writestr("about.html", get_layout("About", "History", f"<section class='max-w-7xl mx-auto py-40 px-6'><h1 class='legal-bold-title'>About Our Heritage</h1><div class='text-xl md:text-2xl leading-relaxed text-slate-700 legal-text'>{a_txt}</div><img src='{img_g}' class='mt-20 w-full h-[600px] object-cover shadow-2xl' style='border-radius: var(--radius)'></section>"))
        z_f.writestr("contact.html", get_layout("Contact", "Location", f"<section class='max-w-[1440px] mx-auto py-32 px-6 text-center'><h1 class='legal-bold-title uppercase'>Technical Hub</h1><div class='grid md:grid-cols-2 gap-16 text-left'><div class='bg-slate-950 p-12 md:p-24 text-white' style='border-radius: var(--radius)'><p class='text-4xl font-black mb-8 text-white'>{b_phone}</p><p class='text-2xl mb-12 opacity-80'>{b_addr}</p></div><div class='rounded-[3rem] overflow-hidden border shadow-2xl bg-slate-100' style='min-height:300px'>{b_map}</div></div></section>"))
        z_f.writestr("privacy.html", get_layout("Privacy", "Legal", f"<div class='max-w-4xl mx-auto py-40 px-6'><h1 class='legal-bold-title'>Privacy Policy</h1><div class='text-lg legal-text'>{p_body}</div></div>"))
        z_f.writestr("terms.html", get_layout("Terms", "Legal", f"<div class='max-w-4xl mx-auto py-40 px-6'><h1 class='legal-bold-title'>Terms & Conditions</h1><div class='text-lg legal-text'>{t_body}</div></div>"))
        z_f.writestr("404.html", get_layout("404", "Not Found", "<div class='py-64 text-center'><h1 class='text-[120px] font-black uppercase text-slate-200'>404</h1></div>"))
        z_f.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {b_url}sitemap.xml")
        z_f.writestr("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{b_url}index.html</loc></url><url><loc>{b_url}about.html</loc></url></urlset>')

    st.success("💎 TITAN SUPREME v9.6 RECTIFIED. Full-Screen Modal and Data Logic fixed.")
    st.download_button("📥 DOWNLOAD ENTERPRISE BIZ PACKAGE", z_b.getvalue(), f"{b_name.lower().replace(' ', '_')}_v9_6.zip")
