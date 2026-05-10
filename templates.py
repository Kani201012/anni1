# templates.py
# All HTML section generators.
#
# Rules enforced here:
#   - Every public function signature is:  gen_*(cfg: SiteConfig) -> str
#   - No Streamlit imports. No global variable reads.
#   - User text passes through sanitize() before injection into JS contexts.
#   - Newlines in user content are never placed inside JS string literals.
#
# Dependency chain:  templates.py → utils.py  (and nothing else)

from __future__ import annotations
import re
from utils import sanitize, sanitize_url, get_simple_icon, extract_youtube_id, clean_phone, format_text

# Forward reference — SiteConfig is defined in compiler.py.
# We use TYPE_CHECKING to avoid a circular import at runtime.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from compiler import SiteConfig


# ---------------------------------------------------------------------------
# SHARED JS HELPERS  (injected once per page via gen_csv_parser)
# ---------------------------------------------------------------------------

def gen_csv_parser() -> str:
    """Emit the shared parseCSVLine() and parseMarkdown() JS helpers."""
    return """
<script defer>
function parseCSVLine(str) {
    const res=[]; let cur=''; let inQuote=false;
    for(let i=0;i<str.length;i++){
        const c=str[i];
        if(c==='"'){if(inQuote&&str[i+1]==='"'){cur+='"';i++;}else{inQuote=!inQuote;}}
        else if(c===','&&!inQuote){res.push(cur.trim());cur='';}
        else{cur+=c;}
    }
    res.push(cur.trim()); return res;
}
function parseMarkdown(text){
    if(!text) return '';
    let clean=text.split('\\\\n').join('<br>').split('\\n').join('<br>');
    let parts=clean.split('**');
    for(let i=1;i<parts.length;i+=2){parts[i]='<strong>'+parts[i]+'</strong>';}
    let bolded=parts.join('');
    return bolded.split('<br>').map(line=>{
        let t=line.trim();
        if(t.startsWith('* ')) return '<li style="margin-left:20px;list-style-type:disc;margin-bottom:8px;">'+t.substring(2)+'</li>';
        return t?'<p style="margin-bottom:15px;">'+t+'</p>':'';
    }).join('');
}
</script>"""


def gen_2050_scripts(cfg: 'SiteConfig') -> str:
    """Emit feature-flag JS (context-aware UI, A/B test, voice search)."""
    context_js = (
        "if(new Date().getHours()>=19||new Date().getHours()<=6)"
        "document.body.classList.add('dark-mode');"
    ) if cfg.enable_context else ""

    # FIX: hoist the A/B line so it is never nested inside an f-string quote context
    ab_js = (
        "let variant=localStorage.getItem('titan_ab')||(Math.random()>0.5?'A':'B');"
        "localStorage.setItem('titan_ab',variant);"
        "if(variant==='B')document.documentElement.style.setProperty('--s','#10b981');"
    ) if cfg.enable_ab else "//"

    voice_js = (
        "function startVoiceSearch(){"
        "if(!('webkitSpeechRecognition' in window))return alert('Voice search not supported.');"
        "const rec=new webkitSpeechRecognition();rec.lang='en-US';"
        "const btn=document.getElementById('voice-btn');btn.classList.add('listening');"
        "rec.onresult=(e)=>{"
        "const transcript=e.results[0][0].transcript.toLowerCase();"
        "document.querySelectorAll('.card').forEach(c=>{"
        "c.style.display=c.innerText.toLowerCase().includes(transcript)?'flex':'none';});};"
        "rec.onend=()=>btn.classList.remove('listening');rec.start();}"
    ) if cfg.enable_voice else ""

    return f"<script defer>{context_js}{ab_js}{voice_js}</script>"


# ---------------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------------

def gen_nav(cfg: 'SiteConfig') -> str:
    logo_display = (
        f'<img src="{sanitize_url(cfg.logo_url)}" height="40" width="auto" alt="{sanitize(cfg.biz_name)} Logo" loading="eager">'
        if cfg.logo_url else
        f'<span style="font-weight:900;font-size:1.5rem;color:var(--p)">{sanitize(cfg.biz_name)}</span>'
    )
    blog_link = '<a href="blog.html" onclick="toggleMenu()">Blog</a>' if cfg.show_blog else ''
    book_link = '<a href="booking.html" onclick="toggleMenu()">Book Now</a>' if cfg.show_booking else ''
    lang_btn  = '<a href="#" onclick="openLangModal()" aria-label="Switch Language">🌐 ES</a>' if cfg.lang_sheet else ''
    top_bar   = f'<div id="top-bar"><a href="{sanitize_url(cfg.top_bar_link)}">{sanitize(cfg.top_bar_text)}</a></div>' if cfg.top_bar_enabled else ''
    nav_top   = "if(true){document.querySelector('#main-navbar').style.top='40px';}" if cfg.top_bar_enabled else ""

    features_link  = '<a href="index.html#features" onclick="toggleMenu()">Features</a>'  if cfg.show_features  else ''
    pricing_link   = '<a href="index.html#pricing" onclick="toggleMenu()">Savings</a>'    if cfg.show_pricing   else ''
    inventory_link = '<a href="index.html#inventory" onclick="toggleMenu()">Store</a>'    if cfg.show_inventory else ''

    return f"""
{top_bar}
<nav id="main-navbar">
    <div class="container nav-flex">
        <a href="index.html" aria-label="Home" style="text-decoration:none;">{logo_display}</a>
        <div class="mobile-menu" onclick="document.querySelector('.nav-links').classList.toggle('active')">☰</div>
        <div class="nav-links">
            <a href="index.html" onclick="toggleMenu()">Home</a>
            {features_link}{pricing_link}{inventory_link}
            {blog_link}{book_link}{lang_btn}
            <a href="contact.html" onclick="toggleMenu()">Contact</a>
            <a href="tel:{clean_phone(cfg.biz_phone)}" class="btn btn-accent" style="padding:0.6rem 1.5rem;border-radius:50px;">Call Now</a>
        </div>
    </div>
</nav>
<div id="theme-toggle" onclick="document.body.classList.toggle('dark-mode')" aria-label="Toggle Dark Mode">🌓</div>
<script>
function toggleMenu(){{document.querySelector('.nav-links').classList.remove('active');}}
{nav_top}
</script>"""


# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------

def gen_hero(cfg: 'SiteConfig') -> str:
    if cfg.hero_video_id:
        clean_id = extract_youtube_id(cfg.hero_video_id)
        bg_media = (
            f'<iframe src="https://www.youtube.com/embed/{clean_id}'
            f'?autoplay=1&mute=1&loop=1&playlist={clean_id}&controls=0&showinfo=0&rel=0"'
            f' class="hero-video" style="width:100%;height:100%;object-fit:cover;pointer-events:none;"'
            f' frameborder="0" allow="autoplay; encrypted-media"></iframe>'
        )
    else:
        bg_media = f"""
<div class="carousel-slide active" style="background-image:url('{sanitize_url(cfg.hero_img_1)}')" fetchpriority="high"></div>
<div class="carousel-slide" style="background-image:url('{sanitize_url(cfg.hero_img_2)}')" loading="lazy"></div>
<div class="carousel-slide" style="background-image:url('{sanitize_url(cfg.hero_img_3)}')" loading="lazy"></div>
<script defer>
let slides=document.querySelectorAll('.carousel-slide');let cur=0;
setInterval(()=>{{slides[cur].classList.remove('active');cur=(cur+1)%slides.length;slides[cur].classList.add('active');}},4000);
</script>"""

    badge_html = f'<div class="hero-badge">{sanitize(cfg.hero_badge_txt)}</div>' if cfg.hero_badge_txt.strip() else ''

    return f"""
<section class="modern-hero">
    <div class="modern-hero-bg"></div>
    <div class="container modern-hero-grid">
        <div class="modern-hero-text reveal active">
            {badge_html}
            <h1 id="hero-title">{sanitize(cfg.hero_h)}</h1>
            <p id="hero-sub">{sanitize(cfg.hero_sub)}</p>
            <div class="hero-btn-group">
                <a href="#inventory" class="btn btn-accent">Explore Now</a>
                <a href="contact.html" class="btn btn-outline-light">Contact Us</a>
            </div>
        </div>
        <div class="modern-hero-visual reveal active" style="transition-delay:0.2s;">
            <div class="visual-frame">{bg_media}</div>
            <div class="floating-element glow-1"></div>
            <div class="floating-element glow-2"></div>
        </div>
    </div>
</section>"""


# ---------------------------------------------------------------------------
# STATS RIBBON
# ---------------------------------------------------------------------------

def gen_stats(cfg: 'SiteConfig') -> str:
    return f"""
<div class="stats-ribbon-container container reveal">
    <div class="stats-ribbon">
        <div class="stat-block"><h3>{sanitize(cfg.stat_1)}</h3><p>{sanitize(cfg.label_1)}</p></div>
        <div class="stat-divider"></div>
        <div class="stat-block"><h3>{sanitize(cfg.stat_2)}</h3><p>{sanitize(cfg.label_2)}</p></div>
        <div class="stat-divider"></div>
        <div class="stat-block"><h3>{sanitize(cfg.stat_3)}</h3><p>{sanitize(cfg.label_3)}</p></div>
    </div>
</div>"""


# ---------------------------------------------------------------------------
# FEATURES GRID
# ---------------------------------------------------------------------------

def gen_features(cfg: 'SiteConfig') -> str:
    cards = ""
    for line in cfg.feat_data.split('\n'):
        if "|" not in line:
            continue
        parts = line.split('|')
        if len(parts) < 3:
            continue
        icon_name = parts[0].strip()
        title_text = sanitize(parts[1].strip())
        raw_desc = parts[2].strip()
        styled_desc = re.sub(
            r'\*\*(.*?)\*\*',
            r'<strong style="color:var(--txt);font-weight:800;font-size:1.05rem;">\1</strong>',
            sanitize(raw_desc)
        )
        cards += f"""
<div class="card reveal" style="padding:0;">
    <div class="card-content" style="text-align:left;padding:2rem;">
        <div style="color:var(--s);margin-bottom:1.5rem;background:rgba(0,0,0,0.04);width:50px;height:50px;display:flex;align-items:center;justify-content:center;border-radius:12px;">
            {get_simple_icon(icon_name)}
        </div>
        <h3 style="font-size:1.3rem;margin-bottom:1rem;color:var(--txt);">{title_text}</h3>
        <p style="opacity:0.8;line-height:1.7;font-size:1rem;color:var(--txt);margin:0;text-align:left;">{styled_desc}</p>
    </div>
</div>"""

    return f"""
<section id="features" style="background:var(--bg)">
    <div class="container">
        <div class="section-head reveal" style="display:flex;flex-direction:column;align-items:center;text-align:center;margin-bottom:4rem;">
            <h2 style="margin-bottom:0.5rem;font-size:2.5rem;">{sanitize(cfg.f_title)}</h2>
            <div style="width:60px;height:4px;background:var(--s);margin:1rem 0;border-radius:2px;"></div>
        </div>
        <div class="grid-3">{cards}</div>
    </div>
</section>"""


