import streamlit as st
import zipfile
import io
import json
from datetime import datetime

# --- 1. DESIGN STUDIO CONFIGURATION ---
st.set_page_config(page_title="Kaydiem Titan v6.1 | Bulletproof Web Architect", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main { background: #0f172a; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1e293b; 
        border-radius: 8px 8px 0 0; 
        padding: 10px 20px; 
        color: white;
        border: 1px solid #334155;
    }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 4em; 
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
        color: white; font-weight: 900; border: none; font-size: 1.4rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: all 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); filter: brightness(1.2); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: DESIGN STUDIO ---
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/business_profile_96dp.png", width=50)
    st.title("Titan v6.1 Studio")
    
    with st.expander("🎭 1. Layout & DNA", expanded=True):
        layout_dna = st.selectbox("Design DNA", ["Industrial Titan", "Classic Royal", "Soft-UI", "Glass-Tech", "Brutalist"])
        p_color = st.color_picker("Primary Brand Color", "#1E293B")
        s_color = st.color_picker("Accent/CTA Color", "#2563EB")
        border_rad = st.select_slider("Corner Roundness", options=["0px", "4px", "12px", "24px", "60px"], value="24px")

    with st.expander("✍️ 2. Typography Studio", expanded=True):
        h_font = st.selectbox("Heading Font", ["Montserrat", "Oswald", "Playfair Display", "Syncopate", "Inter"])
        b_font = st.selectbox("Body Font", ["Inter", "Roboto", "Open Sans", "Lora"])
        h_weight = st.select_slider("Weight", options=["300", "400", "700", "900"], value="900")
        ls = st.select_slider("Letter Spacing", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="-0.02em")

    gsc_tag = st.text_input("GSC Verification Tag")
    st.info("Technical Support: www.kaydiemscriptlab.com")

st.title("🏗️ Kaydiem Titan Supreme v6.1")

# --- 2. MULTI-TAB DATA COLLECTION ---
tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🖼️ Photos", "⚡ Live Data", "🌟 Social Proof", "⚖️ Legal Pages"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name (NAP)", "PETRA Ready Mixed Concrete")
        biz_phone = st.text_input("Verified Phone", "+966 53 785 0627")
        biz_email = st.text_input("Business Email", "info@business.sa")
    with c2:
        biz_cat = st.text_input("Category", "Industrial Supplier")
        biz_hours = st.text_input("Hours", "Sat-Thu: 08:00 - 18:00")
        prod_url = st.text_input("Production URL", "https://kani201012.github.io/site/")
    biz_logo = st.text_input("Logo URL (Direct Image Link)")
    biz_addr = st.text_area("Full Maps Physical Address")
    biz_areas = st.text_area("Service Areas (Comma separated for Geo-Schema)", "Al Olaya, Al Mashael, Malham")
    map_iframe = st.text_area("Map Embed HTML Code (<iframe>)")

with tabs[1]:
    hero_h = st.text_input("Main Hero Headline", "Precision Engineering Excellence")
    seo_d = st.text_input("Meta Description", "Verified 2026 AI-Ready Industrial Assets.")
    biz_key = st.text_input("SEO Keywords")
    biz_serv = st.text_area("Services (One per line)")
    about_txt = st.text_area("Our Story (800+ Words for E-E-A-T)", height=250)

with tabs[2]:
    st.header("📸 Premium Photo Management")
    custom_hero = st.text_input("Hero Background Image URL")
    custom_feat = st.text_input("Feature Image URL")
    custom_gall = st.text_input("Gallery Image URL")

with tabs[3]:
    st.header("⚡ Google Sheets Live-Data Bridge")
    st.warning("IMPORTANT: Go to File > Share > Publish to Web > Select Sheet > Select CSV. Paste that link below.")
    sheet_url = st.text_input("Published CSV URL", placeholder="https://docs.google.com/spreadsheets/d/.../pub?output=csv")

with tabs[4]:
    testi = st.text_area("Testimonials (Name | Quote)")
    faqs = st.text_area("FAQ (Format: Question? ? Answer)")

