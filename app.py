import streamlit as st
import zipfile
import io
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Titan v27.0 | Professional Architect", 
    layout="wide", 
    page_icon="🚀"
)

# --- 2. ADVANCED UI SYSTEM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5rem;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        color: white; font-weight: 800; border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("Titan Architect 2026")
    st.caption("Professional Edition")
    
    with st.expander("🎨 Visual DNA", expanded=True):
        p_color = st.color_picker("Primary Brand", "#0F172A") 
        s_color = st.color_picker("Action (CTA)", "#3B82F6")  
        h_font = st.selectbox("Headings", ["Montserrat", "Space Grotesk", "Inter"])
        b_font = st.selectbox("Body", ["Inter", "Roboto", "Open Sans"])
        border_rad = st.select_slider("Corner Roundness", ["0px", "8px", "16px", "30px"], value="8px")

    with st.expander("⚙️ SEO & Technical"):
        prod_url = st.text_input("Website URL", "https://kaydiemscriptlab.com")
        ga_tag = st.text_input("Google Analytics ID")
        og_image = st.text_input("Social Share Image URL")

# --- 4. DATA INPUT TABS ---
tabs = st.tabs(["Identity", "Content Blocks", "Inventory", "Legal"])

with tabs[0]:
    c1, c2 = st.columns(2)
    biz_name = c1.text_input("Business Name", "Kaydiem Script Lab")
    biz_tagline = c1.text_input("Tagline", "Advanced Scripting & Software Architecture")
    biz_email = c2.text_input("Email", "hello@kaydiemscriptlab.com")
    biz_phone = c2.text_input("Phone", "+91 0000000000")
    biz_addr = st.text_area("Address", "Kolkata, West Bengal, India")
    logo_url = st.text_input("Logo URL (PNG/SVG)")
    wa_num = st.text_input("WhatsApp Number (Include Country Code, no +)", "910000000000")