# ---------------------------------------------------------------------------
# PRICING TABLE
# ---------------------------------------------------------------------------

def gen_pricing_table(cfg: 'SiteConfig') -> str:
    if not cfg.show_pricing:
        return ""
    return f"""
<section id="pricing">
    <div class="container">
        <div class="section-head reveal"><h2>Pricing</h2></div>
        <div class="pricing-wrapper reveal">
            <table class="pricing-table">
                <thead><tr>
                    <th style="width:40%">Expense Category</th>
                    <th style="background:var(--s);">Titan</th>
                    <th>{sanitize(cfg.wix_name)}</th>
                </tr></thead>
                <tbody>
                    <tr><td>Initial Setup Fee</td><td><strong>{sanitize(cfg.titan_price)}</strong></td><td>$0</td></tr>
                    <tr><td>Annual Costs</td><td><strong>{sanitize(cfg.titan_mo)}</strong></td><td>{sanitize(cfg.wix_mo)}</td></tr>
                    <tr><td><strong>5-Year Savings</strong></td>
                        <td style="color:var(--s);font-size:1.3rem;">You Save {sanitize(cfg.save_val)}</td>
                        <td>$0</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</section>"""


# ---------------------------------------------------------------------------
# INVENTORY / STORE
# ---------------------------------------------------------------------------

def gen_inventory(cfg: 'SiteConfig') -> str:
    if not cfg.show_inventory:
        return ""
    voice_btn = '<button id="voice-btn" onclick="startVoiceSearch()" aria-label="Voice Search">🎤</button>' if cfg.enable_voice else ''
    return (
        f'<section id="inventory" style="background:rgba(0,0,0,0.02)">'
        f'<div class="container">'
        f'<div class="section-head reveal"><h2 id="store-title">Store</h2></div>'
        f'<div id="inv-grid" class="grid-3"><div>Loading Edge Data...</div></div>'
        f'</div>{voice_btn}</section>'
        + _gen_inventory_js(cfg)
    )


def _gen_inventory_js(cfg: 'SiteConfig') -> str:
    clean_wa = clean_phone(cfg.wa_num)
    return f"""
{gen_csv_parser()}
<script defer>
async function loadInv(){{
    if(!'{cfg.sheet_url}') return;
    try{{
        const res=await fetch('{cfg.sheet_url}');
        const txt=await res.text();
        const lines=txt.split(/\\r\\n|\\n/);
        const box=document.getElementById('inv-grid');
        if(!box) return;
        box.innerHTML='';
        for(let i=1;i<lines.length;i++){{
            if(!lines[i].trim()) continue;
            const c=parseCSVLine(lines[i]);
            let allImgs=c[3]?c[3].split('|'):[];
            let mainImg=allImgs.length>0?allImgs[0]:'{cfg.custom_feat}';
            if(c.length>1){{
                const pName=encodeURIComponent(c[0]);
                // FIX: escape product name/price for safe onclick injection
                const safeName=c[0].replace(/'/g,"\\'");
                const safePrice=c[1].replace(/'/g,"\\'");
                box.innerHTML+=`
                    <div class="card reveal">
                        <img src="${{mainImg}}" class="prod-img" width="300" height="250" loading="lazy" alt="${{c[0]}}">
                        <div class="card-body">
                            <h3>${{c[0]}}</h3>
                            <p style="font-weight:bold;color:#059669;margin-bottom:10px;">${{c[1]}}</p>
                            <p class="card-desc">${{c[2]}}</p>
                            <div style="margin-top:auto;display:grid;grid-template-columns:1fr 1fr;gap:10px;padding-top:15px;">
                                <button onclick="addToCart('${{safeName}}','${{safePrice}}')" class="btn btn-primary" style="padding:0.6rem;font-size:0.75rem;">ADD</button>
                                <a href="product.html?item=${{pName}}" class="btn btn-accent" style="padding:0.6rem;font-size:0.75rem;text-decoration:none;display:flex;align-items:center;justify-content:center;">DETAILS</a>
                            </div>
                        </div>
                    </div>`;
            }}
        }}
    }}catch(e){{console.log(e);}}
}}
if(document.getElementById('inv-grid')) window.addEventListener('load',loadInv);
</script>"""


# ---------------------------------------------------------------------------
# ABOUT SECTION
# ---------------------------------------------------------------------------