with tabs[5]:
    st.header("⚖️ Legal Compliance")
    priv_body = st.text_area("Privacy Policy Content", height=300)
    terms_body = st.text_area("Terms Content", height=300)

# --- 3. THE SUPREME ENGINE V6.1 ---

if st.button("🚀 DEPLOY WORLD-CLASS DYNAMIC ASSET"):
    
    # Image Fallbacks
    s_hero = "https://images.unsplash.com/photo-1517089591964-9997858a9f7c?auto=format&fit=crop&q=80&w=1600"
    s_feat = "https://images.unsplash.com/photo-1591543622407-368241483321?auto=format&fit=crop&q=80&w=800"
    s_gall = "https://images.unsplash.com/photo-1565011523534-747a8601f10a?auto=format&fit=crop&q=80&w=1600"
    
    img_h = custom_hero if custom_hero else s_hero
    img_f = custom_feat if custom_feat else s_feat
    img_g = custom_gall if custom_gall else s_gall

    # Logo Logic
    logo_html = f'<img src="{biz_logo}" alt="{biz_name}" class="h-10 md:h-14 w-auto object-contain">' if biz_logo else f'<span class="text-xl md:text-3xl font-black tracking-tighter" style="color:var(--p)">{biz_name}</span>'

    # WhatsApp & Geo Logic
    wa_clean = biz_phone.replace(" ", "").replace("+", "")
    wa_url = f"https://wa.me/{wa_clean}?text=Hello%20{biz_name.replace(' ', '%20')},%20I%20am%20interested%20in%20your%20services."
    area_list = [a.strip() for a in biz_areas.split(",")]
    schema_areas = json.dumps(area_list)

    theme_css = f"""
    :root {{ --p: {p_color}; --s: {s_color}; --radius: {border_rad}; }}
    body {{ font-family: '{b_font}', sans-serif; color: #0f172a; line-height: 1.7; overflow-x: hidden; width: 100%; }}
    h1, h2, h3 {{ font-family: '{h_font}', sans-serif; font-weight: {h_weight}; letter-spacing: {ls}; text-transform: uppercase; line-height: 1.05; overflow-wrap: break-word; }}
    .hero-title {{ font-size: clamp(2rem, 9vw, 110px); text-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
    .section-title {{ font-size: clamp(1.8rem, 6vw, 75px); }}
    .btn-supreme {{ background: var(--p); color: white; padding: 1.1rem 2.8rem; border-radius: var(--radius); font-weight: 900; transition: all 0.4s; display: inline-block; text-align: center; }}
    .btn-supreme:hover {{ transform: translateY(-3px); box-shadow: 0 20px 40px rgba(0,0,0,0.2); filter: brightness(1.1); }}
    .glass-nav {{ background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(0,0,0,0.08); width: 100%; }}
    .hero-mask {{ background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.6)), url('{img_h}'); background-size: cover; background-position: center; min-height: 90vh; display: flex; align-items: center; justify-content: center; }}
    .wa-float {{ position: fixed; bottom: 30px; right: 30px; background: #25d366; color: white; width: 65px; height: 65px; border-radius: 50px; display: flex; align-items: center; justify-content: center; z-index: 99999; box-shadow: 0 10px 25px rgba(37,211,102,0.4); transition: 0.3s; }}
    .legal-text {{ white-space: pre-wrap; word-wrap: break-word; font-size: 1.15rem; color: #334155; }}
    .legal-bold-title {{ font-weight: 900; font-size: clamp(2rem, 5vw, 4.5rem); color: var(--p); margin-bottom: 2rem; text-transform: uppercase; line-height: 1; }}
    .dynamic-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
    """

    def get_layout(title, desc, content, is_index=False):
        v_tag = f'<meta name="google-site-verification" content="{gsc_tag}">' if (is_index and gsc_tag) else ""
        
        dynamic_script = ""
        if is_index and sheet_url:
            dynamic_script = f"""
            <script>
            async function fetchLiveData() {{
                try {{
                    const response = await fetch('{sheet_url}');
                    const csv = await response.text();
                    
                    // Technical Validator for Kiran: Stop HTML injection
                    if (csv.includes("<!DOCTYPE") || csv.includes("script")) {{
                        document.getElementById('live-data-container').innerHTML = "<div class='col-span-full p-20 text-center bg-red-50 text-red-600 rounded-3xl border border-red-100 font-bold'>ERROR: Technical Data Link Mismatch. Please ensure you published as CSV, not Web Page.</div>";
                        return;
                    }}

                    const rows = csv.split('\\n').map(row => row.split(','));
                    const container = document.getElementById('live-data-container');
                    container.innerHTML = "";
                    
                    for (let i = 1; i < rows.length; i++) {{
                        const [name, val, dsc] = rows[i];
                        if(name && name.trim() !== "") {{
                            container.innerHTML += `
                            <div class="bg-white p-10 rounded-[2.5rem] border shadow-xl transition-all hover:scale-[1.03]">
                                <h3 class="text-2xl font-black mb-2 uppercase" style="color:{p_color}">${{name.trim()}}</h3>
                                <p class="text-blue-600 font-black text-2xl mb-4">${{val ? val.trim() : ''}}</p>
                                <p class="text-slate-500 text-sm leading-relaxed">${{dsc ? dsc.trim() : ''}}</p>
                            </div>`;
                        }}
                    }}
                }} catch (e) {{ 
                    document.getElementById('live-data-container').innerHTML = "<p class='p-10 text-center text-slate-400 font-bold'>TECHNICAL NOTICE: Live Data Sync in Progress...</p>";
                }}
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
    {{ "@context": "https://schema.org", "@type": "LocalBusiness", "name": "{biz_name}", "address": {{ "@type": "PostalAddress", "streetAddress": "{biz_addr}" }}, "telephone": "{biz_phone}", "areaServed": {schema_areas} }}
    </script>
</head>
<body class="bg-white flex flex-col min-h-screen text-slate-900">
    <nav class="glass-nav sticky top-0 z-50 p-4 md:p-6">
        <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
            <a href="index.html" class="flex items-center">{logo_html}</a>
            <div class="flex items-center space-x-6 md:space-x-12 text-[10px] md:text-xs font-black uppercase tracking-widest text-slate-600">
                <a href="index.html" class="hover:text-blue-600">Home</a> <a href="about.html">About</a> <a href="contact.html">Contact</a>
                <a href="tel:{biz_phone}" class="bg-slate-900 text-white px-6 py-2 rounded-full font-bold shadow-lg">Call</a>
            </div>
        </div>
    </nav>
    <main class="flex-grow">{content}</main>
    <a href="{wa_url}" class="wa-float" target="_blank"><svg style="width:38px;height:38px" viewBox="0 0 24 24"><path fill="currentColor" d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91c0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23c-1.48 0-2.93-.39-4.19-1.15l-.3-.17l-3.12.82l.83-3.04l-.2-.32a8.188 8.188 0 0 1-1.26-4.38c.01-4.54 3.7-8.24 8.25-8.24m-3.53 3.16c-.13 0-.35.05-.54.26c-.19.2-.72.7-.72 1.72s.73 2.01.83 2.14c.1.13 1.44 2.19 3.48 3.07c.49.21.87.33 1.16.43c.49.16.94.13 1.29.08c.4-.06 1.21-.5 1.38-.98c.17-.48.17-.89.12-.98c-.05-.09-.18-.13-.37-.23c-.19-.1-.1.13-.1.13s-1.13-.56-1.32-.66c-.19-.1-.32-.15-.45.05c-.13.2-.51.65-.62.78c-.11.13-.23.15-.42.05c-.19-.1-.8-.3-1.53-.94c-.57-.5-1.02-1.12-1.21-1.45c-.11-.19-.01-.29.09-.38c.09-.08.19-.23.29-.34c.1-.11.13-.19.19-.32c.06-.13.03-.24-.01-.34c-.05-.1-.45-1.08-.62-1.48c-.16-.4-.36-.34-.51-.35c-.11-.01-.25-.01-.4-.01Z"/></svg></a>
    <footer class="bg-slate-950 text-slate-400 py-24 px-10 border-t border-slate-900">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-4 gap-16">
            <div class="col-span-2">
                {logo_html.replace('h-10 md:h-14', 'h-8 mb-6 opacity-70')}
                <p class="text-sm leading-relaxed mb-10 max-w-md">{biz_addr}</p>
                <div class="bg-slate-900/50 p-6 border border-slate-800 rounded-3xl">
                    <h5 class="text-white text-[10px] font-black uppercase tracking-widest mb-4 opacity-50">Verified Coverage Areas</h5>
                    <div class="flex flex-wrap gap-2">
                        {"".join([f'<span class="bg-slate-800 text-[10px] px-3 py-1 rounded-full uppercase font-bold text-white tracking-widest border border-slate-700">{area}</span>' for area in area_list])}
                    </div>
                </div>
                <p class="text-[10px] mt-10 opacity-30 uppercase font-black tracking-widest italic tracking-widest">Architected By <a href="https://www.kaydiemscriptlab.com" class="text-white underline">Kaydiem Script Lab</a></p>
            </div>
            <div><h4 class="text-white font-bold mb-8 uppercase text-xs">Navigation</h4>
                <ul class="space-y-4 text-sm font-bold uppercase"><li><a href="privacy.html" class="hover:text-white transition">Privacy Policy</a></li><li><a href="terms.html" class="hover:text-white transition">Terms</a></li></ul>
            </div>
            <div><h4 class="text-white font-bold mb-8 uppercase text-xs">Connect</h4><p class="text-lg font-bold text-white leading-loose">{biz_phone}<br>{biz_email}</p></div>
        </div>
    </footer>
    {dynamic_script}
</body></html>"""

    # --- ENHANCED INDEX CONTENT ---
    serv_html = "".join([f'<div class="bg-slate-50 p-12 rounded-[2.5rem] border border-slate-100 shadow-xl hover:scale-[1.02] transition-transform"><h3 class="text-2xl font-black mb-4 uppercase text-brand" style="color:var(--p)">{s.strip()}</h3><p class="text-slate-500 text-sm leading-relaxed font-bold uppercase tracking-tight italic">Premium verified solution for {biz_name}.</p></div>' for s in biz_serv.splitlines() if s.strip()])
    testi_cards = "".join([f'<div class="p-10 bg-slate-50 rounded-[3rem] border border-slate-100 italic text-xl shadow-inner mb-8">"{t.split("|")[1].strip()}"<br><span class="font-black not-italic text-sm block mt-6 uppercase tracking-widest text-brand" style="color:var(--p)">— {t.split("|")[0].strip()} <span class="text-emerald-500 font-black ml-2">● Partner</span></span></div>' for t in testi.splitlines() if "|" in t])
    
    # Corrected Last-Separator FAQ Logic
    faq_html = ""
    for f in faqs.splitlines():
        if "?" in f:
            parts = f.rsplit("?", 1)
            if len(parts) > 1:
                q = parts[0].strip() + "?"
                a = parts[1].strip()
                if a.startswith("?"): a = a[1:].strip()
                faq_html += f'<details class="mb-6 bg-white p-6 rounded-2xl border border-slate-100 cursor-pointer shadow-sm"><summary class="font-black text-lg uppercase tracking-tight">{q}</summary><p class="mt-4 text-slate-600 leading-relaxed font-medium">{a}</p></details>'

    # Dynamic Data Section
    dynamic_section = ""
    if sheet_url:
        dynamic_section = f"""
        <section class="py-32 px-6 max-w-[1440px] mx-auto">
            <h2 class="section-title mb-20 text-center uppercase tracking-tighter" style="color:var(--p)">Live Inventory & Pricing</h2>
            <div id="live-data-container" class="dynamic-grid">
                <p class="p-20 text-center text-slate-400 font-bold animate-pulse">Establishing Connection to Google Cloud...</p>
            </div>
        </section>"""

    idx_content = f"""
    <section class="hero-mask px-6 text-center text-white">
        <div class="max-w-[1200px] mx-auto">
            <h1 class="hero-title mb-10 uppercase tracking-tighter leading-none">{hero_h}</h1>
            <p class="text-lg md:text-3xl font-light mb-16 max-w-4xl mx-auto opacity-90 leading-tight">{seo_d}</p>
            <a href="tel:{biz_phone}" class="btn-supreme uppercase tracking-[0.4em] text-[10px] md:text-sm shadow-2xl">Connect Now</a>
        </div>
    </section>
    <section class="max-w-[1440px] mx-auto py-24 px-6 text-center border-b">
        <h2 class="section-title mb-20 uppercase tracking-tighter" style="color:var(--p)">Capabilities</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-10 text-left">{serv_html}</div>
    </section>
    {dynamic_section}
    <section class="bg-slate-50 py-32 px-6 border-y">
        <div class="max-w-[1440px] mx-auto grid md:grid-cols-2 gap-24 items-center">
            <img src="{img_f}" class="shadow-2xl grayscale hover:grayscale-0 transition duration-700" style="border-radius: var(--radius)">
            <div>
                <h2 class="text-5xl font-black mb-12 uppercase tracking-tighter leading-none" style="color:var(--p)">Verified 2026 Authority</h2>
                <p class="text-2xl text-slate-600 mb-12 leading-relaxed italic">"Supplying the engineering foundation for the 2026 Riyadh landscape. Precision mixing, certified safety, and direct owner oversight."</p>
                <a href="about.html" class="btn-supreme text-xs tracking-widest uppercase">View Full Story</a>
            </div>
        </div>
    </section>
    <section class="py-32 px-6 max-w-[1440px] mx-auto">
        <div class="grid md:grid-cols-2 gap-24">
            <div><h2 class="text-4xl font-black mb-16 uppercase tracking-tighter" style="color:var(--p)">Partner Success</h2>{testi_cards}</div>
            <div><h2 class="text-4xl font-black mb-16 uppercase tracking-tighter" style="color:var(--p)">Expert Insights</h2>{faq_html}</div>
        </div>
    </section>
    """

    # --- ZIP OUTPUT ---
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr("index.html", get_layout("Home", seo_d, idx_content, True))
        zf.writestr("about.html", get_layout("About Us", "History", f"<section class='max-w-7xl mx-auto py-32 px-6'><h1 class='legal-bold-title'>About Our Heritage</h1><div class='text-xl md:text-2xl leading-relaxed text-slate-700 legal-text'>{about_txt}</div><img src='{img_g}' class='mt-20 w-full h-[600px] object-cover shadow-2xl' style='border-radius: var(--radius)'></section>"))
        zf.writestr("contact.html", get_layout("Contact", "Location", f"<section class='max-w-[1440px] mx-auto py-32 px-6 text-center'><h1 class='legal-bold-title'>Connect with Us</h1><div class='grid md:grid-cols-2 gap-16 text-left'><div class='bg-slate-950 p-12 md:p-24 text-white' style='border-radius: var(--radius)'><p class='text-4xl font-black mb-8'>{biz_phone}</p><p class='text-2xl mb-12 opacity-80'>{biz_addr}</p></div><div class='rounded-[3rem] overflow-hidden border shadow-2xl bg-slate-100' style='min-height:300px'>{map_iframe}</div></div></section>"))
        zf.writestr("privacy.html", get_layout("Privacy", "Legal", f"<div class='max-w-4xl mx-auto py-32 px-10'><h1 class='legal-bold-title'>Privacy Policy</h1><div class='text-lg legal-text'>{priv_body}</div></div>"))
        zf.writestr("terms.html", get_layout("Terms", "Legal", f"<div class='max-w-4xl mx-auto py-32 px-10'><h1 class='legal-bold-title'>Terms & Conditions</h1><div class='text-lg legal-text'>{terms_body}</div></div>"))
        zf.writestr("404.html", get_layout("404", "Not Found", "<div class='py-64 text-center'><h1 class='text-[120px] font-black uppercase tracking-widest'>404</h1></div>"))
        zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {prod_url}sitemap.xml")
        zf.writestr("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{prod_url}index.html</loc></url><url><loc>{prod_url}about.html</loc></url></urlset>')

    st.success("💎 TITAN SUPREME v6.1 DEPLOYED. Headless Dynamics fixed.")
    st.download_button("📥 DOWNLOAD COMPLETE BIZ PACKAGE", zip_buf.getvalue(), f"{biz_name.lower()}_v6_1.zip")