with tabs[1]:
    hero_h = st.text_input("Hero Headline", "Engineering the Future of Automation")
    hero_sub = st.text_area("Hero Subtext", "Premium custom scripts, revenue leakage solutions, and enterprise software architecture.")
    hero_img = st.text_input("Hero Image URL", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1600")
    
    feat_data = st.text_area("Expertise Grid (Title | Desc | IconURL)", 
                             "Revenue Leakage | Stop profit loss with AI audit scripts. | https://cdn-icons-png.flaticon.com/512/2534/2534063.png\nSheetStore Pro | Advanced Google Sheets database architecture. | https://cdn-icons-png.flaticon.com/512/5968/5968299.png\nSaaS Systems | Full-scale cloud software development. | https://cdn-icons-png.flaticon.com/512/2103/2103633.png")

with tabs[2]:
    st.info("Inventory Data")
    sheet_url = st.text_input("Google Sheet CSV URL")
    fallback_img = st.text_input("Fallback Product Image", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800")

with tabs[3]:
    testi_data = st.text_area("Testimonials (Name | Quote)", "A. Mehta | The best automation scripts in the market.\nS. Kumar | Transformed our workflow overnight.")
    faq_data = st.text_area("FAQs (Q? ? A)", "Is it secure? ? Yes, we use bank-grade encryption.\nCan I get a demo? ? Absolutely, contact us for a walkthrough.")

# --- 5. COMPILER FUNCTIONS ---

def get_css():
    return f"""
    :root {{
        --p: {p_color}; --s: {s_color}; --bg: #ffffff; --txt: #1e293b;
        --radius: {border_rad}; --h-font: '{h_font}', sans-serif; --b-font: '{b_font}', sans-serif;
    }}
    body {{ font-family: var(--b-font); color: var(--txt); margin: 0; line-height: 1.6; }}
    h1, h2, h3 {{ font-family: var(--h-font); color: var(--p); }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    
    /* NEW: Sticky Header */
    nav {{ position: sticky; top: 0; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); z-index: 1000; padding: 1rem 0; border-bottom: 1px solid #eee; }}
    .nav-flex {{ display: flex; justify-content: space-between; align-items: center; }}
    .nav-links a {{ margin-left: 2rem; text-decoration: none; color: var(--txt); font-weight: 600; font-size: 0.9rem; transition: 0.3s; }}
    .nav-links a:hover {{ color: var(--s); }}
    
    .hero {{ padding: 120px 0; background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('{hero_img}'); background-size: cover; background-position: center; color: white; text-align: center; }}
    .hero h1 {{ color: white; font-size: 3.5rem; margin-bottom: 1rem; }}
    .hero p {{ font-size: 1.25rem; max-width: 800px; margin: 0 auto 2rem; opacity: 0.9; }}
    
    .btn {{ display: inline-block; padding: 0.8rem 2rem; background: var(--s); color: white; text-decoration: none; border-radius: var(--radius); font-weight: 700; transition: 0.3s; }}
    .btn:hover {{ transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; padding: 4rem 0; }}
    .card {{ background: #fff; padding: 2rem; border-radius: var(--radius); border: 1px solid #f1f5f9; transition: 0.3s; }}
    .card:hover {{ border-color: var(--s); box-shadow: 0 20px 40px -20px rgba(0,0,0,0.1); }}
    .card img {{ width: 50px; margin-bottom: 1rem; }}

    footer {{ background: var(--p); color: white; padding: 4rem 0; margin-top: 4rem; }}
    footer a {{ color: #cbd5e1; text-decoration: none; display: block; margin-bottom: 0.5rem; }}
    footer a:hover {{ color: white; }}
    
    @media (max-width: 768px) {{ .hero h1 {{ font-size: 2.5rem; }} .nav-links {{ display: none; }} }}
    """

def gen_schema():
    return f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "{biz_name}",
      "url": "{prod_url}",
      "logo": "{logo_url}",
      "contactPoint": {{
        "@type": "ContactPoint",
        "telephone": "{biz_phone}",
        "contactType": "customer service"
      }}
    }}
    </script>"""

def build_page(title, content):
    logo = f'<img src="{logo_url}" height="40">' if logo_url else f'<strong>{biz_name}</strong>'
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} | {biz_name}</title>
        <link href="https://fonts.googleapis.com/css2?family={h_font}:wght@700&family={b_font}:wght@400;600&display=swap" rel="stylesheet">
        <style>{get_css()}</style>
        {gen_schema()}
    </head>
    <body>
        <nav><div class="container nav-flex">
            <a href="index.html" style="text-decoration:none; color:var(--p); font-size:1.5rem;">{logo}</a>
            <div class="nav-links">
                <a href="index.html">Home</a>
                <a href="about.html">Expertise</a>
                <a href="contact.html">Contact</a>
                <a href="https://wa.me/{wa_num}" class="btn" style="color:white; margin-left:1rem;">WhatsApp Us</a>
            </div>
        </div></nav>
        {content}
        <footer><div class="container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:2rem;">
            <div><h3>{biz_name}</h3><p>{biz_tagline}</p></div>
            <div><h4>Quick Links</h4><a href="index.html">Home</a><a href="about.html">About</a><a href="contact.html">Contact</a></div>
            <div><h4>Legal</h4><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Service</a></div>
            <div><h4>Contact</h4><p>{biz_addr}</p><p>{biz_phone}</p></div>
        </div>
        <div style="text-align:center; margin-top:3rem; opacity:0.7; font-size:0.8rem;">
            &copy; {datetime.datetime.now().year} <a href="https://www.kaydiemscriptlab.com/" style="display:inline; color:white; text-decoration:underline;">Kaydiem Script Lab</a>. Powered by Titan Engine.
        </div>
        </footer>
    </body></html>"""

# --- 6. PAGE CONTENT GENERATION ---

home_html = f"""
<section class="hero"><div class="container">
    <h1>{hero_h}</h1>
    <p>{hero_sub}</p>
    <a href="contact.html" class="btn">Get a Custom Quote</a>
</div></section>

<section class="container"><div class="grid">
    {"".join([f'<div class="card"><img src="{x.split("|")[2].strip()}"><h3>{x.split("|")[0].strip()}</h3><p>{x.split("|")[1].strip()}</p></div>' for x in feat_data.split('\\n') if "|" in x])}
</div></section>
"""

# --- 7. DEPLOYMENT ---
st.divider()
if st.button("🚀 GENERATE PROFESSIONAL 2026 SITE ZIP"):
    z_b = io.BytesIO()
    with zipfile.ZipFile(z_b, "a", zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr("index.html", build_page("Home", home_html))
        zf.writestr("about.html", build_page("About", f'<div class="container" style="padding:100px 0;"><h1>Expertise</h1><p>{biz_tagline}</p></div>'))
        zf.writestr("contact.html", build_page("Contact", f'<div class="container" style="padding:100px 0;"><h1>Contact Us</h1><p>Phone: {biz_phone}</p><p>Email: {biz_email}</p><p>Address: {biz_addr}</p></div>'))
        zf.writestr("privacy.html", build_page("Privacy", '<div class="container"><h1>Privacy Policy</h1><p>We respect your data.</p></div>'))
        zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {prod_url}/sitemap.xml")
        zf.writestr("404.html", build_page("404 Not Found", '<div class="container" style="text-align:center; padding:100px 0;"><h1>404</h1><p>Page not found.</p></div>'))

    st.download_button("📥 Download Website", z_b.getvalue(), "kaydiem_pro_site.zip", "application/zip")