def gen_about_section(cfg: 'SiteConfig') -> str:
    if not cfg.show_gallery:
        return ""
    return f"""
<section id="about" class="modern-about">
    <div class="container">
        <div class="about-grid">
            <div class="about-visual reveal">
                <img src="{sanitize_url(cfg.about_img)}" width="600" height="500" loading="lazy" alt="About Us" class="about-main-img">
                <div class="about-experience-badge">
                    <strong>100%</strong>
                    <span>Client<br>Satisfaction</span>
                </div>
            </div>
            <div class="about-text reveal" style="transition-delay:0.2s;">
                <h2 id="about-title">{sanitize(cfg.about_h)}</h2>
                <div class="about-lead">{format_text(cfg.about_short)}</div>
                <div style="margin-top:2rem;"><a href="about.html" class="btn btn-primary">Read Our Story →</a></div>
            </div>
        </div>
    </div>
</section>"""


# ---------------------------------------------------------------------------
# TESTIMONIALS
# ---------------------------------------------------------------------------

def gen_testimonials(cfg: 'SiteConfig') -> str:
    if not cfg.show_testimonials:
        return ""
    cards = ""
    for line in cfg.testi_data.split('\n'):
        if '|' not in line:
            continue
        author = sanitize(line.split('|')[0].strip())
        quote  = sanitize(line.split('|')[1].strip())
        initial = author[0].upper() if author else '?'
        cards += f"""
<div class="card reveal" style="padding:clamp(1.5rem,5vw,2.5rem);display:flex;flex-direction:column;height:100%;text-align:left;">
    <div style="margin-bottom:1.5rem;">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="var(--p)" style="opacity:0.4;"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/></svg>
    </div>
    <p style="font-size:1.1rem;font-style:italic;line-height:1.7;opacity:0.9;flex-grow:1;margin-bottom:2rem;">"{quote}"</p>
    <div style="display:flex;align-items:center;gap:15px;border-top:1px solid rgba(128,128,128,0.1);padding-top:1.5rem;">
        <div style="width:45px;height:45px;min-width:45px;border-radius:50%;background:var(--p);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:1.2rem;">{initial}</div>
        <div>
            <b style="color:var(--txt-h);font-size:1.1rem;display:block;">{author}</b>
            <span style="display:block;font-size:0.8rem;opacity:0.6;margin-top:2px;">Verified Client</span>
        </div>
    </div>
</div>"""

    return f"""
<section id="testimonials" style="background:rgba(128,128,128,0.02)">
    <div class="container">
        <div class="section-head reveal"><h2>Client Stories</h2></div>
        <div class="grid-3">{cards}</div>
    </div>
</section>"""


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

def gen_faq_section(cfg: 'SiteConfig') -> str:
    if not cfg.show_faq:
        return ""
    items = ""
    for line in cfg.faq_data.split('\n'):
        # FIX: use ' ? ' (with spaces) as delimiter and maxsplit=1
        # to avoid discarding content after a second '?' in the answer.
        if ' ? ' not in line:
            continue
        parts = line.split(' ? ', 1)
        q = sanitize(parts[0].strip())
        a = sanitize(parts[1].strip())
        items += f"<details class='reveal'><summary>{q}?</summary><p>{a}</p></details>"

    return f"""
<section id="faq">
    <div class="container" style="max-width:800px;">
        <div class="section-head reveal"><h2 id="faq-title">Frequently Asked Questions</h2></div>
        {items}
    </div>
</section>"""


# ---------------------------------------------------------------------------
# CTA BAND
# ---------------------------------------------------------------------------

def gen_cta(cfg: 'SiteConfig') -> str:
    return (
        '<section style="background:var(--s);color:white;text-align:center;">'
        '<div class="container reveal">'
        '<h2>Start Owning Your Future</h2>'
        '<p style="margin-bottom:2rem;">Stop paying rent.</p>'
        '<a href="contact.html" class="btn" style="background:white;color:var(--s)!important;">Get Started</a>'
        '</div></section>'
    )


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

def gen_footer(cfg: 'SiteConfig') -> str:
    import datetime
    icons = ""
    if cfg.fb_link: icons += f'<a href="{sanitize_url(cfg.fb_link)}" target="_blank" rel="noopener noreferrer" aria-label="Facebook" style="display:inline-block;margin-right:15px;"><svg class="social-icon" viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg></a>'
    if cfg.ig_link: icons += f'<a href="{sanitize_url(cfg.ig_link)}" target="_blank" rel="noopener noreferrer" aria-label="Instagram" style="display:inline-block;margin-right:15px;"><svg class="social-icon" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg></a>'
    if cfg.x_link:  icons += f'<a href="{sanitize_url(cfg.x_link)}" target="_blank" rel="noopener noreferrer" aria-label="X" style="display:inline-block;margin-right:15px;"><svg class="social-icon" viewBox="0 0 24 24"><path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"></path></svg></a>'

    footer_blog = '<a href="blog.html">Blog</a>'    if cfg.show_blog    else ''
    footer_book = '<a href="booking.html">Book Now</a>' if cfg.show_booking else ''

    return f"""
<footer>
    <div class="container">
        <div class="footer-grid">
            <div>
                <h3 style="color:white;margin-bottom:1.5rem;">{sanitize(cfg.biz_name)}</h3>
                <p style="color:rgba(255,255,255,0.7);opacity:1;">{sanitize(cfg.biz_addr)}</p>
                <div style="margin-top:1.5rem;">{icons}</div>
            </div>
            <div>
                <h4 style="color:white;text-transform:uppercase;">Links</h4>
                <a href="index.html">Home</a>
                <a href="about.html">About</a>
                {footer_blog}{footer_book}
            </div>
            <div>
                <h4 style="color:white;text-transform:uppercase;">Legal</h4>
                <a href="privacy.html">Privacy</a>
                <a href="terms.html">Terms</a>
            </div>
        </div>
        <div style="border-top:1px solid rgba(255,255,255,0.1);margin-top:3rem;padding-top:2rem;text-align:center;color:rgba(255,255,255,0.5);">
            &copy; {datetime.datetime.now().year} {sanitize(cfg.biz_name)}. Powered by Titan Engine.
        </div>
    </div>
</footer>"""


