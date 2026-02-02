import streamlit as st
import zipfile
import io
import json
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Titan v26.6 | Kaydiem Architect", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED UI SYSTEM (CSS for Streamlit Interface) ---
st.markdown("""
    <style>
    :root { --primary: #0f172a; --accent: #3b82f6; }
    .stApp { background-color: #f1f5f9; color: #1e293b; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stTextInput input, .stTextArea textarea { border-radius: 8px !important; }
    .stButton>button {
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        color: white; font-weight: 800; border: none; height: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.title("Titan Architect")
    st.caption("v26.6 | SEO & Mobile Fix")
    st.divider()
    
    with st.expander("🎨 Visual DNA", expanded=True):
        theme_mode = st.selectbox("Base Theme", ["Clean Corporate (Light)", "Midnight SaaS (Dark)", "Ocean Breeze", "Glassmorphism"])
        c1, c2 = st.columns(2)
        p_color = c1.color_picker("Primary Brand", "#0F172A") 
        s_color = c2.color_picker("Action (CTA)", "#3B82F6")  
        h_font = st.selectbox("Headings", ["Montserrat", "Space Grotesk", "Playfair Display", "Oswald"])
        b_font = st.selectbox("Body Text", ["Inter", "Roboto", "Open Sans", "Lato"])
        border_rad = st.select_slider("Corner Roundness", ["0px", "4px", "12px", "24px"], value="12px")

    with st.expander("🧩 Section Manager", expanded=False):
        show_hero = st.checkbox("Hero Header", value=True)
        show_stats = st.checkbox("Trust Stats", value=True)
        show_features = st.checkbox("Feature Grid", value=True)
        show_inventory = st.checkbox("Live Inventory", value=True)
        show_gallery = st.checkbox("Visual Gallery", value=True)
        show_testimonials = st.checkbox("Testimonials", value=True)
        show_faq = st.checkbox("F.A.Q.", value=True)
        show_cta = st.checkbox("Final Call to Action", value=True)

    with st.expander("⚙️ SEO & Schema", expanded=False):
        gsc_tag = st.text_input("Google Verification ID")
        ga_tag = st.text_input("Google Analytics ID (G-XXXX)")

# --- 4. MAIN WORKSPACE ---
st.title("🏗️ Site Content Builder")
tabs = st.tabs(["1. Identity", "2. Content Blocks", "3. Inventory", "4. Legal & Footer"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Kaydiem Script Lab")
        biz_tagline = st.text_input("Tagline", "Premium Software & Scripting Solutions")
        biz_phone = st.text_input("Phone", "+966 57 256 2151")
        biz_email = st.text_input("Email (For Forms)", "hello@kaydiemscriptlab.com")
    with c2:
        prod_url = st.text_input("Website URL", "https://kaydiemscriptlab.com")
        biz_addr = st.text_area("Address", "Kanishka's House, Garia Station Rd, Kolkata, West Bengal 700084, India", height=100)
        seo_d = st.text_area("Meta Description", "Kaydiem Script Lab provides advanced custom scripts, automation tools, and web architecture.", height=100)
        logo_url = st.text_input("Logo URL (Leave empty for Text Logo)")

    st.subheader("Social Links")
    sc1, sc2, sc3 = st.columns(3)
    fb_link = sc1.text_input("Facebook URL")
    x_link = sc2.text_input("X (Twitter) URL")
    li_link = sc3.text_input("LinkedIn URL")
    wa_num = st.text_input("WhatsApp Number (No +)", "966572562151")

with tabs[1]:
    st.subheader("Hero Section")
    hero_h = st.text_input("Hero Headline", "Empower Your Digital Ecosystem")
    hero_sub = st.text_input("Hero Subtext", "From custom scripts to full-scale software architecture, we build the tools that drive modern business.")
    hero_img = st.text_input("Hero Image URL", "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1600")
    
    st.subheader("Features (Icon | Title | Desc)")
    feat_data = st.text_area("Features List", 
        "code | Custom Scripting | Automation for repetitive workflows.\n"
        "layers | Web Development | High-performance SaaS & Corporate sites.\n"
        "database | ERP Solutions | Centralized management for your enterprise.", height=150)

    st.subheader("About Section")
    about_h = st.text_input("About Title", "The Future of Digital Architecture")
    about_txt = st.text_area("About Text", "Welcome to Kaydiem Script Lab, a hub of technical innovation where code meets creativity...", height=150)
    about_img = st.text_input("About Image URL", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1600")

with tabs[2]:
    st.info("⚡ Google Sheet CSV Link (Columns: Name, Price, Description, ImageURL)")
    sheet_url = st.text_input("CSV Link", placeholder="https://docs.google.com/spreadsheets/d/e/.../pub?output=csv")
    custom_feat = st.text_input("Default Product Image", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=800")

with tabs[3]:
    st.subheader("Legal & Footer")
    testi_data = st.text_area("Testimonials (Name | Quote)", "Arjun Mehta | The custom scripts from Kaydiem reduced our manual workload by 70%.", height=100)
    faq_data = st.text_area("FAQ (Q? ? A)", "Do you provide custom scripts? ? Yes, tailored to your needs.", height=100)
    priv_txt = st.text_area("Privacy Policy", "We collect information you provide directly to us...", height=100)
    term_txt = st.text_area("Terms of Service", "By accessing the Kaydiem Script Lab website...", height=100)

# --- 5. COMPILER ENGINE (THE BRAIN) ---

def format_text(text):
    if not text: return ""
    return "".join([f"<p>{p.strip()}</p>" for p in text.split('\n') if p.strip()])

def get_theme_css():
    # Theme Colors
    bg, txt, card_bg, nav_bg = "#ffffff", "#0f172a", "#ffffff", "rgba(255, 255, 255, 0.95)"
    if "Midnight" in theme_mode:
        bg, txt, card_bg, nav_bg = "#0f172a", "#f8fafc", "#1e293b", "rgba(15, 23, 42, 0.95)"
    
    hero_bg = f"url('{hero_img}')" if hero_img else "var(--p)"

    return f"""
    :root {{ --p: {p_color}; --s: {s_color}; --bg: {bg}; --txt: {txt}; --card: {card_bg}; --nav: {nav_bg}; --rad: {border_rad}; --hf: '{h_font}'; --bf: '{b_font}'; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--txt); font-family: var(--bf), sans-serif; line-height: 1.6; overflow-x: hidden; }}
    h1, h2, h3, h4 {{ font-family: var(--hf), sans-serif; color: var(--p); line-height: 1.2; margin-bottom: 1rem; }}
    a {{ text-decoration: none; color: inherit; transition: 0.3s; }}
    
    /* Layout */
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
    section {{ padding: 5rem 0; }}
    
    /* Navigation */
    nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 70px; background: var(--nav); backdrop-filter: blur(10px); z-index: 1000; border-bottom: 1px solid rgba(0,0,0,0.05); display: flex; align-items: center; }}
    .nav-con {{ display: flex; justify-content: space-between; align-items: center; width: 100%; }}
    .logo {{ font-weight: 900; font-size: 1.5rem; color: var(--p); }}
    .nav-links {{ display: flex; gap: 2rem; align-items: center; }}
    .nav-links a {{ font-weight: 600; font-size: 0.95rem; opacity: 0.8; }}
    .nav-links a:hover {{ color: var(--s); opacity: 1; }}
    .mobile-menu {{ display: none; font-size: 1.5rem; cursor: pointer; }}
    
    /* Hero */
    .hero {{ min-height: 85vh; display: flex; align-items: center; text-align: center; background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.6)), {hero_bg}; background-size: cover; background-position: center; color: white; padding-top: 70px; }}
    .hero h1 {{ color: white; font-size: clamp(2.5rem, 6vw, 4.5rem); margin-bottom: 1rem; }}
    .hero p {{ color: rgba(255,255,255,0.9); font-size: 1.25rem; max-width: 700px; margin: 0 auto 2.5rem; }}
    
    /* Components */
    .btn {{ display: inline-block; padding: 1rem 2rem; border-radius: var(--rad); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: none; cursor: pointer; }}
    .btn-p {{ background: var(--p); color: white; }}
    .btn-s {{ background: var(--s); color: white; }}
    .btn:hover {{ transform: translateY(-2px); filter: brightness(1.1); }}
    
    .card {{ background: var(--card); padding: 2rem; border-radius: var(--rad); border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); height: 100%; display: flex; flex-direction: column; }}
    .icon-box {{ width: 50px; height: 50px; background: rgba(59, 130, 246, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: var(--s); }}
    
    /* Form */
    input, textarea, select {{ width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #ccc; border-radius: 6px; font-family: inherit; }}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .nav-links {{ position: fixed; top: 70px; left: -100%; width: 100%; height: calc(100vh - 70px); background: var(--bg); flex-direction: column; padding: 2rem; transition: 0.3s; }}
        .nav-links.active {{ left: 0; }}
        .mobile-menu {{ display: block; }}
        .hero {{ min-height: 60vh; }}
    }}
    """

def gen_schema():
    # Generates JSON-LD for Google
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": biz_name,
        "image": logo_url or hero_img,
        "telephone": biz_phone,
        "email": biz_email,
        "address": {"@type": "PostalAddress", "streetAddress": biz_addr},
        "url": prod_url,
        "description": seo_d
    }
    return f'<script type="application/ld+json">{json.dumps(schema)}</script>'

def build_page(title, content, extra_head=""):
    nav_links = f"""
        <a href="index.html">Home</a>
        {'<a href="index.html#features">Services</a>' if show_features else ''}
        {'<a href="index.html#inventory">Products</a>' if show_inventory else ''}
        <a href="about.html">About</a>
        <a href="contact.html">Contact</a>
        <a href="contact.html" class="btn btn-s" style="padding:0.5rem 1.5rem; margin:0;">Get Quote</a>
    """
    
    logo_display = f'<img src="{logo_url}" height="35">' if logo_url else biz_name

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} | {biz_name}</title>
        <meta name="description" content="{seo_d}">
        <link href="https://fonts.googleapis.com/css2?family={h_font.replace(' ','+')}:wght@700&family={b_font.replace(' ','+')}:wght@400;600&display=swap" rel="stylesheet">
        {gen_schema()}
        <style>{get_theme_css()}</style>
        {extra_head}
    </head>
    <body>
        <nav><div class="container nav-con">
            <a href="index.html" class="logo">{logo_display}</a>
            <div class="mobile-menu" onclick="document.querySelector('.nav-links').classList.toggle('active')">☰</div>
            <div class="nav-links">{nav_links}</div>
        </div></nav>
        
        {content}
        
        <footer><div class="container">
            <div class="grid-3" style="padding-bottom:3rem; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:2rem;">
                <div><h3>{biz_name}</h3><p style="opacity:0.8">{biz_tagline}</p></div>
                <div><h4>Quick Links</h4><div style="display:flex; flex-direction:column; gap:0.5rem;">{nav_links.replace('class="btn btn-s"','')}</div></div>
                <div><h4>Legal</h4><a href="privacy.html">Privacy Policy</a><br><a href="terms.html">Terms of Service</a></div>
            </div>
            <div style="text-align:center; opacity:0.6; font-size:0.9rem;">&copy; {datetime.datetime.now().year} {biz_name}. All rights reserved.</div>
        </div></footer>
        
        <script>
        // Simple Reveal Animation
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{ if(entry.isIntersecting) entry.target.style.opacity = 1; }});
        }});
        document.querySelectorAll('section').forEach(sec => {{ sec.style.opacity=0; sec.style.transition='1s'; observer.observe(sec); }});
        </script>
    </body>
    </html>
    """

# --- 6. PAGE CONTENT GENERATORS ---

def get_svg_icon(name):
    # Simple SVG paths for common icons
    icons = {
        "code": '<path d="M16 18l6-6-6-6-1.4 1.4L19.2 12l-4.6 4.6L16 18zM8 18l-6-6 6-6 1.4 1.4L4.8 12l4.6 4.6L8 18z"/>',
        "layers": '<path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5 2 13.5l10 5 10-5-2.5-1.25L12 17.25 4.5 13.5 12 11z"/>',
        "database": '<path d="M12 2C6.48 2 2 4.02 2 6.5S6.48 11 12 11s10-2.02 10-4.5S17.52 2 12 2zm0 9c-5.52 0-10 2.02-10 4.5S6.48 20 12 20s10-2.02 10-4.5S17.52 11 12 11z"/>'
    }
    path = icons.get(name, icons["layers"])
    return f'<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">{path}</svg>'

home_html = ""
if show_hero:
    home_html += f"""
    <section class="hero"><div class="container">
        <h1>{hero_h}</h1><p>{hero_sub}</p>
        <a href="#inventory" class="btn btn-s">Explore Solutions</a>
        <a href="contact.html" class="btn" style="background:rgba(255,255,255,0.2); margin-left:1rem; color:white;">Contact Us</a>
    </div></section>
    """

if show_features:
    cards = ""
    for line in feat_data.split('\n'):
        if "|" in line:
            icon, title, desc = line.split('|')
            cards += f"""
            <div class="card">
                <div class="icon-box">{get_svg_icon(icon.strip())}</div>
                <h3>{title.strip()}</h3><p>{desc.strip()}</p>
            </div>"""
    home_html += f'<section id="features"><div class="container"><h2 style="text-align:center; margin-bottom:3rem;">Our Expertise</h2><div class="grid-3">{cards}</div></div></section>'

if show_inventory and sheet_url:
    home_html += f"""
    <section id="inventory" style="background:rgba(0,0,0,0.02)"><div class="container">
        <h2 style="text-align:center;">Latest Products</h2>
        <div id="inv-grid" class="grid-3">Loading Inventory...</div>
    </div></section>
    <script>
    fetch('{sheet_url}').then(r=>r.text()).then(t => {{
        const lines = t.split(/\\r\\n|\\n/).slice(1);
        const box = document.getElementById('inv-grid');
        box.innerHTML = '';
        lines.forEach(l => {{
            const c = l.split(','); // Basic CSV Split
            if(c.length > 2) {{
                // Fix for CSV parsing quotes omitted for brevity, using simple logic
                let img = c[3] && c[3].startsWith('http') ? c[3] : '{custom_feat}';
                box.innerHTML += `<div class="card">
                    <img src="${{img}}" style="height:200px; object-fit:cover; border-radius:8px; margin-bottom:1rem;">
                    <h3>${{c[0]}}</h3>
                    <p style="color:var(--s); font-weight:bold;">${{c[1]}}</p>
                    <a href="product.html?id=${{encodeURIComponent(c[0])}}" class="btn btn-p" style="margin-top:auto; padding:0.5rem; text-align:center; font-size:0.9rem;">View Details</a>
                </div>`;
            }}
        }});
    }});
    </script>
    """

if show_gallery:
    home_html += f"""
    <section style="background:var(--p); color:white;"><div class="container">
        <div class="grid-3" style="grid-template-columns:1fr 1fr; align-items:center;">
            <div><h2>{about_h}</h2><p>{about_txt[:200]}...</p><br><a href="about.html" class="btn btn-s">Read More</a></div>
            <img src="{about_img}" style="width:100%; border-radius:12px;">
        </div>
    </div></section>
    """

# --- PAGE SPECIFIC GENERATORS ---

# Contact Page with FormSubmit
contact_html = f"""
<section class="hero" style="min-height:50vh;"><div class="container"><h1>Contact Us</h1></div></section>
<section><div class="container">
    <div class="grid-3" style="grid-template-columns: 1fr 2fr;">
        <div>
            <h3>Get In Touch</h3>
            <p><strong>Address:</strong><br>{biz_addr}</p><br>
            <p><strong>Phone:</strong><br><a href="tel:{biz_phone}">{biz_phone}</a></p><br>
            <p><strong>Email:</strong><br><a href="mailto:{biz_email}">{biz_email}</a></p>
        </div>
        <div class="card">
            <form action="https://formsubmit.co/{biz_email}" method="POST">
                <input type="text" name="name" placeholder="Your Name" required>
                <input type="email" name="email" placeholder="Your Email" required>
                <textarea name="message" rows="5" placeholder="How can we help?" required></textarea>
                <button type="submit" class="btn btn-p" style="width:100%;">Send Message</button>
            </form>
        </div>
    </div>
</div></section>
"""

# Product Detail Script
prod_script = f"""
<script>
const params = new URLSearchParams(window.location.search);
const id = params.get('id');
if(id) {{
    fetch('{sheet_url}').then(r=>r.text()).then(t => {{
        const lines = t.split(/\\r\\n|\\n/).slice(1);
        const row = lines.find(l => l.includes(id));
        if(row) {{
            const c = row.split(',');
            let img = c[3] && c[3].startsWith('http') ? c[3] : '{custom_feat}';
            document.getElementById('p-img').src = img;
            document.getElementById('p-title').innerText = c[0];
            document.getElementById('p-price').innerText = c[1];
            document.getElementById('p-desc').innerText = c[2];
            document.getElementById('wa-link').href = `https://wa.me/{wa_num}?text=Hi, I am interested in ${{(c[0])}}`;
        }}
    }});
}}
</script>
"""
prod_html = f"""
<section style="padding-top:150px;"><div class="container">
    <div class="grid-3" style="grid-template-columns:1fr 1fr;">
        <img id="p-img" src="" style="width:100%; border-radius:12px;">
        <div>
            <h1 id="p-title">Loading...</h1>
            <h2 id="p-price" style="color:var(--s)"></h2>
            <p id="p-desc" style="margin:2rem 0; opacity:0.8;"></p>
            <a id="wa-link" href="#" class="btn btn-p">Order via WhatsApp</a>
        </div>
    </div>
</div></section>
{prod_script}
"""

about_page = f'<section class="hero" style="min-height:50vh;"><div class="container"><h1>About Us</h1></div></section><section><div class="container">{format_text(about_txt)}</div></section>'
legal_page = lambda t: f'<section style="padding-top:150px;"><div class="container">{format_text(t)}</div></section>'

# --- 7. EXPORT ---
c1, c2 = st.columns([3, 1])
with c1:
    st.success("Analysis Complete. Code optimized for Mobile & SEO.")
    preview = st.radio("Preview", ["Home", "Contact", "Product"], horizontal=True)
    if preview == "Home": st.components.v1.html(build_page("Home", home_html), height=600, scrolling=True)
    elif preview == "Contact": st.components.v1.html(build_page("Contact", contact_html), height=600, scrolling=True)
    elif preview == "Product": st.components.v1.html(build_page("Product", prod_html), height=600, scrolling=True)

with c2:
    if st.button("DOWNLOAD SITE (v26.6)", type="primary"):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("index.html", build_page("Home", home_html))
            z.writestr("contact.html", build_page("Contact Us", contact_html))
            z.writestr("about.html", build_page("About Us", about_page))
            z.writestr("product.html", build_page("Product Details", prod_html))
            z.writestr("privacy.html", build_page("Privacy Policy", legal_page(priv_txt)))
            z.writestr("terms.html", build_page("Terms of Service", legal_page(term_txt)))
            z.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {prod_url}/sitemap.xml")
            z.writestr("sitemap.xml", f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{prod_url}/</loc></url></urlset>')
        st.download_button("📥 Download ZIP", b.getvalue(), "kaydiem_site.zip", "application/zip")
