import streamlit as st
import zipfile
import io
import json
from datetime import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Kaydiem Titan v9.9 | Audited Master Build", layout="wide", page_icon="💎")

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
    st.title("Titan v9.9 Studio")
    
    with st.expander("🎭 1. Layout & DNA", expanded=True):
        layout_dna = st.selectbox("Design DNA", ["Industrial Titan", "Classic Royal", "Soft-UI", "Glass-Tech", "Brutalist", "Corporate Elite"])
        p_color = st.color_picker("Primary Brand Color", "#4A0E0E")
        s_color = st.color_picker("Accent/CTA Color", "#D4AF37")
        border_rad = st.select_slider("Corner Roundness", options=["0px", "4px", "12px", "24px", "40px", "60px"], value="40px")

    with st.expander("✍️ 2. Typography Studio", expanded=True):
        h_font = st.selectbox("Heading Font", ["Playfair Display", "Oswald", "Montserrat", "Syncopate", "Inter"])
        b_font = st.selectbox("Body Font", ["Montserrat", "Inter", "Roboto", "Open Sans"])
        h_weight = st.select_slider("Heading Weight", options=["300", "400", "700", "900"], value="700")
        ls = st.select_slider("Letter Spacing", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="0.05em")

    inp_gsc_tag = st.text_input("GSC Verification Tag")
    st.info("Technical Authority: Kaydiem Script Lab")

st.title("🏗️ Kaydiem Titan Supreme v9.9")

# --- 2. MULTI-TAB DATA COLLECTION (SYNCHRONIZED NAMES) ---
tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🖼️ Photo Manager", "⚡ Live E-com", "🌟 Social Proof", "⚖️ Legal"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        inp_name = st.text_input("Business Name (NAP)", "Red Hippo (The Planners)")
        inp_phone = st.text_input("Verified Phone Number", "+91 84540 02711")
        inp_email = st.text_input("Business Email Address", "events@redhippoplanners.in")
    with c2:
        inp_cat = st.text_input("Business Category", "Luxury Wedding Planner")
        inp_hours = st.text_input("Opening Hours", "Mon-Sun: 10:00 - 19:00")
        inp_url = st.text_input("Production URL (Include /)", "https://kani201012.github.io/site/")
    inp_logo = st.text_input("Logo Image URL (Direct Link)")
    inp_addr = st.text_area("Full Maps Physical Address")
    inp_areas = st.text_area("Service Areas (Comma separated)", "Vasant Kunj, Chhatarpur, South Delhi")
    inp_map = st.text_area("Map Embed HTML Code (<iframe>)")

with tabs[1]:
    inp_hero_h = st.text_input("Hero Headline", "Crafting Dream Weddings")
    inp_meta_d = st.text_input("Meta Description (160 Chars)", "Best luxury wedding decorators in Delhi.")
    inp_keywords = st.text_input("SEO Keywords (Comma Separated)")
    inp_serv_list = st.text_area("Services Listing (One per line)")
    inp_about_txt = st.text_area("Our Story (800+ Words for E-E-A-T)", height=250)

with tabs[2]:
    st.header("📸 Asset Manager")
    inp_img_hero = st.text_input("Main Hero Image URL")
    inp_img_feat = st.text_input("Feature Section Image URL")
    inp_img_gall = st.text_input("Gallery/About Image URL")

with tabs[3]:
    st.header("⚡ Live Data Feed (Google Sheets CSV)")
    inp_sheet_url = st.text_input("Published CSV Link (Standard Comma-Separated)")

with tabs[4]:
    st.header("🌟 Trust Signals")
    inp_testi = st.text_area("Client Testimonials (Format: Name | Quote)")
    inp_faqs = st.text_area("FAQ (Format: Question? ? Answer)")

with tabs[5]:
    st.header("⚖️ Legal Compliance Hub")
    inp_priv_body = st.text_area("Privacy Policy Content", height=300)
    inp_terms_body = st.text_area("Terms & Conditions Content", height=300)

# --- 3. THE SUPREME TITAN ENGINE ---