# ---------------------------------------------------------------------------
# CART SYSTEM
# ---------------------------------------------------------------------------

def gen_cart_system(cfg: 'SiteConfig') -> str:
    if not cfg.wa_num:
        return ""
    clean_wa = clean_phone(cfg.wa_num)
    safe_upi = sanitize(cfg.upi_id, for_js=True)
    safe_pp  = sanitize(cfg.paypal_link, for_js=True)

    # FIX: hoist the A/B line above the f-string to avoid nested ternary-in-string
    ab_line = "msg+='%0A(Variant:'+( localStorage.getItem('titan_ab')||'')+')' ;" if cfg.enable_ab else "//"

    return f"""
<div id="cart-float" onclick="toggleCart()" style="display:none;" aria-label="Cart">🛒 <span id="cart-count">0</span></div>
<div id="cart-overlay" onclick="toggleCart()"></div>
<div id="cart-modal">
    <h3>Your Cart</h3>
    <div id="cart-items" style="max-height:200px;overflow-y:auto;margin:1rem 0;"></div>
    <div style="font-weight:bold;font-size:1.2rem;margin-bottom:1rem;text-align:right;">Total: <span id="cart-total">0.00</span></div>
    <div class="local-vault">
        <h4 style="font-size:0.9rem;">🔒 Fast Checkout Vault</h4>
        <input type="text" id="vault-name" placeholder="Full Name">
        <input type="text" id="vault-address" placeholder="Delivery Address">
    </div>
    <button onclick="checkoutWhatsApp()" class="btn btn-accent" style="width:100%;margin-top:1rem;">1-Click Checkout via WhatsApp</button>
</div>
<script defer>
let cart=JSON.parse(localStorage.getItem('titanCart'))||[];
document.getElementById('vault-name').value=localStorage.getItem('t_name')||'';
document.getElementById('vault-address').value=localStorage.getItem('t_addr')||'';

function renderCart(){{
    const box=document.getElementById('cart-items');if(!box)return;
    box.innerHTML='';let total=0;
    cart.forEach((item,i)=>{{
        total+=parseFloat(item.price.replace(/[^0-9.]/g,''))||0;
        box.innerHTML+=`<div class="cart-item"><span>${{item.name}}</span><span>${{item.price}} <span onclick="remItem(${{i}})" style="color:red;cursor:pointer;">x</span></span></div>`;
    }});
    document.getElementById('cart-count').innerText=cart.length;
    document.getElementById('cart-total').innerText=total.toFixed(2);
    document.getElementById('cart-float').style.display=cart.length>0?'flex':'none';
    localStorage.setItem('titanCart',JSON.stringify(cart));
}}

function addToCart(name,price){{cart.push({{name,price}});renderCart();alert(name+' added!');}}
function remItem(i){{cart.splice(i,1);renderCart();}}
function toggleCart(){{const m=document.getElementById('cart-modal');m.style.display=m.style.display==='block'?'none':'block';document.getElementById('cart-overlay').style.display=m.style.display;}}

function checkoutWhatsApp(){{
    const n=document.getElementById('vault-name').value;
    const a=document.getElementById('vault-address').value;
    localStorage.setItem('t_name',n);localStorage.setItem('t_addr',a);
    let msg='New Order:%0A';let total=0;
    cart.forEach(i=>{{msg+=`- ${{i.name}} (${{i.price}})%0A`;total+=parseFloat(i.price.replace(/[^0-9.]/g,''))||0;}});
    msg+=`%0ATotal: ${{total.toFixed(2)}}%0A`;
    if(n) msg+=`%0ADeliver to: ${{n}}, ${{a}}`;
    {ab_line}
    msg+=`%0A%0AUPI: {safe_upi} | PayPal: {safe_pp}`;
    window.open(`https://wa.me/{clean_wa}?text=${{msg}}`,'_blank','noopener,noreferrer');
    cart=[];renderCart();toggleCart();
}}
window.addEventListener('load',renderCart);
</script>"""


# ---------------------------------------------------------------------------
# WHATSAPP WIDGET
# ---------------------------------------------------------------------------

def gen_wa_widget(cfg: 'SiteConfig') -> str:
    if not cfg.wa_num:
        return ""
    clean_wa = clean_phone(cfg.wa_num)
    return f"""
<a href="https://wa.me/{clean_wa}" target="_blank" rel="noopener noreferrer" id="wa-widget" aria-label="Chat on WhatsApp">
    <svg viewBox="0 0 24 24" fill="white" width="32" height="32"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2z"/></svg>
</a>
<style>
#wa-widget{{position:fixed;bottom:30px;right:30px;background:#25D366;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,0.3);z-index:999;transition:transform 0.3s;}}
#wa-widget:hover{{transform:scale(1.1);}}
</style>"""


# ---------------------------------------------------------------------------
# LEAD POPUP
# ---------------------------------------------------------------------------

def gen_popup(cfg: 'SiteConfig') -> str:
    if not cfg.popup_enabled:
        return ""
    clean_wa = clean_phone(cfg.wa_num)
    delay_ms = cfg.popup_delay * 1000
    return f"""
<div id="lead-popup">
    <div class="close-popup" onclick="document.getElementById('lead-popup').style.display='none'">&times;</div>
    <h3>{sanitize(cfg.popup_title)}</h3>
    <p>{sanitize(cfg.popup_text)}</p>
    <a href="https://wa.me/{clean_wa}?text=I+want+the+offer" class="btn btn-accent" target="_blank" rel="noopener noreferrer">{sanitize(cfg.popup_cta)}</a>
</div>
<script defer>
setTimeout(()=>{{
    if(!localStorage.getItem('popupShown')){{
        document.getElementById('lead-popup').style.display='block';
        localStorage.setItem('popupShown','true');
    }}
}},{delay_ms});
</script>"""


# ---------------------------------------------------------------------------
# MULTI-LANGUAGE SWITCHER
# ---------------------------------------------------------------------------

def gen_lang_script(cfg: 'SiteConfig') -> str:
    if not cfg.lang_sheet:
        return ""
    return f"""
<div id="lang-overlay" onclick="closeLangModal()"></div>
<div id="lang-modal">
    <h3 style="margin-bottom:1.5rem;border-bottom:1px solid #eee;padding-bottom:10px;">Select Language</h3>
    <div class="lang-grid">
        <div onclick="switchLang('en',0)" class="lang-opt">🇺🇸 English</div>
        <div onclick="switchLang('es',1)" class="lang-opt">🇪🇸 Español</div>
        <div onclick="switchLang('fr',2)" class="lang-opt">🇫🇷 Français</div>
        <div onclick="switchLang('ar',3)" class="lang-opt">🇸🇦 العربية</div>
    </div>
</div>
<script defer>
function openLangModal(){{document.getElementById('lang-modal').style.display='block';document.getElementById('lang-overlay').style.display='block';}}
function closeLangModal(){{document.getElementById('lang-modal').style.display='none';document.getElementById('lang-overlay').style.display='none';}}
async function switchLang(langCode,colIndex){{
    closeLangModal();
    localStorage.setItem('titan_lang',langCode);localStorage.setItem('titan_col',colIndex);
    if(langCode==='en'){{location.reload();return;}}
    try{{
        const res=await fetch('{cfg.lang_sheet}');
        const txt=await res.text();
        const lines=txt.split(/\\r\\n|\\n/);
        for(let i=1;i<lines.length;i++){{
            const row=parseCSVLine(lines[i]);
            if(row.length>colIndex){{const el=document.getElementById(row[0]);if(el&&row[colIndex])el.innerText=row[colIndex];}}
        }}
        document.documentElement.lang=langCode;
    }}catch(e){{console.log('Lang Error',e);}}
}}
window.addEventListener('load',()=>{{
    const sl=localStorage.getItem('titan_lang');const sc=localStorage.getItem('titan_col');
    if(sl&&sl!=='en')switchLang(sl,parseInt(sc));
}});
</script>"""


# ---------------------------------------------------------------------------
# INNER PAGE HEADER BANNER
# ---------------------------------------------------------------------------

def gen_inner_header(title: str) -> str:
    safe_title = sanitize(title)
    return f"""
<div style="min-height:40vh;background:var(--p);display:flex;align-items:center;justify-content:center;text-align:center;padding-top:150px;padding-bottom:50px;">
    <div class="container">
        <h1 style="color:#ffffff!important;margin:0;text-shadow:0 4px 15px rgba(0,0,0,0.3);font-size:clamp(3rem,6vw,4.5rem);">{safe_title}</h1>
    </div>
</div>"""


# ---------------------------------------------------------------------------
# CONTACT PAGE
# ---------------------------------------------------------------------------