if st.button("🚀 DEPLOY 100% STABLE BUSINESS ASSET"):
    
    # 3.1 Setup Image Variables
    img_h = inp_img_hero if inp_img_hero else "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&q=80&w=1600"
    img_f = inp_img_feat if inp_img_feat else "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800"
    img_g = inp_img_gall if inp_img_gall else "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?auto=format&fit=crop&q=80&w=1600"

    # 3.2 Global Logic Variables
    logo_display = f'<img src="{inp_logo}" alt="{inp_name}" class="h-10 md:h-16 w-auto object-contain">' if inp_logo else f'<span class="text-xl md:text-3xl font-black tracking-tighter" style="color:var(--p)">{inp_name}</span>'
    a_list = [a.strip() for a in inp_areas.split(",")]
    s_areas_json = json.dumps(a_list)
    wa_clean = inp_phone.replace(" ", "").replace("+", "")
    wa_final_url = f"https://wa.me/{wa_clean}?text=Hello%20{inp_name.replace(' ', '%20')},%20interested%20in%20your%20services."

    # 3.3 The CSS Theme
    theme_css = f"""
    :root {{ --p: {p_color}; --s: {s_color}; --radius: {border_rad}; }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; width: 100%; overflow-x: hidden; position: relative; scroll-behavior: smooth; }}
    body {{ font-family: '{b_font}', sans-serif; color: #0f172a; line-height: 1.7; background: #fff; }}
    h1, h2, h3 {{ font-family: '{h_font}', sans-serif; font-weight: {h_weight}; letter-spacing: {ls}; text-transform: uppercase; line-height: 1.1; overflow-wrap: break-word; }}
    
    .hero-title {{ font-size: clamp(1.4rem, 8vw, 100px); text-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
    .section-title {{ font-size: clamp(1.6rem, 6vw, 75px); color: var(--p); }}
    
    .btn-supreme {{ background: var(--s); color: white; padding: 1rem 2.5rem; border-radius: var(--radius); font-weight: 900; transition: all 0.4s; display: inline-block; text-align: center; border:none; box-shadow: 0 10px 20px -5px var(--s); cursor: pointer; text-decoration:none; }}
    .btn-supreme:hover {{ transform: translateY(-3px); filter: brightness(1.1); box-shadow: 0 20px 40px -5px var(--s); }}
    
    .glass-nav {{ background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(0,0,0,0.05); width: 100%; z-index: 9999; position: sticky; top: 0; }}
    
    /* RECTIFIED HERO - NO OVERLAP, NO WHITE GAP */
    .hero-mask {{ 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.5)), url('{img_h}'); 
        background-size: cover; background-position: center; 
        min-height: 85vh; display: flex; align-items: center; justify-content: center; 
        width: 100%; padding: 60px 20px;
    }}
    
    .product-card {{ background: white; border-radius: var(--radius); padding: 2rem; border: 1px solid #f1f5f9; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); transition: 0.3s; cursor: pointer; }}
    #modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.95); z-index: 100000; padding: 1rem; align-items: center; justify-content: center; overflow-y: auto; }}
    .modal-content {{ background: white; max-width: 1000px; width: 100%; border-radius: var(--radius); overflow: hidden; position: relative; }}
    .legal-text {{ white-space: pre-wrap; word-wrap: break-word; font-size: 1.1rem; color: #334155; line-height: 1.9; padding: 20px 0; }}
    .legal-bold-title {{ font-weight: 900; font-size: clamp(2.2rem, 6vw, 4.5rem); color: var(--p); margin-bottom: 2rem; text-transform: uppercase; line-height: 1; }}
    .wa-float {{ position: fixed; bottom: 30px; right: 30px; background: #25d366; color: white; width: 60px; height: 60px; border-radius: 50px; display: flex; align-items: center; justify-content: center; z-index: 99999; box-shadow: 0 10px 20px rgba(0,0,0,0.2); transition: 0.3s ease; text-decoration:none; }}
    """

    def get_layout(page_title, page_desc, content_body, is_home=False):
        v_tag = f'<meta name="google-site-verification" content="{inp_gsc_tag}">' if (is_home and inp_gsc_tag) else ""
        
        dyn_script = ""
        if is_home and inp_sheet_url:
            dyn_script = f"""
            <script>
            let currentProducts = [];
            async function fetchLiveData() {{
                try {{
                    const response = await fetch('{inp_sheet_url}');
                    const csv = await response.text();
                    if (csv.trim().startsWith("<!DOCTYPE") || csv.trim().startsWith("<html")) {{
                        document.getElementById('live-data-container').innerHTML = "<div class='col-span-full p-20 text-center bg-red-50 text-red-600 rounded-3xl font-bold uppercase'>Data Source Error: Please use CSV link.</div>";
                        return;
                    }}
                    const rows = csv.split('\\n').map(row => row.split(',')).slice(1);
                    const container = document.getElementById('live-data-container');
                    container.innerHTML = "";
                    rows.forEach((parts, idx) => {{
                        if (parts.length >= 2) {{
                            const p = {{ id: idx, name: parts[0].replace(/"/g, "").trim(), price: parts[1].replace(/"/g, "").trim(), desc: (parts[2] || "").replace(/"/g, "").trim(), img1: (parts[3] || "{img_f}").trim() }};
                            currentProducts.push(p);
                            container.innerHTML += `
                            <div onclick="openProduct(${{idx}})" class="product-card flex flex-col justify-between transition-all hover:scale-[1.03]">
                                <img src="${{p.img1}}" class="w-full h-48 object-cover mb-6 rounded-[2rem] bg-slate-50" onerror="this.src='{img_f}'">
                                <div>
                                    <h3 class="text-xl font-black mb-2 uppercase" style="color:var(--p)">${{p.name}}</h3>
                                    <p class="font-black text-2xl mb-4" style="color:var(--s)">${{p.price}}</p>
                                    <p class="text-slate-400 text-[10px] font-black uppercase tracking-widest italic underline decoration-slate-100 underline-offset-4">Learn More →</p>
                                </div>
                            </div>`;
                        }}
                    }});
                }} catch (e) {{ console.log("Fail"); }}
            }}
            function openProduct(id) {{
                const p = currentProducts[id];
                document.getElementById('m-title').innerText = p.name;
                document.getElementById('m-price').innerText = p.price;
                document.getElementById('m-desc').innerText = p.desc;
                document.getElementById('m-img-1').src = p.img1;
                document.getElementById('m-wa').href = "https://wa.me/{wa_clean}?text=" + encodeURIComponent("Interest in " + p.name);
                document.getElementById('modal').style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }}
            window.onload = fetchLiveData;
            </script>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    {v_tag}
    <title>{page_title} | {inp_name}</title>
    <meta name="description" content="{page_desc}"><meta name="keywords" content="{inp_keywords}">
    <link rel="canonical" href="{inp_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family={h_font.replace(' ', '+')}:wght@700;900&family={b_font.replace(' ', '+')}:wght@400;700&display=swap" rel="stylesheet">
    <style>{theme_css}</style>
    <script type="application/ld+json">
    {{ "@context": "https://schema.org", "@type": "LocalBusiness", "name": "{inp_name}", "address": {{ "@type": "PostalAddress", "streetAddress": "{inp_addr}" }}, "telephone": "{inp_phone}", "areaServed": {s_areas_json} }}
    </script>
</head>
<body class="bg-white">
    <nav class="glass-nav p-4 md:p-6 shadow-sm">
        <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <a href="index.html">{logo_display}</a>
            <div class="flex items-center space-x-6 md:space-x-12 text-[10px] md:text-xs font-black uppercase tracking-widest text-slate-600">
                <a href="index.html">Home</a> <a href="about.html">About</a> <a href="contact.html">Contact</a>
                <a href="tel:{inp_phone}" class="bg-slate-900 text-white px-5 py-2 rounded-full font-bold shadow-lg">Call</a>
            </div>
        </div>
    </nav>
    <main class="flex-grow">{content_body}</main>
    
    <div id="modal" onclick="if(event.target == this) {{ this.style.display='none'; document.body.style.overflow='auto'; }}">
        <div class="modal-content shadow-2xl animate-in zoom-in duration-300">
            <div class="grid md:grid-cols-2">
                <div class="p-6 bg-slate-50 flex flex-col gap-4">
                    <img id="m-img-1" class="w-full h-80 object-cover rounded-[2.5rem] shadow-xl">
                </div>
                <div class="p-12 flex flex-col justify-center text-left">
                    <h2 id="m-title" class="text-4xl font-black mb-4 uppercase text-p" style="color:var(--p)"></h2>
                    <p id="m-price" class="text-3xl font-black mb-8 text-s" style="color:var(--s)"></p>
                    <p id="m-desc" class="text-slate-600 mb-12 leading-relaxed text-lg"></p>
                    <a id="m-wa" href="#" target="_blank" class="btn-supreme w-full uppercase tracking-widest shadow-2xl">Book Now</a>
                    <button onclick="document.getElementById('modal').style.display='none'; document.body.style.overflow='auto';" class="text-xs font-black uppercase tracking-widest opacity-30 mt-8 underline">Close Window</button>
                </div>
            </div>
        </div>
    </div>

    <a href="https://wa.me/{wa_clean}" class="wa-float" target="_blank"><svg style="width:38px;height:38px" viewBox="0 0 24 24"><path fill="currentColor" d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91c0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23c-1.48 0-2.93-.39-4.19-1.15l-.3-.17l-3.12.82l.83-3.04l-.2-.32a8.188 8.188 0 0 1-1.26-4.38c.01-4.54 3.7-8.24 8.25-8.24m-3.53 3.16c-.13 0-.35.05-.54.26c-.19.2-.72.7-.72 1.72s.73 2.01.83 2.14c.1.13 1.44 2.19 3.48 3.07c.49.21.87.33 1.16.43c.49.16.94.13 1.29.08c.4-.06 1.21-.5 1.38-.98c.17-.48.17-.89.12-.98c-.05-.09-.18-.13-.37-.23c-.19-.1-.1.13-.1.13s-1.13-.56-1.32-.66c-.19-.1-.32-.15-.45.05c-.13.2-.51.65-.62.78c-.11.13-.23.15-.42.05c-.19-.1-.8-.3-1.53-.94c-.57-.5-1.02-1.12-1.21-1.45c-.11-.19-.01-.29.09-.38c.09-.08.19-.23.29-.34c.1-.11.13-.19.19-.32c.06-.13.03-.24-.01-.34c-.05-.1-.45-1.08-.62-1.48c-.16-.4-.36-.34-.51-.35c-.11-.01-.25-.01-.4-.01Z"/></svg></a>

    <footer class="bg-slate-950 text-slate-400 py-24 px-10 border-t border-slate-900">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-4 gap-16 text-left">
            <div class="col-span-2">
                <h4 class="text-white text-3xl font-black mb-8 uppercase tracking-tighter">{inp_name}</h4>
                <p class="text-sm leading-relaxed mb-10 max-w-md opacity-80">{inp_addr}</p>
                <div class="bg-slate-900/50 p-6 border border-slate-800 rounded-3xl">
                    <h5 class="text-white text-[10px] font-black uppercase tracking-widest mb-4 opacity-50">Verified Service Coverage</h5>
                    <div class="flex flex-wrap gap-2">{"".join([f'<span class="bg-slate-800 text-[10px] px-3 py-1 rounded-full uppercase font-bold text-white border border-slate-700">{a}</span>' for a in a_list])}</div>
                </div>
                <p class="text-[10px] mt-10 opacity-30 uppercase font-black tracking-widest italic tracking-widest underline decoration-white underline-offset-8 decoration-2 text-white">Architected By Kaydiem Script Lab</p>
            </div>
            <div><h4 class="text-white font-bold mb-8 uppercase text-xs">Technical Hub</h4><ul class="space-y-4 text-sm font-bold uppercase list-none p-0"><li><a href="privacy.html" class="hover:text-white transition">Privacy</a></li><li><a href="terms.html" class="hover:text-white transition">Terms</a></li></ul></div>
            <div><h4 class="text-white font-bold mb-8 uppercase text-xs text-brand" style="color:var(--s)">Direct Connect</h4><p class="text-lg font-bold text-white leading-loose">{inp_phone}<br>{inp_email}</p></div>
        </div>
    </footer>
    {dyn_script}
</body></html>"""

    # --- CONTENT CONSTRUCTORS ---
    serv_html = "".join([f'<div class="bg-slate-50 p-12 rounded-[2.5rem] border border-slate-100 shadow-xl hover:scale-[1.02] transition-transform"><h3 class="text-2xl font-black mb-4 uppercase" style="color:var(--p)">{s.strip()}</h3><p class="text-slate-500 text-sm leading-relaxed font-bold uppercase tracking-tight italic text-left">Premium technical solution for {inp_name}.</p></div>' for s in biz_serv.splitlines() if s.strip()])
    
    t_cards = ""
    for t in t_data.splitlines():
        if "|" in t:
            parts = t.split("|")
            t_cards += f'<div class="p-10 bg-slate-50 rounded-[3rem] border border-slate-100 italic text-xl shadow-inner mb-8">"{parts[1].strip()}"<br><span class="font-black not-italic text-sm block mt-6 uppercase tracking-widest text-brand" style="color:var(--p)">— {parts[0].strip()} <span class="text-emerald-500 font-black ml-2">● Partner</span></span></div>'

    f_cards = ""
    for f in f_data.splitlines():
        if "?" in f:
            parts = f.rsplit("?", 1)
            if len(parts) > 1:
                q = parts[0].strip() + "?"
                a = parts[1].strip()
                if a.startswith("?"): a = a[1:].strip()
                f_cards += f'<details class="mb-6 bg-white p-6 rounded-2xl border border-slate-100 cursor-pointer shadow-sm"><summary class="font-black text-lg uppercase tracking-tight">{q}</summary><p class="mt-4 text-slate-600 leading-relaxed font-medium">{a}</p></details>'

    d_section = f"""<section class="py-32 px-6 max-w-[1440px] mx-auto text-center border-b"><h2 class="section-title mb-20 uppercase tracking-tighter" style="color:var(--p)">Verified Packages</h2><div id="live-data-container" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-10 text-left"><p class="p-20 text-center text-slate-400 font-bold animate-pulse uppercase tracking-widest">Connecting to Data Hub...</p></div></section>""" if inp_sheet_url else ""

    idx_content = f"""
    <section class="hero-mask px-6 text-center text-white">
        <div class="max-w-[1200px] mx-auto">
            <h1 class="hero-title mb-10 uppercase tracking-tighter leading-none">{inp_hero_h}</h1>
            <p class="text-lg md:text-3xl font-light mb-16 max-w-4xl mx-auto opacity-90 leading-tight">{inp_meta_d}</p>
            <a href="tel:{inp_phone}" class="btn-supreme uppercase tracking-[0.4em] text-[10px] md:text-sm shadow-2xl" style="background:var(--p)">Consult an Expert</a>
        </div>
    </section>
    <section class="max-w-[1440px] mx-auto py-24 px-6 text-center border-b">
        <h2 class="section-title mb-20 uppercase tracking-tighter" style="color:var(--p)">Core Competencies</h2>
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
    <section class="py-32 px-6 max-w-7xl mx-auto text-center"><div class="grid md:grid-cols-2 gap-24 text-left"><div><h2 class="text-4xl font-black mb-16 uppercase tracking-tighter" style="color:var(--p)">Success</h2>{t_cards}</div><div><h2 class="text-4xl font-black mb-16 uppercase tracking-tighter" style="color:var(--p)">Expert Insights</h2>{f_cards}</div></div></section>
    """

    # --- ZIP OUTPUT ---
    z_b = io.BytesIO()
    with zipfile.ZipFile(z_b, "a", zipfile.ZIP_DEFLATED, False) as z_f:
        z_f.writestr("index.html", get_layout("Home", inp_meta_d, idx_content, True))
        z_f.writestr("about.html", get_layout("About", "History", f"<section class='max-w-7xl mx-auto py-40 px-6'><h1 class='legal-bold-title uppercase'>About Our Heritage</h1><div class='text-xl md:text-2xl leading-relaxed text-slate-700 legal-text'>{inp_about_txt}</div><img src='{img_g}' class='mt-20 w-full h-[600px] object-cover shadow-2xl' style='border-radius: var(--radius)'></section>"))
        z_f.writestr("contact.html", get_layout("Contact", "Location", f"<section class='max-w-[1440px] mx-auto py-40 px-6 text-center'><h1 class='legal-bold-title uppercase tracking-tighter'>Technical Hub</h1><div class='grid md:grid-cols-2 gap-16 text-left'><div class='bg-slate-950 p-12 md:p-24 text-white' style='border-radius: var(--radius)'><p class='text-4xl font-black mb-8 text-white'>{inp_phone}</p><p class='text-2xl mb-12 opacity-80'>{inp_addr}</p></div><div class='rounded-[3rem] overflow-hidden border shadow-2xl bg-slate-100' style='min-height:300px'>{inp_map}</div></div></section>"))
        z_f.writestr("privacy.html", get_layout("Privacy", "Legal", f"<div class='max-w-4xl mx-auto py-40 px-6'><h1 class='legal-bold-title uppercase'>Privacy Policy</h1><div class='text-lg legal-text'>{inp_priv_body}</div></div>"))
        z_f.writestr("terms.html", get_layout("Terms", "Legal", f"<div class='max-w-4xl mx-auto py-40 px-6'><h1 class='legal-bold-title uppercase'>Terms & Conditions</h1><div class='text-lg legal-text'>{inp_terms_body}</div></div>"))
        z_f.writestr("404.html", get_layout("404", "Not Found", "<div class='py-64 text-center'><h1 class='text-[120px] font-black uppercase text-slate-200 tracking-widest'>404</h1></div>"))
        z_f.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {inp_url}sitemap.xml")
        z_f.writestr("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{inp_url}index.html</loc></url><url><loc>{inp_url}about.html</loc></url></urlset>')

    st.success("💎 TITAN SUPREME v9.9 AUDITED MASTER DEPLOYED.")
    st.download_button("📥 DOWNLOAD ENTERPRISE BIZ PACKAGE", z_b.getvalue(), f"{inp_name.lower().replace(' ', '_')}_v9_9.zip")