def gen_contact_page(cfg: 'SiteConfig') -> str:
    clean_wa = clean_phone(cfg.wa_num)
    return f"""
{gen_inner_header("Contact Us")}
<section style="background:var(--bg);">
    <div class="container">
        <div class="contact-grid">
            <div class="card" style="padding:clamp(1.5rem,5vw,3rem);">
                <h3 style="margin-bottom:1.5rem;color:var(--p);font-size:2rem;">Get In Touch</h3>
                <p><strong>Address</strong><br>{sanitize(cfg.biz_addr)}</p>
                <p><strong>Phone</strong><br><a href="tel:{clean_phone(cfg.biz_phone)}" style="color:var(--s);font-weight:bold;">{sanitize(cfg.biz_phone)}</a></p>
                <p><strong>Email</strong><br><a href="mailto:{sanitize(cfg.biz_email)}" style="color:var(--txt);">{sanitize(cfg.biz_email)}</a></p>
                <a href="https://wa.me/{clean_wa}" target="_blank" class="btn btn-accent" style="width:100%;margin-top:1rem;">WhatsApp Us Instantly</a>
            </div>
            <div class="card" style="padding:clamp(1.5rem,5vw,3rem);">
                <h3 style="margin-bottom:1.5rem;font-size:2rem;">Send a Message</h3>
                <form action="https://formsubmit.co/{sanitize(cfg.biz_email)}" method="POST" style="display:flex;flex-direction:column;gap:1.5rem;">
                    <input type="text" name="name" placeholder="Full Name" required style="width:100%;padding:1.2rem;border:1px solid rgba(128,128,128,0.2);border-radius:8px;background:var(--bg);color:var(--txt);font-size:1rem;font-family:inherit;">
                    <input type="email" name="email" placeholder="Email Address" required style="width:100%;padding:1.2rem;border:1px solid rgba(128,128,128,0.2);border-radius:8px;background:var(--bg);color:var(--txt);font-size:1rem;font-family:inherit;">
                    <textarea name="msg" rows="5" placeholder="Your Message" required style="width:100%;padding:1.2rem;border:1px solid rgba(128,128,128,0.2);border-radius:8px;background:var(--bg);color:var(--txt);font-size:1rem;font-family:inherit;resize:vertical;"></textarea>
                    <button class="btn btn-primary" type="submit" style="height:4rem;border:none;cursor:pointer;">Send Secure Message</button>
                </form>
            </div>
        </div>
        <div style="border-radius:var(--radius);overflow:hidden;border:var(--border);margin-top:4rem;height:450px;position:relative;">
            {cfg.map_iframe}
        </div>
    </div>
</section>"""


# ---------------------------------------------------------------------------
# PRODUCT DETAIL PAGE
# ---------------------------------------------------------------------------

def gen_product_page_content(cfg: 'SiteConfig', is_demo: bool = False) -> str:
    ar_script = '<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>' if cfg.enable_ar else ''
    demo_flag = "true" if is_demo else "false"
    return f"""
{ar_script}
<section style="padding-top:140px;background:var(--bg);min-height:100vh;">
    <div class="container">
        <a href="index.html#inventory" class="back-btn" style="color:var(--p);text-decoration:none;font-weight:700;display:inline-flex;align-items:center;gap:8px;margin-bottom:30px;">← BACK TO STORE</a>
        <div id="product-detail-target">Loading Specifications...</div>
    </div>
</section>
{gen_csv_parser()}
<script defer>
const isDemo={demo_flag};
function changeImg(src){{document.getElementById('main-img').src=src;}}
async function loadProduct(){{
    const params=new URLSearchParams(window.location.search);
    let targetName=params.get('item');
    if(isDemo&&!targetName) targetName="Demo Product";
    try{{
        const res=await fetch('{cfg.sheet_url}');
        const txt=await res.text();
        const lines=txt.split(/\\r\\n|\\n/);
        for(let i=1;i<lines.length;i++){{
            const clean=parseCSVLine(lines[i]);
            if(clean[0]===targetName||(isDemo&&i===1)){{
                let allImgs=clean[3]?clean[3].split('|'):['{cfg.custom_feat}'];
                let thumbHtml='';
                allImgs.forEach(img=>{{thumbHtml+=`<img src="${{img.trim()}}" onclick="changeImg('${{img.trim()}}')" style="width:70px;height:70px;object-fit:cover;margin-right:10px;cursor:pointer;border-radius:12px;border:1px solid rgba(128,128,128,0.2);">`;}} );
                let mainMedia=`<img src="${{allImgs[0]}}" id="main-img" style="width:100%;border-radius:24px;height:500px;object-fit:cover;" alt="${{clean[0]}}">`;
                if({str(cfg.enable_ar).lower()}&&clean.length>5&&clean[5].includes('.glb')){{
                    mainMedia=`<model-viewer src="${{clean[5]}}" ar ar-modes="webxr scene-viewer quick-look" camera-controls auto-rotate style="width:100%;height:500px;border-radius:24px;"></model-viewer>`;
                }}
                const safeName=clean[0].replace(/'/g,"\\'");
                const safePrice=clean[1].replace(/'/g,"\\'");
                let stripe=(clean.length>4&&clean[4].includes('http')&&!clean[4].match(/\\.(jpg|jpeg|png|gif|webp)$/i))?clean[4]:'';
                let btnAction=stripe?
                    `<a href="${{stripe}}" class="btn btn-accent" style="min-width:280px;text-decoration:none;height:4rem;display:inline-flex;align-items:center;justify-content:center;">SECURE NOW</a>`:
                    `<button onclick="addToCart('${{safeName}}','${{safePrice}}')" class="btn btn-accent" style="min-width:280px;height:4rem;">ADD TO CART</button>`;
                document.getElementById('product-detail-target').innerHTML=`
                    <div class="detail-view">
                        <div class="product-media-column">${{mainMedia}}<div style="display:flex;margin-top:20px;">${{thumbHtml}}</div></div>
                        <div class="product-info-column">
                            <h1>${{clean[0]}}</h1>
                            <div class="product-price-tag">${{clean[1]}}</div>
                            <div class="product-specs-container">${{parseMarkdown(clean[2])}}</div>
                            <div style="margin-top:3rem;">${{btnAction}}</div>
                        </div>
                    </div>`;
                document.title=clean[0]+' | {sanitize(cfg.biz_name, for_js=True)}';
                break;
            }}
        }}
    }}catch(e){{console.error('Product Error:',e);}}
}}
window.addEventListener('load',loadProduct);
</script>"""


# ---------------------------------------------------------------------------
# BLOG INDEX
# ---------------------------------------------------------------------------

def gen_blog_index_html(cfg: 'SiteConfig') -> str:
    if not cfg.show_blog:
        return ""
    return f"""
<section class="hero" style="min-height:40vh;background-image:linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.6)),url('{sanitize_url(cfg.hero_img_1)}');background-size:cover;">
    <div class="container hero-content"><h1>{sanitize(cfg.blog_hero_title)}</h1><p>{sanitize(cfg.blog_hero_sub)}</p></div>
</section>
<section><div class="container"><div id="blog-grid" class="grid-3">Loading Posts...</div></div></section>
{gen_csv_parser()}
<script defer>
async function loadBlog(){{
    if(!'{cfg.blog_sheet_url}') return;
    try{{
        const res=await fetch('{cfg.blog_sheet_url}');const txt=await res.text();const lines=txt.split(/\\r\\n|\\n/);
        const box=document.getElementById('blog-grid');box.innerHTML='';
        for(let i=1;i<lines.length;i++){{
            const r=parseCSVLine(lines[i]);
            if(r.length>4){{
                box.innerHTML+=`
                <article class="card reveal" style="overflow:hidden;padding:0;">
                    <img src="${{r[5]}}" style="width:100%;height:220px;object-fit:cover;" loading="lazy" alt="${{r[1]}}">
                    <div style="padding:2rem;">
                        <span style="color:var(--p);font-size:0.75rem;font-weight:800;text-transform:uppercase;">${{r[3]}}</span>
                        <h3 style="margin:0.75rem 0;"><a href="post.html?id=${{r[0]}}" style="color:var(--txt-h);text-decoration:none;">${{r[1]}}</a></h3>
                        <p style="opacity:0.8;font-size:0.95rem;">${{r[4]}}</p>
                        <a href="post.html?id=${{r[0]}}" class="btn btn-primary" style="width:100%;margin-top:1rem;">Read Article</a>
                    </div>
                </article>`;
            }}
        }}
    }}catch(e){{console.log(e);}}
}}
window.addEventListener('load',loadBlog);
</script>"""


# ---------------------------------------------------------------------------
# BLOG POST
# ---------------------------------------------------------------------------

def gen_blog_post_html(cfg: 'SiteConfig') -> str:
    if not cfg.show_blog:
        return ""
    return f"""
<article id="post-container" style="padding-top:0px;">Loading Content...</article>
{gen_csv_parser()}
<script defer>
async function loadPost(){{
    if(!'{cfg.blog_sheet_url}') return;
    const params=new URLSearchParams(window.location.search);const slug=params.get('id');
    try{{
        const res=await fetch('{cfg.blog_sheet_url}');const txt=await res.text();const lines=txt.split(/\\r\\n|\\n/);
        const container=document.getElementById('post-container');
        for(let i=1;i<lines.length;i++){{
            const r=parseCSVLine(lines[i]);
            if(r[0]===slug){{
                const contentHtml=parseMarkdown(r[6]);
                document.title=r[1]+' | {sanitize(cfg.biz_name, for_js=True)}';
                container.innerHTML=`
                    <header style="background:var(--p);padding:120px 1rem 4rem;color:#fff;text-align:center;">
                        <div class="container"><h1 style="color:#fff!important;">${{r[1]}}</h1></div>
                    </header>
                    <div class="container" style="max-width:800px;padding:3rem 1rem;">
                        <img src="${{r[5]}}" style="width:100%;border-radius:12px;margin-bottom:2rem;" alt="${{r[1]}}">
                        <div style="line-height:1.8;">${{contentHtml}}</div>
                        <a href="blog.html" class="btn btn-primary" style="display:inline-block;margin-top:2rem;">&larr; Back to Blog</a>
                    </div>`;
                break;
            }}
        }}
    }}catch(e){{}}
}}
window.addEventListener('load',loadPost);
</script>"""


# ---------------------------------------------------------------------------
# BOOKING PAGE
# ---------------------------------------------------------------------------

def gen_booking_content(cfg: 'SiteConfig') -> str:
    if not cfg.show_booking:
        return ""
    return (
        f'<section class="hero" style="min-height:30vh;background:var(--p);padding-top:140px;display:flex;align-items:center;justify-content:center;">'
        f'<div class="container hero-content" style="text-align:center;">'
        f'<h1>{sanitize(cfg.booking_title)}</h1>'
        f'<p>{sanitize(cfg.booking_desc)}</p>'
        f'</div></section>'
        f'<section><div class="container" style="text-align:center;">'
        f'<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,0.1);">'
        f'{cfg.booking_embed}'
        f'</div></div></section>'
    )
